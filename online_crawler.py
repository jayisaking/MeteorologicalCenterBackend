from threading import Thread
from earthquake import crawl_earthquake_and_store
from electricity import crawl_electricity_and_store
from reservoir import crawl_reservoir_and_store
from crawlers import *
import json
import time


def current_earthquake():
    from earthquake import insert_dataframe_to_database
    result = current_earthquake_crawler()
    result.fillna(-1, inplace = True)
    insert_dataframe_to_database(result)
        

if __name__ == '__main__':
    ## crawl the earthquake history data and save to database
    crawl_earthquake_and_store()
    
    crawl_electricity_and_store()


    ## load the config file
    with open("./config.json", "r") as config_file:
        config = json.load(config_file)
    
    ## use thread to crawl data every "crawl_every" seconds
    while True:
        Thread(target = crawl_electricity_and_store, args = ()).start()
        Thread(target = current_earthquake, args = ()).start()
        time.sleep(config['crawl_every'])        
        
        
    
    