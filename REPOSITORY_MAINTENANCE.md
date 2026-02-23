# Repository Maintenance Checklist

## Git Repository Health

### ✅ Essential Files Present
- [ ] `.gitignore` - Properly configured to exclude build artifacts
- [ ] `README.md` - Comprehensive project documentation
- [ ] `CONTRIBUTING.md` - Contributor guidelines
- [ ] `LICENSE` - MIT license file
- [ ] `.git/` - Git repository initialized

### 📁 Proper File Organization
- [ ] Source code in `src/` directory
- [ ] Build scripts in root directory
- [ ] Documentation files in root
- [ ] No build artifacts committed to repository

## Build System Verification

### 🛠️ Build Scripts Available
- [ ] `build.py` - Main build configuration
- [ ] `build_enhanced.py` - Enhanced cross-platform builds
- [ ] `build_wrapper.py` - Easy build interface
- [ ] Platform-specific scripts in `build_dist/`

### 🎯 Build Targets Working
- [ ] Windows 32-bit/64-bit portable builds
- [ ] Windows installer builds
- [ ] Linux 32-bit/64-bit portable builds
- [ ] Linux installer builds
- [ ] macOS portable builds
- [ ] macOS installer builds
- [ ] Android APK builds

## Code Quality

### 🧹 Clean Repository State
- [ ] No untracked build artifacts
- [ ] No cached Python files committed
- [ ] No IDE configuration files committed
- [ ] No OS-specific files committed

### 📊 Git Status Check
```bash
# Check repository status
git status

# Check ignored files
git status --ignored

# Verify .gitignore effectiveness
python maintain_gitignore.py
```

## Regular Maintenance Tasks

### Weekly
- [ ] Run `python maintain_gitignore.py` to verify exclusions
- [ ] Check for untracked files: `git status --porcelain`
- [ ] Review `.gitignore` for missing patterns

### Monthly
- [ ] Clean repository: `git gc`
- [ ] Update dependencies in requirements files
- [ ] Review and update documentation

### Before Releases
- [ ] Ensure all build targets work
- [ ] Verify no sensitive files are tracked
- [ ] Check repository size and clean if needed
- [ ] Update version numbers in documentation

## Troubleshooting

### Common Issues

**Unwanted files being tracked:**
```bash
# Stop tracking a file but keep it locally
git rm --cached filename

# Remove file from all git history (dangerous!)
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch filename' \
--prune-empty --tag-name-filter cat -- --all
```

**Repository cleanup:**
```bash
# Remove untracked files (be careful!)
git clean -fd

# Remove untracked files and ignored files
git clean -fdx

# Preview what would be removed
git clean -fdxn
```

**Reset .gitignore effects:**
```bash
# Refresh git's ignore cache
git rm -r --cached .
git add .
```

### Emergency Recovery
If repository becomes corrupted:
1. Backup current work
2. Clone fresh repository
3. Copy only necessary files
4. Re-initialize build system
5. Restore from backup selectively

## Best Practices

1. **Never commit build artifacts** - Always use `.gitignore`
2. **Regular .gitignore maintenance** - Run the maintenance script monthly
3. **Clean commits** - Keep commits focused and meaningful
4. **Branch strategy** - Use feature branches for development
5. **Documentation updates** - Keep README and docs current with code changes

---
*Last updated: [Current Date]*
*Maintainer: [Your Name]*