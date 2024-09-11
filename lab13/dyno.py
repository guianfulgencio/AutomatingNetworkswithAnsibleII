#!/usr/bin/env python

import requests
import json

requests.packages.urllib3.disable_warnings()

def main():
    url = 'https://2z3oa80l2c.execute-api.us-east-1.amazonaws.com/prod/switch'
    inventory = requests.get(url, verify=False)
    return inventory.text

if __name__ == "__main__":
    rsp = main()
    print(rsp)
