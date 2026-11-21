from Menu import main_menu

def run():
    main_menu()

    from Game import main as game_main
    game_main()

    from bar import bartender, Bar
    bartender()
    Bar.close()

if __name__ == "__main__":
    run()