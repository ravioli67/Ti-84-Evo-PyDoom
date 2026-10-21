import math
import ti_draw as draw
import ti_system as system

# ======================= CONSTANTS =======================
W = 319
H = 209
FOV = 1.05
MAX_DIST = 14.0
VIEW_TOP = 19
VIEW_BOT = 190
MID = 105
WALLH = 190      # wall height in pixels at distance 1
FLH = 95         # half of that: horizon to floor at distance 1

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

# quality: rays, strip width. Quality also sets how much detail is drawn.
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
LAMP = {5: (255, 220, 60), 6: (255, 70, 70), 7: (90, 160, 255)}

# projectile colours by shooter type (9 = player rocket)
PROJC = {0: (255, 150, 30), 3: (255, 60, 60), 4: (90, 255, 110),
         9: (255, 170, 40)}

# enemy stats:
# 0 name, 1 hp, 2 speed, 3 melee dmg, 4 ranged dmg, 5 range, 6 fire delay,
# 7 stop distance, 8 (unused), 9-10 (unused),
# 11 ranged kind (0 none, 1 hitscan, 2 fireball), 12 fireball speed,
# 13 pain chance %
ET = [
    ("IMP", 3, 0.030, 8, 7, 7, 80, 0.8, 0, 0, 0, 2, 0.09, 70),
    ("ZOMBIE", 3, 0.022, 4, 5, 8, 60, 3.0, 0, 0, 0, 1, 0.0, 60),
    ("DEMON", 10, 0.052, 14, 0, 0, 0, 0.8, 0, 0, 0, 0, 0.0, 40),
    ("CACO", 14, 0.025, 6, 10, 7, 75, 2.2, 0, 0, 0, 2, 0.11, 30),
    ("BARON", 45, 0.032, 18, 12, 9, 50, 2.5, 0, 0, 0, 2, 0.13, 10)
]

# enemy sprites: height (x wall height), width (x height), hover height,
# palette, parts. A part is (x0, y0, x1, y1, colour, tag) in percent of the
# sprite box (x: -50..50 from the centre, y: 0 top .. 100 feet).
# tags: 0 always, 1/2 leg A/B (walk), 3 arm (raises when attacking),
#       4 only while attacking, 5 eyes, 6 detail (skipped when far/low quality)
SPR = [
    # IMP
    (0.60, 0.72, 0.0,
     [(132, 80, 50), (88, 50, 30), (176, 116, 74), (255, 70, 40),
      (232, 222, 190), (60, 36, 22), (255, 150, 40)],
     [(-30, 66, -4, 100, 1, 1), (4, 66, 30, 100, 1, 2),
      (-34, 94, -2, 100, 4, 1), (2, 94, 34, 100, 4, 2),
      (-32, 28, 32, 70, 0, 0), (-16, 40, 16, 64, 2, 6),
      (-48, 30, -32, 60, 0, 3), (32, 30, 48, 60, 0, 3),
      (-50, 58, -32, 66, 4, 3), (32, 58, 50, 66, 4, 3),
      (-22, 4, 22, 32, 0, 0), (-14, 16, -5, 23, 3, 5), (5, 16, 14, 23, 3, 5),
      (-11, 25, 11, 29, 1, 6), (-28, -2, -18, 12, 5, 6),
      (18, -2, 28, 12, 5, 6), (-38, 26, -28, 36, 5, 6),
      (28, 26, 38, 36, 5, 6), (-12, 44, 12, 60, 6, 4)]),
    # ZOMBIE
    (0.66, 0.55, 0.0,
     [(72, 108, 72), (44, 66, 44), (204, 164, 132), (34, 34, 40),
      (96, 100, 108), (255, 220, 100), (30, 30, 30), (120, 96, 52)],
     [(-26, 64, -4, 96, 1, 1), (4, 64, 26, 96, 1, 2),
      (-30, 94, -2, 100, 6, 1), (2, 94, 30, 100, 6, 2),
      (-30, 28, 30, 66, 0, 0), (-30, 58, 30, 63, 7, 6),
      (-46, 30, -30, 62, 0, 0), (30, 30, 44, 52, 0, 3), (6, 36, 26, 50, 3, 3),
      (-16, 6, 16, 30, 2, 0), (-19, 1, 19, 13, 4, 0),
      (-9, 16, -3, 21, 1, 5), (3, 16, 9, 21, 1, 5), (12, 28, 22, 36, 5, 4)]),
    # DEMON
    (0.58, 1.0, 0.0,
     [(206, 112, 142), (142, 62, 92), (238, 152, 178), (255, 230, 60),
      (244, 242, 226), (226, 216, 182), (62, 12, 28)],
     [(-34, 70, -8, 100, 1, 1), (8, 70, 34, 100, 1, 2),
      (-46, 34, 46, 74, 0, 0), (-26, 48, 26, 70, 2, 6),
      (-52, 40, -42, 68, 1, 0), (42, 40, 52, 68, 1, 0),
      (-32, 2, 32, 44, 0, 0), (-22, 30, 22, 42, 6, 0),
      (-20, 30, 20, 34, 4, 0), (-18, 38, 18, 42, 4, 6),
      (-24, 12, -10, 20, 3, 5), (10, 12, 24, 20, 3, 5),
      (-26, 8, -8, 12, 1, 6), (8, 8, 26, 12, 1, 6),
      (-36, -4, -26, 8, 5, 6), (26, -4, 36, 8, 5, 6)]),
    # CACODEMON
    (0.58, 1.0, 0.2,
     [(190, 42, 42), (120, 22, 28), (228, 96, 84), (246, 242, 232),
      (92, 232, 62), (20, 20, 24), (250, 246, 222), (52, 6, 12),
      (232, 222, 190), (255, 170, 50)],
     [(-20, 0, 20, 12, 0, 0), (-34, 10, 34, 24, 0, 0),
      (-46, 22, 46, 72, 0, 0), (-38, 70, 38, 84, 0, 0),
      (-26, 82, 26, 100, 0, 0), (-44, 58, 44, 72, 1, 6),
      (-30, 12, -12, 24, 2, 6), (-18, 22, 18, 50, 3, 0),
      (-10, 28, 10, 46, 4, 0), (-4, 32, 4, 42, 5, 0),
      (-34, 58, 34, 76, 7, 0), (-30, 58, 30, 62, 6, 6),
      (-30, 72, 30, 76, 6, 6), (-16, -8, -8, 6, 8, 6), (8, -8, 16, 6, 8, 6),
      (-30, 50, 30, 80, 9, 4)]),
    # BARON
    (0.95, 0.78, 0.0,
     [(46, 142, 62), (26, 84, 38), (92, 192, 102), (255, 50, 30),
      (236, 230, 200), (46, 30, 26), (152, 102, 82), (126, 255, 142)],
     [(-30, 66, -6, 98, 6, 1), (6, 66, 30, 98, 6, 2),
      (-34, 94, -4, 100, 5, 1), (4, 94, 34, 100, 5, 2),
      (-34, 26, 34, 70, 0, 0), (-20, 32, 20, 50, 2, 6),
      (-34, 60, 34, 66, 1, 0), (-54, 28, -34, 62, 0, 3),
      (34, 28, 54, 62, 0, 3), (-58, 22, -32, 34, 1, 6),
      (32, 22, 58, 34, 1, 6), (-54, 56, -34, 68, 7, 4),
      (34, 56, 54, 68, 7, 4), (-18, 4, 18, 30, 0, 0),
      (-34, 0, -18, 8, 4, 0), (18, 0, 34, 8, 4, 0),
      (-38, -8, -30, 4, 4, 6), (30, -8, 38, 4, 4, 6),
      (-12, 14, -4, 20, 3, 5), (4, 14, 12, 20, 3, 5), (-8, 22, 8, 26, 1, 6)])
]

# weapons: name, ammo type, damage, hit radius, cooldown, auto, max targets, splash
WEAPONS = [
    ("PISTOL", 0, 2, 0.22, 9, False, 1, 0.0),
    ("SHOTGUN", 1, 9, 0.50, 24, False, 2, 0.0),
    ("CHAINGUN", 0, 2, 0.24, 3, True, 1, 0.0),
    ("ROCKET", 2, 14, 0.30, 36, False, 1, 1.6)
]

# first-person weapon art. A part is (x, y, w, h, colour, tag).
# tags: 0 always, 1 detail (MED+), 2 fine detail (HIGH), 3 shotgun pump,
#       5/6 chaingun barrels (the lit barrel alternates while firing)
WPAL = [
    [(58, 60, 68), (128, 132, 146), (20, 20, 24), (214, 170, 134),
     (168, 124, 94), (72, 82, 112)],
    [(58, 60, 68), (128, 132, 146), (20, 20, 24), (214, 170, 134),
     (168, 124, 94), (88, 58, 32), (122, 82, 48), (70, 80, 110)],
    [(58, 60, 68), (128, 132, 146), (20, 20, 24), (214, 170, 134),
     (168, 124, 94), (98, 100, 112), (176, 142, 50), (70, 82, 70)],
    [(58, 60, 68), (128, 132, 146), (20, 20, 24), (214, 170, 134),
     (168, 124, 94), (84, 98, 66), (116, 134, 92), (210, 60, 40),
     (70, 82, 110)]
]
WPAR = [
    # pistol
    [(154, 122, 12, 8, 1, 0), (150, 130, 20, 16, 0, 0),
     (150, 130, 5, 16, 1, 1), (146, 146, 28, 28, 0, 0),
     (146, 146, 6, 28, 1, 1), (158, 148, 4, 6, 2, 2),
     (142, 170, 36, 20, 2, 0), (136, 176, 48, 16, 3, 0),
     (136, 176, 48, 4, 4, 1), (132, 184, 56, 10, 5, 0)],
    # shotgun
    [(154, 106, 12, 8, 2, 0), (150, 114, 20, 48, 0, 0),
     (150, 114, 5, 48, 1, 1), (142, 148, 36, 8, 0, 0),
     (140, 152, 40, 22, 5, 3), (140, 152, 40, 4, 6, 3),
     (144, 160, 32, 2, 2, 2), (146, 172, 28, 20, 0, 0),
     (146, 172, 6, 20, 1, 1), (126, 156, 22, 22, 3, 0),
     (126, 156, 22, 5, 4, 1), (170, 176, 26, 16, 3, 0),
     (120, 184, 80, 10, 7, 0)],
    # chaingun
    [(136, 108, 12, 54, 5, 5), (154, 102, 12, 60, 5, 6),
     (172, 108, 12, 54, 5, 5), (132, 140, 56, 6, 2, 0),
     (128, 158, 64, 30, 7, 0), (128, 158, 64, 5, 1, 1),
     (192, 152, 18, 30, 2, 0), (190, 158, 10, 6, 6, 1),
     (190, 168, 10, 6, 6, 1), (144, 176, 32, 16, 3, 0)],
    # rocket launcher
    [(138, 98, 44, 14, 2, 0), (146, 102, 28, 8, 0, 1),
     (152, 100, 16, 8, 7, 0), (134, 110, 52, 58, 5, 0),
     (134, 110, 10, 58, 6, 1), (178, 104, 8, 24, 2, 1),
     (126, 152, 26, 24, 3, 0), (168, 152, 26, 24, 3, 0),
     (150, 166, 20, 24, 2, 0), (118, 176, 84, 14, 8, 0)]
]
WFL = [(160, 122), (160, 104), (160, 98), (160, 94)]

# ======================= LEVELS =======================
# map chars: 0 floor, 1-4 walls, ~ acid, E exit
#   Y/R/B yellow/red/blue door   G gate (opened by a switch)   W switch
#   a/b/c/d secret wall that looks like wall 1/2/3/4 (press USE on it)
# level = name, map, (x, y, angle), enemies (x, y, type),
#         pickups (x, y, type), theme (ceiling, far floor, near floor),
#         objective
# pickups: H health, V armor, A bullets, B shells, X rockets,
#          y/r/b keys, S shotgun, C chaingun, R rocket launcher
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
     ((34, 38, 56), (44, 36, 30), (74, 60, 50)),
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
     ((26, 48, 34), (34, 46, 30), (58, 78, 44)),
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
     ((20, 30, 52), (30, 34, 46), (56, 64, 82)),
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
     ((52, 16, 14), (50, 20, 16), (92, 40, 28)),
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
     ((44, 12, 12), (40, 16, 12), (84, 34, 24)),
     "KILL THE BARON, REACH THE EXIT")
]

# ======================= STATE =======================
qual = 1
detail = 1
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
hz = MID
trav = 0.0
health = 100
armor = 0
ammo = [30, 0, 0]
have = [True, False, False, False]
wp = 0
wnew = 0
wsw = 0
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
boom = 0
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
fx = []
th = ((34, 38, 56), (44, 36, 30), (74, 60, 50))
MM_RUNS = []
MMC = 4
MMX = 268


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


def setc(c, k=100):
    # set the draw colour to c scaled by k percent
    r = c[0] * k // 100
    g = c[1] * k // 100
    b = c[2] * k // 100
    if r > 255:
        r = 255
    if g > 255:
        g = 255
    if b > 255:
        b = 255
    draw.set_color(r, g, b)


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
    global RAYS, STRIP, COSO, SINO, depths, detail
    RAYS = QUAL[qual][0]
    STRIP = QUAL[qual][1]
    detail = qual
    COSO = []
    SINO = []
    for i in range(RAYS):
        a = -FOV / 2 + FOV * (i + 0.5) / RAYS
        COSO.append(math.cos(a))
        SINO.append(math.sin(a))
    depths = [MAX_DIST] * RAYS


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
    # DDA raycast from the player. (dx, dy) must be a unit vector.
    # Returns (distance, side, tile id, position along the wall 0..1)
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


def project(x, y):
    # screen x and perpendicular distance of a point, or None if hidden
    # (used for small things: the centre column decides if they are visible)
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


def proj_raw(x, y):
    # like project() but without the wall test and with a wider angle,
    # so big sprites can peek in from the screen edge
    dx = x - px
    dy = y - py
    pd = dx * ca + dy * sa
    if pd < 0.25:
        return None
    dl = math.atan2(dy * ca - dx * sa, pd)
    if dl > 1.0 or dl < -1.0:
        return None
    return pd, int((dl / FOV + 0.5) * W)


def vis_span(xl, xr, pd):
    # the part of the pixel range xl..xr that is not hidden behind a wall
    il = xl // STRIP
    ir = xr // STRIP
    if ir < 0 or il >= RAYS:
        return None
    if il < 0:
        il = 0
    if ir >= RAYS:
        ir = RAYS - 1
    a = -1
    b = -1
    lim = pd - 0.15
    for i in range(il, ir + 1):
        if depths[i] >= lim:
            if a < 0:
                a = i
            b = i
    if a < 0:
        return None
    l = a * STRIP
    r = b * STRIP + STRIP
    if l < xl:
        l = xl
    if r > xr:
        r = xr
    return (l, r)


# ======================= DRAWING =======================
def cls():
    draw.set_color(0, 0, 0)
    draw.fill_rect(0, 0, W, H)


def ctext(y, s):
    x = (W - len(s) * 8) // 2
    if x < 0:
        x = 0
    draw.draw_text(x, y, s)


def cfill(x, y, w, h, v):
    # fill_rect clipped to the visible span v and the 3D view area
    x1 = x + w
    if x < v[0]:
        x = v[0]
    if x1 > v[1]:
        x1 = v[1]
    y1 = y + h
    if y < VIEW_TOP:
        y = VIEW_TOP
    if y1 > VIEW_BOT:
        y1 = VIEW_BOT
    if x1 > x and y1 > y:
        draw.fill_rect(x, y, x1 - x, y1 - y)


def rv(x, y, h):
    # one wall strip piece, clipped to the 3D view area
    y1 = y + h
    if y < VIEW_TOP:
        y = VIEW_TOP
    if y1 > VIEW_BOT:
        y1 = VIEW_BOT
    if y1 > y:
        draw.fill_rect(x, y, STRIP, y1 - y)


def draw_flat():
    # ceiling and floor with a depth gradient
    c = th[0]
    f1 = th[1]
    f2 = th[2]
    if detail == 0:
        setc(c)
        draw.fill_rect(0, 0, W, hz)
        setc(f1)
        draw.fill_rect(0, hz, W, H - hz)
        setc(f2)
        draw.fill_rect(0, 150 + hz - MID, W, 40)
        return

    # ceiling bands: lighter overhead, darker toward the horizon
    setc(c, 125)
    draw.fill_rect(0, 0, W, 34)
    setc(c, 105)
    draw.fill_rect(0, 34, W, 36)
    setc(c, 82)
    draw.fill_rect(0, 70, W, hz - 70)

    # floor bands, one per distance
    y = hz
    ds = (9.0, 5.0, 3.2, 2.2, 1.5, 0.0)
    for k in range(6):
        if k < 3:
            setc(f1, 70 + k * 14)
        else:
            setc(f2, 82 + (k - 3) * 14)
        y2 = VIEW_BOT
        if ds[k] > 0:
            y2 = hz + int(FLH / ds[k])
        if k == 0:
            y2 = hz + 11
        if y2 > VIEW_BOT:
            y2 = VIEW_BOT
        if y2 > y:
            draw.fill_rect(0, y, W, y2 - y)
            y = y2
    if y < VIEW_BOT:
        setc(f2, 118)
        draw.fill_rect(0, y, W, VIEW_BOT - y)

    if detail < 2:
        return

    # stripes that slide toward you as you walk: floor tiles + ceiling lights
    t2 = trav % 2.0
    for j in range(0, 8, 2):
        a = j - t2
        b = a + 1.0
        if b <= 0.5:
            continue
        if a < 0.5:
            a = 0.5
        y1 = hz + int(FLH / b)
        y2 = hz + int(FLH / a)
        if y2 > VIEW_BOT:
            y2 = VIEW_BOT
        if y2 > y1:
            setc(f2, 128 - j * 4)
            draw.fill_rect(0, y1, W, y2 - y1)
        y1 = hz - int(FLH / a)
        y2 = hz - int(FLH / b)
        if y1 < VIEW_TOP:
            y1 = VIEW_TOP
        if y1 > y2:
            continue
        setc(c, 150 - j * 6)
        draw.fill_rect(0, y1, W, y2 - y1)


def wall_strip(x, top, h, t, sh, f):
    # one wall column: flat colour, or a textured pattern when close
    if t > 10:
        t -= 10
    wc = WRGB[t]
    r = sh * wc[0] // 100
    g = sh * wc[1] // 100
    b = sh * wc[2] // 100
    if r > 255:
        r = 255
    if g > 255:
        g = 255
    if b > 255:
        b = 255

    if detail == 0 or h < 24:
        draw.set_color(r, g, b)
        rv(x, top, h)
        return

    if t == 1:
        # bricks: mortar underneath, offset rows of bricks on top
        n = 2
        if detail == 2 and h >= 48:
            n = 4
        draw.set_color(r * 45 // 100, g * 45 // 100, b * 45 // 100)
        rv(x, top, h)
        for k in range(n):
            y0 = top + h * k // n
            y1 = top + h * (k + 1) // n
            u = f * 4 + 0.5 * (k & 1)
            iu = int(u)
            if u - iu < 0.1:
                continue
            m = 94 + ((iu * 7 + k * 5) % 4) * 4
            draw.set_color(r * m // 100, g * m // 100, b * m // 100)
            rv(x, y0 + 1, y1 - y0 - 1)
    elif t == 2:
        # tech panels with a groove and a status light
        if f < 0.06 or f > 0.94:
            draw.set_color(r * 55 // 100, g * 55 // 100, b * 55 // 100)
            rv(x, top, h)
            return
        draw.set_color(r, g, b)
        rv(x, top, h)
        if 0.1 < f < 0.9:
            setc((r, g, b), 125)
            rv(x, top + h * 18 // 100, h * 64 // 100)
            draw.set_color(r * 55 // 100, g * 55 // 100, b * 55 // 100)
            rv(x, top + h * 49 // 100, max(1, h // 40))
            if detail == 2 and 0.46 < f < 0.54:
                draw.set_color(90, 255, 230)
                rv(x, top + h * 26 // 100, max(2, h // 18))
    elif t == 3:
        # cracked rock with glowing veins
        m = 100 - (int(f * 10) % 3) * 12
        draw.set_color(r * m // 100, g * m // 100, b * m // 100)
        rv(x, top, h)
        if detail == 2:
            draw.set_color(r * 55 // 100, g * 55 // 100, b * 55 // 100)
            rv(x, top + h * 78 // 100, h * 22 // 100)
        if int(f * 16) % 7 == 0:
            draw.set_color(255, 110, 30)
            rv(x, top + h * 20 // 100, h * 50 // 100)
    elif t == 4:
        # stone dripping slime
        draw.set_color(r, g, b)
        rv(x, top, h)
        dr = (int(f * 12) % 3 + 1) * h // 10
        draw.set_color(r * 130 // 100, min(255, g + 90), b * 130 // 100)
        rv(x, top, dr)
        if detail == 2:
            draw.set_color(r * 55 // 100, g * 55 // 100, b * 55 // 100)
            rv(x, top + h * 82 // 100, h * 18 // 100)
    elif t >= 5 and t <= 7:
        # door: frame, centre bar, lamp and handle
        if f < 0.07 or f > 0.93:
            draw.set_color(r * 40 // 100, g * 40 // 100, b * 40 // 100)
            rv(x, top, h)
            return
        draw.set_color(r, g, b)
        rv(x, top, h)
        setc((r, g, b), 150)
        rv(x, top + h * 45 // 100, max(2, h // 14))
        draw.set_color(LAMP[t][0], LAMP[t][1], LAMP[t][2])
        rv(x, top + h * 8 // 100, max(2, h // 16))
        if detail == 2 and 0.78 < f < 0.86:
            draw.set_color(230, 230, 230)
            rv(x, top + h * 48 // 100, h // 10)
    elif t == 8:
        # iron gate
        if (f * 8) % 1.0 < 0.5:
            draw.set_color(r * 150 // 100, g * 150 // 100, b * 150 // 100)
        else:
            draw.set_color(r * 40 // 100, g * 40 // 100, b * 40 // 100)
        rv(x, top, h)
        if detail == 2:
            draw.set_color(r * 150 // 100, g * 150 // 100, b * 150 // 100)
            rv(x, top + h * 28 // 100, max(1, h // 24))
            rv(x, top + h * 68 // 100, max(1, h // 24))
    else:
        # switch: wall with a dark plate and a lamp
        draw.set_color(r, g, b)
        rv(x, top, h)
        if 0.3 < f < 0.7:
            draw.set_color(30, 30, 34)
            rv(x, top + h * 30 // 100, h * 40 // 100)
            if t == 9:
                draw.set_color(255, 60, 60)
            else:
                draw.set_color(60, 255, 90)
            rv(x, top + h * 42 // 100, h * 16 // 100)


def draw_world():
    draw_flat()

    lb = shoot_flash
    if boom > lb:
        lb = boom
    lb = lb * 12

    for i in range(RAYS):
        co = COSO[i]
        so = SINO[i]
        d, side, t, f = cast(ca * co - sa * so, sa * co + ca * so)

        d *= co
        if d < 0.1:
            d = 0.1
        depths[i] = d

        h = int(WALLH / d)
        if h > 420:
            h = 420
        top = hz - h // 2

        sh = int(190 / (1 + d * 0.18))
        if side:
            sh = sh * 18 // 25
        if f < 0.05 or f > 0.95:
            sh = sh * 2 // 3
        if lb and d < 8:
            sh += int(lb * (8 - d) / 8)
        if sh < 18:
            sh = 18
        elif sh > 235:
            sh = 235

        wall_strip(i * STRIP, top, h, t, sh, f)

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


def draw_acid():
    # bubbling green puddles on the floor
    for hp in HZL:
        r = project(hp[0], hp[1])
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
        y1 = hz + int(FLH / (pd + 0.5))
        far = pd - 0.5
        if far < 0.3:
            far = 0.3
        y2 = hz + int(FLH / far)
        if y2 > VIEW_BOT - 1:
            y2 = VIEW_BOT - 1
        if y2 - y1 < 2:
            continue
        draw.set_color(46, 160, 34)
        draw.fill_rect(sx - w // 2, y1, w, y2 - y1)
        if detail > 0:
            draw.set_color(110, 240, 70)
            ph = (frame // 3 + int(hp[0] * 3)) % 4
            draw.fill_rect(sx - w // 2 + w * (ph + 1) // 6, y1 + (y2 - y1) // 3,
                           max(2, w // 10), max(1, (y2 - y1) // 4))


def draw_exit():
    r = project(EX + 0.5, EY + 0.5)
    if r is None:
        return
    pd = r[0]
    sx = r[1]
    h = int(0.7 * WALLH / pd)
    w = int(24 / pd)
    if w < 4:
        w = 4
    fy = hz + int(FLH / pd)
    top = fy - h
    if boss_alive():
        c = (170, 40, 40)
    else:
        c = (30, 230, 60)
    # glowing doorway
    setc(c, 45)
    cfill(sx - w, top - 2, w * 2, h + 2, (0, W))
    setc(c)
    cfill(sx - w * 2 // 3, top, w * 4 // 3, h, (0, W))
    if not boss_alive():
        draw.set_color(220, 255, 230)
        cfill(sx - w // 5, top + h // 5, max(2, w * 2 // 5), h * 3 // 5, (0, W))


def draw_pickups():
    for idx in range(len(pickups)):
        p = pickups[idx]
        if not p[3]:
            continue
        r = project(p[0], p[1])
        if r is None:
            continue
        pd = r[0]
        sx = r[1]
        u = WALLH / pd
        k = p[2]
        hh = int(u * 0.13)
        if hh < 3:
            hh = 3
        ww = hh * 3 // 2
        fy = hz + int(FLH / pd)
        if k in "ybrSCR":
            fy -= int(u * 0.05) + int(math.sin((frame + idx * 5) * 0.2) * u * 0.02)
        x0 = sx - ww // 2
        y0 = fy - hh
        v = (0, W)

        if k == "H":
            draw.set_color(36, 170, 70)
            cfill(x0, y0, ww, hh, v)
            draw.set_color(240, 240, 240)
            cfill(x0 + ww * 38 // 100, y0 + hh * 15 // 100,
                  max(1, ww * 24 // 100), hh * 70 // 100, v)
            cfill(x0 + ww * 18 // 100, y0 + hh * 38 // 100,
                  ww * 64 // 100, max(1, hh * 24 // 100), v)
        elif k == "V":
            draw.set_color(40, 150, 140)
            cfill(x0, y0 + hh // 4, ww, hh * 3 // 4, v)
            draw.set_color(70, 205, 190)
            cfill(x0 - ww // 8, y0, ww * 5 // 4, hh // 3, v)
            draw.set_color(25, 100, 95)
            cfill(x0 + ww * 40 // 100, y0 + hh // 3, max(1, ww // 5),
                  hh * 2 // 3, v)
        elif k == "A":
            draw.set_color(150, 150, 160)
            cfill(x0, y0 + hh // 3, ww, hh * 2 // 3, v)
            draw.set_color(230, 190, 60)
            cfill(x0 + ww // 8, y0, ww * 3 // 4, hh // 3, v)
        elif k == "B":
            draw.set_color(210, 50, 40)
            cfill(x0 + ww // 6, y0, ww // 3, hh, v)
            cfill(x0 + ww * 55 // 100, y0, ww // 3, hh, v)
            draw.set_color(230, 190, 60)
            cfill(x0 + ww // 6, y0 + hh * 3 // 4, ww // 3, max(1, hh // 4), v)
            cfill(x0 + ww * 55 // 100, y0 + hh * 3 // 4, ww // 3,
                  max(1, hh // 4), v)
        elif k == "X":
            draw.set_color(200, 60, 50)
            cfill(x0 + ww * 35 // 100, y0, ww * 30 // 100, hh, v)
            draw.set_color(160, 160, 170)
            cfill(x0 + ww * 35 // 100, y0 - hh // 5, ww * 30 // 100,
                  max(1, hh // 5), v)
            draw.set_color(90, 40, 40)
            cfill(x0 + ww * 20 // 100, y0 + hh * 3 // 4, ww * 60 // 100,
                  max(1, hh // 4), v)
        elif k == "y" or k == "r" or k == "b":
            if k == "y":
                draw.set_color(255, 220, 50)
            elif k == "r":
                draw.set_color(255, 50, 50)
            else:
                draw.set_color(80, 150, 255)
            q = hh * 55 // 100
            cfill(x0, y0, q, q, v)
            cfill(x0 + q * 7 // 10, y0 + q // 3, ww * 70 // 100,
                  max(1, q // 3), v)
            cfill(x0 + ww * 80 // 100, y0 + q // 3, max(1, q // 3),
                  q * 7 // 10, v)
            draw.set_color(20, 20, 24)
            cfill(x0 + q // 3, y0 + q // 3, max(1, q // 3), max(1, q // 3), v)
        else:
            # weapon pickups: a gun silhouette
            draw.set_color(48, 48, 56)
            cfill(x0 - ww // 4, y0 + hh // 3, ww * 3 // 2, hh // 3, v)
            cfill(x0 + ww // 2, y0 + hh * 2 // 3, ww // 4, hh // 3, v)
            draw.set_color(190, 190, 200)
            cfill(x0 - ww // 4, y0 + hh // 3, ww * 3 // 2, max(1, hh // 9), v)
            if k == "R":
                draw.set_color(210, 60, 40)
                cfill(x0 - ww // 4, y0 + hh // 4, max(2, ww // 5), hh // 2, v)
            elif k == "S":
                draw.set_color(122, 82, 48)
                cfill(x0 + ww // 8, y0 + hh * 45 // 100, ww // 3,
                      max(1, hh // 4), v)


def draw_enemies():
    vis = []
    for i in range(len(enemies)):
        e = enemies[i]
        r = proj_raw(e[0], e[1])
        if r is None:
            continue
        if e[2] <= 0 and e[10] <= 0:
            draw_corpse(e, r[0], r[1])
        else:
            vis.append((r[0], i, r[1]))

    vis.sort()
    for n in range(len(vis) - 1, -1, -1):
        draw_enemy(enemies[vis[n][1]], vis[n][1], vis[n][0], vis[n][2])


def draw_corpse(e, pd, sx):
    T = SPR[e[6]]
    hs = int(T[0] * WALLH / pd)
    if hs > 420:
        hs = 420
    ws = int(hs * T[1])
    fy = hz + int(FLH / pd)
    v = vis_span(sx - ws * 6 // 10, sx + ws * 6 // 10, pd)
    if v is None:
        return
    ph = max(2, hs // 14)
    draw.set_color(110, 10, 10)
    cfill(sx - ws * 6 // 10, fy - ph, ws * 12 // 10, ph, v)
    bh = max(2, hs // 9)
    setc(T[3][1], 90)
    cfill(sx - ws * 45 // 100, fy - bh - ph // 2, ws * 9 // 10, bh, v)
    if detail > 0:
        setc(T[3][0], 80)
        cfill(sx - ws * 20 // 100, fy - bh - ph // 2, ws * 25 // 100,
              max(1, bh // 2), v)


def draw_enemy(e, i, pd, sx):
    T = SPR[e[6]]
    pal = T[3]
    hs = int(T[0] * WALLH / pd)
    if hs > 420:
        hs = 420
    if hs < 4:
        hs = 4
    ws = int(hs * T[1])
    gy = hz + int(FLH / pd)
    fy = gy
    dying = e[2] <= 0
    if T[2] > 0:
        fy -= int(T[2] * WALLH / pd)
        if not dying:
            fy += int(math.sin((frame + i * 7) * 0.2) * hs * 0.05)
    if dying:
        k = e[10]
        hs = hs * (k + 3) // 11
        if T[2] > 0:
            fy = gy - (fy_hover(T, pd) * k // 8)
    top = fy - hs

    v = vis_span(sx - ws // 2 - 2, sx + ws // 2 + 2, pd)
    if v is None:
        return

    # shadow under the feet
    if not dying and detail > 0:
        setc(th[1], 45)
        cfill(sx - ws * 4 // 10, gy - max(1, hs // 22), ws * 8 // 10,
              max(2, hs // 14), v)

    if e[5] > 0:
        pal = []
        for c in T[3]:
            pal.append(((c[0] + 255) // 2, (c[1] + 200) // 2, (c[2] + 200) // 2))

    att = e[7] > 0 or e[3] >= 28
    moving_now = e[11] == 1 and not dying
    ph = ((frame // 4) + i) & 1
    lift = hs * 6 // 100
    arm = hs * 14 // 100
    far = hs < 30 or detail == 0

    for p in T[4]:
        tag = p[5]
        dy = 0
        if tag == 0:
            pass
        elif tag == 1:
            if moving_now and ph == 0:
                dy = -lift
        elif tag == 2:
            if moving_now and ph == 1:
                dy = -lift
        elif tag == 3:
            if att:
                dy = -arm
        elif tag == 4:
            if not att:
                continue
        elif tag == 6:
            if far:
                continue
        x0 = sx + p[0] * ws // 100
        x1 = sx + p[2] * ws // 100
        y0 = top + p[1] * hs // 100 + dy
        y1 = top + p[3] * hs // 100 + dy
        if x1 <= x0:
            x1 = x0 + 1
        if y1 <= y0:
            y1 = y0 + 1
        c = pal[p[4]]
        draw.set_color(c[0], c[1], c[2])
        cfill(x0, y0, x1 - x0, y1 - y0, v)

    # blood spray when hit
    if e[5] > 0 and detail > 0:
        draw.set_color(170, 10, 10)
        o = (e[5] * 5 + i * 3) % 7
        q = max(2, hs // 14)
        cfill(sx - ws // 4 + o * ws // 20, top + hs * 35 // 100, q, q, v)
        cfill(sx + ws // 6 - o * ws // 24, top + hs * 50 // 100, q, q, v)
        cfill(sx - ws // 10 + o * ws // 30, top + hs * 25 // 100, q, q, v)


def fy_hover(T, pd):
    return int(T[2] * WALLH / pd)


def draw_projs():
    for p in projs:
        r = project(p[0], p[1])
        if r is None:
            continue
        u = WALLH / r[0]
        s = int(u * 0.07)
        if s < 3:
            s = 3
        elif s > 30:
            s = 30
        if (frame & 1) == 1:
            s += 1
        c = PROJC[p[5]]
        cy = hz + int(u * 0.15)
        if p[5] == 9:
            setc(c)
            draw.fill_rect(r[1] - s, cy - s, s * 2, s * 2)
            draw.set_color(70, 70, 80)
            draw.fill_rect(r[1] - s // 2, cy - s // 2, s, s)
        else:
            setc(c, 55)
            draw.fill_rect(r[1] - s, cy - s, s * 2, s * 2)
            setc(c)
            draw.fill_rect(r[1] - s * 2 // 3, cy - s * 2 // 3, s * 4 // 3,
                           s * 4 // 3)
            draw.set_color(255, 255, 210)
            q = max(1, s // 2)
            draw.fill_rect(r[1] - q // 2, cy - q // 2, q, q)

    # explosions
    for q in fx:
        r = project(q[0], q[1])
        if r is None:
            continue
        u = WALLH / r[0]
        s = int(u * (0.06 + (6 - q[2]) * 0.05))
        if s < 3:
            s = 3
        cy = hz + int(u * 0.1)
        sx = r[1]
        draw.set_color(255, 110, 20)
        draw.fill_rect(sx - s * 2, cy - s * 2, s * 4, s * 4)
        draw.set_color(255, 200, 60)
        draw.fill_rect(sx - s * 3 // 2, cy - s * 3 // 2, s * 3, s * 3)
        draw.set_color(255, 255, 220)
        draw.fill_rect(sx - s, cy - s, s * 2, s * 2)


def draw_weapon():
    bx = 0
    by = 0
    if bob_on and moving:
        s = math.sin(frame * 0.4)
        bx = int(s * 5)
        by = int(abs(s) * 4)
    by += shoot_flash * 3
    if wsw > 0:
        by += (5 - abs(wsw - 5)) * 14

    w = WEAPONS[wp]
    pal = WPAL[wp]
    pump = 0
    if wp == 1 and fire_cd > 4:
        pump = min(fire_cd - 4, 24 - fire_cd)
        if pump < 0:
            pump = 0

    if shoot_flash > 0 and wsw == 0:
        fx0 = WFL[wp][0] + bx
        fy0 = WFL[wp][1] + by
        if wp == 2:
            fx0 += 10 * ((frame & 1) * 2 - 1)
        if detail == 0:
            draw.set_color(255, 220, 90)
            draw.fill_rect(fx0 - 14, fy0 - 10, 28, 24)
        else:
            draw.set_color(255, 140, 30)
            draw.fill_rect(fx0 - 22, fy0 - 14, 44, 30)
            draw.set_color(255, 220, 90)
            draw.fill_rect(fx0 - 14, fy0 - 10, 28, 22)
            draw.set_color(255, 255, 225)
            draw.fill_rect(fx0 - 7, fy0 - 6, 14, 12)
            if detail == 2:
                draw.set_color(255, 200, 70)
                draw.fill_rect(fx0 - 32, fy0 - 1, 64, 4)
                draw.fill_rect(fx0 - 2, fy0 - 24, 4, 50)

    spin = shoot_flash > 0 and wp == 2
    for t in WPAR[wp]:
        tag = t[5]
        if tag == 1 and detail < 1:
            continue
        if tag == 2 and detail < 2:
            continue
        dy = 0
        if tag == 3:
            dy = pump
        c = pal[t[4]]
        if tag == 5 or tag == 6:
            if spin and (frame & 1) == tag - 5:
                c = pal[1]
        draw.set_color(c[0], c[1], c[2])
        draw.fill_rect(t[0] + bx, t[1] + by + dy, t[2], t[3])

    # smoke after a shot
    if detail > 0 and wsw == 0 and (wp == 0 or wp == 1 or wp == 3):
        age = w[4] - fire_cd
        if fire_cd > 0 and age >= 3 and age < 12:
            draw.set_color(150, 150, 155)
            draw.fill_rect(WFL[wp][0] - 5 + bx, WFL[wp][1] + by - age * 2, 10, 6)

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


# ======================= GAME LOGIC =======================
def move_player(forward, side, turn):
    global px, py, angle, ca, sa, trav

    if turn != 0:
        angle += turn
        ca = math.cos(angle)
        sa = math.sin(angle)

    if forward != 0 or side != 0:
        ox = px
        oy = py
        dx = ca * forward - sa * side
        dy = sa * forward + ca * side
        if can_stand(px + dx, py):
            px += dx
        if can_stand(px, py + dy):
            py += dy
        trav += (px - ox) * ca + (py - oy) * sa


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
        e[10] = 8
        set_msg(ET[e[6]][0] + " DOWN")
        if e[6] == 1:
            # zombies drop their ammo
            pickups.append([e[0], e[1], "A", True])
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


def explode(x, y):
    global boom

    boom = 4
    fx.append([x, y, 6])
    for e in enemies:
        if e[2] <= 0:
            continue
        dx = e[0] - x
        dy = e[1] - y
        dd = math.sqrt(dx * dx + dy * dy)
        if dd < 1.6:
            dmg = int(14 * (1 - dd / 1.6))
            if dmg < 1:
                dmg = 1
            hit_enemy(e, dmg)
    dx = px - x
    dy = py - y
    if dx * dx + dy * dy < 1.7:
        hurt_player(6)
    else:
        set_msg("BOOM!")


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
    global wnew, wsw, fire_cd
    if wsw > 0:
        return
    for i in range(1, 5):
        n = (wp + i) % 4
        if have[n]:
            wnew = n
            wsw = 10
            fire_cd = 12
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

    if w[7] > 0:
        # rocket: a real projectile that explodes on a wall or demon
        projs.append([px + ca * 0.35, py + sa * 0.35, ca * 0.4, sa * 0.4,
                      0, 9, 45])
    else:
        hits = targets(w[3])
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
        if p[5] == 9:
            # the player's rocket
            hit = False
            for e in enemies:
                if e[2] > 0:
                    if -0.45 < e[0] - p[0] < 0.45:
                        if -0.45 < e[1] - p[1] < 0.45:
                            hit = True
                            break
            if hit or p[6] <= 0 or solid(p[0], p[1]):
                explode(p[0] - p[2] * 0.5, p[1] - p[3] * 0.5)
                projs.pop(i)
            continue
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
            if e[10] > 0:
                e[10] -= 1
            continue

        if e[5] > 0:
            e[5] -= 1
        if e[7] > 0:
            e[7] -= 1
        e[11] = 0

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
            e[11] = 1

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
    global projs, fx, th, px, py, angle, ca, sa, kills, total, keys, cruise
    global doors_closed, gates_closed, secrets_found, secrets_total
    global frame, shoot_flash, boom, fire_cd, hurt, acid, acid_t, moving
    global depths, hz, trav, wsw
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
            hzf = False
            if c == "0":
                v = 0
            elif c == "E":
                v = 0
                EX = x
                EY = y
            elif c == "~":
                v = 0
                hzf = True
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
            hrow.append(hzf)
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

    # enemy: x, y, hp, attack timer, awake, hurt flash, type, fire flash,
    #        sees player, stagger, death timer, walking
    enemies = []
    for s in L[3]:
        enemies.append([s[0], s[1], ET[s[2]][1], 0, False, 0, s[2], 0,
                        False, 0, 0, 0])
    pickups = []
    for s in L[4]:
        pickups.append([s[0], s[1], s[2], True])
    projs = []
    fx = []

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
    boom = 0
    fire_cd = 0
    wsw = 0
    hurt = 0
    acid = 0
    acid_t = 0
    moving = False
    hz = MID
    trav = 0.0
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
        "GREEN CROSS=HEALTH TEAL=ARMOR",
        "BOXES=AMMO  GUNS=NEW WEAPONS",
        "KEYS OPEN MATCHING DOORS",
        "GREEN PUDDLES BURN YOU",
        "FIREBALLS CAN BE DODGED",
        "ROCKETS FLY AND EXPLODE:",
        "DON'T FIRE AT NEARBY WALLS",
        "ZOMBIES DROP AMMO",
        "QUALITY SETS THE DETAIL LEVEL"], "HOW TO PLAY 2/2")


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
                "VIEW BOB: " + onoff(bob_on),
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


# ======================= MAIN LOOPS =======================
def play_level():
    # returns 0 = quit to menu, 1 = died, 2 = reached exit
    global frame, shoot_flash, boom, hurt, message, msg_t, moving, fire_cd
    global cruise, strafe, acid, acid_t, health, hz, wsw, wp

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

        # weapon switch animation: lower, swap, raise
        if wsw > 0:
            wsw -= 1
            if wsw == 5:
                wp = wnew
                set_msg(WEAPONS[wp][0])

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
            if fire_cd == 0 and wsw == 0:
                queued = 0
                try_fire()
        elif key == KEYS[0] and fire_cd == 0 and wsw == 0:
            if WEAPONS[wp][5]:
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

        if bob_on and moving:
            hz = MID + int(math.sin(frame * 0.45) * 2)
        else:
            hz = MID

        if autofire and fire_cd == 0 and wsw == 0 and frame % 3 == 0:
            w = WEAPONS[wp]
            if ammo[w[1]] > 0:
                t = targets(w[3] * 0.8)
                if t and (wp != 3 or t[0][0] > 2.5):
                    try_fire()

        frame += 1
        if shoot_flash > 0:
            shoot_flash -= 1
        if boom > 0:
            boom -= 1
        if hurt > 0:
            hurt -= 1
        if msg_t > 0:
            msg_t -= 1
            if msg_t == 0:
                message = hint()

        update_enemies()
        update_projs()
        for q in fx:
            q[2] -= 1
        while len(fx) > 0 and fx[0][2] < 0:
            fx.pop(0)
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
        c = choose("DOOM EVO", ["START GAME", "LEVEL SELECT", "SETTINGS",
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