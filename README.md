# Wikipedia Policy Analyzer

A web application that scrapes Wikipedia talk page discussions and identifies policy mentions using OpenAI's GPT API.

## Features

- 📄 **Two-Column Layout**: Discussion on the left, policy mentions on the right
- 🔍 **Smart Analysis**: Uses GPT-4 to identify Wikipedia policies, guidelines, and essays
- 🎨 **Modern UI**: Beautiful, responsive design with smooth scrolling
- 🚀 **Easy to Use**: Simply paste a Wikipedia talk page URL and click analyze

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key

Set your OpenAI API key as an environment variable:

**On macOS/Linux:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**On Windows:**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

### 3. Run the Application

```bash
python main.py
```

The application will start on `http://localhost:5000`

## Usage

1. Open your web browser and navigate to `http://localhost:5000`
2. Paste a Wikipedia talk page URL (e.g., `https://en.wikipedia.org/wiki/Talk:Example`)
3. Click "Analyze Discussion"
4. View the discussion on the left and identified policies on the right

## How It Works

The application:
1. Scrapes the Wikipedia talk page using BeautifulSoup
2. Extracts the discussion content
3. Sends the content to OpenAI's GPT-4 with specialized prompts
4. Categorizes findings into:
   - **Policies** (🔴): Official Wikipedia policies
   - **Guidelines** (🟡): Recommended Wikipedia guidelines
   - **Essays** (🔵): Wikipedia essays and opinion pieces

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection

## Dependencies

- Flask: Web framework
- BeautifulSoup4: Web scraping
- Requests: HTTP library
- OpenAI: GPT API integration
- lxml: HTML/XML parser

## Notes

- The application uses GPT-4 for more accurate policy identification
- Long discussions are truncated to 8000 characters for analysis
- Make sure you have sufficient OpenAI API credits

