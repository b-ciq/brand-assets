#!/usr/bin/env python3
"""
FastMCP Cloud Deployment Trigger
Forces a refresh of the FastMCP Cloud deployment
"""

import json
import time
from pathlib import Path

def trigger_deployment():
    """Trigger FastMCP Cloud deployment by updating key files"""
    
    print("🚀 Triggering FastMCP Cloud Deployment...\n")
    
    # 1. Update server.py timestamp (touch the file)
    server_file = Path('server.py')
    if server_file.exists():
        # Add a comment with timestamp to force Git to see it as changed
        with open(server_file, 'r') as f:
            content = f.read()
        
        # Add/update deployment timestamp comment
        timestamp = int(time.time())
        deployment_comment = f"# Deployment trigger: {timestamp}\n"
        
        if "# Deployment trigger:" in content:
            # Replace existing timestamp
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "# Deployment trigger:" in line:
                    lines[i] = deployment_comment.strip()
                    break
            content = '\n'.join(lines)
        else:
            # Add timestamp at the top after the shebang
            lines = content.split('\n')
            if lines[0].startswith('#!'):
                lines.insert(1, deployment_comment.strip())
            else:
                lines.insert(0, deployment_comment.strip())
            content = '\n'.join(lines)
        
        with open(server_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated server.py with deployment timestamp: {timestamp}")
    else:
        print("❌ server.py not found!")
    
    # 2. Update package.json version to trigger deployment
    package_file = Path('package.json')
    if package_file.exists():
        with open(package_file, 'r') as f:
            package_data = json.load(f)
        
        # Increment patch version
        current_version = package_data.get('version', '1.0.0')
        version_parts = current_version.split('.')
        if len(version_parts) == 3:
            patch = int(version_parts[2]) + 1
            new_version = f"{version_parts[0]}.{version_parts[1]}.{patch}"
        else:
            new_version = "1.0.1"
        
        package_data['version'] = new_version
        package_data['description'] = f"CIQ Brand Assets MCP Server - Clean Structure v{new_version}"
        
        with open(package_file, 'w') as f:
            json.dump(package_data, f, indent=2)
        
        print(f"✅ Updated package.json version: {current_version} → {new_version}")
    
    # 3. Create deployment trigger file
    deployment_file = Path('.fastmcp-deploy')
    with open(deployment_file, 'w') as f:
        f.write(f"timestamp: {timestamp}\n")
        f.write(f"trigger: clean_structure_deployment\n")
        f.write(f"assets_cleaned: true\n")
        f.write(f"rlc_separated: true\n")
        f.write(f"metadata_updated: pending\n")
    
    print(f"✅ Created deployment trigger file: {deployment_file}")
    
    print(f"\n📋 **FastMCP Cloud Deployment Triggered:**")
    print(f"   🔄 server.py timestamp updated")
    print(f"   📦 package.json version bumped")  
    print(f"   🎯 Deployment trigger file created")
    
    print(f"\n🎯 **Next Steps:**")
    print(f"   1. git add . && git commit -m 'Trigger FastMCP Cloud deployment'")
    print(f"   2. git push origin main")
    print(f"   3. Wait 30-60 seconds for FastMCP Cloud to detect changes")
    print(f"   4. Test the system to verify new logic is active")

if __name__ == "__main__":
    trigger_deployment()
