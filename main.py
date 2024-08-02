import requests
import datetime

# Replace 'your_github_token' with your actual GitHub token
GITHUB_TOKEN = 'your_github_token'
USERNAME = 'mihneabondor'

# Define the GraphQL query to fetch contributions
query = """
{
  user(login: "%s") {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
""" % USERNAME

# Set up the headers for the request
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

# Make the request to the GitHub GraphQL API
response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)

# Check for a successful response
if response.status_code != 200:
    raise Exception(f"Query failed to run with a {response.status_code}: {response.text}")

# Parse the JSON response
data = response.json()

# Extract the contribution days
weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']

# Initialize the contributions matrix (8 rows for weeks, 7 columns for days of the week)
# Each row represents a week, and each column represents a day starting from Sunday (index 0)
contributions_matrix = [[0 for _ in range(7)] for _ in range(8)]

# Populate the contributions matrix
for i, week in enumerate(weeks[-8:]):  # Get only the last 8 weeks
    for day in week['contributionDays']:
        date = datetime.datetime.strptime(day['date'], '%Y-%m-%d')
        week_num = i
        day_num = (date.weekday() + 1) % 7  # Adjust so Sunday is index 0, Monday is index 1, ..., Saturday is index 6
        contributions_matrix[week_num][day_num] = day['contributionCount']

# Print the contributions matrix
for week in contributions_matrix:
    print(week)
