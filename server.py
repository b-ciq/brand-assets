#!/usr/bin/env python3
"""
CIQ Brand Assets MCP Server - Declarative Rules Engine
Clean, scalable server using declarative metadata with rule-based matching
"""

from fastmcp import FastMCP
import json
import requests
from typing import Optional, Dict, Any, List, Tuple
import re
import base64
from io import BytesIO

# Asset metadata URL
METADATA_URL = 'https://raw.githubusercontent.com/b-ciq/brand-assets/main/metadata/asset-inventory.json'

# Initialize FastMCP server
mcp = FastMCP("CIQ Brand Assets")

# Global asset data cache
asset_data = None

def load_image_as_data_uri(image_url: str) -> Optional[str]:
    """Load image from URL and convert to data URI"""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Check if content type is actually an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            print(f"❌ URL does not return an image: {image_url} (got {content_type})")
            return None
        
        # Check if we got actual image data (more than just a few bytes)
        if len(response.content) < 100:  # Very small files are probably not real images
            print(f"❌ Image data too small: {image_url}")
            return None
        
        # Convert to base64
        image_data = base64.b64encode(response.content).decode('utf-8')
        
        # Return as data URI
        return f"data:{content_type};base64,{image_data}"
    except Exception as e:
        print(f"❌ Failed to load image {image_url}: {e}")
        return None

def enhance_asset_with_image(asset: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance asset dictionary with image data"""
    enhanced_asset = asset.copy()
    
    # Load the actual image
    image_data_uri = load_image_as_data_uri(asset['url'])
    if image_data_uri:
        enhanced_asset['image'] = image_data_uri
    else:
        # Still include the key but with None value so the response structure is consistent
        enhanced_asset['image'] = None
    
    return enhanced_asset

def load_asset_data():
    """Load asset metadata from GitHub"""
    global asset_data
    try:
        response = requests.get(METADATA_URL, timeout=10)
        response.raise_for_status()
        asset_data = response.json()
        
        # Validate structure
        if 'assets' not in asset_data or 'rules' not in asset_data or 'index' not in asset_data:
            raise ValueError("Invalid metadata structure")
        
        total_assets = asset_data['index']['total_assets']
        products_count = len(asset_data['index']['products'])
        
        print(f"✅ Loaded {total_assets} assets across {products_count} products")
        print(f"✅ Declarative rules engine ready")
        return True
    except Exception as e:
        print(f"❌ Failed to load asset data: {e}")
        return False

class DeclarativeAssetMatcher:
    """Rule-based asset matching using declarative metadata"""
    
    def __init__(self):
        self.product_patterns = {
            'ciq': ['ciq', 'company', 'brand', 'main'],
            'fuzzball': ['fuzzball', 'fuzz ball', 'workload', 'hpc'],
            'warewulf': ['warewulf', 'cluster', 'provisioning'],
            'apptainer': ['apptainer', 'container', 'scientific'],
            'ascender': ['ascender', 'automation', 'ansible'],
            'bridge': ['bridge', 'centos', 'migration'],
            'support': ['support', 'ciq support'],
            'rlc': ['rlc', 'rocky linux commercial', 'rocky linux'],
            'rlc-ai': ['rlc-ai', 'rlc ai', 'rocky linux ai'],
            'rlc-hardened': ['rlc-hardened', 'rlc hardened', 'rocky linux hardened'],
            'rlc-lts': ['rlc-lts', 'rlc lts', 'rocky linux lts']
        }
        
        self.background_patterns = {
            'light': ['light', 'white', 'light background'],
            'dark': ['dark', 'black', 'dark background']
        }
        
        self.layout_patterns = {
            'icon': ['symbol', 'icon', 'favicon', 'app icon'],
            'horizontal': ['horizontal', 'wide', 'header', 'lockup'],
            'vertical': ['vertical', 'tall', 'stacked'],
            'onecolor': ['1-color', '1 color', 'one color', 'onecolor'],
            'twocolor': ['2-color', '2 color', 'two color', 'twocolor'],
            'green': ['green', 'accent']
        }

    def find_assets(self, request: str) -> Dict[str, Any]:
        """Main asset finding function using declarative rules"""
        if not asset_data:
            return {'error': 'Asset data not loaded'}
        
        # Parse user request
        parsed = self._parse_request(request)
        
        # Find matching assets
        if parsed['product']:
            matches = self._match_assets(parsed['product'], parsed)
            return self._format_response(matches, parsed)
        else:
            return self._generate_product_help()

    def _parse_request(self, request: str) -> Dict[str, Any]:
        """Parse user request into structured attributes"""
        request_lower = request.lower()
        
        # Detect product
        product = None
        product_confidence = 0.0
        
        for prod, patterns in self.product_patterns.items():
            for pattern in patterns:
                if pattern in request_lower:
                    # Longer, more specific patterns get higher confidence
                    confidence = min(len(pattern) / 10.0, 0.6)  # Max 0.6 for product
                    if confidence > product_confidence:
                        product = prod
                        product_confidence = confidence
        
        # Detect background
        background = None
        background_confidence = 0.0
        
        for bg, patterns in self.background_patterns.items():
            for pattern in patterns:
                if pattern in request_lower:
                    background = bg
                    background_confidence = 0.3  # Fixed confidence for background
                    break
        
        # Detect layout/variant
        layout = None
        layout_confidence = 0.0
        
        for lyt, patterns in self.layout_patterns.items():
            for pattern in patterns:
                if pattern in request_lower:
                    layout = lyt
                    layout_confidence = 0.3  # Fixed confidence for layout
                    break
        
        # Calculate total confidence - boost if multiple attributes detected
        total_confidence = product_confidence
        if background:
            total_confidence += background_confidence
        if layout:
            total_confidence += layout_confidence
        
        # Boost total confidence if we have multiple specific attributes
        if product and background and layout:
            total_confidence = min(total_confidence * 1.2, 1.0)  # 20% boost for complete match
        
        return {
            'product': product,
            'background': background,
            'layout': layout,
            'confidence': min(total_confidence, 1.0),
            'raw_request': request
        }

    def _match_assets(self, product: str, parsed: Dict) -> List[Tuple[float, Dict, str]]:
        """Match assets using declarative rules"""
        if product not in asset_data['assets']:
            return []
        
        product_assets = asset_data['assets'][product]
        rules = asset_data['rules']
        matches = []
        
        for asset_key, asset in product_assets.items():
            score, reason = self._score_asset(asset, parsed, rules)
            if score > 0:
                matches.append((score, asset, reason))
        
        # Sort by score (highest first)
        return sorted(matches, key=lambda x: x[0], reverse=True)

    def _score_asset(self, asset: Dict, parsed: Dict, rules: Dict) -> Tuple[float, str]:
        """Score individual asset using confidence rules"""
        score = 0.0
        reasons = []
        
        # Base score for having the product
        score += rules['confidence_scoring']['fallback']
        reasons.append("product match")
        
        # Background matching - critical when specified
        if parsed['background'] and asset['background'] == parsed['background']:
            score += rules['confidence_scoring']['background_match']
            reasons.append(f"optimized for {parsed['background']} backgrounds")
        elif parsed['background'] and asset['background'] != parsed['background']:
            # Penalize wrong background when user specifies one
            score *= 0.5  # Reduce score by half for wrong background
            reasons.append(f"wrong background ({asset['background']} instead of {parsed['background']})")
        
        # Layout matching
        if parsed['layout'] and asset['layout'] == parsed['layout']:
            score += rules['confidence_scoring']['layout_match']
            reasons.append(f"exact {parsed['layout']} match")
        
        # Both background and layout match = exact match
        if (parsed['background'] and parsed['layout'] and 
            asset['background'] == parsed['background'] and 
            asset['layout'] == parsed['layout']):
            score = rules['confidence_scoring']['exact_match']
            reasons = [f"exact match: {parsed['layout']} for {parsed['background']} backgrounds"]
        
        # Use case tag matching
        if parsed.get('use_case'):
            asset_tags = asset.get('tags', [])
            if parsed['use_case'] in asset_tags:
                score += rules['confidence_scoring']['tag_match'] 
                reasons.append(f"perfect for {parsed['use_case']}")
        
        return score, " + ".join(reasons)

    def _format_response(self, matches: List[Tuple[float, Dict, str]], parsed: Dict) -> Dict[str, Any]:
        """Format response based on confidence and matches"""
        if not matches:
            return {
                'message': f"No {parsed['product']} assets found matching your criteria.",
                'confidence': 'none'
            }
        
        confidence_level = self._get_confidence_level(parsed['confidence'])
        
        # Handle simple product-only queries (e.g., "CIQ logo", "can you find me a warewulf logo?") - ask for background first
        if (confidence_level in ['low', 'medium'] and parsed['product'] and 
            not parsed['background'] and not parsed['layout']):
            return {
                'message': f"I have several {parsed['product'].upper()} logos available.",
                'question': "What background will you be using this on?",
                'options': [
                    {"value": "light", "label": "Light backgrounds (white, bright colors)"},
                    {"value": "dark", "label": "Dark backgrounds (black, dark colors)"}
                ],
                'confidence': 'clarifying',
                'help': f"Once I know the background, I can recommend the perfect {parsed['product'].upper()} logo for you."
            }
        
        # Find perfect matches (score > 1.0 - multiple criteria matched)
        perfect_matches = [m for m in matches if m[0] > 1.0]
        # Find exact matches (score >= 1.0)
        exact_matches = [m for m in matches if m[0] >= 1.0]
        
        if confidence_level == 'high' and len(perfect_matches) == 1:
            # High confidence, single perfect match - return it directly
            asset = perfect_matches[0][1]
            enhanced_asset = enhance_asset_with_image(asset)
            return {
                'message': f"Here's the perfect {parsed['product']} asset for your needs:",
                'asset': {
                    'url': asset['url'],
                    'filename': asset['filename'],
                    'description': f"{parsed['product'].title()} {asset['layout']} logo ({asset['color']}) for {parsed['background'] or asset['background']} backgrounds",
                    'background': asset['background'],
                    'layout': asset['layout'],
                    'image': enhanced_asset.get('image')
                },
                'confidence': 'high',
                'reason': perfect_matches[0][2]
            }
        elif confidence_level == 'high' and len(perfect_matches) > 1:
            # High confidence, multiple perfect matches - show them
            assets = []
            for score, asset, reason in perfect_matches:
                enhanced_asset = enhance_asset_with_image(asset)
                assets.append({
                    'url': asset['url'],
                    'filename': asset['filename'],
                    'layout': asset['layout'],
                    'background': asset['background'],
                    'score': round(score, 2),
                    'reason': reason,
                    'image': enhanced_asset.get('image')
                })
            
            return {
                'message': f"Here are the perfect {parsed['product']} matches for your request:",
                'assets': assets,
                'confidence': 'high',
                'suggestion': self._generate_suggestion(parsed)
            }
        elif confidence_level == 'high' and len(exact_matches) == 1:
            # High confidence, single exact match - return it
            asset = exact_matches[0][1]
            enhanced_asset = enhance_asset_with_image(asset)
            return {
                'message': f"Here's the exact {parsed['product']} asset you requested:",
                'asset': {
                    'url': asset['url'],
                    'filename': asset['filename'],
                    'description': f"{parsed['product'].title()} {asset['layout']} logo ({asset['color']}) for {parsed['background'] or asset['background']} backgrounds",
                    'background': asset['background'],
                    'layout': asset['layout'],
                    'image': enhanced_asset.get('image')
                },
                'confidence': 'high',
                'reason': exact_matches[0][2]
            }
        elif confidence_level == 'high' and len(exact_matches) > 1:
            # High confidence, multiple exact matches - try to find perfect match first
            perfect_candidates = []
            if parsed['background'] and parsed['layout']:
                # Filter for assets matching both criteria
                for score, asset, reason in exact_matches:
                    if asset['background'] == parsed['background'] and asset['layout'] == parsed['layout']:
                        perfect_candidates.append((score, asset, reason))
            
            if len(perfect_candidates) == 1:
                # Found single perfect match - return it
                asset = perfect_candidates[0][1]
                enhanced_asset = enhance_asset_with_image(asset)
                return {
                    'message': f"Here's the perfect {parsed['product']} asset for your needs:",
                    'asset': {
                        'url': asset['url'],
                        'filename': asset['filename'],
                        'description': f"{parsed['product'].title()} {asset['layout']} logo ({asset['color']}) for {parsed['background']} backgrounds",
                        'background': asset['background'],
                        'layout': asset['layout'],
                        'image': enhanced_asset.get('image')
                    },
                    'confidence': 'high',
                    'reason': perfect_candidates[0][2]
                }
            else:
                # Multiple matches - show top matches
                assets = []
                for score, asset, reason in exact_matches[:3]:
                    enhanced_asset = enhance_asset_with_image(asset)
                    assets.append({
                        'url': asset['url'],
                        'filename': asset['filename'],
                        'layout': asset['layout'],
                        'background': asset['background'],
                        'score': round(score, 2),
                        'reason': reason,
                        'image': enhanced_asset.get('image')
                    })
                
                return {
                    'message': f"Here are the best {parsed['product']} matches for your request:",
                    'assets': assets,
                    'confidence': 'high',
                    'suggestion': self._generate_suggestion(parsed)
                }
        elif (confidence_level in ['high', 'medium'] and len(matches) <= 4) or \
             (confidence_level == 'medium' and parsed['background'] and len(exact_matches) > 0):
            # Medium confidence or manageable matches - show options
            # Also handle background-specific queries with exact matches
            assets = []
            matches_to_show = exact_matches if parsed['background'] and len(exact_matches) > 0 else matches
            for score, asset, reason in matches_to_show[:3]:
                enhanced_asset = enhance_asset_with_image(asset)
                assets.append({
                    'url': asset['url'],
                    'filename': asset['filename'],
                    'layout': asset['layout'],
                    'background': asset['background'],
                    'score': round(score, 2),
                    'reason': reason,
                    'image': enhanced_asset.get('image')
                })
            
            return {
                'message': f"Here are the best {parsed['product']} options based on your request:",
                'assets': assets,
                'confidence': confidence_level,
                'suggestion': self._generate_suggestion(parsed)
            }
        else:
            # Low confidence or many matches - show categories
            return self._generate_guided_response(parsed['product'], matches)

    def _get_confidence_level(self, score: float) -> str:
        """Convert numeric confidence to level"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'

    def _generate_suggestion(self, parsed: Dict) -> str:
        """Generate helpful suggestion for user"""
        suggestions = []
        
        if not parsed['background']:
            suggestions.append("specify the background (light or dark)")
        
        if not parsed['layout']:
            if parsed['product'] == 'ciq':
                suggestions.append("specify variant (onecolor, twocolor, or green)")
            else:
                suggestions.append("specify layout (icon, horizontal, or vertical)")
        
        if suggestions:
            return f"For more precise results, try also mentioning: {', '.join(suggestions)}"
        
        return "Great match! This should work perfectly for your needs."

    def _generate_guided_response(self, product: str, matches: List) -> Dict[str, Any]:
        """Generate guided response for low-confidence requests"""
        if product not in asset_data['assets']:
            return self._generate_product_help()
        
        product_assets = asset_data['assets'][product]
        
        # Group by layout
        layout_groups = {}
        for asset_key, asset in product_assets.items():
            layout = asset['layout']
            if layout not in layout_groups:
                layout_groups[layout] = []
            layout_groups[layout].append(asset)
        
        options = []
        # Prefer consistent background across examples (light background = black logos)
        preferred_background = 'light'  # Default to light backgrounds (black logos)
        
        for layout, assets in layout_groups.items():
            # Try to find an asset for the preferred background
            example = None
            for asset in assets:
                if asset['background'] == preferred_background:
                    example = asset
                    break
            
            # Fallback to first asset if no preferred background found
            if not example:
                example = assets[0]
                
            enhanced_example = enhance_asset_with_image(example)
            options.append({
                'layout': layout,
                'example_url': example['url'],
                'count': len(assets),
                'description': self._get_layout_description(layout),
                'background_note': f"Showing {example['color']} version (for {example['background']} backgrounds)",
                'image': enhanced_example.get('image')
            })
        
        return {
            'message': f"I found {len(matches)} {product} assets. Here are your options:",
            'product': product,
            'options': options,
            'confidence': 'low',
            'background_question': "What background will you use these on?",
            'background_options': [
                {"type": "light", "description": "Light backgrounds (use black logos)", "example": "white websites, documents"},
                {"type": "dark", "description": "Dark backgrounds (use white logos)", "example": "dark mode, black presentations"}
            ],
            'help': f"For better recommendations, specify: '{product} horizontal logo for light backgrounds' or '{product} icon for dark theme'"
        }

    def _get_layout_description(self, layout: str) -> str:
        """Get description for layout type"""
        descriptions = {
            'icon': 'Square symbol, perfect for favicons and app icons',
            'horizontal': 'Wide format, great for headers and business cards',
            'vertical': 'Tall format, ideal for mobile and social media',
            'onecolor': 'Clean single-color CIQ logo',
            'twocolor': 'Full-color CIQ logo with green accent',
            'green': 'Green CIQ logo for brand accent'
        }
        return descriptions.get(layout, f'{layout.title()} layout')

    def _generate_product_help(self) -> Dict[str, Any]:
        """Generate help when no product is detected"""
        products = asset_data['index']['products']
        
        return {
            'help': True,
            'message': "**CIQ Brand Assets Available:**\n\n" +
                      "**Company Brand:**\n• **CIQ** - Main company logo\n\n" +
                      "**Product Brands:**\n" +
                      "\n".join([f"• **{prod.title()}**" for prod in products if prod != 'ciq']),
            'examples': [
                "CIQ twocolor logo for light backgrounds",
                "Warewulf horizontal logo for dark theme",
                "Apptainer icon for favicon"
            ],
            'confidence': 'none'
        }

# Initialize the matcher
matcher = DeclarativeAssetMatcher()

@mcp.tool()
def get_brand_assets(request: str = "CIQ logo") -> Dict[str, Any]:
    """
    Find and recommend CIQ brand assets based on your needs.
    
    Specify what you need and I'll find the perfect asset:
    - Product: CIQ, Fuzzball, Warewulf, Apptainer, etc.
    - Background: light, dark
    - Layout: icon, horizontal, vertical (or for CIQ: onecolor, twocolor, green)
    - Use case: favicon, business card, presentation, etc.
    
    Examples:
    - "Warewulf logo for dark backgrounds"
    - "CIQ twocolor logo for presentations" 
    - "Apptainer icon for favicon"
    """
    if not asset_data:
        if not load_asset_data():
            return {"error": "Unable to load asset data. Please try again."}
    
    try:
        result = matcher.find_assets(request)
        return result
    except Exception as e:
        return {
            "error": f"Error processing request: {e}",
            "suggestion": "Try a simpler request like 'CIQ logo' or 'Fuzzball assets'"
        }

# Load asset data on startup
print("🚀 Starting CIQ Brand Assets MCP Server v1.1 (Logic Improvements Branch)...")
if load_asset_data():
    print("✅ Server ready!")
else:
    print("⚠️  Server started with limited functionality")

if __name__ == "__main__":
    mcp.run()