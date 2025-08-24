#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - Simple FastMCP Cloud Version
Intelligent brand asset delivery with smart logo recommendations
"""

from mcp.server.fastmcp import FastMCP
import json
import requests
from typing import Optional, Dict, Any

# Asset metadata URL
METADATA_URL = 'https://raw.githubusercontent.com/b-ciq/brand-assets/main/metadata/asset-inventory.json'

# Initialize FastMCP server - simple version for cloud
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
        return True
    except Exception as e:
        print(f"Failed to load asset data: {e}")
        return False

def get_all_products() -> list[str]:
    """Get list of all available products from metadata"""
    if not asset_data:
        return []
    
    products = []
    
    # Add standard products
    if 'logos' in asset_data:
        products.append('ciq')
    if 'fuzzball_logos' in asset_data:
        products.append('fuzzball')
    
    # Add all other products (ending with _logos)
    for key in asset_data.keys():
        if key.endswith('_logos') and key not in ['fuzzball_logos']:
            product_name = key.replace('_logos', '')
            products.append(product_name)
    
    return products

def determine_logo_type(request: str) -> str:
    """Determine which product logo the user is requesting"""
    request_lower = request.lower()
    
    # Get all available products
    available_products = get_all_products()
    
    # Check for specific product keywords
    product_keywords = {
        'ciq': ['ciq', 'company logo', 'main logo', 'brand logo'],
        'fuzzball': ['fuzzball', 'fuzz ball'],
        'apptainer': ['apptainer'],
        'warewulf-pro': ['warewulf', 'warewulf pro', 'warewulf-pro'],
        'ascender-pro': ['ascender', 'ascender pro', 'ascender-pro'],
        'bridge': ['bridge'],
        'rlcx': ['rlc', 'rocky linux', 'rocky', 'rlc-ai', 'rlc ai', 'rlc hardened', 'rlc-hardened'],
        'ciq-support': ['ciq support', 'ciq-support', 'support']
    }
    
    # Check each product
    for product, keywords in product_keywords.items():
        if product in available_products:
            if any(keyword in request_lower for keyword in keywords):
                return product
    
    return 'unclear'

def get_product_assets(product: str) -> Dict[str, Any]:
    """Get assets for a specific product"""
    if not asset_data:
        return {}
    
    if product == 'ciq':
        return asset_data.get('logos', {})
    elif product == 'fuzzball':
        return asset_data.get('fuzzball_logos', {})
    else:
        return asset_data.get(f'{product}_logos', {})

@mcp.tool()
def get_brand_asset(
    request: str,
    background: Optional[str] = None,
    element_type: Optional[str] = None
) -> str:
    """
    Get CIQ brand assets with intelligent recommendations.
    
    Just tell me what you need:
    - "I need a CIQ logo" 
    - "Fuzzball logo"
    - "Apptainer symbol for dark background"
    - "Warewulf logo"
    """
    
    # Load data if not already loaded
    if asset_data is None:
        load_asset_data()
    
    if asset_data is None:
        return "Sorry, I couldn't load the brand assets data. Please try again later."
    
    # Determine which product they want
    product = determine_logo_type(request)
    
    if product == 'unclear':
        available_products = get_all_products()
        product_list = ', '.join([p.title() for p in available_products])
        return f"""Which logo do you need?

Available products: **{product_list}**

For example: "CIQ logo", "Fuzzball logo", "Apptainer logo", "Warewulf logo" """

    # Simple CIQ handling
    if product == 'ciq':
        if not background:
            return """CIQ logo - got it!

What **background**:
• **Light background** (dark logo)
• **Dark background** (light logo)"""
        
        # Find CIQ asset
        product_assets = get_product_assets('ciq')
        for key, asset in product_assets.items():
            if background in key and '2color' in key:  # Prefer 2color
                return f"""Here's your CIQ logo:
**Download:** {asset['url']}

Maximum brand recognition - perfect for primary branding"""
        
        # Fallback to any matching background
        for key, asset in product_assets.items():
            if background in key:
                return f"""Here's your CIQ logo:
**Download:** {asset['url']}

Clean and professional CIQ branding"""
    
    # Handle other products
    product_assets = get_product_assets(product)
    if not product_assets:
        return f"Sorry, I don't have {product.title()} logos available yet."
    
    if not background:
        return f"""{product.title()} logo - got it!

What **background**:
• **Light background** (black logo)
• **Dark background** (white logo)"""
    
    # Find best matching asset
    target_color = 'black' if background == 'light' else 'white'
    
    for key, asset in product_assets.items():
        if target_color in asset.get('color', '') or target_color in key:
            return f"""Here's your {product.title()} logo:
**Download:** {asset['url']}

Perfect {product.title()} branding for {background} backgrounds"""
    
    # Fallback
    first_asset = next(iter(product_assets.values()))
    return f"""Here's your {product.title()} logo:
**Download:** {first_asset['url']}

{product.title()} branding asset"""

@mcp.tool()
def list_all_assets() -> str:
    """List all available CIQ brand assets"""
    
    if asset_data is None:
        load_asset_data()
    
    if asset_data is None:
        return "Sorry, I couldn't load the brand assets data."
    
    result = "# CIQ Brand Assets Library\n\n"
    all_products = get_all_products()
    
    for product in all_products:
        product_assets = get_product_assets(product)
        if product_assets:
            result += f"## {product.title().replace('-', ' ')} Logos\n"
            result += f"Available: {len(product_assets)} variants\n\n"
    
    result += f"""## Available Products
{', '.join([p.title() for p in all_products])}

Just ask: "CIQ logo", "Fuzzball symbol", "Apptainer logo", etc."""
    
    return result

# Simple startup for FastMCP Cloud
if __name__ == "__main__":
    load_asset_data()
    mcp.run()
