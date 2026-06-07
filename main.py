import pygame

from game import Game


def main():
    pygame.init()
    pygame.display.set_caption("Zombie Survival")

    game = Game()
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()
