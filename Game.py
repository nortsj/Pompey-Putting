import math
from graphix import Window, Rectangle, Circle, Point, Line, Text, GraphixError, update
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

WALL = 10
ARROW_REACH = 20
SPIN_SPEED = 3
SPEED = 6
FRICTION = 0.98
MIN_SPEED = 0.2
MIN_REACH = 130
MAX_ROLL_FRAMES = 900
SUBSTEP = 3
HOLE_RADIUS = 10
MAX_STROKES = 10
LEVEL_COUNT = 12
LEFT, TOP, RIGHT, BOTTOM = 100, 150, 700, 450
BOUNDS = (LEFT, TOP, RIGHT, BOTTOM)

win = None
shapelist = []
walls = []
water_areas = []
total_strokes = 0
completed_holes = 0
bar_visits = 0
drinks_taken = 0
clock = 0
current_level = 1


def clear_window():
    for shape in shapelist:
        shape.undraw()
    shapelist.clear()
    walls.clear()
    water_areas.clear()
    update()


def draw_ball(point, effects):
    return create_modified_ball(point, win, shapelist, effects)


def draw_hole(point, effects):
    hole = Circle(point, HOLE_RADIUS)
    hole.fill_colour = "black"
    hole.draw(win)
    apply_hole_effects(hole, effects)
    shapelist.append(hole)
    return hole


def draw_label(point, text, size, colour="white", style="bold"):
    label = Text(point, text)
    label.typeface = "courier"
    label.text_colour = colour
    label.size = size
    label.style = style
    label.draw(win)
    shapelist.append(label)
    return label


def drink_score_modifier():
    expected_drinks = bar_visits * 2
    return (drinks_taken - expected_drinks) * 10


def current_score():
    hole_points = completed_holes * 100
    stroke_deduction = total_strokes * 10
    return hole_points - stroke_deduction + drink_score_modifier()


def draw_total_counter():
    return draw_label(
        Point(400, 55),
        f"Total strokes: {total_strokes}   Score: {current_score()}",
        18,
    )


def update_total_counter(counter):
    counter.text = f"Total strokes: {total_strokes}   Score: {current_score()}"


def update_stroke_counter(counter, strokes):
    counter.text = f"Strokes: {strokes}"


def make_wall(x1, y1, x2, y2):
    wall = Rectangle(Point(x1, y1), Point(x2, y2))
    wall.fill_colour = "saddle brown"
    wall.outline_colour = "saddle brown"
    wall.draw(win)
    shapelist.append(wall)
    walls.append(wall)


def make_water(x1, y1, x2, y2):
    area = Rectangle(Point(x1, y1), Point(x2, y2))
    area.fill_colour = "#287C88"
    area.outline_colour = "#A3DBD9"
    area.outline_width = 2
    area.draw(win)
    shapelist.append(area)
    water_areas.append((x1, y1, x2, y2))
    return area


def make_arrow(ball, angle_degrees):
    centre = ball.get_centre()
    length = ball.radius + ARROW_REACH
    angle = math.radians(angle_degrees)
    end_x = round(centre.x + math.cos(angle) * length)
    end_y = round(centre.y - math.sin(angle) * length)
    arrow = Line(centre, Point(end_x, end_y))
    arrow.arrow = "last"
    arrow.fill_colour = "red"
    arrow.outline_width = 3
    return arrow


def show_message(text):
    message = draw_label(Point(400, 125), text, 18, "gold")
    update()
    win.get_mouse()
    message.undraw()
    shapelist.remove(message)
    update()


def ball_hit_wall(ball):
    centre = ball.get_centre()
    for wall in walls:
        p1, p2 = wall.get_p1(), wall.get_p2()
        closest_x = max(min(p1.x, p2.x), min(centre.x, max(p1.x, p2.x)))
        closest_y = max(min(p1.y, p2.y), min(centre.y, max(p1.y, p2.y)))
        dx = centre.x - closest_x
        dy = centre.y - closest_y
        if dx ** 2 + dy ** 2 <= ball.radius ** 2:
            return wall
    return None


def ball_in_hole(ball, hole):
    b = ball.get_centre()
    h = hole.get_centre()
    return math.hypot(b.x - h.x, b.y - h.y) < hole.radius


def ball_in_water(ball):
    centre = ball.get_centre()
    return any(x1 <= centre.x <= x2 and y1 <= centre.y <= y2
               for x1, y1, x2, y2 in water_areas)


def direction_to(ball, hole):
    b = ball.get_centre()
    h = hole.get_centre()
    return math.degrees(math.atan2(-(h.y - b.y), h.x - b.x)) % 360


def roll(ball, hole, angle_degrees, effects, hole_home_y):
    global clock
    angle = math.radians(angle_degrees)
    launch = SPEED * effects["speed_mult"]
    dx = math.cos(angle) * launch
    dy = -math.sin(angle) * launch
    friction = max(0.90, min(0.99, FRICTION + effects["friction_offset"]))
    friction = min(0.99, max(friction, 1 - launch / MIN_REACH))
    bounce = effects["wall_bounce"]

    centre = ball.get_centre()
    x, y = float(centre.x), float(centre.y)
    frame = 0
    while math.hypot(dx, dy) > MIN_SPEED and frame < MAX_ROLL_FRAMES:
        if win.is_closed():
            raise GraphixError("window closed")
        frame += 1
        clock += 1
        update_moving_hole(hole, effects, clock, hole_home_y, BOUNDS)
        dx, dy = apply_roll_physics(dx, dy, frame, effects)
        steps = max(1, math.ceil(math.hypot(dx, dy) / SUBSTEP))

        for _ in range(steps):
            new_x = x + dx / steps
            move_x = round(new_x) - round(x)
            if move_x:
                ball.move(move_x, 0)
                if ball_hit_wall(ball):
                    ball.move(-move_x, 0)
                    dx = -dx * bounce
                else:
                    x = new_x
            else:
                x = new_x

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

            if ball_in_water(ball):
                return "water"
            if ball_in_hole(ball, hole):
                return "holed"

        dx *= friction
        dy *= friction
        speed = math.hypot(dx, dy)
        if speed > launch:
            dx, dy = dx * launch / speed, dy * launch / speed
        update(60)
    return "stopped"


def aim(ball, hole, effects, hole_home_y):
    global clock
    win.check_key()
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
        arrow.undraw()
        angle = step_aim_angle(angle, frame, SPIN_SPEED, effects,
                               centre=direction_to(ball, hole))
        arrow = make_arrow(ball, angle)
        arrow.draw(win)
        update(60)


def draw_decor(shape, fill, outline, width=1):
    shape.fill_colour = fill
    shape.outline_colour = outline
    shape.outline_width = width
    shape.draw(win)
    shapelist.append(shape)


def draw_bottle_shelf(center_x, shelf_y):
    draw_decor(Rectangle(Point(center_x - 37, shelf_y),
                         Point(center_x + 37, shelf_y + 6)),
               "#8C4A2E", "#2E1C21", 2)
    bottle_colours = ("#A52B32", "#D28A24", "#356C43", "#C34C31")
    bottle_centres = (center_x - 26, center_x - 9,
                      center_x + 9, center_x + 26)
    for bottle_x, colour in zip(bottle_centres, bottle_colours):
        draw_decor(Rectangle(Point(bottle_x - 4, shelf_y - 22),
                             Point(bottle_x + 4, shelf_y - 3)),
                   colour, "#291A1E")
        draw_decor(Rectangle(Point(bottle_x - 2, shelf_y - 29),
                             Point(bottle_x + 2, shelf_y - 21)),
                   colour, "#291A1E")
        draw_decor(Rectangle(Point(bottle_x - 3, shelf_y - 32),
                             Point(bottle_x + 3, shelf_y - 28)),
                   "#E2BF62", "#291A1E")


def draw_tap(y):
    draw_decor(Rectangle(Point(720, y - 8), Point(784, y + 10)),
               "#7B3E29", "#2A1C20", 2)
    draw_decor(Rectangle(Point(746, y - 22), Point(761, y + 3)),
               "#C38D42", "#4A3024", 2)
    draw_decor(Line(Point(753, y - 20), Point(773, y - 27)),
               "#D6AE5C", "#D6AE5C", 4)
    draw_decor(Circle(Point(778, y - 29), 6), "#C22D32", "#E4B45A", 2)
    draw_decor(Line(Point(753, y + 3), Point(753, y + 17)),
               "#D6AE5C", "#D6AE5C", 3)
    draw_decor(Line(Point(747, y + 17), Point(759, y + 17)),
               "#D6AE5C", "#D6AE5C", 3)


def draw_pub_setting():
    draw_decor(Rectangle(Point(0, 0), Point(800, 600)), "#464751", "#464751")
    draw_decor(Rectangle(Point(0, 0), Point(800, 140)), "#09166B", "#09166B")
    draw_decor(Rectangle(Point(0, 140), Point(90, 460)), "#41434D", "#41434D")
    draw_decor(Rectangle(Point(710, 140), Point(800, 460)), "#41434D", "#41434D")
    draw_decor(Rectangle(Point(0, 460), Point(800, 600)), "#702532", "#702532")
    draw_decor(Rectangle(Point(90, 470), Point(710, 598)), "#7F2525", "#C49A5B", 3)
    draw_decor(Rectangle(Point(100, 480), Point(700, 588)), "#68222B", "#A7794A", 2)

    for y, colour, width in [(128, "#CE4B25", 5), (136, "#E3A642", 2)]:
        draw_decor(Line(Point(0, y), Point(800, y)), colour, colour, width)

    for x in (150, 250, 550, 650):
        draw_decor(Line(Point(x, 0), Point(x, 126)), "#18267F", "#18267F", 3)

    for y in (491, 577):
        draw_decor(Line(Point(112, y), Point(688, y)), "#C49A5B", "#C49A5B", 2)

    for x in range(130, 680, 42):
        draw_decor(Line(Point(x, 499), Point(x + 9, 490)), "#A7794A", "#A7794A", 2)
        draw_decor(Line(Point(x, 569), Point(x + 9, 578)), "#A7794A", "#A7794A", 2)

    for shelf_y in (195, 245, 345, 415):
        draw_bottle_shelf(45, shelf_y)

    for tap_y in (180, 250, 340, 410):
        draw_tap(tap_y)


def draw_bar_rails():
    for left, right, top, bottom in ((155, 645, 118, 140), (90, 710, 460, 482)):
        draw_decor(Rectangle(Point(left, top), Point(right, bottom)),
                   "#85462F", "#35211C", 3)
        draw_decor(Line(Point(left + 6, top + 4), Point(right - 6, top + 4)),
                   "#D18B3A", "#D18B3A", 3)
        draw_decor(Line(Point(left + 6, bottom - 4), Point(right - 6, bottom - 4)),
                   "#A72E37", "#A72E37", 3)
        for x in range(left + 24, right - 12, 72):
            draw_decor(Line(Point(x, top + 8), Point(x, bottom - 8)),
                       "#A96A43", "#A96A43", 2)


def build_course():
    draw_pub_setting()
    green = Rectangle(Point(LEFT, TOP), Point(RIGHT, BOTTOM))
    green.fill_colour = GREEN
    green.outline_colour = GREEN
    green.draw(win)
    shapelist.append(green)
    make_wall(LEFT - WALL, TOP - WALL, RIGHT + WALL, TOP)
    make_wall(LEFT - WALL, BOTTOM, RIGHT + WALL, BOTTOM + WALL)
    make_wall(LEFT - WALL, TOP, LEFT, BOTTOM)
    make_wall(RIGHT, TOP, RIGHT + WALL, BOTTOM)
    draw_bar_rails()


def play_level(ball_pos, hole_pos, effects):
    global total_strokes, completed_holes
    strokes = 0
    stroke_counter = draw_label(Point(400, 520), "Strokes: 0", 24)
    total_counter = draw_total_counter()
    draw_active_drinks_hud(win, shapelist, effects)
    draw_label(Point(400, 550), "Press SPACE to shoot", 11, "white", "normal")
    draw_label(Point(400, 100), f"HOLE {current_level} / {LEVEL_COUNT}", 18, "gold")
    hole = draw_hole(hole_pos, effects)
    ball = draw_ball(ball_pos, effects)
    hole_home_y = hole_pos.y
    update()

    while True:
        direction = aim(ball, hole, effects, hole_home_y)
        strokes += 1
        total_strokes += 1
        update_stroke_counter(stroke_counter, strokes)
        update_total_counter(total_counter)
        result = roll(ball, hole, direction, effects, hole_home_y)

        if result == "holed" and strokes <= MAX_STROKES:
            completed_holes += 1
            update_total_counter(total_counter)
            show_message(f"In the hole in {strokes}! Click to continue")
            return True

        if strokes > MAX_STROKES:
            return False

        if result == "water":
            strokes += 1
            total_strokes += 1
            centre = ball.get_centre()
            ball.move(round(ball_pos.x - centre.x), round(ball_pos.y - centre.y))
            update_stroke_counter(stroke_counter, strokes)
            update_total_counter(total_counter)
            if strokes > MAX_STROKES:
                return False
            show_message("Water! One penalty stroke. Click to continue")
            continue

        teleport_hole(hole, effects, walls, ball, BOUNDS)
        update()


def level1(effects):
    build_course()
    make_wall(395, 250, 405, 350)
    return play_level(Point(150, 300), Point(650, 300), effects)


def level2(effects):
    build_course()
    make_wall(295, TOP, 305, 360)
    make_wall(495, 240, 505, BOTTOM)
    return play_level(Point(150, 200), Point(650, 400), effects)


def level3(effects):
    build_course()
    make_wall(200, 295, 400, 305)
    make_wall(555, TOP, 565, 255)
    make_wall(555, 345, 565, BOTTOM)
    return play_level(Point(130, 300), Point(650, 300), effects)


def level4(effects):
    build_course()
    make_wall(250, TOP, 260, 350)
    make_wall(400, 250, 410, BOTTOM)
    make_wall(550, TOP, 560, 350)
    return play_level(Point(140, 400), Point(660, 200), effects)


def level5(effects):
    build_course()
    make_wall(290, 210, 320, 240)
    make_wall(385, 300, 415, 330)
    make_wall(490, 380, 520, 410)
    make_wall(555, TOP, 565, 245)
    make_wall(555, 355, 565, BOTTOM)
    return play_level(Point(140, 300), Point(660, 300), effects)


def level6(effects):
    build_course()
    make_wall(245, TOP, 255, 355)
    make_wall(350, 245, 360, BOTTOM)
    make_wall(455, TOP, 465, 355)
    make_wall(560, 245, 570, BOTTOM)
    return play_level(Point(135, 200), Point(665, 400), effects)


def level7(effects):
    build_course()
    make_wall(250, TOP, 260, 280)
    make_wall(250, 340, 260, BOTTOM)
    make_wall(390, TOP, 400, 210)
    make_wall(390, 270, 400, BOTTOM)
    make_wall(530, TOP, 540, 280)
    make_wall(530, 340, 540, BOTTOM)
    return play_level(Point(140, 300), Point(660, 300), effects)


def level8(effects):
    build_course()
    make_wall(225, 205, 390, 215)
    make_wall(410, 205, 575, 215)
    make_wall(300, 285, 310, 420)
    make_wall(490, 180, 500, 325)
    make_wall(390, 385, 575, 395)
    return play_level(Point(140, 400), Point(660, 200), effects)


def level9(effects):
    build_course()
    make_water(300, 225, 500, 385)
    make_wall(245, TOP, 255, 300)
    make_wall(545, 300, 555, BOTTOM)
    return play_level(Point(140, 200), Point(660, 400), effects)


def level10(effects):
    build_course()
    make_water(310, 210, 480, 390)
    make_wall(230, TOP, 240, 300)
    make_wall(230, 350, 240, BOTTOM)
    make_wall(550, TOP, 560, 250)
    make_wall(550, 300, 560, BOTTOM)
    make_wall(390, 160, 400, 210)
    return play_level(Point(140, 400), Point(660, 200), effects)


def level11(effects):
    build_course()
    make_water(255, 275, 420, 435)
    make_water(405, 165, 555, 315)
    make_wall(235, TOP, 245, 245)
    make_wall(565, 355, 575, BOTTOM)
    make_wall(350, 185, 360, 245)
    make_wall(455, 355, 465, 420)
    return play_level(Point(140, 200), Point(660, 400), effects)


def level12(effects):
    build_course()
    make_water(285, 195, 515, 405)
    make_water(355, 160, 445, 440)
    make_wall(245, TOP, 255, 315)
    make_wall(245, 365, 255, BOTTOM)
    make_wall(545, TOP, 555, 235)
    make_wall(545, 285, 555, BOTTOM)
    make_wall(315, 175, 325, 225)
    make_wall(475, 375, 485, 425)
    return play_level(Point(140, 400), Point(660, 200), effects)


def show_end_screen(won):
    clear_window()
    heading = "COURSE COMPLETE!" if won else "GAME OVER"
    draw_label(Point(400, 210), heading, 36, "gold")
    draw_label(Point(400, 280), f"Final score: {current_score()}", 26)
    draw_label(Point(400, 330), f"Total strokes: {total_strokes}", 20)
    draw_label(Point(400, 375), f"Drink modifier: {drink_score_modifier():+d}", 18)
    draw_label(Point(400, 445), "Click to return to the main menu", 16, "white", "normal")
    update()
    win.get_mouse()


def main(effects=None, bar_callback=None):
    global win, total_strokes, completed_holes, bar_visits
    global drinks_taken, clock, current_level

    active_drinks = []
    if isinstance(effects, dict):
        active_drinks = list(effects.get("active_drinks", []))
        effects = effects if "speed_mult" in effects else parse_drinks(active_drinks)
    else:
        if effects is not None:
            active_drinks = [effects] if isinstance(effects, str) else list(effects)
        effects = parse_drinks(active_drinks)

    total_strokes = 0
    completed_holes = 0
    bar_visits = 0
    drinks_taken = len(active_drinks)
    clock = 0
    current_level = 1
    shapelist.clear()
    walls.clear()
    water_areas.clear()
    win = Window("Pompey Putting!", 800, 600, autoflush=False)
    win.background_colour = "#7f2525"

    levels = [level1, level2, level3, level4, level5, level6,
              level7, level8, level9, level10, level11, level12]
    won = False
    try:
        for level_number, level in enumerate(levels, start=1):
            current_level = level_number
            clear_window()
            if not level(effects):
                break

            if level_number < LEVEL_COUNT and level_number % 2 == 0:
                clear_window()
                bar_visits += 1
                if bar_callback is None:
                    from bar import bartender
                    bar_callback = bartender
                new_drinks = bar_callback() or []
                win.bind_all("<Key>", win._on_key)
                win.focus_set()
                active_drinks.extend(new_drinks)
                drinks_taken += len(new_drinks)
                effects = parse_drinks(active_drinks)
        else:
            won = True

        show_end_screen(won)
        return "win" if won else "loss"
    finally:
        if win.is_open():
            win.close()


if __name__ == "__main__":
    main()
