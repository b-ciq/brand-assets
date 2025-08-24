# 🧹 Repository Cleanup Guide

**Files marked for removal** - These are development artifacts and duplicates that should be cleaned up:

---

## **Files to Remove:**

### **Obsolete Server Versions:**
- `ciq_brand_assets_cloud.py` - Failed cloud deployment attempt
- `enhanced_parser.py` - Development artifact  
- `generate_metadata_recursive.py` - Alternative version not used
- `test_server.py` - Test file

### **Outdated Documentation:**
- `CLOUD_DEPLOYMENT_READY.md` - Superseded by SUCCESS_SUMMARY.md
- `DISTRIBUTION_OPTIONS.md` - No longer relevant (cloud deployment working)
- `FASTMCP_CLOUD_SETUP.md` - Outdated deployment instructions
- `PHASE_1_2_COMPLETE.md` - Development phase doc

### **Development Artifacts:**
- `package.json` - Not needed for Python project
- `pyproject.toml` - Pip package setup (not currently used)
- `.DS_Store` - macOS system file

---

## **Files to Keep:**

### **Production Files:**
- ✅ `server.py` - **ACTIVE FastMCP Cloud server** (updated with correct logic)
- ✅ `ciq_brand_assets_fastmcp.py` - Local development server (still useful)
- ✅ `generate_metadata.py` - **Essential auto-discovery script**
- ✅ `requirements.txt` - Dependencies for cloud deployment

### **Essential Documentation:**
- ✅ `README.md` - Main project documentation
- ✅ `TEAM_SETUP.md` - **Essential for team onboarding**
- ✅ `SUCCESS_SUMMARY.md` - Final achievement summary
- ✅ `INSTALL.md` - Local installation instructions

### **Asset Structure:**
- ✅ All logo directories (`CIQ-logos/`, `Fuzzball-logos/`, etc.)
- ✅ `metadata/` directory - Auto-generated asset inventory
- ✅ `assets/` directory - Future organized structure
- ✅ `src/` directory - If contains useful code

---

## **How to Clean Up:**

### **Manual Cleanup (Recommended):**
```bash
# Navigate to repo
cd brand-assets

# Remove obsolete files
rm ciq_brand_assets_cloud.py
rm enhanced_parser.py  
rm generate_metadata_recursive.py
rm test_server.py
rm package.json
rm pyproject.toml
rm .DS_Store

# Remove outdated docs
rm CLOUD_DEPLOYMENT_READY.md
rm DISTRIBUTION_OPTIONS.md
rm FASTMCP_CLOUD_SETUP.md  
rm PHASE_1_2_COMPLETE.md

# Commit cleanup
git add .
git commit -m "Clean up repository - remove obsolete development files"
git push
```

---

## **After Cleanup Benefits:**

- ✅ **Cleaner repository** - Only essential files
- ✅ **Less confusion** - No duplicate/obsolete files
- ✅ **Easier maintenance** - Clear structure
- ✅ **Better team experience** - Only relevant documentation

---

## **Updated Structure After Cleanup:**

```
brand-assets/
├── server.py                    # 🔴 ACTIVE cloud server
├── ciq_brand_assets_fastmcp.py  # Local development server
├── generate_metadata.py         # 🔴 ESSENTIAL auto-discovery
├── requirements.txt             # Cloud dependencies
├── README.md                    # Main documentation  
├── TEAM_SETUP.md               # 🔴 ESSENTIAL team config
├── SUCCESS_SUMMARY.md          # Achievement summary
├── INSTALL.md                  # Local setup guide
├── metadata/                   # Auto-generated inventory
├── CIQ-logos/                  # Company brand assets
├── Fuzzball-logos/             # Product assets
├── Warewulf-Pro-logos/         # Product assets
├── Apptainer-logos/            # Product assets
├── Ascender-Pro-logos/         # Product assets
├── Bridge-logos/               # Product assets
├── RLC(X)-logos/               # RLC variants
└── CIQ-Support-logos/          # Support division
```

**Clean, focused, production-ready structure!** 🚀
