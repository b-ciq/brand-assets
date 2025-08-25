#!/usr/bin/env python3
# Deployment trigger: 1756150512
"""
CIQ Brand Assets MCP Server - Integrated System with Separated RLC Products
Enhanced with confidence scoring, response templates, and clean attribute-based approach
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

class AttributeDetector:
    """Intelligent attribute detection with confidence scoring"""
    
    def __init__(self):
        self.product_patterns = {
            'ciq': ['ciq', 'company', 'brand', 'main'],
            'fuzzball': ['fuzzball', 'fuzz ball', 'workload', 'hpc'],
            'warewulf': ['warewulf', 'warewulf pro', 'warewulf-pro', 'cluster', 'provisioning'],
            'apptainer': ['apptainer', 'container', 'scientific'],
            'ascender': ['ascender', 'ascender pro', 'automation', 'ansible'],
            'bridge': ['bridge', 'centos', 'migration'],
            'rlc': ['rlc', 'rocky linux commercial', 'rocky linux'],
            'rlc-ai': ['rlc-ai', 'rlc ai', 'rocky linux ai', 'rocky linux commercial ai'],
            'rlc-hardened': ['rlc-hardened', 'rlc hardened', 'rocky linux hardened', 'rocky linux commercial hardened'],
            'rlc-lts': ['rlc-lts', 'rlc lts', 'rocky linux lts', 'rocky linux commercial lts']
        }
        
        self.background_patterns = {
            'light': ['light', 'white', 'light background'],
            'dark': ['dark', 'black', 'dark background']
        }
        
        self.layout_patterns = {
            'icon': ['symbol', 'icon', 'favicon', 'app icon'],
            'horizontal': ['horizontal', 'wide', 'header', 'lockup'],
            'vertical': ['vertical', 'tall', 'stacked'],
            '1color': ['1-color', '1 color', 'one color', 'standard'],
            '2color': ['2-color', '2 color', 'two color', 'hero']
        }
        
        self.context_patterns = {
            'wide_format': ['email signature', 'header', 'business card', 'letterhead', 'banner', 'website header'],
            'square_format': ['social media', 'profile picture', 'avatar', 'mobile app', 'app icon'],
            'flexible_format': ['presentation', 'slide', 'document', 'report', 'proposal']
        }

    def detect_attributes(self, request: str) -> Dict[str, Any]:
        """Detect attributes with confidence scores"""
        request_lower = request.lower()
        
        attributes = {
            'product': self._detect_product(request_lower),
            'background': self._detect_background(request_lower), 
            'layout': self._detect_layout(request_lower),
            'context': self._detect_context(request_lower)
        }
        
        # Calculate total confidence score
        total_confidence = sum(attr['confidence'] for attr in attributes.values() if attr)
        attributes['total_confidence'] = total_confidence
        
        return attributes
    
    def _detect_product(self, request: str) -> Optional[Dict]:
        """Detect product with confidence scoring (50 points max)"""
        scores = {}
        for product, patterns in self.product_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in request:
                    # Longer patterns get higher scores + specificity bonus
                    base_score = len(pattern.split()) * 10
                    
                    # Specificity bonuses for RLC variants
                    if product.startswith('rlc-') and pattern in request:
                        base_score += 20  # Bonus for specific RLC variants
                    
                    score += base_score
            if score > 0:
                scores[product] = min(score, 50)
        
        if scores:
            best_product = max(scores, key=scores.get)
            return {
                'value': best_product,
                'confidence': scores[best_product]
            }
        return None
    
    def _detect_background(self, request: str) -> Optional[Dict]:
        """Detect background preference (30 points max)"""
        for bg_type, patterns in self.background_patterns.items():
            for pattern in patterns:
                if pattern in request:
                    return {
                        'value': bg_type,
                        'confidence': 30
                    }
        return None
    
    def _detect_layout(self, request: str) -> Optional[Dict]:
        """Detect layout preference (30 points max)"""
        for layout_type, patterns in self.layout_patterns.items():
            for pattern in patterns:
                if pattern in request:
                    return {
                        'value': layout_type,
                        'confidence': 30
                    }
        return None
    
    def _detect_context(self, request: str) -> Optional[Dict]:
        """Detect context clues (20 points max)"""
        for context_type, patterns in self.context_patterns.items():
            for pattern in patterns:
                if pattern in request:
                    return {
                        'value': context_type,
                        'confidence': 20
                    }
        return None

class AssetMatcher:
    """Enhanced asset matching with attribute-based intelligence"""
    
    def __init__(self, asset_data: Dict):
        self.asset_data = asset_data
        self.detector = AttributeDetector()
        self.product_info = {
            'ciq': {
                'name': 'CIQ',
                'description': 'Company brand',
                'structure_type': 'company',
                'asset_key': 'logos'
            },
            'fuzzball': {
                'name': 'Fuzzball',
                'description': 'HPC/AI workload management platform', 
                'structure_type': 'product',
                'asset_key': 'fuzzball_logos'
            },
            'warewulf': {
                'name': 'Warewulf',
                'description': 'HPC cluster provisioning tool',
                'structure_type': 'product',
                'asset_key': 'warewulf_logos'
            },
            'apptainer': {
                'name': 'Apptainer',
                'description': 'Container platform for HPC/scientific workflows',
                'structure_type': 'product',
                'asset_key': 'apptainer_logos'
            },
            'ascender': {
                'name': 'Ascender',
                'description': 'Infrastructure automation platform',
                'structure_type': 'product',
                'asset_key': 'ascender_pro_logos'
            },
            'bridge': {
                'name': 'Bridge',
                'description': 'CentOS 7 migration solution',
                'structure_type': 'product',
                'asset_key': 'bridge_logos'
            },
            'rlc': {
                'name': 'RLC',
                'description': 'Rocky Linux Commercial (base platform)',
                'structure_type': 'product',
                'asset_key': 'rlc_logos'
            },
            'rlc-ai': {
                'name': 'RLC-AI',
                'description': 'Rocky Linux Commercial AI-focused platform',
                'structure_type': 'product', 
                'asset_key': 'rlc_ai_logos'
            },
            'rlc-hardened': {
                'name': 'RLC-Hardened',
                'description': 'Rocky Linux Commercial security-focused platform',
                'structure_type': 'product',
                'asset_key': 'rlc_hardened_logos'
            },
            'rlc-lts': {
                'name': 'RLC-LTS',
                'description': 'Rocky Linux Commercial long-term support',
                'structure_type': 'product',
                'asset_key': 'rlc_lts_logos'
            }
        }

    def match_assets(self, request: str) -> Dict[str, Any]:
        """Match assets using attribute detection"""
        attributes = self.detector.detect_attributes(request)
        
        if not attributes['product']:
            return self._generate_product_help()
        
        product_id = attributes['product']['value']
        confidence_level = self._assess_confidence_level(attributes['total_confidence'])
        
        # Get product assets
        product_info = self.product_info[product_id]
        product_assets = self.asset_data.get(product_info['asset_key'], {})
        
        if not product_assets:
            return {'error': f'No assets found for {product_info["name"]}'}
        
        # Score and rank assets
        scored_assets = self._score_assets(product_assets, attributes)
        
        return {
            'success': True,
            'product': product_info,
            'attributes': attributes,
            'confidence_level': confidence_level,
            'scored_assets': scored_assets
        }
    
    def _assess_confidence_level(self, total_confidence: int) -> str:
        """Assess confidence level based on total score"""
        if total_confidence >= 100:
            return 'high'
        elif total_confidence >= 50:
            return 'medium'
        else:
            return 'low'
    
    def _score_assets(self, product_assets: Dict, attributes: Dict) -> List[Tuple[int, Dict, str]]:
        """Score assets based on detected attributes"""
        scored = []
        
        for asset_key, asset in product_assets.items():
            score = 0
            reasons = []
            
            # Layout matching (most important)
            if attributes['layout'] and attributes['layout']['value']:
                target_layout = attributes['layout']['value']
                asset_layout = asset.get('layout', '').lower()
                
                if target_layout in asset_layout:
                    score += 100
                    reasons.append(f"exact {target_layout} match")
                elif asset_layout == 'unknown':
                    score += 30
                    reasons.append("fallback option")
            
            # Background matching
            if attributes['background']:
                target_bg = attributes['background']['value']
                asset_bg = asset.get('background', '').lower()
                
                if target_bg == asset_bg:
                    score += 50
                    reasons.append(f"optimized for {target_bg} backgrounds")
                elif asset_bg == 'unknown':
                    score += 15
                    reasons.append("universal background compatibility")
            
            # Format preferences (only PNG files now)
            if asset.get('format') == 'png':
                score += 20
                reasons.append("high-quality PNG format")
            
            # Context matching
            if attributes['context']:
                context = attributes['context']['value']
                asset_use_cases = asset.get('use_cases', [])
                
                context_bonus = self._calculate_context_bonus(context, asset_use_cases)
                if context_bonus > 0:
                    score += context_bonus
                    reasons.append(f"suitable for {context.replace('_', ' ')}")
            
            if score > 0:
                scored.append((score, asset, " + ".join(reasons)))
        
        # Sort by score (highest first)
        return sorted(scored, key=lambda x: x[0], reverse=True)
    
    def _calculate_context_bonus(self, context: str, use_cases: List[str]) -> int:
        """Calculate context bonus points"""
        context_mappings = {
            'wide_format': ['headers', 'business_cards', 'letterhead', 'wide_banners'],
            'square_format': ['social_media_profile', 'mobile_layout', 'avatars'],
            'flexible_format': ['scalable', 'web', 'print', 'general_branding']
        }
        
        relevant_cases = context_mappings.get(context, [])
        for case in relevant_cases:
            if case in use_cases:
                return 30
        return 0
    
    def _generate_product_help(self) -> Dict[str, Any]:
        """Generate help when product is not detected"""
        return {
            'help': True,
            'message': """**CIQ Brand Assets Available:**

**Company Brand:**
• **CIQ** - Main company logo

**Product Brands:**
• **Fuzzball** - HPC/AI workload management platform
• **Warewulf** - HPC cluster provisioning tool  
• **Apptainer** - Container platform for HPC/scientific workflows
• **Ascender** - Infrastructure automation platform
• **Bridge** - CentOS 7 migration solution

**RLC Product Family:**
• **RLC** - Rocky Linux Commercial (base platform)
• **RLC-AI** - Rocky Linux Commercial AI-focused platform
• **RLC-Hardened** - Rocky Linux Commercial security-focused platform
• **RLC-LTS** - Rocky Linux Commercial long-term support

**Examples:**
• "CIQ logo" → Company brand
• "Fuzzball logo" → Product brand with options
• "RLC-AI logo for dark background" → Specific RLC variant
• "Warewulf symbol" → Icon only

Which brand asset do you need?"""
        }

class ResponseFormatter:
    """Template-based response formatting"""
    
    def format_response(self, match_result: Dict[str, Any]) -> str:
        """Format response based on confidence level"""
        if match_result.get('help'):
            return match_result['message']
        
        if match_result.get('error'):
            return f"❌ {match_result['error']}"
        
        confidence_level = match_result['confidence_level']
        
        if confidence_level == 'high':
            return self._format_high_confidence(match_result)
        elif confidence_level == 'medium':
            return self._format_medium_confidence(match_result) 
        else:
            return self._format_low_confidence(match_result)
    
    def _format_high_confidence(self, result: Dict) -> str:
        """High confidence: Direct answer with single asset"""
        best_asset = result['scored_assets'][0]
        score, asset, reasoning = best_asset
        product_info = result['product']
        
        layout_desc = asset.get('layout', 'logo').replace('icon', 'symbol')
        
        return f"""✅ **{product_info['name']} {layout_desc}:**

📎 **Download:** {asset['url']}

💡 **Selection reasoning:** {reasoning}

📋 **Usage guidance:** {asset.get('guidance', f'Professional {product_info["name"]} branding')}"""
    
    def _format_medium_confidence(self, result: Dict) -> str:
        """Medium confidence: Top choice + alternatives"""
        scored_assets = result['scored_assets'][:3]  # Top 3
        product_info = result['product']
        
        response = f"**{product_info['name']} Logo - Top Recommendation:**\n\n"
        
        # Primary choice
        best_score, best_asset, best_reasoning = scored_assets[0]
        layout_desc = best_asset.get('layout', 'logo').replace('icon', 'symbol')
        
        response += f"""✅ **Primary Choice: {layout_desc.title()}**
• **Download:** {best_asset['url']}
• **Why:** {best_reasoning}

"""
        
        # Alternatives
        if len(scored_assets) > 1:
            response += "**Alternative Options:**\n"
            for i, (score, asset, reasoning) in enumerate(scored_assets[1:], 2):
                alt_layout = asset.get('layout', 'logo').replace('icon', 'symbol')
                response += f"• **Option {i}:** {alt_layout} - {asset['url']}\n"
        
        return response
    
    def _format_low_confidence(self, result: Dict) -> str:
        """Low confidence: Quick clarifying question"""
        product_info = result['product']
        attributes = result['attributes']
        
        # Determine what we need to clarify
        if not attributes['background']:
            return f"""🎨 **I found {product_info['name']} assets for you!**

**What background will this logo be placed on?**

• 🌞 **light** → white, light gray, light colors, most websites
• 🌙 **dark** → black, dark gray, dark colors, dark photos

This helps me recommend the right color version for proper contrast."""
        
        elif not attributes['layout'] and product_info['structure_type'] == 'product':
            return f"""✨ **Perfect! For {product_info['name']} logos...**

**Which layout works best for your use case?**

🔸 **horizontal** → Symbol + text side-by-side (headers, business cards, emails)
🔹 **vertical** → Symbol + text stacked (social media, mobile apps)  
⚫ **symbol** → Icon only (tight spaces, favicons)

What's your primary use case?"""
        
        else:
            # Show top options with guidance
            return self._format_medium_confidence(result)

@mcp.tool()
def get_brand_asset(request: str, background: Optional[str] = None) -> str:
    """
    Get CIQ brand assets with intelligent attribute detection and confidence scoring.
    
    Examples:
    - "CIQ logo for light background" 
    - "Fuzzball logo"
    - "RLC-AI logo for dark background"
    - "Warewulf symbol for email signature"
    - "Apptainer vertical logo for presentation"
    """
    
    # Load data if needed
    if asset_data is None:
        if not load_asset_data():
            return "❌ Sorry, couldn't load brand assets data."
    
    # Override background if provided
    if background:
        request = f"{request} for {background} background"
    
    # Initialize components
    matcher = AssetMatcher(asset_data)
    formatter = ResponseFormatter()
    
    # Match assets and format response
    match_result = matcher.match_assets(request)
    return formatter.format_response(match_result)

@mcp.tool()
def list_all_assets() -> str:
    """List all available brand assets with counts"""
    
    if asset_data is None:
        if not load_asset_data():
            return "❌ Sorry, couldn't load brand assets data."
    
    # Count assets by product
    product_counts = {}
    total_assets = 0
    
    for category_key, category_assets in asset_data.items():
        if category_key == 'brand_guidelines':
            continue
            
        asset_count = len(category_assets)
        total_assets += asset_count
        
        # Clean up category names for display
        product_name = category_key.replace('_logos', '').replace('_', ' ')
        if product_name == 'warewulf pro':
            product_name = 'Warewulf Pro'
        elif product_name == 'ascender pro':
            product_name = 'Ascender Pro'
        elif product_name.startswith('rlc'):
            product_name = product_name.upper().replace('RLC ', 'RLC-')
        else:
            product_name = product_name.title()
            
        product_counts[product_name] = asset_count
    
    result = f"# 🎨 CIQ Brand Assets Library\n\n**{total_assets} Total Clean Assets**\n\n"
    
    # Group by category
    result += "## **Company Brand:**\n"
    for product, count in product_counts.items():
        if product in ['CIQ', 'CIQ-Support']:
            result += f"• **{product}** - {count} variants\n"
    
    result += "\n## **Development & HPC Tools:**\n"
    for product, count in product_counts.items():
        if product in ['Warewulf Pro', 'Ascender Pro', 'Apptainer']:
            result += f"• **{product}** - {count} variants\n"
    
    result += "\n## **Infrastructure & Platform:**\n"
    for product, count in product_counts.items():
        if product in ['Bridge', 'Fuzzball']:
            result += f"• **{product}** - {count} variants\n"
    
    result += "\n## **RLC Product Family:**\n"
    for product, count in product_counts.items():
        if product.startswith('RLC'):
            result += f"• **{product}** - {count} variants\n"
    
    result += """\n**Usage:**
• "Fuzzball logo" → Smart defaults
• "RLC-AI logo for dark background" → Specific variant
• "Warewulf symbol" → Icon only

**Behavior:**
• **High confidence** → Direct answer
• **Medium confidence** → Top choice + alternatives  
• **Low confidence** → Quick clarifying question

🧹 **All assets cleaned:** Only largest PNG files, no SVGs or smaller sizes"""
    
    return result

# Load data on startup  
load_asset_data()

# FastMCP Cloud will handle the server startup
if __name__ == "__main__":
    mcp.run()
