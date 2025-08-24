def parse_generic_filename(filename: str, product: str) -> Dict[str, Any]:
    """
    Parse generic product logo filename patterns:
    - {Product}-Icon_{color}_{size}.{ext} (matches Fuzzball icon pattern)
    - {Product}-Logo_{color}_{layout}_{size}.{ext} (new pattern)  
    - {Product}_logo_{layout}-{color}.{ext} (SVG pattern)
    - {Product}_icon_{color}.{ext} (SVG icon pattern)
    """
    
    # Icon pattern: Product-Icon_blk_L.png
    icon_pattern = rf'{product.title()}-Icon_(\w+)_([LMS])\.(\w+)'
    match = re.match(icon_pattern, filename, re.IGNORECASE)
    
    if match:
        color, size, ext = match.groups()
        background = 'light' if color.lower() == 'blk' else 'dark'
        size_full = {'L': 'large', 'M': 'medium', 'S': 'small'}[size.upper()]
        
        return {
            "filename": filename,
            "description": f"{product.title()} icon ({color}) for {background} backgrounds - {size_full.title()}",
            "layout": "icon",
            "color": "black" if color.lower() == 'blk' else "white",
            "background": background,
            "size": size_full,
            "use_cases": ["favicon", "app_icon", "small_spaces", "avatars"],
            "guidance": f"Perfect for tight spaces where you need just the {product.title()} symbol",
            "format": ext
        }
    
    # Logo pattern: Product-Logo_blk_v_L.png  
    logo_pattern = rf'{product.title()}-Logo_(\w+)_([hv])_([LMS])\.(\w+)'
    match = re.match(logo_pattern, filename, re.IGNORECASE)
    
    if match:
        color, layout_code, size, ext = match.groups()
        layout = 'horizontal' if layout_code.lower() == 'h' else 'vertical'
        background = 'light' if color.lower() == 'blk' else 'dark'
        size_full = {'L': 'large', 'M': 'medium', 'S': 'small'}[size.upper()]
        
        if layout == 'horizontal':
            use_cases = ["headers", "business_cards", "letterhead", "wide_banners"]
            guidance = f"Best for wide spaces - business cards, website headers, email signatures"
        else:  # vertical
            use_cases = ["tall_banners", "social_media_profile", "mobile_layout", "poster"]
            guidance = f"Perfect for tall/narrow spaces - social media profiles, mobile layouts"
        
        return {
            "filename": filename,
            "description": f"{product.title()} {layout} logo ({color}) for {background} backgrounds - {size_full.title()}",
            "layout": layout,
            "color": "black" if color.lower() == 'blk' else "white",
            "background": background,
            "size": size_full,
            "use_cases": use_cases,
            "guidance": guidance,
            "format": ext
        }
    
    # SVG logo pattern: Product_logo_h-blk.svg
    svg_logo_pattern = rf'{product.title()}_logo_([hv])-(\w+)\.(\w+)'
    match = re.match(svg_logo_pattern, filename, re.IGNORECASE)
    
    if match:
        layout_code, color, ext = match.groups()
        layout = 'horizontal' if layout_code.lower() == 'h' else 'vertical'
        background = 'light' if color.lower() == 'blk' else 'dark'
        
        return {
            "filename": filename,
            "description": f"{product.title()} {layout} logo ({color}) for {background} backgrounds - SVG",
            "layout": layout,
            "color": "black" if color.lower() == 'blk' else "white",
            "background": background,
            "size": "vector",
            "use_cases": ["scalable", "web", "print"],
            "guidance": f"Vector format - scales to any size perfectly",
            "format": ext
        }
    
    # SVG icon pattern: Product_icon_blk.svg
    svg_icon_pattern = rf'{product.title()}_icon_(\w+)\.(\w+)'
    match = re.match(svg_icon_pattern, filename, re.IGNORECASE)
    
    if match:
        color, ext = match.groups()
        background = 'light' if color.lower() == 'blk' else 'dark'
        
        return {
            "filename": filename,
            "description": f"{product.title()} icon ({color}) for {background} backgrounds - SVG",
            "layout": "icon",
            "color": "black" if color.lower() == 'blk' else "white",
            "background": background,
            "size": "vector",
            "use_cases": ["scalable", "favicon", "app_icon"],
            "guidance": f"Vector format - scales to any size perfectly",
            "format": ext
        }
    
    # Fallback - basic file info
    return {
        "filename": filename,
        "description": f"{product.title()} logo variant: {filename}",
        "layout": "unknown",
        "color": "unknown", 
        "background": "unknown",
        "size": "unknown",
        "use_cases": ["general"],
        "guidance": f"{product.title()} logo variant",
        "format": filename.split('.')[-1] if '.' in filename else "unknown"
    }
