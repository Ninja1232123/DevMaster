# DevMaster - Unified Developer Toolkit

**One CLI to rule them all.** 🎯

DevMaster orchestrates all your developer tools in one unified interface. Stop switching between tools - let DevMaster combine their powers!

## 🚀 Quick Start

```bash
# Install DevMaster
pip install -e devmaster

# Check what's available
devmaster status

# Initialize all tools in your project
devmaster init

# Start using workflows
devmaster analyze
```

## 🎯 What is DevMaster?

DevMaster is a **meta-CLI** that combines 5 powerful developer tools:

- 🐛 **AI Debug Companion** - Auto-fix errors with AI
- 📖 **DevNarrative** - Git history as readable stories
- 🏺 **CodeArchaeology** - Analyze code evolution and find technical debt
- 🔍 **CodeSeek** - Semantic code search with natural language
- 🧠 **DevKnowledge** - Personal knowledge graph for developers

Instead of learning 5 different CLIs, learn one: `devmaster`

## 📋 Commands

### Setup & Status

```bash
# Initialize all tools at once
devmaster init

# Check what tools are installed and ready
devmaster status

# Install all tools
devmaster install
```

### Workflows

```bash
# Analyze codebase for technical debt
devmaster analyze

# Generate weekly development report
devmaster report
devmaster report --export report.md

# Search everywhere (code + knowledge)
devmaster search "authentication"
devmaster search "database connection"

# Debug with AI assistance
devmaster debug script.py
devmaster debug script.py --fix

# Show available workflows
devmaster workflows
```

## 🎨 Workflows Explained

### `devmaster analyze`

**Combines:** CodeArchaeology + CodeSeek

**What it does:**
1. Finds code hotspots (frequently changed files = risk)
2. Analyzes file coupling (files that change together)
3. Identifies technical debt areas
4. Shows you where to focus refactoring efforts

**Example output:**
```
🔬 Analyzing codebase...

Step 1: Finding code hotspots...
🔥 Code Hotspot Heatmap
🔴 src/auth/login.py          ██████████████████ 25 changes
🟡 src/api/endpoints.py       ███████████ 15 changes
🟢 src/utils/helper.py        █████ 8 changes

Step 2: Analyzing file coupling...
🔗 Temporal Coupling Graph
src/auth/login.py ═══════ src/api/endpoints.py (STRONG 0.85)

✅ Analysis complete!
```

---

### `devmaster report`

**Combines:** DevNarrative + CodeArchaeology

**What it does:**
1. Generates narrative from your week's commits
2. Shows code health metrics
3. Identifies trends and patterns
4. Creates shareable report (text/markdown/html)

**Use cases:**
- Weekly standup reports
- Manager updates
- Project retrospectives
- Team communication

**Example:**
```bash
devmaster report --export weekly-report.md
```

---

### `devmaster search <query>`

**Combines:** CodeSeek + DevKnowledge

**What it does:**
1. Searches your code semantically
2. Searches your knowledge graph
3. Returns results from both in one view

**Example:**
```bash
devmaster search "authentication logic"

🔍 Searching for: authentication logic

📝 Code Results:
  src/auth/login.py:45 - Login authentication function
  src/api/middleware.py:20 - Token authentication middleware

🧠 Knowledge Results:
  Note: "Authentication Flow" - How JWT tokens work in our system
  Code Doc: src/auth/README.md - Authentication implementation guide
```

---

### `devmaster debug <script>`

**Combines:** AI Debug Companion + AI Provider

**What it does:**
1. Runs your script
2. Detects errors
3. Generates fixes
4. Optionally applies them automatically

**Example:**
```bash
devmaster debug script.py --fix

🐛 Debugging: script.py

❌ [error] KeyError: 'email'

🔧 Available fixes:
  Fix 1: Change dict['email'] to dict.get('email', None)
  Confidence: 90%

✅ Applied fix 1
```

---

## 🎓 Workflow Examples

### Daily Development

```bash
# Morning: Check what happened yesterday
devmaster report

# Find the code you need
devmaster search "payment processing"

# Debug an issue
devmaster debug app.py --fix
```

### Weekly Review

```bash
# Generate comprehensive weekly report
devmaster report --export weekly.md

# Analyze code health
devmaster analyze

# Check technical debt
devmaster status
```

### Code Exploration

```bash
# When joining a new project
devmaster init
devmaster analyze
devmaster search "main entry point"
```

### Refactoring Session

```bash
# Find hotspots
devmaster analyze

# Search for usage
devmaster search "legacy function"

# Make changes and track
devmaster report
```

---

## 🔧 Configuration

DevMaster inherits configuration from individual tools:

- **AI Provider**: `~/.devtools-ai.json` (see AI_PROVIDER_GUIDE.md)
- **Git**: Uses repository's git config
- **Tools**: Each tool has its own config

---

## 💡 Tips & Tricks

### 1. Alias for Speed

```bash
# Add to your shell profile
alias dm='devmaster'
alias dma='devmaster analyze'
alias dmr='devmaster report'
alias dms='devmaster search'
```

### 2. Daily Workflows

Create shell scripts for common workflows:

```bash
#!/bin/bash
# morning-check.sh
devmaster report
devmaster analyze
```

### 3. CI/CD Integration

```yaml
# .github/workflows/code-health.yml
- name: Check Code Health
  run: |
    devmaster analyze
    devmaster report --export code-health.md
```

### 4. Team Reports

```bash
# Generate team report weekly
devmaster report --export reports/week-$(date +%Y-%m-%d).md
git add reports/
git commit -m "Weekly report"
git push
```

---

## 🌟 Why DevMaster?

### Before DevMaster:
```bash
# Check code health
cd codearchaeology && codearch hotspots && cd ..

# Generate narrative
cd devnarrative && devnarrative week && cd ..

# Search code
cd codeseek && codeseek find "auth" && cd ..

# Debug
cd ai-debug-companion && debug-companion exec -- python script.py && cd ..
```

### With DevMaster:
```bash
devmaster analyze
devmaster report
devmaster search "auth"
devmaster debug script.py
```

**Result:** 10x faster workflow, unified experience!

---

## 📊 Status Dashboard

```bash
devmaster status
```

Shows:
- Which tools are installed
- Which tools are configured
- Tool versions
- Quick health check

Example output:
```
📊 DevMaster Status Dashboard

Tool                    Status        Info
─────────────────────────────────────────────────────
🐛 AI Debug Companion  ✅ Ready      Auto-fix errors with AI
📖 DevNarrative         ✅ Ready      Git history as stories
🏺 CodeArchaeology      ✅ Ready      Analyze code evolution
🔍 CodeSeek            ⏳ Not installed
🧠 DevKnowledge        ⏳ Not installed

🎉 All core tools ready! (3/5)
```

---

## 🚀 Getting Started

### Step 1: Install DevMaster

```bash
cd devmaster
pip install -e .
```

### Step 2: Check Status

```bash
devmaster status
```

### Step 3: Install Missing Tools

```bash
devmaster install
```

Or install individually:
```bash
pip install -e ../ai-debug-companion
pip install -e ../devnarrative
pip install -e ../codearchaeology
```

### Step 4: Initialize Your Project

```bash
cd your-project
devmaster init
```

### Step 5: Start Using Workflows!

```bash
devmaster analyze
devmaster search "your query"
devmaster report
```

---

## 🎯 Philosophy

DevMaster follows these principles:

1. **Integration over Isolation** - Tools are more powerful together
2. **Workflow over Commands** - Focus on what you want to do, not which tool to use
3. **Simple over Complex** - One command beats five
4. **Smart Defaults** - Works without configuration
5. **Progressive Enhancement** - Start simple, add features as needed

---

## 🤝 Integration with Other Tools

DevMaster plays well with:

- **Git**: All tools respect git ignore and repository structure
- **CI/CD**: Use in GitHub Actions, GitLab CI, etc.
- **Editors**: Works alongside VS Code, Vim, etc.
- **Package Managers**: Standard pip installation

---

## 📚 Learn More

- [AI Provider Guide](../AI_PROVIDER_GUIDE.md) - Configure AI for intelligent fixes
- [Getting Started](../GETTING_STARTED.md) - Install and use individual tools
- [Masterpiece Roadmap](../MASTERPIECE_ROADMAP.md) - Future plans

---

## ❓ FAQ

**Q: Do I need all 5 tools installed?**
A: No! DevMaster works with whichever tools you have. Core tools (AI Debug Companion, DevNarrative, CodeArchaeology) are lightweight.

**Q: Can I use individual tools without DevMaster?**
A: Yes! Each tool works standalone. DevMaster just makes them easier to use together.

**Q: What about large projects?**
A: CodeSeek and DevKnowledge can handle large projects, but initial indexing takes time.

**Q: Does it work on Windows?**
A: Yes! All tools are cross-platform (Python-based).

**Q: What about private code?**
A: Use Ollama (local AI) for complete privacy. No code leaves your machine.

---

## 🎉 You're Ready!

Start exploring your codebase with:
```bash
devmaster analyze
```

Happy coding! 🚀
