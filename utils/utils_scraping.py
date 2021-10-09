# utils_scraping.py
import os
import random
from typing import *
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import random

"""
This file contents usefull functions for scraping.
"""


def make_proxy_entry(proxy_ip_port): 
    val = f"http://{proxy_ip_port}" 
    return dict(http=val, https=val)


def get_proxy():
    ip_opts = ['82.166.105.66:44081', '82.81.32.165:3128', '82.81.169.142:80',
           '81.218.45.159:8080', '82.166.105.66:43926', '82.166.105.66:58774',
           '31.154.189.206:8080', '31.154.189.224:8080', '31.154.189.211:8080',
           '213.8.208.233:8080', '81.218.45.231:8888', '192.116.48.186:3128',
           '185.138.170.204:8080', '213.151.40.43:8080', '81.218.45.141:8080']

    proxy_entry = make_proxy_entry(random.choice(ip_opts))
    return proxy_entry

def get_user_agent():
    user_agent_list = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    ]

    for i in range(1,4):
        #Pick a random user agent
        user_agent = random.choice(user_agent_list)
        #Set the headers 
    headers = {'User-Agent': user_agent}
    #Make the request
    return headers