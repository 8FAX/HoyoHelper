import requests
import time

BASE_URL = "https://sg-hk4e-api.hoyoverse.com/common/apicdkey/api/webExchangeCdkey?"

cookie = ""
codes = ["FORNATLAN"]

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
    # change the uid to for each acount, soon it will be automated
    return {
        "uid": "668290053",
        "region": "os_usa",
        "lang": "en",
        "cdkey": code,
        "game_biz": "hk4e_global",
        "sLangKey": "en-us"
    }

def redeem_code(url, headers, code):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.headers.get("Content-Type") == "application/json":
            data = response.json()
            print(code)
            print(data)
        else:
            print("Response is not JSON:", response.text)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)     

def main():
    for code in codes:
        payload = get_payload(code)
        url = BASE_URL
        for key, value in payload.items():
            url += f"&{key}={value}"
        redeem_code(url, headers, code)
        time.sleep(5)


if __name__ == "__main__":
    main()