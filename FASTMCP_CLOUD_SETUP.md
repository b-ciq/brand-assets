# 🌐 FastMCP Cloud Deployment Guide

**Goal:** Zero-installation team access to CIQ Brand Assets MCP Server

---

## **📋 Prerequisites**

1. **GitHub account** with access to `b-ciq/brand-assets` repo
2. **FastMCP Cloud account** at [fastmcp.cloud](https://fastmcp.cloud)

---

## **🚀 Step-by-Step Cloud Setup**

### **Step 1: Access FastMCP Cloud**
1. Go to [fastmcp.cloud](https://fastmcp.cloud)
2. **Sign in with GitHub account**
3. **Create new project**

### **Step 2: Configure Project**
When creating the project, use these settings:

```
Name: ciq-brand-assets
Repository: b-ciq/brand-assets  
Entrypoint: ciq_brand_assets_cloud.py
Authentication: Disabled (for team access)
```

**Important:** Use `ciq_brand_assets_cloud.py` (not the local version) - this has the cloud-optimized transport settings.

### **Step 3: Deployment**
- FastMCP Cloud will **automatically deploy** from your `main` branch
- Your server will be available at: `https://ciq-brand-assets.fastmcp.app/mcp`
- **Redeploys automatically** when you push changes to main

---

## **👥 Team Configuration**

### **For Team Members (Zero Installation Required):**

**Claude Desktop Setup:**
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

**That's it!** No Python, no FastMCP, no local server needed.

### **Alternative: Direct URL Connection**
Some MCP clients support direct URLs:
```
https://ciq-brand-assets.fastmcp.app/mcp
```

---

## **🔧 Testing Your Cloud Deployment**

### **Test the Server Directly:**
```bash
curl https://ciq-brand-assets.fastmcp.app/mcp
```

### **Test with FastMCP Client:**
```python
from fastmcp import Client
import asyncio

async def test_cloud_server():
    client = Client("test-client")
    
    # Connect to your cloud server
    await client.connect("https://ciq-brand-assets.fastmcp.app/mcp")
    
    # Test tool call
    result = await client.call_tool("get_brand_asset", {
        "request": "CIQ logo for light background"
    })
    
    print("Result:", result)

# Run test
asyncio.run(test_cloud_server())
```

---

## **🎯 Benefits of Cloud Deployment**

### **For Your Team:**
- ✅ **Zero installation** - just add URL to Claude Desktop
- ✅ **Always up-to-date** - auto-deploys from main branch
- ✅ **Same great UX** - identical tool interface
- ✅ **Cross-platform** - works on any device with Claude

### **For You (Maintainer):**
- ✅ **Automatic deployment** - push to main = instant team update
- ✅ **PR previews** - test changes before deploying to team
- ✅ **No server management** - FastMCP Cloud handles infrastructure
- ✅ **Monitoring & logs** - FastMCP Cloud provides observability

---

## **🔄 Development Workflow**

### **Adding New Assets:**
```bash
# 1. Add logo files to appropriate directory
# 2. Regenerate metadata
python generate_metadata.py

# 3. Commit and push
git add .
git commit -m "Add new Warewulf logos"
git push origin main

# ✅ Team gets new assets automatically!
```

### **Adding New Products:**
```bash
# 1. Create new directory: NewProduct-logos/
# 2. Add logo files following naming convention  
# 3. Regenerate metadata
python generate_metadata.py

# 4. Commit and push
git add .
git commit -m "Add NewProduct logo support"
git push origin main

# ✅ Team gets new product automatically!
```

---

## **🚨 Troubleshooting**

### **If deployment fails:**
1. Check **FastMCP Cloud dashboard** for error logs
2. Verify `ciq_brand_assets_cloud.py` syntax
3. Ensure `requirements.txt` has correct dependencies

### **If team can't connect:**
1. Verify URL is accessible: `https://ciq-brand-assets.fastmcp.app/mcp`
2. Check Claude Desktop configuration JSON syntax
3. Restart Claude Desktop after config changes

### **If assets not loading:**
1. Check GitHub raw URLs are accessible
2. Verify `metadata/asset-inventory.json` is up-to-date
3. Run `python generate_metadata.py` and push updates

---

## **🎉 Next Steps**

1. **Configure FastMCP Cloud project** (Step 2 above)
2. **Test deployment** with curl or FastMCP client
3. **Share team instructions** (Claude Desktop config)
4. **Add new products** as needed using auto-discovery

**Result:** Your entire team gets **instant access** to 60+ brand assets through Claude with **zero technical setup required**! 🚀
