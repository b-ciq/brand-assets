#!/usr/bin/env python3
"""
Test script for CIQ Brand Assets MCP Server
Run this to verify your server is working correctly before team deployment
"""

import asyncio
import sys
import subprocess

async def test_server():
    """Test the FastMCP server functionality"""
    print("🧪 Testing CIQ Brand Assets MCP Server...")
    print("=" * 50)
    
    try:
        # Import the server
        from ciq_brand_assets_fastmcp import mcp, load_asset_data
        print("✅ Server imports successfully")
        
        # Test data loading
        success = await load_asset_data()
        if success:
            print("✅ Asset metadata loads successfully")
        else:
            print("❌ Failed to load asset metadata")
            return False
        
        # Test tools are registered
        tools = list(mcp.get_tools().keys())
        expected_tools = ['get_brand_asset', 'list_all_assets', 'get_brand_guidelines']
        
        print(f"🔧 Registered tools: {tools}")
        
        for expected in expected_tools:
            if expected in tools:
                print(f"✅ Tool '{expected}' registered")
            else:
                print(f"❌ Tool '{expected}' missing")
                return False
        
        # Test resources
        resources = list(mcp.get_resources().keys())
        print(f"📚 Registered resources: {resources}")
        
        if 'ciq://metadata' in resources:
            print("✅ Metadata resource registered")
        else:
            print("❌ Metadata resource missing")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Server is ready for deployment.")
        print("\n📋 Next steps:")
        print("1. Install for Claude Desktop: fastmcp install ciq_brand_assets_fastmcp.py")
        print("2. Or add to Claude config manually (see README.md)")
        print("3. Test with your team: ask 'I need a logo for...'")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try: pip install fastmcp httpx")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("📦 Checking dependencies...")
    
    required = ['fastmcp', 'httpx']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} missing")
            missing.append(package)
    
    if missing:
        print(f"\n💡 Install missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def test_fastmcp_cli():
    """Test FastMCP CLI availability"""
    print("\n🖥️  Checking FastMCP CLI...")
    
    try:
        result = subprocess.run(['fastmcp', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FastMCP CLI available")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ FastMCP CLI not working")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ FastMCP CLI not found")
        print("💡 Install with: pip install fastmcp>=2.0.0")
        return False

async def main():
    """Run all tests"""
    print("🚀 CIQ Brand Assets MCP Server Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Dependencies
    if not test_dependencies():
        all_passed = False
        print("\n❌ Dependency test failed - please install missing packages")
        return
    
    # Test 2: FastMCP CLI
    cli_available = test_fastmcp_cli()
    if not cli_available:
        print("⚠️  CLI not available but server may still work")
    
    # Test 3: Server functionality
    print("\n" + "=" * 50)
    if not await test_server():
        all_passed = False
    
    # Final results
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 SUCCESS! Your CIQ Brand Assets MCP Server is ready!")
        print("\n📖 Check README.md for installation instructions")
        print("🔗 https://github.com/b-ciq/brand-assets/")
    else:
        print("❌ Some tests failed - please fix issues before deployment")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
