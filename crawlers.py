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

import json
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


def craw_reservoir_by_date(year, month, day, hour = 0, reservoir = ["石門水庫", "寶山第二水庫", "永和山水庫", "鯉魚潭水庫", "德基水庫",
        "南化水庫", "曾文水庫", "烏山頭水庫"]):
    
    payload = {}
    headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    url = 'https://fhy.wra.gov.tw/ReservoirPage_2011/Statistics.aspx'

    # print(year, month, day, hour)
    max_retries = 100
    retry_delay = 1  # Delay in seconds between retries

    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.post(url, data=payload, headers=headers)
            # Process the response
            if response.status_code == 200:
                # Request was successful
                break  # Exit the loop if the request succeeds
        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            # Handle the exception
            pass
        
        # Wait for the specified delay before retrying
        # time.sleep(retry_delay)
        retry_count += 1
    # print("!!!!!!!!!!!!!!!!!!!!!!!")

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the input element with name '__VIEWSTATE'
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        # viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
        payload['__VIEWSTATE'] = viewstate['value']
        # payload['__VIEWSTATEGENERATOR'] = viewstategenerator['value']
        payload['__EVENTVALIDATION'] = eventvalidation['value']
        # print(viewstate['value'])
        # print(eventvalidation['value'])
        payload['__EVENTTARGET'] = 'ctl00$cphMain$btnQuery'
        payload['ctl00$cphMain$cboSearch'] = '防汛重點水庫'
        payload['ctl00$cphMain$ucDate$cboYear'] = str(year)
        payload['ctl00$cphMain$ucDate$cboMonth'] = str(month)
        payload['ctl00$cphMain$ucDate$cboDay'] = str(day)
        payload['ctl00$cphMain$ucDate$cboHour'] = str(hour)
        payload['ctl00$cphMain$ucDate$cboMinute'] = '0'
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = requests.post(url, data=payload, headers=headers)
                # Process the response
                if response.status_code == 200:
                    # Request was successful
                    break  # Exit the loop if the request succeeds
            except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
                # Handle the exception
                pass
        
            # Wait for the specified delay before retrying
            # time.sleep(retry_delay)
            retry_count += 1
        # print(response.text)

        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'id': 'ctl00_cphMain_gvList'})

        # Find all the rows in the table
        rows = table.find_all('tr')
        # print(rows)
        # Iterate over the rows and extract the data for "石門水庫"
        # print(len(rows))
        data = []
        for row in rows:
            # print(row)
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            columns = row.find_all('td')
            # print(columns)
            # print(len(columns))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            if len(columns) and columns[0].text.strip() in reservoir:
                # Extract the required numeric data from the columns
                data += [[columns[0].text.strip(), columns[1].text.strip().replace(' ', '-'), columns[2].text.strip(), columns[3].text.strip(), columns[4].text.strip(),
                columns[5].text.strip(), columns[6].text.strip(), columns[7].text.strip(), columns[8].text.strip(), columns[9].text.strip(), columns[10].text.strip(),
                columns[11].text.strip(), columns[12].text.strip(), columns[13].text.strip(), columns[14].text.strip(), columns[15].text.strip(), columns[16].text.strip(),
                columns[17].text.strip()]]
                for i in range(2, len(data[-1])):
                    if not len(data[-1][i]):
                        data[-1][i] = "--"
                    elif len(data[-1][i]) and data[-1][i][0].isdigit():
                        if i == 7:
                            data[-1][i] = float(data[-1][i][:-2].replace(',', ''))
                        else:
                            data[-1][i] = float(data[-1][i].replace(',', ''))
    else:
        print('Request failed with status code:', response.status_code)       
    return data


def reservoir_crawler(year1, month1, day1, year2, month2, day2, reservoir = ["石門水庫", "寶山第二水庫", "永和山水庫", "鯉魚潭水庫", "德基水庫", 
                                                                                 "南化水庫", "曾文水庫", "烏山頭水庫"]):
    '''
    水情時間: time
    有效蓄水量(萬立方公尺): effective_storage_capacity
    蓄水百分比(%): storage_ratio

    竹 石門水庫、寶山第二水庫、(寶山水庫)、永和山水庫
    中 鯉魚潭水庫、德基水庫
    南 南化水庫、曾文水庫、烏山頭水庫
    '''

    month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    time = []
    effective_storage_capacity = []
    storage_ratio = []

    data = []
    # first year
    if year1 < year2:
        for m in range(month1, 13):
            if m == month1:
                for d in range(day1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h, reservoir)
            else:
                for d in range(1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h, reservoir)
    if year1 + 1 < year2:
        for y in range(year1 + 1, year2):
            for m in range(1, 13):
                for d in range(1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(y, m, d, h, reservoir)
    if year1 == year2:
        for m in range(month1, month2+1):
            if m == month1 == month2:
                for d in range(day1, day2+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h, reservoir)
            elif m == month1:
                for d in range(day1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h, reservoir)
            elif m == month2:
                for d in range(1, day2+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h, reservoir)
            else:
                for d in range(1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year1, m, d, h, reservoir)
    else:
        for m in range(1, month2+1):
            if m == month2:
                for d in range(1, day2+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year2, m, d, h, reservoir)
            else:
                for d in range(1, month[m-1]+1):
                    for h in range(24):
                        data += craw_reservoir_by_date(year2, m, d, h, reservoir)

    columns = ['水庫名稱', '時間', '本日集水區累積降雨量(mm)', '進流量(cms)', '水位(公尺)', '滿水位(公尺)', '有效蓄水量(萬立方公尺)', 
    '蓄水百分比(%)', '取水流量(cms)', '發電放水口', '排砂道/PRO', '排洪隧道', '溢洪道', '其他', '小計', '目前狀態', '預定時間', '預定放流量(cms)']
		
							
    df = pd.DataFrame(data, columns=columns)
    df = df.replace('--', float('nan'))

    return df


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

    return df



def history_earthquake_crawler():
    
    columns = ['區', '時間', '震度階級', "震央經度", "震央緯度", "震央規模", "震央深度", "震央震度階級"]
    area = ['北', '中', '南']

    url = 'https://scweb.cwb.gov.tw/zh-tw/history/ajaxhandler'

    payload = {
        'draw': '3',
        'columns[0][data]': '0',
        'columns[0][name]': 'eqDate',
        'columns[0][searchable]': 'true',
        'columns[0][orderable]': 'true',
        'columns[0][search][value]': '',
        'columns[0][search][regex]': 'false',
        'columns[1][data]': '1',
        'columns[1][name]': 'EastLongitude',
        'columns[1][searchable]': 'true',
        'columns[1][orderable]': 'true',
        'columns[1][search][value]': '',
        'columns[1][search][regex]': 'false',
        'columns[2][data]': '2',
        'columns[2][name]': 'NorthLatitude',
        'columns[2][searchable]': 'true',
        'columns[2][orderable]': 'true',
        'columns[2][search][value]': '',
        'columns[2][search][regex]': 'false',
        'columns[3][data]': '3',
        'columns[3][name]': 'Magnitude',
        'columns[3][searchable]': 'true',
        'columns[3][orderable]': 'true',
        'columns[3][search][value]': '',
        'columns[3][search][regex]': 'false',
        'columns[4][data]': '4',
        'columns[4][name]': 'Depth',
        'columns[4][searchable]': 'true',
        'columns[4][orderable]': 'true',
        'columns[4][search][value]': '',
        'columns[4][search][regex]': 'false',
        'order[0][column]': '0',
        'order[0][dir]': 'desc',
        'start': '0',
        'length': '-1',
        'search[value]': '',
        'search[regex]': 'false',
        'EQType': '1',
        'StartDate': '2017-01-01',
        'EndDate': '2022-12-04',
        'magnitudeFrom': '0',
        'magnitudeTo': '10',
        'depthFrom': '0',
        'depthTo': '350',
        'minLong': '',
        'maxLong': '',
        'minLat': '',
        'maxLat': '',
        'ddlCity': '',
        'ddlTown': '',
        'ddlStation': '',
        'txtIntensityB': '',
        'txtIntensityE': '',
        'txtLon': '',
        'txtLat': '',
        'txtKM': ''
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        row = response.json()
        # Process the received data as needed
        # print(row['data'])
        # print(row['data'][20])
        # print(len(row['data']))
    
    factory_longitude = [121.01, 120.618, 120.272]
    factory_latitude = [24.773, 24.2115, 23.1135]
    factory_si = [1.758, 1.063, 1.968]
    data = []
    
    # __, date time, longitude, latitude, magnitude, depth, level
    for r in row['data']:
        # r = r.split(',')
        for j in range(len(factory_si)):
            r_ = np.sqrt(float(r[5]) ** 2 + calculate_distance(factory_longitude[j], factory_latitude[j], float(r[2]), float(r[3])) ** 2)
            PGA = 1.657 * np.exp(1.533*float(r[4])) * (r_**-1.607) * factory_si[j]
            if int(r[6]) >= 5:
                data += [[area[j], r[1].replace(' ', '-'), to_level(PGA/8.6561, int(r[6])), float(r[2]), float(r[3]), float(r[4]), float(r[5]), r[6]]]
            else:
                data += [[area[j], r[1].replace(' ', '-'), to_level(PGA, int(r[6])), float(r[2]), float(r[3]), float(r[4]), float(r[5]), r[6]]]

    # print(data)
    # print(len(data))
    df = pd.DataFrame(data, columns=columns)
    df = df.replace('--', float('nan'))

    return df

def current_earthquake_crawler():
    
    columns = ['區', '時間', '震度階級', "震央經度", "震央緯度", "震央規模", "震央深度", "震央震度階級"]
    area = ['北', '中', '南']
    # # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode

    ## load config from config.json
    with open("./config.json") as config_file:
        config = json.load(config_file)
    
    webdriver_service = Service(config['chromedriver_path'])

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.get('https://scweb.cwb.gov.tw/')

    # Start the webdriver
    # driver = webdriver.Chrome()
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # body = driver.find_element(By.TAG_NAME, "body")
    # body.send_keys(Keys.END)
    # time.sleep(10)
    # Load the webpage

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
            date_time += [location_values[2].replace(' ', '-')]
            magnitude += [float(location_values[3])]
            depth += [float(location_values[4])]
            location += [location_values[5]]
            levels += [location_values[6]]
            longitude += [float(location_values[7])]
            latitude += [float(location_values[8])]
    # Close the webdriver
    driver.quit()

    # print(identifier, date_time, magnitude, depth, location, levels, longitude, latitude)
    # print(len(identifier), len(date_time), len(magnitude), len(depth), len(location), len(level), len(longitude), len(latitude))
    factory_longitude = [121.01, 120.618, 120.272]
    factory_latitude = [24.773, 24.2115, 23.1135]
    factory_si = [1.758, 1.063, 1.968]
    data = []
    
    for i, l in enumerate(levels):
        for j in range(len(factory_si)):
            r = np.sqrt(depth[i] ** 2 + calculate_distance(factory_longitude[j], factory_latitude[j], longitude[i], latitude[i]) ** 2)
            PGA = 1.657 * np.exp(1.533*magnitude[i]) * (r**-1.607) * factory_si[j]
            if int(l) >= 5:
                data += [[area[j], date_time[i], to_level(PGA/8.6561, int(l)), float(longitude[i]), float(latitude[i]),
                          float(magnitude[i]), float(depth[i]), int(l)]]
            else:
                data += [[area[j], date_time[i], to_level(PGA, int(l)), float(longitude[i]), float(latitude[i]), float(magnitude[i]), float(depth[i]), int(l)]]
                
    df = pd.DataFrame(data, columns=columns)
    df = df.replace('--', float('nan'))

    return df