from graphix import *

#Main
def main_menu():
    Main = Window("Pompey Putting", 800, 600)
    Main.background_colour = "#7f2525"

    title = Text(Point(400, 140), "POMPEY PUTTING")
    title.typeface = "helvetica"
    title.size = 32
    title.style = "bold"
    title.text_colour = "#8b8b8b"
    title.draw(Main)



 # Play button
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
