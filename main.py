#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - a one-page broadsheet of Saturday 21 November 2026.

Renders a 1024x1024 PNG newspaper front page (masthead with the date, a
verified numbers strip, a lead story and 43 further story cards in a
four-column grid) using only the Python standard library, and writes it to
<output>/entry.png where <output> is $MAKEFUN_OUTPUT_DIR or /output.
Fully deterministic: same bytes on every run.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (248, 244, 234)
INK = (22, 20, 18)
RED = (163, 22, 33)
GREY = (96, 90, 80)
LEADBG = (244, 228, 216)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------------------
# 5x7 bitmap font, drawn for this entry. Each glyph is 7 rows of 5 pixels.
# ---------------------------------------------------------------------------
FONT = {
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", ".#.#.", "..#..", ".#.#.", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#...#", "#...#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..#..", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".....", ".##..", ".....", ".....", ".##..", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "€": ("..###", ".#...", "#....", "####.", "#....", ".#...", "..###"),
    "°": (".##..", "#..#.", "#..#.", ".##..", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", ".####", "..#..", "..#..", "....."),
    "&": (".#...", "#.#..", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "£": ("..##.", ".#.#.", ".#...", "####.", ".#...", ".#...", "#####"),
    "·": (".....", ".....", ".....", ".##..", ".....", ".....", "....."),
}

_REPLACE = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "−": "-", "•": "·",
    '"': "'",
}


def normalize(text):
    return "".join(_REPLACE.get(ch, ch) for ch in text)


def text_width(text, scale):
    return len(normalize(text)) * 6 * scale


# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def fill_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        n = len(row)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.px[off:off + n] = row

    def text(self, x, y, text, scale, color, bold=False):
        text = normalize(text)
        off = 1 if scale <= 2 else scale // 2
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if row[c] == "#":
                        self.fill_rect(cx + c * scale, y + r * scale,
                                       scale, scale, color)
                        if bold:
                            self.fill_rect(cx + c * scale + off,
                                           y + r * scale, scale, scale, color)
            cx += 6 * scale
        return cx

    def text_centered(self, cx, y, text, scale, color, bold=False):
        w = text_width(text, scale)
        return self.text(cx - w // 2, y, text, scale, color, bold)

    def text_right(self, xr, y, text, scale, color, bold=False):
        w = text_width(text, scale)
        return self.text(xr - w, y, text, scale, color, bold)


def wrap(text, maxchars):
    lines = []
    cur = ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if len(trial) <= maxchars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def png_bytes(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# The day's news: Saturday 21 November 2026 (verified research file).
# ---------------------------------------------------------------------------
DATE_LINE = "SATURDAY 21 NOVEMBER 2026"

NUMBERS = [
    ("€7.9bn", ["EU AID TO UKRAINE"]),
    ("$120bn", ["ADAPTATION GOAL"]),
    ("-3.7%", ["S&P 500 FRIDAY"]),
    ("235", ["MONTHS FOR GUPTA"]),
    ("306", ["RUNS: INDIA A WIN"]),
    ("62", ["CHEETAHS IN INDIA"]),
    ("310", ["MEDIA PARTNERS"]),
    ("1.8°C", ["OCTOBER VS", "PRE-INDUSTRIAL"]),
]

LEAD_TAG = "LEAD STORY · EUROPE — CONFLICT"
LEAD_HEAD = "RUSSIAN MISSILES AND A JET DRONE COME DOWN IN POLAND"
LEAD_DECK = (
    "Two Kh-101 cruise missiles, another missile and a jet drone fell in "
    "south-east Poland during a huge barrage on Ukraine that killed 8 and "
    "injured 28. NATO chief Mark Rutte is in Warsaw today; Poland seeks more "
    "allied troops and AWACS for Operation Eastern Sentry, and PM Tusk calls "
    "it a deliberate provocation."
)

SECTIONS = [
    ("EUROPE", [
        ("DENMARK CHARGES TWO OVER PLOT TO KILL RAPPER KYIVSTONER",
         "Two men charged over a foiled Russian plot to kill the rapper in "
         "Copenhagen; Denmark expels Russia's attache."),
        ("THREE PARIS OFFICERS SENTENCED OVER ZECLER BEATING",
         "Five years each, part suspended; racism an aggravating factor, a "
         "first; lifetime police ban."),
        ("UK AND EU SEAL FOOD, CARBON AND YOUTH DEALS",
         "Food checks ease from 2028, carbon markets link, youth mobility "
         "opens for 100,000 a year. Burnham: win-win."),
        ("EU SENDS UKRAINE €7.9BN, ITS LARGEST SINGLE PAYMENT",
         "The ninth Facility tranche: €7,859,441,144, over half from the "
         "Support Loan. EU aid since 2022 now totals €245.5bn."),
        ("EU COUNCIL ADDS €1BN MILITARY AID FOR UKRAINE",
         "Approved through the European Peace Facility, on top of the day's "
         "record payment to Kyiv."),
        ("KYIV BURIES BARRAGE VICTIMS AS TOLL REACHES EIGHT",
         "A couple killed in the strike wave are buried; the huge barrage "
         "leaves 8 dead and 28 injured across Ukraine."),
        ("SIX RUGBY TESTS LIGHT UP NATIONS CHAMPIONSHIP SATURDAY",
         "England v New Zealand at Twickenham, Ireland v South Africa in "
         "Dublin, France v Argentina in Paris."),
    ]),
    ("ASIA-PACIFIC", [
        ("ROHINGYA REFUGEES CHEER ICJ GENOCIDE RULING",
         "Cox's Bazar celebrates; Britain expels Myanmar's attache and seeks "
         "an emergency UN Security Council session."),
        ("310 MEDIA HOUSES LAUNCH ASIA-PACIFIC PARTNERSHIP",
         "310 organisations from 41 countries join the Xinhua-led "
         "partnership, an APEC China 2026 deliverable, at Shenzhen."),
        ("CYCLONE AKVAN RELIEF UNDER WAY ON ODISHA COAST",
         "The storm crossed near Gopalpur and weakened; rescues continue "
         "and Odisha's assembly is suspended to 23 Nov."),
        ("INDIA'S NSE PASSES NASDAQ, NOW WORLD'S No.5 EXCHANGE",
         "The National Stock Exchange overtakes Nasdaq and HKEX to rank "
         "fifth among the world's listed exchanges."),
        ("FOUR CHEETAH CUBS TAKE INDIA'S TOTAL TO 62",
         "Born at Kuno to a Botswana-born mother, the cubs lift India's "
         "cheetah population to 62."),
        ("INDIA UNVEILS FIRST HOME-GROWN BIRD-FLU VACCINE",
         "The indigenous H5N1 vaccine is unveiled at Bhopal, a first for "
         "Indian animal-health science."),
        ("NEPAL PM BALENDRA SHAH TO VISIT INDIA 22-23 NOV",
         "The state visit, at PM Modi's invitation, was announced today."),
        ("JAPANESE TROOPS TO TRAIN AT INDIAN FACILITIES",
         "Japan's forces will use Indian facilities for live-fire training, "
         "a first for the two countries."),
        ("INDIA WOMEN BEAT MALAYSIA 4-1 IN HOCKEY OPENER",
         "A 4-1 win in Bhopal opens India's Asian Champions Trophy campaign."),
        ("LAKSHYA SEN TAKES 13-MATCH STREAK INTO HONG KONG SEMIS",
         "Sen beat ex-world champion Loh Kean Yew in three games; today's "
         "Kowloon semi awaits, Tour Finals place sealed."),
        ("SATWIK-CHIRAG REACH HONG KONG OPEN SEMI-FINALS",
         "The Indian pair beat China's Hu Ke Yuan and Lin Xiang Yi in three "
         "games; their semi-final is today."),
        ("INDIA A BOWL NEPAL OUT FOR 26, WIN BY 306 RUNS",
         "Tilak Varma 107, Kumar Kushagra 117; Nepal's 26 is the "
         "fifth-lowest List A total ever, in Doha."),
    ]),
    ("NORTH AMERICA", [
        ("S&P 500 AND DOW ENTER CORRECTION AS AI ROUT DEEPENS",
         "Friday close: S&P -3.7% to 6,910.39, Dow -949.73, Nasdaq -5.28% "
         "and negative for the year."),
        ("NVIDIA FALLS 14% AS CHIP STOCKS LEAD SELLOFF",
         "Down 23% on the week; the Philadelphia semiconductor index fell "
         "10.7% in the rout."),
        ("ANTHROPIC SLIDES 9.1% AFTER HISTORY'S LARGEST IPO",
         "Shares close at $88.30, down a day after the biggest market debut "
         "on record."),
        ("TRUMP THREATENS TAX ON OVERSEAS AI DATA CENTRES",
         "US firms building abroad face a 'tremendous tax', he says, citing "
         "China; joint AI guardrails with Xi teased."),
        ("LA JURY CONVICTS MAN OVER PALISADES FIRE",
         "Rinderknecht, 30, guilty on two arson counts; the fire killed 12 "
         "and destroyed some 6,800 structures."),
        ("235 MONTHS FOR MURDER-FOR-HIRE PLOTTER GUPTA",
         "Nikhil Gupta is sentenced in Manhattan for plotting to kill Sikh "
         "activist Gurpatwant Singh Pannun."),
        ("WHITE HOUSE REPLACES NATIONAL CYBER DIRECTOR",
         "Cairncross out after a week of tech outages; Pentagon CIO Kirsten "
         "Davies steps in, acting."),
        ("BIG BANKS CONFIRM VENDOR DATA BREACHES",
         "JPMorgan, Visa and Mastercard confirm marketing data taken via "
         "vendors; payment systems untouched."),
        ("FORMULA 1 RACES DOWN THE LAS VEGAS STRIP TONIGHT",
         "The Grand Prix runs under lights on Saturday night on the Strip "
         "circuit."),
    ]),
    ("MIDDLE EAST", [
        ("COALITION DOWNS THREE MISSILES FIRED AT RIYADH",
         "Three Houthi ballistic missiles aimed at the Saudi capital are "
         "destroyed, the second attack in days."),
        ("UN WARNS HODEIDAH STRIKES PUT AID LIFELINE AT RISK",
         "The port handles some 70% of Yemen's imports; the UN aid chief "
         "calls the strikes deeply concerning."),
        ("TRUMP DEMANDS A 'REAL DEAL' FROM IRAN",
         "War nears month nine: Tehran wants a deal 'not acceptable to me'; "
         "a strike decision slips to the new year."),
        ("US PRESSES SINGAPORE, MALAYSIA OVER IRAN SANCTIONS",
         "Front companies and Iran Airtour flights targeted; Bessent: no "
         "Iranian crude at sea for buyers."),
        ("COP31 RUNS INTO OVERTIME IN ANTALYA, NO DEAL",
         "Draft drops fossil fuels and the $120bn adaptation goal; "
         "activists protest. COP32: Addis Ababa."),
    ]),
    ("GLOBAL", [
        ("OCTOBER WAS 1.8°C ABOVE PRE-INDUSTRIAL LEVELS",
         "Berkeley Earth's figure, cited in COP31's Saturday coverage, "
         "underlines the talks' stakes."),
    ]),
    ("AFRICA", [
        ("AFRICA HOLDS OUT FOR $120BN ADAPTATION FINANCE",
         "Negotiators want funding tripled to $120bn a year by 2035, with a "
         "delivery plan, or no deal."),
        ("KENYA PUBLISHES JUDGE-BY-JUDGE SCORECARD",
         "Saturday's papers lead on the judiciary review; the court backlog "
         "is put at some 580,000 cases."),
        ("MAURITANIA ORDERS GOLD PANNERS OUT OF BORDER SITES",
         "Artisanal miners have 14 days to leave the border sites."),
    ]),
    ("LATIN AMERICA", [
        ("TESLA OPENS FIRST ARGENTINA STORE, IN BUENOS AIRES",
         "The EV maker plants its flag in Argentina's capital."),
        ("MISS UNIVERSE COSTUME SHOW LIGHTS UP SAN JUAN",
         "116 delegates parade in Puerto Rico tonight in the 75th pageant; "
         "the final is Tuesday."),
    ]),
    ("OCEANIA", [
        ("NSW LAW LETS COAL MINE LIFT OUTPUT BY 32%",
         "Mount Pleasant may raise output from 12.5 to 16.5 million tonnes "
         "a year to 2032."),
        ("MIDWIVES WARN HOME-BIRTH SERVICES MAY COLLAPSE",
         "The end of an insurance exemption on 31 December could end "
         "private home birth in Australia."),
        ("CYCLONE XAVIER STILL LASHES NORTHERN COOK ISLANDS",
         "Strongest November cyclone east of the date line on record, "
         "220 km/h at peak; gales continue."),
        ("INDIA 159-1 AT WELLINGTON, TRAILING BY 209",
         "Jaiswal-Rahul stand of 130, India's largest in New Zealand this "
         "century; day three today."),
    ]),
]


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
MARGIN = 17
GUTTER = 14
COLW = 237
COLS = 4
CONTENT_W = COLS * COLW + (COLS - 1) * GUTTER  # 990
GRID_TOP = 288
GRID_BOTTOM = 990
WRAP = 38  # characters per column line at scale 1


def col_x(i):
    return MARGIN + i * (COLW + GUTTER)


def draw_masthead(cv):
    cv.fill_rect(MARGIN, 12, CONTENT_W, 3, INK)
    cv.fill_rect(MARGIN, 18, CONTENT_W, 1, INK)
    cv.text_centered(W // 2, 25, "ONE PAGE · EVERY REGION · NOTHING BUT THE DAY",
                     1, GREY)
    cv.text_centered(W // 2, 38, "THE WORLD IN ONE DAY", 6, INK)
    cv.fill_rect(MARGIN, 86, CONTENT_W, 1, INK)
    cv.fill_rect(MARGIN, 89, CONTENT_W, 3, INK)
    # Date banner
    by = 98
    cv.fill_rect(MARGIN, by, CONTENT_W, 38, RED)
    cv.text(MARGIN + 14, by + 15, "44 STORIES", 1, WHITE, bold=True)
    cv.text_right(MARGIN + CONTENT_W - 14, by + 15, "8 REGIONS", 1, WHITE,
                  bold=True)
    cv.text_centered(W // 2, by + 8, DATE_LINE, 3, WHITE, bold=True)


def draw_numbers(cv):
    top = 144
    cv.fill_rect(MARGIN, top, CONTENT_W, 2, INK)
    cell = CONTENT_W / len(NUMBERS)
    for i, (num, labels) in enumerate(NUMBERS):
        cx = MARGIN + cell * i + cell / 2
        cv.text_centered(int(cx), top + 8, num, 3, RED, bold=True)
        ly = top + 36
        for lab in labels:
            cv.text_centered(int(cx), ly, lab, 1, INK)
            ly += 9
        if i:
            bx = int(MARGIN + cell * i)
            cv.fill_rect(bx, top + 8, 1, 40, (205, 198, 182))
    cv.fill_rect(MARGIN, top + 58, CONTENT_W, 2, INK)


def draw_lead(cv):
    y = 208
    h = 68
    cv.fill_rect(MARGIN, y, CONTENT_W, h, LEADBG)
    cv.fill_rect(MARGIN, y, 6, h, RED)
    x = MARGIN + 18
    cv.text(x, y + 7, LEAD_TAG, 1, RED, bold=True)
    cv.text(x, y + 18, LEAD_HEAD, 2, INK, bold=True)
    lines = wrap(LEAD_DECK, 158)
    ly = y + 40
    for line in lines:
        cv.text(x, ly, line, 1, INK)
        ly += 10


def card_height(head, deck):
    hl = len(wrap(head, WRAP))
    dl = len(wrap(deck, WRAP))
    return 3 + hl * 9 + 1 + dl * 9 + 2, hl, dl


def draw_card(cv, x, y, head, deck):
    h, hl, dl = card_height(head, deck)
    ly = y + 3
    for line in wrap(head, WRAP):
        cv.text(x, ly, line, 1, INK, bold=True)
        ly += 9
    ly += 1
    for line in wrap(deck, WRAP):
        cv.text(x, ly, line, 1, (52, 48, 44))
        ly += 9
    cv.fill_rect(x, y + h, COLW, 1, (205, 198, 182))
    return h


def draw_grid(cv):
    col = 0
    y = GRID_TOP
    for name, cards in SECTIONS:
        first_h, _, _ = card_height(*cards[0])
        if y + 22 + first_h > GRID_BOTTOM and y > GRID_TOP:
            col += 1
            y = GRID_TOP
        x = col_x(col)
        cv.fill_rect(x, y, COLW, 18, INK)
        cv.fill_rect(x + 5, y + 5, 8, 8, RED)
        cv.text(x + 19, y + 5, name, 1, WHITE, bold=True)
        cv.text_right(x + COLW - 6, y + 5, str(len(cards)), 1, WHITE)
        y += 22
        for head, deck in cards:
            h, _, _ = card_height(head, deck)
            if y + h + 3 > GRID_BOTTOM and y > GRID_TOP:
                col += 1
                y = GRID_TOP
                x = col_x(col)
            draw_card(cv, x, y, head, deck)
            y += h + 3
    return col, y


def draw_footer(cv):
    cv.fill_rect(MARGIN, 996, CONTENT_W, 1, INK)
    cv.text_centered(
        W // 2, 1003,
        "COMPILED FROM THE DAY'S REPORTING: AP · REUTERS · WSJ · THE TIMES "
        "· LE MONDE · PIB · ESPNCRICINFO · GUARDIAN · AND OTHERS",
        1, GREY)


def render():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_numbers(cv)
    draw_lead(cv)
    col, y = draw_grid(cv)
    draw_footer(cv)
    print("grid: last column index %d, final y %d (bottom %d)"
          % (col, y, GRID_BOTTOM))
    return png_bytes(cv)


def main():
    data = render()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
