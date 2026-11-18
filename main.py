import os
import struct
import zlib
import math

# --- BITMAP FONT (5x7) ---
# Each character is a tuple/list of 7 integers (rows, 5 bits each, bit 4 = leftmost).
FONT = {
    ' ': [0, 0, 0, 0, 0, 0, 0],
    'A': [14, 17, 17, 31, 17, 17, 17],
    'B': [30, 17, 17, 30, 17, 17, 30],
    'C': [14, 17, 16, 16, 16, 17, 14],
    'D': [30, 17, 17, 17, 17, 17, 30],
    'E': [31, 16, 16, 30, 16, 16, 31],
    'F': [31, 16, 16, 30, 16, 16, 16],
    'G': [14, 17, 16, 23, 17, 17, 14],
    'H': [17, 17, 17, 31, 17, 17, 17],
    'I': [14, 4, 4, 4, 4, 4, 14],
    'J': [7, 2, 2, 2, 2, 18, 12],
    'K': [17, 18, 20, 24, 20, 18, 17],
    'L': [16, 16, 16, 16, 16, 16, 31],
    'M': [17, 27, 21, 17, 17, 17, 17],
    'N': [17, 17, 25, 21, 19, 17, 17],
    'O': [14, 17, 17, 17, 17, 17, 14],
    'P': [30, 17, 17, 30, 16, 16, 16],
    'Q': [14, 17, 17, 17, 21, 18, 13],
    'R': [30, 17, 17, 30, 20, 18, 17],
    'S': [14, 17, 16, 14, 1, 17, 14],
    'T': [31, 4, 4, 4, 4, 4, 4],
    'U': [17, 17, 17, 17, 17, 17, 14],
    'V': [17, 17, 17, 17, 17, 10, 4],
    'W': [17, 17, 17, 21, 21, 27, 17],
    'X': [17, 17, 10, 4, 10, 17, 17],
    'Y': [17, 17, 10, 4, 4, 4, 4],
    'Z': [31, 1, 2, 4, 8, 16, 31],
    '0': [14, 17, 19, 21, 25, 17, 14],
    '1': [4, 12, 4, 4, 4, 4, 14],
    '2': [14, 17, 1, 6, 8, 16, 31],
    '3': [31, 1, 2, 6, 1, 17, 14],
    '4': [2, 6, 10, 18, 31, 2, 2],
    '5': [31, 16, 30, 1, 1, 17, 14],
    '6': [14, 16, 16, 30, 17, 17, 14],
    '7': [31, 1, 2, 4, 8, 8, 8],
    '8': [14, 17, 17, 14, 17, 17, 14],
    '9': [14, 17, 17, 15, 1, 1, 14],
    ':': [0, 4, 0, 0, 4, 0, 0],
    '.': [0, 0, 0, 0, 0, 4, 4],
    ',': [0, 0, 0, 0, 4, 4, 8],
    '-': [0, 0, 0, 31, 0, 0, 0],
    '&': [12, 18, 18, 12, 21, 18, 13],
    "'": [4, 4, 2, 0, 0, 0, 0],
    '/': [1, 2, 4, 8, 16, 0, 0],
    '(': [2, 4, 8, 8, 8, 4, 2],
    ')': [8, 4, 2, 2, 2, 4, 8],
}

# --- CANVAS CLASS ---
class Canvas:
    def __init__(self, w, h, bg_color):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        # Fill with bg_color
        r, g, b = bg_color
        for i in range(0, len(self.buf), 3):
            self.buf[i] = r
            self.buf[i+1] = g
            self.buf[i+2] = b

    def set_pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            idx = (y * self.w + x) * 3
            self.buf[idx] = color[0]
            self.buf[idx+1] = color[1]
            self.buf[idx+2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        cr, cg, cb = color
        for py in range(y0, y1):
            row_offset = (py * self.w + x0) * 3
            for px in range(x0, x1):
                self.buf[row_offset] = cr
                self.buf[row_offset+1] = cg
                self.buf[row_offset+2] = cb
                row_offset += 3

    def fill_rounded_rect(self, x, y, w, h, r, color):
        self.fill_rect(x + r, y, w - 2 * r, h, color)
        self.fill_rect(x, y + r, r, h - 2 * r, color)
        self.fill_rect(x + w - r, y + r, r, h - 2 * r, color)
        self.fill_circle_quad(x + r, y + r, r, color, 1)
        self.fill_circle_quad(x + w - r - 1, y + r, r, color, 2)
        self.fill_circle_quad(x + r, y + h - r - 1, r, color, 3)
        self.fill_circle_quad(x + w - r - 1, y + h - r - 1, r, color, 4)

    def fill_circle_quad(self, cx, cy, r, color, quad):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx*dx + dy*dy <= r*r:
                    if quad == 1 and dx <= 0 and dy <= 0:
                        self.set_pixel(cx + dx, cy + dy, color)
                    elif quad == 2 and dx >= 0 and dy <= 0:
                        self.set_pixel(cx + dx, cy + dy, color)
                    elif quad == 3 and dx <= 0 and dy >= 0:
                        self.set_pixel(cx + dx, cy + dy, color)
                    elif quad == 4 and dx >= 0 and dy >= 0:
                        self.set_pixel(cx + dx, cy + dy, color)

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx*dx + dy*dy <= r*r:
                    self.set_pixel(cx + dx, cy + dy, color)

    def draw_line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def fill_polygon(self, points, color):
        if not points:
            return
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        for y in range(max(0, min_y), min(self.h, max_y + 1)):
            nodes = []
            j = len(points) - 1
            for i in range(len(points)):
                xi, yi = points[i]
                xj, yj = points[j]
                if (yi < y and yj >= y) or (yj < y and yi >= y):
                    if yi != yj:
                        nodes.append(int(xi + (y - yi) / (yj - yi) * (xj - xi)))
                j = i
            nodes.sort()
            for i in range(0, len(nodes), 2):
                if i + 1 < len(nodes):
                    x_start = max(0, nodes[i])
                    x_end = min(self.w, nodes[i+1] + 1)
                    for x in range(x_start, x_end):
                        self.set_pixel(x, y, color)

# --- TEXT FUNCTIONS ---
def draw_char(canvas, x, y, ch, scale, color):
    glyph = FONT.get(ch.upper(), FONT[' '])
    for row_idx, row_bits in enumerate(glyph):
        for col_idx in range(5):
            if (row_bits >> (4 - col_idx)) & 1:
                # draw scaled pixel block
                px = x + col_idx * scale
                py = y + row_idx * scale
                canvas.fill_rect(px, py, scale, scale, color)

def draw_text(canvas, x, y, s, scale, color, align='left'):
    char_w = 6 * scale
    total_w = len(s) * char_w - scale # last char has no trailing gap if desired, or full char_w per char
    # Actually, 5 cols + 1 gap = 6 pixels per character cell.
    total_w = len(s) * 6 * scale
    start_x = x
    if align == 'center':
        start_x = x - total_w // 2
    elif align == 'right':
        start_x = x - total_w

    curr_x = start_x
    for ch in s:
        draw_char(canvas, curr_x, y, ch, scale, color)
        curr_x += 6 * scale

def wrap_text(s, max_chars):
    words = s.split(' ')
    lines = []
    current_line = []
    current_length = 0
    for word in words:
        word_len = len(word)
        if current_length == 0:
            current_line.append(word)
            current_length = word_len
        elif current_length + 1 + word_len <= max_chars:
            current_line.append(word)
            current_length += 1 + word_len
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_len
    if current_line:
        lines.append(' '.join(current_line))
    return lines

def draw_text_block(canvas, x, y, width, height, text, scale, color, align='left', max_chars=22):
    lines = wrap_text(text, max_chars)
    line_h = 7 * scale
    gap = 2 * scale
    total_h = len(lines) * line_h + (len(lines) - 1) * gap
    start_y = y + (height - total_h) // 2
    for i, line in enumerate(lines):
        ly = start_y + i * (line_h + gap)
        lx = x
        if align == 'center':
            lx = x + width // 2
        elif align == 'right':
            lx = x + width
        draw_text(canvas, lx, ly, line, scale, color, align=align)

# --- PNG ENCODER ---
def encode_png(buf, w, h, path):
    # buf is raw RGB RGB RGB... length w*h*3
    # Build filtered scanlines (filter type 0 = None)
    scanline_len = w * 3 + 1
    raw_data = bytearray()
    for y in range(h):
        raw_data.append(0) # filter type 0
        row_start = y * w * 3
        raw_data.extend(buf[row_start:row_start + w * 3])

    compressed = zlib.compress(raw_data, level=9)

    def chunk(tag, data):
        c = struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
        return struct.pack('>I', len(data)) + tag + data + c

    png = bytearray(b'\x89PNG\r\n\x1a\n')
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    png.extend(chunk(b'IHDR', ihdr))
    png.extend(chunk(b'IDAT', compressed))
    png.extend(chunk(b'IEND', b''))

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(png)

# --- MAIN DRAWING LOGIC ---
def main():
    width, height = 1024, 1024
    paper_bg = (246, 241, 227)
    canvas = Canvas(width, height, paper_bg)

    navy = (22, 35, 63)
    gold = (232, 184, 75)
    white = (255, 255, 255)
    pale_yellow = (255, 242, 204)

    # 1. HEADER band y=0..140, solid navy #16233F, thin gold #E8B84B rule at y=140..146.
    canvas.fill_rect(0, 0, width, 140, navy)
    canvas.fill_rect(0, 140, width, 6, gold)

    # Centered title '18 NOVEMBER 2026' in large text (scale 6), y~25
    draw_text(canvas, width // 2, 28, '18 NOVEMBER 2026', 6, white, align='center')
    # Centered subline 'WORLD NEWS IN ONE IMAGE' in gold, scale 2, at y~100
    draw_text(canvas, width // 2, 102, 'WORLD NEWS IN ONE IMAGE', 2, gold, align='center')

    # 2. HERO panel y=156..356, full width x=16..1008
    # Canvas side margins 16px -> width is 1024 - 32 = 992. x from 16 to 1008.
    hero_x = 16
    hero_y = 156
    hero_w = 992
    hero_h = 200 # y=156..356

    # Warm dusk sky (flat bands of orange #E8833A top to pale sand #F2C184) in y=156..316
    orange_sky = (232, 131, 58)
    pale_sand = (242, 193, 132)
    dark_teal_sea = (20, 80, 92)

    # Sky gradient / bands (y=156..280)
    for y in range(156, 281):
        t = (y - 156) / (280 - 156)
        r = int(orange_sky[0] * (1 - t) + pale_sand[0] * t)
        g = int(orange_sky[1] * (1 - t) + pale_sand[1] * t)
        b = int(orange_sky[2] * (1 - t) + pale_sand[2] * t)
        canvas.fill_rect(hero_x, y, hero_w, 1, (r, g, b))

    # Sea (y=281..316)
    canvas.fill_rect(hero_x, 281, hero_w, 316 - 281 + 1, dark_teal_sea)

    # Dark island silhouette with a missile launcher
    # Island polygon
    island_pts = [(200, 316), (280, 275), (450, 275), (550, 316)]
    canvas.fill_polygon(island_pts, (15, 25, 40))
    # Missile launcher on island (simple shapes: rect + angled tube)
    canvas.fill_rect(350, 260, 20, 15, (40, 50, 60))
    canvas.draw_line(360, 265, 390, 245, (60, 70, 80))
    canvas.draw_line(361, 265, 391, 245, (60, 70, 80))

    # Dark navy jet silhouette flying left-to-right with a small orange explosion burst where its bomb hits the island
    # Jet at x=600, y=210
    jet_color = (10, 15, 25)
    canvas.fill_polygon([(580, 215), (630, 210), (590, 220)], jet_color)
    canvas.fill_polygon([(595, 212), (615, 212), (605, 205)], jet_color) # wings
    # Bomb line / explosion at island (x=380, y=250)
    canvas.fill_circle(385, 248, 8, (232, 131, 58))
    canvas.fill_circle(385, 248, 4, white)

    # Two small dark drones in the sky
    # Drone 1 at x=750, y=180
    canvas.fill_rect(745, 178, 12, 3, jet_color)
    canvas.fill_rect(750, 176, 2, 7, jet_color)
    # Drone 2 at x=850, y=200
    canvas.fill_rect(845, 198, 12, 3, jet_color)
    canvas.fill_rect(850, 196, 2, 7, jet_color)

    # Dark navy caption bar across the bottom of the hero (y=316..356)
    canvas.fill_rect(hero_x, 316, hero_w, 40, navy)
    # Two lines of white scale-2 text, centered:
    # line 1 'US JETS STRIKE IRAN MISSILE SITE ON QESHM ISLAND'
    # line 2 'IRAN DRONES HIT US BASES IN BAHRAIN AND KUWAIT'
    draw_text(canvas, hero_x + hero_w // 2, 322, 'US JETS STRIKE IRAN MISSILE SITE ON QESHM ISLAND', 2, white, align='center')
    draw_text(canvas, hero_x + hero_w // 2, 340, 'IRAN DRONES HIT US BASES IN BAHRAIN AND KUWAIT', 2, white, align='center')


    # 3. GRID of 4 panels, two rows: row1 y=372..596, row2 y=612..836; columns x=16..504 and x=520..1008 (each 488 wide, 224 tall).
    col_w = 488
    row_h = 224
    row1_y = 372
    row2_y = 612
    col1_x = 16
    col2_x = 520

    # Helper for panel layout:
    def draw_panel(px, py, bg_col, title_text, caption_text, caption_col, icon_func):
        # panel background
        canvas.fill_rect(px, py, col_w, row_h, bg_col)
        # left half for icon (width ~ 200, e.g. px + 12 to px + 212)
        icon_w = 200
        icon_box_x = px + 12
        icon_box_y = py + 12
        icon_box_w = icon_w
        icon_box_h = row_h - 24

        icon_func(icon_box_x, icon_box_y, icon_box_w, icon_box_h)

        # right half for text (x = px + 224 to px + col_w - 12)
        text_x = px + 220
        text_y = py + 16
        text_w = col_w - 232
        text_h = row_h - 32

        # Title: white scale-2 text (wrap to fit ~22 chars per line, up to 3 lines)
        # Below it a shorter caption in scale-2 text in a contrasting colour (up to 3 lines).
        # Let's draw title block and caption block nicely separated.
        lines_title = wrap_text(title_text, 19)
        lines_cap = wrap_text(caption_text, 19)

        scale = 2
        line_h = 7 * scale
        gap = 3 * scale

        curr_y = text_y + 10
        for l in lines_title:
            draw_text(canvas, text_x, curr_y, l, scale, white, align='left')
            curr_y += line_h + gap

        curr_y += 6 # extra spacing between title and caption

        for l in lines_cap:
            draw_text(canvas, text_x, curr_y, l, scale, caption_col, align='left')
            curr_y += line_h + gap

    # Panel A: Steel blue #2E5E7A: Kerch Bridge
    steel_blue = (46, 94, 122)
    water_blue = (30, 70, 100)
    bridge_grey = (140, 150, 160)

    def icon_kerch(ix, iy, iw, ih):
        # background of icon box (darker water)
        canvas.fill_rect(ix, iy, iw, ih, water_blue)
        # Bridge deck horizontal across middle
        deck_y = iy + ih // 2
        canvas.fill_rect(ix, deck_y - 6, iw, 12, bridge_grey)
        # Piers
        canvas.fill_rect(ix + 30, deck_y + 6, 8, ih - (deck_y + 6 - iy), (100, 110, 120))
        canvas.fill_rect(ix + 120, deck_y + 6, 8, ih - (deck_y + 6 - iy), (100, 110, 120))
        # Broken span tilted down into blue water at x=70..110
        # draw tilted span line or polygon
        canvas.fill_polygon([(ix+70, deck_y), (ix+110, deck_y + 35), (ix+115, deck_y + 25), (ix+75, deck_y - 6)], (110, 120, 130))
        # Orange explosion puff at the break
        canvas.fill_circle(ix + 85, deck_y + 5, 10, orange_sky)
        canvas.fill_circle(ix + 85, deck_y + 5, 5, white)

    draw_panel(col1_x, row1_y, steel_blue, 'KERCH BRIDGE HIT AGAIN', 'ROAD SPAN FALLS INTO THE STRAIT', pale_yellow, icon_kerch)


    # Panel B: Deep red #8C2B2B: APEC Shenzhen
    deep_red = (140, 43, 43)
    skyline_dark = (100, 25, 25)

    def icon_apec(ix, iy, iw, ih):
        canvas.fill_rect(ix, iy, iw, ih, (60, 20, 20))
        # Skyline silhouettes with lit windows
        canvas.fill_rect(ix + 10, iy + 40, 35, ih - 40, skyline_dark)
        canvas.fill_rect(ix + 55, iy + 20, 40, ih - 20, skyline_dark)
        canvas.fill_rect(ix + 105, iy + 50, 30, ih - 50, skyline_dark)
        canvas.fill_rect(ix + 145, iy + 30, 45, ih - 30, skyline_dark)

        # Lit windows (tiny yellow rects)
        for wy in range(iy + 30, iy + ih - 10, 12):
            for wx in range(ix + 15, ix + 190, 10):
                if (wx + wy) % 3 == 0:
                    canvas.fill_rect(wx, wy, 3, 5, gold)

        # Three small flag poles and suited figures at podiums at bottom
        canvas.fill_rect(ix + 30, iy + ih - 35, 3, 35, white)
        canvas.fill_rect(ix + 90, iy + ih - 35, 3, 35, white)
        canvas.fill_rect(ix + 150, iy + ih - 35, 3, 35, white)
        # flags
        canvas.fill_rect(ix + 33, iy + ih - 35, 10, 6, (200, 40, 40)) # red
        canvas.fill_rect(ix + 93, iy + ih - 35, 10, 6, (40, 100, 200)) # blue
        canvas.fill_rect(ix + 153, iy + ih - 35, 10, 6, white) # white

    draw_panel(col2_x, row1_y, deep_red, 'APEC OPENS IN SHENZHEN', 'XI AND PUTIN OPEN SUMMIT AHEAD OF TRUMP TALKS', gold, icon_apec)


    # Panel C: Medium blue #2B4C8C: ballot box
    medium_blue = (43, 76, 140)

    def icon_ballot(ix, iy, iw, ih):
        canvas.fill_rect(ix, iy, iw, ih, (30, 55, 105))
        # Ballot box (white box with slot, paper ballot going in)
        box_x = ix + 40
        box_y = iy + 60
        box_w = 100
        box_h = 90
        canvas.fill_rect(box_x, box_y, box_w, box_h, white)
        # Box shadow / inner detail
        canvas.fill_rect(box_x + 10, box_y + 20, box_w - 20, box_h - 30, (220, 225, 235))
        # Slot
        canvas.fill_rect(box_x + 30, box_y + 15, 40, 4, navy)
        # Paper ballot sliding in (tilted rect/polygon)
        ballot_pts = [(box_x + 35, box_y - 25), (box_x + 65, box_y - 25), (box_x + 55, box_y + 15), (box_x + 30, box_y + 15)]
        canvas.fill_polygon(ballot_pts, paper_bg)
        # Big gold check mark next to / above box
        # Check mark lines
        cx_chk = ix + 140
        cy_chk = iy + 50
        canvas.draw_line(cx_chk, cy_chk + 15, cx_chk + 10, cy_chk + 25, gold)
        canvas.draw_line(cx_chk + 10, cy_chk + 25, cx_chk + 30, cy_chk, gold)
        canvas.draw_line(cx_chk, cy_chk + 16, cx_chk + 10, cy_chk + 26, gold)
        canvas.draw_line(cx_chk + 10, cy_chk + 26, cx_chk + 30, cy_chk + 1, gold)

    draw_panel(col1_x, row2_y, medium_blue, 'PELTOLA WINS ALASKA SENATE', 'DEMOCRATS TAKE 56-44 MAJORITY', pale_yellow, icon_ballot)


    # Panel D: Near-black #0E1220 with small white star dots: Voyager 1 probe
    near_black = (14, 18, 32)

    def icon_voyager(ix, iy, iw, ih):
        canvas.fill_rect(ix, iy, iw, ih, near_black)
        # Small white star dots
        for sx in range(ix + 10, ix + iw - 10, 25):
            for sy in range(iy + 10, iy + ih - 10, 20):
                if (sx * sy) % 7 == 0:
                    canvas.set_pixel(sx, sy, white)
        # Small pale sun at far left
        canvas.fill_circle(ix + 25, iy + ih // 2, 8, (245, 230, 180))

        # Voyager 1 probe (gold bus body, white dish, long thin antenna mast)
        probe_x = ix + 110
        probe_y = iy + ih // 2
        # Gold bus body
        canvas.fill_rect(probe_x, probe_y - 8, 20, 16, gold)
        # White dish on left of bus
        canvas.fill_circle(probe_x - 10, probe_y, 12, white)
        canvas.fill_circle(probe_x - 10, probe_y, 10, near_black)
        # Long thin antenna mast extending right
        canvas.draw_line(probe_x + 20, probe_y, probe_x + 60, probe_y - 15, (200, 200, 200))

    draw_panel(col2_x, row2_y, near_black, 'VOYAGER 1: ONE LIGHT-DAY OUT', 'FIRST HUMAN OBJECT SO FAR: 16 BN MILES', pale_yellow, icon_voyager)


    # 4. FOOTER band y=852..1008, solid navy #16233F.
    footer_y = 852
    footer_h = 156
    canvas.fill_rect(0, footer_y, width, footer_h, navy)

    # Gold scale-2 label 'ALSO TODAY:' at top-left inside it
    draw_text(canvas, 32, 860, 'ALSO TODAY:', 2, gold, align='left')

    # Four lines of white scale-2 text:
    draw_text(canvas, 32, 891, 'US LOSES MEASLES-FREE STATUS: 5,412 CASES, 10 DEAD', 2, white, align='left')
    draw_text(canvas, 32, 922, 'EBOLA PASSES 11,000 CASES AND 5,400 DEATHS IN CONGO', 2, white, align='left')
    draw_text(canvas, 32, 953, 'AN-12 CRASH KILLS 19 IN SIBERIA - 146,000 MARCH IN FRANCE', 2, white, align='left')
    draw_text(canvas, 32, 984, 'QUAKES IN PNG AND ROMANIA', 2, white, align='left')


    # Save PNG
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    out_path = os.path.join(out_dir, 'entry.png')
    encode_png(canvas.buf, width, height, out_path)

    file_size = os.path.getsize(out_path)
    print(f"Saved to {out_path} ({file_size} bytes)")

if __name__ == '__main__':
    main()
