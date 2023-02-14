import os
import time
import pandas as pd 
from  datetime import datetime  
from snscrape.modules import twitter
from utils import read_text, save_json, save_csv,read_csv,process_keyword

DATABASE_DIR = "database"
CURRENT_TIME = int(time.time()) #get time in epochs
TWEET_KEYWORDS_FILEPATH = "keywords.txt"
START_TIME = read_text("start_date.txt")

class TwitterScrapper:
    def __init__(
        self, 
        keywords, 
        start_time, 
        end_time, 
        tweet_limit):

        self.keywords = keywords
        self.tweet_responses = []
        self.end_time = end_time
        self.start_time = start_time
        self.tweet_limit = tweet_limit
        self.csv_path = []
        with open("timestamp.txt",mode="a+",encoding="UTF-8") as f:
            self.status_log = f.read()


    def update_timestamp(self):
        with open("timestamp.txt",mode="a+",encoding="UTF-8") as f:
             f.write(self.status_log)

    def initiate_search(self):
        for keyword in self.keywords:
            try:
                keyword_tweets=self.get_keyword_tweets(keyword)
                print(f"finding keyword:{keyword} Found :{len(keyword_tweets)}")
                
                self.status_log=self.status_log+"\n"+(f"{CURRENT_TIME} : {keyword}=>{len(keyword_tweets)}")
                self.update_timestamp()
            except Exception as e:
                    self.status_log=self.status_log+"\n"+(f"{CURRENT_TIME} : Exception At getting keyword data=>{e}") 
                    self.update_timestamp()
                    print(e)
            if len(keyword_tweets) !=0:    
                try:
                    keyword_length = len(keyword_tweets)    
                    self.save_keyword_result(keyword_tweets,keyword,keyword_length)
                except Exception as e:
                    self.status_log=self.status_log+"\n"+(f"{CURRENT_TIME} : Exception At generating profile_link=>{e}") 
                    self.update_timestamp()
    def generate_tweet_link(self,screen_name,tweet_id):
        try:
            return f"https://twitter.com/{screen_name}/status/{tweet_id}"

        except Exception as e:
            print(e)
            self.status_log=status_log+"\n"+(f"{CURRENT_TIME} : Exception At generating tweet_link=>{e}")
            self.update_timestamp()
            return ""
    

    def generate_profile_link(self,screen_name):
        try:
            return  f"https://twitter.com/{screen_name}"
             
        except Exception as e:
            print(e)
            self.status_log=status_log+"\n"+(f"{CURRENT_TIME} : Exception At generating profile_link=>{e}")
            self.update_timestamp()
            return ""

    def get_keyword_tweets(self,keyword):
        keyword_tweets = []
        for i,tweet in enumerate(twitter.TwitterSearchScraper(f"{keyword} since:{self.start_time} until:{self.end_time}").get_items()):
            tweet_date = (tweet.date).strftime('%Y-%m-%d %H:%p')
            keyword_tweets.append(
                        {"keyword":keyword,
                        "date":tweet_date,
                        "User Id": tweet.id,
                        "tweet_link":self.generate_tweet_link(tweet.user.username, tweet.id),
                        "profile_link":self.generate_profile_link(tweet.user.username),
                        "screen_name": tweet.user.username})       
            if self.tweet_limit != False and i == self.tweet_limit:break
        return keyword_tweets 
    


    def save_keyword_result(self,keyword_tweets,keyword,length):
        if not os.path.exists(DATABASE_DIR):
            os.makedirs(DATABASE_DIR)
        
        keyword_dir = os.path.join(DATABASE_DIR,keyword)
        if not os.path.exists(keyword_dir):
            os.makedirs(keyword_dir)
            
            csv_path = os.path.join(keyword_dir,f'{keyword}_results.csv')
            json_path =os.path.join(keyword_dir,f'{keyword}_results.json')
            
            tweets_check = save_json(json_path,dict({"keyword":keyword,"total_tweets":len(keyword_tweets),"tweets":keyword_tweets,}))    
            tweets_check = save_csv(keyword_tweets,csv_path)    

            self.csv_path.append(csv_path)
        

    def generate_combined_csv(self):
        if len(self.csv_path) != 0 :
            combined_dfs = pd.DataFrame()
            
            for csv_path in self.csv_path:
                try:
                    df = read_csv(csv_path)
                    
                    combined_dfs = combined_dfs.append(df,ignore_index=True)
                #TODO: ADD process logger here
                except Exception as e:
                    self.status_log=self.status_log+"\n"+(f"{CURRENT_TIME} : Exception combing dataframe from path {csv_path}=>{e}") 
                    print(e)
            try:
                combined_dfs.to_csv(os.path.join(DATABASE_DIR,"combined_csv.csv"),index=False)
                combined_dfs = read_csv(os.path.join(DATABASE_DIR,"combined_csv.csv"))
                combined_dfs =combined_dfs.drop(combined_dfs.columns[[ 0,1,3]], axis = 1)
                combined_dfs['Frequency'] = combined_dfs.groupby(["User Id","profile_link"])["User Id"].transform('count')
                combined_dfs.to_csv(os.path.join(DATABASE_DIR,"combined_frequency.csv"),mode="w",index=False)
                combined_dfs.sort_values(by='Frequency', ascending=False, inplace=True)
                self.status_log=status_log+"\n"+(f"{CURRENT_TIME} : Combined CSV data Generated") 
                self.update_timestamp()
            except Exception as e:
                    self.status_log=self.status_log+"\n"+(f"{CURRENT_TIME} : Exception at generating combined data csv=>{e}") 
                    self.update_timestamp()
        else:
            self.status_log=self.status_log+"\n"+(f"{CURRENT_TIME} : No csv path provided to generate combined csv result") 
            self.update_timestamp()
            print("No csv path provided to generate combined csv result") 

            
if __name__ == "__main__":
    #Get Keywords
    processed_keyword=[]
    tweet_limit = 10 # Set false to get all tweets otherwise only the specified number of tweets
    try:
        keywords = read_text(TWEET_KEYWORDS_FILEPATH)
        processed_keyword = process_keyword(keywords)
    except Exception as e:
        print(e)
    print("Initiating Process")
    scrapper = TwitterScrapper(processed_keyword,START_TIME,CURRENT_TIME,tweet_limit)

    scrapper.initiate_search()
    scrapper.generate_combined_csv()
    print("Process Completed")

