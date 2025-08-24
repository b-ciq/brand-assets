#!/usr/bin/env python3
"""
Asset Metadata Generator - RECURSIVE VERSION
Automatically scans asset directories (including subdirectories) and generates metadata JSON files
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Base GitHub raw URL for assets
BASE_URL = "https://raw.githubusercontent.com/b-ciq/brand-assets/main"

def extract_product_info_from_path(filepath: Path) -> tuple[str, str]:
    """
    Extract product name and variant from file path
    Examples:
    - RLC(X)-logos/RLC logo/RLC_Logo_blk_h_L.png → product: rlc, variant: rlc
    - RLC(X)-logos/RLC-AI logo/RLC-AI_Logo_blk_h_L.png → product: rlc, variant: rlc-ai
    """
    parts = filepath.parts
    
    # Find the main product directory (ends with -logos)
    main_product = None
    for part in parts:
        if part.endswith('-logos'):
            main_product = part.replace('-logos', '').lower()
            main_product = main_product.replace('(', '').replace(')', '')  # Remove (X) from RLC(X)
            break
    
    if not main_product:
        main_product = 'unknown'
    
    # Check if there's a subdirectory that indicates a product variant
    parent_dir = filepath.parent.name
    if parent_dir.endswith(' logo'):
        variant = parent_dir.replace(' logo', '').lower()
    elif parent_dir != filepath.parts[0]:  # Not in root logo directory
        variant = parent_dir.lower()
    else:
        variant = main_product
    
    return main_product, variant

def create_icon_metadata(filename: str, product: str, color: str, size: str, ext: str) -> Dict[str, Any]:
    """Create metadata for icon files"""
    background = 'light' if color.lower() == 'blk' else 'dark'
    size_full = {'L': 'large', 'M': 'medium', 'S': 'small'}.get(size.upper(), size)
    
    return {
        "filename": filename,
        "description": f"{product.title()} icon ({color}) for {background} backgrounds - {size_full.title()}",
        "layout": "icon",
        "color": "black" if color.lower() == 'blk' else "white",
        "background": background,
        "size": size_full,
        "use_cases": ["favicon", "app_icon", "small_spaces", "avatars"],
        "guidance": f"Perfect for tight spaces where you need just the {product.title()} symbol",
        "format": ext,
        "product": product
    }

def create_logo_metadata(filename: str, product: str, color: str, layout_code: str, size: str, ext: str) -> Dict[str, Any]:
    """Create metadata for logo files"""
    layout = 'horizontal' if layout_code.lower() == 'h' else 'vertical'
    background = 'light' if color.lower() == 'blk' else 'dark'
    size_full = {'L': 'large', 'M': 'medium', 'S': 'small'}.get(size.upper(), size)
    
    if layout == 'horizontal':
        use_cases = ["headers", "business_cards", "letterhead", "wide_banners"]
        guidance = f"Best for wide spaces - business cards, website headers, email signatures"
    else:  # vertical
        use_cases = ["tall_banners", "social_media_profile", "mobile_layout", "poster"]
        guidance = f"Perfect for tall/narrow spaces - social media profiles, mobile layouts"
    
    return {
        "filename": filename,
        "description": f"{product.title()} {layout} logo ({color}) for {background} backgrounds - {size_full.title()}",
        "layout": layout,
        "color": "black" if color.lower() == 'blk' else "white",
        "background": background,
        "size": size_full,
        "use_cases": use_cases,
        "guidance": guidance,
        "format": ext,
        "product": product
    }

def process_match(groups, pattern_type: str, filename: str, product: str) -> Dict[str, Any]:
    """Process regex match based on pattern type"""
    
    if pattern_type in ['icon_pattern1', 'icon_pattern2']:
        # Icon patterns: (product, color, size, ext)
        _, color, size, ext = groups
        return create_icon_metadata(filename, product, color, size, ext)
    
    elif pattern_type in ['logo_pattern1', 'logo_pattern2']:
        # Logo patterns: (product, color, layout, size, ext)
        _, color, layout_code, size, ext = groups
        return create_logo_metadata(filename, product, color, layout_code, size, ext)
    
    elif pattern_type == 'mixed_pattern':
        # Mixed pattern: (product, layout, color, size, ext)
        _, layout_code, color, size, ext = groups
        return create_logo_metadata(filename, product, color, layout_code, size, ext)
    
    elif pattern_type == 'svg_logo_pattern':
        # SVG logo: (product, layout, color, ext)
        _, layout_code, color, ext = groups
        layout = 'horizontal' if layout_code.lower() == 'h' else 'vertical'
        background = 'light' if color.lower() == 'blk' else 'dark'
        
        return {
            "filename": filename,
            "description": f"{product.title()} {layout} logo ({color}) for {background} backgrounds - SVG",
            "layout": layout,
            "color": "black" if color.lower() == 'blk' else "white",
            "background": background,
            "size": "vector",
            "use_cases": ["scalable", "web", "print"],
            "guidance": f"Vector format - scales to any size perfectly",
            "format": ext,
            "product": product
        }
    
    elif pattern_type == 'icon_svg_pattern':
        # SVG icon: (product, color, ext)
        _, color, ext = groups
        background = 'light' if color.lower() == 'blk' else 'dark'
        
        return {
            "filename": filename,
            "description": f"{product.title()} icon ({color}) for {background} backgrounds - SVG",
            "layout": "icon",
            "color": "black" if color.lower() == 'blk' else "white",
            "background": background,
            "size": "vector",
            "use_cases": ["scalable", "favicon", "app_icon"],
            "guidance": f"Vector format - scales to any size perfectly",
            "format": ext,
            "product": product
        }
    
    # Fallback
    return None

def parse_universal_filename(filename: str, product_variant: str) -> Dict[str, Any]:
    """Enhanced universal parser for all naming patterns"""
    
    # All the patterns we've seen - try each one
    patterns = [
        # Product-Icon_color_size.ext
        (r'(\w+)-Icon_(\w+)_([LMS])\.(\w+)', 'icon_pattern1'),
        # Product-Logo_color_layout_size.ext  
        (r'(\w+)-Logo_(\w+)_([hv])_([LMS])\.(\w+)', 'logo_pattern1'),
        # Product_Logo_color_layout_size.ext
        (r'(\w+)_Logo_(\w+)_([hv])_([LMS])\.(\w+)', 'logo_pattern2'),
        # Product_logo_layout-color.ext
        (r'(\w+)_logo_([hv])-(\w+)\.(\w+)', 'svg_logo_pattern'),
        # Product_icon_color_size.ext
        (r'(\w+)_icon_(\w+)_([LMS])\.(\w+)', 'icon_pattern2'),
        # Product_icon-color.ext or Product_icon_color.ext
        (r'(\w+)_icon[-_](\w+)\.(\w+)', 'icon_svg_pattern'),
        # Product_logo_layout-color_size.ext  
        (r'(\w+)_logo_([hv])-(\w+)_([LMS])\.(\w+)', 'mixed_pattern'),
    ]
    
    for pattern, pattern_type in patterns:
        match = re.match(pattern, filename, re.IGNORECASE)
        if match:
            return process_match(match.groups(), pattern_type, filename, product_variant)
    
    # Fallback
    return {
        "filename": filename,
        "description": f"{product_variant.title()} logo variant: {filename}",
        "layout": "unknown",
        "color": "unknown", 
        "background": "unknown",
        "size": "unknown",
        "use_cases": ["general"],
        "guidance": f"{product_variant.title()} logo variant",
        "format": filename.split('.')[-1] if '.' in filename else "unknown",
        "product": product_variant
    }

def scan_all_assets_recursive(base_path: str = ".") -> Dict[str, Dict[str, Any]]:
    """Recursively scan all directories for logo assets"""
    
    all_assets = {}
    base = Path(base_path)
    
    print(f"🔍 Scanning all directories recursively from: {base}")
    
    # Find all directories ending with -logos
    logo_dirs = list(base.glob("*-logos"))
    
    for logo_dir in logo_dirs:
        print(f"📁 Found logo directory: {logo_dir}")
        
        # Extract main product name
        main_product = logo_dir.name.replace('-logos', '').lower()
        main_product = main_product.replace('(', '').replace(')', '')  # Remove (X) from RLC(X)
        
        # Recursively scan this directory and all subdirectories
        for root, dirs, files in os.walk(logo_dir):
            root_path = Path(root)
            
            # Skip archived directories
            if 'archived' in root_path.name.lower() or root_path.name.startswith('_'):
                print(f"   ⏩ Skipping archived: {root_path}")
                continue
                
            for filename in files:
                if filename.startswith('.') or filename.endswith('.DS_Store'):
                    continue
                
                file_path = root_path / filename
                
                # Determine product variant from path
                _, product_variant = extract_product_info_from_path(file_path)
                
                # Parse the filename
                metadata = parse_universal_filename(filename, product_variant)
                
                if metadata:
                    # Build relative path for URL
                    relative_path = file_path.relative_to(base)
                    metadata["url"] = f"{BASE_URL}/{relative_path}"
                    metadata["path"] = str(relative_path)
                    
                    # Generate a unique key
                    key_parts = [
                        product_variant.replace('-', '_').replace(' ', '_'),
                        metadata.get('layout', 'unknown'),
                        metadata.get('color', 'unknown')[:3],
                        metadata.get('size', 'unknown')
                    ]
                    asset_key = '_'.join(key_parts).lower()
                    
                    # Group by main product
                    if main_product not in all_assets:
                        all_assets[main_product] = {}
                    
                    all_assets[main_product][asset_key] = metadata
                    
                    print(f"   ✅ Found: {relative_path}")
    
    return all_assets

def main():
    parser = argparse.ArgumentParser(description='Generate asset metadata from directory structure (recursive)')
    parser.add_argument('--base-path', default='.', help='Base path to scan (default: current directory)')
    parser.add_argument('--output', default='metadata/asset-inventory.json', help='Output JSON file')
    
    args = parser.parse_args()
    
    # Scan all assets recursively
    all_assets = scan_all_assets_recursive(args.base_path)
    
    # Build metadata structure
    metadata = {
        "brand_guidelines": {
            "clear_space": "Equal to 1/4 the height of the 'Q' in the logo",
            "minimum_size": "70px height for digital applications", 
            "primary_green": "#229529",
            "neutral_colors": {
                "light_background": "dark_grey",
                "dark_background": "light_grey"
            }
        }
    }
    
    # Add each product's assets
    total_assets = 0
    for product, assets in all_assets.items():
        if assets:
            if product == 'ciq':
                metadata["logos"] = assets
            elif product == 'fuzzball':
                metadata["fuzzball_logos"] = assets
            else:
                metadata[f"{product}_logos"] = assets
            
            print(f"   {product.title()} logos: {len(assets)}")
            total_assets += len(assets)
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write metadata JSON
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Generated metadata: {args.output}")
    print(f"   Total assets: {total_assets}")
    
    if total_assets > 200:
        print(f"\n🎉 Excellent! Found {total_assets} assets - much closer to your expected 300!")
    elif total_assets < 100:
        print(f"\n⚠️  Expected ~300 assets but found {total_assets}")
        print(f"   This might indicate some naming patterns aren't recognized yet")

if __name__ == "__main__":
    main()
