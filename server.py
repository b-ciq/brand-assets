#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - Intelligent Logo Selection Logic
Smart defaults with context-aware recommendations using rich metadata
"""

from fastmcp import FastMCP
import json
import requests
from typing import Optional, Dict, Any, List, Tuple
import re

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

class BrandAssetMatcher:
    """Intelligent brand asset matching with context-aware selection"""
    
    def __init__(self, asset_data: Dict):
        self.asset_data = asset_data
        self.product_info = {
            'ciq': {
                'name': 'CIQ',
                'description': 'Company brand',
                'keywords': ['ciq', 'company', 'brand', 'main'],
                'structure_type': 'company',  # 1-color vs 2-color
                'asset_key': 'logos'
            },
            'fuzzball': {
                'name': 'Fuzzball', 
                'description': 'HPC/AI workload management platform',
                'keywords': ['fuzzball', 'fuzz ball', 'workload', 'hpc'],
                'structure_type': 'product',  # symbol vs horizontal vs vertical
                'asset_key': 'fuzzball_logos'
            },
            'warewulf': {
                'name': 'Warewulf',
                'description': 'HPC cluster provisioning tool',
                'keywords': ['warewulf', 'warewulf pro', 'cluster', 'provisioning'],
                'structure_type': 'product',
                'asset_key': 'warewulf-pro_logos'
            },
            'apptainer': {
                'name': 'Apptainer',
                'description': 'Container platform for HPC/scientific workflows',
                'keywords': ['apptainer', 'container', 'scientific'],
                'structure_type': 'product',
                'asset_key': 'apptainer_logos'
            },
            'ascender': {
                'name': 'Ascender',
                'description': 'Infrastructure automation platform',
                'keywords': ['ascender', 'ascender pro', 'automation', 'ansible'],
                'structure_type': 'product',
                'asset_key': 'ascender-pro_logos'
            },
            'bridge': {
                'name': 'Bridge',
                'description': 'CentOS 7 migration solution',
                'keywords': ['bridge', 'centos', 'migration'],
                'structure_type': 'product',
                'asset_key': 'bridge_logos'
            },
            'rlc': {
                'name': 'RLC',
                'description': 'Rocky Linux Commercial (RLC-AI, RLC-Hardened)',
                'keywords': ['rlc', 'rocky linux', 'commercial', 'rlc-ai', 'rlc ai', 'rlc-hardened', 'rlc hardened'],
                'structure_type': 'product',
                'asset_key': 'rlcx_logos'
            }
        }
    
    def identify_product(self, request: str) -> Optional[str]:
        """Identify which product the user wants based on keywords"""
        request_lower = request.lower()
        
        # Score each product based on keyword matches
        scores = {}
        for product_id, info in self.product_info.items():
            score = 0
            for keyword in info['keywords']:
                if keyword in request_lower:
                    # Longer keywords get higher scores (more specific)
                    score += len(keyword.split())
            
            if score > 0:
                scores[product_id] = score
        
        # Return highest scoring product
        if scores:
            return max(scores, key=scores.get)
        return None
    
    def get_context_from_use_case(self, request: str) -> Optional[str]:
        """Extract context from specific use case mentions"""
        request_lower = request.lower()
        
        # Wide format contexts
        wide_contexts = [
            'email signature', 'header', 'business card', 'letterhead', 
            'banner', 'website header', 'document header', 'presentation header'
        ]
        
        # Square/mobile contexts  
        square_contexts = [
            'social media', 'profile picture', 'avatar', 'mobile app', 
            'app icon', 'linkedin', 'twitter', 'instagram', 'favicon'
        ]
        
        # Flexible contexts
        flexible_contexts = [
            'presentation', 'slide', 'document', 'report', 'proposal',
            'marketing material', 'brochure', 'flyer'
        ]
        
        for context_phrase in wide_contexts:
            if context_phrase in request_lower:
                return 'wide_format'
        
        for context_phrase in square_contexts:
            if context_phrase in request_lower:
                return 'square_format'
                
        for context_phrase in flexible_contexts:
            if context_phrase in request_lower:
                return 'flexible_format'
        
        return None
    
    def parse_intent(self, request: str) -> Dict[str, Optional[str]]:
        """Parse user intent from request text"""
        request_lower = request.lower()
        
        intent = {
            'layout_type': None,
            'background': None,
            'size_preference': None,
            'context': None
        }
        
        # Layout type detection
        if any(word in request_lower for word in ['symbol', 'icon', 'favicon', 'app icon']):
            intent['layout_type'] = 'icon'
        elif any(word in request_lower for word in ['horizontal', 'wide', 'header', 'lockup']):
            intent['layout_type'] = 'horizontal'
        elif any(word in request_lower for word in ['vertical', 'tall', 'stacked']):
            intent['layout_type'] = 'vertical'
        elif any(word in request_lower for word in ['1-color', '1 color', 'one color', 'standard']):
            intent['layout_type'] = '1color'
        elif any(word in request_lower for word in ['2-color', '2 color', 'two color', 'hero']):
            intent['layout_type'] = '2color'
        
        # Background detection
        if any(word in request_lower for word in ['light', 'white', 'light background']):
            intent['background'] = 'light'
        elif any(word in request_lower for word in ['dark', 'black', 'dark background']):
            intent['background'] = 'dark'
        
        # Size preference
        if any(word in request_lower for word in ['vector', 'svg', 'scalable']):
            intent['size_preference'] = 'vector'
        elif any(word in request_lower for word in ['large', 'big']):
            intent['size_preference'] = 'large'
        elif any(word in request_lower for word in ['small', 'tiny']):
            intent['size_preference'] = 'small'
        
        # Context clues for layout selection
        intent['context'] = self.get_context_from_use_case(request)
        if not intent['context']:
            if any(word in request_lower for word in ['email', 'signature', 'header', 'business card', 'letterhead']):
                intent['context'] = 'wide_format'
            elif any(word in request_lower for word in ['social media', 'profile', 'mobile', 'app']):
                intent['context'] = 'square_format'
            elif any(word in request_lower for word in ['presentation', 'slide', 'document']):
                intent['context'] = 'flexible_format'
        
        return intent
    
    def get_smart_default_layout(self, product_id: str, context: Optional[str] = None) -> str:
        """Determine smart default layout based on product and context"""
        product_info = self.product_info[product_id]
        
        # CIQ company brand defaults to 1-color
        if product_info['structure_type'] == 'company':
            return '1color'
        
        # Product brands - context-aware defaults
        if context == 'wide_format':
            return 'horizontal'
        elif context == 'square_format':
            return 'vertical'
        else:
            # Default to horizontal for most use cases (better brand recognition)
            return 'horizontal'
    
    def score_asset_match(self, asset: Dict, intent: Dict[str, Optional[str]], 
                         target_layout: str, target_background: Optional[str]) -> Tuple[int, str]:
        """Score how well an asset matches the user's intent with enhanced logic"""
        score = 0
        reasons = []
        
        # Layout match (most important - 100 points for exact match)
        asset_layout = asset.get('layout', '').lower()
        if target_layout == 'icon' and 'icon' in asset_layout:
            score += 100
            reasons.append("exact symbol match")
        elif target_layout == 'horizontal' and 'horizontal' in asset_layout:
            score += 100
            reasons.append("horizontal lockup (symbol + text)")
        elif target_layout == 'vertical' and 'vertical' in asset_layout:
            score += 100
            reasons.append("vertical lockup (stacked)")
        elif target_layout in ['1color', '2color'] and target_layout in asset_layout:
            score += 100
            reasons.append(f"{target_layout} company brand")
        elif asset_layout == 'unknown':
            score += 30  # Fallback for incomplete metadata
            reasons.append("fallback option")
        
        # Background match (50 points for perfect match)
        if target_background:
            asset_background = asset.get('background', '').lower()
            if target_background == asset_background:
                score += 50
                reasons.append(f"optimized for {target_background} backgrounds")
            elif asset_background == 'unknown':
                score += 15  # Better fallback score
                reasons.append("universal background compatibility")
        
        # Size preference (25 points)
        intent_size = intent.get('size_preference')
        if intent_size:
            asset_size = asset.get('size', '').lower()
            if intent_size == asset_size:
                score += 25
                reasons.append(f"{intent_size} format requested")
        
        # Vector format bonus (20 points - always valuable)
        if asset.get('format') == 'svg':
            score += 20
            reasons.append("scalable vector format")
        
        # Use case relevance (30 points for perfect context match)
        context = intent.get('context')
        asset_use_cases = asset.get('use_cases', [])
        if context == 'wide_format':
            if any(uc in asset_use_cases for uc in ['headers', 'business_cards', 'letterhead', 'wide_banners']):
                score += 30
                reasons.append("ideal for wide layouts")
        elif context == 'square_format':
            if any(uc in asset_use_cases for uc in ['social_media_profile', 'mobile_layout', 'avatars']):
                score += 30
                reasons.append("ideal for square/mobile layouts")
        elif context == 'flexible_format':
            if any(uc in asset_use_cases for uc in ['scalable', 'web', 'print']):
                score += 25
                reasons.append("versatile for presentations")
        
        # Color consistency bonus (10 points)
        if target_background == 'light' and asset.get('color') == 'black':
            score += 10
            reasons.append("proper dark-on-light contrast")
        elif target_background == 'dark' and asset.get('color') == 'white':
            score += 10
            reasons.append("proper light-on-dark contrast")
        
        return score, " + ".join(reasons)
    
    def generate_alternatives(self, product_id: str, chosen_asset: Dict) -> str:
        """Generate alternative suggestions"""
        product_info = self.product_info[product_id]
        asset_key = product_info['asset_key']
        product_assets = self.asset_data.get(asset_key, {})
        
        alternatives = []
        chosen_layout = chosen_asset.get('layout', '')
        
        # Find different layout options
        for asset in product_assets.values():
            asset_layout = asset.get('layout', '')
            if asset_layout != chosen_layout and asset_layout != 'unknown':
                alt_name = asset_layout.replace('icon', 'symbol')
                if alt_name not in [alt.split(' ')[0] for alt in alternatives]:
                    alternatives.append(f"{alt_name} version")
        
        if alternatives:
            return f"\n\n**Other options:** {', '.join(alternatives[:2])}"
        return ""
    
    def enhance_guidance(self, asset: Dict, product_info: Dict, context: Optional[str]) -> str:
        """Enhance guidance with context-specific advice"""
        base_guidance = asset.get('guidance', f'Professional {product_info["name"]} branding')
        
        # Add context-specific tips
        if context == 'wide_format':
            base_guidance += " • Ideal for horizontal layouts where you have plenty of width"
        elif context == 'square_format':
            base_guidance += " • Perfect for social media and mobile applications"
        elif asset.get('layout') == 'horizontal':
            base_guidance += " • Maximum brand recognition with both symbol and text"
        elif asset.get('layout') == 'icon':
            base_guidance += " • Use when space is limited or brand is already established"
        
        return base_guidance
    
    def find_best_asset(self, product_id: str, intent: Dict[str, Optional[str]]) -> Optional[Dict]:
        """Find the best matching asset for the user's intent"""
        product_info = self.product_info[product_id]
        asset_key = product_info['asset_key']
        product_assets = self.asset_data.get(asset_key, {})
        
        if not product_assets:
            return None
        
        # Determine target layout
        target_layout = intent['layout_type']
        if not target_layout:
            target_layout = self.get_smart_default_layout(product_id, intent.get('context'))
        
        # Determine target background
        target_background = intent['background']
        if not target_background:
            target_background = 'light'  # Default to light background
        
        # Score all assets
        scored_assets = []
        for asset_key, asset in product_assets.items():
            score, reasons = self.score_asset_match(asset, intent, target_layout, target_background)
            if score > 0:
                scored_assets.append((score, asset, reasons))
        
        # Return best match
        if scored_assets:
            scored_assets.sort(key=lambda x: x[0], reverse=True)
            return {
                'asset': scored_assets[0][1],
                'score': scored_assets[0][0],
                'reasoning': scored_assets[0][2]
            }
        
        return None

def get_available_options(product_id: str, matcher: BrandAssetMatcher) -> str:
    """Generate available options for a product"""
    product_info = matcher.product_info[product_id]
    product_assets = matcher.asset_data.get(product_info['asset_key'], {})
    
    if product_info['structure_type'] == 'company':
        return f"""**{product_info['name']} Company Brand:**
*{product_info['description']}*

**Versions Available:**
• **1-color** - Standard version for most applications
• **2-color** - Hero version when logo is primary visual element

**Backgrounds:**
• **Light background** (dark logo)
• **Dark background** (light logo)

**Examples:** "CIQ 1-color logo for light background", "CIQ 2-color logo for dark background" """
    
    else:
        # Analyze available layouts
        layouts = set()
        backgrounds = set()
        for asset in product_assets.values():
            layout = asset.get('layout', '').lower()
            if layout and layout != 'unknown':
                layouts.add(layout)
            bg = asset.get('background', '').lower()
            if bg and bg != 'unknown':
                backgrounds.add(bg)
        
        layout_descriptions = {
            'icon': '**Symbol only** - Just the icon (tight spaces, favicons)',
            'horizontal': '**Horizontal lockup** - Symbol + text side-by-side (most common)',
            'vertical': '**Vertical lockup** - Symbol + text stacked (tall spaces)'
        }
        
        options_text = f"""**{product_info['name']} Logo:**
*{product_info['description']}*

**Layout Options:**"""
        
        for layout in ['horizontal', 'vertical', 'icon']:
            if layout in layouts:
                options_text += f"\n• {layout_descriptions[layout]}"
        
        options_text += "\n\n**Backgrounds:**"
        if 'light' in backgrounds:
            options_text += "\n• **Light background** (black logo)"
        if 'dark' in backgrounds:
            options_text += "\n• **Dark background** (white logo)"
        
        options_text += f'\n\n**Examples:** "{product_info["name"]} logo", "{product_info["name"]} horizontal logo for dark background", "{product_info["name"]} symbol for email signature"'
        
        return options_text

@mcp.tool()
def get_brand_asset(request: str, background: Optional[str] = None) -> str:
    """
    Get CIQ brand assets with intelligent recommendations.
    
    Examples:
    - "CIQ logo for light background"
    - "Fuzzball logo" (defaults to horizontal lockup)
    - "Warewulf symbol for email signature" 
    - "Apptainer vertical logo for presentation"
    - "Bridge logo for dark background"
    - "RLC logo for business card"
    """
    
    # Load data if needed
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, couldn't load brand assets data."
    
    # Initialize matcher
    matcher = BrandAssetMatcher(asset_data)
    
    # Identify product
    product_id = matcher.identify_product(request)
    
    if not product_id:
        # Generate help with all available products
        help_text = """**CIQ Brand Assets Available:**

**Company Brand:**
• **CIQ** - Main company logo

**Product Brands:**
• **Fuzzball** - HPC/AI workload management platform
• **Warewulf** - HPC cluster provisioning tool  
• **Apptainer** - Container platform for HPC/scientific workflows
• **Ascender** - Infrastructure automation platform
• **Bridge** - CentOS 7 migration solution
• **RLC** - Rocky Linux Commercial (AI, Hardened variants)

**Quick Examples:**
• "CIQ logo" → Company brand
• "Fuzzball logo" → Horizontal lockup (default)
• "Warewulf symbol" → Icon only
• "Apptainer logo for dark background" → White logo

Which brand asset do you need?"""
        return help_text
    
    # Parse user intent
    intent = matcher.parse_intent(request)
    if background:
        intent['background'] = background
    
    # Find best matching asset
    result = matcher.find_best_asset(product_id, intent)
    
    if not result:
        # Fallback - show available options
        return get_available_options(product_id, matcher)
    
    asset = result['asset']
    reasoning = result['reasoning']
    product_info = matcher.product_info[product_id]
    
    # Generate response with intelligent context
    layout_desc = asset.get('layout', 'logo').replace('icon', 'symbol')
    enhanced_guidance = matcher.enhance_guidance(asset, product_info, intent.get('context'))
    alternatives = matcher.generate_alternatives(product_id, asset)
    
    response = f"""**{product_info['name']} {layout_desc}:**
**Download:** {asset['url']}

**Selection reasoning:** {reasoning}

**Usage guidance:** {enhanced_guidance}{alternatives}"""
    
    # Add format and size info if relevant
    format_info = asset.get('format', '').upper()
    size_info = asset.get('size', '')
    if format_info or size_info:
        response += f"\n**Format:** {format_info}"
        if size_info and size_info != 'unknown':
            response += f" ({size_info})"
    
    return response

@mcp.tool()
def validate_asset_selection(request: str, expected_product: Optional[str] = None, 
                           expected_layout: Optional[str] = None) -> str:
    """
    Debug tool for validating asset selection logic.
    Useful for testing and monitoring the system.
    
    Examples:
    - validate_asset_selection("Fuzzball logo", expected_product="fuzzball", expected_layout="horizontal")
    """
    
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, couldn't load brand assets data."
    
    matcher = BrandAssetMatcher(asset_data)
    
    # Run the selection logic
    product_id = matcher.identify_product(request)
    intent = matcher.parse_intent(request)
    
    target_layout = intent['layout_type']
    if not target_layout:
        target_layout = matcher.get_smart_default_layout(product_id, intent.get('context'))
    
    target_background = intent['background'] or 'light'
    
    # Generate debug report
    debug_info = f"""**🔍 Asset Selection Debug Report**

**Input:** "{request}"

**Detection Results:**
• **Product identified:** {product_id or 'None'}
• **Target layout:** {target_layout}
• **Target background:** {target_background}
• **Context detected:** {intent.get('context') or 'None'}

**Parsed Intent:**
• **Explicit layout:** {intent.get('layout_type') or 'None (using smart default)'}
• **Explicit background:** {intent.get('background') or 'None (defaulting to light)'}
• **Size preference:** {intent.get('size_preference') or 'None'}

**Smart Logic Applied:**
• **Default reasoning:** {"Used context-aware default" if not intent.get('layout_type') else "User specified explicitly"}"""
    
    # Validation against expected values
    if expected_product or expected_layout:
        debug_info += f"\n\n**Validation:**"
        if expected_product:
            product_match = product_id == expected_product
            debug_info += f"\n• **Product:** {'✅ Correct' if product_match else '❌ Expected ' + expected_product}"
        if expected_layout:
            layout_match = target_layout == expected_layout  
            debug_info += f"\n• **Layout:** {'✅ Correct' if layout_match else '❌ Expected ' + expected_layout}"
    
    # Show what asset would be selected
    if product_id:
        result = matcher.find_best_asset(product_id, intent)
        if result:
            debug_info += f"\n\n**Selected Asset:**\n• **Score:** {result['score']}\n• **Asset:** {result['asset'].get('filename', 'Unknown')}\n• **Reasoning:** {result['reasoning']}"
    
    return debug_info

@mcp.tool()  
def list_all_assets() -> str:
    """List all available CIQ brand assets with intelligent descriptions"""
    
    if asset_data is None:
        if not load_asset_data():
            return "Sorry, couldn't load brand assets data."
    
    matcher = BrandAssetMatcher(asset_data)
    
    result = """# 🎨 CIQ Brand Assets Library

## **Smart Logo Selection**
Just ask for what you need - the system will intelligently choose the best format:

**Simple Requests:**
• **"CIQ logo"** → Standard 1-color company logo
• **"Fuzzball logo"** → Horizontal lockup (symbol + text)
• **"Warewulf logo for email"** → Horizontal format for wide space
• **"Apptainer symbol"** → Icon only for tight spaces

**Specific Requests:**
• **"CIQ 2-color logo for dark background"** → Hero company brand
• **"Fuzzball vertical logo for social media"** → Stacked layout
• **"Warewulf logo for presentation"** → Vector format when available

---

## **🏢 Company Brand**
**CIQ** - Main company brand (unique structure)
• Structure: 1-color (standard) vs 2-color (hero)
• Use: Company-wide branding, official communications

---

## **🚀 Product Brands**
Each product has: **Symbol** (icon only) + **Horizontal** (side-by-side) + **Vertical** (stacked)

"""
    
    # List products with descriptions
    for product_id, info in matcher.product_info.items():
        if product_id != 'ciq':
            # Check if assets actually exist
            assets = matcher.asset_data.get(info['asset_key'], {})
            if assets:
                result += f"**{info['name']}** - {info['description']}\n"
    
    result += """
---

## **💡 Pro Tips**
• **Default behavior:** Product logos default to horizontal lockup (best brand recognition)
• **Explicit overrides:** Say "symbol" for icon-only, "vertical" for stacked layout
• **Background intelligence:** System detects light/dark preferences from context
• **Vector preference:** SVG format provided when available for scalability

**Need help?** Just describe what you're creating: "logo for business card", "icon for mobile app", "presentation header", etc."""
    
    return result

# Load data on startup  
load_asset_data()

# FastMCP Cloud will handle the server startup
if __name__ == "__main__":
    mcp.run()