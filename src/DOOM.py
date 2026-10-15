from math import sin, cos, tan, pi
from ti_draw import *
import ti_system

W = 320
H = 210

MAP = [
    "11111111",
    "10000001",
    "10110001",
    "10000001",
    "10011001",
    "10000001",
    "10000001",
    "11111111"
]

px = 1.5
py = 1.5
ang = 0.0

def wall(x, y):
    mx = int(x)
    my = int(y)
    if mx < 0 or my < 0 or mx >= 8 or my >= 8:
        return 1
    return int(MAP[my][mx])

def render():
    fill_rect(0, 0, W, H // 2)
    set_color(30, 30, 30)
    fill_rect(0, H // 2, W, H // 2)

    for col in range(80):
        ray = ang - 0.55 + col * 1.1 / 80
        dist = 0.1

        while dist < 8:
            rx = px + cos(ray) * dist
            ry = py + sin(ray) * dist
            if wall(rx, ry):
                break
            dist += 0.06

        dist = max(0.1, dist * cos(ray - ang))
        height = int(100 / dist)
        height = min(200, height)

        shade = int(220 / (1 + dist * 0.25))
        set_color(shade, shade // 2, shade // 3)
        fill_rect(col * 4, 105 - height // 2,
                  4, height)

    set_color(255, 255, 255)
    draw_text(5, 15, "EVO DOOM")
    draw_text(5, 30, "W/S move  A/D turn")

    # Minimap
    for y in range(8):
        for x in range(8):
            if wall(x, y):
                set_color(150, 150, 150)
            else:
                set_color(25, 25, 25)
            fill_rect(245 + x * 8, 125 + y * 8, 7, 7)

    set_color(255, 0, 0)
    fill_circle(245 + int(px * 8),
                125 + int(py * 8), 3)

def move(dx, dy):
    global px, py
    if not wall(px + dx, py):
        px += dx
    if not wall(px, py + dy):
        py += dy

clear()
render()

while True:
    k = ti_system.wait_key()

    if k == 9:
        break

    if k == 1:
        move(cos(ang) * 0.25, sin(ang) * 0.25)
    elif k == 2:
        move(-cos(ang) * 0.25, -sin(ang) * 0.25)
    elif k == 3:
        ang -= 0.15
    elif k == 4:
        ang += 0.15

    render()