from graphix import Window, Rectangle, Circle, Point, Line, Text, update
import random, math, time

win = Window("Pompey putting!", 800, 600)
win.background_colour = "#ff3860"
shapelist = []
walls = []

WALL = 10          # the width of the walls on the green
ARROW_LENGTH = 30  # the length of the arrow that spins around the ball
SPIN_SPEED = 3     # the speed that the arrow spins around the ball
SPEED = 6          # pixels per frame at launch
FRICTION = 0.98   # speed is multiplied by this every frame (lower = stops sooner)
MIN_SPEED = 0.2    # below this the ball counts as stopped
total_strokes = 0  # cross level stroke counter

def clear_window():
    for shape in shapelist:
        shape.undraw()
    shapelist.clear()
    walls.clear()

def draw_ball(point):
    ball = Circle(point, 10)
    ball.fill_colour = "grey"
    ball.draw(win)
    shapelist.append(ball)
    return ball

def draw_hole(point):
    hole = Circle(point, 10)
    hole.fill_colour = "black"
    hole.draw(win)
    shapelist.append(hole)
    return hole

def draw_stroke_counter():
    """Draws the stroke counter at the bottom middle of the window.
    Returns the Text object so it can be updated later."""
    counter = Text(Point(400, 550), "Strokes: 0")
    counter.text_colour = "white"
    counter.size = 24
    counter.style = "bold"
    counter.draw(win)
    shapelist.append(counter)
    return counter

def draw_total_counter():
    """Draws the running total at the top middle of the window."""
    total = Text(Point(400, 60), f"Total strokes: {total_strokes}")
    total.text_colour = "white"
    total.size = 24
    total.style = "bold"
    total.draw(win)
    shapelist.append(total)
    return total

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
    angle = math.radians(angle_degrees)
    end_x = round(centre.x + math.cos(angle) * ARROW_LENGTH)
    end_y = round(centre.y - math.sin(angle) * ARROW_LENGTH)   # minus: screen y points down

    arrow = Line(centre, Point(end_x, end_y))
    arrow.arrow = "last"
    arrow.fill_colour = "red"
    arrow.outline_width = 3
    return arrow

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


def wall_is_horizontal(wall):
    """True for the top/bottom walls, False for the left/right ones."""
    p1, p2 = wall.get_p1(), wall.get_p2()
    return abs(p2.x - p1.x) > abs(p2.y - p1.y)


def ball_in_hole(ball, hole):
    """True when the ball's centre is over the hole."""
    b = ball.get_centre()
    h = hole.get_centre()
    distance = math.hypot(b.x - h.x, b.y - h.y)
    return distance < hole.radius

def roll(ball, hole, angle_degrees):
    """Rolls the ball until it stops. Returns True if it fell in the hole."""
    angle = math.radians(angle_degrees)
    dx = math.cos(angle) * SPEED
    dy = -math.sin(angle) * SPEED

    centre = ball.get_centre()
    x, y = float(centre.x), float(centre.y)

    while math.hypot(dx, dy) > MIN_SPEED:
        new_x = x + dx
        new_y = y + dy
        step_x = round(new_x) - round(x)
        step_y = round(new_y) - round(y)

        ball.move(step_x, step_y)

        # wall check: undo the move, then bounce
        wall = ball_hit_wall(ball)
        if wall:
            ball.move(-step_x, -step_y)
            if wall_is_horizontal(wall):
                dy = -dy
            else:
                dx = -dx
        else:
            x, y = new_x, new_y

        # hole check
        if ball_in_hole(ball, hole):
            return True

        dx *= FRICTION
        dy *= FRICTION
        update(60)

    return False

def aim(ball):
    """Spins an arrow around the ball until space is pressed.
    Returns the locked angle in degrees."""
    angle = 0
    arrow = make_arrow(ball, angle)
    arrow.draw(win)

    while True:
        key = win.check_key()
        if key == "space":
            arrow.undraw()
            return angle

        # replace the arrow with one at the new angle
        arrow.undraw()
        angle = (angle + SPIN_SPEED) % 360
        arrow = make_arrow(ball, angle)
        arrow.draw(win)

        update(60)    # limit to about 60 frames per second

# course edges (the playable green area)
LEFT, TOP, RIGHT, BOTTOM = 100, 150, 700, 450
MAX_STROKES = 10


def build_course():
    """Draws the green and the four boundary walls."""
    green = Rectangle(Point(LEFT, TOP), Point(RIGHT, BOTTOM))
    green.fill_colour = "forest green"
    green.outline_colour = "forest green"
    green.draw(win)
    shapelist.append(green)

    make_wall(LEFT - WALL, TOP - WALL, RIGHT + WALL, TOP)          # top
    make_wall(LEFT - WALL, BOTTOM, RIGHT + WALL, BOTTOM + WALL)    # bottom
    make_wall(LEFT - WALL, TOP, LEFT, BOTTOM)                      # left
    make_wall(RIGHT, TOP, RIGHT + WALL, BOTTOM)                    # right


def play_level(ball_pos, hole_pos):
    """Runs the shot loop. Returns True if the ball was sunk in time."""
    global total_strokes

    counter = draw_stroke_counter()
    total = draw_total_counter()
    ball = draw_ball(ball_pos)
    hole = draw_hole(hole_pos)

    strokes = 0
    while strokes < MAX_STROKES:
        direction = aim(ball)
        strokes += 1
        total_strokes += 1
        update_stroke_counter(counter, strokes)
        total.text = f"Total strokes: {total_strokes}"
        if roll(ball, hole, direction):
            return True
    return False


def level1():
    """One wall in the middle, blocking the straight shot."""
    build_course()
    mid_x = (LEFT + RIGHT) // 2
    make_wall(mid_x - WALL // 2, 250, mid_x + WALL // 2, 350)
    return play_level(Point(150, 300), Point(650, 300))


def level2():
    """Zigzag: go under the first wall, then over the second."""
    build_course()
    make_wall(295, TOP, 305, 360)        # hangs from the top, gap at the bottom
    make_wall(495, 240, 505, BOTTOM)     # rises from the bottom, gap at the top
    return play_level(Point(150, 200), Point(650, 400))


def level3():
    """Fortress: a horizontal bar, then a gate guarding the hole."""
    build_course()
    make_wall(200, 295, 400, 305)        # horizontal bar blocking the straight shot
    make_wall(555, TOP, 565, 255)        # gate, upper half
    make_wall(555, 345, 565, BOTTOM)     # gate, lower half (gap between 255 and 345)
    return play_level(Point(130, 300), Point(650, 300))


def main():
    for level in (level1, level2, level3):
        if level():
            print("In the hole!")
        else:
            print("Out of strokes!")
        win.get_mouse()      # click to continue
        clear_window()

    print("Final total:", total_strokes)
    win.close()

if __name__ == "__main__":
    main()