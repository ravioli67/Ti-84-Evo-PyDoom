import math
import ti_draw as draw
import ti_system as system

W = 319
H = 209
FOV = 1.05
RAYS = 53
STRIP = 6
MAX_DIST = 12.0

MAP = [
    "111111111111",
    "100000000001",
    "101110110001",
    "100010000001",
    "100010111101",
    "100000100001",
    "101100100001",
    "100000000001",
    "100110111D01",
    "1000000000E1",
    "111111111111"
]

# Game state
px = 1.5
py = 1.5
angle = 0.0

health = 100
ammo = 24
kills = 0
frame = 0
running = True
won = False
door_open = False
shoot_flash = 0
message = "FIND THE EXIT"

# Enemy: x, y, hp, attack cooldown
enemies = [
    [7.5, 1.5, 2, 0],
    [9.5, 5.5, 2, 0],
    [5.5, 7.5, 2, 0],
    [2.5, 8.5, 2, 0]
]

# Pickup: x, y, type, active
pickups = [
    [3.5, 3.5, "H", True],
    [6.5, 5.5, "A", True],
    [8.5, 7.5, "H", True],
    [2.5, 6.5, "A", True]
]

depths = [MAX_DIST] * RAYS


def tile(x, y):
    mx = int(x)
    my = int(y)

    if my < 0 or my >= len(MAP):
        return "1"
    if mx < 0 or mx >= len(MAP[0]):
        return "1"

    c = MAP[my][mx]

    if c == "D" and door_open:
        return "0"

    return c


def solid(x, y):
    return tile(x, y) in ("1", "D")


def can_stand(x, y):
    r = 0.17

    return (
        not solid(x - r, y - r)
        and not solid(x + r, y - r)
        and not solid(x - r, y + r)
        and not solid(x + r, y + r)
    )


def raycast(ray_angle):
    dx = math.cos(ray_angle)
    dy = math.sin(ray_angle)

    if abs(dx) < 0.00001:
        dx = 0.00001
    if abs(dy) < 0.00001:
        dy = 0.00001

    mx = int(px)
    my = int(py)

    if dx < 0:
        sx = -1
        tx = (px - mx) / -dx
    else:
        sx = 1
        tx = (mx + 1 - px) / dx

    if dy < 0:
        sy = -1
        ty = (py - my) / -dy
    else:
        sy = 1
        ty = (my + 1 - py) / dy

    ddx = abs(1.0 / dx)
    ddy = abs(1.0 / dy)
    side = 0

    for step in range(30):
        if tx < ty:
            mx += sx
            tx += ddx
            side = 0
        else:
            my += sy
            ty += ddy
            side = 1

        if mx < 0 or my < 0:
            break
        if mx >= len(MAP[0]) or my >= len(MAP):
            break

        if tile(mx, my) != "0" and tile(mx, my) != "E":
            if side == 0:
                dist = tx - ddx
            else:
                dist = ty - ddy

            return max(0.1, dist), side

    return MAX_DIST, 0


def draw_world():
    # Sky and floor
    draw.set_color(24, 28, 43)
    draw.fill_rect(0, 0, W, 105)

    draw.set_color(48, 38, 31)
    draw.fill_rect(0, 105, W, 104)

    # Cast vertical wall strips
    for i in range(RAYS):
        ray = angle - FOV / 2 + FOV * i / RAYS
        dist, side = raycast(ray)

        dist *= math.cos(ray - angle)
        dist = max(0.1, dist)
        depths[i] = dist

        height = int(100 / dist)
        height = min(205, height)
        top = max(19, 105 - height // 2)
        bottom = min(190, 105 + height // 2)
        height = bottom - top

        shade = int(190 / (1 + dist * 0.18))
        if side:
            shade = int(shade * 0.72)

        shade = max(18, min(220, shade))

        c = tile(
            int(px + math.cos(ray) * dist),
            int(py + math.sin(ray) * dist)
        )

        if c == "D":
            draw.set_color(shade, shade * 2 // 3, 25)
        else:
            draw.set_color(shade, shade * 3 // 4,
                           shade // 2)

        draw.fill_rect(i * STRIP, top, STRIP, height)

    draw_enemies()
    draw_pickups()
    draw_weapon()
    draw_hud()


def draw_enemies():
    for e in enemies:
        if e[2] <= 0:
            continue

        dx = e[0] - px
        dy = e[1] - py
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 0.1:
            continue

        target = math.atan2(dy, dx)
        delta = target - angle

        while delta > math.pi:
            delta -= 2 * math.pi
        while delta < -math.pi:
            delta += 2 * math.pi

        if abs(delta) >= FOV / 2:
            continue

        sx = int((delta / FOV + 0.5) * W)
        idx = int(sx / STRIP)
        idx = max(0, min(RAYS - 1, idx))

        if dist >= depths[idx] + 0.1:
            continue

        size = max(3, min(35, int(32 / dist)))
        top = max(21, 105 - size)
        bottom = min(188, 105 + size)

        draw.set_color(100, 10, 10)
        draw.fill_rect(sx - size // 2, top,
                       size, bottom - top)

        draw.set_color(255, 180, 40)
        eye = max(1, size // 7)
        draw.fill_rect(sx - size // 4, 105 - size // 3,
                       eye, eye)
        draw.fill_rect(sx + size // 6, 105 - size // 3,
                       eye, eye)


def draw_pickups():
    for p in pickups:
        if not p[3]:
            continue

        dx = p[0] - px
        dy = p[1] - py
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 0.1:
            continue

        delta = math.atan2(dy, dx) - angle

        while delta > math.pi:
            delta -= 2 * math.pi
        while delta < -math.pi:
            delta += 2 * math.pi

        if abs(delta) >= FOV / 2:
            continue

        sx = int((delta / FOV + 0.5) * W)
        idx = max(0, min(RAYS - 1, int(sx / STRIP)))

        if dist >= depths[idx]:
            continue

        size = max(2, min(10, int(14 / dist)))

        if p[2] == "H":
            draw.set_color(30, 255, 80)
        else:
            draw.set_color(255, 210, 30)

        draw.fill_rect(sx - size // 2, 105 - size // 2,
                       size, size)


def draw_weapon():
    # Simple first-person weapon
    if shoot_flash > 0:
        draw.set_color(255, 220, 90)
        draw.fill_rect(145, 132, 29, 25)
        draw.set_color(255, 255, 220)
        draw.fill_rect(153, 120, 13, 18)

    draw.set_color(65, 65, 72)
    draw.fill_rect(132, 157, 55, 52)

    draw.set_color(110, 110, 118)
    draw.fill_rect(145, 143, 29, 48)

    draw.set_color(25, 25, 30)
    draw.fill_rect(152, 139, 15, 27)

    # Crosshair
    draw.set_color(240, 240, 220)
    draw.draw_line(154, 105, 164, 105)
    draw.draw_line(159, 100, 159, 110)


def draw_hud():
    draw.set_color(0, 0, 0)
    draw.fill_rect(0, 0, W, 19)
    draw.fill_rect(0, 190, W, 19)

    draw.set_color(255, 255, 255)
    draw.draw_text(3, 13, "HP " + str(health))
    draw.draw_text(80, 13, "AMMO " + str(ammo))
    draw.draw_text(190, 13, "KILLS " + str(kills))

    draw.draw_text(3, 202, message)

    # Health bar
    draw.set_color(70, 20, 20)
    draw.fill_rect(245, 195, 68, 8)

    draw.set_color(40, 220, 50)
    draw.fill_rect(245, 195, int(68 * health / 100), 8)

    # Minimap
    cell = 5
    ox = 252
    oy = 45

    for my in range(len(MAP)):
        for mx in range(len(MAP[0])):
            c = tile(mx, my)

            if c == "1":
                draw.set_color(135, 135, 145)
            elif c == "D":
                draw.set_color(220, 170, 30)
            elif c == "E":
                draw.set_color(20, 230, 40)
            else:
                draw.set_color(25, 25, 30)

            draw.fill_rect(ox + mx * cell, oy + my * cell,
                           cell - 1, cell - 1)

    # Enemies on map
    for e in enemies:
        if e[2] > 0:
            draw.set_color(255, 30, 30)
            draw.fill_rect(ox + int(e[0] * cell),
                           oy + int(e[1] * cell), 3, 3)

    # Player and direction
    draw.set_color(30, 255, 70)
    sx = ox + int(px * cell)
    sy = oy + int(py * cell)
    draw.fill_rect(sx - 1, sy - 1, 4, 4)

    draw.draw_line(
        sx, sy,
        ox + int((px + math.cos(angle) * 0.7) * cell),
        oy + int((py + math.sin(angle) * 0.7) * cell)
    )


def move_player(forward, turn):
    global px, py, angle

    angle += turn

    dx = math.cos(angle) * forward
    dy = math.sin(angle) * forward

    if can_stand(px + dx, py):
        px += dx

    if can_stand(px, py + dy):
        py += dy


def shoot():
    global ammo, kills, shoot_flash, message

    if ammo <= 0:
        message = "NO AMMO!"
        return

    ammo -= 1
    shoot_flash = 3
    best = None
    best_dist = MAX_DIST

    for e in enemies:
        if e[2] <= 0:
            continue

        dx = e[0] - px
        dy = e[1] - py
        dist = math.sqrt(dx * dx + dy * dy)
        target = math.atan2(dy, dx)

        delta = target - angle

        while delta > math.pi:
            delta -= 2 * math.pi
        while delta < -math.pi:
            delta += 2 * math.pi

        if abs(delta) < 0.13 and dist < best_dist:
            wall_dist, side = raycast(target)

            if wall_dist >= dist - 0.3:
                best = e
                best_dist = dist

    if best is None:
        message = "MISSED"
        return

    best[2] -= 1

    if best[2] <= 0:
        kills += 1
        message = "DEMON DESTROYED"
    else:
        message = "HIT!"


def use_door():
    global door_open, message

    dx = 9.5 - px
    dy = 8.5 - py
    dist = math.sqrt(dx * dx + dy * dy)

    if dist < 1.5:
        door_open = True
        message = "DOOR OPENED"
    else:
        message = "NO DOOR NEARBY"


def update_enemies():
    global health, message

    for e in enemies:
        if e[2] <= 0:
            continue

        dx = px - e[0]
        dy = py - e[1]
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0.8:
            speed = 0.025

            mx = dx / dist * speed
            my = dy / dist * speed

            nx = e[0] + mx
            ny = e[1] + my

            if not solid(nx, e[1]):
                e[0] = nx

            if not solid(e[0], ny):
                e[1] = ny

        else:
            e[3] += 1

            if e[3] >= 35:
                e[3] = 0
                health -= 10
                message = "DEMON ATTACKED YOU!"

                if health < 0:
                    health = 0


def collect_pickups():
    global health, ammo, message

    for p in pickups:
        if not p[3]:
            continue

        dx = px - p[0]
        dy = py - p[1]

        if dx * dx + dy * dy < 0.25:
            if p[2] == "H" and health < 100:
                health = min(100, health + 25)
                p[3] = False
                message = "HEALTH +25"

            elif p[2] == "A" and ammo < 60:
                ammo = min(60, ammo + 12)
                p[3] = False
                message = "AMMO +12"


def show_title():
    draw.set_color(0, 0, 0)
    draw.fill_rect(0, 0, W, H)

    draw.set_color(190, 20, 20)
    draw.draw_text(110, 55, "DOOM EVO")

    draw.set_color(255, 255, 255)
    draw.draw_text(35, 85, "ARROWS: MOVE AND TURN")
    draw.draw_text(35, 105, "2ND: SHOOT")
    draw.draw_text(35, 125, "ENTER: OPEN DOOR")
    draw.draw_text(35, 145, "CLEAR: QUIT")
    draw.draw_text(35, 180, "PRESS ENTER TO START")

    while True:
        k = system.get_key(0)

        if k == 45:
            return False

        if k == 105:
            return True


def show_end(victory):
    draw.set_color(0, 0, 0)
    draw.fill_rect(0, 0, W, H)

    draw.set_color(220, 30, 30)
    if victory:
        draw.draw_text(105, 65, "YOU WIN!")
    else:
        draw.draw_text(100, 65, "GAME OVER")

    draw.set_color(255, 255, 255)
    draw.draw_text(100, 95, "KILLS: " + str(kills))
    draw.draw_text(55, 130, "ENTER: RESTART")
    draw.draw_text(55, 150, "CLEAR: QUIT")

    while True:
        k = system.get_key(0)

        if k == 45:
            return False

        if k == 105:
            return True


def reset_game():
    global px, py, angle, health, ammo, kills
    global frame, running, won, door_open, shoot_flash
    global message, enemies, pickups, depths

    px = 1.5
    py = 1.5
    angle = 0.0
    health = 100
    ammo = 24
    kills = 0
    frame = 0
    running = True
    won = False
    door_open = False
    shoot_flash = 0
    message = "FIND THE EXIT"

    enemies = [
        [7.5, 1.5, 2, 0],
        [9.5, 5.5, 2, 0],
        [5.5, 7.5, 2, 0],
        [2.5, 8.5, 2, 0]
    ]

    pickups = [
        [3.5, 3.5, "H", True],
        [6.5, 5.5, "A", True],
        [8.5, 7.5, "H", True],
        [2.5, 6.5, "A", True]
    ]

    depths = [MAX_DIST] * RAYS


def play_game():
    global running, won, frame, shoot_flash, message

    previous_key = 0

    while running:
        key = system.get_key(0)

        if key == 45:
            return False

        # One-time actions on a new key press
        if key == 21 and previous_key != 21:
            shoot()

        if key == 105 and previous_key != 105:
            use_door()

        previous_key = key

        # Movement
        forward = 0.0
        turn = 0.0

        if key == 25:
            forward = 0.12
        elif key == 34:
            forward = -0.12
        elif key == 24:
            turn = -0.075
        elif key == 26:
            turn = 0.075

        move_player(forward, turn)

        # Game simulation
        frame += 1

        if shoot_flash > 0:
            shoot_flash -= 1

        update_enemies()
        collect_pickups()

        # Exit is at map cell (10, 9)
        if int(px) == 10 and int(py) == 9:
            won = True
            return True

        if health <= 0:
            return True

        draw_world()

    return False


def main():
    while True:
        if not show_title():
            break

        reset_game()
        result = play_game()

        if not result:
            break

        if not show_end(won):
            break

    draw.set_color(0, 0, 0)
    draw.fill_rect(0, 0, W, H)
    draw.set_color(255, 255, 255)
    draw.draw_text(95, 105, "DOOM EVO EXIT")


main()