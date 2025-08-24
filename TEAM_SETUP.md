# 👥 Team Setup Instructions

**For CIQ team members:** Add this to your Claude Desktop configuration

---

## **Claude Desktop Configuration**

Add this to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "ciq-brand-assets": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-http",
        "https://ciq-brand-assets.fastmcp.app/mcp"
      ]
    }
  }
}
```

**That's it!** No installation required.

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
1. **Restart Claude Desktop** after adding config
2. **Check JSON syntax** (use a JSON validator)
3. **Verify file location** (see paths above)

**Still having issues?** Contact the admin who set up the server.

---

## **🎉 That's It!**

You now have **instant access** to all CIQ brand assets through Claude with **zero technical setup**! 🚀
