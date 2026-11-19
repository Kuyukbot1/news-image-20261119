#!/usr/bin/env python3
"""Draw the news-image-20261119 front page: one 1024x1024 PNG.

Thursday 19 November 2026: 42 stories, 6 continents, one front page and a map.
All stories come from RESEARCH_19NOV.md (verified 19 Nov 2026). Nothing invented.
Deterministic: no randomness, no time, fixed PNG settings.
Layout engine adapted from the 18 Nov entry; all 13 illustrations are new,
drawn for today's stories.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (247, 241, 227)      # cream paper
INK = (26, 26, 26)
NAVY = (20, 36, 61)
GOLD = (201, 162, 39)
RED = (179, 35, 42)
BLUE = (31, 78, 121)
ORANGE = (180, 90, 27)
GREEN = (46, 125, 50)
PURPLE = (106, 61, 154)
TEAL = (15, 118, 110)
GREY = (107, 114, 128)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    """Wrap text to fit max_w; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(d, text, path, max_size, max_w, min_size=8):
    """Largest font size (<= max_size) at which text fits max_w."""
    size = max_size
    while size > min_size:
        f = font(path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, min_size)


def kicker_color(region):
    return {
        "AMERICAS": RED, "UNITED STATES": RED, "EUROPE": BLUE,
        "MIDDLE EAST": ORANGE, "AFRICA": GREEN, "ASIA": PURPLE,
        "OCEANIA": TEAL, "GLOBAL": GREY, "VATICAN": BLUE,
    }[region]


# ---------------------------------------------------------------- data
# (region, topic, headline, deck) -- all from RESEARCH_19NOV.md
FEATURES = [
    ("ASIA", "DIPLOMACY",
     "Trump, Xi and Putin meet in Shenzhen today",
     "First-ever trilateral summit; Xi opened APEC with the three in a family photo."),
    ("MIDDLE EAST", "IRAN WAR",
     "Iran says three tankers hit mines in Hormuz",
     "Tehran says the ships caught fire in a restricted zone; the claim is unverified."),
    ("GLOBAL", "TECH",
     "GTA VI launches worldwide after 13-year wait",
     "Midnight release on PS5 and Xbox; Metacritic 99 from 140-plus reviews."),
    ("GLOBAL", "MARKETS",
     "Anthropic prices record $83 IPO; debuts today",
     "Biggest IPO ever at about $68.5bn; shares trade on Nasdaq as ANT."),
    ("GLOBAL", "JUSTICE",
     "World Court rules today on Rohingya genocide",
     "ICJ reads its judgment in Gambia v Myanmar; a first state verdict is possible."),
    ("UNITED STATES", "CULTURE",
     "Van Gogh sells for record $190.4m in New York",
     "\u2018Chestnut Trees in Blossom\u2019 tops the artist\u2019s record after a Nazi-era deal."),
    ("ASIA", "WEATHER",
     "Cyclone Akvan bears down on India\u2019s east coast",
     "Heavy rain forecast in Andhra Pradesh and Odisha; landfall expected Friday."),
    ("AMERICAS", "DIPLOMACY",
     "Hegseth\u2019s surprise trip: US\u2013Venezuela defence pact",
     "Deal re-establishes military ties; Hegseth then flies on to Colombia."),
    ("UNITED STATES", "POLITICS",
     "Jeffries nominated as first Black House Speaker",
     "House Democrats pick Hakeem Jeffries to lead the next Congress."),
    ("MIDDLE EAST", "GAZA",
     "Israeli tanks cross Gaza ceasefire line",
     "Rare ground operation beyond the Yellow Line, Israel\u2019s military says."),
    ("EUROPE", "SPORT",
     "Scotland lose in Greece but stay a win from Cup",
     "Greece win 3\u20132; Denmark\u2019s draw with Belarus keeps Scotland\u2019s dream alive."),
    ("ASIA", "QUAKE",
     "M5.7 quake strikes Kumamoto in Japan",
     "Tremor shakes western Kyushu on Thursday morning."),
    ("GLOBAL", "SCIENCE",
     "Voyager 1 passes one light-day from Earth",
     "NASA\u2019s farthest probe hits the milestone 48 years after launch."),
]

# (number, country, text) -- all from RESEARCH_19NOV.md
ALSO_ON = [
    (14, "US", "military rejects claims troops hurt in Iran attacks"),
    (15, "Yemen", "Saudi-led coalition hits Houthi site in Saada"),
    (16, "US", "State Dept reissues warnings for Bahrain, Saudi"),
    (17, "Russia", "alleged agent arrested over Palantir spying"),
    (18, "Ukraine", "says it hit two Russian refineries"),
    (19, "Russia", "Crimean Bridge attacked again, official says"),
    (20, "US", "Illinois man indicted over temple shooting plot"),
    (21, "US", "Pakistani jailed 27 years for Trump plot"),
    (22, "US", "Nvidia falls ~3% as earnings rally fizzles"),
    (23, "US", "Fed minutes point to possible rate rises"),
    (24, "UK", "William and Kate meet Modi as India tour ends"),
    (25, "India", "India, Canada eye defence pact for Dec visit"),
    (26, "India", "Congress demands white paper on prices"),
    (27, "Bangladesh", "paramilitary deployed over Hasina return"),
    (28, "Japan", "Takaichi\u2019s cool welcome; Trump call due"),
    (29, "Honduras", "four attacks kill 12, incl councilwoman"),
    (30, "Haiti", "Haiti, El Salvador sign security deal"),
    (31, "Colombia", "Hegseth lands after Venezuela visit"),
    (32, "France", "three women jailed for joining ISIS"),
    (33, "Europe", "climate pressures hit wine output again"),
    (34, "COP31", "new drafts due as ministers push for deal"),
    (35, "Africa", "WHO: Ebola still expanding, 400\u2013500 a week"),
    (36, "Australia", "red crabs begin march on Christmas Is."),
    (37, "Saudi Arabia", "condemns Iran attacks on Gulf states"),
    (38, "Ukraine", "urges Xi, Trump to pressure Putin"),
    (39, "Russia", "Putin slams sanctions ahead of summit"),
    (40, "Global", "Islam to pass Christianity by 2035: Pew"),
    (41, "UK", "Prince Harry sees \u2018big separation\u2019 on Ukraine"),
    (42, "US", "ageing grid, AI fixes behind outages wave"),
]

# map pins: (lon, lat) per feature number, nudged where the cluster is tight
PINS = {
    1: (114, 22.5), 2: (56.5, 26.9), 3: (-80, 28), 4: (-122, 37.8),
    5: (8, 54), 6: (2.35, 48.9), 7: (85, 17), 8: (-67, 10.5),
    9: (-77, 38.9), 10: (34.5, 31.4), 11: (23.7, 38), 12: (130.7, 32.8),
    13: (149, -35.4),  # 5 nudged east of The Hague; 13 = Canberra DSN station
}
PIN_REGION = {1: "ASIA", 2: "MIDDLE EAST", 3: "GLOBAL", 4: "GLOBAL",
              5: "GLOBAL", 6: "EUROPE", 7: "ASIA", 8: "AMERICAS",
              9: "AMERICAS", 10: "MIDDLE EAST", 11: "EUROPE",
              12: "ASIA", 13: "GLOBAL"}

# rough flat continents, (lon, lat) polygons
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-115, 72), (-100, 73), (-90, 74),
     (-82, 70), (-78, 62), (-68, 58), (-60, 55), (-55, 47), (-60, 44),
     (-68, 44), (-75, 38), (-76, 34), (-80, 32), (-81, 26), (-84, 30),
     (-90, 21), (-86, 16), (-92, 15), (-97, 16), (-105, 20), (-110, 23),
     (-115, 29), (-122, 37), (-124, 42), (-125, 49), (-132, 56), (-140, 60),
     (-155, 58), (-162, 58), (-168, 66)],
    # Greenland
    [(-55, 60), (-45, 60), (-38, 64), (-30, 68), (-22, 70), (-25, 76),
     (-38, 80), (-52, 78), (-58, 74), (-60, 68)],
    # South America
    [(-80, 10), (-77, 4), (-72, 11), (-64, 10), (-58, 8), (-52, 5),
     (-44, -2), (-35, -6), (-38, -12), (-41, -20), (-48, -26), (-54, -33),
     (-58, -38), (-65, -42), (-68, -50), (-70, -54), (-73, -46), (-73, -36),
     (-71, -28), (-70, -18), (-77, -12), (-80, -4), (-81, 2)],
    # Africa
    [(-17, 15), (-13, 27), (-6, 35), (3, 37), (10, 37), (19, 32),
     (25, 32), (32, 31), (35, 28), (39, 21), (43, 12), (48, 11),
     (51, 11), (46, 4), (41, -2), (40, -8), (36, -16), (33, -24),
     (28, -32), (20, -35), (17, -31), (14, -22), (12, -15), (9, -2),
     (9, 4), (2, 6), (-6, 5), (-13, 8), (-17, 15)],
    # Asia (drawn before Europe so Europe overlaps it)
    [(30, 70), (45, 68), (55, 69), (68, 70), (75, 72), (85, 73),
     (95, 75), (105, 76), (115, 74), (125, 72), (135, 72), (145, 72),
     (155, 70), (160, 66), (162, 60), (158, 52), (150, 59), (142, 55),
     (141, 46), (135, 43), (130, 38), (127, 39), (124, 40), (122, 37),
     (120, 32), (118, 25), (113, 22), (108, 18), (105, 10), (101, 8),
     (98, 14), (96, 16), (93, 21), (90, 22), (87, 21), (83, 18),
     (80, 13), (77, 8), (75, 12), (72, 20), (69, 22), (66, 25),
     (62, 25), (58, 26), (54, 26), (51, 28), (48, 30), (45, 29),
     (42, 31), (39, 33), (36, 36), (33, 36), (30, 40), (28, 45),
     (30, 52), (33, 58), (30, 65), (30, 70)],
    # Europe
    [(-10, 36), (-9, 43), (-3, 48), (-5, 50), (0, 52), (3, 54),
     (7, 57), (10, 59), (6, 60), (10, 62), (14, 66), (18, 69),
     (24, 71), (30, 70), (34, 68), (40, 67), (44, 66), (45, 60),
     (41, 56), (38, 52), (35, 50), (32, 46), (29, 45), (28, 42),
     (24, 40), (22, 38), (19, 40), (16, 38), (13, 44), (10, 44),
     (7, 44), (3, 42), (0, 38), (-3, 37), (-7, 37)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (119, -34), (124, -33), (129, -32),
     (133, -32), (136, -35), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (150, -23), (146, -19), (142, -15), (142, -11), (137, -12),
     (135, -15), (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]

# ---------------------------------------------------------------- helpers
def chip(d, x, y, text, bg, fg=(255, 255, 255), size=11, pad=5):
    f = font(SANS_B, size)
    w = d.textlength(text, font=f) + pad * 2
    d.rounded_rectangle([x, y, x + w, y + size + pad], radius=3, fill=bg)
    d.text((x + pad, y + 2), text, font=f, fill=fg)
    return w


def flag_us(d, x, y, w, h):
    for i in range(13):
        d.rectangle([x, y + i * h / 13, x + w, y + (i + 1) * h / 13],
                    fill=RED if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x, y, x + w * 0.4, y + h * 7 / 13], fill=NAVY)
    for r in range(3):
        for c in range(4):
            d.ellipse([x + 3 + c * w * 0.09, y + 2 + r * h * 0.18,
                       x + 6 + c * w * 0.09, y + 5 + r * h * 0.18],
                      fill=(255, 255, 255))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy = x + w * 0.2, y + h * 0.28
    d.polygon([(cx, cy - 5), (cx + 2, cy - 1), (cx + 6, cy - 1), (cx + 3, cy + 2),
               (cx + 4, cy + 6), (cx, cy + 3), (cx - 4, cy + 6), (cx - 3, cy + 2),
               (cx - 6, cy - 1), (cx - 2, cy - 1)], fill=(255, 222, 0))


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 43, 30))


def flag_ve(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(252, 209, 22))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 47, 167))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(206, 17, 38))
    for i in range(4):
        sx = x + w * (0.22 + i * 0.19)
        d.ellipse([sx - 2, y + h / 2 - 2, sx + 2, y + h / 2 + 2],
                  fill=(255, 255, 255))


def flagpole(d, x, y, h, flagfn, fw=34, fh=22):
    d.line([x, y, x, y - h], fill=(90, 80, 70), width=3)
    d.ellipse([x - 2, y - h - 3, x + 2, y - h + 1], fill=GOLD)
    flagfn(d, x + 2, y - h + 2, fw, fh)


def person(d, x, y, s, suit, skin=(232, 190, 150), hair=(40, 30, 25)):
    d.ellipse([x - s * 0.32, y - s * 1.05, x + s * 0.32, y - s * 0.42],
              fill=skin)
    d.pieslice([x - s * 0.32, y - s * 1.08, x + s * 0.32, y - s * 0.55],
               180, 360, fill=hair)
    d.polygon([(x - s * 0.5, y), (x + s * 0.5, y), (x + s * 0.42, y - s * 0.45),
               (x - s * 0.42, y - s * 0.45)], fill=suit)
    d.polygon([(x - s * 0.08, y - s * 0.42), (x + s * 0.08, y - s * 0.42),
               (x, y - s * 0.1)], fill=(255, 255, 255))


def starburst(d, cx, cy, r, color):
    pts = []
    for i in range(16):
        ang = i * math.pi / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color)


def mine(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 40, 45))
    for i in range(8):
        ang = i * math.pi / 4
        x2 = cx + (r + 4) * math.cos(ang)
        y2 = cy + (r + 4) * math.sin(ang)
        d.line([cx, cy, x2, y2], fill=(40, 40, 45), width=2)
    d.ellipse([cx - r * 0.4, cy - r * 0.4, cx + r * 0.4, cy + r * 0.4],
              fill=(90, 90, 100))

# ---------------------------------------------------------------- illustrations
def ill_1(d, x0, y0, x1, y1):
    """Trilateral summit: three flags over a round table, three leaders."""
    d.rectangle([x0, y0, x1, y1], fill=(226, 232, 240))
    # back wall panel
    d.rectangle([x0, y0, x1, y0 + 46], fill=(30, 48, 78))
    fap = font(SANS_B, 11)
    atxt = "APEC \u00b7 SHENZHEN"
    d.text((x0 + (x1 - x0 - d.textlength(atxt, font=fap)) / 2, y0 + 16),
           atxt, font=fap, fill=GOLD)
    # three flags on poles
    for i, fn in enumerate([flag_us, flag_cn, flag_ru]):
        fx = x0 + 52 + i * 108
        flagpole(d, fx, y0 + 82, 40, fn, 44, 28)
    # round table
    d.ellipse([x0 + 60, y0 + 82, x1 - 60, y0 + 106], fill=(120, 82, 50))
    d.ellipse([x0 + 60, y0 + 78, x1 - 60, y0 + 98], fill=(150, 105, 65))
    # three figures seated behind the table
    person(d, x0 + 96, y0 + 80, 22, (30, 40, 60))
    person(d, x0 + 160, y0 + 80, 22, (140, 30, 30))
    person(d, x0 + 224, y0 + 80, 22, (40, 60, 90))
    # name plates on the table
    for i, (tx, col) in enumerate([("USA", NAVY), ("CHINA", RED), ("RUSSIA", BLUE)]):
        px = x0 + 78 + i * 64
        d.rectangle([px, y0 + 92, px + 34, y0 + 102], fill=(255, 255, 255))
        f = font(SANS_B, 7)
        d.text((px + 3, y0 + 93), tx, font=f, fill=col)
    chip(d, x0 + 8, y1 - 20, "FIRST-EVER TRILATERAL", NAVY, size=10)


def ill_2(d, x0, y0, x1, y1):
    """Three tankers hit mines east of Hormuz; flames and smoke."""
    d.rectangle([x0, y0, x1, y0 + 34], fill=(188, 214, 232))
    d.ellipse([x0 + 250, y0 + 6, x0 + 288, y0 + 24], fill=(255, 255, 255))
    d.rectangle([x0, y0 + 34, x1, y1], fill=(96, 150, 195))
    for i in range(6):
        d.arc([x0 + 8 + i * 52, y0 + 60, x0 + 46 + i * 52, y0 + 78],
              200, 340, fill=(210, 232, 245), width=2)
    # three tankers, staggered
    def tanker(tx, ty, w, col):
        d.polygon([(tx, ty), (tx + w, ty), (tx + w - 8, ty + 14), (tx + 8, ty + 14)],
                  fill=col)
        d.rectangle([tx + w * 0.25, ty - 12, tx + w * 0.55, ty], fill=(230, 230, 230))
        d.rectangle([tx + w * 0.6, ty - 8, tx + w * 0.68, ty], fill=(60, 60, 60))
    tanker(x0 + 20, y0 + 52, 96, (120, 40, 40))
    tanker(x0 + 140, y0 + 70, 88, (40, 60, 90))
    tanker(x0 + 220, y0 + 46, 80, (90, 90, 90))
    # flames on each tanker
    starburst(d, x0 + 62, y0 + 44, 12, (255, 170, 0))
    starburst(d, x0 + 62, y0 + 44, 6, (255, 230, 120))
    starburst(d, x0 + 184, y0 + 62, 11, (255, 170, 0))
    starburst(d, x0 + 258, y0 + 38, 10, (255, 170, 0))
    # smoke
    for sx, sy in [(62, 30), (184, 48), (258, 24)]:
        d.ellipse([x0 + sx - 8, y0 + sy - 4, x0 + sx + 8, y0 + sy + 6],
                  fill=(120, 120, 120))
    # mines in the water
    mine(d, x0 + 120, y0 + 100, 7)
    mine(d, x0 + 210, y0 + 106, 6)
    mine(d, x0 + 285, y0 + 96, 6)
    chip(d, x0 + 8, y0 + 6, "EAST OF HORMUZ", NAVY, size=10)
    chip(d, x0 + 200, y1 - 20, "CLAIM UNVERIFIED", (180, 90, 27), size=10)


def ill_3(d, x0, y0, x1, y1):
    """GTA VI: Vice City sunset, palms, neon VI, game case."""
    # sunset bands
    d.rectangle([x0, y0, x1, y0 + 40], fill=(255, 140, 90))
    d.rectangle([x0, y0 + 40, x1, y0 + 66], fill=(255, 90, 130))
    d.rectangle([x0, y0 + 66, x1, y0 + 90], fill=(120, 60, 160))
    d.ellipse([x0 + 250, y0 + 12, x0 + 290, y0 + 52], fill=(255, 220, 130))
    # skyline
    for bx, bw, bh in [(10, 34, 42), (50, 26, 58), (82, 40, 34), (200, 30, 48),
                       (236, 36, 30), (278, 30, 56)]:
        d.rectangle([x0 + bx, y1 - bh - 28, x0 + bx + bw, y1 - 28],
                    fill=(30, 20, 50))
        for wy in range(2):
            for wx in range(2):
                d.rectangle([x0 + bx + 5 + wx * 12, y1 - bh - 20 + wy * 12,
                             x0 + bx + 9 + wx * 12, y1 - bh - 16 + wy * 12],
                            fill=(255, 220, 120))
    # street
    d.rectangle([x0, y1 - 28, x1, y1], fill=(25, 18, 40))
    d.line([x0, y1 - 14, x1, y1 - 14], fill=(255, 255, 255), width=2)
    # palm trees
    def palm(px, py, s):
        d.line([px, py, px + 3, py - s], fill=(90, 60, 30), width=3)
        for ang in [-70, -35, 0, 35, 70]:
            ex = px + 3 + s * 0.55 * math.cos(math.radians(ang - 90))
            ey = py - s + s * 0.45 * math.sin(math.radians(ang - 90))
            d.line([px + 3, py - s, ex, ey], fill=(30, 140, 70), width=3)
    palm(x0 + 132, y1 - 28, 26)
    palm(x0 + 180, y1 - 28, 20)
    # neon VI
    f = font(SERIF_B, 46)
    d.text((x0 + 128, y0 + 6), "VI", font=f, fill=(0, 230, 255))
    d.text((x0 + 126, y0 + 4), "VI", font=f, fill=(255, 0, 200))
    chip(d, x0 + 8, y0 + 6, "PS5 \u00b7 XBOX", (25, 18, 40), size=10)
    chip(d, x0 + 8, y1 - 20, "METACRITIC 99", (255, 0, 200), size=10)


def ill_4(d, x0, y0, x1, y1):
    """Anthropic IPO: dark board, rocketing chart, $83 and ANT."""
    d.rectangle([x0, y0, x1, y1], fill=(14, 22, 32))
    # grid
    for gy in range(4):
        d.line([x0 + 8, y0 + 14 + gy * 18, x1 - 8, y0 + 14 + gy * 18],
               fill=(40, 55, 75), width=1)
    # rocketing green line
    d.line([(x0 + 12, y0 + 62), (x0 + 50, y0 + 56), (x0 + 88, y0 + 48),
            (x0 + 126, y0 + 30), (x0 + 168, y0 + 12)], fill=(80, 220, 120),
           width=3)
    d.polygon([(x0 + 168, y0 + 12), (x0 + 156, y0 + 10), (x0 + 166, y0 + 24)],
              fill=(80, 220, 120))
    # bars
    for i, hgt in enumerate([8, 14, 20, 30]):
        d.rectangle([x0 + 20 + i * 14, y0 + 78 - hgt, x0 + 30 + i * 14, y0 + 78],
                    fill=(60, 120, 180))
    f = font(SANS_B, 20)
    d.text((x0 + 100, y0 + 50), "$83", font=f, fill=(255, 255, 255))
    f2 = font(SANS_B, 11)
    d.text((x0 + 100, y0 + 72), "$68.5bn", font=f2, fill=(80, 220, 120))
    chip(d, x0 + 8, y0 + 6, "ANT \u00b7 NASDAQ", (200, 120, 30), size=10)


def ill_5(d, x0, y0, x1, y1):
    """ICJ at The Hague: Peace Palace, scales of justice."""
    d.rectangle([x0, y0, x1, y1], fill=(222, 228, 236))
    # Peace Palace: main block + tower
    d.rectangle([x0 + 30, y0 + 34, x0 + 120, y0 + 76], fill=(200, 180, 140))
    d.polygon([(x0 + 30, y0 + 34), (x0 + 75, y0 + 18), (x0 + 120, y0 + 34)],
              fill=(160, 130, 95))
    d.rectangle([x0 + 128, y0 + 14, x0 + 148, y0 + 76], fill=(190, 165, 125))
    d.polygon([(x0 + 126, y0 + 14), (x0 + 138, y0 + 2), (x0 + 150, y0 + 14)],
              fill=(150, 120, 85))
    for i in range(4):
        d.rectangle([x0 + 40 + i * 20, y0 + 48, x0 + 52 + i * 20, y0 + 66],
                    fill=(90, 110, 140))
    d.rectangle([x0 + 68, y0 + 58, x0 + 82, y0 + 76], fill=(90, 70, 50))
    # scales of justice, right
    sx, sy = x0 + 168, y0 + 30
    d.line([sx, sy, sx, sy + 40], fill=GOLD, width=3)
    d.line([sx - 14, sy + 4, sx + 14, sy + 4], fill=GOLD, width=3)
    d.polygon([(sx - 20, sy + 20), (sx - 8, sy + 20), (sx - 14, sy + 10)],
              fill=GOLD)
    d.polygon([(sx + 8, sy + 20), (sx + 20, sy + 20), (sx + 14, sy + 10)],
              fill=GOLD)
    d.ellipse([sx - 3, sy - 4, sx + 3, sy + 2], fill=GOLD)
    # ground
    d.rectangle([x0, y0 + 76, x1, y1], fill=(170, 185, 165))
    chip(d, x0 + 8, y0 + 6, "THE HAGUE", NAVY, size=10)
    chip(d, x0 + 70, y1 - 20, "GAMBIA v MYANMAR", (31, 78, 121), size=9)


def ill_6(d, x0, y0, x1, y1):
    """Van Gogh: easel with a blossoming chestnut tree painting."""
    d.rectangle([x0, y0, x1, y1], fill=(232, 226, 210))
    # easel legs
    d.line([x0 + 60, y0 + 14, x0 + 48, y0 + 84], fill=(120, 90, 60), width=4)
    d.line([x0 + 130, y0 + 14, x0 + 142, y0 + 84], fill=(120, 90, 60), width=4)
    d.line([x0 + 60, y0 + 14, x0 + 130, y0 + 14], fill=(120, 90, 60), width=3)
    # canvas
    d.rectangle([x0 + 52, y0 + 16, x0 + 138, y0 + 74], fill=(255, 255, 255),
                outline=(90, 70, 40), width=2)
    # sky + blossom tree on the canvas
    d.rectangle([x0 + 55, y0 + 19, x0 + 135, y0 + 48], fill=(140, 190, 230))
    d.line([x0 + 95, y0 + 48, x0 + 95, y0 + 71], fill=(90, 60, 30), width=4)
    for bx, by, r in [(76, 32, 10), (95, 26, 12), (114, 32, 10), (86, 40, 9),
                      (105, 40, 9)]:
        d.ellipse([x0 + bx - r, y0 + by - r, x0 + bx + r, y0 + by + r],
                  fill=(90, 160, 80))
        d.ellipse([x0 + bx - r + 3, y0 + by - r + 3, x0 + bx + r - 2,
                   y0 + by + r - 2], fill=(255, 255, 255))
    # grass
    d.rectangle([x0 + 55, y0 + 62, x0 + 135, y0 + 71], fill=(120, 170, 90))
    # price tag
    d.polygon([(x0 + 140, y0 + 58), (x0 + 176, y0 + 58), (x0 + 182, y0 + 68),
               (x0 + 176, y0 + 78), (x0 + 140, y0 + 78)], fill=RED)
    f = font(SANS_B, 9)
    d.text((x0 + 143, y0 + 64), "$190.4m", font=f, fill=(255, 255, 255))
    chip(d, x0 + 8, y0 + 6, "SOTHEBY\u2019S", NAVY, size=10)


def ill_7(d, x0, y0, x1, y1):
    """Cyclone Akvan: spiral over the Bay of Bengal, track arrow."""
    d.rectangle([x0, y0, x1, y1], fill=(150, 190, 220))
    # India coast, right
    d.polygon([(x0 + 150, y0), (x1, y0), (x1, y1), (x0 + 168, y1),
               (x0 + 158, y0 + 50), (x0 + 148, y0 + 22)], fill=(214, 190, 140))
    # spiral bands
    cx, cy = x0 + 78, y0 + 42
    for r, col in [(36, (255, 255, 255)), (28, (220, 235, 245)),
                   (20, (255, 255, 255)), (12, (220, 235, 245))]:
        d.arc([cx - r, cy - r, cx + r, cy + r], 30, 310, fill=col, width=6)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 255, 255))
    # storm track arrow toward the coast
    d.line([(cx + 30, cy + 20), (x0 + 138, y0 + 58)], fill=RED, width=3)
    d.polygon([(x0 + 138, y0 + 58), (x0 + 126, y0 + 52), (x0 + 130, y0 + 64)],
              fill=RED)
    # rain streaks
    for i in range(5):
        d.line([x0 + 14 + i * 12, y0 + 68, x0 + 10 + i * 12, y0 + 80],
               fill=(90, 130, 170), width=2)
    chip(d, x0 + 8, y0 + 6, "BAY OF BENGAL", NAVY, size=10)
    chip(d, x0 + 92, y1 - 20, "LANDFALL FRI", (180, 90, 27), size=10)


def ill_8(d, x0, y0, x1, y1):
    """US–Venezuela pact: two flags, signed document, handshake."""
    d.rectangle([x0, y0, x1, y1], fill=(226, 232, 226))
    flagpole(d, x0 + 34, y0 + 62, 38, flag_us, 40, 26)
    flagpole(d, x0 + 140, y0 + 62, 38, flag_ve, 40, 26)
    # signed document between the flags
    d.rectangle([x0 + 82, y0 + 26, x0 + 122, y0 + 58], fill=(255, 255, 255),
                outline=INK)
    for i in range(3):
        d.line([x0 + 87, y0 + 31 + i * 5, x0 + 117, y0 + 31 + i * 5],
               fill=(120, 120, 120), width=1)
    d.ellipse([x0 + 106, y0 + 46, x0 + 116, y0 + 56], fill=RED,
              outline=GOLD, width=1)
    # handshake figures
    person(d, x0 + 62, y0 + 78, 14, (30, 40, 60))
    person(d, x0 + 130, y0 + 78, 14, (120, 30, 30))
    d.line([x0 + 68, y0 + 66, x0 + 124, y0 + 66], fill=(232, 190, 150), width=3)
    d.rectangle([x0, y0 + 80, x1, y1], fill=(200, 180, 140))
    chip(d, x0 + 8, y0 + 6, "CARACAS", NAVY, size=10)
    chip(d, x0 + 106, y1 - 20, "DEFENCE PACT", (179, 35, 42), size=9)


def ill_9(d, x0, y0, x1, y1):
    """Jeffries: US Capitol dome and a speaker's podium."""
    d.rectangle([x0, y0, x1, y1], fill=(214, 226, 240))
    # Capitol dome
    d.pieslice([x0 + 66, y0 + 6, x0 + 126, y0 + 52], 180, 360,
               fill=(230, 230, 225))
    d.rectangle([x0 + 92, y0 + 0, x0 + 100, y0 + 10], fill=(230, 230, 225))
    d.ellipse([x0 + 93, y0 - 4, x0 + 99, y0 + 2], fill=GOLD)
    d.rectangle([x0 + 56, y0 + 46, x0 + 136, y0 + 56], fill=(220, 220, 215))
    for i in range(5):
        d.rectangle([x0 + 62 + i * 14, y0 + 56, x0 + 68 + i * 14, y0 + 72],
                    fill=(200, 200, 195))
    # wings
    d.rectangle([x0 + 14, y0 + 52, x0 + 56, y0 + 72], fill=(210, 210, 205))
    d.rectangle([x0 + 136, y0 + 52, x0 + 178, y0 + 72], fill=(210, 210, 205))
    # podium with figure
    d.rectangle([x0 + 82, y0 + 66, x0 + 110, y0 + 86], fill=(90, 60, 35))
    person(d, x0 + 96, y0 + 66, 14, (30, 40, 60))
    chip(d, x0 + 8, y0 + 6, "WASHINGTON", NAVY, size=10)
    chip(d, x0 + 118, y1 - 20, "SPEAKER", RED, size=10)


def ill_10(d, x0, y0, x1, y1):
    """Gaza: a tank crosses the yellow ceasefire line; tents behind."""
    d.rectangle([x0, y0, x1, y1], fill=(214, 200, 170))
    # sky strip
    d.rectangle([x0, y0, x1, y0 + 22], fill=(220, 210, 190))
    # tents, left
    for i, tx in enumerate([14, 44]):
        d.polygon([(x0 + tx, y0 + 46), (x0 + tx + 13, y0 + 26),
                   (x0 + tx + 26, y0 + 46)],
                  fill=(240, 235, 220) if i == 0 else (220, 210, 190),
                  outline=(120, 110, 90))
    # damaged building, right
    d.rectangle([x0 + 150, y0 + 12, x0 + 182, y0 + 46], fill=(160, 140, 110))
    d.polygon([(x0 + 150, y0 + 12), (x0 + 166, y0 + 4), (x0 + 182, y0 + 12)],
              fill=(120, 100, 75))
    # yellow line across the ground
    d.rectangle([x0, y0 + 56, x1, y0 + 60], fill=(240, 200, 0))
    # tank crossing the line
    d.rectangle([x0 + 66, y0 + 48, x0 + 128, y0 + 66], fill=(90, 100, 70))
    d.rectangle([x0 + 82, y0 + 38, x0 + 112, y0 + 48], fill=(70, 80, 55))
    d.line([x0 + 112, y0 + 42, x0 + 140, y0 + 40], fill=(70, 80, 55), width=4)
    for wx in range(5):
        d.ellipse([x0 + 72 + wx * 11, y0 + 64, x0 + 80 + wx * 11, y0 + 72],
                  fill=(50, 55, 40))
    # ground
    d.rectangle([x0, y0 + 72, x1, y1], fill=(180, 160, 120))
    chip(d, x0 + 8, y0 + 6, "BEYOND YELLOW LINE", (180, 90, 27), size=10)


def ill_11(d, x0, y0, x1, y1):
    """World Cup qualifiers: pitch, goal, scoreboard GRE 3-2 SCO."""
    d.rectangle([x0, y0, x1, y1], fill=(90, 160, 80))
    d.rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], outline=(255, 255, 255), width=2)
    d.line([x0 + (x1 - x0) // 2, y0 + 8, x0 + (x1 - x0) // 2, y1 - 8],
           fill=(255, 255, 255), width=2)
    d.ellipse([x0 + 78, y0 + 30, x0 + 112, y0 + 56], outline=(255, 255, 255),
              width=2)
    # goal, left
    d.rectangle([x0 + 14, y0 + 26, x0 + 26, y0 + 50], outline=(255, 255, 255),
                width=2)
    # ball in the net
    d.ellipse([x0 + 16, y0 + 38, x0 + 26, y0 + 48], fill=(255, 255, 255),
              outline=INK)
    # players
    person(d, x0 + 70, y0 + 66, 14, (0, 60, 160))
    person(d, x0 + 130, y0 + 66, 14, (255, 255, 255))
    # scoreboard
    f = font(SANS_B, 10)
    d.rectangle([x0 + 104, y0 + 8, x1 - 6, y0 + 26], fill=NAVY)
    d.text((x0 + 108, y0 + 11), "GRE 3\u20132 SCO", font=f, fill=(255, 255, 255))
    d.rectangle([x0 + 104, y0 + 30, x1 - 6, y0 + 48], fill=NAVY)
    d.text((x0 + 108, y0 + 33), "DEN 1\u20131 BLR", font=f, fill=(255, 255, 255))


def ill_12(d, x0, y0, x1, y1):
    """Kumamoto quake: Japan archipelago, red epicentre dot, seismograph."""
    d.rectangle([x0, y0, x1, y1], fill=(226, 232, 236))
    # Japan archipelago (stylised)
    d.polygon([(x0 + 118, y0 + 10), (x0 + 132, y0 + 6), (x0 + 142, y0 + 14),
               (x0 + 136, y0 + 26), (x0 + 124, y0 + 30), (x0 + 116, y0 + 22)],
              fill=(120, 170, 120), outline=(60, 110, 60))
    d.polygon([(x0 + 128, y0 + 30), (x0 + 146, y0 + 28), (x0 + 152, y0 + 38),
               (x0 + 142, y0 + 48), (x0 + 128, y0 + 46), (x0 + 122, y0 + 38)],
              fill=(120, 170, 120), outline=(60, 110, 60))
    d.polygon([(x0 + 138, y0 + 48), (x0 + 152, y0 + 46), (x0 + 158, y0 + 58),
               (x0 + 148, y0 + 68), (x0 + 134, y0 + 64), (x0 + 130, y0 + 54)],
              fill=(120, 170, 120), outline=(60, 110, 60))
    # epicentre: Kumamoto, south-west Kyushu
    d.ellipse([x0 + 130, y0 + 56, x0 + 142, y0 + 68], fill=RED)
    d.ellipse([x0 + 133, y0 + 59, x0 + 139, y0 + 65], fill=(255, 255, 255))
    # radiating rings
    for r in [12, 20]:
        d.ellipse([x0 + 136 - r, y0 + 62 - r, x0 + 136 + r, y0 + 62 + r],
                  outline=RED, width=1)
    # seismograph paper, bottom
    d.rectangle([x0 + 10, y0 + 58, x0 + 118, y0 + 80], fill=(255, 255, 255),
                outline=(150, 150, 150))
    pts = [(x0 + 12, y0 + 69), (x0 + 28, y0 + 69), (x0 + 34, y0 + 62),
           (x0 + 40, y0 + 76), (x0 + 46, y0 + 63), (x0 + 52, y0 + 75),
           (x0 + 58, y0 + 61), (x0 + 66, y0 + 77), (x0 + 74, y0 + 69),
           (x0 + 116, y0 + 69)]
    d.line(pts, fill=RED, width=2)
    chip(d, x0 + 8, y0 + 6, "M5.7", RED, size=12)
    chip(d, x0 + 52, y0 + 6, "KUMAMOTO", NAVY, size=10)


def ill_13(d, x0, y0, x1, y1):
    """Voyager 1: deep space, stars, the probe with its dish."""
    d.rectangle([x0, y0, x1, y1], fill=(10, 14, 30))
    # stars
    for sx, sy, r in [(20, 14, 1), (60, 30, 2), (120, 10, 1), (170, 22, 2),
                      (40, 60, 1), (150, 70, 1), (95, 78, 2), (180, 55, 1),
                      (12, 78, 2), (135, 40, 1)]:
        d.ellipse([x0 + sx - r, y0 + sy - r, x0 + sx + r, y0 + sy + r],
                  fill=(255, 255, 255))
    # faint sun, far left
    d.ellipse([x0 + 6, y0 + 38, x0 + 22, y0 + 54], fill=(255, 220, 120))
    # probe body
    d.rectangle([x0 + 82, y0 + 38, x0 + 118, y0 + 58], fill=(200, 200, 205),
                outline=(150, 150, 155))
    d.rectangle([x0 + 88, y0 + 44, x0 + 100, y0 + 52], fill=GOLD)
    # dish
    d.polygon([(x0 + 118, y0 + 34), (x0 + 146, y0 + 28), (x0 + 146, y0 + 62),
               (x0 + 118, y0 + 58)], fill=(230, 230, 235),
              outline=(170, 170, 175))
    d.line([x0 + 118, y0 + 46, x0 + 146, y0 + 46], fill=(170, 170, 175), width=1)
    # boom + RTG
    d.line([x0 + 82, y0 + 48, x0 + 52, y0 + 48], fill=(180, 180, 185), width=3)
    d.rectangle([x0 + 40, y0 + 42, x0 + 52, y0 + 54], fill=(120, 120, 125))
    # signal waves from the dish
    for r in [8, 16, 24]:
        d.arc([x0 + 146 - r, y0 + 45 - r, x0 + 146 + r, y0 + 45 + r],
              -40, 40, fill=(120, 200, 255), width=2)
    chip(d, x0 + 8, y0 + 6, "1 LIGHT-DAY", (120, 200, 255), size=10)
    chip(d, x0 + 106, y1 - 20, "1977 \u2192 TODAY", (255, 255, 255), size=9,
         fg=NAVY)


ILLUSTRATIONS = {1: ill_1, 2: ill_2, 3: ill_3, 4: ill_4, 5: ill_5, 6: ill_6,
                 7: ill_7, 8: ill_8, 9: ill_9, 10: ill_10, 11: ill_11,
                 12: ill_12, 13: ill_13}

# ---------------------------------------------------------------- page build
def draw_card(d, num, x, y, w, h, large):
    region, topic, headline, deck = FEATURES[num - 1]
    col = kicker_color(region)
    d.rectangle([x, y, x + w, y + h], fill=(255, 252, 244),
                outline=(150, 140, 120), width=1)
    ill_h = 118 if large else 88
    ILLUSTRATIONS[num](d, x + 1, y + 1, x + w - 1, y + 1 + ill_h)
    d.line([x, y + 1 + ill_h, x + w, y + 1 + ill_h], fill=(150, 140, 120), width=1)
    # number circle + kicker
    cx, cy, r = x + 14, y + ill_h + 16, 9
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    fnum = font(SANS_B, 11)
    tw = d.textlength(str(num), font=fnum)
    d.text((cx - tw / 2, cy - 7), str(num), font=fnum, fill=(255, 255, 255))
    fk = font(SANS_B, 11 if large else 9)
    d.text((x + 28, y + ill_h + 9), f"{region} \u00b7 {topic}", font=fk, fill=col)
    # headline, bold serif, 2 lines (shrink font until it fits)
    hs = 20 if large else 14
    while True:
        hf = font(SERIF_B, hs)
        hl = wrap(d, headline, hf, w - 16)
        if len(hl) <= 2 or hs <= 11:
            break
        hs -= 1
    hy = y + ill_h + 28
    for i, line in enumerate(hl[:2]):
        d.text((x + 8, hy + i * (hs + 2)), line, font=hf, fill=INK)
    # deck, 2 lines (shrink font until it fits)
    ds = 12 if large else 10
    while True:
        df = font(SANS, ds)
        dl = wrap(d, deck, df, w - 16)
        if len(dl) <= 2 or ds <= 8:
            break
        ds -= 1
    dy = hy + 2 * (hs + 2) + 2
    for i, line in enumerate(dl[:2]):
        d.text((x + 8, dy + i * (ds + 3)), line, font=df, fill=(60, 55, 45))


def lonlat_to_xy(lon, lat, mx0, my0, mw, mh):
    x = mx0 + (lon + 180) / 360 * mw
    y = my0 + (84 - lat) / 142 * mh
    return x, y


def draw_map(d, mx0, my0, mw, mh):
    d.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=(207, 227, 238),
                outline=(150, 140, 120), width=1)
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, mx0, my0, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=(232, 220, 192), outline=(180, 165, 130))
    # pins, numbered, coloured by continent
    fnum = font(SANS_B, 8)
    for num in range(1, 14):
        lon, lat = PINS[num]
        px, py = lonlat_to_xy(lon, lat, mx0, my0, mw, mh)
        col = kicker_color(PIN_REGION[num])
        r = 7
        d.ellipse([px - r, py - r, px + r, py + r], fill=col,
                  outline=(255, 255, 255), width=1)
        tw = d.textlength(str(num), font=fnum)
        d.text((px - tw / 2, py - 5), str(num), font=fnum, fill=(255, 255, 255))


def draw_legend(d, x, y, w):
    items = [("Americas", RED), ("Europe", BLUE), ("Middle East", ORANGE),
             ("Africa", GREEN), ("Asia", PURPLE), ("Oceania", TEAL),
             ("Global", GREY)]
    f = font(SANS_B, 9)
    cx = x
    for name, col in items:
        d.ellipse([cx, y, cx + 9, y + 9], fill=col)
        d.text((cx + 12, y - 1), name, font=f, fill=INK)
        cx += 12 + d.textlength(name, font=f) + 8
    return cx


ALSO_COLORS = {
    "US": RED, "Yemen": ORANGE, "Russia": BLUE, "Ukraine": BLUE,
    "UK": BLUE, "India": PURPLE, "Bangladesh": PURPLE, "Japan": PURPLE,
    "Honduras": RED, "Haiti": RED, "Colombia": RED, "France": BLUE,
    "Europe": BLUE, "COP31": GREY, "Africa": GREEN, "Australia": TEAL,
    "Saudi Arabia": ORANGE, "Global": GREY,
}


def draw_also_on(d, x0, y0, w, h):
    fnum = font(SANS_B, 8)
    f = font(SANS, 10)
    col_w = (w - 10) // 2
    rows = 15
    rh = h / rows
    for idx, (num, country, text) in enumerate(ALSO_ON):
        col_i = 0 if idx < 15 else 1
        row = idx if idx < 15 else idx - 15
        cx = x0 + col_i * (col_w + 10)
        cy = y0 + row * rh + rh / 2
        col = ALSO_COLORS.get(country, GREY)
        d.ellipse([cx, cy - 6, cx + 12, cy + 6], fill=col)
        tw = d.textlength(str(num), font=fnum)
        d.text((cx + 6 - tw / 2, cy - 5), str(num), font=fnum,
               fill=(255, 255, 255))
        label = f"{country}: {text}"
        d.text((cx + 16, cy - 5), label, font=f, fill=INK)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # outer border
    d.rectangle([4, 4, W - 5, H - 5], outline=NAVY, width=3)

    # ---- masthead: navy band ----
    d.rectangle([8, 8, W - 9, 122], fill=NAVY)
    fk = font(SANS_B, 13)
    d.text((16, 16), "THE DAY IN WORLD NEWS", font=fk, fill=GOLD)
    right = "42 STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM THURSDAY"
    tw = d.textlength(right, font=fk)
    d.text((W - 16 - tw, 16), right, font=fk, fill=(255, 255, 255))
    date_f = fit_font(d, "Thursday 19 November 2026", SERIF_B, 56, W - 40)
    d.text((16, 42), "Thursday 19 November 2026", font=date_f,
           fill=(255, 255, 255))
    d.line([8, 122, W - 9, 122], fill=GOLD, width=3)

    # ---- feature cards ----
    # row 1: 3 large cards
    y1, h1 = 130, 232
    for i in range(3):
        draw_card(d, i + 1, 16 + i * 328, y1, 320, h1, large=True)
    # rows 2-3: 5 small cards each
    for row, base in enumerate([4, 9]):
        y = 370 + row * 190
        for i in range(5):
            draw_card(d, base + i, 16 + i * 200, y, 192, 190, large=False)

    # ---- bottom band ----
    by = 766
    fh = font(SANS_B, 13)
    d.text((16, by), "WHERE IT HAPPENED", font=fh, fill=RED)
    d.line([16, by + 20, 440, by + 20], fill=INK, width=2)
    d.text((452, by), "ALSO ON THURSDAY 19 NOVEMBER", font=fh, fill=RED)
    d.line([452, by + 20, 1008, by + 20], fill=INK, width=2)
    draw_map(d, 16, 792, 424, 166)
    draw_legend(d, 16, 964, 424)
    draw_also_on(d, 452, 792, 556, 196)

    # ---- footer ----
    d.line([16, 988, 1008, 988], fill=INK, width=2)
    ff = font(SANS, 10)
    footer = ("Every story happened or was first reported on Thursday "
              "19 November 2026; disputed claims are attributed. Sources: "
              "AP, Reuters, AFP, BBC, Al Jazeera, UN News. Original drawings.")
    d.text((16, 996), footer, font=ff, fill=(60, 55, 45))

    img.save(OUT, format="PNG", optimize=True)
    return OUT


if __name__ == "__main__":
    path = build()
    print(path, os.path.getsize(path))
