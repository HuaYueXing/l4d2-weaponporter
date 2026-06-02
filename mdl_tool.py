import os
import struct

import weapon_data as wd

MDL_MAGIC = b"IDST"
NAME_OFFSET = 12
NAME_SIZE = 64
STUDIOHDR_LENGTH_OFFSET = 76
STUDIOHDR_NUMSEQ_OFFSET = 188
STUDIOHDR_SEQINDEX_OFFSET = 192

SEQDESC_SIZE = 212
SEQDESC_LABEL_OFFSET = 4
SEQDESC_ACTIVITY_OFFSET = 8
SEQDESC_NUMEVENTS_OFFSET = 24
SEQDESC_EVENTINDEX_OFFSET = 28

STUDIOEVENT_SIZE = 80
STUDIOEVENT_OPTIONS_OFFSET = 12
STUDIOEVENT_OPTIONS_SIZE = 64


MODEL_EXTS = [".mdl", ".vvd", ".phy",
              ".dx90.vtx", ".dx80.vtx", ".sw.vtx", ".vtx", ".xbox.vtx"]

HUNTING_RIFLE_ACTIVITY_MAP = {
    "ACT_VM_IDLE": "ACT_VM_IDLE_SNIPER",
    "ACT_VM_DEPLOY": "ACT_VM_DEPLOY_SNIPER",
    "ACT_VM_DEPLOY_LAYER": "ACT_VM_DEPLOY_SNIPER_LAYER",
    "ACT_VM_RELOAD": "ACT_VM_RELOAD_SNIPER",
    "ACT_VM_RELOAD_LAYER": "ACT_VM_RELOAD_SNIPER_LAYER",
    "ACT_VM_RELOAD_EMPTY": "ACT_VM_RELOAD_EMPTY_SNIPER",
    "ACT_VM_RELOAD_EMPTY_LAYER": "ACT_VM_RELOAD_EMPTY_SNIPER_LAYER",
    "ACT_VM_RELOAD_CLIPOUT": "ACT_VM_RELOAD_CLIPOUT_SNIPER",
    "ACT_VM_RELOAD_CLIPOUT_LAYER": "ACT_VM_RELOAD_CLIPOUT_SNIPER_LAYER",
    "ACT_VM_RELOAD_EMPTY_CLIPOUT": "ACT_VM_RELOAD_EMPTY_CLIPOUT_SNIPER",
    "ACT_VM_RELOAD_EMPTY_CLIPOUT_LAYER": "ACT_VM_RELOAD_EMPTY_CLIPOUT_SNIPER_LAYER",
    "ACT_VM_RELOAD_EMPTY_CLIPIN": "ACT_VM_RELOAD_EMPTY_CLIPIN_SNIPER",
    "ACT_VM_RELOAD_EMPTY_CLIPIN_LAYER": "ACT_VM_RELOAD_EMPTY_CLIPIN_SNIPER_LAYER",
    "ACT_VM_PRIMARYATTACK": "ACT_VM_PRIMARYATTACK_SNIPER",
    "ACT_VM_PRIMARYATTACK_LAYER": "ACT_VM_SHOOT_SNIPER_LAYER",
    "ACT_VM_MELEE": "ACT_VM_MELEE_SNIPER",
    "ACT_VM_MELEE_LAYER": "ACT_VM_MELEE_SNIPER_LAYER",
    "ACT_VM_HELPINGHAND_EXTEND": "ACT_VM_HELPINGHAND_EXTEND_SNIPER",
    "ACT_VM_HELPINGHAND_EXTEND_LAYER": "ACT_VM_HELPINGHAND_EXTEND_SNIPER_LAYER",
    "ACT_VM_HELPINGHAND_LOOP": "ACT_VM_HELPINGHAND_LOOP_SNIPER",
    "ACT_VM_HELPINGHAND_LOOP_LAYER": "ACT_VM_HELPINGHAND_LOOP_SNIPER_LAYER",
    "ACT_VM_HELPINGHAND_RETRACT": "ACT_VM_HELPINGHAND_RETRACT_SNIPER",
    "ACT_VM_HELPINGHAND_RETRACT_LAYER": "ACT_VM_HELPINGHAND_RETRACT_SNIPER_LAYER",
    "ACT_VM_ITEMPICKUP_EXTEND": "ACT_VM_ITEMPICKUP_EXTEND_SNIPER",
    "ACT_VM_ITEMPICKUP_EXTEND_LAYER": "ACT_VM_ITEMPICKUP_EXTEND_SNIPER_LAYER",
    "ACT_VM_ITEMPICKUP_LOOP": "ACT_VM_ITEMPICKUP_LOOP_SNIPER",
    "ACT_VM_ITEMPICKUP_LOOP_LAYER": "ACT_VM_ITEMPICKUP_LOOP_SNIPER_LAYER",
    "ACT_VM_ITEMPICKUP_RETRACT": "ACT_VM_ITEMPICKUP_RETRACT_SNIPER",
    "ACT_VM_ITEMPICKUP_RETRACT_LAYER": "ACT_VM_ITEMPICKUP_RETRACT_SNIPER_LAYER",
    "ACT_VM_PICKUP": "ACT_VM_PICKUP_SNIPER",
    "ACT_VM_PICKUP_LAYER": "ACT_VM_PICKUP_SNIPER_LAYER",
    "ACT_VM_PICKUP_CLIPIN": "ACT_VM_PICKUP_CLIPIN_SNIPER",
    "ACT_VM_PICKUP_CLIPIN_LAYER": "ACT_VM_PICKUP_CLIPIN_SNIPER_LAYER",
    "ACT_VM_PICKUP_CHARGING": "ACT_VM_PICKUP_CHARGING_SNIPER",
    "ACT_VM_PICKUP_CHARGING_LAYER": "ACT_VM_PICKUP_CHARGING_SNIPER_LAYER",
}

HUNTING_RIFLE_EVENT_SUFFIX_MAP = {
    "deploy": "Deploy",
    "bolt": "BoltBack",
    "boltback": "BoltBack",
    "bolt_back": "BoltBack",
    "boltpullback": "BoltBack",
    "boltforward": "BoltForward",
    "bolt_forward": "BoltForward",
    "boltpullforward": "BoltForward",
    "clipin": "ClipIn",
    "clip_in": "ClipIn",
    "cliplocked": "ClipIn",
    "clip_locked": "ClipIn",
    "clipout": "ClipOut",
    "clip_out": "ClipOut",
    "helpinghandextend": "HelpingHandExtend",
    "helping_hand_extend": "HelpingHandExtend",
    "helpinghandretract": "HelpingHandRetract",
    "helping_hand_retract": "HelpingHandRetract",
    "itempickupextend": "ItemPickupExtend",
    "item_pickup_extend": "ItemPickupExtend",
    "itempickupretract": "ItemPickupRetract",
    "item_pickup_retract": "ItemPickupRetract",
}

MELEE_TARGET_PROFILE = {
    "baseball_bat": {"center": 1, "left": 1, "right": 1, "hard": 1, "secondary": 1},
    "cricket_bat": {"center": 1, "left": 1, "right": 1, "hard": 1, "secondary": 1},
    "knife": {"right": 1, "secondary": 2},
    "machete": {"primary": 1, "left": 1, "right": 1, "hard": 1, "secondary": 2},
    "pitchfork": {"primary": 2, "left": 2, "right": 2, "secondary": 2},
    "fireaxe": {"primary": 3, "left": 2, "hard": 1, "secondary": 1},
    "electric_guitar": {"primary": 3, "left": 2, "hard": 1, "secondary": 1},
    "crowbar": {"primary": 2, "left": 1, "secondary": 1},
    "frying_pan": {"primary": 1, "left": 1, "hard": 1, "secondary": 1},
    "tonfa": {"primary": 3, "left": 1, "secondary": 2},
    "shovel": {"primary": 2, "left": 2, "secondary": 1},
    "katana": {"center": 2, "left": 2, "secondary": 1},
    "golfclub": {"center": 2, "left": 2, "secondary": 1},
}

MELEE_BASE_ACTIVITY = {
    "primary": "ACT_VM_PRIMARYATTACK",
    "center": "ACT_VM_HITCENTER",
    "left": "ACT_VM_HITLEFT",
    "right": "ACT_VM_HITRIGHT",
    "hard": "ACT_VM_SWINGHARD",
    "secondary": "ACT_VM_SECONDARYATTACK",
}

MELEE_DEFAULT_LAYER_ACTIVITY = {
    "primary": "ACT_VM_SHOOT_LAYER",
    "center": "ACT_VM_HITLEFT_LAYER",
    "left": "ACT_VM_HITLEFT_LAYER",
    "right": "ACT_VM_HITRIGHT_LAYER",
    "hard": "ACT_VM_SWINGHARD_LAYER",
    "secondary": "ACT_VM_SECONDARYATTACK_LAYER",
}

MELEE_SHOOT_LAYER_TARGETS = {"baseball_bat", "cricket_bat", "katana", "golfclub"}

MELEE_BASE_ACTIVITY_TO_ROLE = {
    "ACT_VM_PRIMARYATTACK": ("primary", False),
    "ACT_VM_HITCENTER": ("center", False),
    "ACT_VM_HITLEFT": ("left", False),
    "ACT_VM_HITRIGHT": ("right", False),
    "ACT_VM_SWINGHARD": ("hard", False),
    "ACT_VM_SECONDARYATTACK": ("secondary", False),
}

MELEE_LAYER_ACTIVITY_MATCH = {
    "ACT_VM_SHOOT_LAYER": ("primary", "center", "left", "right"),
    "ACT_VM_HITLEFT_LAYER": ("left",),
    "ACT_VM_HITRIGHT_LAYER": ("right",),
    "ACT_VM_SWINGHARD_LAYER": ("hard",),
    "ACT_VM_SECONDARYATTACK_LAYER": ("secondary",),
}

MELEE_REASSIGN_PREFERENCES = {
    "primary": ("primary", "center", "left", "right", "hard"),
    "center": ("center", "primary", "left", "right", "hard"),
    "left": ("left", "primary", "center", "right", "hard"),
    "right": ("right", "left", "primary", "center", "hard"),
    "hard": ("hard", "primary", "center", "left", "right"),
    "secondary": ("secondary",),
}

MELEE_EVENT_PREFIXES = {
    "axe", "bat", "cricketbat", "crowbar", "fryingpan", "golfclub",
    "guitar", "katana", "knife", "machete", "pitchfork", "shovel", "tonfa",
}

MELEE_TARGET_EVENT_PREFIX = {
    "machete": "machete",
    "fireaxe": "Axe",
    "crowbar": "Crowbar",
    "frying_pan": "FryingPan",
    "cricket_bat": "CricketBat",
    "baseball_bat": "bat",
    "tonfa": "Tonfa",
    "katana": "Katana",
    "electric_guitar": "Guitar",
    "golfclub": "GolfClub",
    "pitchfork": "Pitchfork",
    "shovel": "Shovel",
    "knife": "Knife",
}

MELEE_EVENT_SUFFIX_MAP = {
    "deploy": "Deploy",
    "draw": "Deploy",
    "miss": "Miss",
    "break": "Break",
    "impactworld": "ImpactWorld",
    "impact_world": "ImpactWorld",
    "hitworld": "ImpactWorld",
    "hit_world": "ImpactWorld",
    "helpinghandextend": "HelpingHandExtend",
    "helping_hand_extend": "HelpingHandExtend",
    "helpinghandretract": "HelpingHandRetract",
    "helping_hand_retract": "HelpingHandRetract",
    "itempickupextend": "ItemPickupExtend",
    "item_pickup_extend": "ItemPickupExtend",
    "itempickupretract": "ItemPickupRetract",
    "item_pickup_retract": "ItemPickupRetract",
}


class MdlError(Exception):
    pass


def _read_cstring(data, offset):
    if offset <= 0 or offset >= len(data):
        return ""
    end = data.find(b"\x00", offset)
    if end < 0:
        end = len(data)
    return data[offset:end].decode("latin-1", "replace")


def _write_fixed_cstring(data, offset, size, text):
    raw = text.encode("latin-1")
    if len(raw) >= size:
        raise MdlError("MDL 事件字符串过长（>%d 字节）：%s" % (size - 1, text))
    data[offset:offset + size] = raw + b"\x00" * (size - len(raw))


def read_internal_name(mdl_path):
    with open(mdl_path, "rb") as f:
        head = f.read(NAME_OFFSET + NAME_SIZE)
    if head[:4] != MDL_MAGIC:
        raise MdlError("不是有效的 MDL 文件（缺少 IDST 标识）：%s" % mdl_path)
    return head[NAME_OFFSET:NAME_OFFSET + NAME_SIZE].split(b"\x00")[0].decode("latin-1")


def patch_internal_name(mdl_path, new_internal):

    nb = new_internal.encode("latin-1")
    if len(nb) >= NAME_SIZE:
        raise MdlError("内嵌模型名过长（>%d 字节）：%s" % (NAME_SIZE - 1, new_internal))
    with open(mdl_path, "r+b") as f:
        head = f.read(NAME_OFFSET + NAME_SIZE)
        if head[:4] != MDL_MAGIC:
            raise MdlError("不是有效的 MDL 文件：%s" % mdl_path)
        old = head[NAME_OFFSET:NAME_OFFSET + NAME_SIZE].split(b"\x00")[0].decode("latin-1")
        f.seek(NAME_OFFSET)
        f.write(nb + b"\x00" * (NAME_SIZE - len(nb)))
    return old, new_internal


def checksum(mdl_path):
    with open(mdl_path, "rb") as f:
        d = f.read(12)
    return struct.unpack("<i", d[8:12])[0]


def _hunting_rifle_event_prefixes(src_key):
    prefixes = []
    src_prefix = wd.get(src_key).get("snd_prefix")
    if src_prefix and src_prefix != "HuntingRifle":
        prefixes.append(src_prefix)

    if src_prefix == "Sniper_Military":
        prefixes.append("Sniper__Military")
    return prefixes


def _hunting_rifle_event_name(prefix, option):
    suffix = option[len(prefix) + 1:]
    normalized = HUNTING_RIFLE_EVENT_SUFFIX_MAP.get(suffix.lower(), suffix)
    return "HuntingRifle." + normalized


def patch_hunting_rifle_metadata(mdl_path, src_key):

    with open(mdl_path, "rb") as f:
        data = bytearray(f.read())
    if data[:4] != MDL_MAGIC:
        raise MdlError("不是有效的 MDL 文件：%s" % mdl_path)
    if len(data) < STUDIOHDR_SEQINDEX_OFFSET + 4:
        raise MdlError("MDL 头过短，无法读取 sequence 信息：%s" % mdl_path)

    old_checksum = struct.unpack("<i", data[8:12])[0]
    numseq = struct.unpack_from("<i", data, STUDIOHDR_NUMSEQ_OFFSET)[0]
    seqindex = struct.unpack_from("<i", data, STUDIOHDR_SEQINDEX_OFFSET)[0]
    if numseq < 0 or seqindex <= 0:
        raise MdlError("MDL sequence 表异常：numseq=%d seqindex=%d" % (numseq, seqindex))
    if seqindex + numseq * SEQDESC_SIZE > len(data):
        raise MdlError("MDL sequence 表越界：numseq=%d seqindex=%d" % (numseq, seqindex))

    appended = {}
    activity_changes = 0
    event_changes = 0
    prefixes = _hunting_rifle_event_prefixes(src_key)

    for i in range(numseq):
        seq_off = seqindex + i * SEQDESC_SIZE
        act_rel = struct.unpack_from("<i", data, seq_off + SEQDESC_ACTIVITY_OFFSET)[0]
        old_activity = _read_cstring(data, seq_off + act_rel) if act_rel else ""
        new_activity = HUNTING_RIFLE_ACTIVITY_MAP.get(old_activity)
        if new_activity:
            if new_activity not in appended:
                appended[new_activity] = len(data)
                data.extend(new_activity.encode("latin-1") + b"\x00")
            struct.pack_into("<i", data, seq_off + SEQDESC_ACTIVITY_OFFSET,
                             appended[new_activity] - seq_off)
            activity_changes += 1

        numevents = struct.unpack_from("<i", data, seq_off + SEQDESC_NUMEVENTS_OFFSET)[0]
        eventindex = struct.unpack_from("<i", data, seq_off + SEQDESC_EVENTINDEX_OFFSET)[0]
        if numevents < 0:
            raise MdlError("MDL event 数量异常：sequence=%d numevents=%d" % (i, numevents))
        for j in range(numevents):
            event_off = seq_off + eventindex + j * STUDIOEVENT_SIZE
            opt_off = event_off + STUDIOEVENT_OPTIONS_OFFSET
            if opt_off + STUDIOEVENT_OPTIONS_SIZE > len(data):
                raise MdlError("MDL event 表越界：sequence=%d event=%d" % (i, j))
            option = _read_cstring(data, opt_off)
            option_low = option.lower()
            for prefix in prefixes:
                mark = prefix + "."
                if option_low.startswith(mark.lower()):
                    new_option = _hunting_rifle_event_name(prefix, option)
                    if new_option != option:
                        _write_fixed_cstring(data, opt_off, STUDIOEVENT_OPTIONS_SIZE, new_option)
                        event_changes += 1
                    break

    struct.pack_into("<i", data, STUDIOHDR_LENGTH_OFFSET, len(data))
    if old_checksum != struct.unpack("<i", data[8:12])[0]:
        raise MdlError("MDL checksum 被意外改变：%s" % mdl_path)

    with open(mdl_path, "wb") as f:
        f.write(data)
    return {
        "activities": activity_changes,
        "events": event_changes,
        "strings_appended": len(appended),
        "checksum": old_checksum,
        "length": len(data),
    }


def _mdl_sequence_bounds(data):
    if data[:4] != MDL_MAGIC:
        raise MdlError("不是有效的 MDL 文件")
    if len(data) < STUDIOHDR_SEQINDEX_OFFSET + 4:
        raise MdlError("MDL 头过短，无法读取 sequence 信息")
    numseq = struct.unpack_from("<i", data, STUDIOHDR_NUMSEQ_OFFSET)[0]
    seqindex = struct.unpack_from("<i", data, STUDIOHDR_SEQINDEX_OFFSET)[0]
    if numseq < 0 or seqindex <= 0:
        raise MdlError("MDL sequence 表异常：numseq=%d seqindex=%d" % (numseq, seqindex))
    if seqindex + numseq * SEQDESC_SIZE > len(data):
        raise MdlError("MDL sequence 表越界：numseq=%d seqindex=%d" % (numseq, seqindex))
    return numseq, seqindex


def _append_activity(data, appended, seq_off, activity):
    if activity not in appended:
        appended[activity] = len(data)
        data.extend(activity.encode("latin-1") + b"\x00")
    struct.pack_into("<i", data, seq_off + SEQDESC_ACTIVITY_OFFSET, appended[activity] - seq_off)


def _read_sequence_entry(data, seqindex, index):
    seq_off = seqindex + index * SEQDESC_SIZE
    label_rel = struct.unpack_from("<i", data, seq_off + SEQDESC_LABEL_OFFSET)[0]
    act_rel = struct.unpack_from("<i", data, seq_off + SEQDESC_ACTIVITY_OFFSET)[0]
    label = _read_cstring(data, seq_off + label_rel) if label_rel else ""
    activity = _read_cstring(data, seq_off + act_rel) if act_rel else ""
    return {
        "index": index,
        "seq_off": seq_off,
        "label": label,
        "activity_rel": act_rel,
        "activity_abs": (seq_off + act_rel) if act_rel else 0,
        "activity": activity,
    }


def _load_sequence_entries(data):
    numseq, seqindex = _mdl_sequence_bounds(data)
    seqs = [_read_sequence_entry(data, seqindex, i) for i in range(numseq)]
    return numseq, seqindex, seqs


def _sequence_activity_offsets(seqs):
    offsets = {}
    for seq in seqs:
        if seq["activity_rel"]:
            offsets.setdefault(seq["activity"], seq["activity_abs"])
    return offsets


def _sequence_activity_counts(seqs):
    counts = {}
    for seq in seqs:
        activity = seq["activity"]
        if activity:
            counts[activity] = counts.get(activity, 0) + 1
    return counts


def _ensure_activity_string(data, activity_offsets, appended, activity):
    if activity in activity_offsets:
        return activity_offsets[activity]
    if activity in appended:
        return appended[activity]
    abs_off = len(data)
    if activity:
        data.extend(activity.encode("latin-1") + b"\x00")
    else:
        data.extend(b"\x00")
    appended[activity] = abs_off
    activity_offsets[activity] = abs_off
    return abs_off


def _set_sequence_activity(data, seq, abs_off):
    rel = abs_off - seq["seq_off"]
    struct.pack_into("<i", data, seq["seq_off"] + SEQDESC_ACTIVITY_OFFSET, rel)
    seq["activity_rel"] = rel
    seq["activity_abs"] = abs_off
    seq["activity"] = _read_cstring(data, abs_off) if abs_off else ""


def _melee_activity_for_role(target_key, role, is_layer):
    if not is_layer:
        return MELEE_BASE_ACTIVITY[role]
    if role in ("center", "left", "right") and target_key in MELEE_SHOOT_LAYER_TARGETS:
        return "ACT_VM_SHOOT_LAYER"
    return MELEE_DEFAULT_LAYER_ACTIVITY[role]


def _parse_melee_attack_groups(seqs):
    groups = []
    orphans = []
    i = 0
    while i < len(seqs):
        seq = seqs[i]
        source = MELEE_BASE_ACTIVITY_TO_ROLE.get(seq["activity"])
        if source:
            role, _ = source
            group = {"role": role, "base": seq, "layer": None}
            if i + 1 < len(seqs):
                next_seq = seqs[i + 1]
                valid_roles = MELEE_LAYER_ACTIVITY_MATCH.get(next_seq["activity"])
                if valid_roles and role in valid_roles:
                    group["layer"] = next_seq
                    i += 1
            groups.append(group)
        elif seq["activity"] in MELEE_LAYER_ACTIVITY_MATCH:
            orphans.append(seq)
        i += 1
    return groups, orphans


def _pick_melee_target_role(source_role, remaining):
    for role in MELEE_REASSIGN_PREFERENCES[source_role]:
        if remaining.get(role, 0) > 0:
            return role
    return None


def _reassign_sequence_activity(data, seq, new_activity, activity_offsets, appended, changes):
    old_activity = seq["activity"]
    if new_activity == old_activity:
        return False
    abs_off = _ensure_activity_string(data, activity_offsets, appended, new_activity)
    _set_sequence_activity(data, seq, abs_off)
    changes.append({
        "index": seq["index"],
        "label": seq["label"],
        "from": old_activity,
        "to": new_activity,
    })
    return True


def _disable_sequence_activity(data, seq, activity_offsets, appended, disabled):
    old_activity = seq["activity"]
    if not old_activity:
        return False
    abs_off = _ensure_activity_string(data, activity_offsets, appended, "")
    _set_sequence_activity(data, seq, abs_off)
    disabled.append({
        "index": seq["index"],
        "label": seq["label"],
        "from": old_activity,
    })
    return True


def _missing_melee_profile(remaining):
    missing = []
    for role, count in remaining.items():
        if count > 0:
            missing.append("%s x%d" % (MELEE_BASE_ACTIVITY[role], count))
    return missing


def _melee_event_option(option, target_key):
    if not option or " " in option or "." not in option:
        return None
    prefix, suffix = option.split(".", 1)
    if prefix.lower() not in MELEE_EVENT_PREFIXES:
        return None
    target_prefix = MELEE_TARGET_EVENT_PREFIX.get(target_key)
    if not target_prefix:
        return None
    target_suffix = MELEE_EVENT_SUFFIX_MAP.get(suffix.lower(), suffix)
    if target_key == "baseball_bat" and target_suffix == "Deploy":
        target_suffix = "deploy"
    return "%s.%s" % (target_prefix, target_suffix)


def patch_melee_metadata(mdl_path, target_key):

    with open(mdl_path, "rb") as f:
        data = bytearray(f.read())
    if data[:4] != MDL_MAGIC:
        raise MdlError("不是有效的 MDL 文件：%s" % mdl_path)

    old_checksum = struct.unpack("<i", data[8:12])[0]
    _, _, seqs = _load_sequence_entries(data)
    activity_offsets = _sequence_activity_offsets(seqs)
    appended = {}
    activity_changes = 0
    event_changes = 0
    reassigned = []
    disabled = []
    before_counts = _sequence_activity_counts(seqs)
    profile = dict(MELEE_TARGET_PROFILE.get(target_key, {}))
    groups, orphans = _parse_melee_attack_groups(seqs)

    for group in groups:
        target_role = _pick_melee_target_role(group["role"], profile)
        if target_role is None:
            if _disable_sequence_activity(data, group["base"], activity_offsets, appended, disabled):
                activity_changes += 1
            if group["layer"] and _disable_sequence_activity(data, group["layer"], activity_offsets,
                                                             appended, disabled):
                activity_changes += 1
            continue

        profile[target_role] -= 1
        if _reassign_sequence_activity(
                data, group["base"], _melee_activity_for_role(target_key, target_role, False),
                activity_offsets, appended, reassigned):
            activity_changes += 1
        if group["layer"] and _reassign_sequence_activity(
                data, group["layer"], _melee_activity_for_role(target_key, target_role, True),
                activity_offsets, appended, reassigned):
            activity_changes += 1

    for seq in orphans:
        if _disable_sequence_activity(data, seq, activity_offsets, appended, disabled):
            activity_changes += 1

    for seq in seqs:
        seq_off = seq["seq_off"]
        numevents = struct.unpack_from("<i", data, seq_off + SEQDESC_NUMEVENTS_OFFSET)[0]
        eventindex = struct.unpack_from("<i", data, seq_off + SEQDESC_EVENTINDEX_OFFSET)[0]
        if numevents < 0:
            raise MdlError("MDL event 数量异常：sequence=%d numevents=%d" % (seq["index"], numevents))
        for j in range(numevents):
            event_off = seq_off + eventindex + j * STUDIOEVENT_SIZE
            opt_off = event_off + STUDIOEVENT_OPTIONS_OFFSET
            if opt_off + STUDIOEVENT_OPTIONS_SIZE > len(data):
                raise MdlError("MDL event 表越界：sequence=%d event=%d" % (seq["index"], j))
            option = _read_cstring(data, opt_off)
            new_option = _melee_event_option(option, target_key)
            if new_option and new_option != option:
                _write_fixed_cstring(data, opt_off, STUDIOEVENT_OPTIONS_SIZE, new_option)
                event_changes += 1

    warnings = []
    missing = _missing_melee_profile(profile)
    if missing:
        warnings.append("目标近战攻击 activity 不足：%s" % ", ".join(missing))

    if appended:
        struct.pack_into("<i", data, STUDIOHDR_LENGTH_OFFSET, len(data))
    if old_checksum != struct.unpack("<i", data[8:12])[0]:
        raise MdlError("MDL checksum 被意外改变：%s" % mdl_path)

    after_counts = _sequence_activity_counts(seqs)
    with open(mdl_path, "wb") as f:
        f.write(data)
    return {
        "kind": "melee",
        "activities": activity_changes,
        "events": event_changes,
        "strings_appended": len(appended),
        "checksum": old_checksum,
        "length": len(data),
        "reassigned_sequences": reassigned,
        "disabled_sequences": disabled,
        "activity_counts_before": before_counts,
        "activity_counts_after": after_counts,
        "warnings": warnings,
    }


def find_model_group(root, basename):

    blow = basename.lower()
    out = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            low = fn.lower()
            stem = low.split(".", 1)[0]
            if stem == blow:
                suffix = low[len(stem):]
                out.append((os.path.join(dirpath, fn), suffix))
    return out


def retarget_model(root, src_key, target_key, is_world, log=None):

    def _log(m):
        if log:
            log(m)

    src_base = wd.model_basename(src_key, is_world)
    group = find_model_group(root, src_base)
    if not group:
        return {"found": False, "files": 0}

    tgt_base = wd.model_basename(target_key, is_world)
    tgt_dir_rel = wd.model_dir(target_key, is_world)
    new_internal = wd.internal_name(target_key, is_world)





    moved = 0
    dst_dir_abs = None
    for full, suffix in group:
        src_dir_abs = os.path.dirname(full)

        rel_dir = os.path.relpath(src_dir_abs, root).replace("\\", "/").lower()
        if rel_dir == tgt_dir_rel.lower():
            dst_dir_abs = src_dir_abs
        else:
            dst_dir_abs = os.path.join(root, tgt_dir_rel.replace("/", os.sep))
            os.makedirs(dst_dir_abs, exist_ok=True)
        dst = os.path.join(dst_dir_abs, tgt_base + suffix)
        if os.path.abspath(full) != os.path.abspath(dst):
            if os.path.exists(dst):
                os.remove(dst)
            os.replace(full, dst)
        moved += 1


    new_mdl = os.path.join(dst_dir_abs, tgt_base + ".mdl")
    old_internal = None
    metadata_patch = None
    if os.path.isfile(new_mdl):
        old_internal, _ = patch_internal_name(new_mdl, new_internal)
        if target_key == "hunting_rifle" and not is_world:
            metadata_patch = patch_hunting_rifle_metadata(new_mdl, src_key)
        elif wd.get(target_key)["category"] == "melee" and not is_world:
            metadata_patch = patch_melee_metadata(new_mdl, target_key)

    kind = "世界" if is_world else "视角"
    _log("  %s模型：%s.* -> %s.*（%d 个文件，内嵌名 %s -> %s）" %
         (kind, src_base, tgt_base, moved, old_internal, new_internal))
    if metadata_patch:
        name = "15连狙" if metadata_patch.get("kind") != "melee" else "近战"
        disabled_count = len(metadata_patch.get("disabled_sequences", []))
        _log("  %s MDL 元数据：activity %d，event %d，禁用 %d，追加字符串 %d，checksum 保持 %d" %
             (name, metadata_patch["activities"], metadata_patch["events"], disabled_count,
              metadata_patch["strings_appended"], metadata_patch["checksum"]))
        for warn in metadata_patch.get("warnings", []):
            _log("  ⚠ " + warn)
    return {"found": True, "files": moved, "old_internal": old_internal,
            "new_internal": new_internal, "dst_dir": dst_dir_abs,
            "mdl_path": new_mdl if os.path.isfile(new_mdl) else None,
            "metadata_patch": metadata_patch}
