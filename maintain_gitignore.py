#!/usr/bin/env python3
"""
.gitignore maintenance script for TutorDraw
Helps verify and update the .gitignore file
"""
import os
import subprocess
import sys
from pathlib import Path

def check_gitignore():
    """Check if .gitignore is working properly"""
    print("Checking .gitignore effectiveness...")
    
    # Run git status to see ignored files
    try:
        result = subprocess.run(['git', 'status', '--ignored'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            ignored_section = False
            ignored_files = []
            
            for line in lines:
                if 'Ignored files:' in line:
                    ignored_section = True
                    continue
                elif ignored_section and line.strip().startswith('('):
                    continue
                elif ignored_section and line.strip():
                    if line.strip().startswith('.'):
                        ignored_files.append(line.strip())
                
            if ignored_files:
                print("✅ Currently ignored files/directories:")
                for file in ignored_files:
                    print(f"  {file}")
            else:
                print("ℹ️  No files are currently being ignored")
        else:
            print("❌ Error running git status")
            print(result.stderr)
            
    except FileNotFoundError:
        print("❌ Git not found. Please install git first.")
        return False
    
    return True

def verify_common_patterns():
    """Verify that common build artifacts are ignored"""
    print("\nVerifying common patterns...")
    
    common_patterns = [
        '__pycache__/',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.venv/',
        'venv/',
        'env/',
        'build/',
        'dist/',
        '*.egg-info/',
        '*.spec',
        '*.exe',
        '*.app',
        '*.msi',
        '*.dmg',
        '*.deb',
        '*.rpm',
        '*.AppImage',
        '*.apk',
        'build_dist/',
        '.DS_Store',
        'Thumbs.db'
    ]
    
    missing_patterns = []
    
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            
        for pattern in common_patterns:
            if pattern not in gitignore_content:
                missing_patterns.append(pattern)
    
    if missing_patterns:
        print("⚠️  Missing patterns in .gitignore:")
        for pattern in missing_patterns:
            print(f"  {pattern}")
        return False
    else:
        print("✅ All common patterns are present in .gitignore")
        return True

def add_missing_patterns():
    """Add commonly missing patterns to .gitignore"""
    print("\nAdding missing patterns...")
    
    additional_patterns = [
        "",
        "# Additional patterns for TutorDraw",
        "*.log",
        "logs/",
        "temp/",
        "tmp/",
        "*.tmp",
        "*.temp",
        "screenshots/",
        "recordings/",
        "*.bak",
        "*.backup",
        "*~",
        ".vscode/",
        ".idea/",
        "*.swp",
        "*.swo"
    ]
    
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'a') as f:
            f.write('\n'.join(additional_patterns) + '\n')
        print("✅ Added additional patterns to .gitignore")
    else:
        print("❌ .gitignore file not found")

def main():
    """Main function"""
    print("🔧 .gitignore Maintenance Tool for TutorDraw")
    print("=" * 50)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("Initializing git repository...")
        subprocess.run(['git', 'init'], cwd='.')
    
    # Check current .gitignore status
    check_gitignore()
    
    # Verify patterns
    patterns_ok = verify_common_patterns()
    
    # Add missing patterns if needed
    if not patterns_ok:
        response = input("\nWould you like to add missing patterns? (y/n): ")
        if response.lower() == 'y':
            add_missing_patterns()
            print("\nRechecking after updates...")
            verify_common_patterns()
    
    print("\n💡 Tips:")
    print("- Run 'git status --ignored' to see currently ignored files")
    print("- Run 'git add .' to stage all non-ignored files")
    print("- Run 'git clean -fd' to remove untracked files (be careful!)")
    print("- Edit .gitignore manually to customize ignored patterns")

if __name__ == "__main__":
    main()