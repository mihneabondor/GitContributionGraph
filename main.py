import requests
import datetime
import time
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas

# Replace with your GitHub token and username
GITHUB_TOKEN = 'your_github_token'
USERNAME = 'your_github_username'

# Define the GraphQL query to fetch contributions for the last 32 weeks
def fetch_contribution_data():
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

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Query failed to run with a {response.status_code}: {response.text}")

    return response.json()

# Define the function to update the LED matrix
def update_led_matrix(contributions_matrix):
    # Set up the LED matrix
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=90, rotate=0)

    # Function to map contribution counts to brightness levels
    def get_brightness(count):
        if count == 0:
            return 0  # Off
        elif count < 5:
            return 1  # Low brightness
        elif count < 10:
            return 2  # Medium brightness
        else:
            return 3  # High brightness

    # Display the contribution graph on the LED matrix
    with canvas(device) as draw:
        for col in range(32):  # For each of the 32 weeks
            for row in range(8):  # For each day in the week
                brightness = get_brightness(contributions_matrix[row][col])
                draw.point((col, row), fill=brightness)

def process_contributions_data(data):
    # Extract the contribution days for the last 32 weeks
    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks'][-32:]

    # Reverse the order of weeks so the most recent week is displayed on the last matrix
    weeks.reverse()

    # Initialize the contributions matrix (8 rows per week, 32 columns for 32 weeks)
    contributions_matrix = [[0 for _ in range(32)] for _ in range(8)]

    # Populate the contributions matrix
    for week_num, week in enumerate(weeks):
        for day in week['contributionDays']:
            date = datetime.datetime.strptime(day['date'], '%Y-%m-%d')
            if date > datetime.datetime.now():
                continue  # Skip future dates
            week_idx = len(weeks) - 1 - week_num  # Reverse index for columns
            day_idx = date.weekday()  # weekday() returns 0 for Monday, ..., 6 for Sunday
            row_idx = (day_idx + 1) % 7  # Adjust so Sunday is row 0, Monday is row 1, ..., Saturday is row 6
            contributions_matrix[row_idx][week_idx] = day['contributionCount']

    return contributions_matrix

# Main loop to update the data every hour
while True:
    # Fetch new data from GitHub
    data = fetch_contribution_data()
    
    # Process the data
    contributions_matrix = process_contributions_data(data)
    
    # Update the LED matrix
    update_led_matrix(contributions_matrix)
    
    # Sleep for an hour before updating again
    time.sleep(3600)  # 3600 seconds = 1 hour
