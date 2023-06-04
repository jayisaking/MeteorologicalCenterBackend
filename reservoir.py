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


class ReservoirItem(BaseModel):
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
    
    reservoir_names: list
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = config["data_allowed_origins"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

@app.post("/reservoir_fetch/")
async def reservoir_fetch(reservoir_item: ReservoirItem):
    ## parse date to datetime object from the item 
    time_end = datetime(clip(reservoir_item.year_to, 2000, 3000), clip(reservoir_item.month_to, 1, 12), 
                                   clip(reservoir_item.day_to, 1, 31), clip(reservoir_item.hour_to, 0, 60), clip(reservoir_item.minute_to, 0, 60), clip(reservoir_item.second_to, 0, 60))
    if reservoir_item.past_hours is not None:
        time_start = time_end - timedelta(hours = max(reservoir_item.past_hours, 0))
    else:
        time_start = datetime(clip(reservoir_item.year_from, 2000, 3000), clip(reservoir_item.month_from, 1, 12), 
                                   clip(reservoir_item.day_from, 1, 31), clip(reservoir_item.hour_from, 0, 60), clip(reservoir_item.minute_from, 0, 60), clip(reservoir_item.second_from, 0, 60))
    exists = check_reservoir_data_exists(reservoir_item.reservoir_names, time_start, time_end)
    if not all(exists):
        crawl_reservoir_and_store(time_start, time_end, [reservoir_item.reservoir_names[i] for i in range(len(exists)) if not exists[i]])

    ## get data from database
    with psycopg2.connect(database = config['db_name'], user = config['db_user'], password = config['db_password'], host = config['db_host'], port = config['db_port']) as conn:
        with conn.cursor() as cur:
            result = []
            for reservoir_name in reservoir_item.reservoir_names:
                cur.execute(f"SELECT * FROM {config['reservoir_schema']}.{config['reservoir_tables'][0]['name']} WHERE 時間 >= \'{time_start}\' AND 時間 <= \'{time_end}\' AND 水庫名稱 = \'{reservoir_name}\'")
                ## fetch with column names
                columns = [desc[0] for desc in cur.description]
                result += [pd.DataFrame(cur.fetchall(), columns = columns)]
            result = pd.concat(result)
            result = result.sort_values(by = ['水庫名稱', '時間'])
            result = result.reset_index(drop = True)
    ## get unique values of 水庫名稱
    reservoir_names = result['水庫名稱'].unique()
    json_data = []
    ## for each 水庫名稱
    for reservoir_name in reservoir_names:
        ## create a dict with other columns in result
        data = {}
        data['水庫名稱'] = reservoir_name
        for column in result.columns:
            if column != '水庫名稱':
                ## if the column is time stamp, turn it to string
                if column == '時間':
                    data[column] = [str(i) for i in result[result['水庫名稱'] == reservoir_name][column]]
                else:
                    data[column] = [i for i in result[result['水庫名稱'] == reservoir_name][column]]
        json_data += [data]        
    
    return { "data": json_data }
    
## check if data exists in database at certain time interval
def check_reservoir_data_exists(reservoirs, time_start, time_end):
    '''
    reservoirs : [names]
    time_start : datetime
    time_end : datetime
    '''
    
    # connect to the database
    with psycopg2.connect(database = config['db_name'], user = config['db_user'], password = config['db_password'], host = config['db_host'], port = config['db_port']) as conn:

        with conn.cursor() as cur:
            result = []
            for reservoir in reservoirs:
                cur.execute(f"SELECT EXISTS(SELECT * FROM {config['reservoir_schema']}.{config['reservoir_tables'][0]['name']} WHERE 時間 >= \'{time_start}\' AND 時間 <= \'{time_end}\' AND 水庫名稱 = \'{reservoir}\')")
                result.append(cur.fetchone()[0])
            return result
def crawl_reservoir_and_store(time_start, time_end, reservoirs):
    '''
    time_start : datetime
    time_end : datetime
    reservoirs : [names]
    '''
    data = reservoir_crawler(time_start.year, time_start.month, time_start.day, time_end.year, time_end.month, time_end.day, reservoirs)
    insert_dataframe_to_database(data)
    
def insert_dataframe_to_database(df: pd.DataFrame, time_format = "%Y-%m-%d-%H:%M:%S"):
    df.fillna(-1, inplace=True)
    
    # Connect to the database
    with psycopg2.connect(database=config['db_name'], user=config['db_user'], password=config['db_password'], host=config['db_host'], port=config['db_port']) as conn:
        columns = ", ".join(f'"{column}"'.replace("%", "%%") for column in config['reservoir_tables'][0]['columns'])
        values = ", ".join("%s" for _ in config['reservoir_tables'][0]['columns'])
        sql = f"INSERT INTO {config['reservoir_schema']}.{config['reservoir_tables'][0]['name']} ({columns}) VALUES ({values}) ON CONFLICT DO NOTHING"
        
        with conn.cursor() as cur:
            for i in range(len(df)):
                params = tuple(
                    datetime.strptime(df.iloc[i][column_name], time_format) if type_name.startswith('TIMESTAMP') else df.iloc[i][column_name]
                    for column_name, type_name in zip(config['reservoir_tables'][0]['columns'], config['reservoir_tables'][0]['types'])
                )
                cur.execute(sql, params)
                
            conn.commit()


if __name__ == "__main__":
    uvicorn.run(app = "reservoir:app", host = config["reservoir_host"], port = config["reservoir_port"], reload = True)