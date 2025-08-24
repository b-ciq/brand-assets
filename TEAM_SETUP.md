# 👥 Team Setup Instructions - WORKING VERSION

**✅ CONFIRMED WORKING** - Add this to your Claude Desktop configuration

---

## **Claude Desktop Configuration**

Add this to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "ciq-brand-assets": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://brand-asset-server.fastmcp.app/mcp"
      ]
    }
  }
}
```

**✅ CONFIRMED: This configuration works!**

---

## **📍 Config File Locations**

### **macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### **Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

---

## **🎯 How to Use**

Once configured, just ask Claude:

- *"I need a CIQ logo"*
- *"Fuzzball symbol for dark background"*  
- *"Apptainer logo"*
- *"Show me all available brand assets"*
- *"What are the brand guidelines?"*
- *"Warewulf logo for light background"*

Claude will guide you through the best options automatically!

---

## **Available Products**

- **CIQ** - Company logos (1-color, 2-color)
- **Fuzzball** - Container platform logos
- **Apptainer** - Container platform logos  
- **Warewulf-Pro** - HPC cluster management
- **Ascender-Pro** - Enterprise tools
- **Bridge** - Infrastructure solutions
- **RLC(X)** - Rocky Linux Commercial
- **CIQ-Support** - Support division logos

## **🔧 Troubleshooting**

**If it doesn't work:**
1. **Restart Claude Desktop** after adding config (Command/Ctrl + R)
2. **Check JSON syntax** (use a JSON validator)
3. **Verify file location** (see paths above)
4. **Ensure Node.js 18+** is installed

**Still having issues?** Contact the admin who set up the server.

---

## **🎉 That's It!**

You now have **instant access** to all CIQ brand assets through Claude with **zero technical setup**! 🚀

**✅ No Python installation required**  
**✅ No FastMCP installation required**  
**✅ No local server management required**  
**✅ Just one config file edit + restart Claude Desktop**

---

## **🎯 Example Usage:**

After setup, you can have conversations like:

**You:** "I need a logo for our new product brochure"  
**Claude:** "What background will this logo be on - light or dark?"  
**You:** "Light background, and it's the main visual element"  
**Claude:** "Perfect! Here's your CIQ 2-color logo: [download link]"

**The magic of natural language brand asset access!** ⚡
