"""
Wikipedia Talk Page Policy Analyzer - Main Flask Application

This is the main Flask backend that serves the web interface and coordinates
the scraping and analysis of Wikipedia talk page discussions.
"""

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

# Import our custom modules
from scraper import scrape_wikipedia_discussion
from analyzer import identify_policies_with_openai
from policy_extractor import extract_wikipedia_links, format_policy_list

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

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
    """
    Analyze Wikipedia discussion endpoint.
    
    Accepts a POST request with a URL to a Wikipedia talk page discussion,
    scrapes the specific discussion section, and analyzes it for policy/guideline/essay mentions.
    
    Request JSON:
        {
            "url": "https://en.wikipedia.org/wiki/Talk:Article#Section_Name"
        }
    
    Response JSON:
        {
            "discussion_html": "<html content of the specific discussion>",
            "policies": "Analysis of policies mentioned",
            "guidelines": "Analysis of guidelines mentioned", 
            "essays": "Analysis of essays mentioned"
        }
    """
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        print(f"\n{'='*60}")
        print(f"Starting analysis for: {url}")
        print(f"{'='*60}")
        
        # Scrape the specific discussion section
        discussion = scrape_wikipedia_discussion(url)
        
        if not discussion:
            print("Error: Failed to scrape Wikipedia page")
            return jsonify({
                'error': 'Failed to scrape Wikipedia page. Please check the URL and try again.'
            }), 500
        
        print(f"\n✓ Successfully scraped discussion")
        print(f"  HTML length: {len(discussion['html'])} characters")
        print(f"  Text length: {len(discussion['text'])} characters")
        
        # Extract Wikipedia policy/guideline/essay links directly from the content
        print(f"\nExtracting Wikipedia policy links...")
        extracted_links = extract_wikipedia_links(discussion['html'], discussion['text'])
        
        print(f"  Found {len(extracted_links['policies'])} policies")
        print(f"  Found {len(extracted_links['guidelines'])} guidelines")
        print(f"  Found {len(extracted_links['essays'])} essays")
        
        # Format the results for display
        policies_html = format_policy_list(extracted_links['policies'])
        guidelines_html = format_policy_list(extracted_links['guidelines'])
        essays_html = format_policy_list(extracted_links['essays'])
        
        print(f"\n✓ Analysis complete!")
        print(f"{'='*60}\n")
        
        return jsonify({
            'discussion_html': discussion['html'],
            'policies': policies_html,
            'guidelines': guidelines_html,
            'essays': essays_html
        })
        
    except Exception as e:
        print(f"\n✗ Error in analyze endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    # Run the Flask development server
    print("\n" + "="*60)
    print("Wikipedia Talk Page Policy Analyzer")
    print("="*60)
    print("Starting server on http://127.0.0.1:5001")
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5001, host='127.0.0.1')

