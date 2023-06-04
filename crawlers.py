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
    else:import re
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
    
    # if year < 1970 or year >
    

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

