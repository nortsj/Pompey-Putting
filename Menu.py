"""
Menu.py - the title screen.  main_menu() returns when PLAY is clicked.
"""

from graphix import Window, Circle, Line, Rectangle, Text, Point

#Main
def main_menu():
    Main = Window("Pompey Putting", 800, 600)
    Main.background_colour = "#7f2525"


#Moon
    moon = Circle(Point(400, 270), 95)
    moon.fill_colour = "white"
    moon.outline_colour = "white"
    moon.draw(Main)

    moon_cutout = Circle(Point(400, 235), 85)
    moon_cutout.fill_colour = "#7f2525"
    moon_cutout.outline_colour = "#7f2525"
    moon_cutout.draw(Main)

#Star
    line1 = Line(Point(300, 150), Point(500, 150))
    line1.fill_colour = "white"
    line1.outline_width = 2
    line1.draw(Main)

    line2 = Line(Point(400, 50), Point(400, 250))
    line2.fill_colour = "white"
    line2.outline_width = 2
    line2.draw(Main)

    line3 = Line(Point(330, 80), Point(470, 220))
    line3.fill_colour = "white"
    line3.outline_width = 2
    line3.draw(Main)

    line4 = Line(Point(330, 220), Point(470, 80))
    line4.fill_colour = "white"
    line4.outline_width = 2
    line4.draw(Main)


#Golf club
    shaft = Line(Point(250, 375), Point(470, 425))
    shaft.fill_colour = "#9B593D"
    shaft.outline_width = 10
    shaft.draw(Main)

    club_head = Line(Point(480, 400), Point(468, 440))
    club_head.fill_colour = "#777777"
    club_head.outline_width = 12
    club_head.draw(Main)


#Play button
    playBut = Rectangle(Point(250, 480), Point(550, 560))
    playBut.fill_colour = "#7b2028"
    playBut.outline_colour = "#b8b8b8"
    playBut.outline_width = 3
    playBut.draw(Main)

    playText = Text(Point(400, 520), "PLAY")
    playText.size = 24
    playText.style = "bold"
    playText.text_colour = "white"
    playText.draw(Main)

    while True:
        click = Main.get_mouse()
        if 250 <= click.x <= 550 and 480 <= click.y <= 560:
            Main.close()
            break


if __name__ == "__main__":
    main_menu()
