import re
import time
import math
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys



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

def to_level(PGA, level):
    levels = [0, 1, 2, 3, 4, 5, 5.5, 6, 6.5, 7]
    PGAs = [0.8, 2.5, 8, 25, 80, 140, 250, 440, 800]
    if level >= 5:
        PGAs = [0.2, 0.7, 1.9, 5.7, 15, 30, 50, 80, 140]
    l, r = 0, len(PGAs) - 1
    while l <= r:
        m = (l + r) // 2 
        # print(l, m, r)
        if PGAs[m] < PGA:
            l = m + 1
        else:
            r = m - 1
    return levels[l]


def craw_reservoir_by_date(year, month, day, hour=0):
    
    # if year < 1970 or year >
    reservoir = ["石門水庫", "寶山第二水庫", "永和山水庫", "鯉魚潭水庫", "德基水庫",
    "南化水庫", "曾文水庫", "烏山頭水庫"]

    times = []
    effective_storage_capacity = []
    storage_ratio = []

    # # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode

    # Set up the ChromeDriver service
    webdriver_service = Service("chromedriver")

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.get("https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx")

    # print(driver.page_source)
    # Locate the year dropdown menu
    year_dropdown = driver.find_element(By.ID, 'ctl00_cphMain_ucDate_cboYear')

    # Create a Select object for the dropdown
    year_select = Select(year_dropdown)

    # Select the desired year
    year_select.select_by_value(str(year))

    # Locate the month dropdown menu
    month_dropdown = driver.find_element(By.ID, 'ctl00_cphMain_ucDate_cboMonth')

    # Create a Select object for the dropdown
    month_select = Select(month_dropdown)

    # Select the desired month
    month_select.select_by_value(str(month))

    # Locate the day dropdown menu
    day_dropdown = driver.find_element(By.ID, 'ctl00_cphMain_ucDate_cboDay')

    # Create a Select object for the dropdown
    day_select = Select(day_dropdown)

    # Select the desired day
    day_select.select_by_value(str(day))

    hour_dropdown = driver.find_element(By.ID, 'ctl00_cphMain_ucDate_cboHour')

    # Create a Select object for the dropdown
    hour_select = Select(hour_dropdown)

    # Select the desired hour
    hour_select.select_by_value(str(hour))

    # print(driver.page_source)
    submit_button = driver.find_element(By.ID, 'ctl00_cphMain_btnQuery')
    submit_button.click()

    # Wait for the data to be displayed (You can use WebDriverWait if needed)
    time.sleep(0.2)

    # Extract the data from the page
    data_element = driver.find_element(By.ID, 'ctl00_cphMain_gvList')
    data = [] 
    for d in data_element.text.split('\n'):
        d = d.split(' ')
        if d[0] in reservoir:
            data += [d[:9]+d[10:]]
            data[-1][1] += ('-' + data[-1][2])
            for i in range(3, len(data[-1])):
                if data[-1][i][0].isdigit():
                    data[-1][i-1] = float(data[-1][i].replace(',', ''))
                else:
                    data[-1][i-1] = data[-1][i]
            data[-1].pop()
            
    # print(data)
    # print(len(data))
    return data

def reservoir_crawler(year1, month1, day1, year2, month2, day2):
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
    month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    data = []
    # first year
    if year1 < year2:
        for m in range(month1, 13):
            if m == month1:
                for d in range(day1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h)
            else:
                for d in range(1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h)
    if year1 + 1 < year2:
        for y in range(year1 + 1, year2):
            for m in range(1, 13):
                for d in range(1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(y, m, d, h)
    if year1 == year2:
        for m in range(month1, month2+1):
            if m == month1 == month2:
                for d in range(day1, day2+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h)
            elif m == month1:
                for d in range(day1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h)
            elif m == month2:
                for d in range(1, day2+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h)
            else:
                for d in range(1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h)
    else:
        for m in range(1, month2+1):
            if m == month2:
                for d in range(1, day2+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year2, m, d, h)
            else:
                for d in range(1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year2, m, d, h)
    # print(data)
    # print(len(data))
    # print(len(data[0]))

    columns = ['水庫名稱', '時間', '本日集水區累積降雨量(mm)', '進流量(cms)', '水位(公尺)', '滿水位(公尺)', '有效蓄水量(萬立方公尺)', 
    '蓄水百分比(%)', '取水流量(cms)', '發電放水口', '排砂道/PRO', '排洪隧道', '溢洪道', '其他', '小計', '目前狀態', '預定時間', '預定放流量(cms)']
		
							
    # print(len(columns))
    df = pd.DataFrame(data, columns=columns)
    df = df.replace('--', float('nan'))
    df.set_index('水庫名稱', inplace=True)
    # reservoir_name = '石門水庫'
    # data_value = df.loc[reservoir_name]
    # print(data_value)

    return df



def craw_electricity_by_date(year, month, day):
    
    # # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run Chrome in headless mode

    # Set up the ChromeDriver service
    webdriver_service = Service("chromedriver")

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.get("https://www.taipower.com.tw/tc/page.aspx?mid=210&cid=340&cchk=eac92988-526f-44e3-a911-1564395de297")
    # Find the iframe element
    # iframe = driver.find_element(By.XPATH, '//div[@id="about_box"]/div[@class="animation"]/p/iframe')
    # Find the iframe element
    # time.sleep(20)
    try:
        iframe = driver.find_element(By.ID, 'IframeId')
    except:
        print(f"Failed at {year}-{month}-{day}")

    driver.switch_to.frame(iframe)
    # date_picker = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, 'datepicker')))
    # date_picker = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "datepicker")))
    date_picker = driver.find_element(By.ID, "datepicker")
    month = str(month) if month > 9 else '0' + str(month)
    day = str(day) if day > 9 else '0' + str(day)
    date = str(year) + month + day
    # driver.execute_script("arguments[0].setAttribute('style', 'border: 2px solid red;');", date_picker)
    driver.execute_script("arguments[0].value = arguments[1];", date_picker, date)
    # driver.execute_script("arguments[0].value = '20230411';", date_picker)
    # driver.execute_script("arguments[0].click();", date_picker)
    # Press the Enter key
    date_picker.send_keys(Keys.ENTER)
    date_picker.send_keys(Keys.ENTER)
    # driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_picker)

    time.sleep(3)
    # date_picker.click()

    # print(driver.page_source)
    supply = float(driver.find_element(By.ID, "supply1").text)
    load = float(driver.find_element(By.ID, "load1").text)
    date = driver.find_element(By.ID, "date1").text[:-5].replace('/', '-')
    supply_ratio = [0.245, 0.274, 0.476]
    load_ratio = [0.358, 0.27, 0.357]
    area = ['北', '中', '南']
    data = []
    for i in range(len(supply_ratio)):
        data += [[area[i], date, round(supply * supply_ratio[i], 6), round(load * load_ratio[i], 6)]]
    # print(supply, load, date)

    return data
    
def electricity_crawler():
    '''
    2022/01 - 2023/04
    '''

    url = 'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/sys_dem_sup.csv'

    response = requests.get(url)

    if response.status_code == 200:
        rows = response.text.split('\n')
        
    columns = ['區', '時間', '供電(萬瓩)', '負載(萬瓩)']
    supply_ratio = [0.245, 0.274, 0.476]
    load_ratio = [0.358, 0.27, 0.357]
    area = ['北', '中', '南']
    data = []
    for r in rows:
        if r:
            r = r.split(',')
            data_ = []
            for i in range(len(supply_ratio)):
                data_ += [[area[i], r[0], float(r[1]) * supply_ratio[i] / 10, float(r[2]) * load_ratio[i] / 10]]
            data += data_
    
    # print(data)
    # print(len(data))
    df = pd.DataFrame(data, columns=columns)
    df = df.replace('--', float('nan'))
    df.set_index('區', inplace=True)

    return df

def test():

    url = 'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/sys_dem_sup.csv'

    response = requests.get(url)

    if response.status_code == 200:
        data = response.text
        print(len(data))
        print(len(data.split('\n')))
        # Process the data as needed
    else:
        print('Error: Failed to fetch data from the API')


def earthquake_crawler():

    # # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode

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
    levels = []
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
            levels += [location_values[6]]
            longitude += [float(location_values[7])]
            latitude += [float(location_values[8])]

            # Do further processing with the extracted values
    print(identifier, date_time, magnitude, depth, location, levels, longitude, latitude)
    # print(len(identifier), len(date_time), len(magnitude), len(depth), len(location), len(level), len(longitude), len(latitude))
    factory_longitude = [121.01, 120.618, 120.272]
    factory_latitude = [24.773, 24.2115, 23.1135]
    factory_si = [1.758, 1.063, 1.968]
    factory_level = []
    for i, l in enumerate(levels):
        if int(l) > 3:
            level = []
            for j in range(len(factory_si)):
                r = np.sqrt(depth[i] ** 2 + calculate_distance(factory_longitude[j], factory_latitude[j], longitude[i], latitude[i]) ** 2)
                PGA = 1.657 * np.exp(1.533*magnitude[i]) * (r**-1.607) * factory_si[j]
                if int(l) >= 5:
                    level += [to_level(PGA/8.6561, int(l))]
                else:
                    level += [to_level(PGA, int(l))]
            factory_level += [level]
    print(factory_level)
   
    # Close the webdriver
    driver.quit()


   





if __name__ == "__main__":
    # reservoir_crawler(2022, 4, 11, 2022, 4, 11)
    electricity_crawler()
    # earthquake_crawler()
    # craw_electricity_by_date(2023, 4, 11)
    # test()