#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - Corrected Product Logic
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
            product_name = key.replace('_logos', '').replace('-', ' ').replace('_', ' ')
            products.append(product_name)
    
    return products

def determine_logo_type(request: str) -> str:
    """Determine which product logo the user wants"""
    request_lower = request.lower()
    
    # CIQ company brand keywords
    if any(keyword in request_lower for keyword in ['ciq', 'company logo', 'main logo', 'brand logo']):
        return 'ciq'
    
    # Product-specific keywords
    product_keywords = {
        'fuzzball': ['fuzzball', 'fuzz ball'],
        'apptainer': ['apptainer'],
        'warewulf pro': ['warewulf', 'warewulf pro'],
        'ascender pro': ['ascender', 'ascender pro'],
        'bridge': ['bridge', 'centos bridge'],
        'rlcx': ['rlc', 'rocky linux', 'rlc-ai', 'rlc ai', 'rlc hardened', 'rlc-hardened'],
        'ciq support': ['ciq support', 'support']
    }
    
    for product, keywords in product_keywords.items():
        if any(keyword in request_lower for keyword in keywords):
            return product
    
    return 'unclear'

@mcp.tool()
def get_brand_asset(request: str, background: Optional[str] = None, logo_type: Optional[str] = None) -> str:
    """
    Get CIQ brand assets with intelligent recommendations.
    
    CIQ Company Brand:
    - "CIQ logo" - 1-color (standard) or 2-color (hero) versions
    
    Product Brands:
    - "Fuzzball logo" - HPC/AI workload management platform
    - "Warewulf logo" - HPC cluster provisioning tool
    - "Apptainer logo" - Container platform for HPC/scientific workflows  
    - "Ascender logo" - Infrastructure automation (Ansible alternative)
    - "Bridge logo" - CentOS 7 migration solution
    - "RLC logo" - Rocky Linux Commercial variants (AI, Hardened)
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

**Company Brand:**
• **CIQ** - Main company logo

**Product Brands:**
• **Fuzzball** - HPC/AI workload management platform
• **Warewulf** - HPC cluster provisioning tool  
• **Apptainer** - Container platform for HPC/scientific workflows
• **Ascender** - Infrastructure automation platform
• **Bridge** - CentOS 7 migration solution
• **RLC** - Rocky Linux Commercial (AI, Hardened variants)

Example: "CIQ logo", "Fuzzball logo", "Warewulf symbol" """

    # Handle CIQ company brand (unique structure)
    if product == 'ciq':
        return handle_ciq_company_logo(request, background, logo_type)
    
    # Handle product brands (standard structure)  
    return handle_product_logo(product, request, background, logo_type)

def handle_ciq_company_logo(request: str, background: Optional[str], version_type: Optional[str]) -> str:
    """Handle CIQ company logo requests - 1-color vs 2-color"""
    
    # Parse version preference from request
    request_lower = request.lower()
    if not version_type:
        if '2 color' in request_lower or 'two color' in request_lower or 'hero' in request_lower:
            version_type = '2color'
        elif '1 color' in request_lower or 'one color' in request_lower or 'standard' in request_lower:
            version_type = '1color'
    
    # Parse background from request
    if not background:
        if 'light' in request_lower or 'white' in request_lower:
            background = 'light'
        elif 'dark' in request_lower or 'black' in request_lower:
            background = 'dark'
    
    # Ask for missing information
    if not background and not version_type:
        return """CIQ company logo - got it!

**Version:**
• **1-color** - Standard version for most applications  
• **2-color** - Hero version when logo is the primary visual element

**Background:**
• **Light background** (dark logo)
• **Dark background** (light logo)"""
    
    elif not background:
        version_desc = "1-color" if version_type == "1color" else "2-color"
        return f"""CIQ {version_desc} logo - got it!

**Background:**
• **Light background** (dark logo)
• **Dark background** (light logo)"""
        
    elif not version_type:
        bg_desc = "light" if background == "light" else "dark"
        return f"""CIQ logo for {bg_desc} background - got it!

**Version:**
• **1-color** - Standard version for most applications
• **2-color** - Hero version when logo is the primary visual element"""
    
    # Find CIQ asset
    ciq_assets = asset_data.get('logos', {})
    for key, asset in ciq_assets.items():
        if version_type in key and background in key:
            reasoning = 'Maximum brand recognition - use when logo is the primary visual element' if version_type == '2color' else 'Clean and professional - works in most contexts'
            return f"""Here's your CIQ {version_type} logo:
**Download:** {asset['url']}

{reasoning}"""
    
    return f"Sorry, couldn't find CIQ {version_type} logo for {background} backgrounds."

def handle_product_logo(product: str, request: str, background: Optional[str], logo_type: Optional[str]) -> str:
    """Handle product logo requests - horizontal/vertical/symbol variants"""
    
    # Parse preferences from request
    request_lower = request.lower()
    if not logo_type:
        if 'symbol' in request_lower or 'icon' in request_lower:
            logo_type = 'symbol'
        elif 'horizontal' in request_lower or 'lockup' in request_lower:
            logo_type = 'horizontal'
        elif 'vertical' in request_lower:
            logo_type = 'vertical'
    
    if not background:
        if 'light' in request_lower or 'white' in request_lower:
            background = 'light'
        elif 'dark' in request_lower or 'black' in request_lower:
            background = 'dark'
    
    # Product descriptions
    descriptions = {
        'fuzzball': 'HPC/AI workload management platform',
        'warewulf pro': 'HPC cluster provisioning tool', 
        'apptainer': 'Container platform for HPC/scientific workflows',
        'ascender pro': 'Infrastructure automation platform (Ansible alternative)',
        'bridge': 'CentOS 7 migration solution',
        'rlcx': 'Rocky Linux Commercial variants (AI, Hardened)'
    }
    
    product_desc = descriptions.get(product, f'{product} product')
    
    # Ask for missing information
    if not background and not logo_type:
        return f"""{product.title()} logo - got it!
*{product_desc}*

**Logo Type:**
• **Symbol only** - Just the icon (tight spaces)
• **Horizontal lockup** - Symbol + text side-by-side
• **Vertical lockup** - Symbol + text stacked

**Background:**
• **Light background** (black logo)
• **Dark background** (white logo)"""
    
    elif not background:
        logo_desc = logo_type if logo_type else "logo"
        return f"""{product.title()} {logo_desc} - got it!

**Background:**
• **Light background** (black logo)  
• **Dark background** (white logo)"""
        
    elif not logo_type:
        bg_desc = "light" if background == "light" else "dark"
        return f"""{product.title()} for {bg_desc} background - got it!

**Logo Type:**
• **Symbol only** - Just the icon (tight spaces)
• **Horizontal lockup** - Symbol + text side-by-side  
• **Vertical lockup** - Symbol + text stacked"""
    
    # Find matching asset
    product_key = product.replace(' ', '-').lower()
    if product == 'rlcx':
        product_assets = asset_data.get('rlcx_logos', {})
    else:
        product_assets = asset_data.get(f'{product_key}_logos', {})
    
    if not product_assets:
        return f"Sorry, no {product.title()} logos available."
    
    # Search for best match
    target_color = 'black' if background == 'light' else 'white'
    
    for key, asset in product_assets.items():
        asset_layout = asset.get('layout', '').lower()
        asset_color = asset.get('color', '').lower()
        
        # Match logo type and color
        if ((logo_type == 'symbol' and 'icon' in asset_layout) or
            (logo_type == 'horizontal' and 'horizontal' in asset_layout) or  
            (logo_type == 'vertical' and 'vertical' in asset_layout)):
            if target_color in asset_color:
                return f"""Here's your {product.title()} {logo_type}:
**Download:** {asset['url']}

{asset.get('guidance', f'Perfect {product.title()} branding for {background} backgrounds')}"""
    
    # Fallback
    first_asset = next(iter(product_assets.values()))
    return f"""Here's your {product.title()} logo:
**Download:** {first_asset['url']}

{product_desc}"""

@mcp.tool()  
def list_all_assets() -> str:
    """List all available CIQ brand assets"""
    
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, couldn't load brand assets data."
    
    result = """# CIQ Brand Assets Library

## CIQ Company Brand
**Structure:** 1-color (standard) and 2-color (hero) versions only
- No symbol-only or vertical variants

## Product Brands  
**Structure:** Each has symbol-only, horizontal lockup, and vertical lockup
- All available for light and dark backgrounds

**Available Products:**
"""

    all_products = get_all_products()
    descriptions = {
        'fuzzball': 'HPC/AI workload management platform',
        'warewulf pro': 'HPC cluster provisioning tool',
        'apptainer': 'Container platform for HPC/scientific workflows', 
        'ascender pro': 'Infrastructure automation platform',
        'bridge': 'CentOS 7 migration solution',
        'rlcx': 'Rocky Linux Commercial (RLC-AI, RLC-Hardened)'
    }
    
    for product in all_products:
        if product != 'ciq':
            desc = descriptions.get(product, f'{product} product')
            result += f"• **{product.title()}** - {desc}\n"
    
    result += f"""

**Usage Examples:**
- "CIQ 2-color logo for light background"
- "Fuzzball horizontal lockup for dark background" 
- "Warewulf symbol for email signature"
- "Apptainer vertical lockup for presentation"

Just describe what you need!"""
    
    return result

# Load data on startup  
load_asset_data()

# FastMCP Cloud will handle the server startup
if __name__ == "__main__":
    mcp.run()
