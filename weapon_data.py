VIEW_DIR_STD = "models/v_models"
WORLD_DIR_STD = "models/w_models/weapons"
MELEE_DIR = "models/weapons/melee"




WEAPONS = {

    "rifle_m16": {
        "label": "M16 突击步枪", "category": "primary", "family": "rifle",
        "v_model": "v_rifle", "w_model": "w_rifle_m16a2",
        "sound_root": "rifle", "icon": "icon_rifle", "snd_prefix": "Rifle",
        "ref_qc": "v_rifle.qc",
    },
    "rifle_ak47": {
        "label": "AK47", "category": "primary", "family": "rifle",
        "v_model": "v_rifle_ak47", "w_model": "w_rifle_ak47",
        "sound_root": "rifle_ak47", "icon": "icon_rifle_ak47", "snd_prefix": "AK47",
        "ref_qc": "v_rifle_ak47.qc",
    },
    "rifle_desert": {
        "label": "SCAR 战斗步枪", "category": "primary", "family": "rifle",
        "v_model": "v_desert_rifle", "w_model": "w_desert_rifle",
        "sound_root": "rifle_desert", "icon": "icon_rifle_desert", "snd_prefix": "Rifle_Desert",
        "ref_qc": "v_desert_rifle.qc",
    },
    "rifle_sg552": {
        "label": "SG552", "category": "primary", "family": "rifle",
        "v_model": "v_rif_sg552", "w_model": "w_rifle_sg552",
        "sound_root": "sg552", "icon": "icon_rifle_sg552", "snd_prefix": "SG552",
        "ref_qc": "v_rif_sg552.qc",
    },

    "rifle_m60": {
        "label": "M60 机枪", "category": "primary", "family": "m60",
        "v_model": "v_m60", "w_model": "w_m60",
        "sound_root": "machinegun_m60", "icon": "icon_rifle_m60", "snd_prefix": "M60",
        "ref_qc": "v_m60.qc",
    },

    "smg_uzi": {
        "label": "UZI 冲锋枪", "category": "primary", "family": "smg",
        "v_model": "v_smg", "w_model": "w_smg_uzi",
        "sound_root": "smg", "icon": "icon_smg", "snd_prefix": "SMG",
        "ref_qc": "v_smg.qc",
    },
    "smg_silenced": {
        "label": "MAC-10 消音冲锋枪", "category": "primary", "family": "smg",
        "v_model": "v_silenced_smg", "w_model": "w_smg_a",
        "sound_root": "smg_silenced", "icon": "icon_smg_silenced", "snd_prefix": "SMG_Silenced",
        "ref_qc": "v_silenced_smg.qc",
    },
    "smg_mp5": {
        "label": "MP5 冲锋枪", "category": "primary", "family": "smg",
        "v_model": "v_smg_mp5", "w_model": "w_smg_mp5",
        "sound_root": "mp5navy", "icon": "icon_smg_mp5", "snd_prefix": "MP5N",
        "ref_qc": "v_smg_mp5.qc",
    },

    "shotgun_pump": {
        "label": "木喷 (Pump Shotgun)", "category": "primary", "family": "shotgun_pump",
        "v_model": "v_pumpshotgun", "w_model": "w_shotgun",
        "sound_root": "shotgun", "icon": "icon_pumpshotgun", "snd_prefix": "Shotgun",
        "ref_qc": "v_pumpshotgun.qc",
    },
    "shotgun_chrome": {
        "label": "铁喷 (Chrome Shotgun)", "category": "primary", "family": "shotgun_pump",
        "v_model": "v_shotgun_chrome", "w_model": "w_pumpshotgun_a",
        "sound_root": "shotgun_chrome", "icon": "icon_shotgun_chrome", "snd_prefix": "Shotgun_Chrome",
        "ref_qc": "v_shotgun_chrome.qc",
    },

    "autoshotgun": {
        "label": "连喷 (Auto Shotgun M4)", "category": "primary", "family": "shotgun_auto",
        "v_model": "v_autoshotgun", "w_model": "w_autoshot_m4super",
        "sound_root": "auto_shotgun", "icon": "icon_autoshotgun", "snd_prefix": "AutoShotgun",
        "ref_qc": "v_autoshotgun.qc",
    },
    "shotgun_spas": {
        "label": "SPAS 连喷", "category": "primary", "family": "shotgun_auto",
        "v_model": "v_shotgun_spas", "w_model": "w_shotgun_spas",
        "sound_root": "auto_shotgun_spas", "icon": "icon_shotgun_spas", "snd_prefix": "AutoShotgun_Spas",
        "ref_qc": "v_shotgun_spas.qc",
    },

    "hunting_rifle": {
        "label": "猎枪 / 15连狙", "category": "primary", "family": "sniper_bolt",
        "v_model": "v_huntingrifle", "w_model": "w_sniper_mini14",
        "sound_root": "hunting_rifle", "icon": "icon_hunting_rifle", "snd_prefix": "HuntingRifle",
        "ref_qc": "v_huntingrifle.qc",
    },

    "sniper_military": {
        "label": "军狙 / 30连狙", "category": "primary", "family": "sniper_mil",
        "v_model": "v_sniper_military", "w_model": "w_sniper_military",
        "sound_root": "sniper_military", "icon": "icon_sniper_military", "snd_prefix": "Sniper_Military",
        "ref_qc": "v_sniper_military.qc",
    },
    "sniper_awp": {
        "label": "AWP 狙击枪", "category": "primary", "family": "sniper_mil",
        "v_model": "v_snip_awp", "w_model": "w_sniper_awp",
        "sound_root": "awp", "icon": "icon_sniper_awp", "snd_prefix": "Weapon_AWP",
        "ref_qc": "v_snip_awp.qc",
    },
    "sniper_scout": {
        "label": "Scout 侦察狙", "category": "primary", "family": "sniper_mil",
        "v_model": "v_snip_scout", "w_model": "w_sniper_scout",
        "sound_root": "scout", "icon": "icon_sniper_scout", "snd_prefix": "Weapon_Scout",
        "ref_qc": "v_snip_scout.qc",
    },

    "grenade_launcher": {
        "label": "榴弹发射器", "category": "primary", "family": "grenade",
        "v_model": "v_grenade_launcher", "w_model": "w_grenade_launcher",
        "sound_root": "grenade_launcher", "icon": "icon_grenade_launcher", "snd_prefix": "GrenadeLauncher",
        "ref_qc": "v_grenade_launcher.qc",
    },


    "machete": {
        "label": "砍刀", "category": "melee", "family": "melee",
        "v_model": "v_machete", "w_model": "w_machete", "melee_dir": True,
        "sound_root": "machete", "icon": "icon_machete", "snd_prefix": "Machete",
        "ref_qc": None,
    },
    "fireaxe": {
        "label": "消防斧", "category": "melee", "family": "melee",
        "v_model": "v_fireaxe", "w_model": "w_fireaxe", "melee_dir": True,
        "sound_root": "axe", "icon": "icon_fireaxe", "snd_prefix": "Fireaxe",
        "ref_qc": None,
    },
    "crowbar": {
        "label": "撬棍", "category": "melee", "family": "melee",
        "v_model": "v_crowbar", "w_model": "w_crowbar", "melee_dir": True,
        "sound_root": "crowbar", "icon": "icon_crowbar", "snd_prefix": "Crowbar",
        "ref_qc": None,
    },
    "frying_pan": {
        "label": "平底锅", "category": "melee", "family": "melee",
        "v_model": "v_frying_pan", "w_model": "w_frying_pan", "melee_dir": True,
        "sound_root": "pan", "icon": "icon_frying_pan", "snd_prefix": "FryingPan",
        "ref_qc": None,
    },
    "cricket_bat": {
        "label": "板球拍", "category": "melee", "family": "melee",
        "v_model": "v_cricket_bat", "w_model": "w_cricket_bat", "melee_dir": True,
        "sound_root": "cricketbat", "icon": "icon_cricket_bat", "snd_prefix": "CricketBat",
        "ref_qc": None,
    },
    "baseball_bat": {
        "label": "棒球棍", "category": "melee", "family": "melee",
        "v_model": "v_bat", "w_model": "w_bat", "melee_dir": True,
        "sound_root": "bat", "icon": "icon_baseball_bat", "snd_prefix": "Bat",
        "ref_qc": None,
    },
    "tonfa": {
        "label": "警棍", "category": "melee", "family": "melee",
        "v_model": "v_tonfa", "w_model": "w_tonfa", "melee_dir": True,
        "sound_root": "tonfa", "icon": "icon_tonfa", "snd_prefix": "Tonfa",
        "ref_qc": None,
    },
    "katana": {
        "label": "武士刀", "category": "melee", "family": "melee",
        "v_model": "v_katana", "w_model": "w_katana", "melee_dir": True,
        "sound_root": "katana", "icon": "icon_katana", "snd_prefix": "Katana",
        "ref_qc": None,
    },
    "electric_guitar": {
        "label": "电吉他", "category": "melee", "family": "melee",
        "v_model": "v_electric_guitar", "w_model": "w_electric_guitar", "melee_dir": True,
        "sound_root": "guitar", "icon": "icon_electric_guitar", "snd_prefix": "Guitar",
        "ref_qc": None,
    },
    "golfclub": {
        "label": "高尔夫球杆", "category": "melee", "family": "melee",
        "v_model": "v_golfclub", "w_model": "w_golfclub", "melee_dir": True,
        "sound_root": "golf_club", "icon": "icon_golfclub", "snd_prefix": "GolfClub",
        "ref_qc": None,
    },
    "pitchfork": {
        "label": "草叉", "category": "melee", "family": "melee",
        "v_model": "v_pitchfork", "w_model": "w_pitchfork", "melee_dir": True,
        "sound_root": "pitchfork", "icon": "icon_pitchfork", "snd_prefix": "Pitchfork",
        "ref_qc": None,
    },
    "shovel": {
        "label": "铁铲", "category": "melee", "family": "melee",
        "v_model": "v_shovel", "w_model": "w_shovel", "melee_dir": True,
        "sound_root": "shovel", "icon": "icon_shovel", "snd_prefix": "Shovel",
        "ref_qc": None,
    },
    "knife": {

        "label": "小刀", "category": "melee", "family": "melee",
        "v_model": "v_knife_t", "w_model": "w_knife_t", "melee_dir": False,
        "sound_root": "knife", "icon": "icon_knife", "snd_prefix": "Knife",
        "ref_qc": None,
    },


    "pistol": {
        "label": "手枪 (P220)", "category": "pistol", "family": "pistol",
        "v_model": "v_pistola", "w_model": "w_pistol_a", "melee_dir": False,
        "sound_root": "pistol", "icon": "icon_pistol", "snd_prefix": "Pistol_Silver",
        "ref_qc": "v_pistola.qc",
    },
    "magnum": {
        "label": "马格南 (沙鹰)", "category": "pistol", "family": "pistol",
        "v_model": "v_desert_eagle", "w_model": "w_desert_eagle", "melee_dir": False,
        "sound_root": "magnum", "icon": "icon_pistol_magnum", "snd_prefix": "Magnum",
        "ref_qc": "v_desert_eagle.qc",
    },
}


CHAINSAW_VMODEL = "v_chainsaw"
CHAINSAW_ICON = "icon_chainsaw"


EXCLUDED_CATEGORIES = {"pistol"}


def all_keys():
    return list(WEAPONS.keys())


def get(key):
    return WEAPONS[key]


def by_vmodel(vname):

    vlow = vname.lower()
    for k, w in WEAPONS.items():
        if w["v_model"].lower() == vlow:
            return k
    return None


def by_wmodel(wname):
    wlow = wname.lower()
    for k, w in WEAPONS.items():
        if w["w_model"].lower() == wlow:
            return k
    return None


def by_sound_root(root):
    rlow = root.lower()
    for k, w in WEAPONS.items():
        if w["sound_root"].lower() == rlow:
            return k
    return None


def by_icon(icon_name):
    ilow = icon_name.lower()
    for k, w in WEAPONS.items():
        if w["icon"].lower() == ilow:
            return k
    return None


def valid_targets(source_key):

    src = WEAPONS.get(source_key)
    if src is None or src["category"] in EXCLUDED_CATEGORIES:
        return [], []
    same, cross = [], []
    for k, w in WEAPONS.items():
        if k == source_key:
            continue
        if w["category"] != src["category"]:
            continue
        if w["category"] in EXCLUDED_CATEGORIES:
            continue
        if w["family"] == src["family"]:
            same.append(k)
        else:
            cross.append(k)
    return same, cross


def is_same_family(a, b):
    return WEAPONS[a]["family"] == WEAPONS[b]["family"]












def model_dir(key, is_world):

    w = WEAPONS[key]
    if w.get("melee_dir"):
        return "models/weapons/melee"
    if is_world:
        return "models/w_models/weapons"
    return "models/v_models"


def model_basename(key, is_world):
    return WEAPONS[key]["w_model"] if is_world else WEAPONS[key]["v_model"]


def internal_name(key, is_world):

    w = WEAPONS[key]
    if w.get("melee_dir"):
        sub = "weapons\\melee"
    elif is_world:

        sub = "w_models\\Weapons" if key != "knife" else "w_models\\weapons"
    else:
        sub = "v_models"
    return "%s\\%s.mdl" % (sub, model_basename(key, is_world))
