#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - FastMCP Cloud Version  
Fixed to work with actual metadata structure
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
    
    # Handle CIQ company logo
    if 'ciq' in request_lower and not any(word in request_lower for word in ['support', 'bridge']):
        if not background:
            return """CIQ logo - got it!

**Background:**
• **Light background** (dark logo)
• **Dark background** (light logo)"""
        
        # Find CIQ asset - try multiple keys since metadata structure varies
        ciq_assets = asset_data.get('logos', {})
        
        # Look for assets matching background
        for key, asset in ciq_assets.items():
            asset_bg = asset.get('background', '')
            if background in asset_bg or background in key:
                return f"""Here's your CIQ logo:
**Download:** {asset['url']}

{asset.get('guidance', 'Clean CIQ company branding')}"""
        
        return f"Sorry, couldn't find CIQ logo for {background} background."
    
    # Handle Warewulf - use correct key from metadata
    elif 'warewulf' in request_lower:
        if not background:
            return """Warewulf logo - HPC cluster provisioning tool!

**Background:**
• **Light background** (black logo)
• **Dark background** (white logo)"""
        
        # Use correct metadata key
        warewulf_assets = asset_data.get('warewulf-pro_logos', {})
        
        # Find asset matching background
        for key, asset in warewulf_assets.items():
            asset_bg = asset.get('background', '')
            if background == asset_bg:
                return f"""Here's your Warewulf logo:
**Download:** {asset['url']}

{asset.get('guidance', 'HPC cluster provisioning tool branding')}"""
        
        return f"Sorry, couldn't find Warewulf logo for {background} background."
    
    # Handle other products
    elif 'fuzzball' in request_lower:
        if not background:
            return """Fuzzball - HPC/AI workload platform!

**Background:**
• **Light background** (black logo)
• **Dark background** (white logo)"""
        
        fuzzball_assets = asset_data.get('fuzzball_logos', {})
        for key, asset in fuzzball_assets.items():
            if background == asset.get('background', ''):
                return f"""Here's your Fuzzball logo:
**Download:** {asset['url']}

{asset.get('guidance', 'HPC/AI workload management platform')}"""
    
    elif 'apptainer' in request_lower:
        if not background:
            return """Apptainer - Container platform for HPC!

**Background:**
• **Light background** (black logo)
• **Dark background** (white logo)"""
        
        apptainer_assets = asset_data.get('apptainer_logos', {})
        for key, asset in apptainer_assets.items():
            if background == asset.get('background', ''):
                return f"""Here's your Apptainer logo:
**Download:** {asset['url']}

{asset.get('guidance', 'Container platform for HPC/scientific workflows')}"""
    
    return """Which logo do you need?

**Available:**
• **CIQ** - Company logo  
• **Fuzzball** - HPC/AI workload platform
• **Warewulf** - HPC cluster provisioning tool
• **Apptainer** - Container platform for HPC
• **Ascender** - Infrastructure automation
• **Bridge** - CentOS migration solution

Example: "Warewulf logo for white background" """

@mcp.tool()  
def list_all_assets() -> str:
    """List all available brand assets"""
    
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, couldn't load brand assets data."
    
    # Show what's actually available from metadata
    available_categories = list(asset_data.keys())
    
    return f"""# CIQ Brand Assets

**Available Categories:** {len(available_categories)}

**Products:**
• **CIQ** - Company brand
• **Fuzzball** - HPC/AI workload platform  
• **Warewulf-Pro** - HPC cluster provisioning tool
• **Apptainer** - Container platform for HPC
• **Ascender-Pro** - Infrastructure automation
• **Bridge** - CentOS migration solution

**Usage:**
- "CIQ logo for light background"
- "Warewulf logo for white background"  
- "Fuzzball logo for dark background"

Found {len(available_categories)} asset categories in metadata."""

# Load data on startup
load_asset_data()

# FastMCP Cloud entry point
if __name__ == "__main__":
    mcp.run()
