#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server
Intelligent brand asset delivery with smart logo recommendations
"""

from mcp.server.fastmcp import FastMCP
import json
import requests
from typing import Optional
import asyncio

# Asset metadata URL
METADATA_URL = 'https://raw.githubusercontent.com/b-ciq/brand-assets/main/metadata/asset-inventory.json'

# Initialize FastMCP server
mcp = FastMCP("CIQ Brand Assets")

# Global asset data cache
asset_data = None

def load_asset_data():
    """Load asset metadata from GitHub using requests"""
    global asset_data
    try:
        response = requests.get(METADATA_URL)
        response.raise_for_status()
        asset_data = response.json()
        return True
    except Exception as e:
        print(f"Failed to load asset data: {e}")
        return False

def determine_logo_type(request: str) -> str:
    """Determine which type of logo the user is requesting"""
    request_lower = request.lower()
    
    # Check for Fuzzball-specific keywords
    fuzzball_keywords = [
        'fuzzball', 'fuzz ball'
    ]
    
    if any(keyword in request_lower for keyword in fuzzball_keywords):
        return 'fuzzball'
    
    # Check for main CIQ logo indicators
    main_logo_keywords = [
        'ciq logo', 'ciq', 'company logo', 'main logo', 'brand logo'
    ]
    
    if any(keyword in request_lower for keyword in main_logo_keywords):
        return 'ciq'
    
    # Generic requests should ask for clarification
    return 'unclear'

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
    
    # Parse Fuzzball type
    fuzzball_type = None
    if 'symbol' in response_lower or 'icon' in response_lower or 'just symbol' in response_lower:
        fuzzball_type = 'symbol'
    elif 'logotype' in response_lower or 'full logo' in response_lower or 'text' in response_lower or 'lockup' in response_lower:
        fuzzball_type = 'logotype'
    
    return background, ciq_version, fuzzball_type

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
    - "CIQ 2-color for light background"
    - "Fuzzball symbol for dark background"
    
    Args:
        request: What logo do you need?
        background: What background? ('light' or 'dark') 
        element_type: For CIQ - standard or hero? For Fuzzball - symbol or full logotype?
        design_context: Optional context (not used for decisions)
    """
    
    # Load data if not already loaded
    if asset_data is None:
        await asyncio.get_event_loop().run_in_executor(None, load_asset_data)
    
    if asset_data is None:
        return "Sorry, I couldn't load the brand assets data. Please try again later."
    
    # Determine which logo type they want
    logo_type = determine_logo_type(request)
    
    if logo_type == 'unclear':
        return """Which logo do you need?

• **CIQ** - Company logo
• **Fuzzball** - Product logo"""

    elif logo_type == 'fuzzball':
        return await handle_fuzzball_request(request, background, element_type)
    
    elif logo_type == 'ciq':
        return await handle_ciq_request(request, background, element_type)
    
    return "I couldn't determine which logo you need. Please specify CIQ or Fuzzball."

async def handle_fuzzball_request(request: str, background: Optional[str], logo_type: Optional[str]) -> str:
    """Handle Fuzzball logo requests"""
    
    # Try to parse from request
    parsed_background, _, parsed_fuzzball_type = parse_user_response(request)
    if parsed_background:
        background = parsed_background
    if parsed_fuzzball_type:
        logo_type = parsed_fuzzball_type
    
    # Ask for missing information
    if not background and not logo_type:
        return """Fuzzball logo - got it!

Do you want:
• **Symbol only** - Just the Fuzzball icon
• **Full logotype** - Symbol + text lockup

And what **background**:
• **Light background** (we'll give you black)
• **Dark background** (we'll give you white)"""
    
    elif not background:
        logo_desc = "symbol" if logo_type == "symbol" else "full logotype"
        return f"""Fuzzball {logo_desc} - got it!

What **background**:
• **Light background** (black logo)
• **Dark background** (white logo)"""
        
    elif not logo_type:
        bg_desc = "light" if background == "light" else "dark"
        return f"""Fuzzball for {bg_desc} background - got it!

Do you want:
• **Symbol only** - Just the Fuzzball icon  
• **Full logotype** - Symbol + text lockup"""
    
    # Build asset key and get logo
    color = 'blk' if background == 'light' else 'wht'
    
    if logo_type == 'symbol':
        # Icon version
        asset_key = f'icon-{color}-medium'  # Default to medium size
        asset = asset_data['fuzzball_logos'].get(asset_key)
        
        if not asset:
            return f"Sorry, I couldn't find the Fuzzball symbol for {background} backgrounds."
        
        return f"""Here's your Fuzzball symbol:
**Download:** {asset['url']}

Perfect for tight spaces where you need just the recognizable Fuzzball icon."""
    
    else:  # logotype
        # Default to horizontal layout, medium size
        asset_key = f'horizontal-{color}-medium'
        asset = asset_data['fuzzball_logos'].get(asset_key)
        
        if not asset:
            return f"Sorry, I couldn't find the Fuzzball logotype for {background} backgrounds."
        
        return f"""Here's your Fuzzball logotype:
**Download:** {asset['url']}

Full logo with symbol + text lockup - perfect for primary branding."""

async def handle_ciq_request(request: str, background: Optional[str], version_type: Optional[str]) -> str:
    """Handle CIQ logo requests"""
    
    # Try to parse from request
    parsed_background, parsed_ciq_version, _ = parse_user_response(request)
    if parsed_background:
        background = parsed_background
    if parsed_ciq_version:
        version_type = parsed_ciq_version
    
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
    
    # Build asset key and get logo
    if version_type == '2color':
        asset_key = f'2color-{background}'
        reasoning = 'Maximum brand recognition - use when logo is the primary element'
    else:  # 1color
        asset_key = f'1color-{background}'
        reasoning = 'Clean and professional - works in most contexts'
    
    asset = asset_data['logos'].get(asset_key)
    if not asset:
        return f"Sorry, I couldn't find the CIQ {version_type} logo for {background} backgrounds."
    
    return f"""Here's your CIQ logo:
**Download:** {asset['url']}

{reasoning}"""

@mcp.tool()
async def list_all_assets() -> str:
    """List all available CIQ brand assets with descriptions and download links"""
    
    # Load data if not already loaded
    if asset_data is None:
        await asyncio.get_event_loop().run_in_executor(None, load_asset_data)
    
    if asset_data is None:
        return "Sorry, I couldn't load the brand assets data. Please try again later."
    
    result = "# CIQ Brand Assets Library\n\n"
    
    # CIQ Logos
    result += "## CIQ Company Logos\n\n"
    
    for key, asset in asset_data['logos'].items():
        result += f"• **{asset['filename']}** - {asset['description']}\n  {asset['url']}\n\n"
    
    # Fuzzball Logos - show key variants
    result += "## Fuzzball Product Logos\n\n"
    
    # Show just the medium size variants for clarity
    key_fuzzball_assets = [
        'icon-blk-medium', 'icon-wht-medium',
        'horizontal-blk-medium', 'horizontal-wht-medium', 
        'vertical-blk-medium', 'vertical-wht-medium'
    ]
    
    for key in key_fuzzball_assets:
        if key in asset_data['fuzzball_logos']:
            asset = asset_data['fuzzball_logos'][key]
            result += f"• **{asset['filename']}** - {asset['description']}\n  {asset['url']}\n\n"
    
    result += """## Quick Reference

**CIQ Logos:**
- **1-color** - Standard version for most uses
- **2-color** - Hero version for primary branding
- Choose **light** or **dark** background version

**Fuzzball Logos:**  
- **Symbol only** - Just the icon (tight spaces)
- **Full logotype** - Symbol + text (primary branding)
- Choose **light** or **dark** background version

Just tell me what you need: "CIQ 2-color for light background" or "Fuzzball symbol for dark background" """
    
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
    
    return f"""# CIQ Brand Guidelines

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
• Choose based on background: light background = dark logo, dark background = light logo

**Fuzzball Logos:**
• **Symbol only** - Use when space is limited or you need just the recognizable icon
• **Full logotype** - Use for primary branding when you want symbol + text
• Choose based on background: light background = black logo, dark background = white logo

## What NOT to Do
• Don't alter logo colors, fonts, or proportions
• Don't place logos on busy backgrounds without proper contrast  
• Don't ignore minimum size requirements
• Don't use outdated logo versions

Need help choosing? Just describe what you need: "CIQ logo" or "Fuzzball logo" and I'll help you get the right version."""

if __name__ == "__main__":
    # Load asset data on startup
    load_asset_data()
    mcp.run()
