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


#Background
Bar = Window("Pompey Putting - Bar", 800, 600)
Bar.background_colour = "#7f2525"

#Torso

#Left arm

#Right arm

#Bar