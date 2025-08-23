#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server (FastMCP 2.0)
Intelligent brand asset delivery with smart logo recommendations
"""

from fastmcp import FastMCP
import json
import httpx
from typing import Optional

# Asset metadata URL
METADATA_URL = 'https://raw.githubusercontent.com/b-ciq/brand-assets/main/metadata/asset-inventory.json'

# Initialize FastMCP 2.0 server with dependencies
mcp = FastMCP(
    "CIQ Brand Assets", 
    dependencies=["httpx"]
)

# Global asset data cache
asset_data = None

async def load_asset_data():
    """Load asset metadata from GitHub using async httpx"""
    global asset_data
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(METADATA_URL)
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
        
        # Check for minimal/neutral design indicators + advertising
        minimal_keywords = ['minimal', 'clean', 'simple', 'black and white', 'neutral', 'advertising', 'ad']
        is_minimal_design = any(keyword in context for keyword in minimal_keywords)
        is_advertising = any(ad_keyword in context for ad_keyword in ['ad', 'advertising', 'advertisement'])
        
        if is_minimal_design and is_advertising:
            return {
                'key': f'green-{background}',
                'reasoning': '💚 Green version helps your logo jump out in minimal advertising designs'
            }
        
        # Default to neutral for supporting elements (when in doubt)
        return {
            'key': f'1color-{background}',
            'reasoning': "🛡️ Neutral version is professional and won't distract from your main content"
        }
    
    # Fallback
    return {
        'key': f'1color-{background}',
        'reasoning': '🤔 When in doubt, neutral is the safest choice'
    }

@mcp.tool()
async def get_brand_asset(
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
        if not await load_asset_data():
            return "❌ Sorry, I couldn't load the brand assets data. Please try again later."
    
    # If we don't have enough info, ask clarifying questions
    if not background:
        return """👋 I'd love to help you find the perfect CIQ logo! 

**What background will this logo be placed on?**
• **Light background** → white, light gray, light colors, most websites
• **Dark background** → black, dark gray, dark colors, dark photos

This helps me recommend the right color version for proper contrast."""
    
    # Validate background parameter
    if background.lower() not in ['light', 'dark']:
        return """🎨 Please specify the background type:
• **light** - for white, light gray, or light colored backgrounds  
• **dark** - for black, dark gray, or dark colored backgrounds"""
    
    background = background.lower()
    
    if not element_type:
        return f"""**Great! For {background} backgrounds, I need to understand the logo's role:**

🌟 **main** - Logo is the hero/star of your design
   • Homepage headers, business cards, presentation title slides
   • Main branding where the logo IS the focus
   
🏷️ **supporting** - Logo is secondary/background element  
   • Footers, watermarks, corner branding
   • Small elements that shouldn't compete with main content

Which describes your use case better? (Type 'main' or 'supporting')"""
    
    # Validate element_type parameter
    if element_type.lower() not in ['main', 'supporting']:
        return """🎯 Please specify the element type:
• **main** - logo is the hero/star of the design
• **supporting** - logo is a secondary/background element"""
    
    element_type = element_type.lower()
    
    # Apply smart decision logic
    recommendation = get_smart_recommendation(background, element_type, design_context or "")
    
    asset = asset_data['logos'].get(recommendation['key'])
    if not asset:
        return "❌ Sorry, I couldn't find the appropriate asset. Please try again or contact the design team."
    
    result = f"""✅ **Perfect! Here's your CIQ logo:**

🎨 **{asset['description']}**

📎 **Download:** {asset['url']}

📋 **Usage Guidelines:**
• {asset['guidance']}
• Keep clear space equal to 1/4 the height of the 'Q' around the logo
• Minimum size: 70px height for digital applications

"""
    
    if recommendation.get('reasoning'):
        result += f"💡 **Why this recommendation:** {recommendation['reasoning']}\n\n"
    
    result += "🔄 **Need a different variation?** Just ask with different parameters!"
    
    return result

@mcp.tool()
async def list_all_assets() -> str:
    """List all available CIQ brand assets with descriptions and direct download links"""
    
    # Load data if not already loaded
    if asset_data is None:
        if not await load_asset_data():
            return "❌ Sorry, I couldn't load the brand assets data. Please try again later."
    
    result = "# 🎨 CIQ Brand Assets Available\n\n"
    
    # Group by background type for better organization
    light_assets = []
    dark_assets = []
    
    for key, asset in asset_data['logos'].items():
        asset_info = f"• **{asset['filename']}** - {asset['description']}\n  📎 {asset['url']}"
        
        if 'light' in key:
            light_assets.append(asset_info)
        else:
            dark_assets.append(asset_info)
    
    result += "## 🌞 Light Backgrounds\n"
    result += "\n".join(light_assets)
    result += "\n\n## 🌙 Dark Backgrounds\n"
    result += "\n".join(dark_assets)
    
    result += """\n\n## 🤖 Smart Recommendations Available
Instead of choosing manually, just tell me what you need! For example:
• "I need a logo for an email signature"
• "Logo for a PowerPoint footer" 
• "Small logo for a magazine ad"
• "Hero logo for our homepage"

I'll ask smart questions and recommend the perfect logo for your specific use case!"""
    
    return result

@mcp.tool()
async def get_brand_guidelines() -> str:
    """Get CIQ brand guidelines and usage specifications"""
    
    # Load data if not already loaded
    if asset_data is None:
        if not await load_asset_data():
            return "❌ Sorry, I couldn't load the brand assets data. Please try again later."
    
    guidelines = asset_data.get('brand_guidelines', {})
    logic = asset_data.get('decision_logic', {})
    
    result = """# 📏 CIQ Brand Guidelines

## 🎨 Logo Usage Standards
"""
    
    result += f"• **Clear Space:** {guidelines.get('clear_space', 'Not specified')}\n"
    result += f"• **Minimum Size:** {guidelines.get('minimum_size', 'Not specified')}\n"
    result += f"• **Primary Green:** {guidelines.get('primary_green', '#229529')}\n\n"
    
    result += """## 🎯 When to Use Each Logo Type

### 🌟 Main Elements (Hero/Star of Design)
"""
    main_logic = logic.get('main_element', {})
    result += f"**Use:** {main_logic.get('recommended', 'Two-color version')}\n"
    result += f"**Examples:** {', '.join(main_logic.get('examples', []))}\n"
    result += f"**Why:** {main_logic.get('description', '')}\n\n"
    
    result += """### 🏷️ Supporting Elements (Secondary/Background)
"""
    supporting_logic = logic.get('supporting_element', {})
    result += f"**Default:** {supporting_logic.get('default', 'Neutral version')}\n"
    result += f"**Alternative:** {supporting_logic.get('alternative', 'Green version for minimal designs')}\n"
    result += f"**Examples:** {', '.join(supporting_logic.get('examples', []))}\n"
    result += f"**Why:** {supporting_logic.get('description', '')}\n\n"
    
    result += """## 🤖 Smart Recommendations
I can automatically recommend the perfect logo based on:
• Background color (light/dark)
• Element importance (main/supporting) 
• Design context (colorful, minimal, advertising, etc.)

Just use the `get_brand_asset` tool and describe what you need!"""
    
    return result

# Add a resource for quick access to the raw metadata
@mcp.resource("ciq://metadata")
async def get_metadata() -> str:
    """Access the raw CIQ brand assets metadata"""
    if asset_data is None:
        if not await load_asset_data():
            return "Failed to load asset data"
    
    return json.dumps(asset_data, indent=2)

if __name__ == "__main__":
    # Load asset data on startup
    import asyncio
    asyncio.run(load_asset_data())
    mcp.run()
