#BusSchedule.py
#Name: Beau Pick
#Date:10-21-25
#Assignment: Bus stop
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re


def loadURL(url):
    """
    Loads a given URL and returns all visible text from the site.
    """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = "/snap/bin/chromium"  # adjust if needed

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    content = driver.find_element(By.XPATH, "/html/body").text
    driver.quit()
    return content


def loadTestPage():
    """
    Reads a test page file to avoid repeated website calls.
    """
    with open("testPage.txt", 'r') as page:
        contents = page.read()
    return contents


def isLater(time1, time2):
    """Returns True if time1 is later than time2."""
    return time1 > time2


def getHours(time_str):
    """Extracts hour from a 'HH:MM AM/PM' string and converts to 24-hour format."""
    time_obj = datetime.datetime.strptime(time_str, "%I:%M %p")
    return time_obj.hour


def getMinutes(time_str):
    """Extracts minute from a 'HH:MM AM/PM' string."""
    time_obj = datetime.datetime.strptime(time_str, "%I:%M %p")
    return time_obj.minute


def findBusTimes(page_text):
    """
    Scans visible text for valid bus times in 'HH:MM AM/PM' format.
    Returns a list of datetime.time objects.
    """
    time_pattern = r'\b([0-1]?[0-9]:[0-5][0-9]\s?(AM|PM))\b'
    matches = re.findall(time_pattern, page_text)

    times = []
    for match in matches:
        try:
            t = datetime.datetime.strptime(match[0].strip(), "%I:%M %p").time()
            times.append(t)
        except ValueError:
            continue
    return times


def getNextBusTimes(bus_times, current_time):
    """Finds the next two bus times after the current time."""
    upcoming = [t for t in bus_times if (t.hour, t.minute) > (current_time.hour, current_time.minute)]
    upcoming.sort()

    if len(upcoming) >= 2:
        return upcoming[0], upcoming[1]
    elif len(upcoming) == 1:
        return upcoming[0], None
    else:
        return None, None


def main():
    # --- Variables you can easily change ---
    STOP_ID = "1235"
    ROUTE = "18"
    DIRECTION = "EAST"

    # Build URL dynamically
    url = f"https://myride.ometro.com/Schedule?stopCode=1235&date=2025-10-22&routeNumber=18&directionName=EAST"

    # --- Load visible content from the website ---
    page_text = loadURL(url)
    # page_text = loadTestPage()  # use this for testing

    # --- Extract times ---
    bus_times = findBusTimes(page_text)

    if not bus_times:
        print("No bus times found on the page.")
        return

    # --- Current time in Central Time ---
    utc_now = datetime.datetime.utcnow()
    central_now = utc_now - datetime.timedelta(hours=5)  # adjust from GMT to CST/CDT
    current_time = central_now.time()

    next1, next2 = getNextBusTimes(bus_times, current_time)

    print(f"Current Time: {central_now.strftime('%I:%M %p')}")

    if next1:
        delta1 = datetime.datetime.combine(datetime.date.today(), next1) - datetime.datetime.combine(datetime.date.today(), current_time)
        print(f"The next bus will arrive in {int(delta1.total_seconds() / 60)} minutes at {next1.strftime('%I:%M %p')}.")
    else:
        print("No upcoming buses today.")

    if next2:
        delta2 = datetime.datetime.combine(datetime.date.today(), next2) - datetime.datetime.combine(datetime.date.today(), current_time)
        print(f"The following bus will arrive in {int(delta2.total_seconds() / 60)} minutes at {next2.strftime('%I:%M %p')}.")


main()
