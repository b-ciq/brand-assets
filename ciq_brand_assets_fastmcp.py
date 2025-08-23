#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server
Intelligent brand asset delivery with smart logo recommendations
"""

from mcp.server.fastmcp import FastMCP
import json
import requests  # Changed from aiohttp to requests for better GitHub compatibility
from typing import Optional

# Asset metadata URL
METADATA_URL = 'https://raw.githubusercontent.com/b-ciq/brand-assets/main/metadata/asset-inventory.json'

# Initialize FastMCP server
mcp = FastMCP("CIQ Brand Assets")

# Global asset data cache
asset_data = None

def load_asset_data():
    """Load asset metadata from GitHub using requests (more compatible than aiohttp)"""
    global asset_data
    try:
        response = requests.get(METADATA_URL)
        response.raise_for_status()
        asset_data = response.json()
        return True
    except Exception as e:
        print(f"Failed to load asset data: {e}")
        return False

def get_smart_recommendation(background: str, element_type: str, design_context: str = "") -> dict:
    """Apply intelligent decision logic for logo selection"""
    context = design_context.lower() if design_context else ""
    
    # Main element = always use 2-color for maximum brand recognition
    if element_type == 'main':
        return {
            'key': f'2color-{background}',
            'reasoning': '🌟 Two-color version provides maximum brand recognition for main design elements'
        }
    
    # Supporting element logic
    if element_type == 'supporting':
        # Check for colorful/busy design indicators
        colorful_keywords = ['colorful', 'busy', 'marketing', 'promotional', 'lots of color', 'vibrant', 'bright']
        is_colorful_design = any(keyword in context for keyword in colorful_keywords)
        
        if is_colorful_design:
            return {
                'key': f'1color-{background}',
                'reasoning': "🎨 Neutral version won't compete with your colorful design elements"
            }
        
        # Check for minimal/neutral design indicators + advertising context
        minimal_keywords = ['minimal', 'clean', 'simple', 'black and white', 'neutral', 'monochrome']
        advertising_keywords = ['ad', 'advertisement', 'advertising', 'promotion']
        
        is_minimal_design = any(keyword in context for keyword in minimal_keywords)
        is_advertising = any(keyword in context for keyword in advertising_keywords)
        
        if is_minimal_design and is_advertising:
            return {
                'key': f'green-{background}',
                'reasoning': '🟢 Green version helps your logo jump out in minimal advertising designs'
            }
        
        # Default to neutral for supporting elements (when in doubt)
        return {
            'key': f'1color-{background}',
            'reasoning': "⚪ Neutral version is professional and won't distract from your main content"
        }
    
    # Fallback
    return {
        'key': f'1color-{background}',
        'reasoning': '🔒 When in doubt, neutral is the safest choice'
    }

@mcp.tool()
def get_brand_asset(
    request: str,
    background: Optional[str] = None,
    element_type: Optional[str] = None,
    design_context: Optional[str] = None
) -> str:
    """
    Get CIQ brand assets with intelligent recommendations based on design context.
    
    Just tell me what you need in natural language, like:
    - "I need a logo for an email signature"
    - "Logo for a PowerPoint footer" 
    - "Small logo for a magazine ad"
    - "Hero logo for our homepage"
    
    Args:
        request: What kind of logo or brand asset do you need?
        background: What background will this logo be placed on? ('light' or 'dark')
        element_type: Is this logo the main element/hero of your design, or a supporting element? ('main' or 'supporting')
        design_context: What type of design is this for? (e.g., "colorful marketing flyer", "minimal black and white ad")
    """
    
    # Load data if not already loaded
    if asset_data is None:
        if not load_asset_data():
            return "🚨 Sorry, I couldn't load the brand assets data. Please try again later."
    
    # If we don't have enough info, ask clarifying questions
    if not background:
        return f"""🎨 **I'd love to help you find the perfect CIQ logo!**

For your request: *"{request}"*

**What background will this logo be placed on?**

• 🌞 **light** → white, light gray, light colors, most websites
• 🌙 **dark** → black, dark gray, dark colors, dark photos

This helps me recommend the right color version for proper contrast."""
    
    if not element_type:
        return f"""✨ **Perfect! For {background} backgrounds...**

I need to understand the logo's role in your design:

🌟 **main** → Logo is the hero/star of your design
   • Homepage headers, business cards, presentation title slides
   • Main branding where the logo IS the focus
   
🏷️ **supporting** → Logo is secondary/background element  
   • Footers, watermarks, corner branding, signatures
   • Small elements that shouldn't compete with main content

Which describes your use case: *"{request}"* better?"""
    
    # Apply smart decision logic
    recommendation = get_smart_recommendation(background, element_type, design_context or "")
    
    asset = asset_data['logos'].get(recommendation['key'])
    if not asset:
        return "🚨 Sorry, I couldn't find the appropriate asset. Please try again or contact the design team."
    
    result = f"""✅ **Perfect! Here's your CIQ logo:**

## 🎨 {asset['description']}

📎 **Download:** {asset['url']}

## 📋 Brand Guidelines
• {asset['guidance']}
• **Clear space:** Keep space equal to 1/4 the height of the 'Q' around the logo
• **Minimum size:** 70px height for digital applications

"""
    
    if recommendation.get('reasoning'):
        result += f"💡 **Why this recommendation:** {recommendation['reasoning']}\n\n"
    
    result += "🔄 **Need a different variation?** Just ask with more context!"
    
    return result

@mcp.tool()
def list_all_assets() -> str:
    """List all available CIQ brand assets with descriptions and download links"""
    
    # Load data if not already loaded
    if asset_data is None:
        if not load_asset_data():
            return "🚨 Sorry, I couldn't load the brand assets data. Please try again later."
    
    result = "# 🎨 CIQ Brand Assets Library\n\n"
    
    # Group by background type for better organization
    light_assets = []
    dark_assets = []
    
    for key, asset in asset_data['logos'].items():
        asset_info = f"• **{asset['filename']}** - {asset['description']}\n  📎 {asset['url']}"
        
        if 'light' in key:
            light_assets.append(asset_info)
        else:
            dark_assets.append(asset_info)
    
    result += "## 🌞 Light Background Versions\n\n"
    result += "\n\n".join(light_assets)
    
    result += "\n\n## 🌙 Dark Background Versions\n\n"
    result += "\n\n".join(dark_assets)
    
    result += f"""

## 💡 Smart Recommendations Available

Instead of choosing manually, just tell me what you need! For example:

• *"I need a logo for an email signature"*
• *"Logo for a PowerPoint footer"* 
• *"Small logo for a magazine ad"*
• *"Hero logo for our homepage"*
• *"Watermark for a colorful brochure"*

I'll ask smart questions and recommend the perfect logo for your specific use case!

## 🎯 Quick Decision Guide

**🌟 Main elements** (logo is the star) → Always **2-color** for maximum brand recognition  
**🏷️ Supporting elements** → **1-color neutral** (safe default) or **green** (minimal ads)  
**🎨 Colorful designs** → **1-color neutral** (won't compete)  
**🔍 Minimal + advertising** → **Green** (helps logo pop)"""
    
    return result

@mcp.tool()
def brand_guidelines() -> str:
    """Get CIQ brand guidelines and usage rules"""
    
    # Load data if not already loaded
    if asset_data is None:
        if not load_asset_data():
            return "🚨 Sorry, I couldn't load the brand assets data. Please try again later."
    
    guidelines = asset_data.get('brand_guidelines', {})
    
    return f"""# 📐 CIQ Brand Guidelines

## 🎨 Logo Usage

**Clear Space Rules:**
• Maintain clear space equal to **{guidelines.get('clear_space', '1/4 the height of the Q')}**
• Never place text, images, or other elements within this protected area

**Size Requirements:**
• **Minimum digital size:** {guidelines.get('minimum_size', '70px height')}
• Never scale smaller than minimum requirements
• Maintain aspect ratio - never stretch or compress

## 🌈 Brand Colors

**Primary Green:** `{guidelines.get('primary_green', '#229529')}` (PMS 347)

**Neutral Colors:**
• Light backgrounds: {guidelines.get('neutral_colors', {}).get('light_background', 'Dark grey')}
• Dark backgrounds: {guidelines.get('neutral_colors', {}).get('dark_background', 'Light grey')}

## 🎯 Smart Usage Logic

{asset_data.get('decision_logic', {}).get('main_element', {}).get('description', 'Main elements')}:
• Examples: {', '.join(asset_data.get('decision_logic', {}).get('main_element', {}).get('examples', []))}
• **Recommended:** {asset_data.get('decision_logic', {}).get('main_element', {}).get('recommended', '2-color version')}

{asset_data.get('decision_logic', {}).get('supporting_element', {}).get('description', 'Supporting elements')}:
• Examples: {', '.join(asset_data.get('decision_logic', {}).get('supporting_element', {}).get('examples', []))}
• **Default:** {asset_data.get('decision_logic', {}).get('supporting_element', {}).get('default', '1-color neutral')}
• **Alternative:** {asset_data.get('decision_logic', {}).get('supporting_element', {}).get('alternative', 'Green for minimal designs')}

## ❌ What NOT to Do
• Don't alter the logo colors, fonts, or proportions
• Don't place logo on busy backgrounds without proper contrast
• Don't use outdated logo versions
• Don't ignore minimum size requirements

Need help choosing the right logo? Just describe your project and I'll recommend the perfect version!"""

if __name__ == "__main__":
    # Load asset data on startup
    load_asset_data()
    mcp.run()
