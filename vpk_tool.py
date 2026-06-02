import os
import struct
import subprocess
import tempfile
import shutil
import time

VPK_SIGNATURE = 0x55AA1234


class VpkError(Exception):
    pass


def _read_cstr(f):
    out = bytearray()
    while True:
        c = f.read(1)
        if c in (b"\x00", b""):
            break
        out += c
    return out.decode("utf-8", "replace")


def read_directory(vpk_path):

    entries = []
    with open(vpk_path, "rb") as f:
        sig, ver = struct.unpack("<II", f.read(8))
        if sig != VPK_SIGNATURE:
            raise VpkError("不是有效的 VPK 文件（签名不匹配）。可能是分卷 _dir.vpk，请提供 _dir.vpk。")
        if ver == 1:
            (tree_size,) = struct.unpack("<I", f.read(4))
        elif ver == 2:
            struct.unpack("<IIIII", f.read(20))
        else:
            raise VpkError("不支持的 VPK 版本：%d" % ver)

        while True:
            ext = _read_cstr(f)
            if ext == "":
                break
            while True:
                path = _read_cstr(f)
                if path == "":
                    break
                while True:
                    name = _read_cstr(f)
                    if name == "":
                        break



                    crc, plen, arch, offset, elen, term = struct.unpack("<IHHIIH", f.read(18))
                    preload = f.read(plen)
                    if path in ("", " "):
                        full = "%s.%s" % (name, ext)
                    else:
                        full = "%s/%s.%s" % (path, name, ext)
                    entries.append({
                        "path": full,
                        "preload": preload,
                        "offset": offset,
                        "archive_index": arch,
                        "length": elen,
                        "crc": crc,
                    })
        data_start = f.tell()
    return entries, data_start


def unpack(vpk_path, out_dir):

    entries, data_start = read_directory(vpk_path)
    written = []
    with open(vpk_path, "rb") as f:
        for e in entries:
            rel = e["path"]
            dst = os.path.join(out_dir, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if e["length"] == 0:
                data = e["preload"]
            else:
                if e["archive_index"] != 0x7FFF:
                    raise VpkError(
                        "VPK 为多分卷格式（archive_index=%d），本工具仅支持单文件 vpk。"
                        % e["archive_index"]
                    )
                f.seek(data_start + e["offset"])
                data = e["preload"] + f.read(e["length"])
            with open(dst, "wb") as out:
                out.write(data)
            written.append(rel)
    return written


def list_contents(vpk_path):

    entries, _ = read_directory(vpk_path)
    return [e["path"] for e in entries]


def pack(src_dir, out_vpk, vpk_exe):

    if not vpk_exe or not os.path.isfile(vpk_exe):
        raise VpkError("找不到 vpk.exe，请在面板中正确配置其路径。")
    src_dir = os.path.abspath(src_dir)
    if not os.path.isdir(src_dir):
        raise VpkError("待打包目录不存在：%s" % src_dir)

    last_log = ""
    attempts = 3
    for attempt in range(attempts):
        staging = tempfile.mkdtemp(prefix="wp_pack_")
        work = os.path.join(staging, "c")
        produced = os.path.join(staging, "c.vpk")
        try:
            shutil.copytree(src_dir, work)
            proc = subprocess.run(
                [vpk_exe, "c"],
                cwd=staging,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=_no_window_flag(),
            )
            last_log = proc.stdout.decode("utf-8", "replace") if proc.stdout else ""

            for _ in range(20):
                if os.path.exists(produced) and os.path.getsize(produced) > 0:
                    break
                time.sleep(0.1)

            if os.path.exists(produced) and os.path.getsize(produced) > 0:
                os.makedirs(os.path.dirname(os.path.abspath(out_vpk)), exist_ok=True)
                if os.path.exists(out_vpk):
                    os.remove(out_vpk)
                shutil.move(produced, out_vpk)
                return out_vpk, last_log
        finally:
            shutil.rmtree(staging, ignore_errors=True)

        if attempt < attempts - 1:
            time.sleep(0.5 * (attempt + 1))

    raise VpkError("vpk.exe 打包失败（已重试 %d 次未生成 vpk）。\n输出：\n%s" % (attempts, last_log))


def _no_window_flag():

    if os.name == "nt":
        return 0x08000000
    return 0
