from graphix import *
import random

drinks = [
    "Lager",
    "Bitter",
    "Pale ale",
    "Stout",
    "Cider",
    "Shandy",
    "Hooch",
    "Gin + tonic",
    "Vodka lemonade",
    "Rum + cola",
    "Vodka + coke",
    "Red wine",
    "White wine",
    "Prosecco",
    "Tequila shot"
]

def bartender():
#Three random drink choices and return the selected drinks
    choices = random.sample(drinks, 3)

    prompt_box = Rectangle(Point(245, 10), Point(555, 60))
    prompt_box.fill_colour = "#444444"
    prompt_box.outline_colour = "#B8B8B8"
    prompt_box.outline_width = 2
    prompt_box.draw(Bar)

    prompt = Text(Point(400, 35), "Can I get you anything?")
    prompt.typeface = "courier"
    prompt.size = 16
    prompt.style = "bold"
    prompt.text_colour = "white"
    prompt.draw(Bar)

    option_centres = [265, 400, 535]

#Dark rubber bar mat for all three drink choices
    drink_mat = Rectangle(Point(195, 525), Point(605, 590))
    drink_mat.fill_colour = "#484848"
    drink_mat.outline_colour = "#333333"
    drink_mat.outline_width = 3
    drink_mat.draw(Bar)

    labels = []
    for x, drink in zip(option_centres, choices):
        label = Text(Point(x, 560), drink)
        label.typeface = "courier"
        label.size = 12
        label.style = "bold"
        label.text_colour = "#F4F0EC"
        label.draw(Bar)
        labels.append(label)

    confirm_button = Rectangle(Point(330, 480), Point(470, 515))
    confirm_button.fill_colour = "#484848"
    confirm_button.outline_colour = "#777777"
    confirm_button.outline_width = 2
    confirm_button.draw(Bar)

    confirm_text = Text(Point(400, 498), "CONFIRM")
    confirm_text.typeface = "courier"
    confirm_text.size = 12
    confirm_text.style = "bold"
    confirm_text.text_colour = "#888888"
    confirm_text.draw(Bar)

    selected = set()
    while True:
        click = Bar.get_mouse()

        if 330 <= click.x <= 470 and 480 <= click.y <= 515:
            if selected:
                selected_drinks = [choices[index] for index in sorted(selected)]
                print("Coming right up: " + ", ".join(selected_drinks))
                return selected_drinks
            continue

        if 525 <= click.y <= 590:
            if 195 <= click.x < 333:
                index = 0
            elif 333 <= click.x < 467:
                index = 1
            elif 467 <= click.x <= 605:
                index = 2
            else:
                continue

            if index in selected:
                selected.remove(index)
                labels[index].text_colour = "#F4F0EC"
            else:
                selected.add(index)
                labels[index].text_colour = "#FFD166"

            if selected:
                confirm_text.text_colour = "#FFD166"
                confirm_button.outline_colour = "#D9B56D"
            else:
                confirm_text.text_colour = "#888888"
                confirm_button.outline_colour = "#777777"


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

#Wood grain along the counter
for x1, y1, x2, y2, colour in [
    (25, 495, 170, 495, "#AA6A4D"),
    (620, 495, 775, 495, "#AA6A4D"),
    (18, 515, 125, 515, "#7F4935"),
    (675, 518, 782, 518, "#7F4935"),
    (28, 592, 190, 592, "#AA6A4D"),
    (610, 590, 775, 590, "#AA6A4D"),
]:
    grain = Line(Point(x1, y1), Point(x2, y2))
    grain.fill_colour = colour
    grain.outline_width = 2
    grain.draw(Bar)

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

#Jacket shading and sleeve creases add a little depth
left_jacket_shadow = Polygon([
    Point(300, 45), Point(318, 55), Point(328, 450), Point(280, 460)
])
left_jacket_shadow.fill_colour = "#29377F"
left_jacket_shadow.outline_colour = "#29377F"
left_jacket_shadow.draw(Bar)

right_jacket_shadow = Polygon([
    Point(500, 45), Point(520, 35), Point(520, 460), Point(474, 450)
])
right_jacket_shadow.fill_colour = "#394B9B"
right_jacket_shadow.outline_colour = "#394B9B"
right_jacket_shadow.draw(Bar)

left_sleeve_crease = Line(Point(263, 300), Point(242, 365))
left_sleeve_crease.fill_colour = "#D8D2CC"
left_sleeve_crease.outline_width = 2
left_sleeve_crease.draw(Bar)

right_sleeve_crease = Line(Point(537, 300), Point(558, 365))
right_sleeve_crease.fill_colour = "#D8D2CC"
right_sleeve_crease.outline_width = 2
right_sleeve_crease.draw(Bar)

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

tie_highlight = Line(Point(396, 55), Point(398, 205))
tie_highlight.fill_colour = "#C34A61"
tie_highlight.outline_width = 2
tie_highlight.draw(Bar)

#Small shirt buttons
for y in (315, 350, 385, 420):
    button = Circle(Point(400, y), 3)
    button.fill_colour = "#9A9A9A"
    button.outline_colour = "#777777"
    button.draw(Bar)

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

#Hand details
for start, end in [
    (Point(145, 494), Point(168, 499)),
    (Point(655, 494), Point(632, 499)),
]:
    crease = Line(start, end)
    crease.fill_colour = "#C9875F"
    crease.outline_width = 2
    crease.draw(Bar)

for x, y in [
    (137, 536), (150, 544), (163, 544), (176, 536),
    (663, 536), (650, 544), (637, 544), (624, 536),
]:
    nail = Oval(Point(x - 3, y - 2), Point(x + 3, y + 2))
    nail.fill_colour = "#F2C19C"
    nail.outline_colour = "#F2C19C"
    nail.draw(Bar)


if __name__ == "__main__":
    bartender()
    Bar.close()
