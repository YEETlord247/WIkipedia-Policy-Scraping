"""
Wikipedia Policy Link Extractor

This module extracts Wikipedia policy, guideline, and essay links directly from
the discussion HTML and text.
"""

import re
from bs4 import BeautifulSoup
from urllib.parse import unquote


# Known Wikipedia policies (mandatory rules)
POLICIES = {
    'NPOV': 'Neutral Point of View',
    'V': 'Verifiability',
    'NOR': 'No Original Research',
    'BLP': 'Biographies of Living Persons',
    '3RR': 'Three-Revert Rule',
    'CIVIL': 'Civility',
    'NPA': 'No Personal Attacks',
    'AGF': 'Assume Good Faith',
    'CON': 'Consensus',
    'CONSENSUS': 'Consensus',
    'NOT': 'What Wikipedia is Not',
    'NOTCENSORED': 'Wikipedia is Not Censored',
    'COPYVIO': 'Copyright Violations',
    'COI': 'Conflict of Interest',
    'PAID': 'Paid Editing',
    'SOCK': 'Sock Puppetry',
    'VAND': 'Vandalism',
    'EW': 'Edit Warring',
}

# Known Wikipedia guidelines (best practices)
GUIDELINES = {
    'N': 'Notability',
    'NOTABLE': 'Notability',
    'RS': 'Reliable Sources',
    'RSP': 'Reliable Sources/Perennial Sources',
    'MOS': 'Manual of Style',
    'MOSBOLD': 'Manual of Style - Bold',
    'CITE': 'Citing Sources',
    'EL': 'External Links',
    'ACCESS': 'Accessibility',
    'ALT': 'Alternative Text',
    'BRD': 'Bold, Revert, Discuss',
    'UNDUE': 'Undue Weight',
    'WEIGHT': 'Due Weight',
    'FRINGE': 'Fringe Theories',
    'INTEXT': 'In-text Attribution',
    'SPS': 'Self-Published Sources',
    'PRIMARY': 'Primary Sources',
    'SECONDARY': 'Secondary Sources',
    'IRS': 'Identifying Reliable Sources',
    'MEDRS': 'Identifying Reliable Sources (Medicine)',
    'PSTS': 'Primary, Secondary, and Tertiary Sources',
}

# Known Wikipedia essays (opinions/advice)
ESSAYS = {
    'COMMON': 'Common Sense',
    'IAR': 'Ignore All Rules',
    'DEADLINE': 'There is No Deadline',
    'STICK': 'Stick to the Point',
    'BEANS': "Don't Explain How to Game the System",
    'SNOW': 'Snowball Clause',
    'RANDY': 'Randy in Boise',
    'DNFTT': "Don't Feed the Trolls",
}


def extract_wikipedia_links(html_content, text_content):
    """
    Extract all Wikipedia policy/guideline/essay links from the discussion.
    
    Args:
        html_content: The HTML content of the discussion
        text_content: The plain text content of the discussion
        
    Returns:
        dict with 'policies', 'guidelines', and 'essays' keys, each containing
        a list of dicts with 'shortcut', 'full_name', and 'url' keys
    """
    found_policies = []
    found_guidelines = []
    found_essays = []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all links in the HTML
    links = soup.find_all('a', href=True)
    
    # Track what we've already found (to avoid duplicates)
    found_shortcuts = set()
    
    for link in links:
        href = link.get('href', '')
        link_text = link.get_text().strip()
        
        # Check if it's a Wikipedia namespace link
        if 'wikipedia.org/wiki/Wikipedia:' in href or href.startswith('/wiki/Wikipedia:'):
            # Extract the page name
            page_name = href.split('/wiki/Wikipedia:')[-1] if '/wiki/Wikipedia:' in href else ''
            page_name = unquote(page_name.split('#')[0])  # Remove anchor and decode
            
            # Check if it's a shortcut (WP:SOMETHING)
            shortcut_match = re.search(r'WP:([A-Z0-9]+)', page_name.upper())
            if shortcut_match:
                shortcut = shortcut_match.group(1)
            else:
                # Use the page name as the shortcut
                shortcut = page_name.replace('_', ' ').upper()
            
            # Skip if we've already found this one
            if shortcut in found_shortcuts:
                continue
            found_shortcuts.add(shortcut)
            
            # Categorize it
            full_url = f"https://en.wikipedia.org/wiki/Wikipedia:{page_name}"
            
            if shortcut in POLICIES:
                found_policies.append({
                    'shortcut': f'WP:{shortcut}',
                    'full_name': POLICIES[shortcut],
                    'url': full_url
                })
            elif shortcut in GUIDELINES:
                found_guidelines.append({
                    'shortcut': f'WP:{shortcut}',
                    'full_name': GUIDELINES[shortcut],
                    'url': full_url
                })
            elif shortcut in ESSAYS:
                found_essays.append({
                    'shortcut': f'WP:{shortcut}',
                    'full_name': ESSAYS[shortcut],
                    'url': full_url
                })
            else:
                # Unknown - try to categorize based on common patterns
                # For now, assume it's a guideline if not in our lists
                found_guidelines.append({
                    'shortcut': f'WP:{shortcut}',
                    'full_name': page_name.replace('_', ' '),
                    'url': full_url
                })
    
    # Also search for WP: shortcuts in plain text (not linked)
    text_shortcuts = re.findall(r'\bWP:([A-Z0-9]+)\b', text_content)
    
    for shortcut in text_shortcuts:
        if shortcut in found_shortcuts:
            continue
        found_shortcuts.add(shortcut)
        
        full_url = f"https://en.wikipedia.org/wiki/Wikipedia:{shortcut}"
        
        if shortcut in POLICIES:
            found_policies.append({
                'shortcut': f'WP:{shortcut}',
                'full_name': POLICIES[shortcut],
                'url': full_url
            })
        elif shortcut in GUIDELINES:
            found_guidelines.append({
                'shortcut': f'WP:{shortcut}',
                'full_name': GUIDELINES[shortcut],
                'url': full_url
            })
        elif shortcut in ESSAYS:
            found_essays.append({
                'shortcut': f'WP:{shortcut}',
                'full_name': ESSAYS[shortcut],
                'url': full_url
            })
    
    return {
        'policies': found_policies,
        'guidelines': found_guidelines,
        'essays': found_essays
    }


def format_policy_list(policy_list):
    """
    Format a list of policies/guidelines/essays as HTML for display.
    
    Args:
        policy_list: List of dicts with 'shortcut', 'full_name', and 'url' keys
        
    Returns:
        HTML string
    """
    if not policy_list:
        return "No items explicitly mentioned in this discussion."
    
    html_parts = []
    for item in policy_list:
        html_parts.append(
            f'<a href="{item["url"]}" target="_blank">{item["shortcut"]}</a> '
            f'({item["full_name"]})'
        )
    
    return '<br>'.join(html_parts)

