#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - FastMCP Cloud Version
Intelligent brand asset delivery with smart logo recommendations
"""

from fastmcp import FastMCP  # Correct import for FastMCP Cloud
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

def get_all_products() -> list[str]:
    """Get list of all available products"""
    if not asset_data:
        return []
    
    products = []
    if 'logos' in asset_data:
        products.append('ciq')
    if 'fuzzball_logos' in asset_data:
        products.append('fuzzball')
    
    for key in asset_data.keys():
        if key.endswith('_logos') and key not in ['fuzzball_logos']:
            product_name = key.replace('_logos', '')
            products.append(product_name)
    
    return products

def determine_logo_type(request: str) -> str:
    """Determine which product logo the user wants"""
    request_lower = request.lower()
    
    product_keywords = {
        'ciq': ['ciq', 'company logo', 'main logo', 'brand logo'],
        'fuzzball': ['fuzzball', 'fuzz ball'],
        'apptainer': ['apptainer'],
        'warewulf-pro': ['warewulf', 'warewulf pro'],
        'ascender-pro': ['ascender', 'ascender pro'],
        'bridge': ['bridge'],
        'rlcx': ['rlc', 'rocky linux', 'rocky'],
        'ciq-support': ['ciq support', 'support']
    }
    
    for product, keywords in product_keywords.items():
        if any(keyword in request_lower for keyword in keywords):
            return product
    
    return 'unclear'

@mcp.tool()
def get_brand_asset(request: str, background: Optional[str] = None) -> str:
    """
    Get CIQ brand assets with smart recommendations.
    
    Examples:
    - "CIQ logo"
    - "Fuzzball symbol for dark background"  
    - "Apptainer logo"
    """
    
    # Load data if needed
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, couldn't load brand assets data."
    
    # Determine product
    product = determine_logo_type(request)
    
    if product == 'unclear':
        available_products = get_all_products()
        return f"""Which logo do you need?

Available: {', '.join([p.title() for p in available_products])}

Example: "CIQ logo", "Fuzzball logo", "Apptainer logo" """

    # Get product assets
    if product == 'ciq':
        assets = asset_data.get('logos', {})
    elif product == 'fuzzball':
        assets = asset_data.get('fuzzball_logos', {})
    else:
        assets = asset_data.get(f'{product}_logos', {})
    
    if not assets:
        return f"Sorry, no {product.title()} logos available."
    
    # Parse background from request
    request_lower = request.lower()
    if not background:
        if 'light' in request_lower or 'white' in request_lower:
            background = 'light'
        elif 'dark' in request_lower or 'black' in request_lower:
            background = 'dark'
    
    if not background:
        return f"""{product.title()} logo - got it!

What **background**:
• **Light background** (black logo)
• **Dark background** (white logo)"""
    
    # Find matching asset
    for key, asset in assets.items():
        if background in key:
            return f"""Here's your {product.title()} logo:
**Download:** {asset['url']}

Perfect for {background} backgrounds"""
    
    # Fallback to first asset
    first_asset = next(iter(assets.values()))
    return f"""Here's your {product.title()} logo:
**Download:** {first_asset['url']}

{product.title()} branding asset"""

@mcp.tool()  
def list_all_assets() -> str:
    """List all available brand assets"""
    
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, couldn't load brand assets data."
    
    all_products = get_all_products()
    
    result = f"""# CIQ Brand Assets

**{len(all_products)} Products Available:**
{', '.join([p.title() for p in all_products])}

**Usage:**
- "CIQ logo for light background"
- "Fuzzball symbol for dark background"  
- "Apptainer logo"
- "Warewulf symbol"

Each product has multiple variants for different backgrounds and use cases."""
    
    return result

# Load data on startup
load_asset_data()

# FastMCP Cloud will handle the server startup
if __name__ == "__main__":
    mcp.run()
