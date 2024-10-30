# Chennai GitHub Users Analysis

- The <a href="https://github.com/basubinayak/tds-project-1/blob/b5b39f49a09f8ac532a1f06995c85ba3fbfe61ef/github_scraper.py">script</a> retrieves GitHub user profiles and repositories by querying the GitHub API for users in a specified location with a minimum follower count. It handles pagination and rate limits, extracts detailed user and repository information, and cleans company names. All data is structured and saved in CSV files for easy analysis and use.
- The most surprising finding from the analysis is the negative correlation between bio length and number of followers. The data shows that developers with longer bios tend to have fewer followers, with each additional word in the bio associated with about 1.7 fewer followers on average. This suggests that concise, focused bios may be more effective than lengthy ones for building a following on GitHub.
- Based on the analysis, an actionable recommendation for developers would be to optimize their GitHub profile by:
  - Keeping their bio concise and to-the-point, rather than writing lengthy descriptions
  - Focusing on building high-quality, starred repositories rather than just amassing a large number of repos
  - Considering their "leader strength" metric (followers / (1 + following)) and working to increase their follower count relative to who they follow
