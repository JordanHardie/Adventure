from src.engine.game_engine import GameEngine

def main():
    try:
        game = GameEngine()
        game.run()
    except Exception as e:
        import traceback
        with open('error_log.txt', 'w') as f:
            f.write(f"Error: {str(e)}\n")
            f.write(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()
