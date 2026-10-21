print("Starting, importing libraries...")
import math
import ti_draw as draw
import ti_system as system
print("Finished importing libraries")
# ======================= CONSTANTS =======================
W = 319
H = 209
FOV = 1.05
MAX_DIST = 14.0
VIEW_TOP = 19
VIEW_BOT = 190
MID = 105

# Fixed keys (menus + movement)
K_ENTER = 105
K_BACK = 45
K_UP = 25
K_DOWN = 34
K_LEFT = 24
K_RIGHT = 26

# Remappable keys (SETTINGS > CONTROLS): shoot, use, next weapon, turn/strafe
DEF_KEYS = [21, 105, 22, 23]
KEYS = [21, 105, 22, 23]
KN = ["SHOOT", "USE", "NEXT WEAPON", "TURN/STRAFE"]
KC = ["YELLOW", "RED", "BLUE"]

QUAL = [(40, 8), (53, 6), (80, 4)]
QN = ["LOW", "MED", "HIGH"]
DN = ["EASY", "NORMAL", "HARD"]
DMGM = [0.6, 1.0, 1.5]
SPDM = [0.8, 1.0, 1.2]
TURN = [0.04, 0.055, 0.075, 0.1, 0.13]
AMAX = [99, 40, 20]

# tile ids: 1-4 walls, 5/6/7 yellow/red/blue door, 8 gate, 9 switch,
# 10 used switch, 11-14 secret walls that look like walls 1-4
WRGB = [None, (100, 75, 50), (50, 65, 100), (100, 35, 30), (40, 90, 50),
        (100, 67, 12), (100, 15, 15), (15, 35, 100), (45, 50, 60),
        (100, 20, 20), (20, 100, 30),
        (100, 75, 50), (50, 65, 100), (100, 35, 30), (40, 90, 50)]
# map character -> tile id
MC = {"1": 1, "2": 2, "3": 3, "4": 4, "Y": 5, "R": 6, "B": 7, "G": 8,
      "W": 9, "a": 11, "b": 12, "c": 13, "d": 14}
# minimap colours for doors and gates
DCOL = {5: (220, 170, 30), 6: (220, 40, 40), 7: (60, 110, 255),
        8: (120, 130, 150)}

# pickup colours (y/r/b = yellow/red/blue keys)
PCOL = {
    "H": (30, 255, 80), "A": (190, 190, 200), "B": (255, 140, 20),
    "X": (255, 70, 70), "V": (70, 200, 190),
    "y": (255, 230, 40), "r": (255, 40, 40), "b": (60, 120, 255),
    "S": (235, 235, 235), "C": (235, 235, 235), "R": (235, 235, 235)
}
PROJC = {0: (255, 150, 30), 3: (255, 60, 60), 4: (90, 255, 110)}

# enemy types:
# 0 name, 1 hp, 2 speed, 3 melee dmg, 4 ranged dmg, 5 range, 6 fire delay,
# 7 stop distance, 8 sprite size, 9 body, 10 head,
# 11 ranged kind (0 none, 1 hitscan, 2 fireball), 12 fireball speed,
# 13 pain chance %
ET = [
    ("IMP", 3, 0.030, 8, 7, 7, 80, 0.8, 34, (110, 12, 12), (160, 30, 25),
     2, 0.09, 70),
    ("ZOMBIE", 3, 0.022, 4, 5, 8, 60, 3.0, 34, (45, 75, 45), (100, 130, 80),
     1, 0.0, 60),
    ("DEMON", 10, 0.052, 14, 0, 0, 0, 0.8, 38, (140, 55, 105),
     (185, 85, 140), 0, 0.0, 40),
    ("CACO", 14, 0.025, 6, 10, 7, 75, 2.2, 42, (170, 35, 35), (215, 70, 70),
     2, 0.11, 30),
    ("BARON", 45, 0.032, 18, 12, 9, 50, 2.5, 52, (30, 110, 45), (65, 165, 75),
     2, 0.13, 10)
]

# weapons: name, ammo type, damage, hit radius, cooldown, auto, max targets, splash
WEAPONS = [
    ("PISTOL", 0, 2, 0.30, 9, False, 1, 0.0),
    ("SHOTGUN", 1, 9, 0.65, 24, False, 2, 0.0),
    ("CHAINGUN", 0, 2, 0.32, 3, True, 1, 0.0),
    ("ROCKET", 2, 14, 0.40, 36, False, 1, 1.6)
]

# weapon sprites: (r, g, b, x, y, w, h)
WSPR = [
    [(65, 65, 72, 132, 157, 55, 52), (110, 110, 118, 145, 143, 29, 48),
     (25, 25, 30, 152, 139, 15, 27)],
    [(55, 40, 28, 124, 176, 72, 33), (80, 80, 88, 140, 158, 40, 30),
     (110, 110, 118, 148, 128, 24, 40), (25, 25, 30, 153, 124, 14, 20),
     (95, 62, 30, 140, 168, 40, 14)],
    [(50, 50, 58, 122, 168, 76, 41), (95, 95, 105, 136, 134, 14, 40),
     (105, 105, 115, 152, 128, 16, 46), (95, 95, 105, 169, 134, 14, 40)],
    [(60, 75, 50, 128, 150, 64, 60), (90, 110, 80, 140, 128, 40, 40),
     (30, 30, 35, 146, 112, 28, 22), (220, 70, 20, 152, 118, 16, 10)]
]
WFLASH = [132, 118, 112, 100]

print("Loaded the variables...")

# levels
LEVELS = [
    ("HANGAR", [
        "111111111111",
        "100000000001",
        "101110110001",
        "100010000001",
        "100010111101",
        "100000100001",
        "101100100001",
        "100000000001",
        "111111111Y11",
        "1000000000E1",
        "111111111111"],
     (1.5, 1.5, 0.0),
     [(7.5, 1.5, 0), (9.5, 5.5, 0), (5.5, 7.5, 0), (5.5, 9.5, 0)],
     [(3.5, 3.5, "H"), (5.5, 5.5, "A"), (8.5, 7.5, "H"), (1.5, 6.5, "A"),
      (10.5, 4.5, "y"), (2.5, 9.5, "H")],
     ((24, 28, 43), (48, 38, 31), (60, 49, 40)),
     "FIND THE YELLOW KEY. USE THE DOOR"),

    ("TOXIC PLANT", [
        "1111111111111111",
        "1000001000000101",
        "1044401044444101",
        "1040000000000401",
        "10401111111104d1",
        "1000000~~0000001",
        "1111011101111111",
        "1000010000100001",
        "1000010~~0100001",
        "1000000~~0Y00001",
        "10000100001000E1",
        "1111111111111111"],
     (1.5, 1.5, 0.0),
     [(8.5, 1.5, 1), (10.5, 3.5, 0), (5.5, 5.5, 0), (7.5, 7.5, 1),
      (2.5, 8.5, 0), (7.5, 10.5, 1), (12.5, 8.5, 2), (3.5, 9.5, 0)],
     [(7.5, 1.5, "S"), (11.5, 1.5, "y"), (1.5, 5.5, "H"), (14.5, 1.5, "V"),
      (14.5, 2.5, "B"), (14.5, 3.5, "H"), (3.5, 7.5, "A"), (9.5, 5.5, "B"),
      (2.5, 10.5, "H"), (4.5, 3.5, "A"), (12.5, 9.5, "H")],
     ((20, 36, 28), (36, 46, 30), (48, 60, 38)),
     "AVOID THE ACID. A WALL HIDES A SECRET"),

    ("DEEP VAULT", [
        "1111111111111111",
        "1000001001000001",
        "1022222b12222201",
        "1020000000000201",
        "1020112222110201",
        "1000100000010001",
        "1110B00000E10111",
        "1000100000010001",
        "1020112222110201",
        "1020000000000201",
        "1022222b122222R1",
        "1000001001000001",
        "1111111111111111"],
     (1.5, 11.5, -1.57),
     [(3.5, 1.5, 0), (6.5, 3.5, 1), (11.5, 1.5, 3), (13.5, 1.5, 1),
      (12.5, 3.5, 2), (3.5, 9.5, 1), (11.5, 11.5, 2), (7.5, 6.5, 2),
      (8.5, 5.5, 3)],
     [(5.5, 1.5, "r"), (14.5, 1.5, "b"), (12.5, 11.5, "C"), (7.5, 1.5, "V"),
      (8.5, 1.5, "B"), (7.5, 11.5, "H"), (8.5, 11.5, "A"), (1.5, 3.5, "H"),
      (14.5, 5.5, "H"), (3.5, 3.5, "B"), (1.5, 9.5, "A"), (11.5, 9.5, "A"),
      (3.5, 11.5, "B"), (13.5, 11.5, "A")],
     ((16, 24, 40), (30, 34, 44), (44, 50, 62)),
     "RED KEY: CHAINGUN. BLUE KEY: VAULT"),

    ("HELL GATE", [
        "1111111111111111",
        "10000Y000E100001",
        "1011011W11101101",
        "1010000000000101",
        "1010333GG3330101",
        "1000300000030001",
        "1110300~~0030111",
        "1000300000030001",
        "1010333GG3330101",
        "1010000000000101",
        "1011011111101101",
        "1000000000000001",
        "1111111111111111"],
     (1.5, 11.5, 0.0),
     [(6.5, 6.5, 3), (9.5, 6.5, 3), (7.5, 3.5, 1), (3.5, 3.5, 0),
      (12.5, 3.5, 1), (3.5, 9.5, 0), (12.5, 9.5, 2), (7.5, 9.5, 2),
      (7.5, 1.5, 2)],
     [(7.5, 5.5, "y"), (14.5, 11.5, "R"), (14.5, 1.5, "X"), (1.5, 1.5, "X"),
      (1.5, 5.5, "H"), (14.5, 5.5, "H"), (14.5, 9.5, "V"), (3.5, 7.5, "A"),
      (12.5, 7.5, "B"), (1.5, 9.5, "B"), (7.5, 11.5, "H"), (12.5, 11.5, "X")],
     ((40, 12, 12), (50, 20, 16), (66, 28, 20)),
     "FIND THE SWITCH TO OPEN THE ARENA"),

    ("BARON'S LAIR", [
        "11111111111111",
        "100000~~000001",
        "10000000000001",
        "10033000033001",
        "10030000003001",
        "10000000000001",
        "10030000003001",
        "10033000033001",
        "100000~~000001",
        "100000000000E1",
        "11111111111111"],
     (1.5, 1.5, 0.7),
     [(7.5, 5.5, 4), (4.5, 8.5, 3), (10.5, 2.5, 3), (12.5, 5.5, 1),
      (1.5, 5.5, 1), (4.5, 1.5, 0), (9.5, 8.5, 0)],
     [(5.5, 1.5, "B"), (7.5, 9.5, "X"), (1.5, 9.5, "X"), (12.5, 1.5, "X"),
      (1.5, 6.5, "H"), (12.5, 7.5, "H"), (5.5, 2.5, "A"), (8.5, 8.5, "B"),
      (12.5, 3.5, "V"), (6.5, 5.5, "H"), (3.5, 5.5, "X")],
     ((30, 8, 8), (40, 16, 12), (55, 22, 16)),
     "KILL THE BARON, REACH THE EXIT")
]

print("Loading levels...")

# variables x1
qual = 1
diff = 1
turn_i = 2
show_map = True
bob_on = True
autofire = False
move_style = 0
strafe = False

BUF = False
try:
    draw.use_buffer()
    BUF = True
except:
    BUF = False

RAYS = 53
STRIP = 6
COSO = []
SINO = []
depths = []

px = 1.5
py = 1.5
angle = 0.0
ca = 1.0
sa = 0.0
health = 100
armor = 0
ammo = [30, 0, 0]
have = [True, False, False, False]
wp = 0
keys = [False, False, False]
kills = 0
tot_kills = 0
total = 0
frame = 0
doors_closed = 0
gates_closed = 0
secrets_found = 0
secrets_total = 0
moving = False
cruise = False
shoot_flash = 0
fire_cd = 0
hurt = 0
acid = 0
acid_t = 0
message = ""
msg_t = 0
seed = 12345
_pk = 0

G = []
HZ = []
HZL = []
DYN = []
DF = []
fcell = (-1, -1)
fframe = 0
MW = 12
MH = 11
STEPS = 24
EX = 0
EY = 0
enemies = []
pickups = []
projs = []
th = ((24, 28, 43), (48, 38, 31), (60, 49, 40))
MM_RUNS = []
MMC = 4
MMX = 268

print("Defined Extra Variables.")

# ======================= HELPERS =======================
def flip():
    if BUF:
        draw.paint_buffer()


def flush():
    global _pk
    _pk = system.get_key(0)


def press():
    # returns a key code only on the frame it changes
    global _pk
    k = system.get_key(0)
    if k == _pk:
        return 0
    _pk = k
    return k


def rnd():
    global seed
    seed = (seed * 75 + 74) % 65537
    return seed / 65537


def set_msg(text):
    global message, msg_t
    message = text
    msg_t = 40


def boss_alive():
    for e in enemies:
        if e[6] == 4 and e[2] > 0:
            return True
    return False


def hint():
    if gates_closed > 0:
        return "FIND THE SWITCH"
    if doors_closed > 0:
        if keys[0] or keys[1] or keys[2]:
            return "FIND THE DOOR"
        return "FIND THE KEYS"
    if boss_alive():
        return "KILL THE BARON"
    return "FIND THE EXIT"


def wake(x, y, r):
    for e in enemies:
        if not e[4]:
            dx = e[0] - x
            dy = e[1] - y
            if dx * dx + dy * dy < r * r:
                e[4] = True


def apply_quality():
    global RAYS, STRIP, COSO, SINO, depths
    RAYS = QUAL[qual][0]
    STRIP = QUAL[qual][1]
    COSO = []
    SINO = []
    for i in range(RAYS):
        a = -FOV / 2 + FOV * (i + 0.5) / RAYS
        COSO.append(math.cos(a))
        SINO.append(math.sin(a))
    depths = [MAX_DIST] * RAYS

print("Defining functions... 40%")

apply_quality()


def solid(x, y):
    return G[int(y)][int(x)] != 0


def can_stand(x, y):
    r = 0.17
    return (
        not solid(x - r, y - r)
        and not solid(x + r, y - r)
        and not solid(x - r, y + r)
        and not solid(x + r, y + r)
    )


def cast(dx, dy):
    if -0.00001 < dx < 0.00001:
        dx = 0.00001
    if -0.00001 < dy < 0.00001:
        dy = 0.00001

    mx = int(px)
    my = int(py)
    ddx = abs(1.0 / dx)
    ddy = abs(1.0 / dy)

    if dx < 0:
        sx = -1
        tx = (px - mx) * ddx
    else:
        sx = 1
        tx = (mx + 1 - px) * ddx

    if dy < 0:
        sy = -1
        ty = (py - my) * ddy
    else:
        sy = 1
        ty = (my + 1 - py) * ddy

    for n in range(STEPS):
        if tx < ty:
            d = tx
            tx += ddx
            mx += sx
            side = 0
        else:
            d = ty
            ty += ddy
            my += sy
            side = 1

        t = G[my][mx]
        if t:
            if side == 0:
                f = py + d * dy
            else:
                f = px + d * dx
            return d, side, t, f - int(f)

    return MAX_DIST, 0, 1, 0.5

print("Defining functions... 55%")

def project(x, y):
    # screen x and perpendicular distance of a point, or None if hidden
    dx = x - px
    dy = y - py
    pd = dx * ca + dy * sa
    if pd < 0.2:
        return None
    dl = math.atan2(dy * ca - dx * sa, pd)
    if dl >= FOV / 2 or dl <= -FOV / 2:
        return None
    sx = int((dl / FOV + 0.5) * W)
    i = sx // STRIP
    if i < 0:
        i = 0
    elif i >= RAYS:
        i = RAYS - 1
    if pd > depths[i] + 0.15:
        return None
    return pd, sx

def cls():
    draw.set_color(0, 0, 0)
    draw.fill_rect(0, 0, W, H)


def ctext(y, s):
    x = (W - len(s) * 8) // 2
    if x < 0:
        x = 0
    draw.draw_text(x, y, s)


def draw_world():
    c = th[0]
    draw.set_color(c[0], c[1], c[2])
    draw.fill_rect(0, 0, W, MID)
    c = th[1]
    draw.set_color(c[0], c[1], c[2])
    draw.fill_rect(0, MID, W, 104)
    c = th[2]
    draw.set_color(c[0], c[1], c[2])
    draw.fill_rect(0, 150, W, 40)

    for i in range(RAYS):
        co = COSO[i]
        so = SINO[i]
        d, side, t, f = cast(ca * co - sa * so, sa * co + ca * so)

        d *= co
        if d < 0.1:
            d = 0.1
        depths[i] = d

        h = int(100 / d)
        if h > 205:
            h = 205
        top = MID - h // 2
        bot = MID + h // 2
        if top < VIEW_TOP:
            top = VIEW_TOP
        if bot > VIEW_BOT:
            bot = VIEW_BOT

        shade = int(190 / (1 + d * 0.18))
        if side:
            shade = shade * 18 // 25
        if f < 0.05 or f > 0.95:
            shade = shade * 2 // 3
        if shade < 18:
            shade = 18
        elif shade > 220:
            shade = 220

        wc = WRGB[t]
        draw.set_color(shade * wc[0] // 100, shade * wc[1] // 100,
                       shade * wc[2] // 100)
        draw.fill_rect(i * STRIP, top, STRIP, bot - top)

    draw_acid()
    draw_exit()
    draw_pickups()
    draw_enemies()
    draw_projs()
    draw_weapon()

    if hurt > 0:
        draw.set_color(200, 0, 0)
        draw.fill_rect(0, VIEW_TOP, 7, VIEW_BOT - VIEW_TOP)
        draw.fill_rect(W - 7, VIEW_TOP, 7, VIEW_BOT - VIEW_TOP)
    if acid > 0:
        draw.set_color(60, 210, 40)
        draw.fill_rect(8, VIEW_TOP, 7, VIEW_BOT - VIEW_TOP)
        draw.fill_rect(W - 15, VIEW_TOP, 7, VIEW_BOT - VIEW_TOP)

    draw_hud()
    flip()

print("Defining functions... 75%")

def draw_acid():
    # flat green puddles on the floor
    for hz in HZL:
        r = project(hz[0], hz[1])
        if r is None:
            continue
        pd = r[0]
        if pd > 9:
            continue
        sx = r[1]
        w = int(120 / pd)
        if w > 300:
            w = 300
        il = (sx - w // 2) // STRIP
        ir = (sx + w // 2) // STRIP
        if il < 0:
            il = 0
        elif il >= RAYS:
            il = RAYS - 1
        if ir < 0:
            ir = 0
        elif ir >= RAYS:
            ir = RAYS - 1
        if depths[il] < pd or depths[ir] < pd:
            continue
        y1 = MID + int(50 / (pd + 0.5))
        far = pd - 0.5
        if far < 0.3:
            far = 0.3
        y2 = MID + int(50 / far)
        if y2 > VIEW_BOT - 1:
            y2 = VIEW_BOT - 1
        if y2 - y1 < 2:
            continue
        draw.set_color(60, 210, 40)
        draw.fill_rect(sx - w // 2, y1, w, y2 - y1)


def draw_exit():
    r = project(EX + 0.5, EY + 0.5)
    if r is None:
        return
    pd = r[0]
    sx = r[1]
    h = int(70 / pd)
    if h > 80:
        h = 80
    w = int(16 / pd)
    if w < 3:
        w = 3
    top = MID - h
    bot = MID + h // 2
    if top < VIEW_TOP + 1:
        top = VIEW_TOP + 1
    if bot > VIEW_BOT - 1:
        bot = VIEW_BOT - 1
    if boss_alive():
        draw.set_color(160, 40, 40)
    else:
        draw.set_color(20, 230, 40)
    draw.fill_rect(sx - w // 2, top, w, bot - top)


def draw_pickups():
    for p in pickups:
        if not p[3]:
            continue
        r = project(p[0], p[1])
        if r is None:
            continue
        pd = r[0]
        sx = r[1]

        if p[2] in "SCRybr":
            size = int(20 / pd)
            lim = 16
        else:
            size = int(14 / pd)
            lim = 12
        if size < 2:
            size = 2
        elif size > lim:
            size = lim

        c = PCOL[p[2]]
        draw.set_color(c[0], c[1], c[2])
        draw.fill_rect(sx - size // 2, MID + int(10 / pd) - size // 2,
                       size, size)


def draw_enemies():
    vis = []
    for i in range(len(enemies)):
        e = enemies[i]
        if e[2] <= 0:
            continue
        r = project(e[0], e[1])
        if r is None:
            continue
        vis.append((r[0], i, r[1]))

    vis.sort()

    for n in range(len(vis) - 1, -1, -1):
        pd = vis[n][0]
        e = enemies[vis[n][1]]
        sx = vis[n][2]
        et = e[6]
        T = ET[et]
        bc = T[9]
        hc = T[10]
        hit = e[5] > 0

        size = int(T[8] / pd)
        if size < 3:
            size = 3
        elif size > 60:
            size = 60

        top = MID - size
        bot = MID + size
        if top < VIEW_TOP + 2:
            top = VIEW_TOP + 2
        if bot > VIEW_BOT - 2:
            bot = VIEW_BOT - 2

        if et == 3:
            # floating eye: one big body
            if hit:
                draw.set_color(255, 150, 150)
            else:
                draw.set_color(bc[0], bc[1], bc[2])
            draw.fill_rect(sx - size // 2, top + size // 3,
                           size, bot - top - size // 2)
            draw.set_color(255, 230, 60)
            q = max(2, size // 4)
            draw.fill_rect(sx - q // 2, MID - q // 2, q, q)
            draw.set_color(30, 0, 0)
            draw.fill_rect(sx - size // 3, MID + size // 4,
                           size * 2 // 3, max(1, size // 8))
        else:
            hh = size * 2 // 3
            if hit:
                draw.set_color(255, 150, 150)
            else:
                draw.set_color(bc[0], bc[1], bc[2])
            draw.fill_rect(sx - size // 2, top + hh, size, bot - top - hh)

            if hit:
                draw.set_color(255, 200, 200)
            else:
                draw.set_color(hc[0], hc[1], hc[2])
            draw.fill_rect(sx - size // 4, top, size // 2 + 1, hh)

            draw.set_color(255, 200, 40)
            eye = max(1, size // 8)
            ey = top + hh // 3
            draw.fill_rect(sx - size // 6 - eye, ey, eye, eye)
            draw.fill_rect(sx + size // 6, ey, eye, eye)

            if et == 4:
                draw.set_color(230, 230, 200)
                hw = max(1, size // 10)
                draw.fill_rect(sx - size // 4 - hw, top, hw, hh // 2)
                draw.fill_rect(sx + size // 4 + 1, top, hw, hh // 2)

        if e[7] > 0:
            draw.set_color(255, 200, 60)
            q = max(2, size // 4)
            draw.fill_rect(sx - q // 2, MID, q, q)

print("Defining functions... 80%")

def draw_projs():
    for p in projs:
        r = project(p[0], p[1])
        if r is None:
            continue
        size = int(18 / r[0])
        if size < 3:
            size = 3
        elif size > 16:
            size = 16
        c = PROJC[p[5]]
        draw.set_color(c[0], c[1], c[2])
        draw.fill_rect(r[1] - size // 2, MID - size // 2, size, size)
        q = size // 2
        if q >= 2:
            draw.set_color(255, 255, 200)
            draw.fill_rect(r[1] - q // 2, MID - q // 2, q, q)


def draw_weapon():
    bx = 0
    by = 0
    if bob_on and moving:
        s = math.sin(frame * 0.4)
        bx = int(s * 4)
        by = int(abs(s) * 3)
    by += shoot_flash * 2

    if shoot_flash > 0:
        fy = WFLASH[wp]
        draw.set_color(255, 220, 90)
        draw.fill_rect(145 + bx, fy, 29, 25)
        draw.set_color(255, 255, 220)
        draw.fill_rect(153 + bx, fy - 12, 13, 18)

    for t in WSPR[wp]:
        draw.set_color(t[0], t[1], t[2])
        draw.fill_rect(t[3] + bx, t[4] + by, t[5], t[6])

    draw.set_color(240, 240, 220)
    draw.draw_line(154, MID, 164, MID)
    draw.draw_line(159, MID - 5, 159, MID + 5)


def draw_hud():
    draw.set_color(0, 0, 0)
    draw.fill_rect(0, 0, W, VIEW_TOP)
    draw.fill_rect(0, VIEW_BOT, W, H - VIEW_BOT)

    w = WEAPONS[wp]
    draw.set_color(255, 255, 255)
    draw.draw_text(3, 13, "HP" + str(health))
    draw.draw_text(50, 13, "AR" + str(armor))
    draw.draw_text(100, 13, w[0] + " " + str(ammo[w[1]]))
    draw.draw_text(196, 13, "K" + str(kills) + "/" + str(total))

    m = ""
    if strafe:
        m = "S"
    if cruise:
        m = m + "R"
    if m != "":
        draw.set_color(255, 200, 60)
        draw.draw_text(252, 13, m)

    kc = ((230, 200, 40), (230, 50, 50), (60, 120, 255))
    for i in range(3):
        if keys[i]:
            c = kc[i]
            draw.set_color(c[0], c[1], c[2])
            draw.fill_rect(282 + i * 11, 5, 9, 9)

    draw.set_color(255, 255, 255)
    draw.draw_text(3, 202, message)

    draw.set_color(70, 20, 20)
    draw.fill_rect(245, 195, 68, 8)
    draw.set_color(40, 220, 50)
    draw.fill_rect(245, 195, int(68 * health / 100), 8)

    if not show_map:
        return

    c = MMC
    ox = MMX
    oy = 22
    draw.set_color(25, 25, 30)
    draw.fill_rect(ox, oy, MW * c, MH * c)

    draw.set_color(135, 135, 145)
    for r in MM_RUNS:
        draw.fill_rect(ox + r[0] * c, oy + r[1] * c, r[2] * c, c)

    # doors, gates and secret walls (they change during play)
    for d in DYN:
        t = G[d[1]][d[0]]
        if t == 0:
            continue
        if t > 10:
            draw.set_color(135, 135, 145)
        else:
            k = DCOL[t]
            draw.set_color(k[0], k[1], k[2])
        draw.fill_rect(ox + d[0] * c, oy + d[1] * c, c, c)

    draw.set_color(20, 230, 40)
    draw.fill_rect(ox + EX * c, oy + EY * c, c, c)

    draw.set_color(255, 30, 30)
    for e in enemies:
        if e[2] > 0:
            draw.fill_rect(ox + int(e[0] * c) - 1,
                           oy + int(e[1] * c) - 1, 3, 3)

    sx = ox + int(px * c)
    sy = oy + int(py * c)
    draw.set_color(30, 255, 70)
    draw.fill_rect(sx - 1, sy - 1, 3, 3)
    draw.draw_line(sx, sy, sx + int(ca * 5), sy + int(sa * 5))

print("Defining functions... 100%")
print("Finished section one of defining functions")
# ======================= GAME LOGIC =======================
def move_player(forward, side, turn):
    global px, py, angle, ca, sa

    if turn != 0:
        angle += turn
        ca = math.cos(angle)
        sa = math.sin(angle)

    if forward != 0 or side != 0:
        dx = ca * forward - sa * side
        dy = sa * forward + ca * side
        if can_stand(px + dx, py):
            px += dx
        if can_stand(px, py + dy):
            py += dy


def hurt_player(d):
    global health, armor, hurt

    d = int(d * DMGM[diff] + 0.5)
    if d < 1:
        d = 1
    if armor > 0:
        a = d // 2
        if a > armor:
            a = armor
        armor -= a
        d -= a
    health -= d
    if health < 0:
        health = 0
    hurt = 4
    set_msg("YOU'RE HIT!")


def hit_enemy(e, dmg):
    global kills, tot_kills

    e[2] -= dmg
    e[4] = True
    e[5] = 4
    if e[2] <= 0:
        kills += 1
        tot_kills += 1
        set_msg(ET[e[6]][0] + " DOWN")
        return

    set_msg("HIT!")
    # pain: the demon staggers and gets knocked back
    if rnd() * 100 < ET[e[6]][13]:
        e[9] = 6
        dx = e[0] - px
        dy = e[1] - py
        d = math.sqrt(dx * dx + dy * dy)
        if d > 0.01:
            nx = e[0] + dx / d * 0.15
            ny = e[1] + dy / d * 0.15
            if not solid(nx, e[1]):
                e[0] = nx
            if not solid(e[0], ny):
                e[1] = ny


def targets(rad):
    # enemies in the crosshair with a clear line, nearest first
    out = []
    for i in range(len(enemies)):
        e = enemies[i]
        if e[2] <= 0:
            continue
        dx = e[0] - px
        dy = e[1] - py
        pd = dx * ca + dy * sa
        if pd <= 0.1:
            continue
        if abs(dy * ca - dx * sa) < rad:
            dist = math.sqrt(dx * dx + dy * dy)
            if cast(dx / dist, dy / dist)[0] >= dist - 0.3:
                out.append((pd, i))
    out.sort()
    return out


def auto_switch():
    global wp
    for i in range(3, -1, -1):
        if have[i] and ammo[WEAPONS[i][1]] > 0:
            wp = i
            return


def next_weapon():
    global wp
    for i in range(1, 5):
        n = (wp + i) % 4
        if have[n]:
            wp = n
            set_msg(WEAPONS[n][0])
            return


def try_fire():
    global fire_cd, shoot_flash

    w = WEAPONS[wp]
    at = w[1]

    if ammo[at] <= 0:
        set_msg("NO AMMO!")
        auto_switch()
        fire_cd = 10
        return

    ammo[at] -= 1
    fire_cd = w[4]
    shoot_flash = 3
    hits = targets(w[3])

    if w[7] > 0:
        # rocket: explodes on the first enemy or wall
        if hits:
            e = enemies[hits[0][1]]
            ix = e[0]
            iy = e[1]
        else:
            d = cast(ca, sa)[0] - 0.1
            ix = px + ca * d
            iy = py + sa * d
        for e in enemies:
            if e[2] <= 0:
                continue
            ddx = e[0] - ix
            ddy = e[1] - iy
            dd = math.sqrt(ddx * ddx + ddy * ddy)
            if dd < w[7]:
                dmg = int(w[2] * (1 - dd / w[7]))
                if dmg < 1:
                    dmg = 1
                hit_enemy(e, dmg)
        ddx = px - ix
        ddy = py - iy
        if ddx * ddx + ddy * ddy < 1.7:
            hurt_player(6)
        else:
            set_msg("BOOM!")
    else:
        n = 0
        for h in hits:
            if n >= w[6]:
                break
            n += 1
            dmg = w[2]
            if wp == 1:
                dmg = int(w[2] * 2.5 / (1 + h[0]))
                if dmg < 1:
                    dmg = 1
            hit_enemy(enemies[h[1]], dmg)
        if n == 0:
            set_msg("MISSED")

    if ammo[at] <= 0:
        auto_switch()


def use_action():
    # doors, switches and secret walls: face them and press USE
    global doors_closed, gates_closed, secrets_found

    d, side, t, f = cast(ca, sa)
    if d > 1.5:
        set_msg("NOTHING TO USE")
        return

    cx = int(px + ca * (d + 0.02))
    cy = int(py + sa * (d + 0.02))

    if t >= 5 and t <= 7:
        if keys[t - 5]:
            G[cy][cx] = 0
            doors_closed -= 1
            set_msg("DOOR OPENED")
            wake(cx + 0.5, cy + 0.5, 8)
        else:
            set_msg("NEED THE " + KC[t - 5] + " KEY")
    elif t == 9:
        G[cy][cx] = 10
        for g in DYN:
            if G[g[1]][g[0]] == 8:
                G[g[1]][g[0]] = 0
        gates_closed = 0
        set_msg("GATES OPENED!")
        wake(px, py, 9)
    elif t >= 11 and t <= 14:
        G[cy][cx] = 0
        secrets_found += 1
        set_msg("SECRET FOUND!")
    else:
        set_msg("NOTHING TO USE")

print("Defined the inventory system")

def build_field():
    # breadth-first distance from the player's tile, used for pathfinding
    global fcell, fframe

    sx = int(px)
    sy = int(py)
    fcell = (sx, sy)
    fframe = frame
    for y in range(MH):
        row = DF[y]
        for x in range(MW):
            row[x] = 999
    DF[sy][sx] = 0
    q = [sx, sy]
    h = 0
    while h < len(q):
        x = q[h]
        y = q[h + 1]
        h += 2
        d = DF[y][x] + 1
        if G[y][x + 1] == 0 and DF[y][x + 1] > d:
            DF[y][x + 1] = d
            q.append(x + 1)
            q.append(y)
        if G[y][x - 1] == 0 and DF[y][x - 1] > d:
            DF[y][x - 1] = d
            q.append(x - 1)
            q.append(y)
        if G[y + 1][x] == 0 and DF[y + 1][x] > d:
            DF[y + 1][x] = d
            q.append(x)
            q.append(y + 1)
        if G[y - 1][x] == 0 and DF[y - 1][x] > d:
            DF[y - 1][x] = d
            q.append(x)
            q.append(y - 1)


def spawn_proj(e, T, dist):
    if len(projs) >= 8:
        return
    sp = T[12]
    projs.append([e[0], e[1], (px - e[0]) / dist * sp,
                  (py - e[1]) / dist * sp, T[4], e[6], 90])


def update_projs():
    for i in range(len(projs) - 1, -1, -1):
        p = projs[i]
        p[0] += p[2]
        p[1] += p[3]
        p[6] -= 1
        dx = p[0] - px
        dy = p[1] - py
        if dx * dx + dy * dy < 0.16:
            hurt_player(p[4])
            projs.pop(i)
        elif p[6] <= 0 or solid(p[0], p[1]):
            projs.pop(i)


def update_enemies():
    for i in range(len(enemies)):
        e = enemies[i]
        if e[2] <= 0:
            continue

        if e[5] > 0:
            e[5] -= 1
        if e[7] > 0:
            e[7] -= 1

        T = ET[e[6]]
        dx = px - e[0]
        dy = py - e[1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 0.01:
            dist = 0.01

        # sleeping demons wake up when they see or hear you
        if not e[4]:
            if dist < 1.5:
                e[4] = True
            elif dist < 9 and (frame + i) % 8 == 0:
                if cast(-dx / dist, -dy / dist)[0] >= dist - 0.2:
                    e[4] = True
            continue

        # pain stagger
        if e[9] > 0:
            e[9] -= 1
            continue

        # line of sight (cached, refreshed every 6 frames)
        if (frame + i) % 6 == 0:
            e[8] = cast(-dx / dist, -dy / dist)[0] >= dist - 0.2

        if dist > T[7]:
            sp = T[2] * SPDM[diff]
            if e[8] or dist < 1.2:
                mx = dx / dist
                my = dy / dist
            else:
                # no line of sight: follow the distance field around walls
                if (int(px), int(py)) != fcell and frame - fframe >= 4:
                    build_field()
                cx = int(e[0])
                cy = int(e[1])
                bv = DF[cy][cx]
                bx = cx
                by = cy
                v = DF[cy][cx + 1]
                if v < bv:
                    bv = v
                    bx = cx + 1
                    by = cy
                v = DF[cy][cx - 1]
                if v < bv:
                    bv = v
                    bx = cx - 1
                    by = cy
                v = DF[cy + 1][cx]
                if v < bv:
                    bv = v
                    bx = cx
                    by = cy + 1
                v = DF[cy - 1][cx]
                if v < bv:
                    bv = v
                    bx = cx
                    by = cy - 1
                if bx == cx and by == cy:
                    mx = dx / dist
                    my = dy / dist
                else:
                    tx = bx + 0.5 - e[0]
                    ty = by + 0.5 - e[1]
                    td = math.sqrt(tx * tx + ty * ty)
                    if td < 0.01:
                        td = 0.01
                    mx = tx / td
                    my = ty / td
            nx = e[0] + mx * sp
            ny = e[1] + my * sp
            if not solid(nx, e[1]):
                e[0] = nx
            if not solid(e[0], ny):
                e[1] = ny

        # keep demons from stacking on each other
        if (frame + i) % 2 == 0:
            for j in range(len(enemies)):
                if j == i:
                    continue
                o = enemies[j]
                if o[2] <= 0:
                    continue
                sx = e[0] - o[0]
                if -0.5 < sx < 0.5:
                    sy = e[1] - o[1]
                    if -0.5 < sy < 0.5:
                        d2 = sx * sx + sy * sy
                        if d2 < 0.25:
                            if d2 < 0.0004:
                                sx = 0.05
                                d2 = 0.0025
                            d3 = math.sqrt(d2)
                            nx = e[0] + sx / d3 * 0.03
                            ny = e[1] + sy / d3 * 0.03
                            if not solid(nx, e[1]):
                                e[0] = nx
                            if not solid(e[0], ny):
                                e[1] = ny

        # attacks
        if dist <= 0.9:
            e[3] += 1
            if e[3] >= 35:
                e[3] = 0
                hurt_player(T[3])
        elif T[11] > 0 and dist <= T[5] and e[8]:
            e[3] += 1
            if e[3] >= T[6]:
                e[3] = 0
                e[7] = 4
                if T[11] == 1:
                    if rnd() < 0.95 - dist * 0.08:
                        hurt_player(T[4])
                else:
                    spawn_proj(e, T, dist)
        elif e[3] > 15:
            e[3] = 15


def collect_pickups():
    global health, armor, wp

    for p in pickups:
        if not p[3]:
            continue
        dx = px - p[0]
        dy = py - p[1]
        if dx * dx + dy * dy >= 0.25:
            continue

        k = p[2]
        if k == "H" and health < 100:
            health = min(100, health + 25)
            set_msg("HEALTH +25")
        elif k == "V" and armor < 100:
            armor = min(100, armor + 50)
            set_msg("ARMOR +50")
        elif k == "A" and ammo[0] < AMAX[0]:
            ammo[0] = min(AMAX[0], ammo[0] + 15)
            set_msg("BULLETS +15")
        elif k == "B" and ammo[1] < AMAX[1]:
            ammo[1] = min(AMAX[1], ammo[1] + 6)
            set_msg("SHELLS +6")
        elif k == "X" and ammo[2] < AMAX[2]:
            ammo[2] = min(AMAX[2], ammo[2] + 3)
            set_msg("ROCKETS +3")
        elif k == "y":
            keys[0] = True
            set_msg("YELLOW KEY!")
        elif k == "r":
            keys[1] = True
            set_msg("RED KEY!")
        elif k == "b":
            keys[2] = True
            set_msg("BLUE KEY!")
        elif k == "S":
            have[1] = True
            ammo[1] = min(AMAX[1], ammo[1] + 8)
            wp = 1
            set_msg("SHOTGUN!")
        elif k == "C":
            have[2] = True
            ammo[0] = min(AMAX[0], ammo[0] + 30)
            wp = 2
            set_msg("CHAINGUN!")
        elif k == "R":
            have[3] = True
            ammo[2] = min(AMAX[2], ammo[2] + 5)
            wp = 3
            set_msg("ROCKET LAUNCHER!")
        else:
            continue
        p[3] = False


def load_level(n):
    global G, HZ, HZL, DYN, DF, MW, MH, STEPS, EX, EY, enemies, pickups
    global projs, th, px, py, angle, ca, sa, kills, total, keys, cruise
    global doors_closed, gates_closed, secrets_found, secrets_total
    global frame, shoot_flash, fire_cd, hurt, acid, acid_t, moving, depths
    global MM_RUNS, MMC, MMX, message, msg_t, fcell, fframe

    L = LEVELS[n]
    rows = L[1]
    MH = len(rows)
    MW = len(rows[0])
    STEPS = MW + MH + 2
    G = []
    HZ = []
    HZL = []
    DYN = []
    DF = []
    doors_closed = 0
    gates_closed = 0
    secrets_total = 0
    for y in range(MH):
        row = []
        hrow = []
        for x in range(MW):
            c = rows[y][x]
            hz = False
            if c == "0":
                v = 0
            elif c == "E":
                v = 0
                EX = x
                EY = y
            elif c == "~":
                v = 0
                hz = True
                HZL.append((x + 0.5, y + 0.5))
            else:
                v = MC[c]
                if v == 8 or (v >= 5 and v <= 7) or v >= 11:
                    DYN.append((x, y))
                if v >= 5 and v <= 7:
                    doors_closed += 1
                elif v == 8:
                    gates_closed += 1
                elif v >= 11:
                    secrets_total += 1
            row.append(v)
            hrow.append(hz)
        G.append(row)
        HZ.append(hrow)
        DF.append([999] * MW)

    # minimap: merge static wall cells into runs
    MM_RUNS = []
    for y in range(MH):
        x = 0
        while x < MW:
            v = G[y][x]
            if v > 0 and (v < 5 or v == 9 or v == 10):
                s = x
                while x < MW:
                    v = G[y][x]
                    if v > 0 and (v < 5 or v == 9 or v == 10):
                        x += 1
                    else:
                        break
                MM_RUNS.append((s, y, x - s))
            else:
                x += 1
    MMC = min(52 // MW, 44 // MH)
    if MMC < 2:
        MMC = 2
    MMX = W - MW * MMC - 3

    enemies = []
    for s in L[3]:
        enemies.append([s[0], s[1], ET[s[2]][1], 0, False, 0, s[2], 0,
                        False, 0])
    pickups = []
    for s in L[4]:
        pickups.append([s[0], s[1], s[2], True])
    projs = []

    px = L[2][0]
    py = L[2][1]
    angle = L[2][2]
    ca = math.cos(angle)
    sa = math.sin(angle)
    th = L[5]
    kills = 0
    total = len(enemies)
    keys = [False, False, False]
    secrets_found = 0
    cruise = False
    frame = 0
    shoot_flash = 0
    fire_cd = 0
    hurt = 0
    acid = 0
    acid_t = 0
    moving = False
    fcell = (-1, -1)
    fframe = -99
    depths = [MAX_DIST] * RAYS
    message = L[0]
    msg_t = 60


def new_game(L):
    global health, armor, ammo, have, wp, tot_kills

    health = 100
    armor = 0
    if L >= 2:
        armor = 25
    ammo = [30 + 10 * L, 0, 0]
    have = [True, L >= 2, L >= 3, L >= 4]
    if L >= 2:
        ammo[1] = 8
    if L >= 4:
        ammo[2] = 4
    tot_kills = 0
    wp = 0
    for i in range(4):
        if have[i]:
            wp = i


# ======================= MENUS =======================
def draw_list(title, labels, sel, sub=""):
    cls()
    draw.set_color(150, 15, 15)
    draw.fill_rect(30, 18, 260, 3)
    draw.fill_rect(30, 52, 260, 3)
    draw.set_color(230, 40, 40)
    ctext(42, title)
    if sub != "":
        draw.set_color(150, 150, 150)
        ctext(70, sub)

    n = len(labels)
    step = 20
    y = 92
    if n > 8:
        step = 14
        y = 70
    elif n > 6:
        step = 17
        y = 76
    elif n <= 4:
        y = 100
    for i in range(n):
        if i == sel:
            draw.set_color(110, 15, 15)
            draw.fill_rect(40, y - step + 5, 240, step - 1)
            draw.set_color(255, 230, 60)
            draw.draw_text(48, y, "> " + labels[i])
        else:
            draw.set_color(210, 210, 210)
            draw.draw_text(48, y, "  " + labels[i])
        y += step
    flip()


def choose(title, labels, sel=0, sub=""):
    # returns the chosen index, or -1 if CLEAR was pressed
    flush()
    n = len(labels)
    draw_list(title, labels, sel, sub)
    while True:
        k = press()
        if k == K_UP:
            sel = (sel - 1) % n
            draw_list(title, labels, sel, sub)
        elif k == K_DOWN:
            sel = (sel + 1) % n
            draw_list(title, labels, sel, sub)
        elif k == K_ENTER:
            return sel
        elif k == K_BACK:
            return -1


def info_screen(lines, title):
    cls()
    draw.set_color(230, 40, 40)
    ctext(30, title)
    draw.set_color(230, 230, 230)
    y = 56
    for s in lines:
        draw.draw_text(20, y, s)
        y += 16
    draw.set_color(150, 150, 150)
    ctext(200, "PRESS ENTER")
    flip()
    flush()
    while True:
        k = press()
        if k == K_ENTER or k == K_BACK:
            return


def how_to():
    info_screen([
        "ARROWS  MOVE AND TURN",
        "2ND     SHOOT",
        "ENTER   USE: DOORS, SWITCHES,",
        "        SECRET WALLS (FACE IT)",
        "CLEAR   PAUSE",
        "THE OTHER KEYS ARE SET IN",
        "SETTINGS > CONTROLS",
        "MOVE STYLE CRUISE: UP TOGGLES",
        "AUTORUN SO YOU CAN TURN+SHOOT"], "HOW TO PLAY 1/2")
    info_screen([
        "GREEN=HEALTH  TEAL=ARMOR",
        "SILVER/ORANGE/RED=AMMO",
        "WHITE=NEW WEAPON",
        "YELLOW/RED/BLUE KEYS OPEN",
        "MATCHING DOORS",
        "GREEN PUDDLES BURN YOU",
        "FIREBALLS CAN BE DODGED",
        "STRAFE SIDEWAYS TO AVOID",
        "SOME WALLS HIDE SECRETS"], "HOW TO PLAY 2/2")


def capture_key(i):
    cls()
    draw.set_color(255, 230, 60)
    ctext(90, "PRESS A KEY FOR")
    ctext(110, KN[i])
    flip()
    flush()
    while True:
        k = press()
        if k and k != -1:
            KEYS[i] = k
            return


def controls_menu():
    sel = 0
    dirty = True
    flush()
    while True:
        if dirty:
            labels = []
            for i in range(4):
                labels.append(KN[i] + ": " + str(KEYS[i]))
            labels.append("RESET DEFAULTS")
            labels.append("BACK")
            draw_list("CONTROLS", labels, sel, "ENTER TO CHANGE")
            dirty = False
        k = press()
        if k == K_UP:
            sel = (sel - 1) % 6
            dirty = True
        elif k == K_DOWN:
            sel = (sel + 1) % 6
            dirty = True
        elif k == K_ENTER:
            if sel < 4:
                capture_key(sel)
            elif sel == 4:
                for i in range(4):
                    KEYS[i] = DEF_KEYS[i]
            else:
                return
            flush()
            dirty = True
        elif k == K_BACK:
            return


def onoff(v):
    if v:
        return "ON"
    return "OFF"


def settings_menu():
    global qual, diff, turn_i, show_map, bob_on, autofire
    global move_style, strafe

    sel = 0
    dirty = True
    flush()
    while True:
        if dirty:
            ms = "HOLD"
            if move_style == 1:
                ms = "CRUISE"
            sk = "TURN"
            if strafe:
                sk = "STRAFE"
            labels = [
                "QUALITY: " + QN[qual],
                "DIFFICULTY: " + DN[diff],
                "TURN SPEED: " + str(turn_i + 1),
                "MOVE STYLE: " + ms,
                "LEFT/RIGHT: " + sk,
                "MINIMAP: " + onoff(show_map),
                "WEAPON BOB: " + onoff(bob_on),
                "AUTO FIRE: " + onoff(autofire),
                "CONTROLS...",
                "BACK"
            ]
            draw_list("SETTINGS", labels, sel)
            dirty = False

        k = press()
        if k == K_UP:
            sel = (sel - 1) % 10
            dirty = True
        elif k == K_DOWN:
            sel = (sel + 1) % 10
            dirty = True
        elif k == K_BACK:
            return
        elif k == K_LEFT or k == K_RIGHT or k == K_ENTER:
            d = 1
            if k == K_LEFT:
                d = -1
            if sel == 0:
                qual = (qual + d) % 3
                apply_quality()
            elif sel == 1:
                diff = (diff + d) % 3
            elif sel == 2:
                turn_i = min(4, max(0, turn_i + d))
            elif sel == 3:
                move_style = 1 - move_style
            elif sel == 4:
                strafe = not strafe
            elif sel == 5:
                show_map = not show_map
            elif sel == 6:
                bob_on = not bob_on
            elif sel == 7:
                autofire = not autofire
            elif sel == 8:
                if k == K_ENTER:
                    controls_menu()
                    flush()
            elif k == K_ENTER:
                return
            dirty = True


def pause_menu():
    # returns True if the player wants to quit to the main menu
    c = choose("PAUSED", ["RESUME", "SETTINGS", "QUIT TO MENU"], 0)
    while c == 1:
        settings_menu()
        c = choose("PAUSED", ["RESUME", "SETTINGS", "QUIT TO MENU"], 1)
    return c == 2


def show_card(n):
    L = LEVELS[n]
    cls()
    draw.set_color(190, 20, 20)
    ctext(55, "LEVEL " + str(n + 1) + " OF " + str(len(LEVELS)))
    draw.set_color(255, 255, 255)
    ctext(80, L[0])
    draw.set_color(60, 200, 255)
    ctext(115, L[6])
    draw.set_color(150, 150, 150)
    ctext(190, "ENTER: BEGIN   CLEAR: MENU")
    flip()
    flush()
    while True:
        k = press()
        if k == K_ENTER:
            return True
        if k == K_BACK:
            return False


def level_done(n, last):
    cls()
    draw.set_color(40, 220, 50)
    if last:
        ctext(50, "YOU WIN!")
    else:
        ctext(50, "LEVEL COMPLETE")
    draw.set_color(255, 255, 255)
    ctext(85, "KILLS: " + str(kills) + "/" + str(total))
    ctext(103, "SECRETS: " + str(secrets_found) + "/" + str(secrets_total))
    ctext(121, "HEALTH: " + str(health))
    if last:
        ctext(145, "TOTAL KILLS: " + str(tot_kills))
    draw.set_color(150, 150, 150)
    ctext(185, "PRESS ENTER")
    flip()
    flush()
    while True:
        k = press()
        if k == K_ENTER or k == K_BACK:
            return

def play_level():
    global frame, shoot_flash, hurt, message, msg_t, moving, fire_cd
    global cruise, strafe, acid, acid_t, health

    prev = system.get_key(0)
    queued = 0
    cruise = False

    while True:
        key = system.get_key(0)
        new = key != prev
        prev = key

        if new and key == K_BACK:
            if pause_menu():
                return 0
            prev = system.get_key(0)
            continue

        if fire_cd > 0:
            fire_cd -= 1

        if new:
            if key == KEYS[0]:
                queued = 8
            elif key == KEYS[1]:
                use_action()
            elif key == KEYS[2]:
                next_weapon()
            elif key == KEYS[3]:
                strafe = not strafe
                if strafe:
                    set_msg("STRAFE MODE")
                else:
                    set_msg("TURN MODE")

        if queued > 0:
            queued -= 1
            if fire_cd == 0:
                queued = 0
                try_fire()
        elif key == KEYS[0] and fire_cd == 0 and WEAPONS[wp][5]:
            try_fire()

        # movement
        fwd = 0.0
        sd = 0.0
        trn = 0.0
        if move_style == 1:
            # cruise: UP toggles autorun, DOWN stops and backs up
            if new and key == K_UP:
                cruise = not cruise
            if key == K_DOWN:
                cruise = False
                fwd = -0.1
            elif cruise:
                fwd = 0.12
        else:
            cruise = False
            if key == K_UP:
                fwd = 0.12
            elif key == K_DOWN:
                fwd = -0.1
        if key == K_LEFT:
            if strafe:
                sd = -0.1
            else:
                trn = -TURN[turn_i]
        elif key == K_RIGHT:
            if strafe:
                sd = 0.1
            else:
                trn = TURN[turn_i]
        moving = fwd != 0 or sd != 0
        move_player(fwd, sd, trn)

        if autofire and fire_cd == 0 and frame % 3 == 0:
            w = WEAPONS[wp]
            if ammo[w[1]] > 0:
                t = targets(w[3] * 0.8)
                if t and (wp != 3 or t[0][0] > 2.5):
                    try_fire()

        frame += 1
        if shoot_flash > 0:
            shoot_flash -= 1
        if hurt > 0:
            hurt -= 1
        if msg_t > 0:
            msg_t -= 1
            if msg_t == 0:
                message = hint()

        update_enemies()
        update_projs()
        collect_pickups()

        # acid floors
        if HZ[int(py)][int(px)]:
            acid = 3
            acid_t += 1
            if acid_t >= 8:
                acid_t = 0
                health -= 2
                if health < 0:
                    health = 0
                set_msg("ACID BURNS!")
        elif acid > 0:
            acid -= 1

        if int(px) == EX and int(py) == EY:
            if boss_alive():
                set_msg("KILL THE BARON FIRST!")
            else:
                return 2

        if health <= 0:
            return 1

        draw_world()


def campaign(start):
    global health, armor, ammo, have, wp

    new_game(start)
    n = start
    while n < len(LEVELS):
        load_level(n)
        snap = (health, armor, ammo[:], have[:], wp)
        if not show_card(n):
            return

        while True:
            r = play_level()
            if r == 2:
                break
            if r == 0:
                return
            c = choose("YOU DIED", ["RETRY LEVEL", "MAIN MENU"], 0,
                       "KILLS " + str(kills) + "/" + str(total))
            if c != 0:
                return
            health = snap[0]
            armor = snap[1]
            ammo = snap[2][:]
            have = snap[3][:]
            wp = snap[4]
            load_level(n)

        last = n == len(LEVELS) - 1
        level_done(n, last)
        if not last:
            health = min(100, health + 20)
        n += 1


def main():
    sel = 0
    while True:
        c = choose("DOOM EVO", ["START GAME", "SELECT LEVEL", "SETTINGS",
                                "HOW TO PLAY", "QUIT"], sel,
                   "CALCULATOR EDITION")
        if c >= 0:
            sel = c
        if c == 0:
            campaign(0)
        elif c == 1:
            names = []
            for i in range(len(LEVELS)):
                names.append(str(i + 1) + ". " + LEVELS[i][0])
            names.append("BACK")
            s = choose("LEVEL SELECT", names, 0)
            if s >= 0 and s < len(LEVELS):
                campaign(s)
        elif c == 2:
            settings_menu()
        elif c == 3:
            how_to()
        elif c == 4:
            break

    cls()
    draw.set_color(255, 255, 255)
    ctext(105, "DOOM EVO EXIT")
    flip()


main()