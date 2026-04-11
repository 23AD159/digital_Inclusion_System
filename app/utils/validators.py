import requests
import re
from flask import current_app

def verify_github_profile(url):
    """
    Extracts GitHub username and fetches repository count.
    Returns (success, repo_count, message)
    """
    if not url:
        return False, 0, "No URL provided"

    # Regex to extract username: https://github.com/username
    match = re.search(r'github\.com/([^/]+)', url)
    if not match:
        return False, 0, "Invalid GitHub URL format"
    
    username = match.group(1).split('?')[0] # remove query params if any
    
    api_url = f"https://api.github.com/users/{username}"
    headers = {}
    
    token = current_app.config.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f"token {token}"
    
    try:
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data.get('public_repos', 0), f"Verified: {username}"
        elif response.status_code == 404:
            return False, 0, "User not found"
        else:
            return False, 0, f"GitHub API error: {response.status_code}"
    except Exception as e:
        return False, 0, f"Connection failed: {str(e)}"

def verify_linkedin_profile(url):
    """
    Simple check for LinkedIn URL format.
    True LinkedIn API access is heavily restricted.
    """
    if not url:
        return False, "No URL provided"
    
    pattern = r'linkedin\.com/in/[^/]+'
    if re.search(pattern, url):
        return True, "Profile format valid"
    return False, "Invalid LinkedIn URL format"
