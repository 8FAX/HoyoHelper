import requests
import json
import time

url = "https://sg-hk4e-api.hoyoverse.com/common/apicdkey/api/webExchangeCdkey?"

cookie = ""
code = ["LA5E77CLZX5V", "MTLF6DKA7PQZ", "WTXV36M1J6CO0", "DEOB21CK9Y6N","SBUEMJB449D9" ]

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": cookie,
    "Origin": "https://genshin.hoyoverse.com",
    "Priority": "u=1, i",
    "Referer": "https://genshin.hoyoverse.com/",
    "Sec-CH-UA": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
    "Sec-CH-UA-Mobile": "?1",
    "Sec-CH-UA-Platform": "\"Android\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "X-Requested-With": "XMLHttpRequest" 
}

def get_payload(code):
    return {
        "uid": "610320530",
        "region": "os_usa",
        "lang": "en",
        "cdkey": code,
        "game_biz": "hk4e_global",
        "sLangKey": "en-us"
    }

for i in code:
    payload = get_payload(i)
                                                                                                
    for key, value in payload.items():
        url += f"&{key}={value}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.headers.get("Content-Type") == "application/json":
            data = response.json()
            print(data)
        else:
            print("Response is not JSON:", response.text)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
    except json.JSONDecodeError:
        print("Failed to parse JSON:", response.text)

    time.sleep(5)
