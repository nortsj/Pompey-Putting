"""
drink_effects.py
Turns the drinks chosen at the bar into modifiers for Pompey Putting:
ball size / shape / colour, speed, friction, curve, aiming arrow
behaviour and hole behaviour.

Drinks stack, so ordering several gives a combination of effects.
"""

import math
import random
from graphix import Oval, Circle, Point, Text

GREEN = "forest green"            # colour of the putting green

# How strongly the "curve" and "wobble" numbers turn the ball (radians per
# frame per unit).  Turning the velocity (rather than adding to it) means a
# drink can never make the ball speed up, so every roll still comes to a stop.
CURVE_TURN = 0.08
WOBBLE_TURN = 0.12

# All 16 drinks from bar.py mapped to unique, stackable modifiers
DRINK_EFFECTS = {
    "Lager": {
        "description": "Heavy Pints: Ball grows bigger and rolls slower.",
        "ball_radius_mult": 1.5,
        "speed_mult": 0.8,
    },
    "Bitter": {
        "description": "Sharp Hook: Ball curves hard to the left.",
        "curve": -0.14,
    },
    "Pale ale": {
        "description": "Hoppy Bounce: Extra bouncy walls and slightly larger ball.",
        "wall_bounce": 1.15,
        "ball_radius_mult": 1.25,
    },
    "Stout": {
        "description": "Heavyweight: Huge, sluggish ball that stops fast.",
        "ball_radius_mult": 1.8,
        "speed_mult": 0.7,
        "friction_offset": -0.015,
    },
    "Cider": {
        "description": "Scrumpy Wobble: Aiming arrow jitters unpredictably.",
        "arrow_mode": "jitter",
    },
    "Shandy": {
        "description": "Half & Half: Gentle S-wave wobble as the ball rolls.",
        "wobble": 0.45,
    },
    "Hooch": {
        "description": "Lemon Twist: Ball turns into a lemon and rolls lopsidedly!",
        "ball_shape": "lemon",
        "ball_colour": "gold",
        "lemon_lopsided": True,
    },
    "Gin and tonic": {
        "description": "Fizzy Bubbles: Ball shrinks tiny and zips super fast.",
        "ball_radius_mult": 0.6,
        "speed_mult": 1.35,
    },
    "Vodka lemonade": {
        "description": "Clear Vision: The hole turns invisible (same colour as the green)!",
        "hole_invisible": True,
    },
    "Rum and cola": {
        "description": "Pirate Drift: Hole slowly patrols up and down the green.",
        "hole_move": "patrol",
    },
    "Whisky": {
        "description": "Double Vision: Aiming arrow swings back and forth like a pendulum.",
        "arrow_mode": "pendulum",
    },
    "Red wine": {
        "description": "Smooth Arc: Deep, sweeping curve to the right.",
        "curve": 0.14,
        "ball_colour": "dark red",
    },
    "White wine": {
        "description": "Crisp & Tiny: Ball becomes tiny and slick on the green.",
        "ball_radius_mult": 0.65,
        "friction_offset": 0.008,
    },
    "Prosecco": {
        "description": "Hyper Fizz: Aiming arrow spins at double speed!",
        "arrow_speed_mult": 2.0,
    },
    "Tequila shot": {
        "description": "Blackout Teleport: Hole jumps to a random spot after every shot!",
        "hole_move": "teleport",
    },
    "Lime and soda": {
        "description": "Sober Up: Clears all active drink effects!",
        "clear_all": True,
    },
}


# ---------------------------------------------------------------------------
# Combining the chosen drinks into one effects dictionary
# ---------------------------------------------------------------------------

def _sober_state():
    """The effects dictionary with no drinks active."""
    return {
        "active_drinks": [],
        "descriptions": [],
        "ball_radius_mult": 1.0,
        "ball_shape": "circle",       # "circle" or "lemon"
        "ball_colour": "grey",
        "lemon_lopsided": False,
        "speed_mult": 1.0,
        "friction_offset": 0.0,
        "wall_bounce": 1.0,
        "curve": 0.0,                 # steady turning of the ball (+ = right)
        "wobble": 0.0,                # sinusoidal side-to-side sway
        "arrow_speed_mult": 1.0,
        "arrow_mode": "normal",       # "normal", "jitter" or "pendulum"
        "hole_invisible": False,
        "hole_move": "static",        # "static", "patrol" or "teleport"
    }


def parse_drinks(chosen_drinks):
    """
    Takes a single drink string, a comma-separated string, or a list of drinks
    chosen at the bar and combines them into a single effects dictionary.
    Unknown drink names are ignored.  Passing [] gives the sober defaults.
    """
    if isinstance(chosen_drinks, str):
        # Supports "Hooch" or "Hooch, Whisky"
        drink_list = [d.strip() for d in chosen_drinks.split(",") if d.strip()]
    else:
        drink_list = list(chosen_drinks)

    # Lookup map for case-insensitive matching
    lookup = {name.lower(): name for name in DRINK_EFFECTS}

    state = _sober_state()

    for raw_drink in drink_list:
        canonical = lookup.get(str(raw_drink).lower())
        if not canonical:
            continue

        effect = DRINK_EFFECTS[canonical]

        if effect.get("clear_all"):
            # Reset everything back to sober defaults
            state = _sober_state()
            state["active_drinks"].append(canonical)
            state["descriptions"].append(effect["description"])
            continue

        state["active_drinks"].append(canonical)
        state["descriptions"].append(effect["description"])

        state["ball_radius_mult"] *= effect.get("ball_radius_mult", 1.0)
        state["speed_mult"] *= effect.get("speed_mult", 1.0)
        state["friction_offset"] += effect.get("friction_offset", 0.0)
        state["wall_bounce"] *= effect.get("wall_bounce", 1.0)
        state["curve"] += effect.get("curve", 0.0)
        state["wobble"] += effect.get("wobble", 0.0)
        state["arrow_speed_mult"] *= effect.get("arrow_speed_mult", 1.0)

        if "ball_shape" in effect:
            state["ball_shape"] = effect["ball_shape"]
        if "ball_colour" in effect:
            state["ball_colour"] = effect["ball_colour"]
        if effect.get("lemon_lopsided"):
            state["lemon_lopsided"] = True
        if effect.get("arrow_mode"):
            state["arrow_mode"] = effect["arrow_mode"]
        if effect.get("hole_invisible"):
            state["hole_invisible"] = True
        if effect.get("hole_move"):
            state["hole_move"] = effect["hole_move"]

    # Clamp extreme stacking values so the game stays playable
    state["ball_radius_mult"] = max(0.4, min(2.5, state["ball_radius_mult"]))
    state["speed_mult"] = max(0.4, min(2.2, state["speed_mult"]))
    state["wall_bounce"] = max(0.5, min(1.5, state["wall_bounce"]))
    state["arrow_speed_mult"] = max(0.5, min(4.0, state["arrow_speed_mult"]))
    state["curve"] = max(-0.4, min(0.4, state["curve"]))
    state["wobble"] = max(0.0, min(1.2, state["wobble"]))
    state["friction_offset"] = max(-0.05, min(0.01, state["friction_offset"]))
    return state


def format_drink_list(names, max_chars=None):
    """'Lager, Lager, Stout' -> 'Lager x2, Stout' (shortened with ... if needed)."""
    counts = {}
    for name in names:
        counts[name] = counts.get(name, 0) + 1
    parts = [n if c == 1 else f"{n} x{c}" for n, c in counts.items()]
    text = ", ".join(parts)
    if max_chars is not None and len(text) > max_chars:
        text = text[:max_chars - 3].rstrip(", ") + "..."
    return text


# ---------------------------------------------------------------------------
# The ball
# ---------------------------------------------------------------------------

class LemonBall:
    """
    Wrapper mimicking graphix.Circle so Game.py's ball.get_centre(),
    ball.move(dx, dy), ball.undraw() and ball.radius work seamlessly
    when Hooch turns the ball into an oval lemon with tips.
    """
    def __init__(self, centre, radius, win, colour="gold"):
        self.radius = radius
        self._centre = Point(centre.x, centre.y)
        rx = int(radius * 1.2)
        ry = int(radius * 0.85)

        self.body = Oval(
            Point(centre.x - rx, centre.y - ry),
            Point(centre.x + rx, centre.y + ry)
        )
        self.body.fill_colour = colour
        self.body.outline_colour = "goldenrod"

        # Little lemon nubs on left and right ends
        nub_r = max(2, radius // 4)
        self.left_nub = Circle(Point(centre.x - rx, centre.y), nub_r)
        self.left_nub.fill_colour = colour
        self.left_nub.outline_colour = "goldenrod"

        self.right_nub = Circle(Point(centre.x + rx, centre.y), nub_r)
        self.right_nub.fill_colour = colour
        self.right_nub.outline_colour = "goldenrod"

        self.parts = [self.left_nub, self.right_nub, self.body]
        for part in self.parts:
            part.draw(win)

    def get_centre(self):
        return self._centre.clone()

    def move(self, dx, dy):
        self._centre.move(dx, dy)
        for part in self.parts:
            part.move(dx, dy)

    def undraw(self):
        for part in self.parts:
            part.undraw()


def create_modified_ball(point, win, shapelist, effects, base_radius=10):
    """Draws either a standard/resized Circle or a LemonBall for Hooch."""
    radius = max(4, round(base_radius * effects["ball_radius_mult"]))
    if effects["ball_shape"] == "lemon":
        ball = LemonBall(point, radius, win, "gold")      # a lemon is always yellow
    else:
        ball = Circle(point, radius)
        ball.fill_colour = effects["ball_colour"]
        ball.draw(win)
    shapelist.append(ball)
    return ball


# ---------------------------------------------------------------------------
# The hole
# ---------------------------------------------------------------------------

def apply_hole_effects(hole, effects):
    """Vodka lemonade: colour the hole the same as the green."""
    if effects["hole_invisible"]:
        hole.fill_colour = GREEN
        hole.outline_colour = GREEN


def _distance_to_rect(px, py, rect):
    p1, p2 = rect.get_p1(), rect.get_p2()
    closest_x = max(min(p1.x, p2.x), min(px, max(p1.x, p2.x)))
    closest_y = max(min(p1.y, p2.y), min(py, max(p1.y, p2.y)))
    return math.hypot(px - closest_x, py - closest_y)


def teleport_hole(hole, effects, walls, ball, bounds=(100, 150, 700, 450)):
    """
    Tequila shot: jump the hole to a random spot.  The spot is chosen so the
    ball can actually reach it: clear of every wall by at least the ball's
    radius, and not on top of the ball.
    """
    if effects["hole_move"] != "teleport":
        return

    left, top, right, bottom = bounds
    clearance = ball.radius + 6
    ball_pos = ball.get_centre()
    min_from_ball = ball.radius + hole.radius + 20

    for _ in range(300):
        x = random.randint(left + clearance, right - clearance)
        y = random.randint(top + clearance, bottom - clearance)
        if any(_distance_to_rect(x, y, wall) < clearance for wall in walls):
            continue
        if math.hypot(x - ball_pos.x, y - ball_pos.y) < min_from_ball:
            continue
        cur = hole.get_centre()
        hole.move(x - cur.x, y - cur.y)
        return
    # no valid spot found (very unlikely): leave the hole where it is


def update_moving_hole(hole, effects, clock, home_y, bounds=(100, 150, 700, 450)):
    """
    Rum and cola: the hole glides up and down around its starting height
    (home_y).  `clock` is a frame counter that keeps counting up.
    """
    if effects["hole_move"] != "patrol":
        return

    _, top, _, bottom = bounds
    margin = hole.radius + 15
    target = home_y + 60 * math.sin(clock * 0.03)
    target = max(top + margin, min(bottom - margin, target))
    target = int(round(target))

    current = hole.get_centre().y
    if target != current:
        hole.move(0, target - current)


# ---------------------------------------------------------------------------
# Aiming and rolling
# ---------------------------------------------------------------------------

def step_aim_angle(angle, frame, base_spin_speed, effects, centre=0):
    """
    Next aiming arrow angle (degrees).  `frame` counts frames since aiming
    began.  `centre` is the angle a Whisky pendulum swings around (Game.py
    passes the direction of the hole, so the whole green stays reachable).
    """
    mode = effects["arrow_mode"]
    speed = base_spin_speed * effects["arrow_speed_mult"]

    if mode == "jitter":
        # Cider: erratic twitchy jumps
        return (angle + speed + random.uniform(-6.5, 6.5)) % 360
    elif mode == "pendulum":
        # Whisky: swings back and forth like a drunken pendulum
        return (centre + 110 * math.sin(frame * 0.02 * speed)) % 360
    else:
        return (angle + speed) % 360


def apply_roll_physics(dx, dy, frame, effects):
    """
    Turns the velocity (dx, dy) a little each frame for curve (Bitter / Red
    wine), wobble (Shandy) and Hooch's lopsided lemon.  The speed is only
    changed by the lemon's small surges, so the ball always slows down.
    """
    speed = math.hypot(dx, dy)
    if speed == 0:
        return dx, dy

    turn = effects["curve"] * CURVE_TURN                      # radians this frame
    if effects["wobble"]:
        turn += math.sin(frame * 0.25) * effects["wobble"] * WOBBLE_TURN
    surge = 1.0
    if effects["lemon_lopsided"]:
        turn += math.sin(frame * 0.35) * 0.05
        surge = 1.0 + 0.04 * math.cos(frame * 0.35)

    if turn:
        # rotate the velocity (screen y points down, so + turns right)
        cos_t, sin_t = math.cos(turn), math.sin(turn)
        dx, dy = dx * cos_t - dy * sin_t, dx * sin_t + dy * cos_t

    return dx * surge, dy * surge


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------

def draw_active_drinks_hud(win, shapelist, effects):
    """Displays the active drinks at the top of the game window."""
    if not effects["active_drinks"]:
        label_text = "Drinks: Sober"
    else:
        label_text = "Drinks: " + format_drink_list(effects["active_drinks"], 70)
    hud = Text(Point(400, 25), label_text)
    hud.text_colour = "gold"
    hud.size = 14
    hud.style = "bold"
    hud.draw(win)
    shapelist.append(hud)
    return hud
