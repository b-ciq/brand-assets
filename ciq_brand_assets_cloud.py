#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - Cloud Deployment Version
Intelligent brand asset delivery with smart logo recommendations for all products
Optimized for FastMCP Cloud hosting
"""

from mcp.server.fastmcp import FastMCP
import json
import requests
from typing import Optional, Dict, Any
import asyncio
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Asset metadata URL
METADATA_URL = 'https://raw.githubusercontent.com/b-ciq/brand-assets/main/metadata/asset-inventory.json'

# Initialize FastMCP server with cloud-optimized settings
mcp = FastMCP(
    name="CIQ Brand Assets",
    instructions="""
    I provide intelligent brand asset delivery for all CIQ products with smart logo recommendations.
    
    Available products: CIQ, Fuzzball, Apptainer, Warewulf-Pro, Ascender-Pro, Bridge, RLC(X), CIQ-Support
    
    Just describe what you need:
    - "CIQ logo for email signature" 
    - "Fuzzball symbol for dark background"
    - "Apptainer logo"
    - "Warewulf symbol"
    
    I'll guide you through the best options with brand compliance built-in.
    """
)

# Global asset data cache
asset_data = None

def load_asset_data():
    """Load asset metadata from GitHub using requests"""
    global asset_data
    try:
        logger.info("Loading asset metadata from GitHub...")
        response = requests.get(METADATA_URL, timeout=10)
        response.raise_for_status()
        asset_data = response.json()
        logger.info(f"Loaded metadata for {len(asset_data)} asset categories")
        return True
    except Exception as e:
        logger.error(f"Failed to load asset data: {e}")
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
    
    # Generic request should ask for clarification
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

def parse_user_response(response: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Parse user response for background, version type, and logo type"""
    response_lower = response.lower()
    
    # Parse background
    background = None
    if any(word in response_lower for word in ['light', 'light background', 'white']):
        background = 'light'
    elif any(word in response_lower for word in ['dark', 'dark background', 'black']):
        background = 'dark'
    
    # Parse CIQ version type
    ciq_version = None
    if '2 color' in response_lower or 'two color' in response_lower or 'hero' in response_lower:
        ciq_version = '2color'
    elif '1 color' in response_lower or 'one color' in response_lower or 'standard' in response_lower:
        ciq_version = '1color'
    
    # Parse logo type (symbol vs logotype)
    logo_type = None
    if 'symbol' in response_lower or 'icon' in response_lower or 'just symbol' in response_lower:
        logo_type = 'symbol'
    elif 'logotype' in response_lower or 'full logo' in response_lower or 'text' in response_lower or 'lockup' in response_lower:
        logo_type = 'logotype'
    
    return background, ciq_version, logo_type

@mcp.tool()
async def get_brand_asset(
    request: str,
    background: Optional[str] = None,
    element_type: Optional[str] = None,
    design_context: Optional[str] = None
) -> str:
    """
    Get CIQ brand assets with intelligent recommendations.
    
    Just tell me what you need:
    - "I need a CIQ logo" 
    - "Fuzzball logo"
    - "Apptainer symbol for dark background"
    - "Warewulf logo"
    
    Args:
        request: What logo do you need?
        background: What background? ('light' or 'dark') 
        element_type: For CIQ - standard or hero? For others - symbol or full logotype?
        design_context: Optional context (not used for decisions)
    """
    
    # Load data if not already loaded
    if asset_data is None:
        await asyncio.get_event_loop().run_in_executor(None, load_asset_data)
    
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

    # Handle the request for the specific product
    return await handle_product_request(product, request, background, element_type)

async def handle_product_request(product: str, request: str, background: Optional[str], logo_type: Optional[str]) -> str:
    """Handle logo requests for any product"""
    
    # Get assets for this product
    product_assets = get_product_assets(product)
    
    if not product_assets:
        return f"Sorry, I don't have {product.title()} logos available yet."
    
    # Parse from request if not provided
    parsed_background, parsed_ciq_version, parsed_logo_type = parse_user_response(request)
    if parsed_background:
        background = parsed_background
    if parsed_logo_type:
        logo_type = parsed_logo_type
    elif parsed_ciq_version and product == 'ciq':
        logo_type = parsed_ciq_version
    
    # Handle CIQ specially (has unique 1color/2color system)
    if product == 'ciq':
        return await handle_ciq_request(request, background, logo_type, product_assets)
    
    # Handle all other products (symbol vs logotype)
    return await handle_generic_product_request(product, request, background, logo_type, product_assets)

async def handle_ciq_request(request: str, background: Optional[str], version_type: Optional[str], assets: Dict[str, Any]) -> str:
    """Handle CIQ logo requests with 1color/2color logic"""
    
    # Ask for missing information
    if not background and not version_type:
        return """CIQ logo - got it!

Do you want:
• **1-color** - Standard version
• **2-color** - Hero version (main branding)

And what **background**:
• **Light background** (dark logo)
• **Dark background** (light logo)"""
    
    elif not background:
        version_desc = "1-color" if version_type == "1color" else "2-color"
        return f"""CIQ {version_desc} - got it!

What **background**:
• **Light background** (dark logo)
• **Dark background** (light logo)"""
        
    elif not version_type:
        bg_desc = "light" if background == "light" else "dark"
        return f"""CIQ for {bg_desc} background - got it!

Do you want:
• **1-color** - Standard version
• **2-color** - Hero version (main branding)"""
    
    # Find the right asset
    asset_key = f'{version_type}-{background}'
    
    # Find matching asset (may need to search through assets)
    matching_asset = None
    for key, asset in assets.items():
        if version_type in key and background in key:
            matching_asset = asset
            break
    
    if not matching_asset:
        return f"Sorry, I couldn't find the CIQ {version_type} logo for {background} backgrounds."
    
    reasoning = 'Maximum brand recognition - use when logo is the primary element' if version_type == '2color' else 'Clean and professional - works in most contexts'
    
    return f"""Here's your CIQ logo:
**Download:** {matching_asset['url']}

{reasoning}"""

async def handle_generic_product_request(product: str, request: str, background: Optional[str], logo_type: Optional[str], assets: Dict[str, Any]) -> str:
    """Handle logo requests for all non-CIQ products"""
    
    # Ask for missing information
    if not background and not logo_type:
        return f"""{product.title()} logo - got it!

Do you want:
• **Symbol only** - Just the icon
• **Full logotype** - Symbol + text lockup

And what **background**:
• **Light background** (black logo)
• **Dark background** (white logo)"""
    
    elif not background:
        logo_desc = "symbol" if logo_type == "symbol" else "full logotype"
        return f"""{product.title()} {logo_desc} - got it!

What **background**:
• **Light background** (black logo)
• **Dark background** (white logo)"""
        
    elif not logo_type:
        bg_desc = "light" if background == "light" else "dark"
        return f"""{product.title()} for {bg_desc} background - got it!

Do you want:
• **Symbol only** - Just the icon  
• **Full logotype** - Symbol + text lockup"""
    
    # Find matching asset
    target_layout = 'icon' if logo_type == 'symbol' else 'horizontal'  # Default to horizontal for logotype
    target_color = 'black' if background == 'light' else 'white'
    
    # Search for best matching asset
    best_match = None
    for key, asset in assets.items():
        if (asset.get('layout') == target_layout and 
            asset.get('color') == target_color and
            asset.get('size') in ['medium', 'large']):  # Prefer medium or large
            best_match = asset
            break
    
    # Fallback to any asset with right background
    if not best_match:
        for key, asset in assets.items():
            if (asset.get('background') == background and 
                asset.get('layout', '').lower() != 'unknown'):
                best_match = asset
                break
    
    if not best_match:
        return f"Sorry, I couldn't find the {product.title()} logo for {background} backgrounds."
    
    logo_desc = "symbol" if logo_type == "symbol" else "logotype"
    
    return f"""Here's your {product.title()} {logo_desc}:
**Download:** {best_match['url']}

{best_match.get('guidance', f'Perfect {product.title()} branding!')}"""

@mcp.tool()
async def list_all_assets() -> str:
    """List all available CIQ brand assets with descriptions and download links"""
    
    # Load data if not already loaded
    if asset_data is None:
        await asyncio.get_event_loop().run_in_executor(None, load_asset_data)
    
    if asset_data is None:
        return "Sorry, I couldn't load the brand assets data. Please try again later."
    
    result = "# CIQ Brand Assets Library\n\n"
    
    # Get all products dynamically
    all_products = get_all_products()
    
    for product in all_products:
        product_assets = get_product_assets(product)
        
        if product_assets:
            result += f"## {product.title().replace('-', ' ').replace('_', ' ')} Logos\n\n"
            
            # Show a few key assets for each product (not all - too many!)
            asset_count = 0
            for key, asset in product_assets.items():
                if asset_count < 3:  # Show max 3 per product
                    result += f"• **{asset['filename']}** - {asset['description']}\n  {asset['url']}\n\n"
                    asset_count += 1
            
            if len(product_assets) > 3:
                result += f"• *...and {len(product_assets) - 3} more {product.title()} variants*\n\n"
    
    result += f"""## Quick Reference

**Available Products:** {', '.join([p.title() for p in all_products])}

**For CIQ:**
- **1-color** - Standard version 
- **2-color** - Hero version for primary branding

**For All Other Products:**  
- **Symbol only** - Just the icon (tight spaces)
- **Full logotype** - Symbol + text (primary branding)

**All products available for:**
- **Light background** (black logo)
- **Dark background** (white logo)

Just tell me what you need: "Apptainer logo", "Warewulf symbol for dark background", etc."""
    
    return result

@mcp.tool()
async def brand_guidelines() -> str:
    """Get CIQ brand guidelines and usage rules"""
    
    # Load data if not already loaded
    if asset_data is None:
        await asyncio.get_event_loop().run_in_executor(None, load_asset_data)
    
    if asset_data is None:
        return "Sorry, I couldn't load the brand assets data. Please try again later."
    
    guidelines = asset_data.get('brand_guidelines', {})
    available_products = get_all_products()
    
    return f"""# CIQ Brand Guidelines

## Available Products

**{len(available_products)} Products Available:** {', '.join([p.title() for p in available_products])}

## Logo Usage Rules

**Clear Space:**
• Maintain clear space equal to **{guidelines.get('clear_space', '1/4 the height of the Q')}**
• Never place text, images, or other elements within this protected area

**Minimum Size:**
• **Digital:** {guidelines.get('minimum_size', '70px height')}
• Never scale smaller than minimum requirements
• Always maintain aspect ratio - never stretch or compress

## Brand Colors

**Primary Green:** `{guidelines.get('primary_green', '#229529')}` (PMS 347)

## Logo Selection Guide

**CIQ Logos:**
• **1-color** - Standard version for most applications
• **2-color** - Hero version when logo is the primary visual element

**All Other Product Logos:**
• **Symbol only** - Use when space is limited or you need just the recognizable icon
• **Full logotype** - Use for primary branding when you want symbol + text

**Background Selection (All Products):**
• Light background = black logo, Dark background = white logo

## What NOT to Do
• Don't alter logo colors, fonts, or proportions
• Don't place logos on busy backgrounds without proper contrast  
• Don't ignore minimum size requirements
• Don't use outdated logo versions

Need help choosing? Just describe what you need: "Apptainer logo", "Warewulf symbol", etc."""

if __name__ == "__main__":
    # Load asset data on startup
    logger.info("Starting CIQ Brand Assets MCP Server for FastMCP Cloud...")
    load_asset_data()
    
    # Cloud deployment: Use streamable-http transport
    # FastMCP Cloud expects this transport type
    port = int(os.getenv("PORT", 8080))
    
    logger.info(f"Server starting on port {port} with streamable-http transport")
    
    # Run with cloud-optimized settings
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",  # Required for cloud deployment
        port=port,
        path="/mcp"  # Standard MCP endpoint
    )
