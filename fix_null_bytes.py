import os
import sys

def fix_file_encoding_issues(file_path):
    """Remove null bytes and invalid Unicode characters from a file."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        has_null_bytes = b'\x00' in content
        has_invalid_unicode = False
        try:
            content.decode('utf-8')
        except UnicodeDecodeError:
            has_invalid_unicode = True
        
        if has_null_bytes or has_invalid_unicode:
            print(f"Fixing encoding issues in {file_path}")
            backup_path = file_path + '.bak'
            with open(backup_path, 'wb') as f:
                f.write(content)
            fixed_content = content.replace(b'\x00', b'')
            if os.path.basename(file_path) == "__init__.py":
                fixed_content = b"# This file is intentionally left empty\n"
            else:
                try:
                    decoded = fixed_content.decode('utf-8', errors='replace')
                    fixed_content = decoded.encode('utf-8')
                except Exception:
                    pass
            with open(file_path, 'wb') as f:
                f.write(fixed_content)
            
            return True
        else:
            print(f"No encoding issues found in {file_path}")
            return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def scan_directory(directory='.'):
    fixed_files = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_file_encoding_issues(file_path):
                    fixed_files += 1
    
    return fixed_files

def fix_package_init_files(directory='.'):
    fixed_files = 0
    
    for root, dirs, files in os.walk(directory):
        if os.path.basename(root) == 'src' or root.startswith(os.path.join(directory, 'src')):
            init_path = os.path.join(root, '__init__.py')
            if not os.path.exists(init_path):
                print(f"Creating missing {init_path}")
                with open(init_path, 'w') as f:
                    f.write("# This file is intentionally left empty\n")
                fixed_files += 1
            elif os.path.isfile(init_path):
                if fix_file_encoding_issues(init_path):
                    fixed_files += 1
    
    return fixed_files

if __name__ == "__main__":
    print("Python File Encoding Fixer - Venus Tracking Project")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.isfile(file_path):
            if fix_file_encoding_issues(file_path):
                print(f"Successfully fixed encoding issues in {file_path}")
            else:
                print(f"No encoding issues found or couldn't fix {file_path}")
        else:
            print(f"File not found: {file_path}")
    else:
        print("Scanning directory for Python files with encoding issues...")
        fixed = scan_directory()
        print("\nChecking package __init__.py files...")
        fixed += fix_package_init_files()
        
        if fixed > 0:
            print(f"\nSuccessfully fixed {fixed} file(s)")
            print("Please try running your application again.")
        else:
            print("\nNo files with encoding issues were found.")
            print("If you're still experiencing issues, please check:")
            print("1. Make sure Python packages are installed correctly")
            print("2. Check import paths in your modules")
            print("3. Verify file permissions on the src directory")
    
    print("\nNote: Backup files with .bak extension were created for modified files.")
