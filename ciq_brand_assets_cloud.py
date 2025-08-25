#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - FastMCP Cloud Version
ENHANCED: Background compatibility filter + CIQ-specific logic
"""

from fastmcp import FastMCP
import json
import requests
from typing import Optional, Dict, Any, List, Tuple

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
    """Enhanced attribute detection with CIQ color_type support"""
    
    def __init__(self):
        self.product_patterns = {
            'ciq': ['ciq', 'company', 'brand', 'main'],
            'fuzzball': ['fuzzball', 'fuzz ball', 'workload', 'hpc'],
            'warewulf': ['warewulf', 'warewulf pro', 'cluster', 'provisioning'],
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
            'horizontal': ['horizontal', 'wide', 'header', 'lockup', 'full logo', 'wordmark'],
            'vertical': ['vertical', 'tall', 'stacked'],
            '1color': ['1-color', '1 color', 'one color', 'standard'],
            '2color': ['2-color', '2 color', 'two color', 'hero']
        }
        
        # CIQ-specific color type patterns
        self.ciq_color_type_patterns = {
            '1color_neutral': ['standard', 'neutral', 'basic', '1-color', '1 color'],
            '1color_green': ['green', 'punch', 'advertising', 'social media', 'exciting'],
            '2color': ['hero', '2-color', '2 color', 'primary visual', 'presentations']
        }

    def detect_attributes(self, request: str) -> Dict[str, Any]:
        """Detect attributes with enhanced confidence scores"""
        request_lower = request.lower()
        
        attributes = {
            'product': self._detect_product(request_lower),
            'background': self._detect_background(request_lower), 
            'layout': self._detect_layout(request_lower),
            'ciq_color_type': self._detect_ciq_color_type(request_lower)
        }
        
        # Enhanced confidence calculation
        total_confidence = 0
        if attributes['product']:
            total_confidence += attributes['product']['confidence']
        if attributes['background']:
            total_confidence += 60  # Background detection worth 60 points
        if attributes['layout']:
            total_confidence += attributes['layout']['confidence']
        if attributes['ciq_color_type']:
            total_confidence += attributes['ciq_color_type']['confidence']
        
        attributes['total_confidence'] = total_confidence
        
        return attributes
    
    def _detect_product(self, request: str) -> Optional[Dict]:
        """Detect product with confidence scoring (50 points max)"""
        scores = {}
        for product, patterns in self.product_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in request:
                    base_score = len(pattern.split()) * 10
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
        """Detect background preference (60 points for higher confidence)"""
        for bg_type, patterns in self.background_patterns.items():
            for pattern in patterns:
                if pattern in request:
                    return {
                        'value': bg_type,
                        'confidence': 60
                    }
        return None
    
    def _detect_layout(self, request: str) -> Optional[Dict]:
        """Detect layout preference (30 points max) - for products only"""
        for layout_type, patterns in self.layout_patterns.items():
            for pattern in patterns:
                if pattern in request:
                    return {
                        'value': layout_type,
                        'confidence': 30
                    }
        return None
    
    def _detect_ciq_color_type(self, request: str) -> Optional[Dict]:
        """Detect CIQ color type preference (40 points max)"""
        for color_type, patterns in self.ciq_color_type_patterns.items():
            for pattern in patterns:
                if pattern in request:
                    return {
                        'value': color_type,
                        'confidence': 40
                    }
        return None

class AssetMatcher:
    """Enhanced asset matching with background filtering + CIQ-specific logic"""
    
    def __init__(self, asset_data: Dict):
        self.asset_data = asset_data
        self.detector = AttributeDetector()
        self.product_info = {
            'ciq': {'name': 'CIQ', 'description': 'Company brand', 'structure_type': 'company', 'asset_key': 'logos'},
            'fuzzball': {'name': 'Fuzzball', 'description': 'HPC/AI workload management platform', 'structure_type': 'product', 'asset_key': 'fuzzball_logos'},
            'warewulf': {'name': 'Warewulf', 'description': 'HPC cluster provisioning tool', 'structure_type': 'product', 'asset_key': 'warewulf_pro_logos'},
            'apptainer': {'name': 'Apptainer', 'description': 'Container platform for HPC/scientific workflows', 'structure_type': 'product', 'asset_key': 'apptainer_logos'},
            'ascender': {'name': 'Ascender', 'description': 'Infrastructure automation platform', 'structure_type': 'product', 'asset_key': 'ascender_pro_logos'},
            'bridge': {'name': 'Bridge', 'description': 'CentOS 7 migration solution', 'structure_type': 'product', 'asset_key': 'bridge_logos'},
            'rlc': {'name': 'RLC', 'description': 'Rocky Linux Commercial (base platform)', 'structure_type': 'product', 'asset_key': 'rlc_logos'},
            'rlc-ai': {'name': 'RLC-AI', 'description': 'Rocky Linux Commercial AI-focused platform', 'structure_type': 'product', 'asset_key': 'rlc_ai_logos'},
            'rlc-hardened': {'name': 'RLC-Hardened', 'description': 'Rocky Linux Commercial security-focused platform', 'structure_type': 'product', 'asset_key': 'rlc_hardened_logos'},
            'rlc-lts': {'name': 'RLC-LTS', 'description': 'Rocky Linux Commercial long-term support', 'structure_type': 'product', 'asset_key': 'rlc_lts_logos'}
        }

    def match_assets(self, request: str) -> Dict[str, Any]:
        """Match assets using enhanced attribute detection"""
        attributes = self.detector.detect_attributes(request)
        
        if not attributes['product']:
            return self._generate_product_help()
        
        product_id = attributes['product']['value']
        confidence_level = self._assess_confidence_level(attributes['total_confidence'])
        
        product_info = self.product_info[product_id]
        product_assets = self.asset_data.get(product_info['asset_key'], {})
        
        if not product_assets:
            return {'error': f'No assets found for {product_info["name"]}'}
        
        # RULE #1: Apply background compatibility filter BEFORE scoring
        filtered_assets = self._apply_background_filter(product_assets, attributes)
        
        if not filtered_assets:
            return {'error': f'No background-compatible assets found for {product_info["name"]}'}
        
        # RULE #2: Use asset-type-specific scoring
        if product_id == 'ciq':
            scored_assets = self._score_ciq_assets(filtered_assets, attributes)
        else:
            scored_assets = self._score_product_assets(filtered_assets, attributes)
        
        return {
            'success': True,
            'product': product_info,
            'attributes': attributes,
            'confidence_level': confidence_level,
            'scored_assets': scored_assets,
            'filtered_count': len(filtered_assets),
            'original_count': len(product_assets)
        }
    
    def _apply_background_filter(self, assets: Dict, attributes: Dict) -> Dict:
        """RULE #1: Filter assets by background compatibility BEFORE scoring"""
        if not attributes['background']:
            return assets  # No background specified, return all
        
        target_background = attributes['background']['value']
        compatible_assets = {}
        
        for asset_key, asset in assets.items():
            asset_background = asset.get('background', '').lower()
            
            # Only include assets compatible with target background
            if asset_background == target_background:
                compatible_assets[asset_key] = asset
        
        return compatible_assets
    
    def _score_ciq_assets(self, assets: Dict, attributes: Dict) -> List[Tuple[int, Dict, str]]:
        """RULE #2: CIQ-specific scoring using color_type + color_mode"""
        scored = []
        
        for asset_key, asset in assets.items():
            score = 0
            reasons = []
            
            # Perfect background match (already filtered, but score it)
            if attributes['background']:
                score += 80
                bg_type = attributes['background']['value']
                reasons.append(f"perfect {bg_type} background match")
            
            # CIQ Color Type Scoring
            asset_color_type = asset.get('color_type', '')
            
            if attributes['ciq_color_type']:
                target_color_type = attributes['ciq_color_type']['value']
                if target_color_type == asset_color_type:
                    score += 100
                    reasons.append(f"exact {target_color_type.replace('_', ' ')} match")
            else:
                # Default CIQ preferences when no specific type requested
                if asset_color_type == '1color_neutral':
                    score += 90
                    reasons.append("standard CIQ company logo")
                elif asset_color_type == '2color':
                    score += 70
                    reasons.append("hero CIQ company logo")
                elif asset_color_type == '1color_green':
                    score += 60
                    reasons.append("standard+ green version")
            
            # Detect hero vs standard context from request
            request_lower = attributes.get('original_request', '').lower()
            is_hero_context = any(term in request_lower for term in ['hero', 'presentation', 'primary', 'large display', 'marketing'])
            
            if is_hero_context and asset_color_type == '2color':
                score += 20
                reasons.append("perfect for hero context")
            elif not is_hero_context and asset_color_type == '1color_neutral':
                score += 20
                reasons.append("ideal for standard applications")
            
            if score > 0:
                scored.append((score, asset, " + ".join(reasons)))
        
        return sorted(scored, key=lambda x: x[0], reverse=True)
    
    def _score_product_assets(self, assets: Dict, attributes: Dict) -> List[Tuple[int, Dict, str]]:
        """RULE #2: Product-specific scoring using layout + background (existing logic)"""
        scored = []
        vertical_requested = attributes['layout'] and attributes['layout']['value'] == 'vertical'
        
        for asset_key, asset in assets.items():
            asset_layout = asset.get('layout', '').lower()
            
            # Skip vertical layouts unless explicitly requested
            if 'vertical' in asset_layout and not vertical_requested:
                continue
            
            score = 0
            reasons = []
            
            # Perfect background match (already filtered, but score it)
            if attributes['background']:
                score += 80
                bg_type = attributes['background']['value']
                reasons.append(f"perfect {bg_type} background match")
            
            # Layout matching for products
            if attributes['layout'] and attributes['layout']['value']:
                target_layout = attributes['layout']['value']
                if target_layout in asset_layout:
                    score += 100
                    reasons.append(f"exact {target_layout} match")
            else:
                # Default product layout preferences
                if 'horizontal' in asset_layout:
                    score += 80
                    reasons.append("default horizontal layout (best brand recognition)")
                elif 'icon' in asset_layout:
                    score += 60
                    reasons.append("icon option")
            
            # Color correctness bonus
            if attributes['background']:
                target_bg = attributes['background']['value']
                asset_color = asset.get('color', '').lower()
                
                if target_bg == 'light' and asset_color == 'black':
                    score += 20
                    reasons.append("proper dark-on-light contrast")
                elif target_bg == 'dark' and asset_color == 'white':
                    score += 20
                    reasons.append("proper light-on-dark contrast")
            
            if score > 0:
                scored.append((score, asset, " + ".join(reasons)))
        
        return sorted(scored, key=lambda x: x[0], reverse=True)
    
    def _assess_confidence_level(self, total_confidence: int) -> str:
        """Assess confidence level with enhanced background weighting"""
        if total_confidence >= 110:  # Product (50) + Background (60) = 110
            return 'high'
        elif total_confidence >= 50:
            return 'medium'
        else:
            return 'low'
    
    def _generate_product_help(self) -> Dict[str, Any]:
        """Generate help when product is not detected"""
        return {
            'help': True,
            'message': """**CIQ Brand Assets Available:**

**Company Brand:**
• **CIQ** - Main company logo (3 color types: neutral, green, hero)

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
• \"CIQ logo for dark background\" → Direct answer
• \"Fuzzball logo for light background\" → Direct answer
• \"RLC-AI vertical logo\" → Specific layout
• \"Warewulf symbol\" → Icon only

Which brand asset do you need?"""
        }

class ResponseFormatter:
    """Template-based response formatting with CIQ-specific templates"""
    
    def format_response(self, match_result: Dict[str, Any]) -> str:
        """Format response based on confidence level and asset type"""
        if match_result.get('help'):
            return match_result['message']
        
        if match_result.get('error'):
            return f"❌ {match_result['error']}"
        
        product_id = match_result['product']['name'].lower()
        confidence_level = match_result['confidence_level']
        
        if confidence_level == 'high':
            return self._format_high_confidence(match_result, is_ciq=(product_id == 'ciq'))
        elif confidence_level == 'medium':
            return self._format_medium_confidence(match_result, is_ciq=(product_id == 'ciq'))
        else:
            return self._format_low_confidence(match_result, is_ciq=(product_id == 'ciq'))
    
    def _format_high_confidence(self, result: Dict, is_ciq: bool = False) -> str:
        """High confidence: Direct answer with single best asset"""
        best_asset = result['scored_assets'][0]
        score, asset, reasoning = best_asset
        product_info = result['product']
        
        if is_ciq:
            # CIQ-specific formatting
            color_type = asset.get('color_type', '').replace('_', ' ')
            color_mode = asset.get('color_mode', '')
            desc = f"{color_type} for {color_mode} backgrounds"
        else:
            # Product formatting
            layout_desc = asset.get('layout', 'logo').replace('icon', 'symbol')
            desc = layout_desc
        
        return f"""✅ **{product_info['name']} {desc}:**

📎 **Download:** {asset['url']}

💡 **Why this choice:** {reasoning}

📋 **Usage guidance:** {asset.get('guidance', f'Professional {product_info["name"]} branding')}"""
    
    def _format_medium_confidence(self, result: Dict, is_ciq: bool = False) -> str:
        """Medium confidence: Top choice + background-compatible alternatives"""
        scored_assets = result['scored_assets'][:3]  # Limit to top 3
        product_info = result['product']
        
        response = f"**{product_info['name']} Logo - Top Recommendation:**\n\n"
        
        # Primary choice
        best_score, best_asset, best_reasoning = scored_assets[0]
        
        if is_ciq:
            color_type = best_asset.get('color_type', '').replace('_', ' ')
            desc = f"{color_type} logo"
        else:
            layout_desc = best_asset.get('layout', 'logo').replace('icon', 'symbol')
            desc = f"{layout_desc.title()}"
        
        response += f"""✅ **Primary Choice: {desc}**
• **Download:** {best_asset['url']}
• **Why:** {best_reasoning}

"""
        
        # Background-compatible alternatives only
        if len(scored_assets) > 1:
            response += "**Alternative Options:**\n"
            for i, (score, asset, reasoning) in enumerate(scored_assets[1:], 2):
                if is_ciq:
                    alt_color_type = asset.get('color_type', '').replace('_', ' ')
                    alt_desc = f"{alt_color_type}"
                else:
                    alt_layout = asset.get('layout', 'logo').replace('icon', 'symbol')
                    alt_desc = alt_layout
                response += f"• **Option {i}:** {alt_desc} - {asset['url']}\n"
        
        return response
    
    def _format_low_confidence(self, result: Dict, is_ciq: bool = False) -> str:
        """Low confidence: Clarifying questions based on asset type"""
        product_info = result['product']
        attributes = result['attributes']
        
        # Determine what we need to clarify
        if not attributes['background']:
            return f"""🎨 **I found {product_info['name']} assets for you!**

**What background will this logo be placed on?**

• 🌞 **light** → white, light gray, light colors, most websites
• 🌙 **dark** → black, dark gray, dark colors, dark photos

This helps me recommend the right color version for proper contrast."""
        
        elif is_ciq and not attributes['ciq_color_type']:
            return f"""✨ **Perfect! For CIQ company logos...**

**Which type works best for your use case?**

🔸 **standard** → 1-color neutral (most applications)
🟢 **green** → 1-color green (when you need extra punch)
🌟 **hero** → 2-color (when logo is primary visual element)

What's your primary use case?"""
        
        elif not is_ciq and not attributes['layout']:
            return f"""✨ **Perfect! For {product_info['name']} logos...**

**Which layout works best for your use case?**

🔸 **horizontal** → Symbol + text side-by-side (headers, business cards)
⚫ **symbol** → Icon only (tight spaces, favicons)

💡 Need vertical? Just ask for \"vertical layout\" specifically!

What's your primary use case?"""
        
        else:
            # Show top options with guidance
            return self._format_medium_confidence(result, is_ciq)

@mcp.tool()
def get_brand_asset(request: str, background: Optional[str] = None) -> str:
    """
    Get CIQ brand assets with intelligent attribute detection and enhanced confidence scoring.
    
    Examples:
    - "CIQ logo for light background" → HIGH confidence, direct answer
    - "Fuzzball logo" → LOW confidence, asks for background
    - "RLC-AI vertical logo for dark background" → HIGH confidence, specific match
    - "Warewulf symbol" → HIGH confidence, direct symbol
    """
    
    # Load data if needed
    if asset_data is None:
        if not load_asset_data():
            return "❌ Sorry, couldn't load brand assets data."
    
    # Override background if provided
    if background:
        request = f"{request} for {background} background"
    
    # Store original request for context detection
    attributes_with_request = request
    
    # Initialize components
    matcher = AssetMatcher(asset_data)
    formatter = ResponseFormatter()
    
    # Match assets and format response
    match_result = matcher.match_assets(request)
    
    # Add original request for context detection
    if match_result.get('attributes'):
        match_result['attributes']['original_request'] = request
    
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
    
    result += """
**ENHANCED Features:**
• **Background filtering:** Only compatible assets suggested
• **CIQ-specific logic:** Color type (neutral/green/hero) + background mode
• **Product logic:** Layout (horizontal/vertical/icon) + background compatibility
• **Smart defaults:** No vertical unless requested, proper contrast

🧹 **Clean structure:** 46 essential assets, no duplicates"""
    
    return result

# Load data on startup
load_asset_data()

# FastMCP Cloud entry point
if __name__ == "__main__":
    mcp.run()
