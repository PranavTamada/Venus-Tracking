import os
import sys
import shutil
import subprocess

def print_header(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)

def fix_encoding_issues():
    print_header("FIXING ENCODING ISSUES")
    if os.path.exists('fix_null_bytes.py'):
        try:
            subprocess.run([sys.executable, 'fix_null_bytes.py'], check=True)
            return True
        except subprocess.CalledProcessError:
            print("Error running fix_null_bytes.py")
            return False
    else:
        print("fix_null_bytes.py not found")
        return False

def recreate_init_files():
    print_header("RECREATING __INIT__.PY FILES")
    
    count = 0
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    
    if not os.path.exists(src_dir):
        print(f"Error: src directory not found at {src_dir}")
        return count
    for root, dirs, files in os.walk(src_dir):
        init_path = os.path.join(root, '__init__.py')
        with open(init_path, 'w') as f:
            f.write("# This file is intentionally left empty\n")
        
        print(f"Created/reset {init_path}")
        count += 1
    return count

def rebuild_src_if_needed():
    print_header("CHECKING SRC DIRECTORY STRUCTURE")
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    if not os.path.exists(src_dir):
        print("src directory does not exist. It will be created.")
        os.makedirs(src_dir)
    expected_dirs = [
        'position_tracking',
        'atmospheric_model',
        'data_logging',
        'config',
        'utils'
    ]
    
    missing_dirs = []
    for directory in expected_dirs:
        dir_path = os.path.join(src_dir, directory)
        if not os.path.exists(dir_path):
            missing_dirs.append(directory)
            os.makedirs(dir_path)
            print(f"Created missing directory: {dir_path}")
    
    if missing_dirs:
        print(f"Created {len(missing_dirs)} missing directories in src/")
        recreate_init_files()
        return True
    else:
        print("All expected directories found in src/")
        return False

def clean_pycache():
    print_header("CLEANING PYTHON CACHE FILES")
    count = 0
    for root, dirs, files in os.walk('.', topdown=True):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            # Prevent os.walk from descending into the directory we are about to delete
            dirs.remove('__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"Removed: {pycache_path}")
                count += 1
            except Exception as e:
                print(f"Error removing {pycache_path}: {e}")
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"Removed: {pyc_path}")
                    count += 1
                except Exception as e:
                    print(f"Error removing {pyc_path}: {e}")
    if count > 0:
        print(f"Removed {count} Python cache files/directories")
    else:
        print("No Python cache files found")
    
    return count

def main():
    print("Venus Tracking Project - Comprehensive Cleanup Utility")
    print("This will fix encoding issues and ensure proper project structure.\n")
    clean_pycache()
    fix_encoding_issues()
    rebuild_needed = rebuild_src_if_needed()
    init_count = recreate_init_files()
    print_header("CLEANUP COMPLETE")
    print(f"Created/reset {init_count} __init__.py files")
    print("\nNext steps:")
    print("1. Try running your application again:")
    print("   python demo_enhanced.py")
    print("2. If you still have issues, check the import statements in your files")
    print("3. Make sure all required Python packages are installed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCleanup interrupted by user")
    except Exception as e:
        print(f"\nError during cleanup: {e}")
        import traceback
        traceback.print_exc()
