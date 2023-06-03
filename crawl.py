import re
import time
import math
import requests
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urljoin
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


import math


def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    earth_radius = 6371

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculate the differences in latitude and longitude
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # Calculate the distance in kilometers
    distance = earth_radius * c

    return distance

def to_level():
    return 

def reservoir_crawler():
    '''
    水情時間: time
    有效蓄水量(萬立方公尺): effective_storage_capacity
    蓄水百分比(%): storage_ratio

    竹 石門水庫、寶山第二水庫、(寶山水庫)、永和山水庫
    中 鯉魚潭水庫、德基水庫
    南 南化水庫、曾文水庫、烏山頭水庫
    '''
    reservoir = ["石門水庫", "寶山第二水庫", "永和山水庫", "鯉魚潭水庫", "德基水庫",
    "南化水庫", "曾文水庫", "烏山頭水庫"]

    time = []
    effective_storage_capacity = []
    storage_ratio = []

    url = "https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx"

    # Send a GET request to the website
    response = requests.get(url)

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    # print(soup)
    # Find the table element with the desired data
    table = soup.find("table", {"id": "ctl00_cphMain_gvList"})
    # print(table)
    # # Extract the table headers
    headers = [header.text for header in table.find_all("th")]
    # print(headers[0] == "水庫名稱")
    # # Extract the table rows

    for row in table.find_all("tr"):
        r = [cell.text for cell in row.find_all("td")]
        if len(r) and r[0][0] == '\n' and r[0][1:-1] in reservoir:
            time += [r[1]]
            if r[6][0] == '-':
                effective_storage_capacity += [0]
            else:
                effective_storage_capacity += [float(r[6].replace(',', ''))]
            if r[7][0] == '-':
                storage_ratio += [0]
            else:
                storage_ratio += [float(r[7][:-2])]

    print(time)
    print(effective_storage_capacity)
    print(storage_ratio)

    # # Print the headers and rows
    # print("Headers:", headers)
    # print("Rows:", rows)

def electricity_crawler():

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode

    # Set up the ChromeDriver service
    # webdriver_service = Service("/usr/local/bin/chromedriver")
    # webdriver_service = Service("/Users/jimmycv07/Library/CloudStorage/GoogleDrive-jimmy.en07@nycu.edu.tw/My Drive/NCTU/Fifth-2/Cloud_native_development/chromedriver")
    webdriver_service = Service("chromedriver")

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    # Load the webpage
    url = "https://www.taiwanstat.com/realtime/power/"
    # url = "https://www.taipower.com.tw/tc/page.aspx?mid=206&cid=403&cchk=1f5269ec-633e-471c-9727-22345366f0be"
    driver.get(url)
    # print(driver.page_source)

    element = 0
    electricity = []
    target = [
        "北部即時發電量", "北部即時用電量",
        "中部即時發電量", "中部即時用電量",
        "南部即時發電量", "南部即時用電量",
        "東部即時發電量", "東部即時用電量"
    ]
    for string in target:
        xpath = f"//h5[contains(text(), '{string}')]"
        # print(driver.find_element(By.XPATH, xpath).text)
        # e.append(driver.find_element(By.XPATH, xpath).text.split('：')[1])
        if element:
            element = element.find_element(By.XPATH, xpath)
        else:
            element = driver.find_element(By.XPATH, xpath)

        # electricity.append(element.text)
        electricity.append(element.text.split('：')[1])

    print(electricity) 

    # Quit the browser
    driver.quit()

def earthquake_crawler():

    # # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode

    # Set up the ChromeDriver service
    # webdriver_service = Service("/usr/local/bin/chromedriver")
    # webdriver_service = Service("/Users/jimmycv07/Library/CloudStorage/GoogleDrive-jimmy.en07@nycu.edu.tw/My Drive/NCTU/Fifth-2/Cloud_native_development/chromedriver")
    webdriver_service = Service("chromedriver")

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    # Start the webdriver
    # driver = webdriver.Chrome()

    # Load the webpage
    driver.get('https://scweb.cwb.gov.tw/')

    # target_index = 4  # Specify the index of the desired element (0 for the first occurrence, 1 for the second, and so on)
    # target_elements = driver.find_elements(By.XPATH, '//div[@class="level green"]')
    # Extract the portion containing the locations variable
    identifier = []
    date_time = []
    magnitude = []
    depth = []
    location = []
    level = []
    longitude = []
    latitude = []
    pattern = r"var locations = \[(.*?)\];"
    matches = re.search(pattern, driver.page_source, re.DOTALL)
    if matches:
        locations_data = matches.group(1)

        # Extract the individual location data
        location_pattern = r"\[(.*?)\]"
        location_matches = re.findall(location_pattern, locations_data)

        # Process each location
        for location_match in location_matches:
            # Split the location data by comma
            location_values = location_match.split(',')

            # Remove leading and trailing whitespace, and quotes
            location_values = [value.strip().strip("'") for value in location_values]

            # Access the desired values
            identifier += [location_values[0]]
            date_time += [location_values[2]]
            magnitude += [float(location_values[3])]
            depth += [float(location_values[4])]
            location += [location_values[5]]
            level += [location_values[6]]
            longitude += [float(location_values[7])]
            latitude += [float(location_values[8])]

            # Do further processing with the extracted values
    print(identifier, date_time, magnitude, depth, location, level, longitude, latitude)
    # print(len(identifier), len(date_time), len(magnitude), len(depth), len(location), len(level), len(longitude), len(latitude))
    factory_longitude = [121.01, 120.618, 120.272]
    factory_latitude = [24.773, 24.2115, 23.1135]
    factory_si = [1.758, 1.063, 1.968]
    factory_PGA = []
    for i, l in enumerate(level):
        if int(l) > 3:
            PGA = []
            for j in range(len(factory_si)):
                r = np.sqrt(depth[i] ** 2 + calculate_distance(factory_longitude[j], factory_latitude[j], longitude[i], latitude[i]) ** 2)
                PGA += [1.657 * np.exp(1.533*magnitude[i]) * (r**-1.607) * factory_si[j]]
            factory_PGA += [PGA]
    print(factory_PGA)
   
    # Close the webdriver
    driver.quit()


   





if __name__ == "__main__":
    reservoir_crawler()
    # electricity_crawler()
    # earthquake_crawler()