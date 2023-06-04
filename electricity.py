import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from crawlers import *
from pydantic import BaseModel
from typing import Union
from datetime import datetime, timedelta

## clip values
def clip(number, min, max):
    if number < min:
        return min
    elif number > max:
        return max
    else:
        return number

## load the config file as config
with open("./config.json") as config_file:
    config = json.load(config_file)

class ElectricityItem(BaseModel):
    year_from: int = 2023
    month_from: int = 1
    day_from: int = 1
    hour_from: int = 0
    minute_from: int = 0
    second_from: int = 0
    
    year_to: int = 2023
    month_to: int = 1
    day_to: int = 1
    hour_to: int = 0
    minute_to: int = 0
    second_to: int = 0
    
    past_days: Union[int, None] = None
    
    power_plant_regions: list

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = config["data_allowed_origins"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)



@app.post("/electricity_fetch/")
async def electricity_fetch(electricity_item: ElectricityItem):
    time_end = datetime(clip(electricity_item.year_to, 2000, 3000), clip(electricity_item.month_to, 1, 12),
                                      clip(electricity_item.day_to, 1, 31), clip(electricity_item.hour_to, 0, 60), clip(electricity_item.minute_to, 0, 60), clip(electricity_item.second_to, 0, 60))
    if electricity_item.past_days is not None:
        time_start = time_end - timedelta(days = max(electricity_item.past_days, 0))
    else:
        time_start = datetime(clip(electricity_item.year_from, 2000, 3000), clip(electricity_item.month_from, 1, 12), 
                                        clip(electricity_item.day_from, 1, 31), clip(electricity_item.hour_from, 0, 60), clip(electricity_item.minute_from, 0, 60), clip(electricity_item.second_from, 0, 60))
    exists = check_electricity_data_exists(electricity_item.power_plant_regions, time_start, time_end)
    if not all(exists):
        crawl_electricity_and_store()
    
    ## get data from database
    with psycopg2.connect(database = config['db_name'], user = config['db_user'], password = config['db_password'],
                          host = config['db_host'], port = config['db_port']) as conn:
        with conn.cursor() as cur:
            result = []
            for power_plant_region in electricity_item.power_plant_regions:
                sql = f"SELECT * FROM {config['electricity_schema']}.{config['electricity_tables'][0]['name']} WHERE 時間 >= \'{time_start}\' AND 時間 <= \'{time_end}\' AND 區 = \'{power_plant_region}\'"
                cur.execute(sql)
                ## fetch with column names
                columns = [desc[0] for desc in cur.description]
                result += [pd.DataFrame(cur.fetchall(), columns = columns)]
            result = pd.concat(result)
            result = result.sort_values(by = ['區', '時間'])
            result = result.reset_index(drop = True)
    power_plant_region_names = result['區'].unique()
    json_data = []
    
    for power_plant_region_name in power_plant_region_names:
        data = {}
        data['區'] = power_plant_region_name
        for column in result.columns:
            if column != '區':
                if column == '時間':
                    data[column] = [str(i) for i in result[result['區'] == power_plant_region_name][column]]
                else:
                    data[column] = [i for i in result[result['區'] == power_plant_region_name][column]]        
        json_data.append(data)
        
    return {"data": json_data}

def check_electricity_data_exists(power_plant_regions, time_start, time_end):
    exists = []
    for power_plant_region in power_plant_regions:
        with psycopg2.connect(database = config['db_name'], user = config['db_user'], password = config['db_password'], 
                            host = config['db_host'], port = config['db_port']) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT EXISTS(SELECT * FROM {config['electricity_schema']}.{config['electricity_tables'][0]['name']} WHERE 時間 >= \'{time_start}\' AND 時間 <= \'{time_end}\'\
                                AND 區 = \'{power_plant_region}\')")
                exists.append(cur.fetchone()[0])
    return exists

def crawl_electricity_and_store():
    data = electricity_crawler()
    insert_dataframe_to_database(data)

def insert_dataframe_to_database(df: pd.DataFrame, time_format = '%Y%m%d_%H_%M_%S'):
    df.fillna(-1, inplace = True)
    
    # connect to the database
    with psycopg2.connect(database = config['db_name'], user = config['db_user'], password = config['db_password'],
                          host = config['db_host'], port = config['db_port']) as conn:
        columns = ", ".join(f'"{column}"'.replace("%", "%%") for column in config['electricity_tables'][0]['columns'])
        values = ", ".join(["%s" for _ in config['electricity_tables'][0]['columns']])  
        sql = f"INSERT INTO {config['electricity_schema']}.{config['electricity_tables'][0]['name']} ({columns}) VALUES ({values}) ON CONFLICT DO NOTHING"
        
        with conn.cursor() as cur:
            for i in range(len(df)):
                params = tuple([datetime.strptime(df.iloc[i][column_name] + "_00_00_00", time_format) if type_name.startswith("TIMESTAMP") else df.iloc[i][column_name]
                                for column_name, type_name in zip(config['electricity_tables'][0]['columns'], config['electricity_tables'][0]['types'])])
                cur.execute(sql, params)
            conn.commit()
            
            
## start server
if __name__ == "__main__":
    uvicorn.run(app = "electricity:app", host = config["electricity_host"], port = config["electricity_port"], reload = True)