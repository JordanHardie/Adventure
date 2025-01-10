import os
import pygame
from src.engine.game_engine import GameEngine # type: ignore

def main():
    os.system('cls' if os.name=='nt' else 'clear')  # Clear console
    game = GameEngine()
    try:
        game.run()
    finally:
        pygame.quit()
        os._exit(0)  # Force exit all windows

if __name__ == "__main__":
    main()