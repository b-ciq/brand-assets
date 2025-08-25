#!/usr/bin/env python3
"""
Declarative Asset Metadata Generator
Creates clean, rule-based metadata for scalable asset management
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
import argparse

# Base GitHub raw URL for assets
BASE_URL = "https://raw.githubusercontent.com/b-ciq/brand-assets/main"

def parse_filename(filename: str) -> Dict[str, str]:
    """
    Parse consistent filename: {Product}_{type}_{layout}_{color}_{size}.{ext}
    Returns: {product, type, layout, color, size, ext}
    """
    name_without_ext = filename.rsplit('.', 1)[0]
    ext = filename.rsplit('.', 1)[1] if '.' in filename else 'png'
    
    parts = name_without_ext.split('_')
    if len(parts) < 5:
        return None
    
    return {
        'product': parts[0].lower(),
        'type': parts[1], 
        'layout': parts[2],
        'color': parts[3],
        'size': parts[4],
        'ext': ext
    }

def generate_asset_key(parsed: Dict[str, str]) -> str:
    """Generate consistent asset key"""
    if parsed['layout'] in ['onecolor', 'twocolor', 'green']:
        # CIQ special variants
        return f"{parsed['layout']}_{parsed['color']}"
    elif parsed['layout'] == 'square':
        # Icons
        return f"icon_{parsed['color']}"
    else:
        # Regular logos
        return f"{parsed['layout']}_{parsed['color']}"

def determine_background(color: str) -> str:
    """Determine optimal background for color"""
    if color.lower() == 'black':
        return 'light'  # black logo on light background
    elif color.lower() == 'white': 
        return 'dark'   # white logo on dark background
    else:
        return 'any'    # color logos work on various backgrounds

def get_asset_tags(layout: str, type_: str) -> List[str]:
    """Get semantic tags for asset matching"""
    tags = []
    
    if layout == 'square' or type_ == 'icon':
        tags.extend(['favicon', 'app_icon', 'compact', 'small_space', 'avatar'])
    elif layout == 'horizontal':
        tags.extend(['business_card', 'header', 'email_signature', 'letterhead', 'wide_format'])
    elif layout == 'vertical':
        tags.extend(['mobile', 'social_profile', 'tall_banner', 'poster', 'stacked'])
    elif layout in ['onecolor', 'twocolor', 'green']:
        if layout == 'onecolor':
            tags.extend(['supporting', 'footer', 'watermark', 'minimal', 'professional'])
        elif layout == 'twocolor':
            tags.extend(['hero', 'primary', 'homepage', 'presentation', 'main_branding'])
        elif layout == 'green':
            tags.extend(['accent', 'highlight', 'call_to_action', 'brand_pop'])
    
    return tags

def scan_assets_directory(assets_path: Path) -> Dict[str, Any]:
    """Scan and catalog all assets"""
    assets = {}
    
    # Scan global assets (CIQ)
    global_logos = assets_path / "global" / "logos"
    if global_logos.exists():
        ciq_assets = {}
        for file_path in global_logos.glob("*.png"):
            parsed = parse_filename(file_path.name)
            if parsed:
                key = generate_asset_key(parsed)
                ciq_assets[key] = {
                    "url": f"{BASE_URL}/assets/global/logos/{file_path.name}",
                    "filename": file_path.name,
                    "background": determine_background(parsed['color']),
                    "color": parsed['color'],
                    "layout": parsed['layout'],
                    "type": parsed['type'],
                    "size": parsed['size'],
                    "tags": get_asset_tags(parsed['layout'], parsed['type'])
                }
        if ciq_assets:
            assets['ciq'] = ciq_assets
    
    # Scan product assets
    products_path = assets_path / "products"
    if products_path.exists():
        for product_dir in products_path.iterdir():
            if product_dir.is_dir():
                product_name = product_dir.name
                logos_path = product_dir / "logos"
                
                if logos_path.exists():
                    product_assets = {}
                    for file_path in logos_path.glob("*.png"):
                        parsed = parse_filename(file_path.name)
                        if parsed:
                            key = generate_asset_key(parsed)
                            product_assets[key] = {
                                "url": f"{BASE_URL}/assets/products/{product_name}/logos/{file_path.name}",
                                "filename": file_path.name,
                                "background": determine_background(parsed['color']),
                                "color": parsed['color'],
                                "layout": "icon" if parsed['layout'] == 'square' else parsed['layout'],
                                "type": parsed['type'],
                                "size": parsed['size'],
                                "tags": get_asset_tags(parsed['layout'], parsed['type'])
                            }
                    
                    if product_assets:
                        assets[product_name] = product_assets
    
    return assets

def generate_rules() -> Dict[str, Any]:
    """Generate declarative matching rules"""
    return {
        "use_case_matching": {
            "favicon": {
                "prefer_layout": "icon",
                "prefer_size": "large",
                "description": "Small square icon for browser tabs"
            },
            "app_icon": {
                "prefer_layout": "icon", 
                "prefer_size": "large",
                "description": "Application icon for software"
            },
            "business_card": {
                "prefer_layout": "horizontal",
                "prefer_size": "large",
                "description": "Logo for business cards and professional materials"
            },
            "email_signature": {
                "prefer_layout": "horizontal",
                "prefer_size": "large", 
                "description": "Logo for email signatures"
            },
            "letterhead": {
                "prefer_layout": "horizontal",
                "prefer_size": "large",
                "description": "Logo for official letterhead"
            },
            "website_header": {
                "prefer_layout": "horizontal",
                "prefer_size": "large",
                "description": "Logo for website headers"
            },
            "mobile_app": {
                "prefer_layout": "vertical",
                "prefer_size": "large",
                "description": "Logo optimized for mobile layouts"
            },
            "social_media": {
                "prefer_layout": "vertical", 
                "prefer_size": "large",
                "description": "Logo for social media profiles"
            },
            "presentation": {
                "prefer_layout": "horizontal",
                "prefer_size": "large",
                "description": "Logo for presentations and slides"
            }
        },
        "background_matching": {
            "light": {
                "prefer_color": "black",
                "description": "Dark logos on light backgrounds"
            },
            "dark": {
                "prefer_color": "white", 
                "description": "Light logos on dark backgrounds"
            },
            "any": {
                "prefer_color": "color",
                "fallback_color": "black",
                "description": "Color logos that work on various backgrounds"
            }
        },
        "ciq_variant_rules": {
            "main_branding": {
                "prefer_variant": "twocolor",
                "description": "Most recognizable CIQ branding - use when logo is the star"
            },
            "supporting": {
                "prefer_variant": "onecolor",
                "description": "Clean, professional - won't compete with other elements"
            },
            "accent": {
                "prefer_variant": "green", 
                "description": "Use when you need the logo to pop in neutral designs"
            }
        },
        "confidence_scoring": {
            "exact_match": 1.0,
            "layout_match": 0.8,
            "background_match": 0.7,
            "tag_match": 0.6,
            "fallback": 0.3
        }
    }

def generate_index(assets: Dict[str, Any]) -> Dict[str, Any]:
    """Generate index for fast lookups"""
    products = list(assets.keys())
    
    all_layouts = set()
    all_colors = set()
    all_backgrounds = set() 
    all_tags = set()
    
    for product_assets in assets.values():
        for asset in product_assets.values():
            all_layouts.add(asset['layout'])
            all_colors.add(asset['color'])
            all_backgrounds.add(asset['background'])
            all_tags.update(asset['tags'])
    
    return {
        "products": sorted(products),
        "layouts": sorted(all_layouts),
        "colors": sorted(all_colors),
        "backgrounds": sorted(all_backgrounds),
        "tags": sorted(all_tags),
        "total_assets": sum(len(assets_dict) for assets_dict in assets.values())
    }

def main():
    parser = argparse.ArgumentParser(description='Generate declarative asset metadata')
    parser.add_argument('--base-path', default='.', help='Base path to scan (default: current directory)')
    parser.add_argument('--output', default='metadata/asset-inventory.json', help='Output JSON file')
    
    args = parser.parse_args()
    assets_path = Path(args.base_path) / "assets"
    
    print(f"🔍 Scanning assets for declarative metadata generation...")
    
    # Scan all assets
    assets = scan_assets_directory(assets_path)
    
    # Build metadata structure
    metadata = {
        "assets": assets,
        "rules": generate_rules(),
        "index": generate_index(assets)
    }
    
    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write metadata
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Print summary
    total_assets = metadata["index"]["total_assets"]
    products = len(metadata["index"]["products"])
    
    print(f"\n✅ Generated declarative metadata: {args.output}")
    print(f"   📊 {total_assets} assets across {products} products")
    print(f"   🏷️  {len(metadata['index']['tags'])} semantic tags")
    print(f"   📐 {len(metadata['index']['layouts'])} layouts")
    print(f"   🎨 {len(metadata['index']['backgrounds'])} background types")
    
    print(f"\n🎯 Benefits:")
    print(f"   • Declarative rules for consistent matching")
    print(f"   • Semantic tags for intelligent recommendations")
    print(f"   • Confidence scoring for quality results")
    print(f"   • Easy debugging and troubleshooting")
    
    print(f"\n🚀 Ready for FastMCP integration!")

if __name__ == "__main__":
    main()