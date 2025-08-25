#!/usr/bin/env python3
"""
Simple CIQ Brand Assets Cleanup - Debug Version
Shows exactly what it's doing step by step
"""

import os
import shutil
from pathlib import Path

def main():
    print("🔍 CIQ Brand Assets Cleanup - Debug Mode")
    print(f"📁 Current directory: {os.getcwd()}")
    print()
    
    # Check if we're in the right place
    current_dir = Path('.')
    expected_files = ['server.py', 'cleanup_and_reorganize.py', 'fuzzball-logos']
    
    print("🔎 Checking for expected files/directories:")
    for item in expected_files:
        if Path(item).exists():
            print(f"  ✅ Found: {item}")
        else:
            print(f"  ❌ Missing: {item}")
    print()
    
    # Step 1: Check fuzzball directory contents
    fuzzball_dir = Path('fuzzball-logos')
    if fuzzball_dir.exists():
        print("📋 Current fuzzball-logos contents:")
        files = list(fuzzball_dir.iterdir())
        print(f"  Total files: {len(files)}")
        
        svg_files = [f for f in files if f.name.endswith('.svg')]
        s_files = [f for f in files if '_S.png' in f.name]
        m_files = [f for f in files if '_M.png' in f.name]  
        l_files = [f for f in files if '_L.png' in f.name]
        
        print(f"  📊 SVG files: {len(svg_files)}")
        print(f"  📊 Small (_S) files: {len(s_files)}")
        print(f"  📊 Medium (_M) files: {len(m_files)}")
        print(f"  📊 Large (_L) files: {len(l_files)}")
        
        if svg_files:
            print("  🎯 SVG files to remove:")
            for f in svg_files[:3]:  # Show first 3
                print(f"    - {f.name}")
            if len(svg_files) > 3:
                print(f"    ... and {len(svg_files) - 3} more")
        
        if s_files:
            print("  🎯 Small files to remove:")
            for f in s_files[:3]:  # Show first 3
                print(f"    - {f.name}")
            if len(s_files) > 3:
                print(f"    ... and {len(s_files) - 3} more")
                
        if m_files:
            print("  🎯 Medium files to remove:")
            for f in m_files[:3]:  # Show first 3
                print(f"    - {f.name}")
            if len(m_files) > 3:
                print(f"    ... and {len(m_files) - 3} more")
        print()
    else:
        print("❌ fuzzball-logos directory not found!")
        return
    
    # Ask for confirmation before proceeding
    print("🤔 Do you want to proceed with cleanup?")
    print("   This will:")
    print("   - Remove ALL SVG files")
    print("   - Remove ALL _S.png and _M.png files")  
    print("   - Keep only _L.png files")
    print()
    
    response = input("Type 'yes' to continue: ").strip().lower()
    if response != 'yes':
        print("❌ Cleanup cancelled")
        return
    
    print("\n🧹 Starting cleanup...")
    
    # Step 2: Actually clean fuzzball directory
    removed_count = 0
    kept_count = 0
    
    for file_path in fuzzball_dir.iterdir():
        if file_path.is_file():
            filename = file_path.name.lower()
            
            # Should we remove this file?
            should_remove = (
                filename.endswith('.svg') or 
                '_s.png' in filename or 
                '_m.png' in filename or
                filename.endswith('.ai') or
                filename.endswith('.pdf')
            )
            
            if should_remove:
                print(f"  ❌ Removing: {file_path.name}")
                try:
                    file_path.unlink()
                    removed_count += 1
                except Exception as e:
                    print(f"    ⚠️  Error removing {file_path.name}: {e}")
            else:
                print(f"  ✅ Keeping: {file_path.name}")
                kept_count += 1
    
    print(f"\n📊 Fuzzball cleanup results:")
    print(f"   ❌ Files removed: {removed_count}")
    print(f"   ✅ Files kept: {kept_count}")
    
    # Show what's left
    remaining_files = list(fuzzball_dir.iterdir())
    print(f"   📁 Files remaining: {len(remaining_files)}")
    
    if remaining_files:
        print("   📋 Remaining files:")
        for f in remaining_files:
            if f.is_file():
                print(f"     - {f.name}")
    
    print("\n✅ Cleanup complete!")
    print("📌 To push changes: git add . && git commit -m 'Clean up fuzzball assets' && git push")

if __name__ == "__main__":
    main()
