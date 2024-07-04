import requests 
import os
import time
import logging
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO, BufferedReader
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from typing import Tuple, List, Any, Dict

def time_formater(time: str) -> str:
    input_time = int(time)
    now_time = datetime.now(timezone.utc)
    input_datetime = datetime.fromtimestamp(input_time, timezone.utc)
    delta = now_time - input_datetime
    
    days: int = delta.days
    seconds: float = delta.total_seconds() % (24 * 3600) 
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)

    if days < 1:
        if hours < 1:
            return f"{minutes}m"
        else:
            return f"{hours}h {minutes}m"
    else:
        return f"{days}d {hours}h {minutes}m"

def reward_info(cookie: str, act_id: str) -> List[Dict[str,str]]:
    headers: Dict[str,str]  = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": cookie,
        "Origin": "https://act.hoyolab.com",
        "Referer": "https://act.hoyolab.com/",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "macOS",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    rewards_url = f"https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/home?lang=en-us&act_id={act_id}"
    
    try:
        rewards_response: requests.Response = requests.get(rewards_url, headers=headers)
        rewards_response.raise_for_status()
        rewards_data: Dict[str,Any]  = rewards_response.json().get('data')
        rewards: List[Dict[str,str]] = rewards_data.get('awards')
        return rewards
    except requests.exceptions.RequestException as e:
        logging.error(f"Request for reward_info failed: {e}")
        return None

def day_counter(cookie: str, act_id: str) -> int:
    headers: Dict[str,str] = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": cookie,
        "Origin": "https://act.hoyolab.com",
        "Referer": "https://act.hoyolab.com/",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "macOS",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    day_count_url: str = f"https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/info?lang=en-us&act_id={act_id}"

    try:
        day_count_response: requests.Response = requests.get(day_count_url, headers=headers)
        day_count_response.raise_for_status()
        rewards_data: Dict[str,str]  = day_count_response.json().get('data')
        day_count: str = rewards_data.get('total_sign_day')
        
        return int(day_count)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request for day_count failed: {e}")
        return None

def time_info(cookie: str, act_id: str) -> str:
    headers: Dict[str,str] = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": cookie,
        "Origin": "https://act.hoyolab.com",
        "Referer": "https://act.hoyolab.com/",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "macOS",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    time_url: str = f"https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/recommend?act_id={act_id}&lang=en-us&plat=PT_M"

    try:
        time_response: requests.Response = requests.get(time_url, headers=headers)
        time_response.raise_for_status()
        time_data: Dict[str,str] = time_response.json().get('data')
        refresh_time: str = time_data.get('refresh_time')
        
        return refresh_time
    except requests.exceptions.RequestException as e:
        logging.error(f"Request for time_info failed: {e}")
        return None

def signin_check(cookie: str, act_id: str) -> bool:
    headers: Dict[str,str] = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": cookie,
        "Origin": "https://act.hoyolab.com",
        "Referer": "https://act.hoyolab.com/",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "macOS",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    signin_check_url: str = f"https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/info?lang=en-us&act_id={act_id}"

    try:
        signin_check_response: requests.Response = requests.get(signin_check_url, headers=headers)
        signin_check_response.raise_for_status()
        signin_check_response: Dict[str,any] = signin_check_response.json().get('data')
        signin_check: bool = signin_check_response.get('is_sign')
        return bool(signin_check)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request for signin_check failed: {e}")
        return False

def signin(cookie: str, act_id: str) -> bool:
    headers: Dict[str,str] = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Length": "29",
        "Content-Type": "application/json;charset=UTF-8",
        "Cookie": cookie,
        "Origin": "https://act.hoyolab.com",
        "Priority": "u=1, i",
        "Referer": "https://act.hoyolab.com/",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "macOS",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "X-Rpc-App_version": "",
        "X-Rpc-Device_id": "e2cd5b1c-7a89-472e-9795-8313f937e6ff",
        "X-Rpc-Device_name": "",
        "X-Rpc-Platform": "4"
    }

    url: str = "https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/sign"
    payload: Dict[str,str] = {"act_id": act_id}

    try:
        response: requests.Response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        formatted_response: Dict[str,str] = response.json()
        if formatted_response.get('message') == "OK":
            return True
        else:
            logging.warning(f"Sign-in failed: {formatted_response.get('message')}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return False

def webhook(card: Image.Image, message: str) -> bool:
    url: str = os.getenv("discord_webhook")
    if not url:
        logging.error("Webhook URL not specified in environment variables.")
        return False
    if card == None:
        data: Dict[str,str] = {
            'content': message
        }
        try:
            response: requests.Response = requests.post(url, data=data)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send webhook notification: {e}")
            return False
    else:
        data: Dict[str,str] = {
            'content': message
        }

        card.save('assets/junk/Card.png')
        with open('assets/junk/Card.png', 'rb') as file:
            files: Dict[str,BufferedReader] = {'file': file}

            try:
                response: requests.Response = requests.post(url, data=data, files=files)
                response.raise_for_status()
                return True
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to send webhook notification: {e}")
                return False

def card_generator(data: Dict[str,str]) -> Image.Image:
    base_number: int = random.randint(1, 9)
    base: Image.Image = Image.open(f'assets/cards/{base_number}.png')
    base = base.convert('RGB')

    frame: Image.Image = Image.open('assets/other_art/UI_Frm_AlchemySimCodexPage_Bg.png')
    base.paste(frame, (20, 68), frame)
    base.paste(frame, (20, 284), frame)

    icon_1: Image.Image = Image.open(BytesIO(requests.get(data['icon_1']).content))
    icon_1 = icon_1.resize((100, 100))
    if icon_1.mode != 'RGBA':
        icon_1 = icon_1.convert('RGBA')
    
    if not data['end_of_month']:
        icon_2: Image.Image = Image.open(BytesIO(requests.get(data['icon_2']).content))
        icon_2 = icon_2.resize((100, 100))
        if icon_2.mode != 'RGBA':
            icon_2 = icon_2.convert('RGBA')
        base.paste(icon_2, (40, 304), icon_2)
    
    base.paste(icon_1, (40, 88), icon_1)

    d: ImageDraw.ImageDraw = ImageDraw.Draw(base)
    font: ImageFont.ImageFont = ImageFont.load_default()
    font_reward = font.font_variant(size=34)
    font_day_title = font.font_variant(size=24)

    d.text((180, 80), "Today you got:", font=font_day_title, fill="Black")
    d.text((180, 120), f"{data['name_1']} x{data['cnt_1']}", font=font_reward, fill="pink")
    d.text((179, 119), f"{data['name_1']} x{data['cnt_1']}", font=font_reward, fill="purple")

    if data['end_of_month']:
        sticker_number: int = random.randint(2, 153)
        sticker: Image.Image = Image.open(f'assets/character_stickers/{sticker_number}.png')
        sticker = sticker.resize((100, 100))
        if sticker.mode != 'RGBA':
            sticker = sticker.convert('RGBA')
        base.paste(sticker, (40, 304), sticker)
        d.text((180, 300), "No More rewards this month!", font=font_day_title, fill="Black")
        d.text((180, 340), f"You have claimed all rewards this month!\nCome back in {data['refresh']}\nto see next month's rewards!", font=font_day_title, fill="pink")
        d.text((179, 339), f"You have claimed all rewards this month!\nCome back in {data['refresh']}\nto see next month's rewards!", font=font_day_title, fill="purple")
    else:
        d.text((180, 300), f"In {data['refresh']} you will get:", font=font_day_title, fill="Black")
        d.text((180, 340), f"{data['name_2']} x{data['cnt_2']}", font=font_reward, fill="pink")
        d.text((179, 339), f"{data['name_2']} x{data['cnt_2']}", font=font_reward, fill="purple")

    if data['days'] == 1:
        d.text((865, 20), f"Checked in", font=ImageFont.load_default().font_variant(size=24), fill="black")
        d.text((912, 62), f"{data['days']}", font=ImageFont.load_default().font_variant(size=35), fill="pink")
        d.text((910, 60), f"{data['days']}", font=ImageFont.load_default().font_variant(size=35), fill="black")
        d.text((835, 100), f"day this month!", font=ImageFont.load_default().font_variant(size=24), fill="black")
    else:
        d.text((865, 20), f"Checked in", font=ImageFont.load_default().font_variant(size=24), fill="black")
        d.text((902, 62), f"{data['days']}", font=ImageFont.load_default().font_variant(size=35), fill="pink")
        d.text((900, 60), f"{data['days']}", font=ImageFont.load_default().font_variant(size=35), fill="black")
        d.text((835, 100), f"days this month!", font=ImageFont.load_default().font_variant(size=23), fill="black")

    portrait_number: int = random.randint(2, 32)
    portrait: Image.Image = Image.open(f'assets/car_dec/{portrait_number}.png')
    if portrait.mode != 'RGBA':
        portrait = portrait.convert('RGBA')
    base.paste(portrait, (630, 422), portrait)

    return base

def data_parser(rewards: list[dict[str,str]], day_count: str, refresh_time: str, end_of_month: bool = False, checked_in: bool = False) -> Dict[str,any]:
    if not checked_in:
        day_count += 1
    else:
        day_count -= 1

    today: Dict[str,Any] = rewards[day_count]


    if not end_of_month:
        tomorrow: Dict[str,Any] = rewards[day_count + 1]
        data: Dict[str,str] = {
            "icon_1": today["icon"],
            "name_1": today["name"],
            "cnt_1": today["cnt"],
            "icon_2": tomorrow["icon"],
            "name_2": tomorrow["name"],
            "cnt_2": tomorrow["cnt"],
            "end_of_month": end_of_month,
            "days": day_count+1,
            "refresh": refresh_time
        }
    else:
        data: Dict[str,str]  = {
            "icon_1": today["icon"],
            "name_1": today["name"],
            "cnt_1": today["cnt"],
            "end_of_month": end_of_month,
            "days": day_count+1,
            "refresh": refresh_time
        }

    return data

def load_env() -> bool:
    loaded: bool = load_dotenv()
    if not loaded:
        return False
    logging.basicConfig(level=logging.INFO)
    accounts: str = os.getenv("num_of_accounts")
    if not accounts:
        logging.error("Number of accounts not specified in environment variables.")
        return False
    try:
        accounts = int(accounts)
    except ValueError:
        logging.error("Invalid number of accounts specified.")
        return False 
    
    return True

def get_account_info(i: int) -> Tuple[str, str, str]:
    cookie: str = os.getenv(f"account_{i}_cookie")
    name: str = os.getenv(f"account_{i}_name")
    games: str = os.getenv(f"account_{i}_games")
    return cookie, name, games

def process_account(cookie: str, name: str, act_id: str) -> bool:
    signedin: bool = signin_check(cookie, act_id)
    logging.debug(f"Signed in status for {name}: {signedin}")
    
    rewards: list[Dict[str,str]] = reward_info(cookie, act_id)
    logging.debug(f"Rewards for {name}: {rewards}")
    
    day_count: int = day_counter(cookie, act_id)
    logging.debug(f"Day count for {name}: {day_count}")
    
    refresh_time: str = time_info(cookie, act_id)
    logging.debug(f"Refresh time for {name}: {refresh_time}")
    
    refresh_time_formatted: str = time_formater(refresh_time)
    logging.debug(f"Formatted refresh time for {name}: {refresh_time_formatted}")

    if not cookie or not act_id or not name:
        logging.error(f"Missing environment variables for account {name}.")
        return False

    if signedin:
        logging.info(f"{name} has already signed in today.")
        message = f"{name} has already signed in today, this was their rewards:"
        if len(rewards) <= day_count+1:
            logging.info(f"{name} has claimed all rewards, cannot see next month's rewards yet check back tomorrow.")
            end_of_month = True
            data = data_parser(rewards, day_count, refresh_time_formatted , end_of_month, signedin)
            card = card_generator(data)
            is_sent = webhook(card, message)
            if is_sent:
                logging.info(f"Webhook sent for {name}.")
            return True
        else:
            end_of_month = False
            data = data_parser(rewards, day_count, refresh_time_formatted, end_of_month, signedin)
            card = card_generator(data)
            is_sent = webhook(card, message)
            if is_sent:
                logging.info(f"Webhook sent for {name}.")
            return True

    if not signedin:
        logging.info(f"{name} has not signed in today, proceeding to sign in...")
        message: str  = f"{name} has signed in and gotten this reward:"
        if len(rewards) <= day_count+1:
            logging.info(f"{name} has just claimed the last rewards for this month, cannot see next month's rewards yet check back tomorrow.")
            end_of_month = True
            data = data_parser(rewards, day_count, refresh_time_formatted, end_of_month, signedin)
            card = card_generator(data)
            is_sent = webhook(card, message)
            if is_sent:
                logging.info(f"Webhook sent for {name}.")
            signin_satus = signin(cookie, act_id)
            if signin_satus:
                logging.info(f"{name} has successfully signed in, now verifying...")
                signedin = signin_check(cookie, act_id)
                if signedin:
                    logging.info(f"{name} has successfully signed in and claimed their reward.")
                else:
                    logging.warning(f"{name} has failed to sign in.")
            else:
                logging.warning(f"{name} has failed to sign in. The reward will not be claimed. Refresh the token and try again.")
        else:
            end_of_month = False
            data: Dict[str,Any]= data_parser(rewards, day_count, refresh_time_formatted, end_of_month, signedin)
            card: Image.Image  = card_generator(data)
            is_sent: bool = webhook(card, message)
            if is_sent:
                logging.info(f"Webhook sent for {name}.")
            signin_satus = signin(cookie, act_id)
            if signin_satus:
                logging.info(f"{name} has successfully signed in, now verifying...")
                signedin = signin_check(cookie, act_id)
                if signedin:
                    logging.info(f"{name} has successfully signed in and claimed their reward.")
                else:
                    logging.warning(f"{name} has failed to sign in.")
                    message: str = f"{name} has failed to sign in, please check the logs and try again."
                    is_sent = webhook(None, message)
                    if is_sent:
                        logging.info(f"Webhook sent for {name}.")
            else:
                logging.warning(f"{name} has failed to sign in. The reward will not be claimed. Refresh the token and try again.")
                message: str  = f"{name} has failed to sign in, please check the logs and try again."
                is_sent = webhook(None, message)
                if is_sent:
                    logging.info(f"Webhook sent for {name}.")
    return True

def main() -> None:
    if not load_env():
        raise SystemError("Failed to load environment variables.")
    
    accounts = os.getenv("num_of_accounts")
    logging.info(f"Number of accounts: {accounts}")

    for i in range(1, int(accounts) + 1):
        logging.info(f"Processing account {i}")
        cookie, name, games = get_account_info(i)
        games = games.split(",")
        for game in games:
            if game == "zzz":
                act_id = os.getenv(f"account_{i}_zzz_act_id")
                logging.debug(f"Account info - Cookie: {cookie}, Name: {name}, Act ID: {act_id}")
                if not process_account(cookie, name, act_id):
                    message: str = f"Failed to process account {name}, please check the logs."
                    is_sent: bool = webhook(None, message)
                    if is_sent:
                        logging.info(f"Webhook sent for {name}.")
                        time.sleep(10)
            if game == "gi":
                logging.info(f"Account {name} is a Genshin account, skipping.")
                continue
            if game == "hrs":
                logging.info(f"Account {name} is a Honkai account, skipping.")
                continue





        logging.debug(f"Account info - Cookie: {cookie}, Name: {name}, Act ID: {act_id}")
        if not process_account(cookie, name, act_id):
            message: str = f"Failed to process account {name}, please check the logs."
            is_sent: bool = webhook(None, message)
            if is_sent:
                logging.info(f"Webhook sent for {name}.")
        time.sleep(10)

if __name__ == "__main__":
    # main()
    load_env()
    while True:
        cookie = "mi18nLang=en-us; _MHYUUID=70a040de-3074-47e3-8723-63c414da8804; HYV_LOGIN_PLATFORM_OPTIONAL_AGREEMENT={%22content%22:[]}; HYV_LOGIN_PLATFORM_TRACKING_MAP={%22sourceValue%22:%2276%22}; DEVICEFP_SEED_ID=bbffa532407effc2; DEVICEFP_SEED_TIME=1719630997410; _gid=GA1.2.494754028.1719630998; _gat_gtag_UA_201411121_1=1; _ga=GA1.1.1405462616.1719630997; DEVICEFP=38d7f28d5f123; _ga_54PBK3QDF4=GS1.1.1719630997.1.1.1719630998.0.0.0; _ga_T9HTWX7777=GS1.1.1719630997.1.0.1719630998.0.0.0; HYV_LOGIN_PLATFORM_LIFECYCLE_ID={%22value%22:%22b51510ec-5606-4611-bda6-7f70c35e1087%22}; HYV_LOGIN_PLATFORM_LOAD_TIMEOUT={%22value%22:null}; ltoken_v2=v2_CAISDGNlMXRidXdiMDB6axokNzBhMDQwZGUtMzA3NC00N2UzLTg3MjMtNjNjNDE0ZGE4ODA0IKX5_bMGKKign-IEMN__56oBQgtoazRlX2dsb2JhbA.pXx_ZgAAAAAB.MEUCIA-3W6Fg4IBu3uraLefBECB8S4qUyUsh7gD3v3hzMBP6AiEAzdmNuYOjSbsAnbOIsprD1c2KF_Jxs8huq7hff75Ri8o; ltmid_v2=1z39031j7i_hy; ltuid_v2=358219743"
        name = "8FA"
        act_id = "e202406031448091"
        logging.debug(f"Account info - Cookie: {cookie}, Name: {name}, Act ID: {act_id}")
        if not process_account(cookie, name, act_id):
            message: str = f"Failed to process account {name}, please check the logs."
            is_sent: bool = webhook(None, message)
            if is_sent:
                logging.info(f"Webhook sent for {name}.")
