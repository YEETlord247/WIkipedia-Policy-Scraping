# Wikipedia Talk Page Policy Analyzer

A web application that analyzes Wikipedia talk page discussions and identifies policy, guideline, and essay mentions by directly extracting Wikipedia links from the discussion content.

## 🌟 Features

* **📄 Two-Column Layout**: Discussion content on the left, policy mentions on the right
* **🔍 Direct Link Extraction**: Scans discussions for Wikipedia policy shortcuts (WP:NPOV, WP:RS, etc.)
* **📍 Section-Specific Analysis**: Analyzes specific discussion sections using URL anchors
* **🎨 Modern UI**: Beautiful, responsive design with smooth scrolling
* **⚡ Fast & Accurate**: No AI guessing - directly extracts actual policy links

## 🏗️ Architecture

The project is organized into clean, modular components:

```
Wikipedia/
├── main.py                  # Flask application & routes
├── scraper.py               # Wikipedia page scraping & section extraction
├── policy_extractor.py      # Direct policy/guideline/essay link extraction
├── analyzer.py              # OpenAI integration (optional)
├── prompts.py               # AI prompt templates (optional)
├── static/
│   └── style.css           # Frontend styling
├── templates/
│   └── index.html          # Frontend HTML
├── requirements.txt         # Python dependencies
└── setup.sh                # Setup script
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YEETlord247/WIkipedia-Policy-Scraping.git
cd WIkipedia-Policy-Scraping
```

### 2. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, for OpenAI features)
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 3. Run the Application

```bash
python main.py
```

The application will start on **http://127.0.0.1:5001**

## 💡 Usage

1. Open your web browser and navigate to `http://127.0.0.1:5001`
2. Paste a Wikipedia talk page URL with a section anchor:
   ```
   https://en.wikipedia.org/wiki/Talk:Article#Section_Name
   ```
3. Click "Analyze Discussion"
4. View the discussion on the left and identified policies on the right

### Example URLs

* `https://en.wikipedia.org/wiki/Talk:List_of_2022_FIFA_World_Cup_controversies#RfC_self-published_cartoon`
* `https://en.wikipedia.org/wiki/Talk:Dinosaur#Taxonomy`
* `https://en.wikipedia.org/wiki/Talk:Climate_change#Recent_edits`

## 🔧 How It Works

1. **URL Parsing**: Extracts the section anchor from the provided URL
2. **Web Scraping**: Fetches the Wikipedia talk page using BeautifulSoup
3. **Section Extraction**: Isolates the specific discussion section
4. **Policy Detection**: Scans for Wikipedia policy/guideline links:
   - HTML links to `wikipedia.org/wiki/Wikipedia:*`
   - Text shortcuts like `WP:NPOV`, `WP:RS`, `WP:UNDUE`
5. **Categorization**: Classifies each into:
   - **🔴 Policies**: Mandatory rules (NPOV, BLP, NOTCENSORED)
   - **🟡 Guidelines**: Best practices (RS, UNDUE, MOS)
   - **🔵 Essays**: Opinion pieces (IAR, COMMON, DEADLINE)

## 📋 Requirements

* Python 3.7+
* Internet connection

## 📦 Dependencies

* **Flask**: Web framework
* **BeautifulSoup4**: Web scraping
* **Requests**: HTTP library
* **lxml**: HTML/XML parser
* **python-dotenv**: Environment variable management
* **openai** (optional): For AI-powered analysis features

## 🎯 Project Goals

This tool was created to help Wikipedia editors:
- Quickly identify which policies are being discussed
- Understand the context of policy references
- Facilitate policy-focused discussions
- Research patterns in Wikipedia governance

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📝 License

This project is open source and available for educational and research purposes.

## 🙏 Acknowledgments

Built with ❤️ for the Wikipedia community.

---

**Note**: This tool is for educational purposes and is not affiliated with the Wikimedia Foundation.
