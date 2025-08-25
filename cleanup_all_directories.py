#!/usr/bin/env python3
"""
Complete CIQ Brand Assets Cleanup - All Directories
Applies the successful fuzzball approach to all logo directories
"""

import os
from pathlib import Path

def clean_directory(dir_path):
    """Clean a single directory using the proven approach"""
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"  ⚠️  Directory {dir_path.name} not found, skipping")
        return 0, 0
    
    print(f"\n🧹 Cleaning {dir_path.name}...")
    
    # Count current files
    all_files = [f for f in dir_path.iterdir() if f.is_file()]
    svg_files = [f for f in all_files if f.name.lower().endswith('.svg')]
    s_files = [f for f in all_files if '_S.png' in f.name]
    m_files = [f for f in all_files if '_M.png' in f.name]
    l_files = [f for f in all_files if '_L.png' in f.name]
    other_files = [f for f in all_files if f.name.lower().endswith(('.ai', '.pdf'))]
    
    print(f"  📊 Current: {len(all_files)} total files")
    print(f"     - SVGs: {len(svg_files)}")
    print(f"     - Small (_S): {len(s_files)}")
    print(f"     - Medium (_M): {len(m_files)}")
    print(f"     - Large (_L): {len(l_files)}")
    print(f"     - Other (.ai/.pdf): {len(other_files)}")
    
    if len(svg_files) == 0 and len(s_files) == 0 and len(m_files) == 0 and len(other_files) == 0:
        print(f"  ✅ {dir_path.name} is already clean!")
        return len(all_files), 0
    
    # Clean up files
    removed_count = 0
    kept_count = 0
    
    for file_path in all_files:
        filename_lower = file_path.name.lower()
        
        # Should we remove this file?
        should_remove = (
            filename_lower.endswith('.svg') or 
            '_s.png' in filename_lower or 
            '_m.png' in filename_lower or
            filename_lower.endswith('.ai') or
            filename_lower.endswith('.pdf')
        )
        
        if should_remove:
            try:
                file_path.unlink()
                removed_count += 1
            except Exception as e:
                print(f"    ⚠️  Error removing {file_path.name}: {e}")
        else:
            kept_count += 1
    
    print(f"  📊 Results: {kept_count} kept, {removed_count} removed")
    return kept_count, removed_count

def main():
    print("🚀 Complete CIQ Brand Assets Cleanup - All Directories")
    print("Using the proven approach that worked for fuzzball\n")
    
    # Define all directories to clean
    directories_to_clean = [
        "CIQ-logos",
        "fuzzball-logos",
        "Apptainer-logos", 
        "Warewulf-Pro-logos",
        "Ascender-Pro-logos",
        "Bridge-logos",
        "CIQ-Support-logos",
        "rlc_logos",
        "rlc_ai_logos",
        "rlc_hardened_logos", 
        "rlc_lts_logos"
    ]
    
    print(f"🎯 Directories to clean: {len(directories_to_clean)}")
    for dir_name in directories_to_clean:
        if Path(dir_name).exists():
            print(f"  ✅ {dir_name}")
        else:
            print(f"  ❌ {dir_name} (not found)")
    
    # Ask for confirmation
    print(f"\n🤔 This will remove ALL:")
    print("   - .svg files")
    print("   - _S.png files (small)")
    print("   - _M.png files (medium)")
    print("   - .ai/.pdf files")
    print("   And keep only _L.png files (large)")
    print()
    
    response = input("Type 'yes' to proceed with full cleanup: ").strip().lower()
    if response != 'yes':
        print("❌ Cleanup cancelled")
        return
    
    print("\n🧹 Starting complete cleanup...")
    
    # Track totals
    total_kept = 0
    total_removed = 0
    cleaned_dirs = 0
    
    # Clean each directory
    for dir_name in directories_to_clean:
        dir_path = Path(dir_name)
        kept, removed = clean_directory(dir_path)
        total_kept += kept
        total_removed += removed
        if removed > 0:
            cleaned_dirs += 1
    
    # Final summary
    print(f"\n✅ Complete cleanup finished!")
    print(f"📊 **FINAL SUMMARY:**")
    print(f"   🗂️  Directories processed: {len(directories_to_clean)}")
    print(f"   🧹 Directories cleaned: {cleaned_dirs}")
    print(f"   ✅ Files kept: {total_kept}")
    print(f"   ❌ Files removed: {total_removed}")
    
    # Show what should be left
    print(f"\n📋 **EXPECTED STRUCTURE PER DIRECTORY:**")
    print(f"   • Product-Icon_blk_L.png (black icon)")
    print(f"   • Product-Icon_wht_L.png (white icon)")
    print(f"   • Product_logo_h-blk_L.png (horizontal black)")
    print(f"   • Product_logo_h-wht_L.png (horizontal white)")
    print(f"   • Product_logo_v-blk_L.png (vertical black)")  
    print(f"   • Product_logo_v-wht_L.png (vertical white)")
    print(f"   = ~6 clean PNG files per directory")
    
    print(f"\n🎯 **NEXT STEPS:**")
    print(f"   1. Check the cleaned directories look correct")
    print(f"   2. git add . && git commit -m 'Clean all brand assets'")
    print(f"   3. git push origin main")
    print(f"   4. FastMCP Cloud will auto-update with clean structure")

if __name__ == "__main__":
    main()
