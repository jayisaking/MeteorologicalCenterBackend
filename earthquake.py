from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import psycopg2
from pydantic import BaseModel
from typing import Union
from datetime import datetime, timedelta
app = FastAPI()
from crawlers import *
import uvicorn

request_set = set()

# Load the contents of config.json
with open("./config.json") as config_file:
            config = json.load(config_file)
            
origins = config["data_allowed_origins"]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

## clip number into a min, max range
def clip(number, min, max):
    if number < min:
        return min
    elif number > max:
        return max
    else:
        return number

class EarthquakeItem(BaseModel):
    year_from: int = 2023
    month_from: int = 1
    day_from: int = 1
    hour_from: int = 0
    minute_from: int = 0
    second_from: float = 0
    
    year_to: int = 2023
    month_to: int = 1
    day_to: int = 1
    hour_to: int = 0
    minute_to: int = 0
    second_to: float = 0
    
    past_hours: Union[int, None] = None
    
    past_days: Union[int, None] = None
    
    past_months: Union[int, None] = None
    
    earthquake_regions: list

@app.post("/earthquake_fetch/")
async def earthquake_fetch(earthquake_item: EarthquakeItem):
    time_end = datetime(clip(earthquake_item.year_to, 2000, 3000), clip(earthquake_item.month_to, 1, 12),
                                        clip(earthquake_item.day_to, 1, 31), clip(earthquake_item.hour_to, 0, 60), clip(earthquake_item.minute_to, 0, 60), clip(earthquake_item.second_to, 0, 60))
    time_start = None
    
    if earthquake_item.past_months is not None:
        time_start = time_end - timedelta(days = max(earthquake_item.past_months * 30, 0))
    if earthquake_item.past_days is not None:
        time_start = time_end - timedelta(days = max(earthquake_item.past_days, 0))
    if earthquake_item.past_hours is not None:
        time_start = time_end - timedelta(hours = max(earthquake_item.past_hours, 0))
    if time_start is None:
        time_start = datetime(clip(earthquake_item.year_from, 2000, 3000), clip(earthquake_item.month_from, 1, 12),
                                        clip(earthquake_item.day_from, 1, 31), clip(earthquake_item.hour_from, 0, 60), clip(earthquake_item.minute_from, 0, 60), clip(earthquake_item.second_from, 0, 60))
    if str(earthquake_item.earthquake_regions) + str(time_start) + str(time_end) not in request_set:
        exists = check_earthquake_data_exists(earthquake_item.earthquake_regions, time_start, time_end)
        if not all(exists):
            crawl_earthquake_and_store()
        request_set.add(str(earthquake_item.earthquake_regions) + str(time_start) + str(time_end))
    
    ## get data from database
    with psycopg2.connect(database = config['db_name'], user = config['db_user'], password = config['db_password'],
                          host = config['db_host'], port = config['db_port']) as conn:
        with conn.cursor() as cur:
            result = []
            for earthquake_region in earthquake_item.earthquake_regions:
                sql = f"SELECT * FROM {config['earthquake_schema']}.{config['earthquake_tables'][0]['name']} WHERE 時間 >= \'{time_start}\' AND 時間 <= \'{time_end}\' AND 區 = \'{earthquake_region}\'"
                cur.execute(sql)
                ## fetch with column names
                columns = [desc[0] for desc in cur.description]
                result += [pd.DataFrame(cur.fetchall(), columns = columns)]
            result = pd.concat(result)
            result = result.sort_values(by = ['區', '時間'])
            result = result.reset_index(drop = True)
    earthquake_region_names = result['區'].unique()
    json_data = []
    
    for earthquake_region_name in earthquake_region_names:
        data = {}
        data['區'] = earthquake_region_name
        for column in result.columns:
            if column != '區':
                if column == '時間':
                    data[column] = [str(i) for i in result[result['區'] == earthquake_region_name][column]]
                else:
                    data[column] = [i for i in result[result['區'] == earthquake_region_name][column]]        
        json_data.append(data)
        
    return {"data": json_data}
    
    
def check_earthquake_data_exists(earthquake_regions, time_start, time_end):
    exists = []
    for earthquake_region in earthquake_regions:
        with psycopg2.connect(database = config['db_name'], user = config['db_user'], password = config['db_password'], 
                        host = config['db_host'], port = config['db_port']) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT EXISTS(SELECT 1 FROM {config['earthquake_schema']}.{config['earthquake_tables'][0]['name']} WHERE 時間 >= \'{time_start}\' AND 時間 <= \'{time_end}\' AND 區 = \'{earthquake_region}\')")
                exist = cur.fetchone()[0]
                exists.append(exist)
    return exists
def crawl_earthquake_and_store():
    data = history_earthquake_crawler()
    insert_dataframe_to_database(data)

def insert_dataframe_to_database(df: pd.DataFrame, time_format = '%Y-%m-%d-%H:%M:%S'):
    df.fillna(-1, inplace = True)
    with psycopg2.connect(database = config['db_name'], user = config['db_user'], password = config['db_password'],
                                host = config['db_host'], port = config['db_port']) as conn:
        columns = ", ".join(f'"{column}"'.replace("%", "%%") for column in config['earthquake_tables'][0]['columns'])
        values = ", ".join(["%s" for _ in config['earthquake_tables'][0]['columns']])  
        sql = f"INSERT INTO {config['earthquake_schema']}.{config['earthquake_tables'][0]['name']} ({columns}) VALUES ({values}) ON CONFLICT DO NOTHING"
        
        with conn.cursor() as cur:
            for i in range(len(df)):
                params = tuple([datetime.strptime(df.iloc[i][column_name], time_format) if type_name.startswith("TIMESTAMP") else str(df.iloc[i][column_name])
                                for column_name, type_name in zip(config['earthquake_tables'][0]['columns'], config['earthquake_tables'][0]['types'])])
                cur.execute(sql, params)
            conn.commit()
    
## start server
if __name__ == "__main__":
    uvicorn.run(app = "earthquake:app", host = config["earthquake_host"], port = config["earthquake_port"], reload = True)