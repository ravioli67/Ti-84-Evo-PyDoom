import math
import ti_draw as draw
import ti_system as system

# ---------------- SETTINGS ----------------
W = 319
H = 209
FOV = 1.05
RAYS = 53
STRIP = 6
MAX_DIST = 12.0
VIEW_TOP = 19
VIEW_BOT = 190
MID = 105
N_ENEMIES = 4

# Key codes - change these if your calculator reports other values
K_QUIT = 45
K_SHOOT = 21
K_USE = 105
K_UP = 25
K_DOWN = 34
K_LEFT = 24
K_RIGHT = 26

# Door is at (9,8). Row 9 is only reachable through it.
MAP = [
    "111111111111",
    "100000000001",
    "101110110001",
    "100010000001",
    "100010111101",
    "100000100001",
    "101100100001",
    "100000000001",
    "111111111D11",
    "1000000000E1",
    "111111111111"
]
MW = len(MAP[0])
MH = len(MAP)

# Double buffering (removes flicker) if the calculator supports it
BUF = False
try:
    draw.use_buffer()
    BUF = True
except:
    BUF = False

# Precomputed ray offsets, so no trig is needed per ray
COSO = []
SINO = []
for _i in range(RAYS):
    _a = -FOV / 2 + FOV * (_i + 0.5) / RAYS
    COSO.append(math.cos(_a))
    SINO.append(math.sin(_a))

# Minimap wall runs (one rectangle per run instead of per cell)
MM_RUNS = []
for _y in range(MH):
    _x = 0
    while _x < MW:
        if MAP[_y][_x] == "1":
            _s = _x
            while _x < MW and MAP[_y][_x] == "1":
                _x += 1
            MM_RUNS.append((_s, _y, _x - _s))
        else:
            _x += 1

# ---------------- GAME STATE ----------------
px = 1.5
py = 1.5
angle = 0.0
ca = 1.0
sa = 0.0
health = 100
ammo = 24
kills = 0
frame = 0
won = False
has_key = False
moving = False
shoot_flash = 0
hurt = 0
message = ""
msg_t = 0
G = []
enemies = []
pickups = []
depths = []


def flip():
    if BUF:
        draw.paint_buffer()


def set_msg(text):
    global message, msg_t
    message = text
    msg_t = 40


def hint():
    if has_key:
        return "FIND THE EXIT"
    return "FIND THE KEY"


def solid(x, y):
    c = G[int(y)][int(x)]
    return c == "1" or c == "D"


def can_stand(x, y):
    r = 0.17
    return (
        not solid(x - r, y - r)
        and not solid(x + r, y - r)
        and not solid(x - r, y + r)
        and not solid(x + r, y + r)
    )


def cast(dx, dy):
    # DDA raycast. dx, dy should be a unit vector.
    # Returns (distance, side, tile hit, position along wall 0..1)
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

    for n in range(24):
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

        c = G[my][mx]
        if c == "1" or c == "D":
            if side == 0:
                f = py + d * dy
            else:
                f = px + d * dx
            return d, side, c, f - int(f)

    return MAX_DIST, 0, "1", 0.5


# ---------------- DRAWING ----------------
def draw_world():
    # Ceiling and floor
    draw.set_color(24, 28, 43)
    draw.fill_rect(0, 0, W, MID)
    draw.set_color(48, 38, 31)
    draw.fill_rect(0, MID, W, 104)
    draw.set_color(60, 49, 40)
    draw.fill_rect(0, 150, W, 40)

    # Wall strips
    for i in range(RAYS):
        co = COSO[i]
        so = SINO[i]
        d, side, c, f = cast(ca * co - sa * so, sa * co + ca * so)

        d *= co  # fisheye correction
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
            shade = shade * 2 // 3  # dark seams between tiles
        if shade < 18:
            shade = 18
        elif shade > 220:
            shade = 220

        if c == "D":
            draw.set_color(shade, shade * 2 // 3, 25)
        else:
            draw.set_color(shade, shade * 3 // 4, shade // 2)

        draw.fill_rect(i * STRIP, top, STRIP, bot - top)

    draw_pickups()
    draw_enemies()
    draw_weapon()

    if hurt > 0:
        draw.set_color(200, 0, 0)
        draw.fill_rect(0, VIEW_TOP, 7, VIEW_BOT - VIEW_TOP)
        draw.fill_rect(W - 7, VIEW_TOP, 7, VIEW_BOT - VIEW_TOP)

    draw_hud()
    flip()


def draw_enemies():
    vis = []
    for i in range(len(enemies)):
        e = enemies[i]
        if e[2] <= 0:
            continue

        dx = e[0] - px
        dy = e[1] - py
        pd = dx * ca + dy * sa
        if pd < 0.2:
            continue

        delta = math.atan2(dy * ca - dx * sa, pd)
        if abs(delta) >= FOV / 2:
            continue

        sx = int((delta / FOV + 0.5) * W)
        idx = sx // STRIP
        if idx < 0:
            idx = 0
        elif idx >= RAYS:
            idx = RAYS - 1

        if pd > depths[idx] + 0.15:
            continue

        vis.append((pd, i, sx))

    vis.sort()

    # Far to near so close demons cover distant ones
    for n in range(len(vis) - 1, -1, -1):
        pd, i, sx = vis[n]
        e = enemies[i]

        size = int(34 / pd)
        if size < 3:
            size = 3
        elif size > 40:
            size = 40

        top = MID - size
        bot = MID + size
        if top < VIEW_TOP + 2:
            top = VIEW_TOP + 2
        if bot > VIEW_BOT - 2:
            bot = VIEW_BOT - 2

        hh = size * 2 // 3

        if e[5] > 0:
            draw.set_color(255, 150, 150)
        else:
            draw.set_color(110, 12, 12)
        draw.fill_rect(sx - size // 2, top + hh, size, bot - top - hh)

        if e[5] > 0:
            draw.set_color(255, 200, 200)
        else:
            draw.set_color(160, 30, 25)
        draw.fill_rect(sx - size // 4, top, size // 2 + 1, hh)

        draw.set_color(255, 200, 40)
        eye = max(1, size // 8)
        ey = top + hh // 3
        draw.fill_rect(sx - size // 6 - eye, ey, eye, eye)
        draw.fill_rect(sx + size // 6, ey, eye, eye)


def draw_pickups():
    for p in pickups:
        if not p[3]:
            continue

        dx = p[0] - px
        dy = p[1] - py
        pd = dx * ca + dy * sa
        if pd < 0.2:
            continue

        delta = math.atan2(dy * ca - dx * sa, pd)
        if abs(delta) >= FOV / 2:
            continue

        sx = int((delta / FOV + 0.5) * W)
        idx = sx // STRIP
        if idx < 0:
            idx = 0
        elif idx >= RAYS:
            idx = RAYS - 1

        if pd > depths[idx]:
            continue

        size = int(14 / pd)
        if size < 2:
            size = 2
        elif size > 12:
            size = 12

        if p[2] == "H":
            draw.set_color(30, 255, 80)
        elif p[2] == "A":
            draw.set_color(255, 210, 30)
        else:
            draw.set_color(60, 200, 255)

        draw.fill_rect(sx - size // 2,
                       MID + int(10 / pd) - size // 2, size, size)


def draw_weapon():
    bx = 0
    by = 0
    if moving:
        s = math.sin(frame * 0.4)
        bx = int(s * 4)
        by = int(abs(s) * 3)
    by += shoot_flash * 2

    if shoot_flash > 0:
        draw.set_color(255, 220, 90)
        draw.fill_rect(145 + bx, 132, 29, 25)
        draw.set_color(255, 255, 220)
        draw.fill_rect(153 + bx, 120, 13, 18)

    draw.set_color(65, 65, 72)
    draw.fill_rect(132 + bx, 157 + by, 55, 52)
    draw.set_color(110, 110, 118)
    draw.fill_rect(145 + bx, 143 + by, 29, 48)
    draw.set_color(25, 25, 30)
    draw.fill_rect(152 + bx, 139 + by, 15, 27)

    # Crosshair
    draw.set_color(240, 240, 220)
    draw.draw_line(154, MID, 164, MID)
    draw.draw_line(159, MID - 5, 159, MID + 5)


def draw_hud():
    draw.set_color(0, 0, 0)
    draw.fill_rect(0, 0, W, VIEW_TOP)
    draw.fill_rect(0, VIEW_BOT, W, H - VIEW_BOT)

    draw.set_color(255, 255, 255)
    draw.draw_text(3, 13, "HP " + str(health))
    draw.draw_text(70, 13, "AMMO " + str(ammo))
    draw.draw_text(150, 13,
                   "KILLS " + str(kills) + "/" + str(N_ENEMIES))
    if has_key:
        draw.set_color(60, 200, 255)
        draw.draw_text(250, 13, "KEY")

    draw.set_color(255, 255, 255)
    draw.draw_text(3, 202, message)

    # Health bar
    draw.set_color(70, 20, 20)
    draw.fill_rect(245, 195, 68, 8)
    draw.set_color(40, 220, 50)
    draw.fill_rect(245, 195, int(68 * health / 100), 8)

    # Minimap (top right)
    cell = 4
    ox = 268
    oy = 22

    draw.set_color(25, 25, 30)
    draw.fill_rect(ox, oy, MW * cell, MH * cell)

    draw.set_color(135, 135, 145)
    for r in MM_RUNS:
        draw.fill_rect(ox + r[0] * cell, oy + r[1] * cell,
                       r[2] * cell, cell)

    if G[8][9] == "D":
        draw.set_color(220, 170, 30)
        draw.fill_rect(ox + 9 * cell, oy + 8 * cell, cell, cell)

    draw.set_color(20, 230, 40)
    draw.fill_rect(ox + 10 * cell, oy + 9 * cell, cell, cell)

    draw.set_color(255, 30, 30)
    for e in enemies:
        if e[2] > 0:
            draw.fill_rect(ox + int(e[0] * cell) - 1,
                           oy + int(e[1] * cell) - 1, 3, 3)

    sx = ox + int(px * cell)
    sy = oy + int(py * cell)
    draw.set_color(30, 255, 70)
    draw.fill_rect(sx - 1, sy - 1, 3, 3)
    draw.draw_line(sx, sy,
                   sx + int(ca * 5), sy + int(sa * 5))


# ---------------- GAME LOGIC ----------------
def move_player(forward, turn):
    global px, py, angle, ca, sa

    if turn != 0:
        angle += turn
        ca = math.cos(angle)
        sa = math.sin(angle)

    if forward != 0:
        dx = ca * forward
        dy = sa * forward

        if can_stand(px + dx, py):
            px += dx
        if can_stand(px, py + dy):
            py += dy


def shoot():
    global ammo, kills, shoot_flash

    if ammo <= 0:
        set_msg("NO AMMO!")
        return

    ammo -= 1
    shoot_flash = 3
    best = None
    best_d = MAX_DIST

    for e in enemies:
        if e[2] <= 0:
            continue

        dx = e[0] - px
        dy = e[1] - py
        pd = dx * ca + dy * sa
        if pd <= 0.1:
            continue

        lat = dy * ca - dx * sa
        if abs(lat) < 0.3 and pd < best_d:
            dist = math.sqrt(dx * dx + dy * dy)
            wall = cast(dx / dist, dy / dist)[0]
            if wall >= dist - 0.3:
                best = e
                best_d = pd

    if best is None:
        set_msg("MISSED")
        return

    best[2] -= 1
    best[4] = True
    best[5] = 4

    if best[2] <= 0:
        kills += 1
        set_msg("DEMON DESTROYED")
    else:
        set_msg("HIT!")


def use_door():
    global has_key

    if G[8][9] != "D":
        return

    dx = 9.5 - px
    dy = 8.5 - py

    if dx * dx + dy * dy < 2.25:
        if has_key:
            G[8][9] = "0"
            set_msg("DOOR OPENED")
            for e in enemies:
                e[4] = True
        else:
            set_msg("NEED THE KEY")
    else:
        set_msg("NO DOOR NEARBY")


def update_enemies():
    global health, hurt

    for i in range(len(enemies)):
        e = enemies[i]
        if e[2] <= 0:
            continue

        if e[5] > 0:
            e[5] -= 1

        dx = px - e[0]
        dy = py - e[1]
        dist = math.sqrt(dx * dx + dy * dy)

        # Demons sleep until they see you, hear you, or get shot
        if not e[4]:
            if dist < 1.5:
                e[4] = True
            elif dist < 8 and (frame + i) % 8 == 0:
                if cast(-dx / dist, -dy / dist)[0] >= dist - 0.2:
                    e[4] = True
            continue

        if dist > 0.8:
            e[3] = 10
            speed = 0.03
            nx = e[0] + dx / dist * speed
            ny = e[1] + dy / dist * speed

            if not solid(nx, e[1]):
                e[0] = nx
            if not solid(e[0], ny):
                e[1] = ny
        else:
            e[3] += 1
            if e[3] >= 35:
                e[3] = 0
                health -= 10
                hurt = 4
                set_msg("DEMON ATTACKED YOU!")
                if health < 0:
                    health = 0


def collect_pickups():
    global health, ammo, has_key

    for p in pickups:
        if not p[3]:
            continue

        dx = px - p[0]
        dy = py - p[1]

        if dx * dx + dy * dy < 0.25:
            if p[2] == "H" and health < 100:
                health = min(100, health + 25)
                p[3] = False
                set_msg("HEALTH +25")
            elif p[2] == "A" and ammo < 60:
                ammo = min(60, ammo + 12)
                p[3] = False
                set_msg("AMMO +12")
            elif p[2] == "K":
                has_key = True
                p[3] = False
                set_msg("GOT THE KEY! FIND THE DOOR")


def reset_game():
    global px, py, angle, ca, sa, health, ammo, kills, frame
    global won, has_key, moving, shoot_flash, hurt, message, msg_t
    global G, enemies, pickups, depths

    px = 1.5
    py = 1.5
    angle = 0.0
    ca = 1.0
    sa = 0.0
    health = 100
    ammo = 24
    kills = 0
    frame = 0
    won = False
    has_key = False
    moving = False
    shoot_flash = 0
    hurt = 0
    message = "FIND THE KEY"
    msg_t = 60

    G = [list(r) for r in MAP]

    # x, y, hp, attack timer, awake, hurt flash
    enemies = [
        [7.5, 1.5, 2, 0, False, 0],
        [9.5, 5.5, 2, 0, False, 0],
        [5.5, 7.5, 2, 0, False, 0],
        [5.5, 9.5, 2, 0, False, 0]
    ]

    # x, y, type (H health, A ammo, K key), active
    pickups = [
        [3.5, 3.5, "H", True],
        [5.5, 5.5, "A", True],
        [8.5, 7.5, "H", True],
        [1.5, 6.5, "A", True],
        [10.5, 4.5, "K", True],
        [2.5, 9.5, "H", True]
    ]

    depths = [MAX_DIST] * RAYS


# ---------------- SCREENS ----------------
def wait_release():
    # Ignore a held action key so one press doesn't count twice
    for n in range(300):
        k = system.get_key(0)
        if k != K_USE and k != K_SHOOT and k != K_QUIT:
            break


def show_title():
    draw.set_color(0, 0, 0)
    draw.fill_rect(0, 0, W, H)

    draw.set_color(190, 20, 20)
    draw.draw_text(110, 45, "DOOM EVO")

    draw.set_color(255, 255, 255)
    draw.draw_text(35, 75, "ARROWS: MOVE AND TURN")
    draw.draw_text(35, 93, "2ND: SHOOT")
    draw.draw_text(35, 111, "ENTER: OPEN DOOR")
    draw.draw_text(35, 129, "CLEAR: QUIT")
    draw.set_color(60, 200, 255)
    draw.draw_text(35, 155, "FIND THE KEY, OPEN THE")
    draw.draw_text(35, 171, "DOOR, REACH THE EXIT")
    draw.set_color(255, 255, 255)
    draw.draw_text(35, 197, "PRESS ENTER TO START")
    flip()

    wait_release()
    while True:
        k = system.get_key(0)
        if k == K_QUIT:
            return False
        if k == K_USE:
            return True


def show_end(victory):
    draw.set_color(0, 0, 0)
    draw.fill_rect(0, 0, W, H)

    if victory:
        draw.set_color(40, 220, 50)
        draw.draw_text(105, 65, "YOU WIN!")
    else:
        draw.set_color(220, 30, 30)
        draw.draw_text(100, 65, "GAME OVER")

    draw.set_color(255, 255, 255)
    draw.draw_text(85, 95, "KILLS: " + str(kills) + "/" + str(N_ENEMIES))
    draw.draw_text(85, 112, "HEALTH: " + str(health))
    draw.draw_text(55, 145, "ENTER: RESTART")
    draw.draw_text(55, 165, "CLEAR: QUIT")
    flip()

    wait_release()
    while True:
        k = system.get_key(0)
        if k == K_QUIT:
            return False
        if k == K_USE:
            return True


def play_game():
    global frame, shoot_flash, hurt, message, msg_t, moving, won

    prev = 0

    while True:
        key = system.get_key(0)

        if key == K_QUIT:
            return False

        # One-shot actions on a new key press
        if key == K_SHOOT and prev != K_SHOOT:
            shoot()
        if key == K_USE and prev != K_USE:
            use_door()
        prev = key

        forward = 0.0
        turn = 0.0
        if key == K_UP:
            forward = 0.12
        elif key == K_DOWN:
            forward = -0.12
        elif key == K_LEFT:
            turn = -0.075
        elif key == K_RIGHT:
            turn = 0.075

        moving = forward != 0
        move_player(forward, turn)

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
        collect_pickups()

        # Exit is map cell (10, 9)
        if int(px) == 10 and int(py) == 9:
            won = True
            return True

        if health <= 0:
            return True

        draw_world()


def main():
    while True:
        if not show_title():
            break

        reset_game()
        wait_release()
        result = play_game()

        if not result:
            break

        if not show_end(won):
            break

    draw.set_color(0, 0, 0)
    draw.fill_rect(0, 0, W, H)
    draw.set_color(255, 255, 255)
    draw.draw_text(95, 105, "DOOM EVO EXIT")
    flip()


main()