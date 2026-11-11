"""Render Free Parking goods cards: card art + traits & price overlay.

The card art carries a light title banner at the top and a large blank light panel in the
lower half. This script finds both areas automatically, then draws on them:
  - the card name and category in the title banner (over any title baked into the art)
  - a combat-effect line, the SUV space symbols, and the price table in the blank panel

Usage:
  python3 scripts/render_goods_cards.py                       # render the six mock-ups
  python3 scripts/render_goods_cards.py <card_id> <art> <out> # render one card
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = "/System/Library/Fonts/Supplemental"
F_TITLE = os.path.join(FONTS, "DIN Condensed Bold.ttf")
F_BOLD = os.path.join(FONTS, "Arial Bold.ttf")
F_NUM = os.path.join(FONTS, "DIN Alternate Bold.ttf")

CATEGORY_LABEL = {
    "Grain": "WEED", "Marble": "PARTY", "Weapons": "WEAPONS", "Guards": "HENCHMEN",
    "Meat Animals": "PILL UPPERS", "Exotic Animals": "POWDER UPPERS",
    "Cheap Wine": "STREET OPIATES", "Fine Wine": "PHARMA OPIATES",
}
SCARCITY = ["<<", "<", "=", ">", ">>"]
SCARCITY_COLORS = [(31, 122, 31), (31, 160, 60), (190, 170, 20), (214, 90, 40), (150, 20, 40)]
INK = (24, 22, 20)
SELL_GREEN = (22, 110, 40)
BUY_RED = (150, 28, 28)
GRID = (60, 60, 60)
SCARCITY_LABEL = {"Grain": "WEED", "Marble": "PARTY"}


def btc(units):
    """Engine amounts are tenths of a Bitcoin (1 Denarius = 0.1 BTC)."""
    v = round(int(units)) / 10
    return str(int(v)) if v == int(v) else f"{v:.1f}"


def load_cards():
    m = json.load(open(os.path.join(ROOT, "src/data/market_and_missions.json"), encoding="utf-8"))
    return {c["id"]: c for c in m["market"]}


def category_label(card):
    return CATEGORY_LABEL.get(card.get("subcategory"), CATEGORY_LABEL.get(card.get("track"), str(card.get("track", "")).upper()))


def light_rows(gray, y0, y1, x0, x1, thresh=205, frac=0.93):
    rows = []
    w = x1 - x0
    px = gray.load()
    for y in range(y0, y1):
        n = sum(1 for x in range(x0, x1, 2) if px[x, y] >= thresh)
        rows.append(n / (w / 2) >= frac)
    return rows


def longest_run(flags, offset):
    best, cur, start, bstart = 0, 0, 0, 0
    for i, f in enumerate(flags):
        if f:
            if cur == 0:
                start = i
            cur += 1
            if cur > best:
                best, bstart = cur, start
        else:
            cur = 0
    return offset + bstart, offset + bstart + best


def panel_x_bounds(gray, y, thresh=205):
    px = gray.load()
    w = gray.size[0]
    mid = w // 2
    left = mid
    while left > 0 and px[left, y] >= thresh:
        left -= 1
    right = mid
    while right < w - 1 and px[right, y] >= thresh:
        right += 1
    return left + 1, right - 1


def find_zones(img):
    gray = img.convert("L")
    W, H = gray.size
    # Blank price panel: longest light run in the lower 60%
    ys = int(H * 0.40)
    py0, py1 = longest_run(light_rows(gray, ys, H, int(W * 0.25), int(W * 0.75)), ys)
    px0, px1 = panel_x_bounds(gray, (py0 + py1) // 2)
    if px1 < W * 0.85:  # right edge hidden by a border flap: mirror the left margin
        px1 = W - px0
    # Title banner: rows in the top 32% whose left and right margins are both light
    px = gray.load()
    def edge_light(y):
        cols = list(range(int(W * 0.115), int(W * 0.135)))
        return sum(1 for x in cols if px[x, y] >= 140) / len(cols) >= 0.85
    ty0, ty1 = longest_run([edge_light(y) for y in range(0, int(H * 0.32))], 0)
    xm = int(W * 0.125)
    tx0 = xm
    while tx0 > 0 and px[tx0, (ty0 + ty1) // 2] >= 140:
        tx0 -= 1
    tx1 = int(W * 0.875)
    while tx1 < W - 1 and px[tx1, (ty0 + ty1) // 2] >= 190:
        tx1 += 1
    tx0, tx1 = tx0 + 1, tx1 - 1
    if tx1 < W * 0.85:
        tx1 = W - tx0
    return (tx0, ty0, tx1, ty1), (px0, py0, px1, py1)


def fit_font(path, text, max_w, start, min_size=10):
    size = start
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(path, min_size)


def center_text(d, box, text, font, fill):
    x0, y0, x1, y1 = box
    bb = d.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text((x0 + (x1 - x0 - tw) / 2 - bb[0], y0 + (y1 - y0 - th) / 2 - bb[1]), text, font=font, fill=fill)


def draw_title(img, d, zone, card):
    x0, y0, x1, y1 = zone
    fill = tuple(int(v) for v in ImageStat.Stat(img.crop((x0 + 4, y0 + 4, x0 + 24, y1 - 4))).median)
    d.rectangle((x0 + 2, y0 + 2, x1 - 2, y1 - 2), fill=fill)
    h = y1 - y0
    name = card["name"].upper()
    sub = None
    if "(" in name and name.endswith(")"):
        name, sub = name[: name.index("(")].strip(), name[name.index("(") + 1:-1]
    title_font = fit_font(F_TITLE, name, (x1 - x0) * 0.9, int(h * 0.58))
    cat = category_label(card) + (f"  \u2022  {sub}" if sub else "")
    cat_font = fit_font(F_BOLD, cat, (x1 - x0) * 0.9, int(h * 0.17))
    center_text(d, (x0, y0 + h * 0.04, x1, y0 + h * 0.70), name, title_font, INK)
    center_text(d, (x0, y0 + h * 0.68, x1, y1 - h * 0.06), cat, cat_font, (176, 60, 20))


def draw_symbols(d, cx, cy, size, blocks, guards):
    items = [("sq", INK)] * blocks + [("tri", (196, 150, 20))] * guards
    if not items:
        return
    gap = size * 0.45
    total = len(items) * size + (len(items) - 1) * gap
    x = cx - total / 2
    for kind, col in items:
        if kind == "sq":
            d.rectangle((x, cy - size / 2, x + size, cy + size / 2), fill=col)
        else:
            d.polygon([(x, cy + size / 2), (x + size / 2, cy - size / 2), (x + size, cy + size / 2)], fill=col, outline=INK)
        x += size + gap


def draw_panel(d, zone, card):
    x0, y0, x1, y1 = zone
    w, h = x1 - x0, y1 - y0
    pad = w * 0.05
    combat = card.get("combatText")
    if card.get("track") == "Guards" and card.get("bonusBlocks"):
        combat = combat  # already describes the bonus space
    rows_h = h * 0.16
    y = y0 + h * 0.04
    if combat:
        f = fit_font(F_BOLD, combat, w - 2 * pad, int(rows_h * 0.62))
        center_text(d, (x0, y, x1, y + rows_h), combat, f, INK)
    y += rows_h
    draw_symbols(d, (x0 + x1) / 2, y + rows_h * 0.45, rows_h * 0.5, int(card.get("blocks") or 0), int(card.get("guards") or 0))
    y += rows_h
    # Price table
    tx0, tx1 = x0 + pad, x1 - pad
    label_w = (tx1 - tx0) * 0.10
    col_w = (tx1 - tx0 - label_w) / 5
    ty0 = y + h * 0.02
    ty1 = y1 - h * 0.05
    sell, buy = card.get("sell"), card.get("buy")
    rows = [("hdr", None)] + ([("SELL", sell)] if sell else []) + [("HIRE" if card.get("track") == "Guards" else "BUY", buy)]
    rh = (ty1 - ty0) / len(rows)
    d.rectangle((tx0, ty0, tx1, ty1), outline=SELL_GREEN, width=3)
    for ri, (lbl, vals) in enumerate(rows):
        ry0 = ty0 + ri * rh
        if ri:
            d.line((tx0, ry0, tx1, ry0), fill=SELL_GREEN, width=2)
        # label column
        lab_col = SELL_GREEN if lbl == "SELL" else (BUY_RED if lbl in ("BUY", "HIRE") else (230, 230, 225))
        d.rectangle((tx0 + 1, ry0 + 1, tx0 + label_w, ry0 + rh - 1), fill=lab_col)
        if lbl != "hdr":
            lf = ImageFont.truetype(F_BOLD, max(10, int(min(label_w * 0.32, rh * 0.30))))
            txt = Image.new("RGBA", (int(rh), int(label_w)), (0, 0, 0, 0))
            td = ImageDraw.Draw(txt)
            center_text(td, (0, 0, int(rh), int(label_w)), lbl, lf, (255, 255, 255))
            d._image.paste(txt.rotate(90, expand=True), (int(tx0 + 1), int(ry0)), txt.rotate(90, expand=True))
        for ci in range(5):
            cx0 = tx0 + label_w + ci * col_w
            d.line((cx0, ty0, cx0, ty1), fill=SELL_GREEN, width=2)
            box = (cx0, ry0, cx0 + col_w, ry0 + rh)
            if lbl == "hdr":
                f = ImageFont.truetype(F_BOLD, int(rh * 0.55))
                center_text(d, box, SCARCITY[ci], f, SCARCITY_COLORS[ci])
            else:
                v = btc(vals[ci])
                bold = lbl in ("BUY", "HIRE") and ci == 2
                f = fit_font(F_NUM, v, col_w * 0.86, int(rh * (0.70 if bold else 0.60)))
                center_text(d, box, v, f, INK if not bold else (0, 0, 0))


def render(card, art, out):
    img = Image.open(art).convert("RGB")
    title_zone, panel_zone = find_zones(img)
    d = ImageDraw.Draw(img)
    draw_title(img, d, title_zone, card)
    draw_panel(d, panel_zone, card)
    img.save(out)
    return title_zone, panel_zone


MOCKUPS = {
    "grn_?": ("OG Kush (Flower)", "weed_humboldt_indoor.png"),
    "mrb_?": ("Champagne Molly (MDMA Crystal)", "party_pure_mdma_crystal.png"),
    "ea_?": ("Peruvian Flake", "uppers_peruvian_flake.png"),
    "cw_?": ("China White", "opiates_china_white.png"),
    "wpn_?": ("Glock 19", "weapons_glock_19.png"),
    "grd_?": ("Big Mike", "henchmen_big_mike.png"),
}

if __name__ == "__main__":
    cards = load_cards()
    if len(sys.argv) == 4:
        print(render(cards[sys.argv[1]], sys.argv[2], sys.argv[3]))
        sys.exit()
    src = os.path.join(ROOT, "public/assets/fp/mockups")
    dst = os.path.join(src, "rendered")
    os.makedirs(dst, exist_ok=True)
    by_name = {c["name"]: c for c in cards.values()}
    for _, (name, art) in MOCKUPS.items():
        card = by_name[name]
        out = os.path.join(dst, art)
        print(card["id"], name, render(card, os.path.join(src, art), out))
