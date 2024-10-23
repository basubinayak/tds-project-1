# Chennai GitHub Users Analysis

This repository contains data about GitHub users from Chennai with more than 50 followers and their repositories.

## Data Files

1. `users.csv`: Contains information about 419 GitHub users from Chennai with more than 50 followers
2. `repositories.csv`: Contains information about their public repositories
3. `github_scraper.py`: Python script used to collect the data

## Data Collection

Data was collected on 2024-10-23 using the GitHub API v3.

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
