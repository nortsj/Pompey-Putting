"""
Game.py - the putting game itself.

main(effects) plays the three levels using the drink effects chosen at the
bar (see drink_effects.parse_drinks).  Running this file directly plays the
game sober.
"""

import math
from graphix import (Window, Rectangle, Circle, Point, Line, Text,
                     GraphixError, update)
from drink_effects import (
    parse_drinks,
    create_modified_ball,
    apply_hole_effects,
    teleport_hole,
    update_moving_hole,
    step_aim_angle,
    apply_roll_physics,
    draw_active_drinks_hud,
    GREEN,
)

WALL = 10            # the width of the walls on the green
ARROW_REACH = 20     # how far the aiming arrow sticks out past the ball
SPIN_SPEED = 3       # degrees the arrow turns per frame
SPEED = 6            # pixels per frame at launch
FRICTION = 0.98      # speed is multiplied by this every frame (lower = stops sooner)
MIN_SPEED = 0.2      # below this the ball counts as stopped
MIN_REACH = 130      # however many heavy drinks are stacked, a shot rolls at least this far
MAX_ROLL_FRAMES = 900  # safety net: a roll can never last longer than this
SUBSTEP = 3          # the ball moves at most this many pixels at a time
HOLE_RADIUS = 10

# course edges (the playable green area)
LEFT, TOP, RIGHT, BOTTOM = 100, 150, 700, 450
BOUNDS = (LEFT, TOP, RIGHT, BOTTOM)
MAX_STROKES = 10

# Game state (set up by main)
win = None
shapelist = []
walls = []
total_strokes = 0    # cross level stroke counter
clock = 0            # counts frames for the whole game (drives the moving hole)


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def clear_window():
    for shape in shapelist:
        shape.undraw()
    shapelist.clear()
    walls.clear()
    update()


def draw_ball(point, effects):
    return create_modified_ball(point, win, shapelist, effects)


def draw_hole(point, effects):
    hole = Circle(point, HOLE_RADIUS)
    hole.fill_colour = "black"
    hole.draw(win)
    apply_hole_effects(hole, effects)      # Vodka lemonade: invisible hole
    shapelist.append(hole)
    return hole


def draw_label(point, text, size, colour="white", style="bold"):
    label = Text(point, text)
    label.text_colour = colour
    label.size = size
    label.style = style
    label.draw(win)
    shapelist.append(label)
    return label


def draw_stroke_counter():
    """Stroke counter at the bottom middle of the window.
    Returns the Text object so it can be updated later."""
    return draw_label(Point(400, 550), "Strokes: 0", 24)


def draw_total_counter():
    """Running total at the top middle of the window."""
    return draw_label(Point(400, 60), f"Total strokes: {total_strokes}", 24)


def update_stroke_counter(counter, strokes):
    """Changes the number shown on the counter."""
    counter.text = f"Strokes: {strokes}"


def make_wall(x1, y1, x2, y2):
    """Draws one wall segment and records it."""
    wall = Rectangle(Point(x1, y1), Point(x2, y2))
    wall.fill_colour = "saddle brown"
    wall.outline_colour = "saddle brown"
    wall.draw(win)
    shapelist.append(wall)
    walls.append(wall)


def make_arrow(ball, angle_degrees):
    """Creates (but doesn't draw) an arrow pointing out from the ball."""
    centre = ball.get_centre()
    length = ball.radius + ARROW_REACH
    angle = math.radians(angle_degrees)
    end_x = round(centre.x + math.cos(angle) * length)
    end_y = round(centre.y - math.sin(angle) * length)   # minus: screen y points down

    arrow = Line(centre, Point(end_x, end_y))
    arrow.arrow = "last"
    arrow.fill_colour = "red"
    arrow.outline_width = 3
    return arrow


def show_message(text):
    """Shows a message above the green and waits for a click."""
    draw_label(Point(400, 105), text, 18, "gold")
    update()
    win.get_mouse()


# ---------------------------------------------------------------------------
# Physics
# ---------------------------------------------------------------------------

def ball_hit_wall(ball):
    """Returns the wall the ball is touching, or None."""
    centre = ball.get_centre()
    for wall in walls:
        p1, p2 = wall.get_p1(), wall.get_p2()

        # closest point on the wall rectangle to the ball's centre
        closest_x = max(min(p1.x, p2.x), min(centre.x, max(p1.x, p2.x)))
        closest_y = max(min(p1.y, p2.y), min(centre.y, max(p1.y, p2.y)))

        dx = centre.x - closest_x
        dy = centre.y - closest_y
        if dx ** 2 + dy ** 2 <= ball.radius ** 2:
            return wall
    return None


def ball_in_hole(ball, hole):
    """True when the ball's centre is over the hole."""
    b = ball.get_centre()
    h = hole.get_centre()
    distance = math.hypot(b.x - h.x, b.y - h.y)
    return distance < hole.radius


def direction_to(ball, hole):
    """Angle in degrees (0 = right, 90 = up) from the ball to the hole."""
    b = ball.get_centre()
    h = hole.get_centre()
    return math.degrees(math.atan2(-(h.y - b.y), h.x - b.x)) % 360


def roll(ball, hole, angle_degrees, effects, hole_home_y):
    """Rolls the ball until it stops. Returns True if it fell in the hole."""
    global clock

    angle = math.radians(angle_degrees)
    launch = SPEED * effects["speed_mult"]
    dx = math.cos(angle) * launch
    dy = -math.sin(angle) * launch
    friction = max(0.90, min(0.99, FRICTION + effects["friction_offset"]))
    friction = min(0.99, max(friction, 1 - launch / MIN_REACH))   # roll distance ~ launch / (1 - friction)
    bounce = effects["wall_bounce"]

    centre = ball.get_centre()
    x, y = float(centre.x), float(centre.y)   # exact position; the ball sits at round(x), round(y)

    frame = 0
    while math.hypot(dx, dy) > MIN_SPEED and frame < MAX_ROLL_FRAMES:
        if win.is_closed():
            raise GraphixError("window closed")
        frame += 1
        clock += 1

        update_moving_hole(hole, effects, clock, hole_home_y, BOUNDS)
        dx, dy = apply_roll_physics(dx, dy, frame, effects)

        # Move in small steps so a fast ball can't jump over the hole or a wall
        steps = max(1, math.ceil(math.hypot(dx, dy) / SUBSTEP))
        for _ in range(steps):
            # horizontal part of the step
            new_x = x + dx / steps
            move_x = round(new_x) - round(x)
            if move_x:
                ball.move(move_x, 0)
                if ball_hit_wall(ball):
                    ball.move(-move_x, 0)      # undo, then bounce
                    dx = -dx * bounce
                else:
                    x = new_x
            else:
                x = new_x

            # vertical part of the step
            new_y = y + dy / steps
            move_y = round(new_y) - round(y)
            if move_y:
                ball.move(0, move_y)
                if ball_hit_wall(ball):
                    ball.move(0, -move_y)
                    dy = -dy * bounce
                else:
                    y = new_y
            else:
                y = new_y

            if ball_in_hole(ball, hole):
                return True

        dx *= friction
        dy *= friction

        # bouncy walls must never make the ball faster than it was hit
        speed = math.hypot(dx, dy)
        if speed > launch:
            dx, dy = dx * launch / speed, dy * launch / speed

        update(60)

    return False


def aim(ball, hole, effects, hole_home_y):
    """Spins an arrow around the ball until space is pressed.
    Returns the locked angle in degrees."""
    global clock

    win.check_key()          # throw away any key pressed while the ball was rolling
    angle = 0
    frame = 0
    arrow = make_arrow(ball, angle)
    arrow.draw(win)

    while True:
        key = win.check_key()
        if key == "space":
            arrow.undraw()
            update()
            return angle

        frame += 1
        clock += 1
        update_moving_hole(hole, effects, clock, hole_home_y, BOUNDS)

        # replace the arrow with one at the new angle
        arrow.undraw()
        angle = step_aim_angle(angle, frame, SPIN_SPEED, effects,
                               centre=direction_to(ball, hole))
        arrow = make_arrow(ball, angle)
        arrow.draw(win)

        update(60)    # limit to about 60 frames per second


# ---------------------------------------------------------------------------
# Levels
# ---------------------------------------------------------------------------

def build_course():
    """Draws the green and the four boundary walls."""
    green = Rectangle(Point(LEFT, TOP), Point(RIGHT, BOTTOM))
    green.fill_colour = GREEN
    green.outline_colour = GREEN
    green.draw(win)
    shapelist.append(green)

    make_wall(LEFT - WALL, TOP - WALL, RIGHT + WALL, TOP)          # top
    make_wall(LEFT - WALL, BOTTOM, RIGHT + WALL, BOTTOM + WALL)    # bottom
    make_wall(LEFT - WALL, TOP, LEFT, BOTTOM)                      # left
    make_wall(RIGHT, TOP, RIGHT + WALL, BOTTOM)                    # right


def play_level(ball_pos, hole_pos, effects):
    """Runs the shot loop. Returns True if the ball was sunk in time."""
    global total_strokes

    counter = draw_stroke_counter()
    total = draw_total_counter()
    draw_active_drinks_hud(win, shapelist, effects)
    draw_label(Point(400, 580), "Press SPACE to shoot", 11, "white", "normal")
    hole = draw_hole(hole_pos, effects)      # hole first, so the ball rolls over it
    ball = draw_ball(ball_pos, effects)
    hole_home_y = hole_pos.y
    update()

    strokes = 0
    while strokes < MAX_STROKES:
        direction = aim(ball, hole, effects, hole_home_y)
        strokes += 1
        total_strokes += 1
        update_stroke_counter(counter, strokes)
        total.text = f"Total strokes: {total_strokes}"

        if roll(ball, hole, direction, effects, hole_home_y):
            show_message(f"In the hole in {strokes}! Click to continue")
            return True

        # Tequila shot: the hole jumps somewhere new after every shot
        teleport_hole(hole, effects, walls, ball, BOUNDS)
        update()

    show_message("Out of strokes! Click to continue")
    return False


def level1(effects):
    """One wall in the middle, blocking the straight shot."""
    build_course()
    mid_x = (LEFT + RIGHT) // 2
    make_wall(mid_x - WALL // 2, 250, mid_x + WALL // 2, 350)
    return play_level(Point(150, 300), Point(650, 300), effects)


def level2(effects):
    """Zigzag: go under the first wall, then over the second."""
    build_course()
    make_wall(295, TOP, 305, 360)        # hangs from the top, gap at the bottom
    make_wall(495, 240, 505, BOTTOM)     # rises from the bottom, gap at the top
    return play_level(Point(150, 200), Point(650, 400), effects)


def level3(effects):
    """Fortress: a horizontal bar, then a gate guarding the hole."""
    build_course()
    make_wall(200, 295, 400, 305)        # horizontal bar blocking the straight shot
    make_wall(555, TOP, 565, 255)        # gate, upper half
    make_wall(555, 345, 565, BOTTOM)     # gate, lower half (gap between 255 and 345)
    return play_level(Point(130, 300), Point(650, 300), effects)


def main(effects=None):
    """Plays all three levels.  `effects` comes from drink_effects.parse_drinks."""
    global win, total_strokes, clock

    if effects is None:
        effects = parse_drinks([])           # sober

    total_strokes = 0
    clock = 0
    shapelist.clear()
    walls.clear()
    # autoflush off: the screen is refreshed by update() once per frame, which
    # is much faster than redrawing after every tiny ball movement.
    win = Window("Pompey putting!", 800, 600, autoflush=False)
    win.background_colour = "#7f2525"

    try:
        for level in (level1, level2, level3):
            level(effects)
            clear_window()

        draw_label(Point(400, 260), "Game over!", 36, "gold")
        draw_label(Point(400, 320), f"Final total: {total_strokes} strokes", 24)
        draw_label(Point(400, 380), "Click to close", 14, "white", "normal")
        update()
        win.get_mouse()
    finally:
        if win.is_open():
            win.close()


if __name__ == "__main__":
    main()
