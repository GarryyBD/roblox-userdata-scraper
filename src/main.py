import httpx
import os
from utils import Utils
from Proxy import Proxy
import concurrent.futures
from dotenv import dotenv_values
from pymongo import MongoClient
from User import User
import time

config = dotenv_values(".env")

try:
    MAX_WORKERS = int(config["MAX_WORKERS"])
    MAX_GENERATIONS = int(config["MAX_GENERATIONS"])
    MONGO_URI = config["MONGO_URI"]
except KeyError as e:
    raise KeyError(f"Please make sure to provide {str(e)} in .env file")

class App:
    @classmethod  
    def run(cls):
        App.get_files_paths()

        Proxy.check_proxies_file_format(cls.proxies_file)

        collection_users = cls.setup_database()

        # get highest user id of collection
        try:
            last_user_id = collection_users.find_one(sort=[("id", -1)])["id"] 
        except TypeError:
            last_user_id = 0

        print(f"Last user id : {last_user_id}")

        print("Starting scraping...")

        worked_req = 0
        failed_req = 0
        total_req = last_user_id

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = [executor.submit(cls.scrape_username, last_user_id+user_id+1) for user_id in range(MAX_GENERATIONS)]

            for future in concurrent.futures.as_completed(results):
                try:
                    has_scraped, response_text, user = future.result()
                except Exception as e:
                    has_scraped, response_text = False, str(e)

                if has_scraped:
                    worked_req += 1
                    total_req += 1
                    collection_users.insert_one(user.to_dict())
                else:
                    failed_req += 1

                cls.print_status(worked_req, failed_req, total_req, response_text, has_scraped)
    
    @classmethod
    def scrape_username(cls, user_id: int) -> tuple:
        while True:
            proxies = Proxy.get_random_proxies(cls.proxies_file)

            try:
                response = httpx.get(f"https://users.roblox.com/v1/users/{user_id}", proxies=proxies)
                status_code = response.status_code
            except Exception as e:
                print("Proxy error: " + str(e) + " Retrying...")
            else:
                if status_code == 429:
                    print("Rate limited by roblox api. Retrying...")
                    time.sleep(1)
                else:
                    result = response.json()
                    user = User(result.get("description"), result.get("created"), result.get("isBanned"), result.get("externalAppDisplayName"), result.get("hasVerifiedBadge"), result.get("id"), result.get("name"), result.get("displayName"))

                    return status_code == 200, Utils.return_res(response), user

    @classmethod
    def get_files_paths(cls) -> tuple:
        """
        Get the files paths of the files.
        """
        files_folder_path = os.path.join(os.path.dirname(__file__), "../files")
        cls.proxies_file = os.path.join(files_folder_path, "./proxies.txt")

        Utils.ensure_directories_exist([files_folder_path])
        Utils.ensure_files_exist([cls.proxies_file])

    @classmethod
    def setup_database(cls):
        """
        Setup mongodb database and collection
        """
        client = MongoClient(MONGO_URI)

        # create database if not exists
        db = client["roblox-scraping"]
        collection_users = db["users"]
        collection_users.create_index("id", unique=True)

        return collection_users

    @classmethod
    def print_status(self, req_worked, req_failed, total_req, response_text, has_worked):
        """
        Prints the status of a request
        """
        print(f"\033[1;32mScraped: {str(req_worked)}\033[0;0m | \033[1;31mFailed: {str(req_failed)}\033[0;0m | \033[1;34mTotal: {str(total_req)}\033[0;0m")
        print(f"\033[1;32mWorked: {response_text}\033[0;0m" if has_worked else f"\033[1;31mFailed: {response_text}\033[0;0m")
    
if __name__ == '__main__':
    App.run()