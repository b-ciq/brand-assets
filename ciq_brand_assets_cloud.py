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
    
    # Simple working logic for now
    if 'ciq' in request.lower():
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
    
    return "Which logo do you need? CIQ, Fuzzball, Warewulf, Apptainer, etc.?"

@mcp.tool()  
def list_all_assets() -> str:
    """List all available brand assets"""
    
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, couldn't load brand assets data."
    
    return "# CIQ Brand Assets\n\nAvailable: CIQ, Fuzzball, Warewulf, Apptainer, Ascender, Bridge, RLC variants\n\nJust ask: 'CIQ logo', 'Fuzzball logo', etc."

# Load data on startup
load_asset_data()

# FastMCP Cloud entry point
if __name__ == "__main__":
    mcp.run()
