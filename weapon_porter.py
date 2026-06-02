import os
import json
import threading
import traceback

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import weapon_data as wd
import vpk_tool
import converter


try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    _HAS_DND = True
except Exception:
    _HAS_DND = False

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
CONFIG_PATH = os.path.join(APP_DIR, "config.json")




def autodetect_vpk_exe():

    candidates = []
    local_vpk = os.path.join(PROJECT_ROOT, "VPKConverter", "vpk.exe")
    if os.path.isfile(local_vpk):
        candidates.append(local_vpk)
    drives = ["C", "D", "E", "F", "G", "H"]
    subpaths = [
        r"Steam\steamapps\common\Left 4 Dead 2\bin\vpk.exe",
        r"SteamLibrary\steamapps\common\Left 4 Dead 2\bin\vpk.exe",
        r"Program Files (x86)\Steam\steamapps\common\Left 4 Dead 2\bin\vpk.exe",
    ]
    for d in drives:
        for s in subpaths:
            p = "%s:\\%s" % (d, s)
            if os.path.isfile(p):
                candidates.append(p)
    return candidates[0] if candidates else ""


def default_config():
    return {
        "vpk_exe": autodetect_vpk_exe(),
        "out_dir": os.path.join(APP_DIR, "输出"),
        "cache_dir": os.path.join(APP_DIR, "缓存"),
    }


def load_config():
    cfg = default_config()
    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            for k in cfg:
                val = saved.get(k)
                if not val:
                    continue
                if k == "vpk_exe" and not os.path.isfile(val):
                    continue
                cfg[k] = val
        except Exception:
            pass
    return cfg


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass




class App:
    def __init__(self, root):
        self.root = root
        self.cfg = load_config()
        self.vpk_path = None
        self.src_key = None
        self.target_vars = {}
        self.busy = False

        root.title("求生之路2 武器模型转换工具")
        root.geometry("920x720")
        root.minsize(820, 640)

        self._build_config_area()
        self._build_source_area()
        self._build_target_area()
        self._build_action_area()
        self._build_log_area()

        self._set_status("就绪。请拖入或选择一个武器 VPK。")
        if not self.cfg.get("vpk_exe"):
            self.log("⚠ 未自动找到 vpk.exe，请在上方配置其路径（L4D2 安装目录的 bin\\vpk.exe）。")

        self._sync_cfg()


    def _build_config_area(self):
        frm = ttk.LabelFrame(self.root, text="① 工具与目录配置")
        frm.pack(fill="x", padx=10, pady=(10, 6))

        self.var_vpk = tk.StringVar(value=self.cfg.get("vpk_exe", ""))
        self.var_out = tk.StringVar(value=self.cfg.get("out_dir", ""))
        self.var_cache = tk.StringVar(value=self.cfg.get("cache_dir", ""))

        self._config_row(frm, 0, "vpk.exe：", self.var_vpk, self._pick_vpk,
                         "L4D2 安装目录\\bin\\vpk.exe（解包/打包用）")
        self._config_row(frm, 2, "输出目录：", self.var_out, self._pick_out,
                         "转换完成的 VPK 输出到这里")
        self._config_row(frm, 4, "缓存目录：", self.var_cache, self._pick_cache,
                         "临时解包/处理目录，可随时清空")
        frm.columnconfigure(1, weight=1)

    def _config_row(self, frm, r, label, var, cmd, hint):
        ttk.Label(frm, text=label).grid(row=r, column=0, sticky="w", padx=6, pady=(4, 0))
        ent = ttk.Entry(frm, textvariable=var)
        ent.grid(row=r, column=1, sticky="ew", padx=4, pady=(4, 0))
        ttk.Button(frm, text="浏览…", command=cmd, width=8).grid(row=r, column=2, padx=6, pady=(4, 0))
        ttk.Label(frm, text=hint, foreground="#888").grid(
            row=r + 1, column=1, columnspan=2, sticky="w", padx=6, pady=(0, 2))


    def _build_source_area(self):
        frm = ttk.LabelFrame(self.root, text="② 源 VPK（拖入此处，或点击选择）")
        frm.pack(fill="x", padx=10, pady=6)

        self.drop = tk.Label(frm, text="把 .vpk 文件拖到这里", relief="ridge", bd=2,
                             height=3, bg="#f3f3f3", fg="#666", cursor="hand2")
        self.drop.pack(fill="x", padx=8, pady=8)
        self.drop.bind("<Button-1>", lambda e: self._pick_vpk_file())

        if _HAS_DND:
            self.drop.drop_target_register(DND_FILES)
            self.drop.dnd_bind("<<Drop>>", self._on_drop)
        else:
            self.drop.config(text="把 .vpk 文件拖到这里\n（未装 tkinterdnd2，仅支持点击选择）")

        self.src_label = ttk.Label(frm, text="尚未加载 VPK。", font=("Microsoft YaHei UI", 10, "bold"))
        self.src_label.pack(anchor="w", padx=10, pady=(0, 8))


    def _build_target_area(self):
        frm = ttk.LabelFrame(self.root, text="③ 选择目标武器（可多选）")
        frm.pack(fill="both", expand=True, padx=10, pady=6)

        bar = ttk.Frame(frm)
        bar.pack(fill="x", padx=6, pady=(6, 0))
        ttk.Button(bar, text="全选同族", command=self._select_same).pack(side="left", padx=3)
        ttk.Button(bar, text="全选", command=lambda: self._select_all(True)).pack(side="left", padx=3)
        ttk.Button(bar, text="清空", command=lambda: self._select_all(False)).pack(side="left", padx=3)
        ttk.Label(bar, text="（标〔跨族〕者：能进游戏但动作可能异常）").pack(side="left", padx=10)


        canvas = tk.Canvas(frm, height=180, highlightthickness=0)
        sb = ttk.Scrollbar(frm, orient="vertical", command=canvas.yview)
        self.target_inner = ttk.Frame(canvas)
        self.target_inner.bind("<Configure>",
                               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.target_inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        sb.pack(side="right", fill="y", pady=6)
        self.target_hint = ttk.Label(self.target_inner, text="加载 VPK 后在此显示可转换的目标武器。")
        self.target_hint.pack(anchor="w", padx=6, pady=6)


    def _build_action_area(self):
        frm = ttk.Frame(self.root)
        frm.pack(fill="x", padx=10, pady=(0, 4))
        self.btn_convert = ttk.Button(frm, text="开始转换", command=self._start_convert)
        self.btn_convert.pack(side="left", padx=3)
        ttk.Button(frm, text="打开输出目录", command=self._open_out).pack(side="left", padx=3)
        ttk.Button(frm, text="清空缓存", command=self._clear_cache).pack(side="left", padx=3)
        self.status = ttk.Label(frm, text="", foreground="#0a0")
        self.status.pack(side="right", padx=6)


    def _build_log_area(self):
        frm = ttk.LabelFrame(self.root, text="④ 运行日志")
        frm.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        self.logbox = tk.Text(frm, height=10, wrap="word", state="disabled",
                              bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 9))
        sb = ttk.Scrollbar(frm, orient="vertical", command=self.logbox.yview)
        self.logbox.configure(yscrollcommand=sb.set)
        self.logbox.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        sb.pack(side="right", fill="y", pady=6)



    def log(self, msg):
        self.logbox.configure(state="normal")
        self.logbox.insert("end", msg + "\n")
        self.logbox.see("end")
        self.logbox.configure(state="disabled")
        self.root.update_idletasks()

    def _set_status(self, text, color="#0a0"):
        self.status.config(text=text, foreground=color)


    def _sync_cfg(self):
        self.cfg["vpk_exe"] = self.var_vpk.get().strip()
        self.cfg["out_dir"] = self.var_out.get().strip()
        self.cfg["cache_dir"] = self.var_cache.get().strip()
        save_config(self.cfg)

    def _pick_vpk(self):
        p = filedialog.askopenfilename(title="选择 vpk.exe",
                                       filetypes=[("vpk.exe", "vpk.exe"), ("可执行文件", "*.exe")])
        if p:
            self.var_vpk.set(p)
            self._sync_cfg()

    def _pick_out(self):
        p = filedialog.askdirectory(title="选择输出目录")
        if p:
            self.var_out.set(p)
            self._sync_cfg()

    def _pick_cache(self):
        p = filedialog.askdirectory(title="选择缓存目录")
        if p:
            self.var_cache.set(p)
            self._sync_cfg()


    def _pick_vpk_file(self):
        if self.busy:
            return
        p = filedialog.askopenfilename(title="选择武器 VPK", filetypes=[("VPK 文件", "*.vpk")])
        if p:
            self._load_vpk(p)

    def _on_drop(self, event):
        if self.busy:
            return
        data = event.data.strip()

        path = self._parse_drop(data)
        if path:
            self._load_vpk(path)

    @staticmethod
    def _parse_drop(data):
        data = data.strip()
        if data.startswith("{"):
            end = data.find("}")
            if end != -1:
                return data[1:end]
        return data.split()[0] if data else ""

    def _load_vpk(self, path):
        if not path.lower().endswith(".vpk"):
            messagebox.showerror("文件类型错误", "请选择 .vpk 文件。")
            return
        if not os.path.isfile(path):
            messagebox.showerror("文件不存在", "找不到文件：\n%s" % path)
            return
        self.vpk_path = path
        self.src_key = None
        self.log("加载 VPK：%s" % os.path.basename(path))
        try:
            files = vpk_tool.list_contents(path)
        except Exception as e:
            messagebox.showerror("VPK 读取失败", "无法读取该 VPK：\n%s" % e)
            self.src_label.config(text="读取失败。")
            return

        det = converter.detect_source(files)
        if det is None:
            self.src_label.config(text="✗ 无法识别该 VPK 替换的武器类型。")
            self._render_targets(None)
            messagebox.showwarning("无法识别",
                                   "未能识别该 VPK 替换的武器（未找到已知 v_/w_ 模型、音效或图标）。\n"
                                   "请确认这是一个武器替换 MOD。")
            return
        if det.get("chainsaw"):
            self.src_label.config(text="识别为：电锯（不在转换范围内）")
            self._render_targets(None)
            messagebox.showinfo("电锯", "识别为电锯，电锯不在转换范围内。")
            return

        self.src_key = det["key"]
        cat = {"primary": "主武器", "melee": "近战", "pistol": "手枪类"}.get(
            wd.get(self.src_key)["category"], "")
        txt = "识别源武器：%s〔%s〕  （依据：%s）" % (det["label"], cat, "、".join(det["by"]))
        if det["ambiguous"]:
            txt += "  ⚠多候选"
        self.src_label.config(text=txt)
        self.log("识别：%s（%s）" % (det["label"], "、".join(det["by"])))

        if wd.get(self.src_key)["category"] in wd.EXCLUDED_CATEGORIES:
            self._render_targets(None)
            messagebox.showinfo("暂不支持",
                                "识别为手枪类（手枪/马格南），按需求暂不加入转换列表。")
            return
        self._render_targets(self.src_key)


    def _render_targets(self, src_key):
        for w in self.target_inner.winfo_children():
            w.destroy()
        self.target_vars = {}
        if src_key is None:
            ttk.Label(self.target_inner, text="（无可用目标）").pack(anchor="w", padx=6, pady=6)
            return
        same, cross = wd.valid_targets(src_key)
        if not same and not cross:
            ttk.Label(self.target_inner, text="（该武器没有可转换目标）").pack(anchor="w", padx=6, pady=6)
            return

        if same:
            ttk.Label(self.target_inner, text="── 同动画族（无损，推荐）──",
                      foreground="#070").pack(anchor="w", padx=6, pady=(6, 0))
            for k in same:
                self._add_target_check(k, False)
        if cross:
            ttk.Label(self.target_inner, text="── 跨动画族（动作可能异常）──",
                      foreground="#a50").pack(anchor="w", padx=6, pady=(8, 0))
            for k in cross:
                self._add_target_check(k, True)

    def _add_target_check(self, key, cross):
        var = tk.BooleanVar(value=False)
        self.target_vars[key] = var
        label = wd.get(key)["label"] + ("　〔跨族〕" if cross else "")
        ttk.Checkbutton(self.target_inner, text=label, variable=var).pack(anchor="w", padx=20, pady=1)

    def _select_same(self):
        if not self.src_key:
            return
        same, _ = wd.valid_targets(self.src_key)
        sset = set(same)
        for k, v in self.target_vars.items():
            v.set(k in sset)

    def _select_all(self, val):
        for v in self.target_vars.values():
            v.set(val)


    def _start_convert(self):
        if self.busy:
            return
        self._sync_cfg()
        if not self.vpk_path:
            messagebox.showwarning("未选择 VPK", "请先拖入或选择一个武器 VPK。")
            return
        if not self.src_key:
            messagebox.showwarning("未识别", "尚未识别出源武器，无法转换。")
            return
        vpk_exe = self.var_vpk.get().strip()
        if not vpk_exe or not os.path.isfile(vpk_exe):
            messagebox.showerror("缺少 vpk.exe", "请先在上方配置正确的 vpk.exe 路径。")
            return
        targets = [k for k, v in self.target_vars.items() if v.get()]
        if not targets:
            messagebox.showwarning("未选择目标", "请至少勾选一个目标武器。")
            return

        out_dir = self.var_out.get().strip() or os.path.join(APP_DIR, "输出")
        cache_dir = self.var_cache.get().strip() or os.path.join(APP_DIR, "缓存")
        tools = {"vpk": vpk_exe}

        self.busy = True
        self.btn_convert.config(state="disabled")
        self._set_status("转换中…", "#a50")
        self.log("\n========== 开始转换（%d 个目标）==========" % len(targets))

        t = threading.Thread(target=self._run_convert,
                             args=(self.vpk_path, targets, tools, out_dir, cache_dir),
                             daemon=True)
        t.start()

    def _run_convert(self, vpk_path, targets, tools, out_dir, cache_dir):
        def prog(msg):
            self.root.after(0, self.log, msg)
        try:
            results = converter.convert(vpk_path, targets, tools, out_dir, cache_dir, progress=prog)
            self.root.after(0, self._on_done, results, None)
        except Exception as e:
            tb = traceback.format_exc()
            self.root.after(0, self._on_done, None, (str(e), tb))

    def _on_done(self, results, fatal):
        self.busy = False
        self.btn_convert.config(state="normal")

        if fatal is not None:
            err, tb = fatal
            self._set_status("转换失败", "#c00")
            self.log("✗ 失败：%s" % err)
            self.log(tb)
            messagebox.showerror("转换出错", "转换过程中出错：\n\n%s" % err)
            return

        ok = [r for r in results if r["ok"]]
        bad = [r for r in results if not r["ok"]]
        warns = [(r["label"], w) for r in ok for w in r["warnings"]]

        self.log("========== 完成：成功 %d，失败 %d ==========" % (len(ok), len(bad)))
        self._set_status("成功 %d / 失败 %d" % (len(ok), len(bad)),
                         "#0a0" if not bad else "#a50")


        if bad:
            detail = "\n\n".join("【%s】%s" % (r["label"], r["error"]) for r in bad)
            messagebox.showerror("部分目标转换失败", "以下目标转换失败：\n\n%s" % detail)


        if warns:
            wtext = "\n".join("【%s】%s" % (lbl, w) for lbl, w in warns)
            messagebox.showwarning("注意（跨动画族）", wtext)

        if ok and not bad:
            messagebox.showinfo("完成",
                                "全部 %d 个目标转换完成！\n输出目录：\n%s" % (len(ok), self.var_out.get()))


    def _open_out(self):
        out = self.var_out.get().strip() or os.path.join(APP_DIR, "输出")
        os.makedirs(out, exist_ok=True)
        try:
            os.startfile(out)
        except Exception:
            messagebox.showinfo("输出目录", out)

    def _clear_cache(self):
        import shutil
        cache = self.var_cache.get().strip() or os.path.join(APP_DIR, "缓存")
        if os.path.isdir(cache):
            if messagebox.askyesno("清空缓存", "确定清空缓存目录？\n%s" % cache):
                shutil.rmtree(cache, ignore_errors=True)
                os.makedirs(cache, exist_ok=True)
                self.log("已清空缓存。")
        else:
            self.log("缓存目录为空或不存在。")


def main():
    if _HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
