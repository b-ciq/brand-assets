#!/usr/bin/env python3
"""
Asset Metadata Generator
Automatically scans asset directories and generates metadata JSON files
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Base GitHub raw URL for assets
BASE_URL = "https://raw.githubusercontent.com/b-ciq/brand-assets/main"

def parse_ciq_filename(filename: str) -> Dict[str, Any]:
    """
    Parse CIQ logo filename: CIQ-Logo-{variant}-{background}.{ext}
    Examples: CIQ-Logo-2color-light.png, CIQ-Logo-1color-dark.png
    """
    pattern = r'CIQ-Logo-(\w+)-(\w+)\.(\w+)'
    match = re.match(pattern, filename)
    
    if not match:
        return None
    
    variant, background, ext = match.groups()
    
    # Generate description
    if variant == '1color':
        desc = f"Single color (neutral) logo for {background} backgrounds"
        use_cases = ["supporting_element", "footer", "watermark", "professional_documents"]
        colors = ["neutral"]
        guidance = "Professional and clean - won't compete with colorful design elements"
    elif variant == '2color':
        desc = f"Two color (neutral + green) logo for {background} backgrounds"
        use_cases = ["hero", "main_element", "homepage", "business_cards", "presentations"]
        colors = ["neutral", "PMS_347_green"]
        guidance = "Most recognizable CIQ branding - use when logo is the star of the design"
    elif variant == 'green':
        desc = f"Single color (green) logo for {background} backgrounds"
        use_cases = ["supporting_element", "minimal_designs", "advertising", "brand_accent"]
        colors = ["PMS_347_green"]
        guidance = "Use in neutral/minimal designs when you need the logo to jump out"
    else:
        desc = f"CIQ logo variant: {variant} for {background} backgrounds"
        use_cases = ["general"]
        colors = ["unknown"]
        guidance = "CIQ logo variant"
    
    return {
        "filename": filename,
        "description": desc,
        "use_cases": use_cases,
        "colors": colors,
        "background": background,
        "guidance": guidance,
        "variant": variant,
        "format": ext
    }

def parse_fuzzball_filename(filename: str) -> Dict[str, Any]:
    """
    Parse Fuzzball logo filename patterns:
    - Fuzzball-Icon_{color}_{size}.{ext}  
    - Fuzzball_logo_logo_{layout}-{color}_{size}.{ext}
    - Fuzzball_logo_{layout}-{color}.{ext}
    """
    
    # Icon pattern: Fuzzball-Icon_blk_L.png
    icon_pattern = r'Fuzzball-Icon_(\w+)_([LMS])\.(\w+)'
    icon_match = re.match(icon_pattern, filename)
    
    if icon_match:
        color, size, ext = icon_match.groups()
        background = 'light' if color == 'blk' else 'dark'
        size_full = {'L': 'large', 'M': 'medium', 'S': 'small'}[size]
        
        return {
            "filename": filename,
            "description": f"Fuzzball icon ({color}) for {background} backgrounds - {size_full.title()}",
            "layout": "icon",
            "color": "black" if color == 'blk' else "white",
            "background": background,
            "size": size_full,
            "use_cases": ["favicon", "app_icon", "small_spaces", "avatars"],
            "guidance": "Perfect for tight spaces where you need just the Fuzzball symbol",
            "format": ext
        }
    
    # Horizontal/Vertical pattern: Fuzzball_logo_logo_h-blk_L.png or Fuzzball_logo_logo_v-wht_M.png
    layout_pattern = r'Fuzzball_logo_logo_([hv])-(\w+)_([LMS])\.(\w+)'
    layout_match = re.match(layout_pattern, filename)
    
    if layout_match:
        layout_code, color, size, ext = layout_match.groups()
        layout = 'horizontal' if layout_code == 'h' else 'vertical'
        background = 'light' if color == 'blk' else 'dark'
        size_full = {'L': 'large', 'M': 'medium', 'S': 'small'}[size]
        
        if layout == 'horizontal':
            use_cases = ["headers", "business_cards", "letterhead", "wide_banners"]
            guidance = "Best for wide spaces - business cards, website headers, email signatures"
        else:  # vertical
            use_cases = ["tall_banners", "social_media_profile", "mobile_layout", "poster"]
            guidance = "Perfect for tall/narrow spaces - social media profiles, mobile layouts"
        
        return {
            "filename": filename,
            "description": f"Fuzzball {layout} logo ({color}) for {background} backgrounds - {size_full.title()}",
            "layout": layout,
            "color": "black" if color == 'blk' else "white",
            "background": background,
            "size": size_full,
            "use_cases": use_cases,
            "guidance": guidance,
            "format": ext
        }
    
    # SVG pattern: Fuzzball_logo_h-blk.svg or Fuzzball_logo_logo_v-wht.svg
    svg_pattern = r'Fuzzball_logo_(?:logo_)?([hv])-(\w+)\.(\w+)'
    svg_match = re.match(svg_pattern, filename)
    
    if svg_match:
        layout_code, color, ext = svg_match.groups()
        layout = 'horizontal' if layout_code == 'h' else 'vertical'
        background = 'light' if color == 'blk' else 'dark'
        
        return {
            "filename": filename,
            "description": f"Fuzzball {layout} logo ({color}) for {background} backgrounds - SVG",
            "layout": layout,
            "color": "black" if color == 'blk' else "white",
            "background": background,
            "size": "vector",
            "use_cases": ["scalable", "web", "print"],
            "guidance": f"Vector format - scales to any size perfectly",
            "format": ext
        }
    
    # If no pattern matches, return basic info
    return {
        "filename": filename,
        "description": f"Fuzzball logo variant: {filename}",
        "layout": "unknown",
        "color": "unknown",
        "background": "unknown",
        "size": "unknown",
        "use_cases": ["general"],
        "guidance": "Fuzzball logo variant",
        "format": filename.split('.')[-1] if '.' in filename else "unknown"
    }

def scan_directory(base_path: str, product: str, asset_type: str) -> Dict[str, Any]:
    """Scan a directory and parse all asset files"""
    directory_path = Path(base_path) / product / asset_type
    assets = {}
    
    if not directory_path.exists():
        print(f"Directory not found: {directory_path}")
        return assets
    
    for file_path in directory_path.glob("*"):
        if file_path.is_file() and not file_path.name.startswith('.'):
            filename = file_path.name
            
            # Parse based on product
            if product == 'ciq':
                metadata = parse_ciq_filename(filename)
            elif product == 'fuzzball':
                metadata = parse_fuzzball_filename(filename)
            else:
                # Generic fallback for new products
                metadata = {
                    "filename": filename,
                    "description": f"{product.title()} {asset_type} - {filename}",
                    "format": filename.split('.')[-1] if '.' in filename else "unknown"
                }
            
            if metadata:
                # Add URL
                url_path = f"{product}-{asset_type}" if base_path == "." else f"assets/{product}/{asset_type}"
                metadata["url"] = f"{BASE_URL}/{url_path}/{filename}"
                
                # Generate asset key for current structure
                if product == 'ciq':
                    asset_key = f"{metadata['variant']}-{metadata['background']}"
                elif product == 'fuzzball':
                    if metadata['layout'] == 'icon':
                        asset_key = f"icon-{metadata['color'][:3]}-{metadata['size']}"
                    else:
                        asset_key = f"{metadata['layout']}-{metadata['color'][:3]}-{metadata['size']}"
                else:
                    asset_key = filename.replace('.', '_').replace('-', '_').lower()
                
                assets[asset_key] = metadata
    
    return assets

def generate_brand_guidelines() -> Dict[str, Any]:
    """Generate brand guidelines structure"""
    return {
        "clear_space": "Equal to 1/4 the height of the 'Q' in the logo",
        "minimum_size": "70px height for digital applications", 
        "primary_green": "#229529",
        "neutral_colors": {
            "light_background": "dark_grey",
            "dark_background": "light_grey"
        }
    }

def generate_decision_logic() -> Dict[str, Any]:
    """Generate decision logic for both CIQ and Fuzzball"""
    return {
        "ciq": {
            "main_element": {
                "description": "Logo is the hero/star of the design",
                "examples": ["homepage headers", "business cards", "presentation title slides"],
                "recommended": "2color (most recognizable branding)"
            },
            "supporting_element": {
                "description": "Logo is secondary/background element",
                "examples": ["footers", "watermarks", "corner branding"], 
                "default": "1color neutral (when in doubt)",
                "alternative": "green (for neutral designs where logo needs to pop)"
            }
        },
        "fuzzball": {
            "layout_selection": {
                "icon": {
                    "description": "Just the symbol - most compact",
                    "examples": ["favicons", "app icons", "avatars", "tight spaces"],
                    "when_to_use": "Space is very limited or you need just the recognizable symbol"
                },
                "horizontal": {
                    "description": "Symbol + text side-by-side",
                    "examples": ["business cards", "headers", "email signatures", "letterhead"],
                    "when_to_use": "Wide spaces, professional documents, primary branding"
                },
                "vertical": {
                    "description": "Symbol + text stacked", 
                    "examples": ["social media profiles", "mobile layouts", "tall banners", "posters"],
                    "when_to_use": "Tall/narrow spaces, mobile-first designs"
                }
            },
            "size_selection": {
                "small": "Compact usage, small spaces",
                "medium": "Standard usage, most common",
                "large": "Hero placement, high-impact usage"
            }
        }
    }

def main():
    parser = argparse.ArgumentParser(description='Generate asset metadata from directory structure')
    parser.add_argument('--base-path', default='.', help='Base path to scan (default: current directory)')
    parser.add_argument('--output', default='metadata/asset-inventory.json', help='Output JSON file')
    parser.add_argument('--products', nargs='+', default=['ciq', 'fuzzball'], help='Products to scan')
    
    args = parser.parse_args()
    
    print(f"🔍 Scanning asset directories in: {args.base_path}")
    
    # Build complete metadata structure
    metadata = {
        "logos": {},
        "fuzzball_logos": {},
        "brand_guidelines": generate_brand_guidelines(),
        "decision_logic": generate_decision_logic()
    }
    
    # Scan each product
    for product in args.products:
        print(f"📁 Scanning {product} assets...")
        
        # For current directory structure, check both old and new paths
        if args.base_path == '.':
            # Check old structure first: /CIQ-logos, /fuzzball-logos  
            old_path = Path(f"{product.upper()}-logos" if product == 'ciq' else f"{product}-logos")
            if old_path.exists():
                print(f"   Found old structure: {old_path}")
                assets = {}
                for file_path in old_path.glob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        filename = file_path.name
                        
                        if product == 'ciq':
                            asset_metadata = parse_ciq_filename(filename)
                        else:
                            asset_metadata = parse_fuzzball_filename(filename)
                        
                        if asset_metadata:
                            # Use old URL path for now
                            asset_metadata["url"] = f"{BASE_URL}/{old_path}/{filename}"
                            
                            # Generate key
                            if product == 'ciq':
                                key = f"{asset_metadata['variant']}-{asset_metadata['background']}"
                                metadata["logos"][key] = asset_metadata
                            else:
                                if asset_metadata['layout'] == 'icon':
                                    key = f"icon-{asset_metadata['color'][:3]}-{asset_metadata['size']}"
                                else:
                                    key = f"{asset_metadata['layout']}-{asset_metadata['color'][:3]}-{asset_metadata['size']}"
                                metadata["fuzzball_logos"][key] = asset_metadata
            
            # Also check new structure: /assets/{product}/logos
            new_path = Path("assets") / product / "logos"
            if new_path.exists():
                print(f"   Found new structure: {new_path}")
                new_assets = scan_directory("assets", product, "logos")
                
                if product == 'ciq':
                    metadata["logos"].update(new_assets)
                else:
                    metadata["fuzzball_logos"].update(new_assets)
        else:
            # Scan new structure
            assets = scan_directory(args.base_path, product, "logos")
            
            if product == 'ciq':
                metadata["logos"].update(assets)
            else:
                metadata["fuzzball_logos"].update(assets)
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write metadata JSON
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Print summary
    print(f"\n✅ Generated metadata: {args.output}")
    print(f"   CIQ logos: {len(metadata['logos'])}")
    print(f"   Fuzzball logos: {len(metadata['fuzzball_logos'])}")
    print(f"   Total assets: {len(metadata['logos']) + len(metadata['fuzzball_logos'])}")
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Review generated metadata: {args.output}")
    print(f"   2. Restart your MCP server to use new metadata")
    print(f"   3. Test with: 'I need a CIQ logo' or 'Fuzzball logo'")

if __name__ == "__main__":
    main()
