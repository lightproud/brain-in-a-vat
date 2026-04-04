#!/usr/bin/env python3
"""
Spot-check data source availability for sample characters across realms.

Tests Fandom wiki, Bilibili Game Wiki, and GameKee for data availability.
Run periodically or before batch fetches to verify sources are online.

Usage:
  python3 probe_sources.py          # probe 5 sample characters
  python3 probe_sources.py --all    # probe all characters (slow)

This is a diagnostic script — does not modify any data files.
Exit code 0 if at least one source is available for all probed characters.
Exit code 1 if any character has zero available sources.
"""

import json
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, ".")
from character_mapping import FANDOM_PAGE_MAP, BILI_PAGE_MAP

UA = "Mozilla/5.0 (compatible; MorimensWikiBot/1.0; +https://github.com/lightproud/brain-in-a-vat)"

FANDOM_WIKIS = [
    "https://forget-last-night-morimens.fandom.com",
    "https://morimens.fandom.com",
]
BILIGAME_BASE = "https://wiki.biligame.com/morimens"
GAMEKEE_BASE = "https://www.gamekee.com"

# Pick 5 characters: one per realm + one multi-realm
PROBE_CHARS = [
    ("alva", "chaos"),       # Chaos realm, popular character
    ("celeste", "aequor"),   # Aequor realm
    ("tulu", "caro"),        # Caro realm
    ("murphy", "ultra"),     # Ultra realm
    ("24", "all"),           # Multi-realm special character
]


def http_get(url: str, timeout: int = 15) -> bytes | None:
    """Simple HTTP GET returning raw bytes or None on error."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as e:
        return None


def check_fandom(char_id: str) -> dict:
    """Check Fandom wiki availability."""
    page = FANDOM_PAGE_MAP.get(char_id)
    if not page:
        return {"available": False, "error": "no mapping"}

    for base in FANDOM_WIKIS:
        params = urllib.parse.urlencode({
            "action": "parse", "page": page,
            "prop": "wikitext", "format": "json",
        })
        raw = http_get(f"{base}/api.php?{params}")
        if raw:
            try:
                data = json.loads(raw)
                wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
                if wikitext:
                    has_skills = any(kw in wikitext.lower() for kw in
                                     ["command card", "指令卡", "rouse", "觉醒", "exalt", "狂气"])
                    has_stats = any(kw in wikitext.lower() for kw in
                                    ["hp", "atk", "def", "生命", "攻击", "防御"])
                    return {
                        "available": True,
                        "wiki": base.split("//")[1].split(".")[0],
                        "length": len(wikitext),
                        "has_skills": has_skills,
                        "has_stats": has_stats,
                    }
            except Exception:
                pass
    return {"available": False, "error": "no wikitext from any Fandom wiki"}


def check_bilibili(char_id: str) -> dict:
    """Check Bilibili Game Wiki availability."""
    page = BILI_PAGE_MAP.get(char_id)
    if not page:
        return {"available": False, "error": "no mapping"}

    params = urllib.parse.urlencode({
        "action": "parse", "page": page,
        "prop": "wikitext", "format": "json",
    })
    raw = http_get(f"{BILIGAME_BASE}/api.php?{params}")
    if raw:
        try:
            data = json.loads(raw)
            wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
            if wikitext:
                has_skills = any(kw in wikitext for kw in
                                 ["指令卡", "觉醒", "狂气", "启灵", "天赋", "技能"])
                has_stats = any(kw in wikitext for kw in
                                 ["生命", "攻击", "防御", "HP", "ATK", "DEF"])
                return {
                    "available": True,
                    "length": len(wikitext),
                    "has_skills": has_skills,
                    "has_stats": has_stats,
                }
        except Exception:
            pass
    return {"available": False, "error": "no wikitext"}


def check_gamekee(char_id: str) -> dict:
    """Check GameKee availability (HTML scraping probe only)."""
    # GameKee uses a SPA / API-driven site. Check if the search returns results.
    search_url = f"{GAMEKEE_BASE}/morimens/search?keyword={urllib.parse.quote(char_id)}"
    raw = http_get(search_url, timeout=10)
    if raw:
        try:
            text = raw.decode("utf-8", errors="replace")
            # Check if we got a non-empty page with character data
            has_content = len(text) > 5000
            has_char_ref = char_id.lower() in text.lower() or FANDOM_PAGE_MAP.get(char_id, "").lower() in text.lower()
            return {
                "available": has_content,
                "page_size": len(text),
                "has_char_ref": has_char_ref,
                "note": "SPA - may need API or headless browser",
            }
        except Exception:
            pass
    return {"available": False, "error": "unreachable"}


def main():
    all_mode = "--all" in sys.argv

    if all_mode:
        probe_list = [(cid, "?") for cid in sorted(FANDOM_PAGE_MAP.keys())]
    else:
        probe_list = PROBE_CHARS

    print("=" * 70)
    print(f"Data Source Availability Probe ({len(probe_list)} characters)")
    print("=" * 70)
    print()

    results = {}
    for char_id, realm in probe_list:
        print(f"--- {char_id} (realm: {realm}) ---")
        results[char_id] = {}

        # Fandom
        print(f"  Fandom:   ", end="", flush=True)
        r = check_fandom(char_id)
        results[char_id]["fandom"] = r
        if r["available"]:
            print(f"OK ({r['length']} chars, skills={r['has_skills']}, stats={r['has_stats']}, wiki={r['wiki']})")
        else:
            print(f"FAIL ({r.get('error', '?')})")
        time.sleep(0.5)

        # Bilibili
        print(f"  Bilibili: ", end="", flush=True)
        r = check_bilibili(char_id)
        results[char_id]["bilibili"] = r
        if r["available"]:
            print(f"OK ({r['length']} chars, skills={r['has_skills']}, stats={r['has_stats']})")
        else:
            print(f"FAIL ({r.get('error', '?')})")
        time.sleep(0.5)

        # GameKee
        print(f"  GameKee:  ", end="", flush=True)
        r = check_gamekee(char_id)
        results[char_id]["gamekee"] = r
        if r["available"]:
            print(f"MAYBE (page_size={r['page_size']}, char_ref={r['has_char_ref']}, note={r['note']})")
        else:
            print(f"FAIL ({r.get('error', '?')})")
        time.sleep(0.5)

        print()

    # Summary
    print("=" * 70)
    print("Summary:")
    print(f"{'Source':<12} {'Available':<12} {'Has Skills':<14} {'Has Stats':<12}")
    print("-" * 50)
    for source in ["fandom", "bilibili"]:
        avail = sum(1 for c in results.values() if c[source].get("available"))
        skills = sum(1 for c in results.values() if c[source].get("has_skills"))
        stats = sum(1 for c in results.values() if c[source].get("has_stats"))
        print(f"{source:<12} {avail}/5{'':<8} {skills}/5{'':<10} {stats}/5")
    gk_avail = sum(1 for c in results.values() if c["gamekee"].get("available"))
    print(f"{'gamekee':<12} {gk_avail}/5 (SPA)")
    print()

    # Recommendation
    print("Recommendation:")
    fandom_ok = all(r["fandom"].get("available") for r in results.values())
    bili_ok = all(r["bilibili"].get("available") for r in results.values())
    if fandom_ok and bili_ok:
        print("  Both Fandom and Bilibili are reliable. Current fallback strategy is sound.")
    elif fandom_ok:
        print("  Fandom is reliable. Bilibili has gaps — use as supplement only.")
    elif bili_ok:
        print("  Bilibili is reliable. Fandom has gaps — consider swapping primary source.")
    else:
        print("  Both sources have gaps. Consider adding GameKee or manual data entry.")
    if gk_avail < 3:
        print("  GameKee: SPA-based, not viable for simple HTTP scraping without headless browser.")

    # Exit code: 1 if any character has zero sources available
    zero_sources = sum(
        1 for r in results.values()
        if not r["fandom"].get("available") and not r["bilibili"].get("available")
    )
    if zero_sources:
        print(f"\n  WARNING: {zero_sources} character(s) have no available source.")
    return 1 if zero_sources == len(results) else 0


if __name__ == "__main__":
    sys.exit(main())
