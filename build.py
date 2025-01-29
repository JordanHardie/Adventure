import os
import sys
import shutil
import PyInstaller.__main__
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor

class GameBuilder:
    def __init__(self):
        self.project_root = os.path.abspath(os.path.dirname(__file__))
        self.src_dir = os.path.join(self.project_root, 'src')
        self.config_dir = os.path.join(self.src_dir, 'config')
        self.dist_dir = os.path.join(self.project_root, 'dist')
        self.build_dir = os.path.join(self.project_root, 'build')
        
    def setup_directories(self):
        """Create necessary directories."""
        for directory in [self.src_dir, self.config_dir, self.dist_dir, self.build_dir]:
            os.makedirs(directory, exist_ok=True)
            
    def copy_config_files(self):
        """Copy configuration files to the config directory."""
        config_files = [
            'biomes.json', 'items.json', 'monsters.json',
            'prefixes.json', 'descriptions.json', 'font_support.json'
        ]
        
        def copy_file(filename: str):
            src = os.path.join(self.project_root, filename)
            dst = os.path.join(self.config_dir, filename)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                
        with ThreadPoolExecutor() as executor:
            executor.map(copy_file, config_files)
            
    def create_main_file(self):
        """Create the main.py file."""
        main_path = os.path.join(self.src_dir, 'main.py')
        main_content = '''from src.engine.game_engine import GameEngine

def main():
    try:
        game = GameEngine()
        game.run()
    except Exception as e:
        import traceback
        with open('error_log.txt', 'w') as f:
            f.write(f"Error: {str(e)}\\n")
            f.write(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()
'''
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(main_content)
            
    def get_pyinstaller_args(self) -> List[str]:
        """Configure PyInstaller arguments."""
        main_path = os.path.join(self.src_dir, 'main.py')
        data_files = [(os.path.join(self.config_dir, f), f'src/config') 
                     for f in os.listdir(self.config_dir) 
                     if f.endswith('.json')]
                     
        args = [
            main_path,
            '--name=Adventure!',
            '--onefile',
            '--noconsole',
            '--clean',
            f'--distpath={self.dist_dir}',
            f'--workpath={self.build_dir}',
            '--add-data', f'{";".join(data_files[0])}' if sys.platform == 'win32'
                         else f'{":".join(data_files[0])}'
        ]
        
        # Add remaining data files
        for src, dst in data_files[1:]:
            args.extend(['--add-data', 
                        f'{src};{dst}' if sys.platform == 'win32' else f'{src}:{dst}'])
            
        return args
        
    def build(self) -> Dict[str, str]:
        """Execute the build process."""
        try:
            self.setup_directories()
            self.copy_config_files()
            self.create_main_file()
            
            PyInstaller.__main__.run(self.get_pyinstaller_args())
            
            executable = 'Adventure.exe' if sys.platform == 'win32' else 'Adventure'
            executable_path = os.path.join(self.dist_dir, executable)
            
            return {
                'status': 'success',
                'executable': executable_path,
                'size': f"{os.path.getsize(executable_path) / (1024*1024):.2f} MB"
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

def main():
    builder = GameBuilder()
    result = builder.build()
    
    if result['status'] == 'success':
        print(f"""
Build completed successfully!
Executable: {result['executable']}
Size: {result['size']}
""")
    else:
        print(f"Build failed: {result['message']}")

if __name__ == '__main__':
    main()