from graphix import *

drinks = [
    "Lager",
    "Bitter",
    "Pale ale",
    "Stout",
    "Cider",
    "Shandy",
    "Hooch",
    "Gin and tonic",
    "Vodka lemonade",
    "Rum and cola",
    "Whisky",
    "Red wine",
    "White wine",
    "Prosecco",
    "Tequila shot",
    "Lime and soda"
]

def bartender():
    choice=str(input("Can I interest you?"))
    if choice in drinks:
        print("coming right up")
    else:
        print("we don't have that bud")


#Bar window and colours
Bar = Window("Pompey Putting - Bar", 800, 600)
Bar.background_colour = "#7f2525"

torso = "#303F9B"
Larm = "#F4F0EC"
Rarm = "#F4F0EC"
bar = "#9B593D"
skin = "#E6A575"

#Counter
counter = Rectangle(Point(0, 460), Point(800, 600))
counter.fill_colour = bar
counter.outline_colour = bar
counter.draw(Bar)

counter_edge = Line(Point(0, 460), Point(800, 460))
counter_edge.fill_colour = "#70412F"
counter_edge.outline_width = 3
counter_edge.draw(Bar)

#Sleeves
left_sleeve = Polygon([
    Point(320, 0), Point(350, 0), Point(380, 45),
    Point(305, 290), Point(255, 390), Point(220, 445),
    Point(190, 478), Point(135, 466), Point(115, 438),
    Point(150, 390), Point(250, 90)
])
left_sleeve.fill_colour = Larm
left_sleeve.outline_colour = Larm
left_sleeve.draw(Bar)

right_sleeve = Polygon([
    Point(480, 0), Point(450, 0), Point(420, 45),
    Point(495, 290), Point(545, 390), Point(580, 445),
    Point(610, 478), Point(665, 466), Point(685, 438),
    Point(650, 390), Point(550, 90)
])
right_sleeve.fill_colour = Rarm
right_sleeve.outline_colour = Rarm
right_sleeve.draw(Bar)

#Torso
body = Polygon([
    Point(300, 0), Point(500, 0),
    Point(540, 35), Point(520, 460),
    Point(280, 460), Point(260, 35)
])
body.fill_colour = torso
body.outline_colour = torso
body.draw(Bar)

#White shirt
undershirt = Polygon([
    Point(365, 0), Point(435, 0),
    Point(420, 460), Point(380, 460)
])
undershirt.fill_colour = "#F4F0EC"
undershirt.outline_colour = "#F4F0EC"
undershirt.draw(Bar)

#Collar and red tie
left_collar = Polygon([
    Point(365, 0), Point(400, 18),
    Point(385, 48), Point(355, 18)
])
left_collar.fill_colour = "#FFFFFF"
left_collar.outline_colour = "#FFFFFF"
left_collar.draw(Bar)

right_collar = Polygon([
    Point(435, 0), Point(400, 18),
    Point(415, 48), Point(445, 18)
])
right_collar.fill_colour = "#FFFFFF"
right_collar.outline_colour = "#FFFFFF"
right_collar.draw(Bar)

tie_knot = Polygon([
    Point(392, 12), Point(408, 12),
    Point(414, 30), Point(400, 43), Point(386, 30)
])
tie_knot.fill_colour = "#A00030"
tie_knot.outline_colour = "#A00030"
tie_knot.draw(Bar)

tie = Polygon([
    Point(391, 37), Point(409, 37),
    Point(418, 230), Point(400, 275), Point(382, 230)
])
tie.fill_colour = "#A00030"
tie.outline_colour = "#A00030"
tie.draw(Bar)

#Palms
left_palm = Oval(Point(132, 472), Point(188, 520))
left_palm.fill_colour = skin
left_palm.outline_colour = skin
left_palm.draw(Bar)

right_palm = Oval(Point(612, 472), Point(668, 520))
right_palm.fill_colour = skin
right_palm.outline_colour = skin
right_palm.draw(Bar)

#Fingers
for x1, x2, y1, y2 in [
    (130, 144, 505, 542),
    (143, 157, 510, 550),
    (156, 170, 510, 550),
    (169, 183, 505, 542),
]:
    finger = Oval(Point(x1, y1), Point(x2, y2))
    finger.fill_colour = skin
    finger.outline_colour = skin
    finger.draw(Bar)

for x1, x2, y1, y2 in [
    (617, 631, 505, 542),
    (643, 657, 510, 550),
    (630, 644, 510, 550),
    (656, 670, 505, 542),
]:
    finger = Oval(Point(x1, y1), Point(x2, y2))
    finger.fill_colour = skin
    finger.outline_colour = skin
    finger.draw(Bar)

#Thumbs
left_thumb = Oval(Point(178, 487), Point(202, 516))
left_thumb.fill_colour = skin
left_thumb.outline_colour = skin
left_thumb.draw(Bar)

right_thumb = Oval(Point(598, 487), Point(622, 516))
right_thumb.fill_colour = skin
right_thumb.outline_colour = skin
right_thumb.draw(Bar)
Bar.get_mouse()
