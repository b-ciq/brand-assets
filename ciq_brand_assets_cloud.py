#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - FastMCP Cloud Version  
Fixed to use proper metadata structure for ALL products
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

def find_matching_asset(assets: Dict[str, Any], background: str, layout: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Find asset matching background and optionally layout using metadata fields"""
    
    # First pass - exact matches
    for key, asset in assets.items():
        asset_bg = asset.get('background', '').lower()
        asset_layout = asset.get('layout', '').lower()
        
        if background == asset_bg:
            if layout and layout in asset_layout:
                return asset
            elif not layout:  # Background match is enough
                return asset
    
    # Second pass - partial matches (fallback)
    for key, asset in assets.items():
        if background in key.lower():
            return asset
    
    return None

@mcp.tool()
def get_brand_asset(request: str, background: Optional[str] = None) -> str:
    """
    Get CIQ brand assets with intelligent recommendations.
    
    Examples:
    - "CIQ logo for light background"
    - "Warewulf logo for white background"  
    - "Fuzzball symbol for dark background"
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

**Available:**
• **CIQ** - Company logo  
• **Fuzzball** - HPC/AI workload platform
• **Warewulf** - HPC cluster provisioning tool
• **Apptainer** - Container platform for HPC
• **Ascender** - Infrastructure automation
• **Bridge** - CentOS migration solution
• **RLC** - Rocky Linux Commercial variants

Example: "Warewulf logo for white background" """
    
    # Get assets for this product
    assets = find_product_assets(product)
    
    if not assets:
        return f"Sorry, no {product.title()} logos found in metadata."
    
    # Ask for background if not provided
    if not background:
        product_descriptions = {
            'ciq': 'Company logo',
            'fuzzball': 'HPC/AI workload platform',
            'warewulf': 'HPC cluster provisioning tool',
            'apptainer': 'Container platform for HPC',
            'ascender': 'Infrastructure automation',
            'bridge': 'CentOS migration solution',
            'rlc': 'Rocky Linux Commercial variants',
            'support': 'Support division'
        }
        
        desc = product_descriptions.get(product, f'{product} product')
        return f"""{product.title()} - {desc}!

**Background:**
• **Light background** (black logo)
• **Dark background** (white logo)"""
    
    # Find matching asset using metadata
    matching_asset = find_matching_asset(assets, background)
    
    if matching_asset:
        return f"""Here's your {product.title()} logo:
**Download:** {matching_asset['url']}

{matching_asset.get('guidance', f'{product.title()} branding for {background} backgrounds')}"""
    
    return f"Sorry, couldn't find {product.title()} logo for {background} background."

@mcp.tool()  
def list_all_assets() -> str:
    """List all available brand assets"""
    
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
                    product_name = 'CIQ'
                product_info.append(f"• **{product_name}** ({asset_count} variants)")
    
    result = f"""# CIQ Brand Assets Library

**{total_products} Products, {total_assets} Total Assets**

"""
    result += '\n'.join(product_info)
    
    result += """

**Usage Examples:**
- "CIQ logo for light background"
- "Warewulf logo for white background"  
- "Fuzzball symbol for dark background"
- "Apptainer horizontal lockup"

Each product has multiple layouts and backgrounds available!"""
    
    return result

# Load data on startup
load_asset_data()

# FastMCP Cloud entry point
if __name__ == "__main__":
    mcp.run()
