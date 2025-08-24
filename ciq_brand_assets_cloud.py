#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - FastMCP Cloud Version  
Intelligent brand asset delivery with accurate CIQ product information
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

@mcp.tool()
def get_brand_asset(request: str, background: Optional[str] = None) -> str:
    """
    Get CIQ brand assets with intelligent recommendations.
    
    CIQ Company Brand: 1-color (standard) or 2-color (hero)
    Product Brands: Symbol, horizontal lockup, or vertical lockup
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
    
    # Handle CIQ company logo
    if 'ciq' in request_lower:
        if not background:
            return """CIQ logo - got it!

**Background:**
• **Light background** (dark logo)
• **Dark background** (light logo)"""
        
        # Find CIQ asset for background
        ciq_assets = asset_data.get('logos', {})
        for key, asset in ciq_assets.items():
            if background in key and '2color' in key:  # Prefer 2color
                return f"""Here's your CIQ logo:
**Download:** {asset['url']}

Maximum brand recognition for primary branding"""
        
        # Fallback to any matching background
        for key, asset in ciq_assets.items():
            if background in key:
                return f"""Here's your CIQ logo:
**Download:** {asset['url']}

Clean CIQ branding"""
    
    # Handle Warewulf
    elif 'warewulf' in request_lower:
        if not background:
            return """Warewulf logo - HPC cluster provisioning tool!

**Background:**
• **Light background** (black logo)
• **Dark background** (white logo)"""
        
        # Find Warewulf asset
        warewulf_assets = asset_data.get('warewulf-pro_logos', {})
        target_color = 'black' if background == 'light' else 'white'
        
        for key, asset in warewulf_assets.items():
            if target_color in asset.get('color', '').lower():
                return f"""Here's your Warewulf logo:
**Download:** {asset['url']}

Perfect for HPC cluster management branding"""
        
        # Fallback
        if warewulf_assets:
            first_asset = next(iter(warewulf_assets.values()))
            return f"""Here's your Warewulf logo:
**Download:** {first_asset['url']}

HPC cluster provisioning tool branding"""
    
    # Handle other products
    elif any(product in request_lower for product in ['fuzzball', 'apptainer', 'ascender', 'bridge']):
        product_found = None
        for product in ['fuzzball', 'apptainer', 'ascender', 'bridge']:
            if product in request_lower:
                product_found = product
                break
        
        if not background:
            return f"""{product_found.title()} logo - got it!

**Background:**
• **Light background** (black logo)
• **Dark background** (white logo)"""
        
        # Try to find asset
        product_assets = asset_data.get(f'{product_found}_logos', {})
        if product_assets:
            first_asset = next(iter(product_assets.values()))
            return f"""Here's your {product_found.title()} logo:
**Download:** {first_asset['url']}

{product_found.title()} branding asset"""
    
    return """Which logo do you need?

**Available:**
• **CIQ** - Company logo
• **Fuzzball** - HPC/AI platform  
• **Warewulf** - HPC cluster tool
• **Apptainer** - Container platform
• **Ascender** - Automation platform
• **Bridge** - CentOS migration

Example: "CIQ logo", "Warewulf logo", "Fuzzball logo" """

@mcp.tool()  
def list_all_assets() -> str:
    """List all available brand assets"""
    
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, couldn't load brand assets data."
    
    return """# CIQ Brand Assets

**Available Products:**
• **CIQ** - Company brand (1-color, 2-color)
• **Fuzzball** - HPC/AI workload platform
• **Warewulf** - HPC cluster provisioning  
• **Apptainer** - HPC container platform
• **Ascender** - Infrastructure automation
• **Bridge** - CentOS migration solution

**Usage:**
- "CIQ 2-color logo for light background"
- "Warewulf logo for white background"
- "Fuzzball symbol for dark background"

Each product has multiple variants!"""

# Load data on startup
load_asset_data()

# FastMCP Cloud entry point
if __name__ == "__main__":
    mcp.run()
