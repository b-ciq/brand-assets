#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - Minimal FastMCP Cloud Version
Based on FastMCP Cloud examples and working local server
"""

from fastmcp import FastMCP
import requests

# Initialize server
mcp = FastMCP("CIQ Brand Assets")

@mcp.tool()
def get_brand_asset(request: str) -> str:
    """
    Get CIQ brand assets with smart recommendations.
    
    Examples:
    - "CIQ logo"
    - "Fuzzball logo"  
    - "Apptainer logo"
    """
    
    try:
        # Load asset data from GitHub
        response = requests.get('https://raw.githubusercontent.com/b-ciq/brand-assets/main/metadata/asset-inventory.json', timeout=5)
        response.raise_for_status()
        asset_data = response.json()
        
        # Simple logic for testing
        if 'ciq' in request.lower():
            if 'logos' in asset_data:
                first_logo = next(iter(asset_data['logos'].values()))
                return f"""Here's your CIQ logo:
**Download:** {first_logo['url']}

CIQ branding asset from cloud server"""
        
        elif 'fuzzball' in request.lower():
            if 'fuzzball_logos' in asset_data:
                first_logo = next(iter(asset_data['fuzzball_logos'].values()))
                return f"""Here's your Fuzzball logo:
**Download:** {first_logo['url']}

Fuzzball branding asset from cloud server"""
        
        # List available products
        products = []
        if 'logos' in asset_data:
            products.append('CIQ')
        if 'fuzzball_logos' in asset_data:
            products.append('Fuzzball')
        for key in asset_data.keys():
            if key.endswith('_logos') and key not in ['fuzzball_logos']:
                products.append(key.replace('_logos', '').title())
        
        return f"""Which logo do you need?

Available: {', '.join(products)}

Example: "CIQ logo", "Fuzzball logo" """
        
    except Exception as e:
        return f"Sorry, couldn't load brand assets: {str(e)}"

@mcp.tool()
def test_connection() -> str:
    """Test if the server is working"""
    return "✅ CIQ Brand Assets server is working on FastMCP Cloud!"

# This is the standard FastMCP Cloud pattern
if __name__ == "__main__":
    mcp.run()
