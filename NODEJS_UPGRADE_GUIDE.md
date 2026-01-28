# Node.js Upgrade Guide

## What's Needed

Vite 7.3.1 requires **Node.js 20.19+** or **22.12+**

## Compatibility Check ✅

All dependencies are compatible with Node.js 20.19+ and 22.12+:

| Package | Version | Node.js Support | Status |
|---------|---------|-----------------|--------|
| Vite | 7.3.1 | 20.19+ or 22.12+ | ✅ Requires update |
| React | 18.2.0 | 14.0+ | ✅ Compatible |
| TypeScript | 5.0 | 12.0+ | ✅ Compatible |
| React Router | 6.11.0 | 12.0+ | ✅ Compatible |
| Axios | 1.4.0 | 14.0+ | ✅ Compatible |
| Lucide React | 0.263.0 | 12.0+ | ✅ Compatible |
| Recharts | 2.8.0 | 12.0+ | ✅ Compatible |

**Result: No dependency conflicts. Safe to upgrade.** ✅

## How to Upgrade Node.js

### Option 1: Using NVM (Node Version Manager) - Recommended

**Windows (PowerShell):**
```powershell
# If using nvm-windows
nvm install 22.12.0
nvm use 22.12.0
```

**Mac/Linux:**
```bash
nvm install 22.12.0
nvm use 22.12.0
```

### Option 2: Direct Download

Visit https://nodejs.org/ and download:
- **Latest LTS**: 22.12.0+ (recommended)
- **Current**: 23.0.0+

Then restart your terminal.

### Option 3: Using Package Manager

**Windows (Chocolatey):**
```powershell
choco upgrade nodejs
```

**Mac (Homebrew):**
```bash
brew upgrade node
```

**Ubuntu/Debian:**
```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## Verification

After upgrading, verify in a new terminal:

```bash
node --version
# Should show: v22.12.0 or v20.19.0+

npm --version
# Should show: 10.0.0+
```

## After Upgrading

Clear npm cache and reinstall dependencies:

```bash
cd frontend

# Clear cache
npm cache clean --force

# Reinstall dependencies (optional but recommended)
npm install

# Verify build works
npm run build
```

## package.json Update

The frontend `package.json` has been updated with:

```json
{
  "engines": {
    "node": ">=20.19.0 || >=22.12.0",
    "npm": ">=10.0.0"
  }
}
```

This explicitly documents the required Node.js version.

## Expected Behavior After Upgrade

✅ `npm run dev` - Development server works
✅ `npm run build` - Build completes without errors
✅ `npm run preview` - Preview server works
✅ `npm run lint` - Type checking passes

## Troubleshooting

**Error: "vite requires Node.js version..."**
- Ensure you've upgraded Node.js
- Restart terminal/PowerShell
- Verify with `node --version`

**Error: "npm ERR! peer dep missing"**
- Run `npm install`
- This is normal after Node.js upgrade

**Build still fails after upgrade**
- Delete `node_modules`: `rm -r node_modules`
- Delete `package-lock.json`: `rm package-lock.json`
- Reinstall: `npm install`
- Build: `npm run build`

## Summary

No code changes needed. Simply upgrade Node.js to 20.19+ or 22.12+, and everything will work.

Recommended: Use Node.js 22.12.0 LTS for best long-term support.
