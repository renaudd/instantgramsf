#!/usr/bin/env python3
"""
Batch-render full-bleed card faces for the InstantGram SF webapp:
  1. Influence cards   -> public/assets/fp/cards/influence/<id>.jpg
  2. Job cards         -> public/assets/fp/cards/jobs/<id>.jpg
  3. Encounter cards   -> public/assets/fp/cards/encounters/<id>.jpg
  4. Cargo/Offer goods -> public/assets/fp/cards/goods/mcargo_<id>.jpg & offer_<id>.jpg
"""

import hashlib
import json
import os
import re
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import render_encounter_mockups as rem
import render_goods_cards as rgc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCKUPS_DIR = os.path.join(ROOT, "public/assets/fp/mockups")
PORTRAITS_DIR = os.path.join(ROOT, "public/assets/fp/portraits")
CARDS_DIR = os.path.join(ROOT, "public/assets/fp/cards")

FACTION_TO_GEM = {
    "MAGA": "Ruby",
    "TECH": "Diamond",
    "DSA": "Sapphire",
    "MS13": "Amethyst",
    "ISIS": "Emerald",
    "RUBY": "Ruby",
    "DIAMOND": "Diamond",
    "SAPPHIRE": "Sapphire",
    "AMETHYST": "Amethyst",
    "EMERALD": "Emerald",
}

SF_TEXT_RULES = [
    (r"\bGladiator's Intervention\b", "Backup Arrives"),
    (r"\bHenchman's Intervention\b", "Backup Arrives"),
    (r"\bFriend In The City (?:Guard|Henchman)\b", "City Hall Fixer"),
    (r"\bFlying Chamber Pot\b", "Pepper Spray"),
    (r"\bMercenary Ambush\b", "Drive-By"),
    (r"\bWine Forger\b", "Fentanyl Press"),
    (r"\bOpiates Forger\b", "Fentanyl Press"),
    (r"\bProphecy\b", "Bad Trip"),
    (r"\bProcurer\b", "Dark Web Plug"),
    (r"\bSupplicant\b", "VIP Vouch"),
    (r"\bDramaturge\b", "Viral Heckler"),
    (r"\bMake Haste\b", "Floor It"),
    (r"\bPuffery\b", "Market Hype"),
    (r"\bDenarii\b", "₿"),
    (r"\bDenarius\b", "₿"),
    (r"\bGrain\b", "Weed"),
    (r"\bMarble\b", "Party"),
    (r"\bMeat Animals\b", "Pill Uppers"),
    (r"\bExotic Animals\b", "Powder Uppers"),
    (r"\bAnimals\b", "Uppers"),
    (r"\bCheap Wine\b", "Street Opiates"),
    (r"\bFine Wine\b", "Pharma Opiates"),
    (r"\bWine\b", "Opiates"),
    (r"\bGladiators\b", "Henchmen"),
    (r"\bGladiator\b", "Henchman"),
    (r"\bCartwright\b", "Body Shop"),
    (r"\bSUVwright\b", "Body Shop"),
    (r"\bCart\b", "SUV"),
    (r"\bCasus Belli\b", "Doxxing"),
    (r"\bSoothsayer\b", "Schizophrenic"),
    (r"\bForum\b", "Market"),
    (r"\bPatrons\b", "Celebrities"),
    (r"\bPatron\b", "Sponsor"),
    (r"\bLegionaries\b", "Cops"),
    (r"\bLegionary\b", "Cop"),
    (r"\bNefarious\b", "Criminals"),
    (r"\bPraetorian\b", "SWAT"),
    (r"\bMissions\b", "Jobs"),
    (r"\bMission\b", "Job"),
    (r"\bMissio\b", "Job"),
]


def sf_reskin(text: str) -> str:
    if not text:
        return ""
    out = str(text)
    out = re.sub(r"(\bD4\s*[—–\-·]\s*)Mission\b", r"\1__SF_NBHD_MISSION__", out)
    out = re.sub(r"\(\s*Mission\s*\)", "(__SF_NBHD_MISSION__)", out)
    out = re.sub(r"\b(in\s+the\s+|the\s+)Mission\b", r"\1__SF_NBHD_MISSION__", out)
    out = re.sub(r"\bMission(\s+(?:District|Dolores|St|Street|Bay))\b", r"__SF_NBHD_MISSION__\1", out)

    def _den_repl(m):
        val = int(m.group(1))
        b = round(val) / 10.0
        b_str = str(int(b)) if b == int(b) else f"{b:.1f}"
        return f"₿{b_str}"

    out = re.sub(r"\b(\d+)\s*\(d\)", _den_repl, out)
    for pat, rep in SF_TEXT_RULES:
        out = re.sub(pat, rep, out)
    out = out.replace("__SF_NBHD_MISSION__", "Mission")
    return out


def stable_hash(s: str) -> int:
    return int(hashlib.md5(s.encode("utf-8")).hexdigest()[:8], 16)


def parse_gem_token(tok: str):
    s = str(tok or "").strip()
    is_neg = s.startswith("-")
    key = s.lstrip("+-").upper()
    gem_name = FACTION_TO_GEM.get(key, "Ruby")
    return gem_name, is_neg


# ============================================================================
# 1. RENDER ALL INFLUENCE CARDS ON FULL-BLEED SMARTPHONE TEMPLATES
# ============================================================================
INFLUENCE_TEMPLATES = [
    {
        "file": "influence_instantgram.png",
        "crop_box": (77, 27, 770, 1238),
        "title_clear": (120, 770, 730, 858),
        "title_bg": (12, 20, 27),
        "title_box": (130, 775, 718, 852),
        "body_clear": (146, 868, 702, 1156),
        "body_bg": (43, 58, 64),
        "body_box": (162, 880, 686, 1145),
    },
    {
        "file": "influence_clocktok.png",
        "crop_box": (61, 29, 786, 1238),
        "title_clear": (128, 720, 560, 818),
        "title_bg": (22, 34, 40),
        "title_box": (140, 725, 550, 810),
        "body_clear": (132, 842, 716, 1182),
        "body_bg": (61, 74, 83),
        "body_box": (152, 856, 696, 1168),
    },
    {
        "file": "influence_youtoob.png",
        "crop_box": (81, 28, 767, 1229),
        "title_clear": (125, 595, 620, 668),
        "title_bg": (14, 24, 26),
        "title_box": (135, 600, 610, 662),
        "body_clear": (142, 770, 706, 1038),
        "body_bg": (47, 68, 77),
        "body_box": (160, 782, 688, 1026),
    },
    {
        "file": "influence_facespace.png",
        "crop_box": (43, 29, 804, 1243),
        "title_clear": (125, 675, 580, 742),
        "title_bg": (28, 37, 48),
        "title_box": (135, 680, 570, 738),
        "body_clear": (126, 798, 722, 1156),
        "body_bg": (62, 74, 88),
        "body_box": (148, 812, 700, 1142),
    },
    {
        "file": "influence_linkedout.png",
        "crop_box": (57, 34, 789, 1229),
        "title_clear": (140, 520, 710, 632),
        "title_bg": (27, 36, 41),
        "title_box": (150, 530, 700, 624),
        "body_clear": (126, 692, 722, 1152),
        "body_bg": (55, 68, 76),
        "body_box": (148, 708, 700, 1138),
    },
]

FACTION_FAVOR_INFLUENCE_SPECS = {
    "DSA Favor": (
        "Receive ₿0.6, gain 1 DSA Sapphire, and lose 1 MAGA Ruby (may be played after encounter is revealed).",
        ["DSA", "-MAGA"],
    ),
    "MS13 Favor": (
        "Receive ₿0.6, gain 1 MS13 Amethyst, and lose 1 MAGA Ruby (may be played after encounter is revealed).",
        ["MS13", "-MAGA"],
    ),
    "ISIS Favor": (
        "Receive ₿0.5, gain 1 ISIS Emerald, and lose 1 MAGA Ruby (may be played after encounter is revealed).",
        ["ISIS", "-MAGA"],
    ),
    "TECH Favor": (
        "Receive ₿0.6, gain 1 TECH Diamond, and lose 1 DSA Sapphire & 1 MS13 Amethyst (may be played after encounter is revealed).",
        ["TECH", "-DSA", "-MS13"],
    ),
    "MAGA Favor": (
        "Receive ₿0.5, gain 1 MAGA Ruby, and lose 1 ISIS Emerald & 1 DSA Sapphire (may be played after encounter is revealed).",
        ["MAGA", "-ISIS", "-DSA"],
    ),
}


def render_influence_card(card: dict, out_path: str):
    cid = str(card.get("id", "inf_1"))
    num_match = re.search(r"(\d+)", cid)
    num_id = int(num_match.group(1)) if num_match else 1
    tpl = INFLUENCE_TEMPLATES[(num_id - 1) % len(INFLUENCE_TEMPLATES)]

    im = Image.open(os.path.join(MOCKUPS_DIR, tpl["file"])).convert("RGBA")
    draw = ImageDraw.Draw(im)

    cname_raw = str(card.get("name", "Influence")).strip()
    cname = sf_reskin(cname_raw).upper()

    eff_raw = str(card.get("effectText", "")).strip()
    gems = []
    if cname_raw in FACTION_FAVOR_INFLUENCE_SPECS:
        eff_raw, gems = FACTION_FAVOR_INFLUENCE_SPECS[cname_raw]
    elif cname_raw == "Patron":
        if cid == "inf_2":
            eff_raw = "Receive ₿0.8, and lose 1 MAGA Ruby and 1 TECH Diamond."
            gems = ["-MAGA", "-TECH"]
        else:
            eff_raw = "Receive ₿0.8, and lose 1 ISIS Emerald and 1 DSA Sapphire."
            gems = ["-ISIS", "-DSA"]
    else:
        fg = card.get("favorGain") or {}
        if isinstance(fg, dict) and isinstance(fg.get("extraFavor"), list):
            gems = list(fg["extraFavor"])

    eff_text = sf_reskin(eff_raw)

    # Clear & draw Title
    tx0, ty0, tx1, ty1 = tpl["title_clear"]
    draw.rounded_rectangle((tx0, ty0, tx1, ty1), radius=8, fill=tpl["title_bg"])
    bx0, by0, bx1, by1 = tpl["title_box"]
    f_title = rgc.fit_font(rem.F_COND, cname, (bx1 - bx0) * 0.94, int((by1 - by0) * 0.80), min_size=28)
    bb = draw.textbbox((0, 0), cname, font=f_title)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((bx0 + (bx1 - bx0 - tw) // 2 - bb[0], by0 + (by1 - by0 - th) // 2 - bb[1]), cname, font=f_title, fill=(255, 255, 255))

    # Clear & draw Body
    cx0, cy0, cx1, cy1 = tpl["body_clear"]
    draw.rounded_rectangle((cx0, cy0, cx1, cy1), radius=14, fill=tpl["body_bg"])

    px0, py0, px1, py1 = tpl["body_box"]
    gem_reserve = 78 if gems else 0
    text_max_h = (py1 - py0) - gem_reserve
    avail_w = px1 - px0

    best_font = ImageFont.truetype(rem.F_SYM, 24)
    best_lines = [eff_text]
    for sz in range(36, 20, -2):
        f_try = ImageFont.truetype(rem.F_SYM, sz)
        try:
            f_try.set_variation_by_name("Bold")
        except Exception:
            pass
        lines = rem.wrap_text_lines(draw, eff_text, f_try, avail_w)
        total_h = len(lines) * int(sz * 1.24)
        if total_h <= text_max_h:
            best_font = f_try
            best_lines = lines
            break

    line_h = int(best_font.size * 1.24)
    tot_h = len(best_lines) * line_h
    cur_y = py0 + max(0, (text_max_h - tot_h) // 2)
    for ln in best_lines:
        bb_l = draw.textbbox((0, 0), ln.replace("(R)", "R"), font=best_font)
        lw = bb_l[2] - bb_l[0]
        rem.draw_formula_with_rome_die(
            draw,
            px0 + max(0, (avail_w - lw) // 2),
            cur_y + line_h // 2,
            ln,
            best_font,
            fill_col=(248, 250, 252),
        )
        cur_y += line_h

    if gems:
        gem_sz = 64
        gap = 12
        tot_gw = len(gems) * gem_sz + (len(gems) - 1) * gap
        gx = px0 + (avail_w - tot_gw) // 2
        gy = py1 - gem_sz - 4
        for g_tok in gems:
            gem_name, is_neg = parse_gem_token(g_tok)
            rem.draw_gem_with_slash(im, gx, gy, gem_name, is_negative=is_neg, size=gem_sz, black_border=True, border_px=3)
            gx += gem_sz + gap

    # Crop tightly so the outer edges of the phone press right up against the image limits
    cbox = tpl.get("crop_box", (0, 0, im.width, im.height))
    im = im.crop(cbox).resize((848, 1264), Image.LANCZOS)
    im.convert("RGB").save(out_path, quality=90)


# ============================================================================
# 2. RENDER ALL JOB CARDS AS 24 EMAIL & MESSAGING PLATFORM UIs ON PHONE SCREEN
# ============================================================================
JOB_PLATFORM_THEMES = [
    # 1. Gmail
    {
        "id": "gmail",
        "kind": "email",
        "app_name": "G-Mail • Inbox",
        "header_bg": (234, 67, 53),
        "header_fg": (255, 255, 255),
        "screen_bg": (246, 248, 252),
        "card_bg": (255, 255, 255),
        "card_border": (218, 220, 224),
        "accent": (234, 67, 53),
        "sender": "NightPlug.SF@g-mail.com",
        "sub_meta": "to me • Starred • Encrypted",
        "badge": "INBOX",
        "dark": False,
    },
    # 2. Outlook
    {
        "id": "outlook",
        "kind": "email",
        "app_name": "OutLook • Focused Inbox",
        "header_bg": (0, 120, 212),
        "header_fg": (255, 255, 255),
        "screen_bg": (240, 244, 249),
        "card_bg": (255, 255, 255),
        "card_border": (0, 120, 212),
        "accent": (0, 120, 212),
        "sender": "Dispatch Desk <ops@baylogistics.io>",
        "sub_meta": "High Importance ! • Focused",
        "badge": "FOCUSED",
        "dark": False,
    },
    # 3. LinkedIn Messages
    {
        "id": "linkedin",
        "kind": "chat",
        "app_name": "LinkedOut Messaging",
        "header_bg": (10, 102, 194),
        "header_fg": (255, 255, 255),
        "screen_bg": (243, 242, 239),
        "card_bg": (255, 255, 255),
        "card_border": (10, 102, 194),
        "accent": (10, 102, 194),
        "sender": "Chadwick Vance • 1st",
        "sub_meta": "VP of Street Supply Chain @SomaVC",
        "badge": "INMAIL",
        "dark": False,
    },
    # 4. Facebook Messages
    {
        "id": "facebook",
        "kind": "chat",
        "app_name": "FaceSpace Messenger",
        "header_bg": (0, 132, 255),
        "header_fg": (255, 255, 255),
        "screen_bg": (245, 247, 252),
        "card_bg": (235, 244, 255),
        "card_border": (0, 132, 255),
        "accent": (140, 48, 255),
        "sender": "Bay Area Night Network",
        "sub_meta": "Active Now • Messenger Direct",
        "badge": "ACTIVE",
        "dark": False,
    },
    # 5. WhatsApp Messages
    {
        "id": "whatsapp",
        "kind": "chat",
        "app_name": "WhatsUp • Encrypted",
        "header_bg": (7, 94, 84),
        "header_fg": (255, 255, 255),
        "screen_bg": (236, 229, 221),
        "card_bg": (220, 248, 198),
        "card_border": (37, 211, 102),
        "accent": (18, 140, 126),
        "sender": "+1 (415) 890-PLUG",
        "sub_meta": "online • End-to-End Encrypted",
        "badge": "READ",
        "dark": False,
    },
    # 6. Android Messages
    {
        "id": "android",
        "kind": "chat",
        "app_name": "Droid Messages • RCS",
        "header_bg": (27, 110, 243),
        "header_fg": (255, 255, 255),
        "screen_bg": (242, 245, 251),
        "card_bg": (219, 232, 255),
        "card_border": (27, 110, 243),
        "accent": (27, 110, 243),
        "sender": "Burner #415-RCS",
        "sub_meta": "RCS Chat • Verified Carrier",
        "badge": "RCS",
        "dark": False,
    },
    # 7. iPhone Messages
    {
        "id": "iphone",
        "kind": "chat",
        "app_name": "iText • iMessage",
        "header_bg": (244, 244, 247),
        "header_fg": (18, 18, 22),
        "screen_bg": (255, 255, 255),
        "card_bg": (233, 233, 235),
        "card_border": (0, 122, 255),
        "accent": (0, 122, 255),
        "sender": "Unknown Caller (415)",
        "sub_meta": "iMessage • Today 3:42 AM • Delivered",
        "badge": "iMESSAGE",
        "dark": False,
    },
    # 8. Snapchat (SnatchTap) Messages
    {
        "id": "snapchat",
        "kind": "chat",
        "app_name": "SnatchTap • Chat",
        "header_bg": (255, 252, 0),
        "header_fg": (16, 16, 18),
        "screen_bg": (250, 250, 252),
        "card_bg": (255, 255, 255),
        "card_border": (255, 0, 73),
        "accent": (0, 182, 255),
        "sender": "ghost_plug415 [128 Streak]",
        "sub_meta": "SAVED IN CHAT • SCREENSHOT ALERT",
        "badge": "SNAP",
        "dark": False,
    },
    # 9. AOL Instant Messenger (AIM)
    {
        "id": "aim",
        "kind": "chat",
        "app_name": "AIM • Instant Message",
        "header_bg": (0, 52, 153),
        "header_fg": (255, 255, 255),
        "screen_bg": (212, 208, 200),
        "card_bg": (255, 255, 255),
        "card_border": (110, 110, 118),
        "accent": (210, 24, 24),
        "sender": "xXBayKingpin99Xx",
        "sub_meta": "Buddy Warning Level: 0% • Online",
        "badge": "AIM",
        "dark": False,
    },
    # 10. MSN Instant Messenger
    {
        "id": "msn",
        "kind": "chat",
        "app_name": "MSN Messenger Live",
        "header_bg": (58, 122, 198),
        "header_fg": (255, 255, 255),
        "screen_bg": (222, 236, 250),
        "card_bg": (250, 253, 255),
        "card_border": (108, 162, 224),
        "accent": (40, 150, 60),
        "sender": "SF_NightRunner@msn.com",
        "sub_meta": "just sent you a Nudge!",
        "badge": "NUDGE",
        "dark": False,
    },
    # 11. ICQ Messages
    {
        "id": "icq",
        "kind": "chat",
        "app_name": "ICQ • Incoming Event",
        "header_bg": (46, 118, 54),
        "header_fg": (255, 255, 255),
        "screen_bg": (218, 220, 212),
        "card_bg": (252, 252, 246),
        "card_border": (82, 92, 80),
        "accent": (215, 45, 35),
        "sender": "UIN #415-808-99",
        "sub_meta": "Uh-Oh! • Direct Pager Message",
        "badge": "ICQ#",
        "dark": False,
    },
    # 12. Craigslist Messages
    {
        "id": "craigslist",
        "kind": "email",
        "app_name": "greg's list • sfbay relay",
        "header_bg": (85, 26, 139),
        "header_fg": (255, 255, 255),
        "screen_bg": (250, 250, 252),
        "card_bg": (255, 255, 255),
        "card_border": (175, 165, 195),
        "accent": (85, 26, 139),
        "sender": "99x415-gig@serv.gregslist.org",
        "sub_meta": "sfbay > city of sf > gigs > urgent",
        "badge": "CL RELAY",
        "dark": False,
    },
    # 13. eBay Messages
    {
        "id": "ebay",
        "kind": "email",
        "app_name": "eBuy • Member Message",
        "header_bg": (0, 100, 210),
        "header_fg": (255, 255, 255),
        "screen_bg": (247, 247, 247),
        "card_bg": (255, 255, 255),
        "card_border": (229, 50, 56),
        "accent": (245, 175, 2),
        "sender": "powerseller_sf415 (99.8% Pos)",
        "sub_meta": "Question about Listing #415009281",
        "badge": "BUY NOW",
        "dark": False,
    },
    # 14. Hotmail
    {
        "id": "hotmail",
        "kind": "email",
        "app_name": "HotMail • MSN WebMail",
        "header_bg": (24, 58, 108),
        "header_fg": (255, 255, 255),
        "screen_bg": (244, 246, 250),
        "card_bg": (255, 255, 255),
        "card_border": (255, 140, 0),
        "accent": (255, 120, 0),
        "sender": "bay_syndicate@hotmail.com",
        "sub_meta": "Priority: HIGH • Folder: Inbox (1)",
        "badge": "HOTMAIL",
        "dark": False,
    },
    # 15. Yahoo Mail
    {
        "id": "yahoo",
        "kind": "email",
        "app_name": "Yohoo! Mail",
        "header_bg": (96, 1, 210),
        "header_fg": (255, 255, 255),
        "screen_bg": (245, 240, 255),
        "card_bg": (255, 255, 255),
        "card_border": (138, 68, 225),
        "accent": (96, 1, 210),
        "sender": "sf_nightmarket@yohoo.com",
        "sub_meta": "Yohoo! Priority Dispatch!",
        "badge": "YOHOO!",
        "dark": False,
    },
    # 16. OnlyFans Messages
    {
        "id": "onlyfans",
        "kind": "chat",
        "app_name": "OnlyStans • VIP Direct",
        "header_bg": (0, 175, 240),
        "header_fg": (255, 255, 255),
        "screen_bg": (20, 26, 34),
        "card_bg": (30, 40, 52),
        "card_border": (0, 175, 240),
        "accent": (0, 175, 240),
        "sender": "@Top0.1%_Connect [Verified]",
        "sub_meta": "Top 0.01% Creator • Custom Request",
        "badge": "VIP DM",
        "dark": True,
    },
    # 17. Instagram Messages
    {
        "id": "instagram",
        "kind": "chat",
        "app_name": "InstantGram • Direct",
        "header_bg": (193, 53, 132),
        "header_fg": (255, 255, 255),
        "screen_bg": (18, 18, 24),
        "card_bg": (34, 28, 44),
        "card_border": (225, 48, 108),
        "accent": (247, 119, 55),
        "sender": "@sf.night.merchant [Verified]",
        "sub_meta": "Replied to your story • Active now",
        "badge": "IG DM",
        "dark": True,
    },
    # 18. TikTok Messages
    {
        "id": "tiktok",
        "kind": "chat",
        "app_name": "ClockTok • Inbox DM",
        "header_bg": (16, 16, 20),
        "header_fg": (37, 244, 238),
        "screen_bg": (14, 14, 18),
        "card_bg": (28, 28, 36),
        "card_border": (254, 44, 85),
        "accent": (37, 244, 238),
        "sender": "@viral.plug.sf",
        "sub_meta": "Sent you a video + direct order",
        "badge": "FYP DM",
        "dark": True,
    },
    # 19. Tinder Messages
    {
        "id": "tinder",
        "kind": "chat",
        "app_name": "Cinder • New Match!",
        "header_bg": (253, 41, 123),
        "header_fg": (255, 255, 255),
        "screen_bg": (255, 246, 249),
        "card_bg": (255, 255, 255),
        "card_border": (255, 101, 91),
        "accent": (253, 41, 123),
        "sender": "Roxy, 25 • 1 mile away",
        "sub_meta": "Super Liked You • Verified Photo",
        "badge": "MATCH",
        "dark": False,
    },
    # 20. Grindr Messages
    {
        "id": "grindr",
        "kind": "chat",
        "app_name": "Grindr • 180 ft away",
        "header_bg": (255, 182, 0),
        "header_fg": (14, 14, 16),
        "screen_bg": (18, 18, 20),
        "card_bg": (32, 30, 26),
        "card_border": (255, 182, 0),
        "accent": (255, 182, 0),
        "sender": "LookingNow415 [Online]",
        "sub_meta": "Online Now • Tapped You • 180 ft",
        "badge": "TAP",
        "dark": True,
    },
    # 21. Hinge Messages
    {
        "id": "hinge",
        "kind": "chat",
        "app_name": "Unhinged • Prompt Reply",
        "header_bg": (92, 26, 78),
        "header_fg": (255, 255, 255),
        "screen_bg": (249, 245, 239),
        "card_bg": (255, 255, 255),
        "card_border": (132, 52, 112),
        "accent": (92, 26, 78),
        "sender": "Julian • Nob Hill",
        "sub_meta": "Liked your prompt: 'My after-hours side hustle...'",
        "badge": "ROSE",
        "dark": False,
    },
    # 22. Bumble Messages
    {
        "id": "bumble",
        "kind": "chat",
        "app_name": "BumbleBee • Your Move",
        "header_bg": (255, 198, 41),
        "header_fg": (20, 18, 14),
        "screen_bg": (255, 252, 240),
        "card_bg": (255, 255, 255),
        "card_border": (240, 175, 15),
        "accent": (215, 145, 0),
        "sender": "Chloe • Marina District",
        "sub_meta": "23h 14m left before match expires!",
        "badge": "HIVE",
        "dark": False,
    },
    # 23. OkCupid Messages
    {
        "id": "okcupid",
        "kind": "chat",
        "app_name": "OkCulpid • 99% Match",
        "header_bg": (0, 70, 190),
        "header_fg": (255, 255, 255),
        "screen_bg": (244, 247, 255),
        "card_bg": (255, 255, 255),
        "card_border": (255, 0, 122),
        "accent": (255, 0, 122),
        "sender": "SynthWaveSF • Haight",
        "sub_meta": "99% Match • 1% Enemy • Sent an Intro",
        "badge": "99% MATCH",
        "dark": False,
    },
    # 24. Feely Messages
    {
        "id": "feely",
        "kind": "chat",
        "app_name": "Feely • Ping Connection",
        "header_bg": (42, 24, 56),
        "header_fg": (255, 168, 138),
        "screen_bg": (22, 16, 28),
        "card_bg": (38, 28, 48),
        "card_border": (255, 126, 95),
        "accent": (255, 126, 95),
        "sender": "K & V • SOMA Loft",
        "sub_meta": "0.4 km away • Sent you a Ping",
        "badge": "PING",
        "dark": True,
    },
]

_JOB_PHONE_CACHE = None


def get_job_phone_base():
    global _JOB_PHONE_CACHE
    if _JOB_PHONE_CACHE is not None:
        return _JOB_PHONE_CACHE
    _JOB_PHONE_CACHE = rem.prepare_full_bleed_phone_base()
    return _JOB_PHONE_CACHE


def format_job_concise_text(m: dict) -> str:
    kind = str(m.get("kind", "")).lower()
    if kind == "delivery":
        item = sf_reskin(m.get("item") or "Cargo")
        p_cell = m.get("pickupCell") or "A1"
        d_cell = m.get("deliverCell") or "C3"
        return f"Pick up {item} at {p_cell} and deliver to {d_cell}!"
    if kind == "sell":
        cat = sf_reskin(m.get("item") if (m.get("item") and m.get("item") != "Cargo") else (m.get("category") or "Goods"))
        mod = m.get("modifier") or "="
        cell = m.get("cell") or "A5"
        return f"Sell {cat} at {mod} in {cell}!"
    obj = m.get("objectiveText") or m.get("description") or m.get("name") or "Complete Job."
    obj = sf_reskin(obj)
    obj = re.sub(r"\s*Reward:.*$", "", obj, flags=re.IGNORECASE)
    return obj


def format_job_bezel_reward(m: dict) -> str:
    rew_raw = sf_reskin(str(m.get("rewardText") or "Special"))
    # Strip any trailing job rule descriptions so ONLY the reward appears in the top-right bezel
    rew_raw = re.sub(r"\s*&\s*Cancels.*$", "", rew_raw, flags=re.IGNORECASE)
    rew_short = (
        rew_raw.replace("Cheapest ", "Cheap ")
        .replace("Most Expensive ", "Top ")
        .replace(" on Market", "")
        .replace(" on Mkt", "")
        .replace("Influence Cards", "Inf")
        .replace("Influence Card", "Inf")
        .replace("Influence", "Inf")
        .replace("Henchman", "Hench")
        .replace("Henchmen", "Hench")
        .strip()
    )
    return rew_short


def render_job_card(m: dict, out_path: str):
    mid = str(m.get("id", "mis_1"))
    num_match = re.search(r"(\d+)", mid)
    num_id = int(num_match.group(1)) if num_match else 1
    theme = JOB_PLATFORM_THEMES[(num_id - 1) % len(JOB_PLATFORM_THEMES)]

    phone_base, mask, glass_delta = get_job_phone_base()
    im = phone_base.copy()
    draw = ImageDraw.Draw(im)

    SX0, SX1 = 46, 854
    SY0, SY1 = 104, 1296

    # 1. Top Black Phone Bezel / Outcome Bar (y=36..104 inside the rounded phone frame)
    draw.rectangle((SX0, 36, SX1, SY0), fill=(14, 18, 24))
    draw.line((SX0, SY0, SX1, SY0), fill=(212, 175, 55), width=3)

    top_cy = 72
    thumb_sz = 54
    thumb_up = rem.load_icon("thumb_up_green.png", thumb_sz, tight=True)
    im.paste(thumb_up, (62, top_cy - thumb_sz // 2), thumb_up)
    f_colon = ImageFont.truetype(rem.F_BOLD, 34)
    draw.text((64 + thumb_sz, top_cy - 20), ":", font=f_colon, fill=(255, 255, 255))

    favor_list = m.get("favor") or []
    gem_sz = 48 if len(favor_list) >= 3 else 54
    gx = 78 + thumb_sz
    for g_tok in favor_list:
        gem_name, is_neg = parse_gem_token(g_tok)
        gx = rem.draw_gem_with_slash(im, gx, top_cy - gem_sz // 2, gem_name, is_negative=is_neg, size=gem_sz, black_border=True, border_px=3)

    # Top-Right Bezel: ONLY the Job Reward (kept strictly to the right of the center speaker notch x=385..565)
    rew_short = format_job_bezel_reward(m)
    rew_str = f":{rew_short}"
    cash_sz = 46
    max_rew_w = min(218, max(135, 836 - max(gx, 570) - cash_sz - 10))
    f_rew = rgc.fit_font(rem.F_SYM, rew_str, max_rew_w, 32, min_size=17)
    try:
        f_rew.set_variation_by_name("Bold")
    except Exception:
        pass
    bb_r = draw.textbbox((0, 0), rew_str, font=f_rew)
    rw, rh = bb_r[2] - bb_r[0], bb_r[3] - bb_r[1]
    rx = 836 - rw
    ry = top_cy - rh // 2 - bb_r[1]
    cash_ic = rem.load_icon("cash_white.png", cash_sz, tight=True)
    im.paste(cash_ic, (rx - cash_sz - 4, top_cy - cash_sz // 2), cash_ic)
    draw.text((rx, ry), rew_str, font=f_rew, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))

    # 2. Phone Screen Interior (x=46..854, y=104..1296)
    draw.rectangle((SX0, SY0, SX1, SY1), fill=theme["screen_bg"])

    # Platform App Header Bar (y=104..188)
    hy0, hy1 = SY0, SY0 + 84
    draw.rectangle((SX0, hy0, SX1, hy1), fill=theme["header_bg"])
    if theme["id"] == "ebay":
        # Multi-color eBuy stripe under header
        sw = (SX1 - SX0) // 4
        draw.rectangle((SX0, hy1 - 8, SX0 + sw, hy1), fill=(229, 50, 56))
        draw.rectangle((SX0 + sw, hy1 - 8, SX0 + 2 * sw, hy1), fill=(0, 100, 210))
        draw.rectangle((SX0 + 2 * sw, hy1 - 8, SX0 + 3 * sw, hy1), fill=(245, 175, 2))
        draw.rectangle((SX0 + 3 * sw, hy1 - 8, SX1, hy1), fill=(134, 184, 23))

    f_app = rgc.fit_font(rem.F_BOLD, theme["app_name"], 550, 36, min_size=24)
    draw.text((SX0 + 26, hy0 + 22), f"‹  {theme['app_name']}", font=f_app, fill=theme["header_fg"])

    # Badge pill on right of header bar
    badge_str = theme["badge"]
    f_badge = ImageFont.truetype(rem.F_BOLD, 22)
    bb_b = draw.textbbox((0, 0), badge_str, font=f_badge)
    bw, bh = bb_b[2] - bb_b[0], bb_b[3] - bb_b[1]
    bx0_p = SX1 - bw - 48
    by0_p = hy0 + (84 - bh) // 2 - 8
    draw.rounded_rectangle((bx0_p, by0_p, SX1 - 20, by0_p + bh + 16), radius=12, fill=theme["accent"])
    draw.text((bx0_p + 14 - bb_b[0], by0_p + 8 - bb_b[1]), badge_str, font=f_badge, fill=(255, 255, 255))

    # 3. Sender / Metadata Header Strip (y=202..324)
    meta_y0, meta_y1 = 202, 324
    is_dark = theme["dark"]
    meta_bg = (28, 32, 42) if is_dark else (255, 255, 255)
    meta_fg = (242, 245, 250) if is_dark else (20, 24, 32)
    sub_fg = (170, 182, 200) if is_dark else (95, 105, 120)
    draw.rounded_rectangle((SX0 + 18, meta_y0, SX1 - 18, meta_y1), radius=16, fill=meta_bg, outline=theme["card_border"], width=2)

    # Avatar circle on left
    av_cx, av_cy, av_r = SX0 + 72, (meta_y0 + meta_y1) // 2, 36
    draw.ellipse((av_cx - av_r, av_cy - av_r, av_cx + av_r, av_cy + av_r), fill=theme["accent"], outline=theme["header_bg"], width=3)
    initials = "".join([w[0] for w in theme["sender"].lstrip("@+").split()[:2] if w and w[0].isalnum()]).upper() or "SF"
    f_init = ImageFont.truetype(rem.F_BOLD, 28)
    bb_i = draw.textbbox((0, 0), initials[:2], font=f_init)
    draw.text((av_cx - (bb_i[2] - bb_i[0]) // 2 - bb_i[0], av_cy - (bb_i[3] - bb_i[1]) // 2 - bb_i[1]), initials[:2], font=f_init, fill=(255, 255, 255))

    f_sender = rgc.fit_font(rem.F_BOLD, theme["sender"], 610, 28, min_size=20)
    f_sub = rgc.fit_font(rem.F_REG, theme["sub_meta"], 610, 22, min_size=16)
    draw.text((SX0 + 124, meta_y0 + 22), theme["sender"], font=f_sender, fill=meta_fg)
    draw.text((SX0 + 124, meta_y0 + 62), theme["sub_meta"], font=f_sub, fill=sub_fg)

    # 4. Message Bubble / Email Body Container (y=340..1276)
    bx0, by0, bx1, by1 = SX0 + 20, 340, SX1 - 20, 1276
    rad = 26 if theme["kind"] == "chat" else 12
    draw.rounded_rectangle((bx0, by0, bx1, by1), radius=rad, fill=theme["card_bg"], outline=theme["card_border"], width=4)

    if theme["id"] == "snapchat":
        # Iconic vertical red/blue saved-chat bar on left of message
        draw.rounded_rectangle((bx0 + 14, by0 + 20, bx0 + 26, by1 - 20), radius=5, fill=(255, 0, 73))

    # Job Title Header inside message/email
    title_str = sf_reskin(str(m.get("name") or "JOB")).upper()
    prefix = "SUBJECT: " if theme["kind"] == "email" else ""
    full_title = f"{prefix}{title_str}"
    f_title = rgc.fit_font(rem.F_COND, full_title, (bx1 - bx0) - 64, 52, min_size=30)
    bb_t = draw.textbbox((0, 0), full_title, font=f_title)
    tw, th = bb_t[2] - bb_t[0], bb_t[3] - bb_t[1]
    ty = by0 + 28
    title_col = (255, 215, 90) if is_dark else theme["header_bg"]
    if theme["id"] in ("iphone", "snapchat", "bumble", "grindr"):
        title_col = (255, 195, 0) if is_dark else (18, 22, 30)
    draw.text((bx0 + (bx1 - bx0 - tw) // 2 - bb_t[0], ty), full_title, font=f_title, fill=title_col)
    underline_y = ty + th + 16
    draw.line((bx0 + 36, underline_y, bx1 - 36, underline_y), fill=theme["card_border"], width=3)

    # 5. Large Concise Job Assignment Text (Strictly in the center information face)
    concise_text = format_job_concise_text(m)
    has_delivery_table = str(m.get("kind", "")).lower() == "delivery" and isinstance(m.get("fencedSell"), list) and len(m["fencedSell"]) >= 5

    pad_x = 38
    avail_w = (bx1 - bx0) - 2 * pad_x
    text_top = underline_y + 18
    text_bottom = (by1 - 220) if has_delivery_table else (by1 - 34)
    avail_h = max(120, text_bottom - text_top)

    best_font = ImageFont.truetype(rem.F_BOLD, 34)
    best_lines = [concise_text]
    for sz in range(54, 26, -2):
        f_try = ImageFont.truetype(rem.F_BOLD, sz)
        lines = rem.wrap_text_lines(draw, concise_text, f_try, avail_w)
        if len(lines) * int(sz * 1.25) <= avail_h:
            best_font = f_try
            best_lines = lines
            break

    lh = int(best_font.size * 1.25)
    tot_th = len(best_lines) * lh
    cy = text_top + max(0, (avail_h - tot_th) // 2)
    ink_col = (248, 250, 255) if is_dark else (16, 20, 28)
    stroke_col = (10, 12, 18) if is_dark else (255, 255, 255)
    for ln in best_lines:
        bb_l = draw.textbbox((0, 0), ln, font=best_font)
        lw = bb_l[2] - bb_l[0]
        lx = bx0 + pad_x + (avail_w - lw) // 2 - bb_l[0]
        draw.text((lx, cy), ln, font=best_font, fill=ink_col, stroke_width=3, stroke_fill=stroke_col)
        cy += lh

    # 6. Delivery Fence Value Price Table (only if delivery job)
    if has_delivery_table:
        good_spec = {
            "name": sf_reskin(str(m.get("item") or "Cargo")),
            "category": sf_reskin(str(m.get("category") or "Good")),
            "blocks": max(1, int(m.get("blocks") or 1)),
            "sell": [rgc.btc(v) for v in m["fencedSell"][:5]],
        }
        rem.draw_good_price_grid(
            im,
            draw,
            bx0 + 18,
            by1 - 212,
            bx1 - 18,
            by1 - 14,
            good_spec,
            dark_mode=is_dark,
        )

    # 7. Bottom Phone Chin / Home Indicator Bezel (y=1296..1352) so the phone frame encloses all 4 sides
    draw.rectangle((SX0, SY1, SX1, 1354), fill=(14, 18, 24))
    draw.line((SX0, SY1, SX1, SY1), fill=(58, 70, 78), width=2)
    draw.rounded_rectangle((345, 1320, 555, 1330), radius=5, fill=(148, 158, 172))

    # 8. Blend Subtle Cracked-Screen Overlay & Composite into Full-Bleed 4-Sided Phone Frame
    rgb_arr = np.array(im.convert("RGB"), dtype=np.float32)
    scr_sub = rgb_arr[36:1352, 46:854, :]
    scr_sub = np.clip(scr_sub + glass_delta * 0.42, 0, 255)
    rgb_arr[36:1352, 46:854, :] = scr_sub
    comp = Image.fromarray(rgb_arr.astype(np.uint8))
    final = Image.composite(comp, phone_base, mask).resize((848, 1264), Image.LANCZOS)
    final.convert("RGB").save(out_path, quality=90)


# ============================================================================
# 3. RENDER ALL 88 ENCOUNTER CARDS ON FULL-BLEED ENCOUNTER TEMPLATES
# ============================================================================
ENCOUNTER_ARCHETYPES_BY_DECK = {
    "cops": ["police_id_badge", "police_id_phone", "news_article"],
    "celebrities": ["wikipedia", "news_article", "craigslist"],
    "criminals": ["wanted_poster", "snapchat", "payment", "craigslist"],
}

PORTRAIT_FILES_BY_DECK = {
    "cops": ["portrait_cop.jpg", "portrait_dea.jpg"],
    "celebrities": ["portrait_zuck.jpg", "portrait_scammer.jpg", "portrait_farmer.jpg"],
    "criminals": ["portrait_wanted.jpg", "portrait_enforcer.jpg", "portrait_scammer.jpg", "portrait_farmer.jpg"],
}


def pick_portrait_path(card: dict, deck_key: str) -> str:
    name_l = str(card.get("name") or "").lower()
    if "zuckerberg" in name_l:
        return os.path.join(PORTRAITS_DIR, "portrait_zuck.jpg")
    if "narcotics" in name_l:
        return os.path.join(PORTRAITS_DIR, "portrait_cop.jpg")
    if "dea" in name_l or "ice" in name_l:
        return os.path.join(PORTRAITS_DIR, "portrait_dea.jpg")
    if "scammer" in name_l or "crypto" in name_l:
        return os.path.join(PORTRAITS_DIR, "portrait_scammer.jpg")
    if "enforcer" in name_l or "clique" in name_l:
        return os.path.join(PORTRAITS_DIR, "portrait_enforcer.jpg")
    if "farmer" in name_l:
        return os.path.join(PORTRAITS_DIR, "portrait_farmer.jpg")
    candidates = PORTRAIT_FILES_BY_DECK.get(deck_key, PORTRAIT_FILES_BY_DECK["celebrities"])
    h = stable_hash(str(card.get("id") or card.get("name") or "0"))
    return os.path.join(PORTRAITS_DIR, candidates[h % len(candidates)])


def convert_card_to_spec(card: dict, deck_key: str) -> dict:
    cid = str(card.get("id") or "pat_1")
    h = stable_hash(cid)
    archs = ENCOUNTER_ARCHETYPES_BY_DECK.get(deck_key, ENCOUNTER_ARCHETYPES_BY_DECK["celebrities"])
    archetype = archs[h % len(archs)]

    # Specific iconic overrides
    name_l = str(card.get("name") or "").lower()
    if "zuckerberg" in name_l:
        archetype = "wikipedia"
    elif "narcotics" in name_l:
        archetype = "police_id_badge"
    elif "dea" in name_l:
        archetype = "news_article"
    elif "scammer" in name_l:
        archetype = "payment"
    elif "enforcer" in name_l:
        archetype = "wanted_poster"
    elif "farmer" in name_l:
        archetype = "craigslist"

    raw_up = card.get("friendlyFavor") or ([card["faction"]] if card.get("faction") else [])
    raw_dn = card.get("hostileFavor") or ([f"-{card['faction']}"] if card.get("faction") else [])
    friendly_gems = []
    for g in raw_up:
        if g:
            gn, neg = parse_gem_token(g)
            friendly_gems.append((gn, "-" if neg else "+"))
    hostile_gems = []
    for g in raw_dn:
        if g:
            gn, neg = parse_gem_token(g)
            hostile_gems.append((gn, "-" if neg else "+"))

    tiers = []
    for r in (card.get("reactions") or []):
        cond = (
            str(r.get("condition") or ">=0")
            .replace("-1..0", "-1 to 0")
            .replace("0..1", "0-1")
            .replace("<=", "\u2264 ")
            .replace(">=", "\u2265 ")
            .replace("==", "= ")
        )
        rtype = str(r.get("type") or r.get("effect") or "demand")
        if rtype == "combat":
            if r.get("ifCarrying"):
                eff = f"IF_CARRYING:{sf_reskin(str(r.get('ifCarrying')))}"
            else:
                eff = "COMBAT"
        elif rtype == "demand_strict":
            eff = "!!"
        elif rtype == "demand":
            eff = "!"
        elif rtype in ("offer", "quest_optional"):
            eff = "?"
        elif rtype == "mission_strict":
            eff = "CASH_!!"
        elif rtype == "mission_request":
            eff = "CASH_!"
        elif rtype in ("mission_offer", "mission_bonus"):
            eff = "CASH_?"
        elif rtype == "deck_quest_strict":
            eff = "DECK_CASH_!!"
        elif rtype == "deck_quest_demand":
            eff = "DECK_CASH_!"
        elif rtype == "deck_quest_offer":
            eff = "DECK_CASH_?"
        else:
            eff = "!"
        tiers.append((cond, eff))
    if not tiers:
        tiers = [("\u2264 -1", "COMBAT"), ("\u2265 0", "!")]

    raw_act_str = card.get("actionText")
    act_text = sf_reskin(str(raw_act_str if raw_act_str is not None else "Comply with this party."))
    lines = [ln.strip() for ln in re.split(r"[\n\r]+|\s+•\s+", act_text) if ln.strip()]
    assignments = []
    for ln in lines:
        m_job = re.match(r"^(?:\[cash\]|\(QUEST_ICON\)|\(DECK_ICON\)\(QUEST_ICON\))([!?]+)\s*(.*)$", ln, flags=re.IGNORECASE)
        m_deal = re.match(r"^\[([!?]+)\]\s*(.*)$", ln)
        if m_job:
            assignments.append(("job", m_job.group(1), m_job.group(2)))
        elif m_deal:
            assignments.append(("deal", m_deal.group(1), m_deal.group(2)))
        else:
            cleaned = re.sub(r"^\(QUEST_ICON\)[!?]*\s*", "", ln)
            assignments.append(("deal", "!", cleaned))

    good_table = None
    m_obj = card.get("mission")
    if isinstance(m_obj, dict) and str(m_obj.get("kind", "")).lower() == "delivery" and isinstance(m_obj.get("fencedSell"), list) and len(m_obj["fencedSell"]) >= 5:
        cat_str = sf_reskin(str(m_obj.get("category") or "Good"))
        if m_obj.get("subcategory"):
            sub_str = sf_reskin(str(m_obj["subcategory"]))
            if sub_str and sub_str.lower() != cat_str.lower():
                cat_str = f"{cat_str}, {sub_str}"
        good_table = {
            "name": sf_reskin(str(m_obj.get("item") or "Cargo")),
            "category": cat_str,
            "blocks": max(1, int(m_obj.get("blocks") or 1)),
            "combat": sf_reskin(str(m_obj.get("combatText") or "")),
            "sell": [rgc.btc(v) for v in m_obj["fencedSell"][:5]],
        }
    elif isinstance(card.get("offerGood"), dict):
        og = card["offerGood"]
        if isinstance(og.get("sell"), list) and len(og["sell"]) >= 5:
            good_table = {
                "name": sf_reskin(str(og.get("name") or "Special Good")),
                "category": sf_reskin(str(og.get("category") or "Good")),
                "blocks": max(1, int(og.get("blocks") or 1)),
                "combat": sf_reskin(str(og.get("combatText") or "")),
                "sell": [rgc.btc(v) for v in og["sell"][:5]],
                "buy": [rgc.btc(v) for v in og["buy"][:5]] if (isinstance(og.get("buy"), list) and len(og["buy"]) >= 5) else None,
            }

    def _short_rew(s: str) -> str:
        out = sf_reskin(s)
        out = out.replace(" & +1 Influence Card", " + 1 Inf").replace(" & +1 Influence", " + 1 Inf").replace(" & 1 Influence Card", " + 1 Inf").replace(" & 1 Influence", " + 1 Inf")
        out = out.replace(" & +1 TECH Favor", " + 1 Diamond").replace(" & Cheapest ", " + Cheap ")
        out = out.replace("Cheapest ", "Cheap ").replace(" on Market", " Mkt").replace(" on Mkt", " Mkt").replace(" on the Market", " Mkt").replace(" from Market", " Mkt")
        out = out.replace("Influence Cards", "Inf").replace("Influence Card", "Inf").replace("Influence", "Inf")
        return out.strip()

    cp_raw = str(card.get("combatFormula") or "2(R)")

    return {
        "archetype": archetype,
        "faction": str(card.get("faction") or "TECH").upper() if str(card.get("faction") or "").upper() in rem.FACTION_BAR_STYLE else "TECH",
        "name": sf_reskin(str(card.get("name") or "Encounter")),
        "bio": sf_reskin(str(card.get("bio") or f"{deck_key.title()} Encounter")),
        "cp": cp_raw,
        "friendly_reward": _short_rew(str(card.get("friendlyReward") or "₿1.5")),
        "combat_loot": _short_rew(str(card.get("combatReward") or "₿2")),
        "friendly_gems": friendly_gems,
        "hostile_gems": hostile_gems,
        "tiers": tiers,
        "assignments": assignments,
        "good_table": good_table,
        "portrait_path": pick_portrait_path(card, deck_key),
    }


def build_clean_wanted_base():
    raw_w = Image.open(os.path.join(rem.PREV_ARTIFACT_DIR, "enc_criminals_wanted_1794554990209.jpg")).convert("RGB")
    w_card = raw_w.resize((rem.CARD_W, rem.CARD_H), Image.LANCZOS).convert("RGBA")
    w_arr = np.array(w_card.convert("RGB"))

    rt_crop = w_arr[1278:1386, 34:132].copy()
    r, g, b = rt_crop[:, :, 0].astype(np.int16), rt_crop[:, :, 1].astype(np.int16), rt_crop[:, :, 2].astype(np.int16)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    is_red = (r - g > 42) & (r > 85)
    k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    near_red = cv2.dilate(is_red.astype(np.uint8), k5, iterations=1) > 0
    fg_mask = (is_red | ((lum < 95) & near_red)).astype(np.uint8) * 255
    fg_mask = cv2.GaussianBlur(fg_mask, (3, 3), 0.8)
    rt_rgba = np.dstack([rt_crop, fg_mask])
    rt_up = Image.fromarray(rt_rgba).rotate(180, resample=Image.BICUBIC).resize((80, 74), Image.LANCZOS)

    bot_roi = w_arr[1272:1392, 28:140]
    br, bg_c, bb_c = bot_roi[:, :, 0].astype(np.int16), bot_roi[:, :, 1].astype(np.int16), bot_roi[:, :, 2].astype(np.int16)
    blum = 0.299 * br + 0.587 * bg_c + 0.114 * bb_c
    b_mask = (((br - bg_c) > 32) | (blum < 95)).astype(np.uint8) * 255
    b_mask = cv2.dilate(b_mask, np.ones((5, 5), np.uint8), iterations=2)
    w_arr[1272:1392, 28:140] = cv2.inpaint(bot_roi, b_mask, 7, cv2.INPAINT_TELEA)

    tl_roi = w_arr[8:110, 128:300]
    tl_r, tl_g, tl_b = tl_roi[:, :, 0].astype(np.int16), tl_roi[:, :, 1].astype(np.int16), tl_roi[:, :, 2].astype(np.int16)
    tl_lum = 0.299 * tl_r + 0.587 * tl_g + 0.114 * tl_b
    tl_mask = ((tl_lum < 145) | (np.abs(tl_r - tl_g) > 30) | (np.abs(tl_b - tl_g) > 28)).astype(np.uint8) * 255
    tl_mask[:8, :] = 0
    tl_mask[-8:, :] = 0
    tl_mask[:, :8] = 0
    tl_mask[:, -8:] = 0
    tl_mask = cv2.dilate(tl_mask, np.ones((5, 5), np.uint8), iterations=2)
    w_arr[8:110, 128:300] = cv2.inpaint(tl_roi, tl_mask, 7, cv2.INPAINT_TELEA)

    tr_roi = w_arr[16:112, 750:880]
    tlum = tr_roi.mean(axis=2)
    t_mask = ((tlum < 120) | (tlum > 235)).astype(np.uint8) * 255
    t_mask = cv2.dilate(t_mask, np.ones((5, 5), np.uint8), iterations=2)
    w_arr[16:112, 750:880] = cv2.inpaint(tr_roi, t_mask, 7, cv2.INPAINT_TELEA)

    # Inpaint out the right-side title/bio/cp text on Wanted poster (y=282..648, x=474..836) without touching WANTED!
    cf_roi = w_arr[282:648, 474:836]
    cflum = cf_roi.mean(axis=2)
    cf_mask = (cflum < 125).astype(np.uint8) * 255
    cf_mask = cv2.dilate(cf_mask, np.ones((5, 5), np.uint8), iterations=2)
    w_arr[282:648, 474:836] = cv2.inpaint(cf_roi, cf_mask, 7, cv2.INPAINT_TELEA)
    return Image.fromarray(w_arr).convert("RGBA"), rt_up


def build_clean_police_id_base():
    raw_id = Image.open(os.path.join(rem.PREV_ARTIFACT_DIR, "enc_cops_police_id_1794554967299.jpg")).convert("RGB")
    id_card = raw_id.resize((rem.CARD_W, rem.CARD_H), Image.LANCZOS).convert("RGBA")
    arr = np.array(id_card.convert("RGB"))

    rt_cop_crop = arr[1268:1326, 88:146].copy()
    cr, cg, cb = rt_cop_crop[:, :, 0].astype(np.int16), rt_cop_crop[:, :, 1].astype(np.int16), rt_cop_crop[:, :, 2].astype(np.int16)
    clum = 0.299 * cr + 0.587 * cg + 0.114 * cb
    is_thumb_red = (cr - cg) > 75
    k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    near_thumb_red = cv2.dilate(is_thumb_red.astype(np.uint8), k3, iterations=1) > 0
    cop_rt_mask = (is_thumb_red | ((clum < 55) & near_thumb_red)).astype(np.uint8) * 255
    cop_rt_rgba = np.dstack([rt_cop_crop, cop_rt_mask])
    rt_cop_up = Image.fromarray(cop_rt_rgba).rotate(180, resample=Image.BICUBIC).resize((56, 56), Image.LANCZOS)

    for x in range(152, 305):
        arr[71:138, x] = arr[71:138, 450]
    for x in range(735, 816):
        arr[71:138, x] = arr[71:138, 725]
    arr[1263:1330, 84:152] = arr[1263:1330, 170:238]

    # Erase right-side title/bio/cp region on Police ID below header (y=332..596, x=364..795)
    for y in range(332, 596):
        arr[y, 364:795] = arr[y, 798]

    cream_med = np.median(arr[815:860, 200:700], axis=(0, 1)).astype(np.uint8)
    arr[800:1228, 104:796] = cream_med
    return Image.fromarray(arr).convert("RGBA"), rt_cop_up


def render_encounter_card(spec: dict, out_path: str, bases: dict):
    arch = spec["archetype"]
    p_im = Image.open(spec["portrait_path"]).convert("RGB")

    if arch == "wanted_poster":
        w_card = bases["wanted_base"].copy()
        rt_up = bases["wanted_rt"]
        d = ImageDraw.Draw(w_card)

        # Draw character name, bio, and large CP formula on right (x=478..836, y=288..600)
        f_name = rgc.fit_font(rem.F_COND, spec["name"].upper(), 355, 56, min_size=34)
        d.text((478, 288), spec["name"].upper(), font=f_name, fill=(20, 18, 16))
        f_bio = ImageFont.truetype(rem.F_REG, 22)
        bio_lines = rem.wrap_text_lines(d, spec["bio"], f_bio, 355)[:4]
        by = 358
        for ln in bio_lines:
            d.text((478, by), ln, font=f_bio, fill=(38, 34, 30))
            by += 28
        rem.draw_cp_line(w_card, 478, 548, spec["cp"], dark_text=True, icon_sz=68, font_sz=58)

        # Top & Bottom outcome bars
        f_colon = ImageFont.truetype(rem.F_BOLD, 44)
        top_cy = 58
        gem_sz_top = 64 if len(spec["friendly_gems"]) >= 3 else 80
        gem_sz_bot = 64 if len(spec["hostile_gems"]) >= 3 else 80
        d.text((116, top_cy - 24), ":", font=f_colon, fill=(255, 255, 255), stroke_width=4, stroke_fill=(12, 12, 16))
        gx = 138
        for g_name, sign in spec["friendly_gems"]:
            gx = rem.draw_gem_with_slash(w_card, gx, top_cy - gem_sz_top // 2, g_name, is_negative=(sign == "-"), size=gem_sz_top, black_border=True, border_px=4)
            gx += 4

        rew_txt = f":{spec['friendly_reward']}"
        f_rew_top = rgc.fit_font(rem.F_SYM, rew_txt, max(160, 868 - gx - 72), 40, min_size=24)
        bb_r = d.textbbox((0, 0), rew_txt, font=f_rew_top)
        rw, rh = bb_r[2] - bb_r[0], bb_r[3] - bb_r[1]
        rx = 868 - rw
        cash_icon = rem.load_icon("cash_white.png", 60)
        rem.paste_with_optional_border(w_card, cash_icon, rx - 64, top_cy - 30, black_border=True, border_px=3)
        d.text((rx, top_cy - rh // 2 - bb_r[1]), rew_txt, font=f_rew_top, fill=(255, 255, 255), stroke_width=4, stroke_fill=(12, 12, 16))

        bot_cy = 1330
        pistol_w = rem.load_icon("pistol_white.png", 58)
        rem.paste_with_optional_border(w_card, pistol_w, 42, bot_cy - 29, black_border=True, border_px=3)

        td_x = 866 - rt_up.size[0]
        w_card.paste(rt_up, (td_x, bot_cy - rt_up.size[1] // 2), rt_up)
        d.text((td_x - 22, bot_cy - 24), ":", font=f_colon, fill=(255, 255, 255), stroke_width=4, stroke_fill=(12, 12, 16))
        hx = td_x - 26
        for g_name, sign in reversed(spec["hostile_gems"]):
            hx -= (gem_sz_bot + 6)
            rem.draw_gem_with_slash(w_card, hx, bot_cy - gem_sz_bot // 2, g_name, is_negative=(sign == "-"), size=gem_sz_bot, black_border=True, border_px=4)

        loot_txt = f":{spec['combat_loot']}"
        f_rew_bot = rgc.fit_font(rem.F_SYM, loot_txt, max(160, hx - 118), 40, min_size=24)
        bb_l = d.textbbox((0, 0), loot_txt, font=f_rew_bot)
        lh = bb_l[3] - bb_l[1]
        d.text((108, bot_cy - lh // 2 - bb_l[1]), loot_txt, font=f_rew_bot, fill=(255, 255, 255), stroke_width=4, stroke_fill=(12, 12, 16))

        rem.draw_tall_faction_interaction_bar(w_card, 55, 698, 845, 817, spec["faction"], spec["tiers"])
        d.rectangle((58, 856, 842, 1240), fill=(224, 212, 190))
        rem.draw_lower_card_details(w_card, 56, 856, 844, 1240, False, spec["assignments"], spec["good_table"])
        w_card.convert("RGB").save(out_path, quality=90)
        return

    if arch == "police_id_badge":
        id_card = bases["police_id_base"].copy()
        rt_cop_up = bases["police_id_rt"]
        d = ImageDraw.Draw(id_card)

        f_name = rgc.fit_font(rem.F_COND, spec["name"].upper(), 420, 52, min_size=32)
        d.text((368, 336), spec["name"].upper(), font=f_name, fill=(14, 20, 30))
        f_bio = ImageFont.truetype(rem.F_REG, 21)
        bio_lines = rem.wrap_text_lines(d, spec["bio"], f_bio, 420)[:4]
        by = 398
        for ln in bio_lines:
            d.text((368, by), ln, font=f_bio, fill=(32, 38, 48))
            by += 26
        rem.draw_cp_line(id_card, 368, 548, spec["cp"], dark_text=True, icon_sz=64, font_sz=56)

        f_colon = ImageFont.truetype(rem.F_BOLD, 38)
        top_cy = 104
        gem_sz_top = 50 if len(spec["friendly_gems"]) >= 3 else 60
        gem_sz_bot = 50 if len(spec["hostile_gems"]) >= 3 else 60
        d.text((156, top_cy - 22), ":", font=f_colon, fill=(255, 255, 255), stroke_width=3, stroke_fill=(12, 24, 18))
        gx = 176
        for g_name, sign in spec["friendly_gems"]:
            gx = rem.draw_gem_with_slash(id_card, gx, top_cy - gem_sz_top // 2, g_name, is_negative=(sign == "-"), size=gem_sz_top, black_border=True, border_px=3)
            gx += 2

        rew_txt = f":{spec['friendly_reward']}"
        f_rew_top = rgc.fit_font(rem.F_SYM, rew_txt, max(150, 812 - gx - 64), 36, min_size=22)
        bb_r = d.textbbox((0, 0), rew_txt, font=f_rew_top)
        rw, rh = bb_r[2] - bb_r[0], bb_r[3] - bb_r[1]
        rx = 812 - rw
        cash_w = rem.load_icon("cash_white.png", 52)
        rem.paste_with_optional_border(id_card, cash_w, rx - 56, top_cy - 26, black_border=True, border_px=2)
        d.text((rx, top_cy - rh // 2 - bb_r[1]), rew_txt, font=f_rew_top, fill=(255, 255, 255), stroke_width=3, stroke_fill=(12, 24, 18))

        bot_cy = 1296
        pistol_w = rem.load_icon("pistol_white.png", 52)
        rem.paste_with_optional_border(id_card, pistol_w, 84, bot_cy - 26, black_border=True, border_px=2)

        td_x = 814 - rt_cop_up.size[0]
        id_card.paste(rt_cop_up, (td_x, bot_cy - rt_cop_up.size[1] // 2), rt_cop_up)
        d.text((td_x - 18, bot_cy - 22), ":", font=f_colon, fill=(255, 255, 255), stroke_width=3, stroke_fill=(28, 10, 14))
        hx = td_x - 24
        for g_name, sign in reversed(spec["hostile_gems"]):
            hx -= (gem_sz_bot + 6)
            rem.draw_gem_with_slash(id_card, hx, bot_cy - gem_sz_bot // 2, g_name, is_negative=(sign == "-"), size=gem_sz_bot, black_border=True, border_px=3)

        loot_txt = f":{spec['combat_loot']}"
        f_rew_bot = rgc.fit_font(rem.F_SYM, loot_txt, max(150, hx - 150), 36, min_size=22)
        bb_l = d.textbbox((0, 0), loot_txt, font=f_rew_bot)
        lh = bb_l[3] - bb_l[1]
        d.text((142, bot_cy - lh // 2 - bb_l[1]), loot_txt, font=f_rew_bot, fill=(255, 255, 255), stroke_width=3, stroke_fill=(28, 10, 14))

        rem.draw_tall_faction_interaction_bar(id_card, 96, 652, 804, 766, spec["faction"], spec["tiers"])
        rem.draw_lower_card_details(id_card, 98, 792, 802, 1234, False, spec["assignments"], spec["good_table"])
        # Crop slightly so the ID card edges are just barely enclosed within the edges of the image
        id_card = id_card.crop((32, 32, 868, 1372)).resize((rem.CARD_W, rem.CARD_H), Image.LANCZOS)
        id_card.convert("RGB").save(out_path, quality=90)
        return

    # Smartphone screen archetypes
    phone_base, mask, glass_delta = bases["phone_base"], bases["phone_mask"], bases["phone_glass"]
    SX0, SX1 = 46, 854
    SY_TOP, SY_BOT = 104, 1278
    c_scr = phone_base.copy().convert("RGBA")
    d = ImageDraw.Draw(c_scr)

    dark_mode = arch in ("snapchat", "payment")
    if arch == "snapchat":
        d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(18, 18, 22))
        hy0, hy1 = SY_TOP, SY_TOP + 72
        d.rectangle((SX0, hy0, SX1, hy1), fill=(255, 252, 0))
        d.text((SX0 + 28, hy0 + 14), "SnatchTap", font=ImageFont.truetype(rem.F_BOLD, 36), fill=(14, 14, 18))
        d.rounded_rectangle((SX0 + 16, 190, SX1 - 16, 618), radius=16, fill=(28, 28, 34), outline=(255, 252, 0), width=3)
        d.rounded_rectangle((SX0 + 16, 808, SX1 - 16, 1266), radius=14, fill=(28, 28, 34), outline=(255, 252, 0), width=2)
        title_col, bio_col = (255, 255, 255), (224, 226, 232)
    elif arch == "payment":
        d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(14, 20, 18))
        hy0, hy1 = SY_TOP, SY_TOP + 70
        d.rectangle((SX0, hy0, SX1, hy1), fill=(0, 214, 79))
        d.text((SX0 + 22, hy0 + 13), "$CashNet • P2P ESCROW", font=ImageFont.truetype(rem.F_BOLD, 34), fill=(10, 18, 12))
        d.rounded_rectangle((SX0 + 16, 188, SX1 - 16, 618), radius=14, fill=(22, 32, 28), outline=(0, 195, 75), width=2)
        d.rounded_rectangle((SX0 + 16, 808, SX1 - 16, 1266), radius=14, fill=(24, 34, 30), outline=(0, 195, 75), width=2)
        title_col, bio_col = (248, 255, 250), (205, 220, 212)
    elif arch == "wikipedia":
        d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(255, 255, 255))
        hy0, hy1 = SY_TOP, SY_TOP + 70
        d.rectangle((SX0, hy0, SX1, hy1), fill=(234, 236, 240))
        d.text((SX0 + 24, hy0 + 15), "WikiBio • Biographical Encyclopedia", font=ImageFont.truetype(rem.F_SERIF_B, 28), fill=(32, 33, 34))
        d.rounded_rectangle((SX0 + 16, 188, SX1 - 16, 618), radius=6, fill=(248, 249, 250), outline=(162, 169, 177), width=2)
        d.rounded_rectangle((SX0 + 16, 808, SX1 - 16, 1266), radius=6, fill=(248, 249, 250), outline=(162, 169, 177), width=2)
        title_col, bio_col = (32, 33, 34), (48, 50, 54)
    elif arch == "craigslist":
        d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(255, 255, 255))
        hy0, hy1 = SY_TOP, SY_TOP + 68
        d.rectangle((SX0, hy0, SX1, hy1), fill=(238, 238, 246))
        d.text((SX0 + 20, hy0 + 14), "greg's list > sfbay > gigs", font=ImageFont.truetype(rem.F_SERIF, 26), fill=(85, 26, 139))
        d.rectangle((SX0 + 16, 184, SX1 - 16, 618), fill=(250, 250, 252), outline=(204, 204, 216), width=2)
        d.rectangle((SX0 + 16, 808, SX1 - 16, 1266), fill=(250, 250, 252), outline=(204, 204, 216), width=2)
        title_col, bio_col = (0, 0, 210), (28, 28, 32)
    elif arch == "police_id_phone":
        d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(218, 224, 232))
        d.rounded_rectangle((SX0 + 16, 114, SX1 - 16, 618), radius=18, fill=(236, 241, 246), outline=(28, 42, 68), width=4)
        d.rounded_rectangle((SX0 + 19, 117, SX1 - 19, 192), radius=15, fill=(14, 32, 62))
        d.text((SX0 + 36, 132), "SAN FRANCISCO POLICE DEPT. • CREDENTIAL", font=ImageFont.truetype(rem.F_COND, 34), fill=(255, 255, 255))
        d.rounded_rectangle((SX0 + 16, 808, SX1 - 16, 1266), radius=12, fill=(246, 245, 240), outline=(45, 52, 64), width=3)
        title_col, bio_col = (14, 20, 30), (32, 38, 48)
    else:  # news_article
        d.rectangle((SX0, SY_TOP, SX1, SY_BOT), fill=(246, 242, 232))
        hy0, hy1 = SY_TOP, SY_TOP + 76
        d.rectangle((SX0, hy0, SX1, hy1), fill=(238, 232, 218))
        d.text((SX0 + 180, hy0 + 14), "The SF Chronicler", font=ImageFont.truetype(rem.F_SERIF_B, 40), fill=(20, 18, 16))
        d.rectangle((SX0 + 16, 192, SX1 - 16, 618), fill=(252, 249, 242), outline=(180, 172, 158), width=2)
        d.rectangle((SX0 + 16, 808, SX1 - 16, 1266), fill=(252, 249, 242), outline=(180, 172, 158), width=2)
        title_col, bio_col = (18, 18, 18), (32, 30, 28)

    f_name = rgc.fit_font(rem.F_BOLD, spec["name"], 460, 42, min_size=26)
    d.text((SX0 + 34, 210), spec["name"], font=f_name, fill=title_col)
    f_bio = ImageFont.truetype(rem.F_REG, 22)
    bio_lines = rem.wrap_text_lines(d, spec["bio"], f_bio, 460)[:5]
    by = 278
    for ln in bio_lines:
        d.text((SX0 + 34, by), ln, font=f_bio, fill=bio_col)
        by += 29

    rem.draw_cp_line(c_scr, SX0 + 34, 536, spec["cp"], dark_text=(not dark_mode), icon_sz=62, font_sz=54)

    p_crop = p_im.resize((228, 268), Image.LANCZOS)
    c_scr.paste(p_crop, (SX1 - 266, 236))
    d.rectangle((SX1 - 266, 236, SX1 - 38, 504), outline=(120, 125, 135), width=3)

    rem.draw_tall_faction_interaction_bar(c_scr, SX0 + 16, 630, SX1 - 16, 796, spec["faction"], spec["tiers"])
    rem.draw_lower_card_details(c_scr, SX0 + 16, 808, SX1 - 16, 1266, dark_mode, spec["assignments"], spec["good_table"])
    rem.draw_phone_bezel_outcomes(
        c_scr,
        friendly_gems=spec["friendly_gems"],
        friendly_reward=spec["friendly_reward"],
        combat_loot=spec["combat_loot"],
        hostile_gems=spec["hostile_gems"],
    )

    scr_arr = np.array(c_scr.convert("RGB"), dtype=np.float32)
    sub = scr_arr[36:1352, 46:854, :]
    sub = np.clip(sub + glass_delta * 0.45, 0, 255)
    scr_arr[36:1352, 46:854, :] = sub
    comp = Image.fromarray(scr_arr.astype(np.uint8))
    final = Image.composite(comp, phone_base, mask)
    final.convert("RGB").save(out_path, quality=90)


def main():
    os.makedirs(os.path.join(CARDS_DIR, "influence"), exist_ok=True)
    os.makedirs(os.path.join(CARDS_DIR, "jobs"), exist_ok=True)
    os.makedirs(os.path.join(CARDS_DIR, "encounters"), exist_ok=True)
    os.makedirs(os.path.join(CARDS_DIR, "goods"), exist_ok=True)

    mm = json.load(open(os.path.join(ROOT, "src/data/market_and_missions.json"), encoding="utf-8"))
    dk = json.load(open(os.path.join(ROOT, "src/data/decks.json"), encoding="utf-8"))
    rc = json.load(open(os.path.join(ROOT, "src/data/reserve_cards.json"), encoding="utf-8"))

    # 1. Influence cards (preserve user's manual edits on ClockTok & FaceSpace cards)
    MANUALLY_FIXED_INFLUENCE_IDS = {
        "inf_2", "inf_12", "inf_14", "inf_17", "inf_22",
        "inf_27", "inf_29", "inf_34", "inf_37", "inf_39",
        "inf_44", "inf_49", "inf_52", "inf_57", "inf_59",
    }
    inf_count = 0
    for c in dk.get("influence", []):
        cid = c.get("id")
        if not cid:
            continue
        out_p = os.path.join(CARDS_DIR, "influence", f"{cid}.jpg")
        if cid in MANUALLY_FIXED_INFLUENCE_IDS and os.path.exists(out_p):
            continue
        render_influence_card(c, out_p)
        inf_count += 1
    print(f"Rendered {inf_count} Influence cards.")

    # 2. Job cards (+ cargo good cards for delivery jobs)
    job_count = 0
    for m in mm.get("missions", []):
        mid = m.get("id")
        if not mid:
            continue
        out_p = os.path.join(CARDS_DIR, "jobs", f"{mid}.jpg")
        render_job_card(m, out_p)
        job_count += 1

        if str(m.get("kind", "")).lower() == "delivery":
            cat = m.get("category") or "Grain"
            tpl_name = rgc.TRACK_TO_TEMPLATE.get(cat, "weed_humboldt_indoor.png")
            cargo_card = {
                "id": f"mcargo_{mid}",
                "name": sf_reskin(str(m.get("item") or "Job Cargo")),
                "subtitle": "JOB CARGO",
                "track": cat,
                "subcategory": cat,
                "blocks": max(1, int(m.get("blocks") or 1)),
                "henchmen": 0,
                "combat": m.get("combat"),
                "combatText": sf_reskin(str(m.get("combatText") or "")) if m.get("combatText") else None,
                "sell": m.get("fencedSell") if (isinstance(m.get("fencedSell"), list) and len(m["fencedSell"]) >= 5) else [50, 40, 30, 20, 10],
                "buy": [0, 0, 0, 0, 0],
            }
            rgc.render(
                cargo_card,
                os.path.join(MOCKUPS_DIR, tpl_name),
                os.path.join(CARDS_DIR, "goods", f"mcargo_{mid}.jpg"),
            )
    print(f"Rendered {job_count} Job cards.")

    # 3. Encounter cards
    phone_base, phone_mask, phone_glass = rem.prepare_full_bleed_phone_base()
    wanted_base, wanted_rt = build_clean_wanted_base()
    police_id_base, police_id_rt = build_clean_police_id_base()
    bases = {
        "phone_base": phone_base,
        "phone_mask": phone_mask,
        "phone_glass": phone_glass,
        "wanted_base": wanted_base,
        "wanted_rt": wanted_rt,
        "police_id_base": police_id_base,
        "police_id_rt": police_id_rt,
    }

    enc_count = 0
    for deck_key in ("celebrities", "cops", "criminals"):
        all_cards = list(dk.get(deck_key, [])) + list(rc.get(deck_key, []))
        for c in all_cards:
            cid = c.get("id")
            if not cid:
                continue
            out_p = os.path.join(CARDS_DIR, "encounters", f"{cid}.jpg")
            if c.get("type") == "event":
                spec = {
                    "archetype": "news_article",
                    "faction": "TECH",
                    "name": sf_reskin(str(c.get("name") or "Street Event")),
                    "bio": f"{deck_key.upper()} • MANDATORY STREET EVENT",
                    "cp": "0",
                    "friendly_reward": "₿0",
                    "combat_loot": "₿0",
                    "friendly_gems": [],
                    "hostile_gems": [],
                    "tiers": [("EVENT", "!")],
                    "assignments": [("deal", "!", sf_reskin(str(c.get("actionText") or "Resolve event.")))],
                    "good_table": None,
                    "portrait_path": pick_portrait_path(c, deck_key),
                }
            else:
                spec = convert_card_to_spec(c, deck_key)
            render_encounter_card(spec, out_p, bases)
            enc_count += 1

            m_obj = c.get("mission")
            if isinstance(m_obj, dict) and str(m_obj.get("kind", "")).lower() == "delivery":
                cat = m_obj.get("category") or "Weapons"
                tpl_name = rgc.TRACK_TO_TEMPLATE.get(cat, "weapons_glock_19.png")
                cargo_card = {
                    "id": f"mcargo_{cid}",
                    "name": sf_reskin(str(m_obj.get("item") or "Job Cargo")),
                    "subtitle": "JOB CARGO",
                    "track": cat,
                    "subcategory": cat,
                    "blocks": max(1, int(m_obj.get("blocks") or 1)),
                    "henchmen": 0,
                    "combat": m_obj.get("combat"),
                    "combatText": sf_reskin(str(m_obj.get("combatText") or "")) if m_obj.get("combatText") else None,
                    "sell": m_obj.get("fencedSell") if (isinstance(m_obj.get("fencedSell"), list) and len(m_obj["fencedSell"]) >= 5) else [60, 50, 40, 30, 20],
                    "buy": [0, 0, 0, 0, 0],
                }
                rgc.render(
                    cargo_card,
                    os.path.join(MOCKUPS_DIR, tpl_name),
                    os.path.join(CARDS_DIR, "goods", f"mcargo_{cid}.jpg"),
                )
    print(f"Rendered {enc_count} Encounter cards.")


if __name__ == "__main__":
    main()
