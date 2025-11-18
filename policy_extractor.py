"""
Wikipedia Policy Link Extractor

This module extracts Wikipedia policy, guideline, and essay links directly from
the discussion HTML and text.
"""

import re
from bs4 import BeautifulSoup
from urllib.parse import unquote


# Comprehensive Wikipedia policy/guideline/essay database
WIKIPEDIA_ITEMS = {
    "Policy": [
        "Neutral point of view",
        "No original research",
        "Verifiability",
        "Article titles",
        "Biographies of living persons",
        "Image use policy",
        "What Wikipedia is not",
        "Block evasion",
        "Civility",
        "Clean start",
        "Consensus",
        "Dispute resolution",
        "Edit warring",
        "Editing policy",
        "Harassment",
        "No personal attacks",
        "No legal threats",
        "Ownership of content",
        "Sockpuppetry",
        "Username policy",
        "Vandalism",
        "Deletion policy",
        "Speedy deletion",
        "Proposed deletion",
        "Proposed deletion (BLP)",
        "Revision deletion",
        "Oversight"
    ],
    "Guideline": [
        "Assume good faith",
        "Conflict of interest",
        "Disruptive editing",
        "Don't bite the newcomers",
        "Don't disrupt to make a point",
        "Etiquette",
        "Gaming the system",
        "Citing sources",
        "External links",
        "Reliable sources",
        "Fringe theories",
        "Naming conventions",
        "Non-free content",
        "Offensive material",
        "Article size",
        "Be bold",
        "Understandability",
        "Categories, lists, templates",
        "Categorization",
        "Disambiguation",
        "Manual of Style",
        "Notability",
        "Deletion process"
    ],
    "Essay": [
        "What no consensus really means",
        "One against many",
        "Getting your way at Wikipedia",
        "Lob a grenade and run away",
        "Always keep context in mind when arguing claims",
        "Academic Neutrality",
        "Avoid contemporary sources",
        "A POV that draws a source.",
        "Beyond the Neutral Point of View",
        "Civil POV pushing is POV pushing",
        "CIVIL POV Pushing Strategies",
        "Gendered category criterion",
        "Yes. We are biased.",
        "Don't act neutral",
        "Don't throw your POV up to the sky",
        "Systemic bias against Transformers",
        "Neutrality and consensus",
        "Neutrality of sources",
        "Neutral = source-oriented",
        "No. We are not biased.",
        "NPOV, a detailed breakdown",
        "Asymmetric controversy",
        "Crying MEDRS!",
        "Lede bombing",
        "The big mistake",
        "Writing neutrally for Wikipedia",
        "Prefer truth",
        "Splitting the difference",
        "Reliable sources for geopolitical adversaries",
        "Media, Politics, and Peace",
        "ChristianityAndNPOV",
        "Essjay neutrality",
        "Yes, you are a nerd.",
        "When interest compromises neutrality"
    ]
}

# Common shortcuts mapping (for quick detection)
SHORTCUTS = {
    'NPOV': 'Neutral point of view',
    'NOR': 'No original research',
    'V': 'Verifiability',
    'BLP': 'Biographies of living persons',
    'NOT': 'What Wikipedia is not',
    'NOTCENSORED': 'What Wikipedia is not',
    'CIVIL': 'Civility',
    'CON': 'Consensus',
    'CONSENSUS': 'Consensus',
    'EW': 'Edit warring',
    '3RR': 'Edit warring',
    'NPA': 'No personal attacks',
    'SOCK': 'Sockpuppetry',
    'VAND': 'Vandalism',
    'AGF': 'Assume good faith',
    'COI': 'Conflict of interest',
    'BITE': "Don't bite the newcomers",
    'POINT': "Don't disrupt to make a point",
    'GAME': 'Gaming the system',
    'CITE': 'Citing sources',
    'EL': 'External links',
    'RS': 'Reliable sources',
    'FRINGE': 'Fringe theories',
    'MOS': 'Manual of Style',
    'N': 'Notability',
    'NOTABLE': 'Notability',
    'UNDUE': 'Neutral point of view',  # UNDUE is part of NPOV
    'WEIGHT': 'Neutral point of view',
}


def extract_wikipedia_links(html_content, text_content):
    """
    Extract all Wikipedia policy/guideline/essay links from the discussion.
    
    Args:
        html_content: The HTML content of the discussion
        text_content: The plain text content of the discussion
        
    Returns:
        dict with 'policies', 'guidelines', and 'essays' keys, each containing
        a list of dicts with 'name' and 'url' keys
    """
    found_items = {
        'policies': {},
        'guidelines': {},
        'essays': {}
    }
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Method 1: Extract from Wikipedia links in HTML
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href', '')
        if 'wikipedia.org/wiki/Wikipedia:' in href or href.startswith('/wiki/Wikipedia:'):
            process_wikipedia_link(href, found_items)
    
    # Method 2: Search for shortcuts in text (WP:SOMETHING)
    shortcut_matches = re.findall(r'\bWP:([A-Z0-9]+)\b', text_content, re.IGNORECASE)
    for shortcut in shortcut_matches:
        shortcut_upper = shortcut.upper()
        if shortcut_upper in SHORTCUTS:
            full_name = SHORTCUTS[shortcut_upper]
            category = find_category(full_name)
            if category:
                add_item(found_items, category, full_name, f'WP:{shortcut_upper}')
    
    # Method 3: Search for full names in text (case-insensitive)
    for category, items in WIKIPEDIA_ITEMS.items():
        for item_name in items:
            # Create regex pattern that matches the item name (case-insensitive, word boundaries)
            # Handle special characters in the item name
            escaped_name = re.escape(item_name)
            # Make it flexible: allow some variation
            pattern = r'\b' + escaped_name.replace(r'\ ', r'\s+') + r'\b'
            
            if re.search(pattern, text_content, re.IGNORECASE):
                add_item(found_items, category.lower() + 's', item_name)
    
    # Convert dicts to lists for output
    return {
        'policies': list(found_items['policies'].values()),
        'guidelines': list(found_items['guidelines'].values()),
        'essays': list(found_items['essays'].values())
    }


def process_wikipedia_link(href, found_items):
    """Process a Wikipedia link and add it to found_items if it's a policy/guideline/essay."""
    # Extract the page name
    if '/wiki/Wikipedia:' in href:
        page_name = href.split('/wiki/Wikipedia:')[-1]
    else:
        page_name = href.replace('/wiki/Wikipedia:', '')
    
    page_name = unquote(page_name.split('#')[0])  # Remove anchor and decode
    page_name = page_name.replace('_', ' ')
    
    # Check if this page name matches any known item
    for category, items in WIKIPEDIA_ITEMS.items():
        for item_name in items:
            # Case-insensitive comparison
            if page_name.lower() == item_name.lower() or item_name.lower() in page_name.lower():
                add_item(found_items, category.lower() + 's', item_name)
                return
    
    # If not found in our database, check shortcuts
    shortcut_match = re.search(r'WP[:/]?([A-Z0-9]+)', page_name, re.IGNORECASE)
    if shortcut_match:
        shortcut = shortcut_match.group(1).upper()
        if shortcut in SHORTCUTS:
            full_name = SHORTCUTS[shortcut]
            category = find_category(full_name)
            if category:
                add_item(found_items, category, full_name, f'WP:{shortcut}')


def find_category(item_name):
    """Find which category (policies/guidelines/essays) an item belongs to."""
    for category, items in WIKIPEDIA_ITEMS.items():
        if item_name in items:
            return category.lower() + 's'
    return None


def add_item(found_items, category, item_name, shortcut=None):
    """Add an item to found_items, avoiding duplicates."""
    if category not in found_items:
        return
    
    # Use item_name as key to avoid duplicates
    if item_name not in found_items[category]:
        # Create Wikipedia URL
        url_name = item_name.replace(' ', '_')
        url = f"https://en.wikipedia.org/wiki/Wikipedia:{url_name}"
        
        found_items[category][item_name] = {
            'name': item_name,
            'shortcut': shortcut,
            'url': url
        }


def format_policy_list(policy_list):
    """
    Format a list of policies/guidelines/essays as HTML for display.
    
    Args:
        policy_list: List of dicts with 'name', 'shortcut', and 'url' keys
        
    Returns:
        HTML string
    """
    if not policy_list:
        return "No items explicitly mentioned in this discussion."
    
    html_parts = []
    for item in policy_list:
        if item.get('shortcut'):
            display = f'<a href="{item["url"]}" target="_blank">{item["shortcut"]}</a> ({item["name"]})'
        else:
            display = f'<a href="{item["url"]}" target="_blank">{item["name"]}</a>'
        html_parts.append(display)
    
    return '<br>'.join(html_parts)
