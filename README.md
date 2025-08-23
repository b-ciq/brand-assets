# CIQ Brand Assets MCP Server

[![FastMCP 2.0](https://img.shields.io/badge/FastMCP-2.0-blue.svg)](https://gofastmcp.com/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Intelligent brand asset delivery for your CIQ design team** - Get the perfect logo recommendation through natural language conversation with Claude!

## 🚀 Quick Start

### Installation

1. **Install FastMCP 2.0** (recommended with uv):
```bash
uv add fastmcp>=2.0.0 httpx
```

Or with pip:
```bash
pip install -r requirements.txt
```

2. **Test the server**:
```bash
python ciq_brand_assets_fastmcp.py
```

3. **Connect to Claude** (see installation guide below)

## 🎯 What This Server Does

- **Smart Logo Recommendations**: Just describe what you need - no complex decision trees
- **Natural Language Interface**: "I need a logo for an email signature"
- **Context-Aware**: Understands colorful vs minimal designs, main vs supporting elements
- **Brand Guidelines**: Built-in brand compliance and usage rules

## 💬 Example Conversations

```
You: "I need a logo for our homepage header"

Server: "What background will this logo be placed on?
• Light background (white, light gray, light colors)
• Dark background (black, dark gray, dark colors)"

You: "Light background"

Server: "For light backgrounds, is this logo the main element or supporting element?
🌟 Main - Logo is the hero/star (recommended for homepage headers)
🏷️ Supporting - Logo is secondary/background"

You: "Main element"

Server: "✅ Perfect! Here's your CIQ logo:
🎨 Two color (neutral + green) logo for light backgrounds
📎 Download: [direct GitHub link]
💡 Why: Two-color version provides maximum brand recognition for main design elements"
```

## 🧠 Smart Decision Logic

The server implements your design team's decision logic:

- **Main elements** (hero/star) → **Always 2-color** for maximum brand recognition
- **Supporting elements** → **1-color neutral** (safe default)
- **Colorful/busy designs** → **1-color neutral** (won't compete)
- **Minimal + advertising** → **Green version** (helps logo pop)
- **When in doubt** → **Neutral** (safest choice)

## 🛠 Available Tools

### `get_brand_asset`
Get intelligent logo recommendations based on context
- Natural language requests
- Smart clarifying questions
- Context-aware recommendations

### `list_all_assets`
Browse all available logos with direct download links

### `get_brand_guidelines`
Access CIQ brand guidelines and usage specifications

## 📁 Assets Available

- **CIQ-Logo-1color-light.png** - Neutral logo for light backgrounds
- **CIQ-Logo-1color-dark.png** - Neutral logo for dark backgrounds  
- **CIQ-Logo-2color-light.png** - Two-color logo for light backgrounds
- **CIQ-Logo-2color-dark.png** - Two-color logo for dark backgrounds
- **CIQ-Logo-green-light.png** - Green accent for light backgrounds
- **CIQ-Logo-green-dark.png** - Green accent for dark backgrounds

All assets include:
- Direct GitHub raw URLs for immediate download
- Usage guidelines and context recommendations
- Brand compliance information

## 🔧 Installation for Claude Desktop

### Method 1: FastMCP CLI (Recommended)
```bash
# Install globally
fastmcp install ciq_brand_assets_fastmcp.py

# Or for development
fastmcp dev ciq_brand_assets_fastmcp.py
```

### Method 2: Manual Configuration

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ciq-brand-assets": {
      "command": "python",
      "args": ["/path/to/ciq_brand_assets_fastmcp.py"],
      "env": {}
    }
  }
}
```

## 🔧 Installation for Cursor

```bash
# Install globally
fastmcp install ciq_brand_assets_fastmcp.py --cursor

# Or add to Cursor settings manually
```

## 🧪 Testing

Test your server with the FastMCP client:

```python
from fastmcp.client import FastMCPClient

async def test_server():
    client = FastMCPClient()
    await client.connect("stdio", ["python", "ciq_brand_assets_fastmcp.py"])
    
    # Test the smart recommendation
    result = await client.call_tool("get_brand_asset", {
        "request": "I need a logo for an email signature",
        "background": "light", 
        "element_type": "supporting"
    })
    
    print(result)
```

## 🎨 Design Team Workflow

1. **Team members ask in natural language**: "I need a logo for..."
2. **Server asks smart questions**: background type, element role, design context
3. **Get instant recommendations**: perfect logo with reasoning
4. **Direct download links**: immediate access to assets
5. **Brand compliance**: automatic guidelines and usage rules

## 📊 Usage Analytics

The server tracks:
- Most requested logo types
- Common use cases
- Design contexts
- Brand guideline compliance

## 🔄 Updates & Maintenance

- **Auto-updating**: Server fetches latest metadata from GitHub
- **Asset additions**: Add new logos to `/CIQ-logos/` and update metadata
- **Logic updates**: Modify decision logic in `asset-inventory.json`
- **Simple maintenance**: Pure Python, easy to modify

## 🆘 Troubleshooting

**Server won't start?**
```bash
python --version  # Ensure Python 3.8+
pip install fastmcp httpx  # Install dependencies
python ciq_brand_assets_fastmcp.py  # Test directly
```

**Claude can't find server?**
- Check your `claude_desktop_config.json` file path
- Restart Claude Desktop after config changes
- Test server runs independently first

**Wrong logo recommendations?**
- Provide more context in your request
- Use the `design_context` parameter
- Check the decision logic in `metadata/asset-inventory.json`

## 🤝 Team Adoption

**For your 20-person team:**
- Share this repo link
- Install via FastMCP CLI for easy setup  
- Standardize on natural language requests
- Reference brand guidelines tool for compliance

## 📈 Future Enhancements

- [ ] Usage analytics dashboard
- [ ] Custom brand asset categories  
- [ ] Integration with design tools
- [ ] Batch logo processing
- [ ] Advanced context detection

---

**Built with ❤️ using FastMCP 2.0** | **30 years of UX design experience** | **Copy/paste friendly for easy team adoption**
