#!/usr/bin/env python3
"""
Test script for CIQ Brand Assets MCP Server
Run this to verify your server is working correctly before team deployment
"""

import sys

def test_server():
    """Test the FastMCP server functionality"""
    print("🧪 Testing CIQ Brand Assets MCP Server...")
    print("=" * 50)
    
    try:
        # Import the server
        from ciq_brand_assets_fastmcp import mcp, load_asset_data
        print("✅ Server imports successfully")
        
        # Test data loading (now sync function)
        success = load_asset_data()
        if success:
            print("✅ Asset metadata loads successfully")
        else:
            print("❌ Failed to load asset metadata")
            return False
        
        # Test tools are registered
        tools = list(mcp.get_tools().keys())
        expected_tools = ['get_brand_asset', 'list_all_assets', 'brand_guidelines']
        
        print(f"🔧 Registered tools: {tools}")
        
        for expected in expected_tools:
            if expected in tools:
                print(f"✅ Tool '{expected}' registered")
            else:
                print(f"❌ Tool '{expected}' missing")
                return False
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Server is ready for deployment.")
        print("\n📋 Next steps:")
        print("1. Run the server: /opt/homebrew/bin/python3.11 ciq_brand_assets_fastmcp.py")
        print("2. Connect to Claude Desktop (see README.md for instructions)")
        print("3. Test with your team: ask 'I need a logo for...'")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try: /opt/homebrew/bin/python3.11 -m pip install fastmcp requests")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("📦 Checking dependencies...")
    
    required = ['fastmcp', 'requests']
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
        print(f"/opt/homebrew/bin/python3.11 -m pip install {' '.join(missing)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 CIQ Brand Assets MCP Server Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Dependencies
    if not test_dependencies():
        all_passed = False
        print("\n❌ Dependency test failed - please install missing packages")
        return
    
    # Test 2: Server functionality
    print("\n" + "=" * 50)
    if not test_server():
        all_passed = False
    
    # Final results
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 SUCCESS! Your CIQ Brand Assets MCP Server is ready!")
        print("\n📖 Next: Run the server with:")
        print("/opt/homebrew/bin/python3.11 ciq_brand_assets_fastmcp.py")
    else:
        print("❌ Some tests failed - please fix issues before deployment")
        sys.exit(1)

if __name__ == "__main__":
    main()
