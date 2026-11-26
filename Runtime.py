from graphix import GraphixError
from Menu import main_menu
from Game import main as game_main


def visit_bar():
    from bar import bartender
    return bartender()


def run():
    try:
        while True:
            main_menu()
            game_main(bar_callback=visit_bar)
    except GraphixError:
        return


if __name__ == "__main__":
    run()
