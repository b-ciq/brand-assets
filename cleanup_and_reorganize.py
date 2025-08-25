#!/usr/bin/env python3
"""
CIQ Brand Assets - Complete Cleanup and Reorganization Script
Removes unwanted files, separates RLC variants, and regenerates clean metadata
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set

class BrandAssetsCleanup:
    """Complete cleanup and reorganization of CIQ brand assets"""
    
    def __init__(self):
        self.root_dir = Path('.')
        self.cleanup_stats = {
            'files_removed': 0,
            'files_kept': 0,
            'directories_created': 0,
            'files_moved': 0
        }
        
        # Files to keep pattern - only largest PNGs
        self.keep_patterns = [
            '_L.png',  # Large PNGs
            '_large.png',  # Alternative large naming
        ]
        
        # Files to remove patterns
        self.remove_patterns = [
            '.svg',     # All SVGs
            '_S.png',   # Small PNGs  
            '_M.png',   # Medium PNGs
            '_small.png',   # Alternative small naming
            '_medium.png',  # Alternative medium naming
            '.ai',      # Adobe Illustrator files
            '.pdf',     # PDF files
        ]
        
        # RLC separation mapping
        self.rlc_separation = {
            'RLC logo': 'rlc_logos',
            'RLC-AI logo': 'rlc_ai_logos', 
            'RLC-Hardened logo': 'rlc_hardened_logos',
            'RLC-LTS logo': 'rlc_lts_logos'
        }
    
    def should_keep_file(self, filename: str) -> bool:
        """Determine if a file should be kept based on patterns"""
        filename_lower = filename.lower()
        
        # Check if it matches keep patterns
        for pattern in self.keep_patterns:
            if pattern in filename_lower:
                return True
        
        # Check if it matches remove patterns  
        for pattern in self.remove_patterns:
            if pattern in filename_lower:
                return False
        
        # Keep other files (like single logo files without size indicators)
        if filename_lower.endswith('.png'):
            return True
            
        return False
    
    def cleanup_directory(self, dir_path: Path) -> None:
        """Clean up a single logo directory"""
        if not dir_path.exists() or not dir_path.is_dir():
            return
            
        print(f"🧹 Cleaning up {dir_path.name}...")
        
        files_in_dir = list(dir_path.iterdir())
        for file_path in files_in_dir:
            if file_path.is_file():
                if self.should_keep_file(file_path.name):
                    print(f"  ✅ Keeping: {file_path.name}")
                    self.cleanup_stats['files_kept'] += 1
                else:
                    print(f"  ❌ Removing: {file_path.name}")
                    file_path.unlink()
                    self.cleanup_stats['files_removed'] += 1
    
    def separate_rlc_variants(self) -> None:
        """Separate mixed RLC variants into proper product directories"""
        rlc_dir = self.root_dir / "RLC(X)-logos"
        if not rlc_dir.exists():
            print("⚠️  RLC(X)-logos directory not found, skipping separation")
            return
        
        print("🔄 Separating RLC variants...")
        
        # Create new product directories
        for subdir_name, new_dir_name in self.rlc_separation.items():
            source_path = rlc_dir / subdir_name
            if source_path.exists():
                target_path = self.root_dir / new_dir_name
                
                if target_path.exists():
                    print(f"  📁 Directory {new_dir_name} already exists, merging...")
                    # Move files from source to target
                    for file_path in source_path.iterdir():
                        if file_path.is_file():
                            target_file = target_path / file_path.name
                            shutil.move(str(file_path), str(target_file))
                            self.cleanup_stats['files_moved'] += 1
                else:
                    print(f"  📁 Creating new directory: {new_dir_name}")
                    shutil.move(str(source_path), str(target_path))
                    self.cleanup_stats['directories_created'] += 1
        
        # Clean up the separated directories
        for new_dir_name in self.rlc_separation.values():
            dir_path = self.root_dir / new_dir_name
            if dir_path.exists():
                self.cleanup_directory(dir_path)
    
    def get_logo_directories(self) -> List[Path]:
        """Get all logo directories for cleanup"""
        logo_dirs = []
        
        # Standard logo directories
        standard_dirs = [
            "CIQ-logos",
            "fuzzball-logos", 
            "Apptainer-logos",
            "Warewulf-Pro-logos",
            "Ascender-Pro-logos",
            "Bridge-logos",
            "CIQ-Support-logos"
        ]
        
        for dir_name in standard_dirs:
            dir_path = self.root_dir / dir_name
            if dir_path.exists():
                logo_dirs.append(dir_path)
        
        # Add separated RLC directories
        for new_dir_name in self.rlc_separation.values():
            dir_path = self.root_dir / new_dir_name
            if dir_path.exists():
                logo_dirs.append(dir_path)
                
        return logo_dirs
    
    def generate_clean_metadata(self) -> Dict:
        """Generate clean metadata after cleanup"""
        print("📋 Generating clean metadata...")
        
        metadata = {
            "brand_guidelines": {
                "clear_space": "Equal to 1/4 the height of the 'Q' in the logo",
                "minimum_size": "70px height for digital applications",
                "primary_green": "#229529",
                "neutral_colors": {
                    "light_background": "dark_grey",
                    "dark_background": "light_grey"
                }
            }
        }
        
        # Product mapping
        product_mapping = {
            "CIQ-logos": ("logos", "ciq", "CIQ", "company"),
            "fuzzball-logos": ("fuzzball_logos", "fuzzball", "Fuzzball", "product"),
            "Apptainer-logos": ("apptainer_logos", "apptainer", "Apptainer", "product"),
            "Warewulf-Pro-logos": ("warewulf_pro_logos", "warewulf-pro", "Warewulf-Pro", "product"),
            "Ascender-Pro-logos": ("ascender_pro_logos", "ascender-pro", "Ascender-Pro", "product"),
            "Bridge-logos": ("bridge_logos", "bridge", "Bridge", "product"),
            "CIQ-Support-logos": ("ciq_support_logos", "ciq-support", "CIQ-Support", "product"),
            "rlc_logos": ("rlc_logos", "rlc", "RLC", "product"),
            "rlc_ai_logos": ("rlc_ai_logos", "rlc-ai", "RLC-AI", "product"),
            "rlc_hardened_logos": ("rlc_hardened_logos", "rlc-hardened", "RLC-Hardened", "product"),
            "rlc_lts_logos": ("rlc_lts_logos", "rlc-lts", "RLC-LTS", "product"),
        }
        
        for dir_name, (metadata_key, product_id, product_name, structure_type) in product_mapping.items():
            dir_path = self.root_dir / dir_name
            if dir_path.exists():
                print(f"  Processing {dir_name}...")
                metadata[metadata_key] = self.process_directory_metadata(
                    dir_path, product_id, product_name, structure_type
                )
        
        return metadata
    
    def process_directory_metadata(self, dir_path: Path, product_id: str, 
                                 product_name: str, structure_type: str) -> Dict:
        """Process a single directory for metadata"""
        assets = {}
        
        for file_path in dir_path.iterdir():
            if file_path.is_file() and file_path.name.lower().endswith('.png'):
                asset_data = self.analyze_file(file_path, product_id, product_name, structure_type)
                if asset_data:
                    key = self.generate_asset_key(asset_data)
                    assets[key] = asset_data
        
        return assets
    
    def analyze_file(self, file_path: Path, product_id: str, 
                    product_name: str, structure_type: str) -> Dict:
        """Analyze a single file and extract metadata"""
        filename = file_path.name
        
        # Parse filename components
        layout = self.detect_layout(filename)
        color = self.detect_color(filename) 
        background = self.detect_background(filename, color)
        size = self.detect_size(filename)
        
        # Generate description
        if structure_type == "company":
            if "2color" in filename.lower() or "hero" in filename.lower():
                layout = "2color"
                description = f"{product_name} 2-color company logo"
            else:
                layout = "1color"
                description = f"{product_name} 1-color company logo"
        else:
            description = f"{product_name} {layout} logo"
            if color != "unknown":
                description += f" ({color})"
            if background != "unknown":
                description += f" for {background} backgrounds"
            if size != "unknown":
                description += f" - {size.title()}"
        
        # Generate use cases and guidance
        use_cases, guidance = self.generate_use_cases_and_guidance(layout, structure_type, product_name)
        
        return {
            "filename": filename,
            "description": description,
            "layout": layout,
            "color": color,
            "background": background,
            "size": size,
            "use_cases": use_cases,
            "guidance": guidance,
            "format": "png",
            "product": product_id,
            "url": f"https://raw.githubusercontent.com/b-ciq/brand-assets/main/{file_path.parent.name}/{filename}",
            "path": f"{file_path.parent.name}/{filename}"
        }
    
    def detect_layout(self, filename: str) -> str:
        """Detect layout from filename"""
        filename_lower = filename.lower()
        
        if any(x in filename_lower for x in ['icon', 'symbol', '_i_', '_icon_']):
            return "icon"
        elif any(x in filename_lower for x in ['_h', 'horizontal', '_h_', '_horiz']):
            return "horizontal"  
        elif any(x in filename_lower for x in ['_v', 'vertical', '_v_', '_vert']):
            return "vertical"
        elif any(x in filename_lower for x in ['1color', '1-color', 'onecolor']):
            return "1color"
        elif any(x in filename_lower for x in ['2color', '2-color', 'twocolor', 'hero']):
            return "2color"
        
        return "horizontal"  # Default to horizontal for better brand recognition
    
    def detect_color(self, filename: str) -> str:
        """Detect color from filename"""
        filename_lower = filename.lower()
        
        if any(x in filename_lower for x in ['_blk', 'black', '_bk_', 'dark']):
            return "black"
        elif any(x in filename_lower for x in ['_wht', 'white', '_wt_', 'light']):
            return "white"  
        elif any(x in filename_lower for x in ['green', '_grn', 'color']):
            return "green"
        
        return "black"  # Default assumption for most logos
    
    def detect_background(self, filename: str, color: str) -> str:
        """Detect intended background from filename and color"""
        filename_lower = filename.lower()
        
        if any(x in filename_lower for x in ['light_bg', 'light-bg', 'lightbg']):
            return "light"
        elif any(x in filename_lower for x in ['dark_bg', 'dark-bg', 'darkbg']):
            return "dark"
        
        # Infer from color
        if color == "black":
            return "light"
        elif color == "white":
            return "dark"
        
        return "light"  # Default assumption
    
    def detect_size(self, filename: str) -> str:
        """Detect size from filename"""
        filename_lower = filename.lower()
        
        if '_l' in filename_lower or 'large' in filename_lower:
            return "large"
        elif '_m' in filename_lower or 'medium' in filename_lower:
            return "medium"
        elif '_s' in filename_lower or 'small' in filename_lower:
            return "small"
        
        return "large"  # Since we only keep large files
    
    def generate_use_cases_and_guidance(self, layout: str, structure_type: str, 
                                      product_name: str) -> tuple:
        """Generate use cases and guidance based on layout and type"""
        if structure_type == "company":
            if layout == "1color":
                use_cases = ["headers", "business_cards", "letterhead", "general_branding"]
                guidance = f"Standard {product_name} company logo for most applications"
            else:  # 2color
                use_cases = ["hero_sections", "presentations", "marketing_materials", "large_displays"]
                guidance = f"Hero {product_name} company logo when the logo is the primary visual element"
        else:
            if layout == "horizontal":
                use_cases = ["headers", "business_cards", "letterhead", "wide_banners"]
                guidance = f"Best for wide spaces - business cards, website headers, email signatures"
            elif layout == "vertical": 
                use_cases = ["tall_banners", "social_media_profile", "mobile_layout", "poster"]
                guidance = f"Perfect for tall/narrow spaces - social media profiles, mobile layouts"
            else:  # icon
                use_cases = ["favicon", "app_icon", "small_spaces", "avatars"]
                guidance = f"Perfect for tight spaces where you need just the {product_name} symbol"
        
        return use_cases, guidance
    
    def generate_asset_key(self, asset_data: Dict) -> str:
        """Generate a unique key for the asset"""
        product = asset_data['product'].replace('-', '_')
        layout = asset_data['layout']
        color = asset_data['color'][:3] if asset_data['color'] != "unknown" else "unk"
        size = asset_data['size']
        
        return f"{product}_{layout}_{color}_{size}"
    
    def run_complete_cleanup(self) -> None:
        """Run the complete cleanup and reorganization process"""
        print("🚀 Starting complete CIQ Brand Assets cleanup and reorganization...\n")
        
        # Step 1: Separate RLC variants first
        self.separate_rlc_variants()
        
        # Step 2: Clean up all logo directories
        logo_dirs = self.get_logo_directories()
        for logo_dir in logo_dirs:
            self.cleanup_directory(logo_dir)
        
        # Step 3: Generate clean metadata
        clean_metadata = self.generate_clean_metadata()
        
        # Step 4: Write metadata file
        metadata_dir = self.root_dir / "metadata"
        metadata_dir.mkdir(exist_ok=True)
        
        metadata_file = metadata_dir / "asset-inventory.json"
        with open(metadata_file, 'w') as f:
            json.dump(clean_metadata, f, indent=2)
        
        print(f"\n✅ Cleanup complete! Summary:")
        print(f"   📁 Directories created: {self.cleanup_stats['directories_created']}")
        print(f"   📄 Files moved: {self.cleanup_stats['files_moved']}")
        print(f"   ✅ Files kept: {self.cleanup_stats['files_kept']}")
        print(f"   ❌ Files removed: {self.cleanup_stats['files_removed']}")
        print(f"   📋 Metadata regenerated: {metadata_file}")
        
        # Generate summary
        self.generate_cleanup_summary(clean_metadata)
    
    def generate_cleanup_summary(self, metadata: Dict) -> None:
        """Generate a summary of the cleaned assets"""
        print(f"\n📊 **CLEANED ASSET SUMMARY:**")
        
        total_assets = 0
        for key, value in metadata.items():
            if key != "brand_guidelines":
                count = len(value)
                total_assets += count
                product_name = key.replace('_logos', '').replace('_', ' ').title()
                print(f"   • **{product_name}** - {count} variants")
        
        print(f"\n   🎯 **Total: {total_assets} clean assets**")
        print(f"   ✨ **Only largest PNG files kept**")
        print(f"   🔄 **RLC variants properly separated**")
        print(f"   🧹 **All SVGs and smaller sizes removed**")

if __name__ == "__main__":
    cleanup = BrandAssetsCleanup()
    cleanup.run_complete_cleanup()
