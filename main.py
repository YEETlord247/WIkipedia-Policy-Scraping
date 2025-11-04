from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import os
from openai import OpenAI
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def scrape_wikipedia_discussion(url):
    """Scrape Wikipedia talk page discussion"""
    try:
        # Add proper headers to avoid being blocked by Wikipedia
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main content area
        content = soup.find('div', {'id': 'mw-content-text'})
        
        if not content:
            print("Error: Could not find main content div with id 'mw-content-text'")
            # Try alternative selectors
            content = soup.find('div', {'class': 'mw-parser-output'})
            if not content:
                print("Error: Could not find content with alternative selectors")
                return None
        
        print(f"Found content, length: {len(str(content))} characters")
        
        # Extract discussion text while preserving structure
        discussion_html = str(content)
        
        # Extract plain text for OpenAI analysis
        discussion_text = content.get_text(separator='\n', strip=True)
        
        print(f"Extracted text length: {len(discussion_text)} characters")
        
        return {
            'html': discussion_html,
            'text': discussion_text
        }
    except requests.exceptions.RequestException as e:
        print(f"Request error scraping Wikipedia: {e}")
        return None
    except Exception as e:
        print(f"Error scraping Wikipedia: {e}")
        import traceback
        traceback.print_exc()
        return None

def identify_policies_with_openai(discussion_text):
    """Use OpenAI to identify policies, guidelines, and essays"""
    try:
        # Prompts for different categories
        prompts = {
            'policies': """You are analyzing a Wikipedia talk page discussion. Your task is to identify Wikipedia POLICIES that are actually DISCUSSED, DEBATED, or REFERENCED in the conversation content - NOT just listed in the header template.

IGNORE the standard header template that lists "Neutral point of view, No original research, Verifiability" - these appear on every talk page. Only list them if they're actually discussed in the conversation.

Wikipedia POLICIES (mandatory rules) include:
- Core content: NPOV, Verifiability, No Original Research
- Biographical: Biographies of Living Persons (BLP)
- Behavioral: Edit warring, Civility, No personal attacks, Assume good faith, Consensus
- Content: What Wikipedia is Not (NOT), Copyright, Conflict of interest
- Access: Accessibility, Alternative text

Look for actual discussions about:
- Edit disputes (→ Edit warring, Consensus policy)
- Living people (→ BLP policy)
- Accessibility issues (→ Accessibility policy)
- Civility/behavior issues (→ Civility, No personal attacks)
- Content type debates (→ What Wikipedia is Not)

Format: <a href="https://en.wikipedia.org/wiki/Wikipedia:Policy_Name" target="_blank">Policy Name</a>: Quote or explain how it's actually discussed.

If no policies are actively discussed (beyond the header), say "No policies discussed in conversation.""",
            
            'guidelines': """You are analyzing a Wikipedia talk page discussion. Your task is to identify Wikipedia GUIDELINES that are actually DISCUSSED or REFERENCED in the conversation.

Wikipedia GUIDELINES (best-practice recommendations) include:
- Content: Notability (WP:N), Reliable Sources (WP:RS)
- Style: Manual of Style (WP:MOS), Article titles, Lead sections
- Technical: Citing sources (WP:CITE), External links, Categories
- Layout: Accessibility (WP:ACCESS), Article size, Section organization
- Images: Image use policy, Alternative text for images

Look for actual discussions about:
- "This is notable/not notable" (→ Notability guideline)
- "This source is reliable/unreliable" (→ Reliable Sources)
- Formatting debates, readability issues (→ Manual of Style, Accessibility)
- Mobile display problems (→ Accessibility, MOS)
- Article structure, sections (→ Article layout guidelines)
- Image or table formatting (→ MOS, Accessibility)

For the Dinosaur talk page example: Look for discussions about taxonomy formatting, mobile readability, accessibility for people with disabilities, article structure.

Format: <a href="https://en.wikipedia.org/wiki/Wikipedia:Guideline_Name" target="_blank">Guideline Name</a>: Quote or explain the actual discussion.

If no guidelines are discussed, say "No guidelines discussed in conversation.""",
            
            'essays': """You are analyzing a Wikipedia talk page discussion. Your task is to identify ALL Wikipedia ESSAYS that are mentioned or referenced.

Wikipedia ESSAYS are opinion/advice pages written by editors. They are NOT official policy or guidelines. Common essays include:
- WP:COMMON (Common sense)
- WP:IAR (Ignore all rules)
- WP:DEADLINE (There is no deadline)
- WP:STICK (Stick to the point)
- WP:BEANS (Don't explain how to game the system)

Essays are often cited in discussions to give advice or perspective, but they don't carry official weight.

Look for: References to essay pages (often starting with "WP:" but not official policy/guidelines), advice-giving shortcuts, or opinion pieces.

Format each as: <a href="https://en.wikipedia.org/wiki/Wikipedia:Essay_Name" target="_blank">Essay Name</a>: Brief explanation.

List ALL essays you find. If none are mentioned, say "No essays found."""
        }
        
        results = {}
        
        for category, prompt in prompts.items():
            full_prompt = f"{prompt}\n\nDiscussion text:\n{discussion_text[:8000]}"  # Limit text length
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at identifying Wikipedia policies, guidelines, and essays from discussion text."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            results[category] = response.choices[0].message.content
        
        return results
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return {
            'policies': f'Error: {str(e)}',
            'guidelines': f'Error: {str(e)}',
            'essays': f'Error: {str(e)}'
        }

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    """Return empty favicon to prevent 404 errors"""
    return '', 204

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze Wikipedia discussion"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        print(f"\n=== Starting analysis for: {url} ===")
        
        # Scrape the discussion
        discussion = scrape_wikipedia_discussion(url)
        
        if not discussion:
            print("Error: Failed to scrape Wikipedia page")
            return jsonify({'error': 'Failed to scrape Wikipedia page. Please check the URL and try again.'}), 500
        
        print("Successfully scraped discussion, calling OpenAI...")
        
        # Identify policies using OpenAI
        policy_results = identify_policies_with_openai(discussion['text'])
        
        print("Analysis complete!")
        
        return jsonify({
            'discussion_html': discussion['html'],
            'policies': policy_results['policies'],
            'guidelines': policy_results['guidelines'],
            'essays': policy_results['essays']
        })
    except Exception as e:
        print(f"Error in analyze endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')

