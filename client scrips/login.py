import requests 
import os
import time
import logging
import random
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from io import BytesIO, BufferedReader
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from typing import Tuple, List, Any, Dict
import json

def header_formater(cookie: str = False) -> Dict[str,str]:
    if not cookie:
        logging.debug("No cookie provided, returning cdn headers.")
        headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "If-Modified-Since": "Fri, 05 Jul 2024 03:14:57 GMT",
        "If-None-Match": 'W/"66876531-22e"',
        "Priority": "u=0, i",
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": '"Android"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
    }
        return headers
    else:
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
        return headers

def get_links(url: str) -> Dict[str,str]:
    headers: dict[str,str] = header_formater()
    try:
        response = requests.get(url, headers=headers)
        response = json.loads(response.text)
        return response
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Request for links failed: {e}")
        return None
    
def get_assets(url: str) -> Image.Image:
    headers: dict[str, str] = header_formater()
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        try:
            image = Image.open(BytesIO(response.content))
            return image
        except UnidentifiedImageError:
            logging.error(f"Failed to open image from assets due to unrecognized image format. link: {url}")
            return None
        except OSError:
            logging.error(f"Failed to open image from assets due to an OS error. link: {url}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request for assets failed: {e}")
        return None


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

def reward_info(cookie: str, links: Dict[str,str]) -> List[Dict[str,str]]:
    headers: dict[str,str] = header_formater(cookie)
    rewards_url: str = links.get('reward_info')

    
    try:
        rewards_response: requests.Response = requests.get(rewards_url, headers=headers)
        rewards_response.raise_for_status()
        rewards_data: Dict[str,Any]  = rewards_response.json().get('data')
        rewards: List[Dict[str,str]] = rewards_data.get('awards')
        return rewards
    except requests.exceptions.RequestException as e:
        logging.error(f"Request for reward_info failed: {e}")
        return None

def day_counter(cookie: str, links: str) -> int:
    headers: dict[str,str] = header_formater(cookie)
    
    day_count_url: str = links.get('day_counter')

    try:
        day_count_response: requests.Response = requests.get(day_count_url, headers=headers)
        day_count_response.raise_for_status()
        rewards_data: Dict[str,str]  = day_count_response.json().get('data')
        day_count: str = rewards_data.get('total_sign_day')
        
        return int(day_count)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request for day_count failed: {e}")
        return None

def time_info(cookie: str, links: str) -> str:
    headers: dict[str,str] = header_formater(cookie)

    time_url: str = links.get('time_info')

    try:
        time_response: requests.Response = requests.get(time_url, headers=headers)
        time_response.raise_for_status()
        time_data: Dict[str,str] = time_response.json().get('data')
        refresh_time: str = time_data.get('refresh_time')
        
        return refresh_time
    except requests.exceptions.RequestException as e:
        logging.error(f"Request for time_info failed: {e}")
        return None

def signin_check(cookie: str, links: str) -> bool:
    headers: dict[str,str] = header_formater(cookie)

    signin_check_url: str = links.get('signin_check')

    try:
        signin_check_response: requests.Response = requests.get(signin_check_url, headers=headers)
        signin_check_response.raise_for_status()
        signin_check_response: Dict[str,any] = signin_check_response.json().get('data')
        signin_check: bool = signin_check_response.get('is_sign')
        return bool(signin_check)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request for signin_check failed: {e}")
        return False

def signin(cookie: str, links: str) -> bool:
    headers: dict[str,str] = header_formater(cookie)

    signin_url: str = links.get('signin')
    act_id: str = links.get('id')
    payload: Dict[str,str] = {"act_id": act_id}

    try:
        response: requests.Response = requests.post(signin_url, headers=headers, json=payload)
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

def webhook(message: str, card: Image.Image = None) -> bool:
    url: str = os.getenv("discord_webhook")
    if not url:
        logging.error("Webhook URL not specified in environment variables.")
        return False
    
    data: Dict[str, str] = {
        'content': message
    }

    if card is None:
        try:
            response: requests.Response = requests.post(url, data=data)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send webhook notification: {e}")
            return False
    else:
        buffer = BytesIO()
        card.save(buffer, format="PNG" )
        buffer.seek(0)
        files: Dict[str, tuple] = {'file': ('Card.png', buffer, 'image/png')}
        try:
            response: requests.Response = requests.post(url, data=data, files=files)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send webhook notification: {e}")
            return False

def card_generator(data: Dict[str,str]) -> Image.Image:
    base_number: int = random.randint(1, 9)
    base: Image.Image = get_assets(f'https://8fax.github.io/HoyoHelper/assets/gi/cards/{base_number}.png')
    if base is None:
        logging.error("Failed to load base card image. loading default card.")
        base = get_assets("https://8fax.github.io/HoyoHelper/assets/gi/cards/1.png")
        
    base = base.convert('RGB')

    frame: Image.Image = get_assets("https://8fax.github.io/HoyoHelper/assets/other_art/UI_Frm_AlchemySimCodexPage_Bg.png")
    if frame is None:
        logging.error("Failed to load frame image. The program will continue without the frame.")
    else:
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
        sticker: Image.Image = get_assets(f'https://8fax.github.io/HoyoHelper/assets/gi/character_stickers/{sticker_number}.png')
        if sticker is None:
            logging.error("Failed to load sticker image. The program will continue without the sticker.")
        else:
        
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
    portrait: Image.Image = get_assets(f'https://8fax.github.io/HoyoHelper/assets/gi/car_dec/{portrait_number}.png')
    if portrait is None:
        logging.error("Failed to load portrait image. The program will continue without the portrait.")
    else:
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

def process_account(cookie: str, name: str, links: str) -> bool:

    if not cookie or not links or not name:
        logging.error(f"Missing environment variables for account {name}.")
        return False
    
    signedin: bool = signin_check(cookie, links)
    logging.debug(f"Signed in status for {name}: {signedin}")
    
    rewards: list[Dict[str,str]] = reward_info(cookie, links)
    logging.debug(f"Rewards for {name}: {rewards}")
    
    day_count: int = day_counter(cookie, links)
    logging.debug(f"Day count for {name}: {day_count}")
    
    refresh_time: str = time_info(cookie, links)
    logging.debug(f"Refresh time for {name}: {refresh_time}")
    
    refresh_time_formatted: str = time_formater(refresh_time)
    logging.debug(f"Formatted refresh time for {name}: {refresh_time_formatted}")

    if signedin:
        logging.info(f"{name} has already signed in today.")
        message = f"{name} has already signed in today, this was their rewards:"
        if len(rewards) <= day_count+1:
            logging.info(f"{name} has claimed all rewards, cannot see next month's rewards yet check back tomorrow.")
            end_of_month = True
            data = data_parser(rewards, day_count, refresh_time_formatted , end_of_month, signedin)
            card = card_generator(data)
            is_sent = webhook(message, card)
            if is_sent:
                logging.info(f"Webhook sent for {name}.")
            return True
        else:
            end_of_month = False
            data = data_parser(rewards, day_count, refresh_time_formatted, end_of_month, signedin)
            card = card_generator(data)
            is_sent = webhook(message, card)
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
            is_sent = webhook(message, card)
            if is_sent:
                logging.info(f"Webhook sent for {name}.")
            signin_satus = signin(cookie, links)
            if signin_satus:
                logging.info(f"{name} has successfully signed in, now verifying...")
                signedin = signin_check(cookie, links)
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
            is_sent: bool = webhook(message, card)
            if is_sent:
                logging.info(f"Webhook sent for {name}.")
            signin_satus = signin(cookie, links)
            if signin_satus:
                logging.info(f"{name} has successfully signed in, now verifying...")
                signedin = signin_check(cookie, links)
                if signedin:
                    logging.info(f"{name} has successfully signed in and claimed their reward.")
                else:
                    logging.warning(f"{name} has failed to sign in.")
                    message: str = f"{name} has failed to sign in, please check the logs and try again."
                    is_sent: bool = webhook(message=message)
                    if is_sent:
                        logging.info(f"Webhook sent for {name}.")
            else:
                logging.warning(f"{name} has failed to sign in. The reward will not be claimed. Refresh the token and try again.")
                message: str  = f"{name} has failed to sign in, please check the logs and try again."
                is_sent: bool = webhook(message=message)
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
        logging.debug(f"Account info - Cookie: {cookie}, Name: {name}, Act ID: {games}")
        games = games.split(",")
        for game in games:
            logging.debug(f"Game: {game}")
            if game == "gi":
                links = get_links("https://8fax.github.io/HoyoHelper/info/links/gi_links.txt")
            elif game == "hsr":
                links = get_links("https://8fax.github.io/HoyoHelper/info/links/hsr_links.txt")
            elif game == "zzz":
                links = get_links("https://8fax.github.io/HoyoHelper/info/links/zzz_links.txt")
            else:
                logging.error(f"Invalid game specified for account {name}.")
                continue
            if not process_account(cookie, name, links):
                message: str = f"Failed to process account {name}, please check the logs."
                is_sent: bool = webhook(message)
                if is_sent:
                    logging.info(f"Webhook sent for {name}.")
            time.sleep(5)

if __name__ == "__main__":
    main()
