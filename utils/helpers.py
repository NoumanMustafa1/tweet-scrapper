import os
import time
import json
import pandas as pd
from datetime import datetime

def read_text(filepath):
    
    with open(filepath,encoding="utf-8") as f:
        return f.read()


def save_csv(data,save_path):
        
        df = pd.DataFrame(data)
        df.to_csv(save_path,index=False)
        return True
    

def save_json(save_path, data):
    
        with open(save_path,"w",encoding="utf-8") as f:
            json.dump(data, f)
    
def read_csv(path):
    return pd.read_csv(path)
    
def get_time_period(start_day=1675262149):
    """
    start_day = epoch start day
    """
    return int(time.time()) - int(start_day)

def process_keyword(keywords):
    keywords = keywords.replace("#","")
    return keywords.split("\n")


# tweet_response={}
# DATABASE_DIR="DB"
# tweet_response["keyword"] ="text"
# db_path=os.path.join(DATABASE_DIR,f'{tweet_response["keyword"]}')
# csv_path =os.path.join(db_path,f'{tweet_response["keyword"]}_result.csv')
# print("db_path:",db_path)
# print("csv_path:",csv_path)