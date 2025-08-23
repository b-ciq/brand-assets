#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server (FastMCP Version)
Intelligent brand asset delivery with smart logo recommendations
"""

from mcp.server.fastmcp import FastMCP
import json
import requests
from typing import Optional

# Asset metadata URL
METADATA_URL = 'https://raw.githubusercontent.com/b-ciq/brand-assets/main/metadata/asset-inventory.json'

# Initialize FastMCP
mcp = FastMCP("CIQ Brand Assets")

# Load asset data
asset_data = None

def load_asset_data():
    """Load asset metadata from GitHub"""
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
    context = design_context.lower()
    
    # Main element = always use 2-color for maximum brand recognition
    if element_type == 'main':
        return {
            'key': f'2color-{background}',
            'reasoning': 'Two-color version provides maximum brand recognition for main design elements'
        }
    
    # Supporting element logic
    if element_type == 'supporting':
        # Check for colorful/busy design indicators
        colorful_keywords = ['colorful', 'busy', 'marketing', 'promotional', 'lots of color', 'vibrant']
        is_colorful_design = any(keyword in context for keyword in colorful_keywords)
        
        if is_colorful_design:
            return {
                'key': f'1color-{background}',
                'reasoning': "Neutral version won't compete with your colorful design elements"
            }
        
        # Check for minimal/neutral design indicators
        minimal_keywords = ['minimal', 'clean', 'simple', 'black and white', 'neutral', 'advertising', 'ad']
        is_minimal_design = any(keyword in context for keyword in minimal_keywords)
        
        if is_minimal_design and ('ad' in context or 'advertising' in context):
            return {
                'key': f'green-{background}',
                'reasoning': 'Green version helps your logo jump out in minimal advertising designs'
            }
        
        # Default to neutral for supporting elements (when in doubt)
        return {
            'key': f'1color-{background}',
            'reasoning': "Neutral version is professional and won't distract from your main content"
        }
    
    # Fallback
    return {
        'key': f'1color-{background}',
        'reasoning': 'When in doubt, neutral is the safest choice'
    }

@mcp.tool()
def get_brand_asset(
    request: str,
    background: Optional[str] = None,
    element_type: Optional[str] = None,
    design_context: Optional[str] = None
) -> str:
    """
    Get CIQ brand assets with intelligent recommendations based on design context
    
    Args:
        request: What kind of logo or brand asset do you need? (e.g., "I need a logo for an email signature")
        background: What background will this logo be placed on? ('light' or 'dark')
        element_type: Is this logo the main element/hero of your design, or a supporting element? ('main' or 'supporting')
        design_context: What type of design is this for? (e.g., "colorful marketing flyer", "minimal black and white ad")
    """
    
    # Load data if not already loaded
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, I couldn't load the brand assets data. Please try again later."
    
    # If we don't have enough info, ask clarifying questions
    if not background:
        return """I'd love to help you find the perfect CIQ logo! 

What background will this logo be placed on?
• **Light background** (white, light gray, light colors)
• **Dark background** (black, dark gray, dark colors, dark photos)

This helps me recommend the right color version for proper contrast."""
    
    if not element_type:
        return f"""Great! For {background} backgrounds, I need to understand the logo's role:

🌟 **Main element** - Logo is the hero/star of your design
   • Homepage headers, business cards, presentation title slides
   • Main branding where the logo IS the focus
   
🏷️ **Supporting element** - Logo is secondary/background element  
   • Footers, watermarks, corner branding
   • Small elements that shouldn't compete with main content

Which describes your use case better?"""
    
    # Apply smart decision logic
    recommendation = get_smart_recommendation(background, element_type, design_context or "")
    
    asset = asset_data['logos'].get(recommendation['key'])
    if not asset:
        return "Sorry, I couldn't find the appropriate asset. Please try again or contact the design team."
    
    result = f"""Perfect! Here's your CIQ logo:

🎨 **{asset['description']}**

📎 **Download:** {asset['url']}

📋 **Usage Guidelines:**
• {asset['guidance']}
• Keep clear space equal to 1/4 the height of the 'Q' around the logo
• Minimum size: 70px height for digital applications
"""
    
    if recommendation.get('reasoning'):
        result += f"\n💡 **Why this recommendation:** {recommendation['reasoning']}"
    
    result += "\n\nNeed a different variation? Just ask!"
    
    return result

@mcp.tool()
def list_all_assets() -> str:
    """List all available CIQ brand assets with descriptions"""
    
    # Load data if not already loaded
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, I couldn't load the brand assets data. Please try again later."
    
    asset_list = []
    for key, asset in asset_data['logos'].items():
        asset_list.append(f"• **{asset['filename']}** - {asset['description']}\n  📎 {asset['url']}")
    
    assets_text = "\n\n".join(asset_list)
    
    return f"""# CIQ Brand Assets Available

{assets_text}

## 💡 Smart Recommendations Available
Instead of choosing manually, just tell me what you need! For example:
• "I need a logo for an email signature"
• "Logo for a PowerPoint footer" 
• "Small logo for a magazine ad"
• "Hero logo for our homepage"

I'll ask smart questions and recommend the perfect logo for your specific use case!"""

if __name__ == "__main__":
    # Load asset data on startup
    load_asset_data()
    mcp.run()
