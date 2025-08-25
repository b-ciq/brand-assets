#!/usr/bin/env python3
"""
Generate Clean Metadata - Post Cleanup
Scans the cleaned directories and generates accurate metadata
"""

import json
from pathlib import Path

def analyze_file(file_path, product_id, product_name):
    """Analyze a cleaned file and generate metadata"""
    filename = file_path.name
    filename_lower = filename.lower()
    
    # Detect layout
    if 'icon' in filename_lower:
        layout = 'icon'
        use_cases = ['favicon', 'app_icon', 'small_spaces', 'avatars']
        guidance = f'Perfect for tight spaces where you need just the {product_name} symbol'
    elif '_h' in filename_lower or 'horizontal' in filename_lower:
        layout = 'horizontal'
        use_cases = ['headers', 'business_cards', 'letterhead', 'wide_banners']
        guidance = f'Best for wide spaces - business cards, website headers, email signatures'
    elif '_v' in filename_lower or 'vertical' in filename_lower:
        layout = 'vertical'
        use_cases = ['tall_banners', 'social_media_profile', 'mobile_layout', 'poster']
        guidance = f'Perfect for tall/narrow spaces - social media profiles, mobile layouts'
    elif '1color' in filename_lower or '1-color' in filename_lower:
        layout = '1color'
        use_cases = ['headers', 'business_cards', 'letterhead', 'general_branding']
        guidance = f'Standard {product_name} company logo for most applications'
    elif '2color' in filename_lower or '2-color' in filename_lower or 'hero' in filename_lower:
        layout = '2color'
        use_cases = ['hero_sections', 'presentations', 'marketing_materials', 'large_displays']
        guidance = f'Hero {product_name} company logo when logo is primary visual element'
    else:
        layout = 'horizontal'  # Default
        use_cases = ['headers', 'business_cards', 'letterhead', 'wide_banners']
        guidance = f'Best for wide spaces - business cards, website headers, email signatures'
    
    # Detect color and background
    if '_blk' in filename_lower or 'black' in filename_lower:
        color = 'black'
        background = 'light'
    elif '_wht' in filename_lower or 'white' in filename_lower:
        color = 'white'
        background = 'dark'
    elif 'green' in filename_lower:
        color = 'green'
        background = 'light'
    else:
        color = 'black'
        background = 'light'
    
    # All cleaned files are large
    size = 'large'
    
    # Generate description
    if layout in ['1color', '2color']:
        description = f'{product_name} {layout} company logo'
    else:
        description = f'{product_name} {layout} logo ({color}) for {background} backgrounds - {size.title()}'
    
    # Generate unique key
    key = f'{product_id.replace("-", "_")}_{layout}_{color[:3]}_{size}'
    
    return {
        'filename': filename,
        'description': description,
        'layout': layout,
        'color': color,
        'background': background,
        'size': size,
        'use_cases': use_cases,
        'guidance': guidance,
        'format': 'png',
        'product': product_id,
        'url': f'https://raw.githubusercontent.com/b-ciq/brand-assets/main/{file_path.parent.name}/{filename}',
        'path': f'{file_path.parent.name}/{filename}'
    }, key

def process_directory(dir_path, metadata_key, product_id, product_name):
    """Process a cleaned directory"""
    if not dir_path.exists():
        return {}
    
    assets = {}
    png_files = [f for f in dir_path.iterdir() if f.is_file() and f.name.lower().endswith('.png')]
    
    print(f'  📁 {dir_path.name}: {len(png_files)} PNG files')
    
    for file_path in png_files:
        asset_data, key = analyze_file(file_path, product_id, product_name)
        assets[key] = asset_data
        print(f'    ✅ {file_path.name} → {asset_data["layout"]} {asset_data["color"]}')
    
    return assets

def main():
    print('🔄 Generating Clean Metadata from Cleaned Directories...\n')
    
    # Brand guidelines
    metadata = {
        'brand_guidelines': {
            'clear_space': "Equal to 1/4 the height of the 'Q' in the logo",
            'minimum_size': '70px height for digital applications',
            'primary_green': '#229529',
            'neutral_colors': {
                'light_background': 'dark_grey',
                'dark_background': 'light_grey'
            }
        }
    }
    
    # Directory mapping: (dir_name, metadata_key, product_id, product_name)
    directories = [
        ('CIQ-logos', 'logos', 'ciq', 'CIQ'),
        ('fuzzball-logos', 'fuzzball_logos', 'fuzzball', 'Fuzzball'),
        ('Apptainer-logos', 'apptainer_logos', 'apptainer', 'Apptainer'),
        ('Warewulf-Pro-logos', 'warewulf_pro_logos', 'warewulf-pro', 'Warewulf-Pro'),
        ('Ascender-Pro-logos', 'ascender_pro_logos', 'ascender-pro', 'Ascender-Pro'),
        ('Bridge-logos', 'bridge_logos', 'bridge', 'Bridge'),
        ('CIQ-Support-logos', 'ciq_support_logos', 'ciq-support', 'CIQ-Support'),
        ('rlc_logos', 'rlc_logos', 'rlc', 'RLC'),
        ('rlc_ai_logos', 'rlc_ai_logos', 'rlc-ai', 'RLC-AI'),
        ('rlc_hardened_logos', 'rlc_hardened_logos', 'rlc-hardened', 'RLC-Hardened'),
        ('rlc_lts_logos', 'rlc_lts_logos', 'rlc-lts', 'RLC-LTS')
    ]
    
    total_assets = 0
    
    for dir_name, metadata_key, product_id, product_name in directories:
        dir_path = Path(dir_name)
        assets = process_directory(dir_path, metadata_key, product_id, product_name)
        metadata[metadata_key] = assets
        total_assets += len(assets)
    
    # Write clean metadata
    metadata_file = Path('metadata/asset-inventory.json')
    metadata_file.parent.mkdir(exist_ok=True)
    
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f'\n✅ Clean metadata generated!')
    print(f'📊 **SUMMARY:**')
    print(f'   🗂️  Products: {len(directories)}')
    print(f'   📄 Total assets: {total_assets}')
    print(f'   💾 File: {metadata_file}')
    
    # Show breakdown
    print(f'\n📋 **ASSET BREAKDOWN:**')
    for dir_name, metadata_key, product_id, product_name in directories:
        count = len(metadata.get(metadata_key, {}))
        if count > 0:
            print(f'   • {product_name}: {count} assets')
    
    print(f'\n🎯 This should show ~60 total assets (down from 107+)')
    print(f'🔄 Next: Commit and push to trigger FastMCP Cloud update')

if __name__ == '__main__':
    main()
