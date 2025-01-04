import os
import shutil
import PyInstaller.__main__

project_root = r"C:\Users\xcool\Desktop\Python Projects\Adventure!"
src_dir = os.path.join(project_root, 'src')
main_path = os.path.join(src_dir, 'main.py')
config_dir = os.path.join(src_dir, 'config')
biomes_path = os.path.join(config_dir, 'biomes.json')
dist_dir = os.path.join(project_root, 'dist')

os.makedirs(src_dir, exist_ok=True)
os.makedirs(config_dir, exist_ok=True)
os.makedirs(dist_dir, exist_ok=True)

with open(main_path, 'w', encoding='utf-8') as f:
    f.write('''from src.engine.game_engine import GameEngine

def main():
    game = GameEngine()
    game.run()

if __name__ == "__main__":
    main()
''')

if os.path.exists('biomes.json'):
    shutil.copy('biomes.json', biomes_path)

PyInstaller.__main__.run([
    main_path,
    '--onefile',
    '--noconsole',
    '--name=Adventure',
    f'--add-data={biomes_path};src/config',
    f'--distpath={dist_dir}'
])
