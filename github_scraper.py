import requests
import pandas as pd
import time
from datetime import datetime
import os
from typing import List, Dict, Any

class GitHubScraper:
    def __init__(self, token: str):
        # Initialize GitHub API authorization headers
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'  # Base URL for GitHub API requests
        
    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """
        Make a request to GitHub API with rate limit handling.
        If rate limit is exceeded, wait until reset time and retry.
        """
        response = requests.get(url, headers=self.headers, params=params)
        
        # Handle rate limit by checking reset time and retrying if necessary
        if response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
            reset_time = int(response.headers['X-RateLimit-Reset'])
            sleep_time = reset_time - time.time() + 1
            if sleep_time > 0:
                time.sleep(sleep_time)
            return self._make_request(url, params)
        
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()  # Return JSON response

    def clean_company_name(self, company: str) -> str:
        """
        Clean and format company name by removing leading '@' and converting to uppercase.
        """
        if not company:
            return ""
        company = str(company).strip()  # Remove whitespace
        if company.startswith('@'):
            company = company[1:]  # Remove '@' if it exists
        return company.upper()  # Convert to uppercase for consistency

    def search_users(self, location: str, min_followers: int) -> List[Dict]:
        """
        Search for GitHub users in a specified location with a minimum number of followers.
        Retrieves additional user details.
        """
        users = []
        page = 1
        
        # Paginate through results until no users are returned
        while True:
            params = {
                'q': f'location:{location} followers:>{min_followers}',
                'type': 'user',
                'page': page,
                'per_page': 100  # Max results per page
            }
            
            response = self._make_request(f'{self.base_url}/search/users', params)
            
            if not response['items']:
                break  # Exit loop if no more users
            
            # Retrieve detailed data for each user
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
            
            page += 1  # Move to the next page of results
        
        return users

    def get_user_repositories(self, username: str, max_repos: int = 500) -> List[Dict]:
        """
        Retrieve repositories for a specified user, limited by max_repos.
        Includes key repository details.
        """
        repos = []
        page = 1
        
        # Paginate through repositories until max_repos is reached or no more repos found
        while len(repos) <= max_repos:
            params = {
                'sort': 'pushed',
                'direction': 'desc',
                'per_page': min(100, max_repos - len(repos)),
                'page': page
            }
            
            response = self._make_request(f'{self.base_url}/users/{username}/repos', params)
            
            if not response:
                break  # Exit loop if no more repositories
            
            # Append each repository's details to the repos list
            for repo in response:
                license_key = repo['license'].get('key', '') if repo.get('license') else ''
                
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
            
            page += 1  # Move to the next page of results
            
            if len(response) < params['per_page']:
                break  # Exit if fewer results than requested (last page)
        
        return repos[:max_repos]

def main():
    # Retrieve GitHub token from environment variable
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise ValueError("Please set GITHUB_TOKEN environment variable")
    
    scraper = GitHubScraper(token)
    
    # Search for users in Chennai with more than 50 followers
    users = scraper.search_users('Chennai', 50)
    
    # Retrieve repositories for each user and store results
    all_repos = []
    for user in users:
        user_repos = scraper.get_user_repositories(user['login'])
        all_repos.extend(user_repos)
    
    # Convert user and repository data to DataFrames
    users_df = pd.DataFrame(users)
    repos_df = pd.DataFrame(all_repos)
    
    # Save DataFrames to CSV files
    users_df.to_csv('users.csv', index=False)
    repos_df.to_csv('repositories.csv', index=False)

if __name__ == "__main__":
    main()
