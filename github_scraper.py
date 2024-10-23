import requests
import pandas as pd
import time
from datetime import datetime
import os
from typing import List, Dict, Any

class GitHubScraper:
    def __init__(self, token: str):
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """Make a request to GitHub API with rate limit handling"""
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
            reset_time = int(response.headers['X-RateLimit-Reset'])
            sleep_time = reset_time - time.time() + 1
            if sleep_time > 0:
                time.sleep(sleep_time)
            return self._make_request(url, params)
            
        response.raise_for_status()
        return response.json()
    
    def clean_company_name(self, company: str) -> str:
        """Clean company name according to specifications"""
        if not company:
            return ""
        company = str(company).strip()
        if company.startswith('@'):
            company = company[1:]
        return company.upper()
    
    def search_users(self, location: str, min_followers: int) -> List[Dict]:
        """Search for users in a specific location with minimum followers"""
        users = []
        page = 1
        
        while True:
            params = {
                'q': f'location:{location} followers:>{min_followers}',
                'type': 'user',
                'page': page,
                'per_page': 100
            }
            
            response = self._make_request(f'{self.base_url}/search/users', params)
            
            if not response['items']:
                break
                
            for user in response['items']:
                user_data = self._make_request(user['url'])
                users.append({
                    'login': user_data.get('login', ''),
                    'name': user_data.get('name', ''),
                    'company': self.clean_company_name(user_data.get('company')),
                    'location': user_data.get('location', ''),
                    'email': user_data.get('email', ''),
                    'hireable': str(user_data.get('hireable', '')).lower(),
                    'bio': user_data.get('bio', ''),
                    'public_repos': user_data.get('public_repos', 0),
                    'followers': user_data.get('followers', 0),
                    'following': user_data.get('following', 0),
                    'created_at': user_data.get('created_at', '')
                })
            
            page += 1
            
        return users
    
    def get_user_repositories(self, username: str, max_repos: int = 500) -> List[Dict]:
        """Get repositories for a specific user"""
        repos = []
        page = 1
        
        while len(repos) <= max_repos:
            params = {
                'sort': 'pushed',
                'direction': 'desc',
                'per_page': min(100, max_repos - len(repos)),
                'page': page
            }
            
            response = self._make_request(f'{self.base_url}/users/{username}/repos', params)
            
            if not response:
                break
                
            for repo in response:
                # Handle the case where license is None
                license_key = ''
                if repo.get('license') is not None:
                    license_key = repo['license'].get('key', '')
                
                repos.append({
                    'login': username,
                    'full_name': repo.get('full_name', ''),
                    'created_at': repo.get('created_at', ''),
                    'stargazers_count': repo.get('stargazers_count', 0),
                    'watchers_count': repo.get('watchers_count', 0),
                    'language': repo.get('language', ''),
                    'has_projects': str(repo.get('has_projects', '')).lower(),
                    'has_wiki': str(repo.get('has_wiki', '')).lower(),
                    'license_name': license_key
                })
            
            page += 1
            
            if len(response) < params['per_page']:
                break
            
        return repos[:max_repos]

def main():
    # Replace with your GitHub token
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("Please set GITHUB_TOKEN environment variable")
        
    scraper = GitHubScraper(token)
    
    # Get users from Chennai with >50 followers
    users = scraper.search_users('Chennai', 50)
    
    # Get repositories for each user
    all_repos = []
    for user in users:
        user_repos = scraper.get_user_repositories(user['login'])
        all_repos.extend(user_repos)
    
    # Create DataFrames
    users_df = pd.DataFrame(users)
    repos_df = pd.DataFrame(all_repos)
    
    # Save to CSV
    users_df.to_csv('users.csv', index=False)
    repos_df.to_csv('repositories.csv', index=False)
    
    # Create README.md
    readme_content = f"""# Chennai GitHub Users Analysis

This repository contains data about GitHub users from Chennai with more than 50 followers and their repositories.

## Data Files

1. `users.csv`: Contains information about {len(users)} GitHub users from Chennai with more than 50 followers
2. `repositories.csv`: Contains information about their public repositories
3. `github_scraper.py`: Python script used to collect the data

## Data Collection

Data was collected on {datetime.now().strftime('%Y-%m-%d')} using the GitHub API v3.

### Users Dataset Columns
- login: GitHub user ID
- name: Full name
- company: Company name (cleaned and standardized)
- location: User location
- email: User email
- hireable: Whether user is available for hire
- bio: User bio
- public_repos: Number of public repositories
- followers: Number of followers
- following: Number of users being followed
- created_at: Account creation date

### Repositories Dataset Columns
- login: Repository owner's GitHub user ID
- full_name: Repository full name
- created_at: Repository creation date
- stargazers_count: Number of stars
- watchers_count: Number of watchers
- language: Primary programming language
- has_projects: Projects feature status
- has_wiki: Wiki feature status
- license_name: Repository license key

## Usage
To run the scraper:
1. Set your GitHub token as environment variable: `export GITHUB_TOKEN='your_token'`
2. Install requirements: `pip install requests pandas`
3. Run the script: `python github_scraper.py`
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)

if __name__ == "__main__":
    main()