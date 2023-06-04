import psycopg2
import json

# load config file
with open("./config.json") as config_file:
    config = json.load(config_file)

# connect to database
conn = psycopg2.connect(database = config['db_name'], user = config['db_user'], password = config['db_password'], 
                        host = config['db_host'], port = config['db_port'])

with conn.cursor() as cur:
    ## check if schema and table exist, if not, create them
    
    ### reservoir
    cur.execute(f"SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = \'{config['reservoir_schema']}\')")
    exist = cur.fetchone()[0]
    if not exist:
        cur.execute(f"CREATE SCHEMA {config['reservoir_schema']}")
        conn.commit()
    for reservoir_table in config['reservoir_tables']: 
        cur.execute(f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = \'{config['reservoir_schema']}\' AND table_name = \'{reservoir_table['name']}\')")
        exist = cur.fetchone()[0]
        if not exist:
            ## create table according to columns and types in config file
            columns = ""
            for column, type in zip(reservoir_table['columns'], reservoir_table['types']):
                columns += f"\"{column}\" {type}, "
            columns = columns[:-2]
            primary_keys = ", ".join(reservoir_table['primary_keys'])
            cur.execute(f"CREATE TABLE {config['reservoir_schema']}.{reservoir_table['name']} ({columns}, PRIMARY KEY ({primary_keys}));")
            conn.commit()
            
    
    ### electricity
    cur.execute(f"SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = \'{config['electricity_schema']}\')")
    exist = cur.fetchone()[0]
    if not exist:
        cur.execute(f"CREATE SCHEMA {config['electricity_schema']}")
        conn.commit()
    for electricity_table in config['electricity_tables']: 
        cur.execute(f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = \'{config['electricity_schema']}\' AND table_name = \'{electricity_table['name']}\')")
        exist = cur.fetchone()[0]
        if not exist:
            ## create table according to columns and types in config file
            columns = ""
            for column, type in zip(electricity_table['columns'], electricity_table['types']):
                columns += f"\"{column}\" {type}, "
            columns = columns[:-2]
            primary_keys = ", ".join(electricity_table['primary_keys'])
            cur.execute(f"CREATE TABLE {config['electricity_schema']}.{electricity_table['name']} ({columns}, PRIMARY KEY ({primary_keys}));")
            conn.commit()
    
    ### earthquake
    cur.execute(f"SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = \'{config['earthquake_schema']}\')")
    exist = cur.fetchone()[0]
    if not exist:
        cur.execute(f"CREATE SCHEMA {config['earthquake_schema']}")
        conn.commit()
    for earthquake_table in config['earthquake_tables']: 
        cur.execute(f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = \'{config['earthquake_schema']}\' AND table_name = \'{earthquake_table['name']}\')")
        exist = cur.fetchone()[0]
        if not exist:
            ## create table according to columns and types in config file
            columns = ""
            for column, type in zip(earthquake_table['columns'], earthquake_table['types']):
                columns += f"\"{column}\" {type}, "
            columns = columns[:-2]
            primary_keys = ", ".join(earthquake_table['primary_keys'])
            cur.execute(f"CREATE TABLE {config['earthquake_schema']}.{earthquake_table['name']} ({columns}, PRIMARY KEY ({primary_keys}));")
            conn.commit()
    