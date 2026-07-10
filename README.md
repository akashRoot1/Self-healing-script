Here is your professional `README.md` for your repo `Self-healing-script`. Just create a new file `README.md` in your project root and paste this:

```markdown
# 🤖 Self-Healing Test Automation - Playwright + Ollama

> When UI changes, your tests don't fail. A self-healing framework that fixes broken locators using local AI.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-green)](https://playwright.dev)
[![Ollama](https://img.shields.io/badge/AI-Ollama%20llama3.2-orange)](https://ollama.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

### 🚨 The Problem
Every QA faces this:
```python
page.locator("button:text-is('Print')").click() # Works today
# Tomorrow dev changes Print -> Publish / Save & Print / Prints
# Test Fails ❌
```
Brittle locators = Flaky tests = Wasted time.

### 💡 The Solution
This framework heals itself:

1.  **Try** original locator
2.  If fails → **Extract** all visible buttons/inputs from page
3.  **Ask Ollama (llama3.2 local LLM)** -> "Which element matches intent: `the main print/publish button`?"
4.  If Ollama is down → **Fuzzy fallback** using keyword + difflib matching
5.  **Heal, Click, and Cache** it for next run

**100% offline, free, private. No OpenAI API key needed.**

### 🎬 Live Demo App
I built a demo Flask website to prove it. The primary button text changes on every refresh: `Print, Prints, Publish, Save & Print, Print Now, Output...`

Old locator fails. Healed locator passes every time.

### 🏗️ Project Structure
```
Self-healing-script/
├── app.py              # Demo website - button text changes randomly
├── healer.py           # Core self-healing logic (Ollama + fuzzy)
├── test_simple.py      # Simple test to show healing
├── requirements.txt    # playwright, ollama, flask
├── .gitignore
└── README.md
```

### ⚙️ Installation

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/Self-healing-script.git
cd Self-healing-script
```

**2. Install Python dependencies**
```bash
pip install -r requirements.txt
playwright install chromium
```

**3. Install Ollama (Local AI)**
Download from: https://ollama.com/download

```bash
ollama pull llama3.2
ollama serve
```
Leave `ollama serve` running in one terminal.

### 🚀 How to Run

You need **2 terminals**.

**Terminal 1 - Start Demo Website:**
```bash
python app.py
```
Website will run at `http://localhost:5000`

**Terminal 2 - Run Self-Healing Test:**
```bash
python -u test_simple.py
```

### ✅ Expected Output

**Before Healing (Original Locator Fails):**
```
Current button text on site is: 'Save & Print'
Trying to heal locator: button:text-is('Print')
[INFO] ⚠️  Original locator failed: button:text-is('Print')
```

**After Healing (AI Fixes It):**
```
[INFO] Found 6 interactive elements on page
[INFO] LLM healed → get_by_test_id("btn-primary")
[INFO] ✅ Clicked: the main print/publish button
 SUCCESS - Healed and clicked!
Healed 1 locator(s), cache size: 1
```
And a real Chrome browser will open (`headless=False`) and click the button even though the text is `Save & Print` not `Print`.

### 🧠 How Healing Works
```
Original Locator
      |
      v
[ Try Original ] --success--> Click ✅
      | fail
      v
[ Check Cache ] --hit--> Click ✅
      | miss
      v
[ Ask Ollama LLM with page candidates ] --found--> Heal & Click ✅
      | fail
      v
[ Fuzzy Logic (difflib keyword match) ] --found--> Heal & Click ✅
      | fail
      v
  Failed ❌
```

### 🔧 Core API

```python
from healer import SelfHealer

healer = SelfHealer(model="llama3.2")

# Instead of: page.locator("button:text-is('Print')").click()
# Use:
await healer.smart_click(page, "button:text-is('Print')", "the main print/publish button")
await healer.smart_fill(page, "#username", "the username field", "testuser")
```

### 💻 Tech Stack
- **Python 3.11**
- **Playwright** - Browser automation
- **Ollama + llama3.2** - Local LLM for healing
- **Flask** - Demo website
- **Difflib** - Fuzzy fallback when Ollama is offline

### 🗺️ Roadmap
- [ ] Persistent cache in JSON file
- [ ] Vision healing with screenshot + llava
- [ ] Selenium version
- [ ] Auto-update test files with healed locators

### 🤝 Contributing
PRs welcome!

### 📄 License
MIT License

### 👤 Author
Built by you for robust test automation portfolios.

---
⭐ Star this repo if it helped you!
```

**Don't forget to replace `YOUR_USERNAME` with your GitHub username in 2 places.**

After pasting, in PyCharm terminal:
```powershell
git add README.md
git commit -m "docs: add professional readme"
git push origin main
```
