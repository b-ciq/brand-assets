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

class SemanticAssetMatcher:
    """Semantic intent-based asset matching system"""
    
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
            'rlc-lts': ['rlc-lts', 'rlc lts', 'rocky linux lts', 'rocky linux commercial lts', 'long term support', 'long-term support', 'lts']
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
        
        # Semantic intent categories
        self.intent_categories = {
            'all_assets': ['everything', 'all assets', 'all materials', 'complete set', 'full package', 'everything available'],
            'documents': ['docs', 'documentation', 'papers', 'materials', 'content', 'files', 'pdfs'],
            'sales_materials': ['sales', 'brief', 'sheet', '1-pager', '1 pager', 'one pager', 'overview', 'summary', 'sales sheet'],
            'technical_docs': ['specs', 'technical', 'datasheet', 'data sheet', 'whitepaper', 'white paper', 'guide', 'manual'],
            'visual_assets': ['logos', 'images', 'graphics', 'branding', 'visual', 'brand assets'],
            'case_studies': ['case study', 'success story', 'customer story', 'case studies']
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
            # Handle global queries when no specific product detected
            if parsed['primary_intent'] in ['documents', 'sales_materials', 'technical_docs', 'all_assets']:
                return self._handle_global_query(parsed)
            else:
                return self._generate_product_help()

    def _parse_request(self, request: str) -> Dict[str, Any]:
        """Parse user request using semantic intent recognition"""
        request_lower = request.lower()
        
        # Check for CIQ disambiguation cases
        product_context_patterns = [
            'product', 'products', 'portfolio', 'offerings', 'solutions',
            'brands', 'brand logos', 'all logos', 'available logos'
        ]
        
        contains_ciq = any(pattern in request_lower for pattern in ['ciq', 'company'])
        contains_product_context = any(pattern in request_lower for pattern in product_context_patterns)
        
        company_only_patterns = [
            'ciq company logo', 'main ciq logo', 'ciq brand logo',
            'corporate logo', 'company brand'
        ]
        is_clearly_company_only = any(pattern in request_lower for pattern in company_only_patterns)
        
        is_ciq_product_query = (contains_ciq and contains_product_context and not is_clearly_company_only)
        
        # Detect product - prioritize longer, more specific patterns
        product = None
        product_confidence = 0.0
        best_pattern_length = 0
        
        # First pass: find all matches and their pattern lengths
        all_matches = []
        for prod, patterns in self.product_patterns.items():
            for pattern in patterns:
                if pattern in request_lower:
                    confidence = min(len(pattern) / 10.0, 0.6)
                    all_matches.append((prod, confidence, len(pattern), pattern))
        
        # Sort by pattern length (longer first), then by confidence
        all_matches.sort(key=lambda x: (x[2], x[1]), reverse=True)
        
        # Take the best match
        if all_matches:
            product, product_confidence, _, _ = all_matches[0]
        
        # Detect semantic intent
        intent_scores = {}
        for intent_type, patterns in self.intent_categories.items():
            score = 0.0
            matched_patterns = []
            for pattern in patterns:
                if pattern in request_lower:
                    score += len(pattern) / 15.0  # Weight by pattern length
                    matched_patterns.append(pattern)
            intent_scores[intent_type] = {
                'score': min(score, 1.0),
                'patterns': matched_patterns
            }
        
        # Determine primary intent
        primary_intent = max(intent_scores.items(), key=lambda x: x[1]['score'])
        
        # Legacy parsing for backward compatibility
        background = None
        for bg, patterns in self.background_patterns.items():
            for pattern in patterns:
                if pattern in request_lower:
                    background = bg
                    break
        
        layout = None
        for lyt, patterns in self.layout_patterns.items():
            for pattern in patterns:
                if pattern in request_lower:
                    layout = lyt
                    break
        
        # Calculate confidence based on semantic understanding
        total_confidence = product_confidence
        if primary_intent[1]['score'] > 0:
            total_confidence += primary_intent[1]['score'] * 0.5
        
        if product and primary_intent[1]['score'] > 0.3:
            total_confidence = min(total_confidence * 1.3, 1.0)
        
        return {
            'product': product,
            'background': background,
            'layout': layout,
            'primary_intent': primary_intent[0],
            'intent_scores': intent_scores,
            'confidence': min(total_confidence, 1.0),
            'raw_request': request,
            'needs_ciq_disambiguation': is_ciq_product_query and product == 'ciq'
        }

    def _match_assets(self, product: str, parsed: Dict) -> List[Tuple[float, Dict, str]]:
        """Match assets using semantic intent-based rules"""
        if product not in asset_data['assets']:
            return []
        
        product_assets = asset_data['assets'][product]
        matches = []
        
        for asset_key, asset in product_assets.items():
            score, reason = self._score_asset_semantic(asset, parsed)
            if score > 0:
                matches.append((score, asset, reason))
        
        # Sort by score (highest first)
        return sorted(matches, key=lambda x: x[0], reverse=True)
    
    def _classify_assets_by_intent(self, assets: List[Dict]) -> Dict[str, List[Dict]]:
        """Classify assets based on their type and properties"""
        classification = {
            'all': assets,
            'logos': [],
            'documents': [],
            'sales_materials': [],
            'technical_docs': [],
            'visual_assets': []
        }
        
        for asset in assets:
            if asset['type'] == 'document':
                classification['documents'].append(asset)
                # Further classify documents by content type
                doc_type = asset.get('doc_type', '').lower()
                if any(term in doc_type for term in ['brief', 'overview', 'summary', 'sales']):
                    classification['sales_materials'].append(asset)
                elif any(term in doc_type for term in ['spec', 'technical', 'guide', 'manual']):
                    classification['technical_docs'].append(asset)
            else:
                classification['logos'].append(asset)
                classification['visual_assets'].append(asset)
        
        return classification
    
    def _handle_global_query(self, parsed: Dict) -> Dict[str, Any]:
        """Handle queries across all products (e.g., 'show me all solution briefs')"""
        intent = parsed['primary_intent']
        all_matching_assets = []
        
        # Search across all products
        for product_name, product_assets in asset_data['assets'].items():
            for asset_key, asset in product_assets.items():
                # Filter by intent
                should_include = False
                
                if intent == 'all_assets':
                    should_include = True
                elif intent == 'documents':
                    should_include = (asset['type'] == 'document')
                elif intent == 'sales_materials':
                    should_include = (asset['type'] == 'document' and 
                                    any(term in asset.get('doc_type', '').lower() 
                                        for term in ['brief', 'overview', 'summary', 'sales']))
                elif intent == 'technical_docs':
                    should_include = (asset['type'] == 'document' and 
                                    any(term in asset.get('doc_type', '').lower() 
                                        for term in ['spec', 'technical', 'guide', 'manual']))
                
                if should_include:
                    # Add product info to asset for display
                    enhanced_asset = asset.copy()
                    enhanced_asset['product'] = product_name
                    all_matching_assets.append(enhanced_asset)
        
        return self._format_global_response(all_matching_assets, parsed)
    
    def _format_global_response(self, assets: List[Dict], parsed: Dict) -> Dict[str, Any]:
        """Format response for global cross-product queries"""
        intent = parsed['primary_intent']
        
        if not assets:
            intent_label = {
                'documents': 'documents',
                'sales_materials': 'solution briefs or sales materials', 
                'technical_docs': 'technical documentation',
                'all_assets': 'assets'
            }.get(intent, 'assets')
            
            return {
                'message': f"No {intent_label} found across any products.",
                'suggestion': "Try asking for a specific product, like 'RLC-LTS solution brief' or 'Warewulf logos'",
                'confidence': 'medium'
            }
        
        # Group by product for better presentation
        by_product = {}
        for asset in assets:
            product = asset['product']
            if product not in by_product:
                by_product[product] = []
            by_product[product].append(asset)
        
        intent_labels = {
            'documents': 'documents',
            'sales_materials': 'solution briefs and sales materials',
            'technical_docs': 'technical documentation', 
            'all_assets': 'assets'
        }
        label = intent_labels.get(intent, 'assets')
        
        response = {
            'message': f"Here are all available {label} across CIQ products:",
            'total_count': len(assets),
            'products_with_assets': len(by_product),
            'confidence': 'high'
        }
        
        # Add products with their assets
        product_results = []
        for product_name, product_assets in by_product.items():
            product_info = {
                'product': product_name.upper(),
                'count': len(product_assets),
                'assets': self._format_asset_list(product_assets)
            }
            product_results.append(product_info)
        
        response['by_product'] = sorted(product_results, key=lambda x: x['product'])
        response['summary'] = f"Found {len(assets)} {label} across {len(by_product)} products"
        
        return response
    
    def _score_asset_semantic(self, asset: Dict, parsed: Dict) -> Tuple[float, str]:
        """Score assets using semantic intent understanding"""
        score = 0.4  # Base score for product match
        reasons = []
        
        primary_intent = parsed['primary_intent']
        intent_scores = parsed['intent_scores']
        
        # Handle intent-based scoring
        if primary_intent == 'all_assets':
            score = 0.8  # High score for comprehensive requests
            reasons.append("matches comprehensive asset request")
            
        elif primary_intent == 'documents':
            if asset['type'] == 'document':
                score = 0.9
                reasons.append(f"document: {asset.get('doc_type', 'unknown type')}")
            else:
                score = 0.2  # Lower but not zero - might still be relevant
                reasons.append("logo (documents requested)")
                
        elif primary_intent == 'sales_materials':
            if asset['type'] == 'document':
                doc_type = asset.get('doc_type', '').lower()
                if any(term in doc_type for term in ['brief', 'overview', 'summary', 'sales']):
                    score = 1.0
                    reasons.append(f"perfect sales material: {asset['doc_type']}")
                else:
                    score = 0.5
                    reasons.append(f"document: {asset['doc_type']}")
            else:
                score = 0.3
                reasons.append("logo (sales materials requested)")
                
        elif primary_intent == 'visual_assets':
            if asset['type'] != 'document':
                # Use detailed legacy logo scoring for visual assets
                score = self._legacy_score_asset(asset, parsed)
                if parsed['background'] and asset.get('background') == parsed['background']:
                    reasons.append(f"logo optimized for {parsed['background']} backgrounds")
                elif parsed['layout'] and asset.get('layout') == parsed['layout']:
                    reasons.append(f"exact {parsed['layout']} match")
                else:
                    reasons.append(f"{asset.get('layout', 'unknown')} logo")
            else:
                score = 0.1
                reasons.append("document (logos requested)")
        else:
            # Default scoring - use detailed legacy scoring
            if asset['type'] == 'document':
                score = 0.6
                reasons.append(f"document: {asset.get('doc_type', 'unknown type')}")
            else:
                score = self._legacy_score_asset(asset, parsed)
                reasons.append("logo match")
        
        # Boost score if multiple intents match
        high_intent_count = sum(1 for intent_data in intent_scores.values() if intent_data['score'] > 0.3)
        if high_intent_count > 1:
            score = min(score * 1.1, 1.0)
            reasons.append("matches multiple intents")
        
        return score, " + ".join(reasons)
    
    def _legacy_score_asset(self, asset: Dict, parsed: Dict) -> float:
        """Legacy scoring for backward compatibility"""
        score = 0.3
        
        if asset['type'] == 'document':
            return 0.6
        
        if parsed['background'] and asset.get('background') == parsed['background']:
            score += 0.4
        if parsed['layout'] and asset.get('layout') == parsed['layout']:
            score += 0.3
            
        return min(score, 1.0)

    def _score_asset(self, asset: Dict, parsed: Dict, rules: Dict) -> Tuple[float, str]:
        """Score individual asset using confidence rules"""
        score = 0.0
        reasons = []
        
        # Base score for having the product
        score += rules['confidence_scoring']['fallback']
        reasons.append("product match")
        
        # Handle document matching
        if asset['type'] == 'document':
            if parsed['doc_type']:
                if parsed['doc_type'] in asset['doc_type']:
                    score = rules['confidence_scoring']['exact_match']
                    reasons = [f"exact document match: {asset['doc_type']}"]
                else:
                    score *= 0.3  # Low score for wrong document type
                    reasons.append(f"document type mismatch")
            else:
                # Generic document request
                score = 0.6
                reasons = [f"document: {asset['doc_type']}"]
        else:
            # Handle logo matching (existing logic)
            # Background matching - critical when specified
            if parsed['background'] and asset.get('background') == parsed['background']:
                score += rules['confidence_scoring']['background_match']
                reasons.append(f"optimized for {parsed['background']} backgrounds")
            elif parsed['background'] and asset.get('background') != parsed['background']:
                # Penalize wrong background when user specifies one
                score *= 0.5  # Reduce score by half for wrong background
                reasons.append(f"wrong background ({asset.get('background')} instead of {parsed['background']})")
            
            # Layout matching
            if parsed['layout'] and asset.get('layout') == parsed['layout']:
                score += rules['confidence_scoring']['layout_match']
                reasons.append(f"exact {parsed['layout']} match")
            
            # Both background and layout match = exact match
            if (parsed['background'] and parsed['layout'] and 
                asset.get('background') == parsed['background'] and 
                asset.get('layout') == parsed['layout']):
                score = rules['confidence_scoring']['exact_match']
                reasons = [f"exact match: {parsed['layout']} for {parsed['background']} backgrounds"]
        
        # Use case tag matching (for both logos and documents)
        if parsed.get('use_case'):
            asset_tags = asset.get('tags', [])
            if parsed['use_case'] in asset_tags:
                score += rules['confidence_scoring']['tag_match'] 
                reasons.append(f"perfect for {parsed['use_case']}")
        
        return score, " + ".join(reasons)

    def _format_response(self, matches: List[Tuple[float, Dict, str]], parsed: Dict) -> Dict[str, Any]:
        """Format response using semantic understanding"""
        if not matches:
            return {
                'message': f"No {parsed['product']} assets found matching your criteria.",
                'confidence': 'none'
            }
        
        # Handle CIQ product disambiguation
        if parsed.get('needs_ciq_disambiguation'):
            return self._generate_ciq_disambiguation()
        
        # Extract just the assets for classification
        matched_assets = [match[1] for match in matches]
        asset_classification = self._classify_assets_by_intent(matched_assets)
        
        primary_intent = parsed['primary_intent']
        confidence_level = self._get_confidence_level(parsed['confidence'])
        
        # Handle different intent types
        if primary_intent == 'all_assets':
            return self._format_comprehensive_response(asset_classification, parsed, matches)
        elif primary_intent == 'documents' or primary_intent == 'sales_materials':
            return self._format_document_focused_response(asset_classification, parsed, matches, primary_intent)
        else:
            # Use enhanced legacy formatting
            return self._format_legacy_enhanced_response(matches, parsed, asset_classification)
    
    def _format_comprehensive_response(self, classification: Dict, parsed: Dict, matches: List) -> Dict[str, Any]:
        """Format response for 'show me everything' requests"""
        product_name = parsed['product'].upper()
        
        response = {
            'message': f"Here are all available {product_name} assets:",
            'confidence': 'high',
            'product': parsed['product']
        }
        
        # Group assets by type
        if classification['logos']:
            response['logos'] = {
                'count': len(classification['logos']),
                'assets': self._format_asset_list(classification['logos'][:6])  # Limit for readability
            }
        
        if classification['documents']:
            response['documents'] = {
                'count': len(classification['documents']),
                'assets': self._format_asset_list(classification['documents'])
            }
        
        total_count = len(classification['all'])
        response['summary'] = f"Found {total_count} total assets ({len(classification['logos'])} logos, {len(classification['documents'])} documents)"
        
        return response
    
    def _format_document_focused_response(self, classification: Dict, parsed: Dict, matches: List, intent: str) -> Dict[str, Any]:
        """Format response for document-focused requests"""
        product_name = parsed['product'].upper()
        
        if not classification['documents']:
            return {
                'message': f"No documents found for {product_name}, but I have logos available:",
                'logos': {
                    'count': len(classification['logos']),
                    'assets': self._format_asset_list(classification['logos'][:3])
                },
                'suggestion': f"Try asking for '{product_name} logos' or check if documents are available for other products.",
                'confidence': 'medium'
            }
        
        intent_label = 'sales materials' if intent == 'sales_materials' else 'documents'
        
        response = {
            'message': f"Here are the {product_name} {intent_label} I found:",
            'documents': {
                'count': len(classification['documents']),
                'assets': self._format_asset_list(classification['documents'])
            },
            'confidence': 'high'
        }
        
        # Also mention logos if available
        if classification['logos']:
            response['also_available'] = {
                'message': f"I also have {len(classification['logos'])} {product_name} logos available if needed.",
                'logos_sample': self._format_asset_list(classification['logos'][:2])
            }
        
        return response
    
    def _format_asset_list(self, assets: List[Dict]) -> List[Dict]:
        """Format list of assets for response"""
        formatted = []
        for asset in assets:
            asset_info = {
                'url': asset['url'],
                'filename': asset['filename'],
                'type': asset['type']
            }
            
            if asset['type'] == 'document':
                asset_info['doc_type'] = asset.get('doc_type', 'Document')
                asset_info['description'] = f"{asset.get('doc_type', 'Document').title()} - {asset['filename']}"
            else:
                asset_info['layout'] = asset.get('layout', 'unknown')
                asset_info['background'] = asset.get('background', 'any')
                asset_info['description'] = f"{asset.get('layout', 'Logo').title()} logo for {asset.get('background', 'any')} backgrounds"
            
            formatted.append(asset_info)
        
        return formatted
    
    def _format_legacy_enhanced_response(self, matches: List, parsed: Dict, classification: Dict) -> Dict[str, Any]:
        """Enhanced legacy response formatting"""
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
            return {
                'message': f"Here's the perfect {parsed['product']} asset for your needs:",
                'asset': {
                    'url': asset['url'],
                    'filename': asset['filename'],
                    'description': f"{parsed['product'].title()} {asset['layout']} logo ({asset['color']}) for {parsed['background'] or asset['background']} backgrounds",
                    'background': asset['background'],
                    'layout': asset['layout']
                },
                'confidence': 'high',
                'reason': perfect_matches[0][2]
            }
        elif confidence_level == 'high' and len(perfect_matches) > 1:
            # High confidence, multiple perfect matches - show them
            assets = []
            for score, asset, reason in perfect_matches:
                assets.append({
                    'url': asset['url'],
                    'filename': asset['filename'],
                    'layout': asset['layout'],
                    'background': asset['background'],
                    'score': round(score, 2),
                    'reason': reason
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
            return {
                'message': f"Here's the exact {parsed['product']} asset you requested:",
                'asset': {
                    'url': asset['url'],
                    'filename': asset['filename'],
                    'description': f"{parsed['product'].title()} {asset['layout']} logo ({asset['color']}) for {parsed['background'] or asset['background']} backgrounds",
                    'background': asset['background'],
                    'layout': asset['layout']
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
                return {
                    'message': f"Here's the perfect {parsed['product']} asset for your needs:",
                    'asset': {
                        'url': asset['url'],
                        'filename': asset['filename'],
                        'description': f"{parsed['product'].title()} {asset['layout']} logo ({asset['color']}) for {parsed['background']} backgrounds",
                        'background': asset['background'],
                        'layout': asset['layout']
                    },
                    'confidence': 'high',
                    'reason': perfect_candidates[0][2]
                }
            else:
                # Multiple matches - show top matches
                assets = []
                for score, asset, reason in exact_matches[:3]:
                    assets.append({
                        'url': asset['url'],
                        'filename': asset['filename'],
                        'layout': asset['layout'],
                        'background': asset['background'],
                        'score': round(score, 2),
                        'reason': reason
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
                assets.append({
                    'url': asset['url'],
                    'filename': asset['filename'],
                    'layout': asset['layout'],
                    'background': asset['background'],
                    'score': round(score, 2),
                    'reason': reason
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
                
            options.append({
                'layout': layout,
                'example_url': example['url'],
                'count': len(assets),
                'description': self._get_layout_description(layout),
                'background_note': f"Showing {example['color']} version (for {example['background']} backgrounds)"
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

    def _generate_ciq_disambiguation(self) -> Dict[str, Any]:
        """Generate disambiguation response for CIQ product queries"""
        if not asset_data:
            return {'error': 'Asset data not loaded'}
        
        products = [prod.title() for prod in asset_data['index']['products'] if prod != 'ciq']
        
        return {
            'message': "I found CIQ assets. Are you looking for:",
            'question': "Which type of logo do you need?",
            'options': [
                {
                    "value": "company", 
                    "label": "CIQ Company Logo", 
                    "description": "The main CIQ brand logo (onecolor, twocolor, green variants)"
                },
                {
                    "value": "products", 
                    "label": "CIQ Product Logos", 
                    "description": f"Logos for CIQ products: {', '.join(products)}"
                }
            ],
            'confidence': 'clarifying',
            'help': "Please specify 'CIQ company logo' or name a specific product like 'Warewulf logo' for more precise results."
        }

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
matcher = SemanticAssetMatcher()

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
print("🚀 Starting CIQ Brand Assets MCP Server...")
if load_asset_data():
    print("✅ Server ready!")
else:
    print("⚠️  Server started with limited functionality")

if __name__ == "__main__":
    mcp.run()