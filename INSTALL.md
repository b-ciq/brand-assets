# Installation Guide - CIQ Brand Assets MCP

## 🐍 FastMCP Version (Recommended - Easiest!)

**Super simple setup with visual interface:**

### Quick Install
1. **Download the Python file:** [`ciq_brand_assets_fastmcp.py`](https://raw.githubusercontent.com/b-ciq/brand-assets/main/ciq_brand_assets_fastmcp.py)
2. **Install dependencies:** `pip install fastmcp requests`
3. **Run the server:** `python ciq_brand_assets_fastmcp.py`
4. **Open FastMCP interface:** Visit the URL shown in terminal (usually `http://localhost:8000`)
5. **Click "Add to Claude Desktop"** → Done! 🎉

### What You Get
- ✅ **Visual setup interface** - no config file editing
- ✅ **One Python file** - easy to modify later  
- ✅ **Same smart logic** - identical brand recommendations
- ✅ **One-click connection** to Claude Desktop

---

## 🟢 Node.js Version (Advanced)

For developers who prefer Node.js or want package management:

### Local Installation
```bash
git clone https://github.com/b-ciq/brand-assets.git
cd brand-assets
npm install
```

### Claude Desktop Configuration
Add to `.claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "ciq-brand-assets": {
      "command": "node",
      "args": ["src/index.js"],
      "cwd": "/full/path/to/brand-assets"
    }
  }
}
```

---

## Usage Examples (Both Versions)

Once installed, you can ask Claude:

### Simple Requests
- "I need a CIQ logo"
- "Get me a logo for email signature"
- "Logo for PowerPoint footer"

### Specific Context
- "I need a logo for a colorful marketing flyer"
- "Small logo for a black and white magazine ad"  
- "Hero logo for our homepage"
- "Watermark for social media posts"

### The MCP Will:
1. **Ask clarifying questions** about background and context
2. **Apply design best practices** based on your answers
3. **Provide direct download links** to the perfect logo
4. **Include brand usage guidance** and clear space requirements

## Troubleshooting

### FastMCP Issues
- **Make sure Python and pip are installed**
- **Check terminal for the server URL** (usually localhost:8000)
- **Restart Claude Desktop** after adding via FastMCP interface

### Node.js Issues
- **Make sure Node.js is installed** (version 18+)
- **Use full absolute path** in cwd setting
- **Restart Claude Desktop** after config changes
- **Check for MCP server indicators** at bottom of chat input

## What Makes This Smart

Both versions implement professional design decision-making:
- **When in doubt → defaults to neutral** (safe choice)
- **Colorful designs → recommends neutral** (won't compete) 
- **Minimal designs + ads → offers green** (helps logo pop)
- **Main/hero elements → always two-color** (maximum brand recognition)

## For Your Team

**FastMCP approach:**
- Share the Python file + simple install instructions
- Everyone gets the same visual setup experience
- No JSON config file editing needed

**Node.js approach:**  
- Professional package structure
- Traditional MCP setup
- More familiar to developers

---

*Built for the CIQ team with ❤️ by Design*
