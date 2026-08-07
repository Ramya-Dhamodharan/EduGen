# gen_imports.py
import subprocess
import sys
from pathlib import Path

# Directories you want to automatically manage
TARGET_DIRECTORIES = [
    "./app/schemas",
    "./app/models",
    "./app/services",
    "./app/routes",
    "./app/repositories"
]

def run():
    print("🚀 Starting auto-import generation...")
    for folder in TARGET_DIRECTORIES:
        dir_path = Path(folder)
        
        # Guard: mkinit needs an __init__.py file present to scan the directory
        init_file = dir_path / "__init__.py"
        if dir_path.exists() and not init_file.exists():
            init_file.touch()
            print(f"📁 Created missing placeholder: {init_file}")

        print(f"Parsing module: {folder}")
        # Build an isolated execution array for each individual directory
        cmd = ["uvx", "mkinit", folder, "--write", "--relative"]
        
        # Execute natively. setting shell=True handles Windows execution mappings
        result = subprocess.run(cmd, shell=True)
        
        if result.returncode != 0:
            print(f"❌ Error occurred while processing {folder}")
            sys.exit(result.returncode)
            
    print("✨ All __init__.py files synchronized successfully!")

if __name__ == "__main__":
    run()
