# Installation Guide - CIQ Brand Assets MCP

## Quick Install (Recommended)

Add this to your `.claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "ciq-brand-assets": {
      "command": "npx",
      "args": ["-y", "https://github.com/b-ciq/brand-assets.git"],
      "cwd": "/tmp"
    }
  }
}
```

## Alternative Install Methods

### Method 1: Direct from GitHub
```json
"ciq-brand-assets": {
  "command": "node", 
  "args": ["src/index.js"],
  "cwd": "/path/to/cloned/brand-assets"
}
```

### Method 2: Local Development
```bash
git clone https://github.com/b-ciq/brand-assets.git
cd brand-assets
npm install
```

Then add to Claude Desktop config:
```json
"ciq-brand-assets": {
  "command": "node",
  "args": ["src/index.js"], 
  "cwd": "/full/path/to/brand-assets"
}
```

## Usage Examples

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

- **Make sure Claude Desktop is restarted** after adding the configuration
- **Check for MCP server indicators** at the bottom of chat input
- **All logo files are accessible** via direct GitHub raw URLs
- **No authentication needed** for team members - they just use Claude

## What Makes This Smart

The MCP implements professional design decision-making:
- **When in doubt → defaults to neutral** (safe choice)
- **Colorful designs → recommends neutral** (won't compete) 
- **Minimal designs + ads → offers green** (helps logo pop)
- **Main/hero elements → always two-color** (maximum brand recognition)

---

*Built for the CIQ team with ❤️ by Design*
