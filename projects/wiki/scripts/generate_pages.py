#!/usr/bin/env python3
"""
Auto-generate VitePress character detail pages from characters.json + equipment.json.

Usage:
    python generate_pages.py                  # generate all langs
    python generate_pages.py --lang zh        # Chinese only
    python generate_pages.py --lang en        # English only
    python generate_pages.py --lang ja        # Japanese only
    python generate_pages.py --dry-run        # preview without writing
    python generate_pages.py --dry-run --lang zh
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent                       # projects/wiki
DATA_DIR = PROJECT_ROOT / "data" / "db"
DOCS_DIR = PROJECT_ROOT / "docs"

CHARACTERS_JSON = DATA_DIR / "characters.json"
EQUIPMENT_JSON = DATA_DIR / "equipment.json"

# ---------------------------------------------------------------------------
# i18n labels
# ---------------------------------------------------------------------------
LABELS: dict[str, dict[str, str]] = {
    "zh": {
        "title_suffix": "忘却前夜 Wiki",
        "rarity": "稀有度",
        "realm": "界域",
        "role": "职能",
        "limited": "限定",
        "obtain": "获取",
        "yes": "是",
        "no": "否",
        "attr": "属性",
        "value": "值",
        "intro": "简介",
        "skills": "技能",
        "command_cards": "指令卡",
        "rouse": "觉醒卡",
        "exalt": "狂气爆发",
        "overexalt": "超限爆发",
        "enlighten": "启灵",
        "talent": "天赋",
        "recommended_equipment": "推荐装备",
        "signature_wheel": "专属命轮",
        "recommended_wheel": "推荐命轮",
        "pending": "数据待补充",
        "card_name": "卡名",
        "cost": "费用",
        "effect": "效果",
        "level": "等级",
        "note": "备注",
        "description_tpl": "{name}（{name_en}）{realm}属性{role}角色详细资料",
    },
    "en": {
        "title_suffix": "Morimens Wiki",
        "rarity": "Rarity",
        "realm": "Realm",
        "role": "Role",
        "limited": "Limited",
        "obtain": "Availability",
        "yes": "Yes",
        "no": "No",
        "attr": "Attribute",
        "value": "Value",
        "intro": "Introduction",
        "skills": "Skills",
        "command_cards": "Command Cards",
        "rouse": "Rouse (Awakening)",
        "exalt": "Exalt",
        "overexalt": "Over-Exalt",
        "enlighten": "Enlighten",
        "talent": "Talent",
        "recommended_equipment": "Recommended Equipment",
        "signature_wheel": "Signature Wheel",
        "recommended_wheel": "Recommended Wheel",
        "pending": "Data pending",
        "card_name": "Card",
        "cost": "Cost",
        "effect": "Effect",
        "level": "Level",
        "note": "Note",
        "description_tpl": "Full profile of {name_en} ({name}), a {realm} {role} in Morimens",
    },
    "ja": {
        "title_suffix": "忘却前夜 Wiki",
        "rarity": "レアリティ",
        "realm": "界域",
        "role": "役割",
        "limited": "限定",
        "obtain": "入手方法",
        "yes": "はい",
        "no": "いいえ",
        "attr": "属性",
        "value": "値",
        "intro": "紹介",
        "skills": "スキル",
        "command_cards": "指令カード",
        "rouse": "覚醒カード",
        "exalt": "狂気爆発",
        "overexalt": "超限爆発",
        "enlighten": "啓霊",
        "talent": "天賦",
        "recommended_equipment": "推奨装備",
        "signature_wheel": "専用命輪",
        "recommended_wheel": "推奨命輪",
        "pending": "データ準備中",
        "card_name": "カード名",
        "cost": "コスト",
        "effect": "効果",
        "level": "レベル",
        "note": "備考",
        "description_tpl": "{name}（{name_en}）{realm}属性{role}キャラクター詳細",
    },
}

REALM_NAMES: dict[str, dict[str, str]] = {
    "zh": {"chaos": "混沌", "aequor": "深海", "caro": "血肉", "ultra": "超维"},
    "en": {"chaos": "Chaos", "aequor": "Aequor", "caro": "Caro", "ultra": "Ultra"},
    "ja": {"chaos": "混沌", "aequor": "深海", "caro": "血肉", "ultra": "超次元"},
}

REALM_CSS: dict[str, str] = {
    "chaos": "realm-chaos",
    "aequor": "realm-aequor",
    "caro": "realm-caro",
    "ultra": "realm-ultra",
}

ROLE_NAMES: dict[str, dict[str, str]] = {
    "zh": {
        "attack": "输出",
        "sub_attack": "副输出",
        "support": "辅助",
        "defense": "防御",
        "healer": "治疗",
        "chorus": "合唱",
        "dps": "输出",
    },
    "en": {
        "attack": "Attack",
        "sub_attack": "Sub-Attack",
        "support": "Support",
        "defense": "Defense",
        "healer": "Healer",
        "chorus": "Chorus",
        "dps": "DPS",
    },
    "ja": {
        "attack": "攻撃型",
        "sub_attack": "副攻撃型",
        "support": "支援型",
        "defense": "防御型",
        "healer": "回復型",
        "chorus": "合唱型",
        "dps": "攻撃型",
    },
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_characters() -> list[dict[str, Any]]:
    with open(CHARACTERS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    chars = list(data.get("characters", []))
    chars.extend(data.get("sr_characters", []))
    return chars


def load_equipment() -> dict[str, Any]:
    with open(EQUIPMENT_JSON, encoding="utf-8") as f:
        return json.load(f)


def build_wheel_index(equip_data: dict[str, Any]) -> dict[str, list[dict]]:
    """Build a mapping from character name -> list of wheels."""
    index: dict[str, list[dict]] = {}
    wheels = equip_data.get("wheels_of_destiny", {})
    for category_key, wheel_list in wheels.items():
        if not isinstance(wheel_list, list):
            continue
        for wheel in wheel_list:
            if not isinstance(wheel, dict):
                continue
            char_field = wheel.get("character")
            if char_field:
                # character field like "希莱斯特(Celeste)" — extract the Chinese name
                cn_name = char_field.split("(")[0].strip()
                index.setdefault(cn_name, []).append(wheel)
            # Also check recommended list
            for rec_name in wheel.get("recommended", []):
                index.setdefault(rec_name, []).append(wheel)
    return index


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def _esc(text: Any) -> str:
    """Ensure we have a string and lightly escape pipe chars for tables."""
    if text is None:
        return ""
    return str(text).replace("|", "\\|")


def render_skills_table(skills: dict, lang: str) -> str:
    """Render all skills (command cards, rouse, exalt, overexalt, enlighten,
    talent) in a single unified table."""
    L = LABELS[lang]
    pending = L["pending"]

    def _name(obj: dict | None) -> str:
        if not obj:
            return ""
        return obj.get("name_en", obj.get("name", "")) if lang == "en" else obj.get("name", "")

    lines = [
        f"| {L['card_name']} | {L['cost']} | {L['effect']} |",
        "|------|------|------|",
    ]

    # ── 1. Exalt (狂气爆发) ──
    exalt = skills.get("exalt")
    exalt_name = _name(exalt) if exalt else L["exalt"]
    exalt_effect = _esc(exalt.get("effect", pending)) if exalt else pending
    lines.append(f"| **{L['exalt']}**: {_esc(exalt_name)} | — | {exalt_effect} |")

    # ── Over-Exalt (optional) ──
    oe = skills.get("overexalt")
    if oe:
        oe_name = _name(oe)
        oe_effect = _esc(oe.get("effect", pending))
        lines.append(f"| **{L['overexalt']}**: {_esc(oe_name)} | — | {oe_effect} |")

    # ── 2. Rouse (觉醒卡) ──
    rouse = skills.get("rouse")
    rouse_name = _name(rouse) if rouse else L["rouse"]
    rouse_effect = _esc(rouse.get("effect", pending)) if rouse else pending
    lines.append(f"| **{L['rouse']}**: {_esc(rouse_name)} | — | {rouse_effect} |")

    # ── 3-4. Skill cards (non-strike, non-defense) then 5-6. Strike/Defense ──
    cards = skills.get("command_cards")
    if cards:
        basic = []   # 打击/防御
        skill = []   # 技能卡
        for card in cards:
            name_lower = (card.get("name", "") + card.get("name_en", "")).lower()
            if any(kw in name_lower for kw in ("打击", "防御", "strike", "defense", "defend", "guard")):
                basic.append(card)
            else:
                skill.append(card)
        for card in skill + basic:
            name = _name(card)
            cost = _esc(card.get("cost", "—"))
            effect = _esc(card.get("effect", ""))
            note = card.get("note", "")
            cell = effect
            if note:
                cell += f" ({_esc(note)})"
            lines.append(f"| {_esc(name)} | {cost} | {cell} |")
            for upg in card.get("upgrades", []):
                uname = _esc(upg.get("name", ""))
                ueffect = _esc(upg.get("effect", ""))
                lines.append(f"| ↳ {uname} | — | {ueffect} |")
    else:
        lines.append(f"| *{L['command_cards']}* | — | {pending} |")

    # ── Special Mechanic (optional) ──
    spec = skills.get("special_mechanic")
    if spec and isinstance(spec, dict):
        sp_name = _name(spec) or "Special"
        sp_desc = _esc(spec.get("description", spec.get("effect", "")))
        lines.append(f"| **{sp_name}** | — | {sp_desc} |")

    # ── Talent (optional) ──
    talent = skills.get("talent")
    if talent:
        t_name = _name(talent)
        t_effect = _esc(talent.get("effect", pending))
        lines.append(f"| **{L['talent']}**: {_esc(t_name)} | — | {t_effect} |")

    # ── Enlighten ──
    enlighten = skills.get("enlighten")
    if enlighten:
        for e in enlighten:
            level = e.get("level", "?")
            ename = _name(e)
            eeffect = _esc(e.get("effect", ""))
            lines.append(f"| **{L['enlighten']} {level}**: {_esc(ename)} | — | {eeffect} |")
    else:
        lines.append(f"| *{L['enlighten']}* | — | {pending} |")

    lines.append("")

    # Command cards note
    note = skills.get("command_cards_note", "")
    if note:
        lines.extend([f"::: tip\n{note}\n:::"])
    lines.append("")

    return "\n".join(lines) + "\n"


def render_equipment(char: dict, wheel_index: dict[str, list[dict]], lang: str) -> str:
    L = LABELS[lang]
    char_name = char["name"]
    char_name_en = char.get("name_en", "")

    wheels = wheel_index.get(char_name, [])
    # Also try English name match
    if not wheels and char_name_en:
        wheels = wheel_index.get(char_name_en, [])

    if not wheels:
        return f"## {L['recommended_equipment']}\n\n{L['pending']}\n"

    lines = [f"## {L['recommended_equipment']}", ""]

    seen = set()
    for w in wheels:
        wname = w.get("name", "")
        if wname in seen:
            continue
        seen.add(wname)

        wname_en = w.get("name_en", "")
        # Check if this wheel's character field matches THIS character
        wheel_char = w.get("character", "") or ""
        is_signature = char_name in wheel_char or (char_name_en and char_name_en in wheel_char)
        tag = L["signature_wheel"] if is_signature else L["recommended_wheel"]

        display = f"{wname}" if lang == "zh" else (f"{wname_en}" if lang == "en" else f"{wname}（{wname_en}）")

        lines.append(f"### {tag}: {display}")
        lines.append("")

        effect = w.get("effect", "")
        effect_en = w.get("effect_en", "")
        if lang == "en" and effect_en:
            lines.append(effect_en.split("\n")[0] if "\n" in effect_en else effect_en)
        elif effect:
            lines.append(effect)
        else:
            lines.append(L["pending"])
        lines.append("")

    return "\n".join(lines) + "\n"


def generate_character_page(char: dict, wheel_index: dict[str, list[dict]], lang: str) -> str:
    """Generate full markdown for one character in the given language."""
    L = LABELS[lang]
    cid = char["id"]
    name = char["name"]
    name_en = char.get("name_en", name)
    rarity = char.get("rarity", "?")
    realm_key = char.get("realm", "chaos")
    role_key = char.get("role", "attack")
    is_limited = char.get("is_limited", False)
    obtain = char.get("obtain", L["pending"])
    description = char.get("description", L["pending"])

    realm_display = REALM_NAMES[lang].get(realm_key, realm_key)
    role_display = ROLE_NAMES[lang].get(role_key, role_key)
    limited_display = L["yes"] if is_limited else L["no"]

    # Frontmatter
    desc_text = L["description_tpl"].format(
        name=name, name_en=name_en, realm=realm_display, role=role_display
    )
    title_name = name_en if lang == "en" else name

    # Quote YAML values that contain colons to avoid parse errors
    title_val = f"{title_name} | {L['title_suffix']}"
    if ':' in title_val:
        title_val = f'"{title_val}"'
    desc_val = desc_text
    if ':' in desc_val:
        desc_val = f'"{desc_val}"'

    fm = [
        "---",
        f"title: {title_val}",
        f"description: {desc_val}",
        f"portrait: /portraits/{cid}.png",
        "---",
    ]

    # Header
    header_name = f"{name_en} ({name})" if lang == "en" else f"{name} ({name_en})"
    body = [
        "",
        f"# {header_name}",
        "",
        '<div class="character-header">',
        f'  <img :src="\'/brain-in-a-vat/wiki/portraits/{cid}.png\'" alt="{name}" class="portrait" />',
        "",
        f"  | {L['attr']} | {L['value']} |",
        "  |------|-----|",
        f"  | {L['rarity']} | {rarity} |",
        f"  | {L['realm']} | {realm_display} |",
        f"  | {L['role']} | {role_display} |",
        f"  | {L['limited']} | {limited_display} |",
        f"  | {L['obtain']} | {obtain} |",
        "</div>",
        "",
    ]

    # Intro
    body.extend([f"## {L['intro']}", "", description, ""])

    # Skills section
    skills = char.get("skills")
    if skills:
        body.extend([f"## {L['skills']}", ""])
        body.append(render_skills_table(skills, lang))
    else:
        body.extend([f"## {L['skills']}", "", L["pending"], ""])

    # Equipment
    body.append(render_equipment(char, wheel_index, lang))

    # Component
    body.extend(["", "<CharacterCompare />", ""])

    return "\n".join(fm) + "\n".join(body)


# ---------------------------------------------------------------------------
# List page update
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    import re
    slug = text.lower().strip()
    slug = re.sub(r"[''']", "", slug)
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def generate_wheel_pages(equip_data: dict[str, Any], langs: list[str], dry_run: bool) -> int:
    """Generate/update wheel detail pages from equipment.json data."""
    wod = equip_data.get("wheels_of_destiny", {})
    generated = 0

    # Category display names
    CAT_NAMES = {
        "zh": {
            "ssr_limited_oblivion": "SSR限定·忘却线",
            "ssr_limited_stellar": "SSR限定·星辰线",
            "ssr_standard": "SSR常驻",
            "sr_wheels": "SR",
            "r_wheels": "R",
        },
        "en": {
            "ssr_limited_oblivion": "SSR Limited (Oblivion)",
            "ssr_limited_stellar": "SSR Limited (Stellar)",
            "ssr_standard": "SSR Standard",
            "sr_wheels": "SR",
            "r_wheels": "R",
        },
        "ja": {
            "ssr_limited_oblivion": "SSR限定・忘却線",
            "ssr_limited_stellar": "SSR限定・星辰線",
            "ssr_standard": "SSR常設",
            "sr_wheels": "SR",
            "r_wheels": "R",
        },
    }

    for cat_key, wheel_list in wod.items():
        if not isinstance(wheel_list, list):
            continue
        for wheel in wheel_list:
            if not isinstance(wheel, dict):
                continue
            name = wheel.get("name", "")
            name_en = wheel.get("name_en", "")
            if not name_en:
                continue

            slug = slugify(name_en)
            rarity = "SSR" if "ssr" in cat_key else ("SR" if "sr" in cat_key else "R")
            char_field = wheel.get("character", "")
            recommended = wheel.get("recommended", [])
            effect = wheel.get("effect", "")
            effect_en = wheel.get("effect_en", "")
            main_stat = wheel.get("main_stat", "")

            for lang in langs:
                out_dir = DOCS_DIR / lang / "wheels"
                page_path = out_dir / f"{slug}.md"

                L = LABELS[lang]
                cat_display = CAT_NAMES.get(lang, CAT_NAMES["zh"]).get(cat_key, cat_key)
                pending = L["pending"]

                # Build page content
                if lang == "en":
                    title = f"{name_en} - Wheel of Destiny"
                    heading = f"{name_en}"
                    sub = f"**{name}**" if name else ""
                elif lang == "ja":
                    title = f"{name}（{name_en}）- 運命の輪"
                    heading = f"{name}"
                    sub = f"**{name_en}**"
                else:
                    title = f"{name} - 命轮"
                    heading = f"{name}"
                    sub = f"**{name_en}**"

                lines = [
                    "---",
                    f'title: "{title}"',
                    f'description: "{name}({name_en}) - {"Morimens Wiki" if lang == "en" else "忘却前夜命轮详情"}"',
                    "---",
                    "",
                    f"# {heading}",
                    sub,
                    "",
                ]

                # Info table
                attr_label = L.get("attr", "属性")
                val_label = L.get("value", "信息")
                lines.extend([
                    f"| {attr_label} | {val_label} |",
                    "|------|------|",
                    f"| {L['rarity']} | <span class=\"rarity-{rarity.lower()}\">{rarity}</span> |",
                    f"| {'分类' if lang == 'zh' else 'Category' if lang == 'en' else 'カテゴリ'} | {cat_display} |",
                ])

                if char_field:
                    char_label = "适用角色" if lang == "zh" else "Character" if lang == "en" else "対応キャラ"
                    lines.append(f"| {char_label} | {char_field} |")

                if recommended:
                    rec_label = "推荐角色" if lang == "zh" else "Recommended" if lang == "en" else "おすすめ"
                    lines.append(f"| {rec_label} | {', '.join(recommended)} |")

                if main_stat:
                    stat_label = "主属性" if lang == "zh" else "Main Stat" if lang == "en" else "メインステータス"
                    lines.append(f"| {stat_label} | {main_stat} |")

                lines.append("")

                # Effect section
                eff_label = "效果" if lang == "zh" else "Effect" if lang == "en" else "効果"
                lines.append(f"## {eff_label}")
                lines.append("")

                if lang == "en" and effect_en:
                    lines.append(effect_en)
                elif effect:
                    lines.append(effect)
                elif effect_en:
                    lines.append(effect_en)
                else:
                    lines.append(f"*{pending}*")

                lines.append("")
                content = "\n".join(lines)

                if dry_run:
                    print(f"  [DRY-RUN] {page_path.relative_to(PROJECT_ROOT)}")
                else:
                    out_dir.mkdir(parents=True, exist_ok=True)
                    page_path.write_text(content, encoding="utf-8")
                generated += 1

    return generated


def update_list_page(characters: list[dict], lang: str, dry_run: bool) -> str | None:
    """Append <CharacterGrid /> component to list page if not already present."""
    list_path = DOCS_DIR / lang / "awakeners" / "list.md"
    if not list_path.exists():
        return None

    content = list_path.read_text(encoding="utf-8")
    if "<CharacterGrid" in content:
        return None  # already has it

    new_content = content.rstrip() + "\n\n<CharacterGrid />\n"
    if not dry_run:
        list_path.write_text(new_content, encoding="utf-8")
    return str(list_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate VitePress character detail pages")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument(
        "--lang",
        choices=["zh", "en", "ja", "all"],
        default="all",
        help="Language to generate (default: all)",
    )
    args = parser.parse_args()

    langs = ["zh", "en", "ja"] if args.lang == "all" else [args.lang]

    # Load data
    characters = load_characters()
    equip_data = load_equipment()
    wheel_index = build_wheel_index(equip_data)

    print(f"Loaded {len(characters)} characters, {sum(len(v) for v in wheel_index.values())} wheel mappings")
    print(f"Languages: {', '.join(langs)}")
    print(f"Dry run: {args.dry_run}")
    print()

    generated = 0
    skipped = 0
    updated_lists: list[str] = []

    for lang in langs:
        out_dir = DOCS_DIR / lang / "awakeners"
        if not args.dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)

        for char in characters:
            cid = char["id"]
            page_path = out_dir / f"{cid}.md"
            content = generate_character_page(char, wheel_index, lang)

            if args.dry_run:
                print(f"  [DRY-RUN] {page_path.relative_to(PROJECT_ROOT)}")
                generated += 1
            else:
                page_path.write_text(content, encoding="utf-8")
                generated += 1

        # Update list page
        result = update_list_page(characters, lang, args.dry_run)
        if result:
            updated_lists.append(result)

    # Generate wheel pages
    wheel_count = generate_wheel_pages(equip_data, langs, args.dry_run)

    # Summary
    print()
    print("=" * 60)
    print(f"  Generated: {generated} character pages + {wheel_count} wheel pages")
    print(f"  Languages: {', '.join(langs)}")
    print(f"  Characters: {len(characters)}")
    if updated_lists:
        print(f"  Updated list pages: {len(updated_lists)}")
        for p in updated_lists:
            print(f"    - {p}")
    if args.dry_run:
        print("  (dry-run mode — no files written)")
    print("=" * 60)


if __name__ == "__main__":
    main()
