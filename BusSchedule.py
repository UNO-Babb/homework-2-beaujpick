#BusSchedule.py
#Name: Beau Pick
#Date:10-21-25
#Assignment: Bus stop

import datetime
import re
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Bus stop info
STOP_ID = "1235"
ROUTE = "18"
DIRECTION = "EAST"
BASE_URL = f"https://myride.ometro.com/Schedule?stopCode={STOP_ID}&routeNumber={ROUTE}&directionName={DIRECTION}"

def loadURL(url):
    """
    Loads a given URL and returns the visible text on the page.
    Uses a temporary user-data-dir to prevent session conflicts.
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.binary_location = "/usr/bin/chromium-browser"

    # Temporary user data dir to avoid "already in use" error
    temp_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(url)
    content = driver.find_element(By.TAG_NAME, "body").text
    driver.quit()

    return content

def loadTestPage():
    """
    Returns the contents of a saved test page to avoid hitting live site.
    """
    with open("testPage.txt", 'r') as page:
        contents = page.read()
    return contents

# Helper functions
def getHours(time_str):
    """Convert HH:MM AM/PM to 24-hour int hour"""
    dt = datetime.datetime.strptime(time_str, "%I:%M %p")
    return dt.hour

def getMinutes(time_str):
    """Extract minutes from HH:MM AM/PM"""
    dt = datetime.datetime.strptime(time_str, "%I:%M %p")
    return dt.minute

def isLater(time_str, now):
    """Return True if the bus time is later than now"""
    bus_time = now.replace(hour=getHours(time_str), minute=getMinutes(time_str), second=0, microsecond=0)
    return bus_time > now

def find_next_buses(page_text):
    """Find the next two upcoming buses from the page text"""
    # Current Central Time
    now_utc = datetime.datetime.utcnow()
    now = now_utc - datetime.timedelta(hours=5)  # Convert UTC → CST

    # Find all times in HH:MM AM/PM format
    times = re.findall(r"\b\d{1,2}:\d{2} [AP]M\b", page_text)

    # Filter only future times
    future_times = [t for t in times if isLater(t, now)]

    if len(future_times) == 0:
        return None, None

    next_bus = future_times[0]
    following_bus = future_times[1] if len(future_times) > 1 else None
    return next_bus, following_bus

def minutes_until(time_str):
    """Return minutes until the given bus time"""
    now_utc = datetime.datetime.utcnow()
    now = now_utc - datetime.timedelta(hours=5)  # Central Time
    bus_time = now.replace(hour=getHours(time_str), minute=getMinutes(time_str), second=0, microsecond=0)
    delta = bus_time - now
    return int(delta.total_seconds() // 60)

# Main program
def main():
    print(f"Bus Stop: {STOP_ID}, Route: {ROUTE}, Direction: {DIRECTION}")

    page_text = loadURL(BASE_URL)
    # page_text = loadTestPage()  # Uncomment to test with saved page

    next_bus, following_bus = find_next_buses(page_text)

    now_ct = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    print("Current Time:", now_ct.strftime("%I:%M %p"))

    if next_bus:
        print(f"The next bus will arrive in {minutes_until(next_bus)} minutes.")
    else:
        print("No upcoming buses found today.")

    if following_bus:
        print(f"The following bus will arrive in {minutes_until(following_bus)} minutes.")

if __name__ == "__main__":
    main()
