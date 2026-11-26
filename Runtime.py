"""
Runtime.py - run this file to play.
Menu -> Bar (choose drinks) -> Game (played with those drink effects).
Keep graphix.py in the same folder.
"""

from graphix import GraphixError
from Menu import main_menu
from bar import bartender
from Game import main as game_main


def run():
    try:
        main_menu()
        effects = bartender()
        game_main(effects)
    except GraphixError:
        # a window was closed with its X button: just stop quietly
        pass


if __name__ == "__main__":
    run()
