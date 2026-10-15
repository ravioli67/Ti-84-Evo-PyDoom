import math
import ti_draw as d
import ti_system as sys

W = 319
H = 209
FOV = 1.05
RAYS = 53
STRIP = 6
MAX_DIST = 12.0

WORLD = [
    "1111111111",
    "1000000001",
    "1011000101",
    "1000000101",
    "1001100001",
    "1000101101",
    "1000000001",
    "1011000101",
    "1000000001",
    "1111111111"
]

# Player state
px = 1.5
py = 1.5
angle = 0.0
health = 100
ammo = 20
score = 0
running = True
message = "FIND THE DEMONS"

# Enemy positions: x, y, health
enemies = [
    [5.5, 1.5, 2],
    [7.5, 4.5, 2],
    [4.5, 7.5, 2]
]

depths = [MAX_DIST] * RAYS


def wall(x, y):
    mx = int(x)
    my = int(y)

    if my < 0 or my >= len(WORLD):
        return True
    if mx < 0 or mx >= len(WORLD[0]):
        return True

    return WORLD[my][mx] == "1"


def raycast(ray_angle):
    # Grid-based DDA ray traversal
    dx = math.cos(ray_angle)
    dy = math.sin(ray_angle)

    mx = int(px)
    my = int(py)

    if abs(dx) < 0.0001:
        dx = 0.0001
    if abs(dy) < 0.0001:
        dy = 0.0001

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

    for step in range(32):
        if tx < ty:
            mx += sx
            tx += ddx
            side = 0
        else:
            my += sy
            ty += ddy
            side = 1

        if my < 0 or my >= len(WORLD):
            break
        if mx < 0 or mx >= len(WORLD[0]):
            break

        if WORLD[my][mx] == "1":
            if side == 0:
                dist = tx - ddx
            else:
                dist = ty - ddy

            return max(0.1, dist), side

    return MAX_DIST, 0


def draw_world():
    # Sky
    d.set_color(30, 35, 50)
    d.fill_rect(0, 0, W, 105)

    # Floor
    d.set_color(48, 38, 32)
    d.fill_rect(0, 105, W, 104)

    # Walls
    for i in range(RAYS):
        ray_angle = angle - FOV / 2 + FOV * i / RAYS
        dist, side = raycast(ray_angle)

        # Correct fisheye distortion
        corrected = dist * math.cos(ray_angle - angle)
        corrected = max(0.1, corrected)
        depths[i] = corrected

        height = int(100 / corrected)
        if height > 205:
            height = 205

        top = 105 - height // 2
        if top < 0:
            top = 0

        shade = int(190 / (1 + corrected * 0.18))
        if side:
            shade = int(shade * 0.72)

        if shade > 220:
            shade = 220
        if shade < 20:
            shade = 20

        d.set_color(shade, int(shade * 0.72),
                    int(shade * 0.48))

        x = i * STRIP
        d.fill_rect(x, top, STRIP, height)

    # Enemies, drawn only if not hidden behind walls
    for e in enemies:
        if e[2] <= 0:
            continue

        ex = e[0] - px
        ey = e[1] - py
        dist = math.sqrt(ex * ex + ey * ey)

        if dist < 0.2:
            continue

        enemy_angle = math.atan2(ey, ex)
        delta = enemy_angle - angle

        while delta > math.pi:
            delta -= 2 * math.pi
        while delta < -math.pi:
            delta += 2 * math.pi

        if abs(delta) < FOV / 2 and dist < MAX_DIST:
            screen_x = int(
                (delta / FOV + 0.5) * W
            )
            ray_index = int(screen_x / STRIP)

            if ray_index < 0:
                ray_index = 0
            if ray_index >= RAYS:
                ray_index = RAYS - 1

            if dist < depths[ray_index] + 0.15:
                size = int(30 / dist)
                if size < 3:
                    size = 3
                if size > 35:
                    size = 35

                d.set_color(150, 15, 15)
                d.fill_circle(screen_x, 105, size)

                d.set_color(255, 180, 60)
                d.fill_circle(
                    screen_x - size // 3,
                    105 - size // 4,
                    max(1, size // 7)
                )
                d.fill_circle(
                    screen_x + size // 3,
                    105 - size // 4,
                    max(1, size // 7)
                )

    # Crosshair
    d.set_color(230, 230, 210)
    d.draw_line(155, 105, 163, 105)
    d.draw_line(159, 101, 159, 109)

    draw_hud()


def draw_hud():
    # Top HUD background
    d.set_color(0, 0, 0)
    d.fill_rect(0, 0, W, 19)

    d.set_color(255, 255, 255)
    d.draw_text(4, 14, "HP:" + str(health))
    d.draw_text(90, 14, "AMMO:" + str(ammo))
    d.draw_text(210, 14, "K:" + str(score))

    # Minimap
    cell = 7
    ox = 250
    oy = 130

    for my in range(len(WORLD)):
        for mx in range(len(WORLD[0])):
            if WORLD[my][mx] == "1":
                d.set_color(130, 130, 140)
            else:
                d.set_color(25, 25, 30)

            d.fill_rect(
                ox + mx * cell,
                oy + my * cell,
                cell - 1,
                cell - 1
            )

    # Player marker
    d.set_color(50, 255, 70)
    d.fill_circle(
        ox + int(px * cell),
        oy + int(py * cell),
        3
    )

    # Direction marker
    d.set_color(255, 255, 0)
    d.draw_line(
        ox + int(px * cell),
        oy + int(py * cell),
        ox + int((px + math.cos(angle) * 0.7) * cell),
        oy + int((py + math.sin(angle) * 0.7) * cell)
    )

    d.set_color(255, 255, 255)
    d.draw_text(5, 202, message)


def shoot():
    global ammo, score, message

    if ammo <= 0:
        message = "OUT OF AMMO"
        return

    ammo -= 1
    best = None
    best_dist = MAX_DIST

    for e in enemies:
        if e[2] <= 0:
            continue

        dx = e[0] - px
        dy = e[1] - py
        dist = math.sqrt(dx * dx + dy * dy)
        target_angle = math.atan2(dy, dx)

        delta = target_angle - angle
        while delta > math.pi:
            delta -= 2 * math.pi
        while delta < -math.pi:
            delta += 2 * math.pi

        # Must be close to the crosshair
        if abs(delta) < 0.10 and dist < best_dist:
            wall_dist, side = raycast(target_angle)

            if wall_dist >= dist - 0.25:
                best = e
                best_dist = dist

    if best is not None:
        best[2] -= 1

        if best[2] <= 0:
            score += 1
            message = "DEMON DESTROYED"
        else:
            message = "HIT!"
    else:
        message = "SHOT MISSED"


def move_player(forward, turn):
    global px, py, angle

    angle += turn

    dx = math.cos(angle) * forward
    dy = math.sin(angle) * forward

    # Separate axis checks allow sliding along walls
    radius = 0.18

    if not wall(px + dx + radius, py) and \
       not wall(px + dx - radius, py):
        px += dx

    if not wall(px, py + dy + radius) and \
       not wall(px, py + dy - radius):
        py += dy


def game_over():
    d.set_color(0, 0, 0)
    d.fill_rect(0, 0, W, H)

    d.set_color(220, 30, 30)
    d.draw_text(95, 75, "GAME OVER")

    d.set_color(255, 255, 255)
    d.draw_text(65, 110, "KILLS: " + str(score))
    d.draw_text(35, 145, "PRESS CLEAR TO EXIT")


def main():
    global running, health, message

    previous_key = 0

    d.set_color(0, 0, 0)
    d.fill_rect(0, 0, W, H)

    d.set_color(220, 30, 30)
    d.draw_text(65, 75, "DOOM EVO")

    d.set_color(255, 255, 255)
    d.draw_text(25, 110, "ARROWS: MOVE / TURN")
    d.draw_text(25, 135, "2ND: SHOOT")
    d.draw_text(25, 160, "CLEAR: QUIT")
    d.draw_text(25, 190, "PRESS ANY KEY")

    sys.wait_key()

    while running and health > 0:
        key = sys.get_key(0)

        if key == 45:
            running = False
            break

        forward = 0.0
        turn = 0.0

        if key == 25:       # Up
            forward = 0.12
        elif key == 34:     # Down
            forward = -0.12
        elif key == 24:     # Left
            turn = -0.08
        elif key == 26:     # Right
            turn = 0.08

        move_player(forward, turn)

        # Shoot once per key press
        if key == 21 and previous_key != 21:
            shoot()

        previous_key = key

        draw_world()

    if health <= 0:
        game_over()
        sys.wait_key()


main()