import os
import re
import shutil
import struct
import wave
from pathlib import Path

import weapon_data as wd
import sound_map as sm
import vpk_tool
import mdl_tool


TOOL_NAME_CN = "求生之路2 武器模型转换工具"
TOOL_NAME_EN = "L4D2 Weapon Porter"
TOOL_CREATOR = "爱芳乃岁岁年年"
UNKNOWN_AUTHOR = "Original author unknown / 原作者未知"


def _kv_escape(value):
    value = str(value).replace("\r", " ").replace("\n", " ")
    value = value.replace("\\", "/")
    value = value.replace('"', "'")
    while "  " in value:
        value = value.replace("  ", " ")
    return value.strip()


def _read_text(path):
    for enc in ("utf-8-sig", "utf-8", "gbk", "cp936", "latin-1"):
        try:
            return Path(path).read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except OSError:
            return ""
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _read_addoninfo_pairs(path):
    text = _read_text(path)
    pairs = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line in ("{", "}"):
            continue
        if line.startswith("//") or line.startswith("#"):
            continue
        m = re.match(r'^"?([^"\s{}]+)"?\s+(?:"([^"]*)"|([^\s{}]+))', line)
        if not m:
            continue
        key = m.group(1).strip()
        value = (m.group(2) if m.group(2) is not None else m.group(3) or "").strip()
        if key.lower() != "addoninfo":
            pairs.append((key, value))
    return pairs


def _get_pair(pairs, key, default=""):
    key_l = key.lower()
    for k, v in pairs:
        if k.lower() == key_l:
            return v
    return default


def _set_pair(pairs, key, value):
    key_l = key.lower()
    out = []
    written = False
    for k, v in pairs:
        if k.lower() == key_l:
            if not written:
                out.append((key, value))
                written = True
        else:
            out.append((k, v))
    if not written:
        out.append((key, value))
    return out


def _write_addoninfo(work, base_name, src_key, target_key):
    src_label = wd.get(src_key)["label"]
    target_label = wd.get(target_key)["label"]
    addoninfo = Path(work, "addoninfo.txt")
    pairs = _read_addoninfo_pairs(addoninfo)
    original_title = _get_pair(pairs, "addonTitle", base_name) or base_name
    original_author = _get_pair(pairs, "addonAuthor", "").strip() or UNKNOWN_AUTHOR
    original_description = _get_pair(pairs, "addonDescription", "").strip()
    converted_title = "%s -> %s" % (original_title, target_label)
    note_cn = "本版本由 %s 转换生成；转换工具制作人：%s；原作者：%s；源武器：%s；目标武器：%s。" % (
        TOOL_NAME_CN, TOOL_CREATOR, original_author, src_label, target_label)
    note_en = "Converted with %s; tool creator: %s; original author: %s; source weapon: %s; target weapon: %s." % (
        TOOL_NAME_EN, TOOL_CREATOR, original_author, src_label, target_label)
    converted_description = "%s | %s %s" % (original_description, note_cn, note_en) if original_description else "%s %s" % (note_cn, note_en)

    pairs = _set_pair(pairs, "addonSteamAppID", _get_pair(pairs, "addonSteamAppID", "550") or "550")
    pairs = _set_pair(pairs, "addonTitle", converted_title)
    pairs = _set_pair(pairs, "addonVersion", _get_pair(pairs, "addonVersion", "1.0") or "1.0")
    pairs = _set_pair(pairs, "addonAuthor", original_author)
    pairs = _set_pair(pairs, "addonDescription", converted_description)
    pairs = _set_pair(pairs, "addonOriginalTitle", original_title)
    pairs = _set_pair(pairs, "addonOriginalAuthor", original_author)
    pairs = _set_pair(pairs, "addonConvertedBy", TOOL_CREATOR)
    pairs = _set_pair(pairs, "addonConverter", "%s / %s" % (TOOL_NAME_CN, TOOL_NAME_EN))
    pairs = _set_pair(pairs, "addonConversionSourceWeapon", src_label)
    pairs = _set_pair(pairs, "addonConversionTargetWeapon", target_label)
    pairs = _set_pair(pairs, "addonConversionNote", "初版转换结果可能存在爆音或动作错位，请以游戏内实测为准。 Initial version output may contain audio pops or animation mismatch; in-game testing is recommended.")

    lines = ['"AddonInfo"', '{']
    for key, value in pairs:
        lines.append('\t"%s" "%s"' % (_kv_escape(key), _kv_escape(value)))
    lines.extend(['}', ''])
    addoninfo.write_text("\n".join(lines), encoding="utf-8")


class ConvertError(Exception):
    pass


def _norm(p):
    return p.replace("\\", "/").lower()


def _safe(name):
    return re.sub(r'[<>:"/\\|?*]+', "_", name).strip() or "weapon"




def detect_source(file_list):

    vmodels, wmodels, sroots, icons = set(), set(), set(), set()
    has_chainsaw = False
    for raw in file_list:
        p = _norm(raw)
        m = re.search(r"/(v_[a-z0-9_]+)\.mdl$", p) or re.match(r"(v_[a-z0-9_]+)\.mdl$", p)
        if m:
            vmodels.add(m.group(1))
        m = re.search(r"/(w_[a-z0-9_]+)\.mdl$", p) or re.match(r"(w_[a-z0-9_]+)\.mdl$", p)
        if m:
            wmodels.add(m.group(1))
        m = re.search(r"sound/weapons/([a-z0-9_]+)/", p)
        if m:
            sroots.add(m.group(1))
        m = re.search(r"materials/vgui/hud/(icon_[a-z0-9_]+)\.(vtf|vmt)$", p)
        if m:
            icons.add(m.group(1))
        if "v_chainsaw" in p or "icon_chainsaw" in p or "w_chainsaw" in p:
            has_chainsaw = True

    votes = {}

    def vote(key, weight, why):
        if key is None:
            return
        votes.setdefault(key, [0, []])
        votes[key][0] += weight
        votes[key][1].append(why)

    for v in vmodels:
        vote(wd.by_vmodel(v), 5, "视角模型 %s" % v)
    for w in wmodels:
        vote(wd.by_wmodel(w), 4, "世界模型 %s" % w)
    for s in sroots:
        vote(wd.by_sound_root(s), 2, "音效目录 %s" % s)
    for ic in icons:
        vote(wd.by_icon(ic), 1, "图标 %s" % ic)

    if has_chainsaw and not votes:
        return {"key": None, "label": "电锯（不在转换范围内）", "by": ["检测到 chainsaw"],
                "ambiguous": False, "candidates": [], "chainsaw": True}
    if not votes:
        return None

    ranked = sorted(votes.items(), key=lambda kv: kv[1][0], reverse=True)
    best_key, (best_score, whys) = ranked[0]
    ambiguous = len(ranked) > 1 and ranked[1][1][0] == best_score
    return {"key": best_key, "label": wd.get(best_key)["label"], "by": whys,
            "ambiguous": ambiguous, "candidates": [k for k, _ in ranked],
            "chainsaw": False}




def _decode_pcm_samples(raw, sample_width):
    if sample_width == 1:
        return [(b - 128) << 8 for b in raw]
    if sample_width == 2:
        count = len(raw) // 2
        return list(struct.unpack("<%dh" % count, raw))
    raise ConvertError("暂不支持 %d 字节采样宽度的 WAV 音频" % sample_width)


def _channels_for_frame(frame, src_channels, dst_channels):
    if src_channels == dst_channels:
        return frame
    if dst_channels == 2 and src_channels == 1:
        return (frame[0], frame[0])
    if dst_channels == 1:
        return (sum(frame) // len(frame),)
    if src_channels > dst_channels:
        return tuple(frame[:dst_channels])
    return tuple(list(frame) + [frame[-1]] * (dst_channels - src_channels))


def _resample_frames(frames, src_rate, dst_rate):
    if src_rate == dst_rate or not frames:
        return frames
    out_len = max(1, int(round(len(frames) * float(dst_rate) / float(src_rate))))
    ratio = float(src_rate) / float(dst_rate)
    last = len(frames) - 1
    out = []
    for i in range(out_len):
        pos = i * ratio
        lo = int(pos)
        hi = min(lo + 1, last)
        frac = pos - lo
        mixed = []
        for ch in range(len(frames[0])):
            val = frames[lo][ch] * (1.0 - frac) + frames[hi][ch] * frac
            mixed.append(int(round(val)))
        out.append(tuple(mixed))
    return out


def _write_pcm16(path, frames, channels, framerate):
    out = bytearray()
    for frame in frames:
        for sample in frame:
            sample = max(-32768, min(32767, int(sample)))
            out.extend(struct.pack("<h", sample))
    with wave.open(path, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(framerate)
        wav.writeframes(bytes(out))


def _apply_fade(frames, framerate, milliseconds=3.0):
    if not frames or framerate <= 0:
        return False
    fade_frames = int(round(framerate * (milliseconds / 1000.0)))
    fade_frames = max(1, min(fade_frames, len(frames)))
    if fade_frames == 1:
        zero = tuple(0 for _ in frames[0])
        changed = frames[0] != zero or frames[-1] != zero
        frames[0] = zero
        frames[-1] = zero
        return changed

    changed = False
    last = len(frames) - 1
    for i in range(fade_frames):
        gain = float(i) / float(fade_frames - 1)
        faded_in = tuple(int(round(sample * gain)) for sample in frames[i])
        faded_out = tuple(int(round(sample * gain)) for sample in frames[last - i])
        if faded_in != frames[i]:
            frames[i] = faded_in
            changed = True
        if faded_out != frames[last - i]:
            frames[last - i] = faded_out
            changed = True
    return changed


def _limit_peak(frames, limit_db=-1.0):
    peak = 0
    for frame in frames:
        for sample in frame:
            peak = max(peak, abs(sample))
    if peak <= 0:
        return False
    limit = int(round(32767 * (10.0 ** (limit_db / 20.0))))
    if peak <= limit:
        return False
    scale = float(limit) / float(peak)
    for i, frame in enumerate(frames):
        frames[i] = tuple(int(round(sample * scale)) for sample in frame)
    return True


def _pad_tail_to_floor(frames, channels, framerate, duration_floor, tolerance=0.1):
    if not frames or duration_floor is None or framerate <= 0:
        return False
    current_duration = len(frames) / float(framerate)
    if current_duration >= (duration_floor - tolerance):
        return False
    target_len = int(round(duration_floor * framerate))
    if target_len <= len(frames):
        return False
    silence = tuple(0 for _ in range(channels))
    frames.extend([silence] * (target_len - len(frames)))
    return True


def _normalize_wav(path, fmt, duration_floor=None, post_process=False):

    dst_channels, dst_width, dst_rate = fmt
    if dst_width != 2:
        raise ConvertError("内部错误：仅支持归一化到 16-bit PCM")
    try:
        with wave.open(path, "rb") as wav:
            src_channels = wav.getnchannels()
            src_width = wav.getsampwidth()
            src_rate = wav.getframerate()
            raw = wav.readframes(wav.getnframes())
    except wave.Error as e:
        raise ConvertError("无法读取 WAV 音频 %s：%s" % (os.path.basename(path), e))

    if (src_channels, src_width, src_rate) == fmt and not post_process and duration_floor is None:
        return False
    if src_channels <= 0:
        raise ConvertError("WAV 音频声道数异常：%s" % os.path.basename(path))

    samples = _decode_pcm_samples(raw, src_width)
    if len(samples) % src_channels != 0:
        raise ConvertError("WAV 音频帧数据异常：%s" % os.path.basename(path))

    frames = []
    for i in range(0, len(samples), src_channels):
        frame = samples[i:i + src_channels]
        frames.append(_channels_for_frame(frame, src_channels, dst_channels))
    frames = _resample_frames(frames, src_rate, dst_rate)
    changed = (src_channels, src_width, src_rate) != fmt

    if post_process:
        if _apply_fade(frames, dst_rate):
            changed = True
        if _limit_peak(frames):
            changed = True
    if _pad_tail_to_floor(frames, dst_channels, dst_rate, duration_floor):
        changed = True

    if changed:
        _write_pcm16(path, frames, dst_channels, dst_rate)
    return changed

def _walk_sound_files(src_dir):
    src_files = []
    for dirpath, _, files in os.walk(src_dir):
        for fn in files:
            full = os.path.join(dirpath, fn)
            rel = _norm(os.path.relpath(full, src_dir))
            src_files.append((full, rel))
    return sorted(src_files, key=lambda item: item[1])


def _copy_sound(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.copy2(src, dst)


def _melee_candidates(src_by_role, role):
    roles = [role] + list(sm.equivalent_roles(role))
    candidates = []
    seen = set()
    for r in roles:
        for item in src_by_role.get(r, []):
            if item[1] not in seen:
                candidates.append(item)
                seen.add(item[1])
    return candidates


def _convert_melee_sounds(work, src_key, target_key, log, warnings):
    src_root = wd.get(src_key)["sound_root"]
    dst_root = wd.get(target_key)["sound_root"]
    src_dir = os.path.join(work, "sound", "weapons", src_root)
    if not os.path.isdir(src_dir):
        msg = "源 VPK 无近战音效目录 sound/weapons/%s，跳过音效。" % src_root
        if warnings is not None:
            warnings.append(msg)
        log("  ⚠ " + msg)
        return 0, 0

    dst_dir = os.path.join(work, "sound", "weapons", dst_root)
    target_role_map = sm.role_to_paths(dst_root)
    target_standard = set()
    for paths in target_role_map.values():
        target_standard.update(_norm(p) for p in paths)

    src_files = _walk_sound_files(src_dir)
    src_by_role = {}
    for full, rel in src_files:
        if not rel.lower().endswith(".wav"):
            continue
        role = sm.standard_role_of(src_root, rel)
        if role and sm.is_melee_role(role):
            src_by_role.setdefault(role, []).append((full, rel))

    moved, kept, normalized = 0, 0, 0
    used_sources = set()
    written_targets = set()
    missing_targets = []

    for role, target_paths in target_role_map.items():
        candidates = _melee_candidates(src_by_role, role)
        if not candidates:
            missing_targets.extend(target_paths)
            continue
        for i, target_rel in enumerate(target_paths):
            if i >= len(candidates):
                missing_targets.append(target_rel)
                continue
            src_full, src_rel = candidates[i]
            dst = os.path.join(dst_dir, target_rel.replace("/", os.sep))
            _copy_sound(src_full, dst)
            used_sources.add(src_rel)
            written_targets.add(_norm(target_rel))
            moved += 1
            fmt = sm.target_wav_format(dst_root, target_rel)
            duration_floor = sm.target_wav_duration_floor(dst_root, target_rel)
            if fmt and _normalize_wav(dst, fmt, duration_floor=duration_floor, post_process=True):
                normalized += 1

    for full, rel in src_files:
        rel_norm = _norm(rel)
        if rel_norm in used_sources or rel_norm in written_targets or rel_norm in target_standard:
            continue
        dst = os.path.join(dst_dir, rel.replace("/", os.sep))
        _copy_sound(full, dst)
        kept += 1

    same_dir = _norm(src_dir) == _norm(dst_dir)
    if not same_dir:
        shutil.rmtree(src_dir, ignore_errors=True)

    if missing_targets:
        msg = "近战标准音效缺少可复用源声音，未生成：%s" % "、".join(missing_targets)
        if warnings is not None:
            warnings.append(msg)
        log("  ⚠ " + msg)

    log("  音效：%s/ -> %s/（标准映射 %d，自定义保留 %d，格式归一 %d）" %
        (src_root, dst_root, moved, kept, normalized))
    return moved, kept


def _convert_sounds(work, src_key, target_key, log, warnings=None):

    if wd.get(target_key)["category"] == "melee":
        return _convert_melee_sounds(work, src_key, target_key, log, warnings)

    src_root = wd.get(src_key)["sound_root"]
    dst_root = wd.get(target_key)["sound_root"]
    src_dir = os.path.join(work, "sound", "weapons", src_root)
    if not os.path.isdir(src_dir):
        log("  （源 VPK 无武器音效目录，跳过音效）")
        return 0, 0
    dst_dir = os.path.join(work, "sound", "weapons", dst_root)
    target_role_map = sm.role_to_path(dst_root)

    src_files = _walk_sound_files(src_dir)

    moved, kept, normalized = 0, 0, 0
    used = set()
    same_dir = _norm(src_dir) == _norm(dst_dir)
    for full, rel in src_files:
        role = sm.role_of(rel)
        target_rel = None
        if role and role in target_role_map and target_role_map[role] not in used:
            target_rel = target_role_map[role]
            used.add(target_rel)
            dst = os.path.join(dst_dir, target_rel.replace("/", os.sep))
            moved += 1
        else:
            dst = os.path.join(dst_dir, rel.replace("/", os.sep))
            kept += 1
        _copy_sound(full, dst)
        if target_rel:
            fmt = sm.target_wav_format(dst_root, target_rel)
            if fmt and _normalize_wav(dst, fmt):
                normalized += 1
    if not same_dir:
        shutil.rmtree(src_dir, ignore_errors=True)
    log("  音效：%s/ -> %s/（标准映射 %d，自定义保留 %d，格式归一 %d）" %
        (src_root, dst_root, moved, kept, normalized))
    return moved, kept




def _convert_icon(work, src_key, target_key, log):
    src_icon = wd.get(src_key)["icon"]
    dst_icon = wd.get(target_key)["icon"]
    hud = os.path.join(work, "materials", "vgui", "hud")
    if not os.path.isdir(hud):
        log("  （无 HUD 图标目录，跳过图标）")
        return 0
    n = 0
    for ext in (".vtf", ".vmt"):
        src = os.path.join(hud, src_icon + ext)
        if os.path.isfile(src):
            dst = os.path.join(hud, dst_icon + ext)
            if _norm(src) != _norm(dst):
                if os.path.exists(dst):
                    os.remove(dst)
                os.replace(src, dst)
            n += 1
    if n:
        log("  图标：%s -> %s" % (src_icon, dst_icon))
    else:
        log("  （未找到 %s 图标，跳过；游戏回退原版图标）" % src_icon)
    return n




def _convert_vscripts(work, src_key, target_key, log):
    vroot = os.path.join(work, "scripts", "vscripts")
    if not os.path.isdir(vroot):
        return 0
    src, dst = wd.get(src_key), wd.get(target_key)
    pairs = [(src["v_model"], dst["v_model"]), (src["w_model"], dst["w_model"]),
             (src["sound_root"], dst["sound_root"]), (src["icon"], dst["icon"])]
    n = 0
    for dirpath, _, files in os.walk(vroot):
        for fn in files:
            if not fn.lower().endswith(".nut"):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, "r", encoding="utf-8", errors="replace") as f:
                    txt = f.read()
            except OSError:
                continue
            orig = txt
            for a, b in pairs:
                if a and a != b:
                    txt = re.sub(re.escape(a), b, txt, flags=re.IGNORECASE)
            if txt != orig:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(txt)
                n += 1
                log("  vscript 改写：%s" % fn)
    if n == 0:
        log("  （vscript 无武器名引用或无需改写）")
    return n




def convert(vpk_path, target_keys, tools, out_dir, cache_dir, progress=None):

    def log(msg):
        if progress:
            progress(msg)

    if not os.path.isfile(vpk_path):
        raise ConvertError("VPK 文件不存在：%s" % vpk_path)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(vpk_path))[0]
    job_cache = os.path.join(cache_dir, "job_" + _safe(base_name))
    if os.path.isdir(job_cache):
        shutil.rmtree(job_cache, ignore_errors=True)
    os.makedirs(job_cache, exist_ok=True)

    src_unpack = os.path.join(job_cache, "src")
    os.makedirs(src_unpack, exist_ok=True)
    log("解包 %s ..." % os.path.basename(vpk_path))
    try:
        file_list = vpk_tool.unpack(vpk_path, src_unpack)
    except Exception as e:
        raise ConvertError("解包失败：%s" % e)

    det = detect_source(file_list)
    if det is None:
        raise ConvertError("无法识别该 VPK 替换的武器（未找到已知的 v_/w_ 模型、音效或图标）。")
    if det.get("chainsaw"):
        raise ConvertError("识别为电锯，电锯不在转换范围内。")
    src_key = det["key"]
    log("识别源武器：%s（依据：%s）" % (det["label"], "、".join(det["by"])))
    if det["ambiguous"]:
        log("  ⚠ 存在多个同分候选：%s，已取第一个。" %
            "、".join(wd.get(k)["label"] for k in det["candidates"][:3]))

    results = []
    for tkey in target_keys:
        try:
            results.append(_convert_to_target(
                src_unpack, src_key, tkey, tools, job_cache, base_name, out_dir, log))
        except Exception as e:
            results.append({"target": tkey, "label": wd.get(tkey)["label"],
                            "ok": False, "out_vpk": None, "warnings": [], "error": str(e)})
            log("✗ %s 失败：%s" % (wd.get(tkey)["label"], e))
    return results


def _convert_to_target(src_unpack, src_key, target_key, tools, job_cache,
                       base_name, out_dir, log):
    tw = wd.get(target_key)
    log("──── 转换为：%s ────" % tw["label"])
    warnings = []
    if not wd.is_same_family(src_key, target_key):
        msg = "跨动画族转换（%s -> %s）：可进游戏，但开火/换弹/开镜等动作可能异常，建议同族转换。" % (
            wd.get(src_key)["family"], tw["family"])
        warnings.append(msg)
        log("  ⚠ " + msg)

    work = os.path.join(job_cache, "to_" + target_key)
    if os.path.isdir(work):
        shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(src_unpack, work)


    converted = False
    for is_world in (False, True):
        r = mdl_tool.retarget_model(work, src_key, target_key, is_world, log=log)
        if r["found"]:
            converted = True
            metadata_patch = r.get("metadata_patch") or {}
            for warn in metadata_patch.get("warnings", []):
                warnings.append("V 模型 MDL 元数据：%s" % warn)
        elif not is_world:
            warnings.append("源 VPK 未包含视角模型 %s.mdl。" % wd.model_basename(src_key, False))
            log("  ⚠ 未找到视角模型 %s.mdl" % wd.model_basename(src_key, False))
        else:
            log("  （源 VPK 无世界模型 %s.mdl，跳过）" % wd.model_basename(src_key, True))
    if not converted:
        raise ConvertError("源 VPK 内未找到可转换的武器模型。")

    _convert_sounds(work, src_key, target_key, log, warnings)
    _convert_icon(work, src_key, target_key, log)
    _convert_vscripts(work, src_key, target_key, log)
    _write_addoninfo(work, base_name, src_key, target_key)

    out_vpk = os.path.join(out_dir, "%s__%s.vpk" % (_safe(base_name), target_key))
    log("  打包 -> %s" % os.path.basename(out_vpk))
    try:
        vpk_tool.pack(work, out_vpk, tools["vpk"])
    except Exception as e:
        raise ConvertError("打包失败：%s" % e)
    log("✓ 完成：%s" % os.path.basename(out_vpk))
    return {"target": target_key, "label": tw["label"], "ok": True,
            "out_vpk": out_vpk, "warnings": warnings, "error": None}
