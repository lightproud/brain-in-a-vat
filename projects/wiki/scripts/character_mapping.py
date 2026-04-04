#!/usr/bin/env python3
"""
Shared character ID → wiki page title mappings.

All fetch_*.py scripts import from here instead of maintaining separate copies.
To add a new character, add entries to FANDOM_PAGE_MAP and BILI_PAGE_MAP below.

Usage:
  from character_mapping import FANDOM_PAGE_MAP, BILI_PAGE_MAP, VOICE_PAGE_MAP
"""

# Character ID -> Fandom page title (English wiki)
# Used by: fetch_portraits.py, fetch_skills.py, fetch_cards.py, fetch_stats.py
FANDOM_PAGE_MAP = {
    "alva": "Alva",
    "doll": "Doll",
    "ramona-timeworn": "Ramona:_Timeworn",
    "ogier": "Ogier",
    "lotan": "Lotan",
    "ramona": "Ramona",
    "pandya": "Pandya",
    "nodera": "Nodera",
    "galen": "Galen",
    "nymphia": "Nymphia",
    "lily": "Lily",
    "danmo": "Danmo",
    "miryam": "Miryam",
    "tulu": "Tulu",
    "divine-king-tulu": "Divine_King_Tulu",
    "celeste": "Celeste",
    "goliath": "Goliath",
    "shan": "Shan",
    "aurita": "Aurita",
    "caecus": "Caecus",
    "faros": "Faros",
    "uvhash": "Uvhash",
    "rhea": "Rhea",
    "sorel": "Sorel",
    "thais": "Thais",
    "alice": "Alice",
    "faint": "Faint",
    "agrippa": "Agrippa",
    "shilo": "Shilo",
    "erica": "Erica",
    "liz": "Liz",
    "daffodil": "Daffodil",
    "winkle": "Winkle",
    "casiah": "Casiah",
    "jenkins": "Jenkins",
    "tincture": "Tincture",
    "horla": "Horla",
    "karen": "Karen",
    "hameln": "Hameln",
    "murphy": "Murphy",
    "salvador": "Salvador",
    "tawil": "Tawil",
    "wanda": "Wanda",
    "aigis": "Aigis",
    "doll-inferno": "Doll:_Inferno",
    "24": "24_(character)",
    "clementine": "Clementine",
    "corposant": "Corposant",
    "kathigu-ra": "Kathigu-Ra",
    "murphy-fauxborn": "Murphy:_Fauxborn",
    "mouchette": "Mouchette",
    "xu": "Xu",
    "castor": "Castor",
    "pollux": "Pollux",
    "helot": "Helot",
    "leigh": "Leigh",
    "doresain": "Doresain",
    "pickman": "Pickman",
    "arachne": "Arachne",
}

# Character ID -> Bilibili Wiki page title (Chinese wiki)
# Used by: fetch_portraits.py, fetch_skills.py
BILI_PAGE_MAP = {
    "alva": "阿尔瓦", "doll": "玩偶", "ramona-timeworn": "拉蒙娜·经年",
    "ogier": "奥吉尔", "lotan": "洛坦", "ramona": "拉蒙娜",
    "pandya": "潘迪亚", "nodera": "诺德拉", "galen": "加仑",
    "nymphia": "宁芙", "lily": "莉莉", "danmo": "丹莫",
    "miryam": "弥利亚姆", "tulu": "图鲁", "divine-king-tulu": "图鲁·神王",
    "celeste": "希莱斯特", "goliath": "戈利亚", "shan": "杉",
    "aurita": "奥瑞塔", "caecus": "凯刻斯", "faros": "法罗斯",
    "uvhash": "尤乌哈希", "rhea": "蕾亚", "sorel": "索蕾尔",
    "thais": "塔薇", "alice": "爱丽丝", "faint": "费恩特",
    "agrippa": "阿格里帕", "shilo": "希洛", "erica": "艾瑞卡",
    "liz": "莉兹", "daffodil": "水仙", "winkle": "环娜",
    "casiah": "迦叶", "jenkins": "詹金斯", "tincture": "酊剂",
    "horla": "奥尔拉", "karen": "珈伦", "hameln": "哈姆林",
    "murphy": "墨菲", "salvador": "萨尔瓦多", "tawil": "塔薇儿",
    "wanda": "旺达", "aigis": "艾癸斯", "doll-inferno": "玩偶·炼狱",
    "24": "24", "clementine": "克莱门汀", "corposant": "圣艾尔摩之火",
    "kathigu-ra": "卡蒂古拉", "murphy-fauxborn": "墨菲·诞妄",
    "mouchette": "穆雪特", "xu": "勖", "castor": "卡斯托尔",
    "pollux": "波吕克斯", "helot": "希洛特", "leigh": "莱克",
    "doresain": "多瑞塞", "pickman": "皮克曼", "arachne": "阿拉克涅",
}

# Character ID -> Fandom voice/quote subpage
# Currently only 10 characters have voice pages on Fandom.
# TODO: Expand as more voice pages become available.
VOICE_PAGE_MAP = {
    "tulu": "Tulu/Voice",
    "doll": "Doll/Voice",
    "ramona": "Ramona/Voice",
    "alva": "Alva/Voice",
    "lily": "Lily/Voice",
    "24": "24_(character)/Voice",
    "miryam": "Miryam/Voice",
    "tawil": "Tawil/Voice",
    "celeste": "Celeste/Voice",
    "liz": "Liz/Voice",
}


def get_all_character_ids():
    """Return sorted list of all character IDs with Fandom page mappings."""
    return sorted(FANDOM_PAGE_MAP.keys())


if __name__ == "__main__":
    print(f"Fandom mappings:  {len(FANDOM_PAGE_MAP)} characters")
    print(f"Bilibili mappings: {len(BILI_PAGE_MAP)} characters")
    print(f"Voice mappings:    {len(VOICE_PAGE_MAP)} characters")
    fandom_only = set(FANDOM_PAGE_MAP) - set(BILI_PAGE_MAP)
    bili_only = set(BILI_PAGE_MAP) - set(FANDOM_PAGE_MAP)
    if fandom_only:
        print(f"Fandom only (no Bilibili): {fandom_only}")
    if bili_only:
        print(f"Bilibili only (no Fandom): {bili_only}")
