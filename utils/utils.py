import os 
import json
from tqdm import tqdm 
import multiprocessing

"""
This file contents usefull basique functions 
"""


def MakeDir(DIR:str) -> None:
    try:
        if not os.path.exists(DIR):
            os.makedirs(DIR)
    except OSError as err:
        print(err)
        pass

def dict_to_json(dictionary:dict, json_path:str) -> None:
    with open(json_path, "w", encoding='utf-8') as outfile: 
        json.dump(dictionary, outfile, indent=4, ensure_ascii=False)
        print(f'json file saved in {json_path}')


def run_imap_multiprocessing(func, argument_list, num_processes=multiprocessing.cpu_count()-1):
    with multiprocessing.Pool(processes=num_processes) as pool:
        result_list_tqdm = []
        for result in tqdm(pool.imap(func=func, iterable=argument_list), total=len(argument_list)):
         result_list_tqdm.append(result)
    return result_list_tqdm

def open_json_file(json_path):
    # Opening JSON file
    with open(json_path) as json_file:
        data = json.load(json_file)
    return data 
    

