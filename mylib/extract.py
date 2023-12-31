"""
Extract a dataset from a URL like Kaggle or data.gov. 
JSON or CSV formats tend to work well

food dataset
"""
import requests
import os
from dotenv import load_dotenv
import json
import base64

load_dotenv()
server_h = os.getenv("SERVER_HOSTNAME")
access_token = os.getenv("ACCESS_TOKEN")
FILESTORE_PATH = "dbfs:/FileStore/mini11"
headers = {'Authorization': 'Bearer %s' % access_token}
url = "https://"+server_h+"/api/2.0"

def perform_query(path, headers, data={}):
    session = requests.Session()
    resp = session.request('POST', url + path, 
                           data=json.dumps(data), 
                           verify=True, 
                           headers=headers)
    return resp.json()

def mkdirs(path, headers):
    _data = {}
    _data['path'] = path
    return perform_query('/dbfs/mkdirs', headers=headers, data=_data)
  

def create(path, overwrite, headers):
    _data = {}
    _data['path'] = path
    _data['overwrite'] = overwrite
    return perform_query('/dbfs/create', headers=headers, data=_data)


def add_block(handle, data, headers):
    _data = {}
    _data['handle'] = handle
    _data['data'] = data
    return perform_query('/dbfs/add-block', headers=headers, data=_data)


def close(handle, headers):
    _data = {}
    _data['handle'] = handle
    return perform_query('/dbfs/close', headers=headers, data=_data)


def put_file_from_url(url, dbfs_path, overwrite, headers):
    response = requests.get(url)
    if response.status_code == 200:
        content = response.content
        handle = create(dbfs_path, overwrite, headers=headers)['handle']
        print("Putting file: " + dbfs_path)
        for i in range(0, len(content), 2**20):
            add_block(handle, 
                      base64.standard_b64encode(content[i:i+2**20]).decode(), 
                      headers=headers)
        close(handle, headers=headers)
        print(f"File {dbfs_path} uploaded successfully.")
    else:
        print(f"Error downloading file from {url}. Status code: {response.status_code}")


def extract(
    url="""
    https://github.com/fivethirtyeight/data/blob/master/alcohol-consumption/drinks.csv?raw=true 
    """,
    url2 = """
    https://github.com/nogibjj/Command_line_tool_Python_tr/blob/main/data/toy.csv?raw=true 
    """,
    file_path=FILESTORE_PATH + "/alcohol.csv",
    file_path2=FILESTORE_PATH + "/toy.csv",
    directory=FILESTORE_PATH,
    overwrite=True
):
    """Extract a url to a file path"""
    mkdirs(path=directory, headers=headers)
    # Add the csv files, no need to check if it exists or not
    put_file_from_url(url, file_path, overwrite, headers=headers)
    put_file_from_url(url2, file_path2, overwrite, headers=headers)
    return file_path, file_path2

if __name__ == "__main__":
    extract()
