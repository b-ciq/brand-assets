#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - FastMCP Cloud Version  
Fixed to prioritize correct logo types (wordmark vs symbol)
"""

from fastmcp import FastMCP
import json
import requests
from typing import Optional, Dict, Any

# Asset metadata URL
METADATA_URL = 'https://raw.githubusercontent.com/b-ciq/brand-assets/main/metadata/asset-inventory.json'

# Initialize FastMCP server
mcp = FastMCP("CIQ Brand Assets")

# Global asset data cache
asset_data = None

def load_asset_data():
    """Load asset metadata from GitHub"""
    global asset_data
    try:
        response = requests.get(METADATA_URL, timeout=10)
        response.raise_for_status()
        asset_data = response.json()
        print(f"✅ Loaded {len(asset_data)} asset categories")
        return True
    except Exception as e:
        print(f"❌ Failed to load asset data: {e}")
        return False

def find_product_assets(product_name: str) -> Dict[str, Any]:
    """Find assets for a product using proper metadata keys"""
    if not asset_data:
        return {}
    
    # Product mapping to metadata keys
    product_keys = {
        'ciq': 'logos',
        'fuzzball': 'fuzzball_logos', 
        'warewulf': 'warewulf-pro_logos',
        'apptainer': 'apptainer_logos',
        'ascender': 'ascender-pro_logos', 
        'bridge': 'bridge_logos',
        'rlc': 'rlcx_logos',
        'support': 'ciq-support_logos'
    }
    
    metadata_key = product_keys.get(product_name, f'{product_name}_logos')
    return asset_data.get(metadata_key, {})

def find_best_asset(assets: Dict[str, Any], background: str, request: str) -> Optional[Dict[str, Any]]:
    """Find best asset based on background and request intent"""
    
    request_lower = request.lower()
    
    # Determine preferred layout from request
    preferred_layout = None
    if any(word in request_lower for word in ['symbol', 'icon', 'just icon']):
        preferred_layout = 'icon'
    elif any(word in request_lower for word in ['horizontal', 'lockup', 'with text', 'wordmark', 'full logo']):
        preferred_layout = 'horizontal'
    elif 'vertical' in request_lower:
        preferred_layout = 'vertical'
    else:
        # Default: when someone asks for "logo", prefer wordmark over symbol
        preferred_layout = 'horizontal'  # Default to horizontal lockup
    
    # First pass - find assets matching background and preferred layout
    candidates = []
    fallback_candidates = []
    
    for key, asset in assets.items():
        asset_bg = asset.get('background', '').lower()
        asset_layout = asset.get('layout', '').lower()
        
        if background == asset_bg:
            if preferred_layout and preferred_layout in asset_layout:
                candidates.append(asset)
            else:
                fallback_candidates.append(asset)
    
    # Return best candidate
    if candidates:
        return candidates[0]  # First matching layout + background
    elif fallback_candidates:
        return fallback_candidates[0]  # First matching background
    
    # Last resort - any asset
    return next(iter(assets.values())) if assets else None

@mcp.tool()
def get_brand_asset(request: str, background: Optional[str] = None) -> str:
    """
    Get CIQ brand assets with intelligent recommendations.
    
    Examples:
    - "CIQ logo for light background"
    - "Warewulf logo for white background"  
    - "Fuzzball full logo for dark background"
    - "Apptainer symbol for light background"
    """
    
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, couldn't load brand assets data."
    
    request_lower = request.lower()
    
    # Parse background if not provided
    if not background:
        if 'light' in request_lower or 'white' in request_lower:
            background = 'light'
        elif 'dark' in request_lower or 'black' in request_lower:
            background = 'dark'
    
    # Determine product
    product = None
    if 'ciq' in request_lower and not any(word in request_lower for word in ['support', 'bridge']):
        product = 'ciq'
    elif 'warewulf' in request_lower:
        product = 'warewulf'
    elif 'fuzzball' in request_lower:
        product = 'fuzzball'
    elif 'apptainer' in request_lower:
        product = 'apptainer'
    elif 'ascender' in request_lower:
        product = 'ascender'
    elif 'bridge' in request_lower:
        product = 'bridge'
    elif any(word in request_lower for word in ['rlc', 'rocky']):
        product = 'rlc'
    elif 'support' in request_lower:
        product = 'support'
    
    if not product:
        return """Which logo do you need?

**Company Brand:**
• **CIQ** - Main company logo

**Product Brands:**
• **Fuzzball** - HPC/AI workload management platform
• **Warewulf** - HPC cluster provisioning tool
• **Apptainer** - Container platform for HPC/scientific workflows
• **Ascender** - Infrastructure automation platform
• **Bridge** - CentOS migration solution
• **RLC** - Rocky Linux Commercial (AI, Hardened variants)

Example: "Fuzzball full logo for dark background" """
    
    # Get assets for this product
    assets = find_product_assets(product)
    
    if not assets:
        return f"Sorry, no {product.title()} logos found in metadata."
    
    # Ask for background if not provided
    if not background:
        product_descriptions = {
            'ciq': 'Company logo',
            'fuzzball': 'HPC/AI workload management platform',
            'warewulf': 'HPC cluster provisioning tool',
            'apptainer': 'Container platform for HPC/scientific workflows',
            'ascender': 'Infrastructure automation platform',
            'bridge': 'CentOS migration solution',
            'rlc': 'Rocky Linux Commercial variants',
            'support': 'Support division'
        }
        
        desc = product_descriptions.get(product, f'{product} product')
        return f"""{product.title()} - {desc}!

**Background:**
• **Light background** (black logo)
• **Dark background** (white logo)"""
    
    # Find best matching asset using intelligent selection
    matching_asset = find_best_asset(assets, background, request)
    
    if matching_asset:
        layout = matching_asset.get('layout', 'logo')
        layout_desc = f" {layout}" if layout != 'logo' else ""
        
        return f"""Here's your {product.title()}{layout_desc}:
**Download:** {matching_asset['url']}

{matching_asset.get('guidance', f'{product.title()} branding for {background} backgrounds')}"""
    
    return f"Sorry, couldn't find {product.title()} logo for {background} background."

@mcp.tool()  
def list_all_assets() -> str:
    """List all available brand assets with counts"""
    
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, couldn't load brand assets data."
    
    # Count actual assets in metadata
    total_products = 0
    total_assets = 0
    
    product_info = []
    for key, category in asset_data.items():
        if key.endswith('_logos') or key == 'logos':
            total_products += 1
            if isinstance(category, dict):
                asset_count = len(category)
                total_assets += asset_count
                product_name = key.replace('_logos', '').replace('-', ' ').title()
                if key == 'logos':
                    product_name = 'CIQ Company'
                product_info.append(f"• **{product_name}** - {asset_count} variants")
    
    result = f"""# CIQ Brand Assets Library

**{total_products} Products, {total_assets} Total Assets**

"""
    result += '\n'.join(product_info)
    
    result += """

**Logo Types Available:**
- **Symbol only** - Just the icon (tight spaces)
- **Horizontal lockup** - Symbol + text side-by-side  
- **Vertical lockup** - Symbol + text stacked

**Usage Examples:**
- "Fuzzball full logo for dark background" (gets horizontal lockup)
- "Fuzzball symbol for tight space" (gets icon only)
- "Warewulf vertical logo for presentation"

Specify "symbol", "horizontal", "vertical", or "full logo" for best results!"""
    
    return result

# Load data on startup
load_asset_data()

# FastMCP Cloud entry point
if __name__ == "__main__":
    mcp.run()
