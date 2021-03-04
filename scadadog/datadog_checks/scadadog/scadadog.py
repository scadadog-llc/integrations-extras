from typing import Any
from datadog_checks.base import AgentCheck


class ScadadogCheck(AgentCheck):
    def check(self, _):
        # type: (Any) -> None
        # Use self.instance to read the check configuration
        #self.service_check('scadadog.wonderware', self.OK)
        kepserver = KepserverAPI(ip="127.0.0.1",port="57412",user="api",password="scadadogapi1Pass")
        for channel in kepserver.get_channels():
            count = channel["servermain.CHANNEL_STATIC_TAG_COUNT"]
            name = channel["common.ALLTYPES_NAME"].replace(' ','_').replace('.','_').replace('-','_').lower()
            #print(f'scadadog.kepserver.{name}.tagcount:{count}')
            self.gauge(f'scadadog.kepserver.{name}.tagcount', count)
        

import requests
import json
class KepserverAPI():
    def __init__(self,ip,port,user,password):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password

    def call(self,url):
        response = requests.get(f"http://{self.ip}:{self.port}{url}",auth=(user,password))
        status_code = response.status_code
        if status_code >= 200 and status_code < 207:
            return response.json()
        return self.resp_code(status_code)
        
    def resp_code(self,status_code) :
        # HTTPS/1.1 200 OK 
        # HTTPS/1.1 201 Created 
        # HTTPS/1.1 202 Accepted 
        # HTTPS/1.1 207 Multi-Status 
        # HTTPS/1.1 400 Bad Request 
        # HTTPS/1.1 401 Unauthorized 
        # HTTPS/1.1 403 Forbidden 
        # HTTPS/1.1 404 Not Found 
        # HTTPS/1.1 429 Too Many Requests 
        # HTTPS/1.1 500 Internal Server Error 
        # HTTPS/1.1 503 Server Runtime Unavailable 
        # HTTPS/1.1 504 Gateway Timeout 
        # HTTPS/1.1 520 Unknown Error
        switcher = {
            200: "OK",
            201: "Created",
            202: "Accepted",
            207: "Multi-Status",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            429: "Too Many Requests",
            500: "Internal Server Error",
            503: "Server Runtime Unavailable ",
            504: "Gateway Timeout",
            520: "Unknown Error"
        }
        return switcher.get(status_code, "Unknown")

    
    def get_channels(self):
        url = "/config/v1/project/channels"
        return  self.call(url)

    def get_devices(self,channel_name):
        url = f"/config/v1/project/channels/{channel_name}/devices"
        return self.call(url)
        
    def get_tags(self,channel_name,device_name):
        url = f"/config/v1/project/channels/{channel_name}/devices/{device_name}/tags"
        return self.call(url)
    
    def get_tag(self,channel_name,device_name,tag_name):
        url = f"/config/v1/project/channels/{channel_name}/devices/{device_name}/tags/{tag_name}"
        return self.call(url



