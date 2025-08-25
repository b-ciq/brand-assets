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

def parse_generic_filename(filename: str, product: str) -> Dict[str, Any]:
    """
    Parse generic product logo filename patterns for new products:
    - {Product}-Icon_{color}_{size}.{ext} (icon pattern)
    - {Product}-Logo_{color}_{layout}_{size}.{ext} (new logo pattern)  
    - {Product}_logo_{layout}-{color}.{ext} (SVG logo pattern)
    - {Product}_icon_{color}.{ext} (SVG icon pattern)
    """
    
    # CIQ-prefixed pattern: CIQ-Bridge-logo_h_wht_L.png 
    ciq_pattern = rf'CIQ-{re.escape(product.title())}-(\w+)_(\w+)_(\w+)_([LMS])\.(\w+)'
    match = re.match(ciq_pattern, filename, re.IGNORECASE)
    
    if match:
        asset_type, layout, color, size, ext = match.groups()
        background = 'light' if color.lower() == 'blk' else 'dark'
        size_full = {'L': 'large', 'M': 'medium', 'S': 'small'}[size.upper()]
        final_layout = "icon" if asset_type.lower() == "icon" else layout.lower()
        
        # Layout-specific use cases
        if final_layout == 'icon':
            use_cases = ["favicon", "app_icon", "small_spaces", "avatars"]
            guidance = "Perfect for tight spaces where you need just the symbol"
        elif final_layout == 'horizontal':
            use_cases = ["headers", "business_cards", "letterhead", "wide_banners"]
            guidance = "Best for wide spaces - business cards, website headers, email signatures"
        else:  # vertical
            use_cases = ["tall_banners", "social_media_profile", "mobile_layout", "poster"]
            guidance = "Perfect for tall/narrow spaces - social media profiles, mobile layouts"
        
        return {
            "filename": filename,
            "description": f"{product.title()} {asset_type} ({color}) for {background} backgrounds - {size_full.title()}",
            "layout": final_layout,
            "color": "black" if color.lower() == 'blk' else "white",
            "background": background,
            "size": size_full.lower(),
            "use_cases": use_cases,
            "guidance": guidance,
            "format": ext.lower()
        }
    
    # Icon pattern: Product-Icon_blk_L.png (like Apptainer-Icon_blk_L.png)
    icon_pattern = rf'{re.escape(product.title())}-Icon_(\w+)_([LMS])\.(\w+)'
    match = re.match(icon_pattern, filename, re.IGNORECASE)
    
    if match:
        color, size, ext = match.groups()
        background = 'light' if color.lower() == 'blk' else 'dark'
        size_full = {'L': 'large', 'M': 'medium', 'S': 'small'}[size.upper()]
        
        return {
            "filename": filename,
            "description": f"{product.title()} icon ({color}) for {background} backgrounds - {size_full.title()}",
            "layout": "icon",
            "color": "black" if color.lower() == 'blk' else "white",
            "background": background,
            "size": size_full,
            "use_cases": ["favicon", "app_icon", "small_spaces", "avatars"],
            "guidance": f"Perfect for tight spaces where you need just the {product.title()} symbol",
            "format": ext
        }
    
    # Logo pattern: Product-Logo_blk_v_L.png (like Apptainer-Logo_blk_v_L.png)
    logo_pattern = rf'{re.escape(product.title())}-Logo_(\w+)_([hv])_([LMS])\.(\w+)'
    match = re.match(logo_pattern, filename, re.IGNORECASE)
    
    if match:
        color, layout_code, size, ext = match.groups()
        layout = 'horizontal' if layout_code.lower() == 'h' else 'vertical'
        background = 'light' if color.lower() == 'blk' else 'dark'
        size_full = {'L': 'large', 'M': 'medium', 'S': 'small'}[size.upper()]
        
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
            "format": ext
        }
    
    # SVG logo pattern: Product_logo_h-blk.svg (like Apptainer_logo_h-blk.svg)
    svg_logo_pattern = rf'{re.escape(product.title())}_logo_([hv])-(\w+)\.(\w+)'
    match = re.match(svg_logo_pattern, filename, re.IGNORECASE)
    
    if match:
        layout_code, color, ext = match.groups()
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
            "format": ext
        }
    
    # SVG icon pattern: Product_icon_blk.svg (like Apptainer_icon_blk.svg)
    svg_icon_pattern = rf'{re.escape(product.title())}_icon_(\w+)\.(\w+)'
    match = re.match(svg_icon_pattern, filename, re.IGNORECASE)
    
    if match:
        color, ext = match.groups()
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
            "format": ext
        }
    
    # Fallback - basic file info
    return {
        "filename": filename,
        "description": f"{product.title()} logo variant: {filename}",
        "layout": "unknown",
        "color": "unknown", 
        "background": "unknown",
        "size": "unknown",
        "use_cases": ["general"],
        "guidance": f"{product.title()} logo variant",
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
                # Use generic parser for new products
                metadata = parse_generic_filename(filename, product)
            
            if metadata:
                # Add URL
                url_path = f"{product}-{asset_type}" if base_path == "." else f"assets/{product}/{asset_type}"
                metadata["url"] = f"{BASE_URL}/{url_path}/{filename}"
                
                # Generate asset key for current structure
                if product == 'ciq':
                    asset_key = f"{metadata['variant']}-{metadata['background']}"
                elif metadata.get('layout') and metadata.get('background') and metadata.get('size'):
                    if metadata['layout'] == 'icon':
                        asset_key = f"icon-{metadata['color'][:3]}-{metadata['size']}"
                    else:
                        asset_key = f"{metadata['layout']}-{metadata['color'][:3]}-{metadata['size']}"
                else:
                    # Fallback key
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

def discover_products(base_path: str) -> List[str]:
    """Auto-discover products by finding assets subdirectories"""
    products = []
    
    # Check /assets/ structure first
    assets_path = Path(base_path) / "assets"
    if assets_path.exists():
        for item in assets_path.iterdir():
            if item.is_dir() and (item / "logos").exists():
                products.append(item.name)
    
    # Fallback: Find old *-logos directories at root
    path = Path(base_path)
    for item in path.iterdir():
        if item.is_dir() and item.name.endswith('-logos'):
            # Extract product name
            product_name = item.name.replace('-logos', '').lower()
            
            # Map directory names to product names
            if product_name == 'ciq':
                products.append('ciq')
            elif product_name == 'fuzzball':
                products.append('fuzzball')
            elif product_name == 'apptainer':
                products.append('apptainer')
            elif product_name == 'bridge':
                products.append('bridge')
            elif product_name == 'ascender-pro':
                products.append('ascender-pro')
            elif product_name == 'warewulf-pro':
                products.append('warewulf-pro')
            elif product_name == 'ciq-support':
                products.append('ciq-support')
            else:
                # Generic product
                products.append(product_name)
    
    return list(set(products))  # Remove duplicates

def main():
    parser = argparse.ArgumentParser(description='Generate asset metadata from directory structure')
    parser.add_argument('--base-path', default='.', help='Base path to scan (default: current directory)')
    parser.add_argument('--output', default='metadata/asset-inventory.json', help='Output JSON file')
    parser.add_argument('--products', nargs='*', help='Products to scan (default: auto-discover)')
    
    args = parser.parse_args()
    
    # Auto-discover products if not specified
    if not args.products:
        args.products = discover_products(args.base_path)
        print(f"🔍 Auto-discovered products: {', '.join(args.products)}")
    
    print(f"🔍 Scanning asset directories in: {args.base_path}")
    
    # Build complete metadata structure
    all_product_logos = {}
    
    # Scan each product
    for product in args.products:
        print(f"📁 Scanning {product} assets...")
        
        # For current directory structure, prioritize /assets/ structure
        if args.base_path == '.':
            # Check NEW assets structure FIRST: /assets/product/logos/
            assets_found = {}
            new_path = Path("assets") / product / "logos"
            if new_path.exists():
                print(f"   Found assets structure: {new_path}")
                for file_path in new_path.glob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.') and not file_path.name.endswith('.svg'):
                        filename = file_path.name
                        
                        if product == 'ciq':
                            asset_metadata = parse_ciq_filename(filename)
                        elif product == 'fuzzball':
                            asset_metadata = parse_fuzzball_filename(filename)
                        else:
                            asset_metadata = parse_generic_filename(filename, product)
                        
                        if asset_metadata:
                            # Use new assets URL path
                            asset_metadata["url"] = f"{BASE_URL}/assets/{product}/logos/{filename}"
                            
                            # Generate key
                            if product == 'ciq':
                                key = f"{asset_metadata['variant']}-{asset_metadata['background']}"
                            elif asset_metadata.get('layout') and asset_metadata.get('background') and asset_metadata.get('size'):
                                if asset_metadata['layout'] == 'icon':
                                    key = f"icon-{asset_metadata['color'][:3]}-{asset_metadata['size']}"
                                else:
                                    key = f"{asset_metadata['layout']}-{asset_metadata['color'][:3]}-{asset_metadata['size']}"
                            else:
                                key = filename.replace('.', '_').replace('-', '_').lower()
                            
                            assets_found[key] = asset_metadata
            
            # Fallback to old structure if no assets found: /CIQ-logos, /fuzzball-logos, /Product-logos
            if not assets_found:
                old_dirs = []
                if product == 'ciq':
                    old_dirs = ['CIQ-logos']
                elif product == 'fuzzball':
                    old_dirs = ['fuzzball-logos'] 
                elif product == 'apptainer':
                    old_dirs = ['Apptainer-logos']
                elif product == 'bridge':
                    old_dirs = ['Bridge-logos']
                elif product == 'ascender-pro':
                    old_dirs = ['Ascender-Pro-logos']
                elif product == 'warewulf-pro':
                    old_dirs = ['Warewulf-Pro-logos']
                elif product == 'ciq-support':
                    old_dirs = ['CIQ-Support-logos']
                else:
                    # For other products, try multiple possible directory names
                    old_dirs = [
                        f"{product.title()}-logos",
                        f"{product}-logos", 
                        f"{product.upper()}-logos",
                        f"{product.title().replace('-', ' ').replace(' ', '-')}-logos"
                    ]
                
                for dir_name in old_dirs:
                    old_path = Path(dir_name)
                    if old_path.exists():
                        print(f"   Found old structure: {old_path}")
                        for file_path in old_path.glob("*"):
                            if file_path.is_file() and not file_path.name.startswith('.') and not file_path.name.endswith('.svg'):
                                filename = file_path.name
                                
                                if product == 'ciq':
                                    asset_metadata = parse_ciq_filename(filename)
                                elif product == 'fuzzball':
                                    asset_metadata = parse_fuzzball_filename(filename)
                                else:
                                    asset_metadata = parse_generic_filename(filename, product)
                                
                                if asset_metadata:
                                    # Use old URL path for now
                                    asset_metadata["url"] = f"{BASE_URL}/{old_path}/{filename}"
                                    
                                    # Generate key
                                    if product == 'ciq':
                                        key = f"{asset_metadata['variant']}-{asset_metadata['background']}"
                                    elif asset_metadata.get('layout') and asset_metadata.get('background') and asset_metadata.get('size'):
                                        if asset_metadata['layout'] == 'icon':
                                            key = f"icon-{asset_metadata['color'][:3]}-{asset_metadata['size']}"
                                        else:
                                            key = f"{asset_metadata['layout']}-{asset_metadata['color'][:3]}-{asset_metadata['size']}"
                                    else:
                                        key = filename.replace('.', '_').replace('-', '_').lower()
                                    
                                    assets_found[key] = asset_metadata
            
            all_product_logos[product] = assets_found
        else:
            # Scan new structure
            assets = scan_directory(args.base_path, product, "logos")
            all_product_logos[product] = assets
    
    # Build final metadata structure
    metadata = {
        "brand_guidelines": generate_brand_guidelines(),
        "decision_logic": generate_decision_logic()
    }
    
    # Add product-specific logos
    if 'ciq' in all_product_logos:
        metadata["logos"] = all_product_logos['ciq']
    if 'fuzzball' in all_product_logos:
        metadata["fuzzball_logos"] = all_product_logos['fuzzball']
    
    # Add other products as separate categories
    for product, assets in all_product_logos.items():
        if product not in ['ciq', 'fuzzball'] and assets:
            metadata[f"{product}_logos"] = assets
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write metadata JSON
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Print summary
    print(f"\n✅ Generated metadata: {args.output}")
    total_assets = 0
    for product, assets in all_product_logos.items():
        if assets:
            print(f"   {product.title()} logos: {len(assets)}")
            total_assets += len(assets)
    print(f"   Total assets: {total_assets}")
    
    print(f"\n🚀 Next steps:")
    print(f"   1. Review generated metadata: {args.output}")
    print(f"   2. Restart your MCP server to use new metadata")
    print(f"   3. Test with: 'I need a CIQ logo' or 'Fuzzball logo'")
    
    if total_assets > 30:
        print(f"\n🎉 Great! Found {total_assets} total assets - much better!")

if __name__ == "__main__":
    main()
