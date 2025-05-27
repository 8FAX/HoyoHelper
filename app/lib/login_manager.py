FILE_VERSION = "0.1.1"

import requests
import os
import time
import logging
import random
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError, ImageFile
from io import BytesIO
from datetime import datetime, timezone
from typing import List, Any, Dict, Optional
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .webhook_manager import WebhookManager
from .exceptions import (
    APIRequestError, APIDataError, AssetFetchError, 
    CardGenerationError, SigninError, LoginManagerError
)

ImageFile.LOAD_TRUNCATED_IMAGES = True
logger = logging.getLogger(__name__)


class LoginManager:
    CDN_BASE_URL = "https://cdn.hoyohelper.com/"
    GAME_ASSET_PATHS = {
        "gi": "gi/",
        "hsr": "hsr/", 
        "zzz": "zzz/", 
        "default_gi": "gi/" 
    }
    
    def __init__(self, webhook_manager: WebhookManager):
        """
        The function initializes various font attributes and loads the fonts.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param webhook_manager (WebhookManager)  - The `webhook_manager` parameter is an instance of
        the `WebhookManager` class. It seems like the `__init__` method is initializing various font
        attributes and loading fonts. If you have any specific questions or need further assistance with
        this code snippet, feel free to ask!
        
        .-.-.-.
        
        
        """
        self.webhook_manager = webhook_manager
        self.default_font: Optional[ImageFont.FreeTypeFont] = None
        self.reward_font: Optional[ImageFont.FreeTypeFont] = None
        self.day_title_font: Optional[ImageFont.FreeTypeFont] = None
        self.large_day_font: Optional[ImageFont.FreeTypeFont] = None
        self.small_text_font: Optional[ImageFont.FreeTypeFont] = None
        self._load_fonts()

    def _load_fonts(self):
        """
        The function `_load_fonts` attempts to load custom fonts for a LoginManager, falling back to
        Pillow's default fonts if the custom font file is not found or loading fails.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        """
        try:
            font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")
            main_font_path = os.path.join(font_dir, "NotoSans-Regular.ttf") 

            if os.path.exists(main_font_path):
                self.default_font = ImageFont.truetype(main_font_path, 15)
                self.reward_font = ImageFont.truetype(main_font_path, 30)
                self.day_title_font = ImageFont.truetype(main_font_path, 20)
                self.large_day_font = ImageFont.truetype(main_font_path, 35)
                self.small_text_font = ImageFont.truetype(main_font_path, 23)
                logger.info("Successfully loaded custom fonts for LoginManager.")
            else:
                logger.warning(f"Custom font file not found at '{main_font_path}'. Using Pillow default.")
                raise FileNotFoundError("Custom font file not found.")
        except Exception as e:
            logger.warning(f"Custom font loading failed ({e}), using Pillow default. Text rendering might be suboptimal.")
            try:
                self.default_font = ImageFont.load_default()
                self.reward_font = self.default_font.font_variant(size=34)
                self.day_title_font = self.default_font.font_variant(size=24)
                self.large_day_font = self.default_font.font_variant(size=35)
                self.small_text_font = self.default_font.font_variant(size=23)
            except Exception as e_pillow:
                logger.error(f"Failed to load even Pillow's default font: {e_pillow}")
                self.default_font = self.reward_font = self.day_title_font = self.large_day_font = self.small_text_font = None

    @staticmethod
    def _header_formater(cookie: Optional[str] = None, links_for_game: Optional[Dict[str,str]] = None) -> Dict[str, str]:
        """
        The function `_header_formater` generates HTTP headers based on the presence of a cookie and
        game links.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param cookie (Optional[str])  - The `cookie` parameter in the `_header_formater` function is
        used to provide a cookie string for making API requests. If the `cookie` parameter is provided,
        the function will generate API headers with the cookie included. If the `cookie` parameter is
        not provided, the function will generate headers
        
        .-.-.-.
        
        @ param links_for_game (Optional[Dict[str,str]])  - The `links_for_game` parameter is expected
        to be a dictionary containing information related to the game context. It should include at
        least a key named `'short_name'` which represents the short name for the game context. This
        parameter is required when the `cookie` parameter is set.
        
        .-.-.-.
        
        
        
        @ returns The function `_header_formater` returns a dictionary containing HTTP headers based on
        the input parameters `cookie` and `links_for_game`.
        
        .-.-.-.
        
        
        """
        if not cookie:
            return {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "max-age=0",
                "Priority": "u=0, i",
                "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                "Sec-Ch-Ua-Mobile": "?1",
                "Sec-Ch-Ua-Platform": '"Android"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
                "Source": "Docker-LoginManager",
                "Version": f"{FILE_VERSION}",
            }
        else:
            if not links_for_game:
                logger.error("Links for game context are required when cookie is set, but none were provided.")
                raise LoginManagerError("Links for game context must be provided when cookie is set.")
            else:
                gameformat = links_for_game.get('short_name')
                if not gameformat:
                    logger.error("Short name for game context is required in links_for_game, but none were provided.")
                    raise LoginManagerError("Short name for game context must be provided in links_for_game.")
            api_headers: Dict[str,str] = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Cookie": cookie,
                "Origin": "https://act.hoyolab.com",
                "Referer": "https://act.hoyolab.com/",
                "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"macOS"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "x-rpc-signgame": gameformat
            }
            return api_headers

    @staticmethod
    def _create_retry_session() -> requests.Session:
        """
        The function `_create_retry_session` creates a `requests.Session` object with retry
        functionality for specific HTTP status codes and methods.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        
        
        @ returns A requests.Session object with a retry strategy configured to retry a request up to 3
        times with a backoff factor of 0.5 seconds, for specific HTTP status codes (500, 502, 503, 504)
        and allowed HTTP methods (GET).
        
        .-.-.-.
        
        
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],  
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    @staticmethod
    def _get_assets_image(url: str) -> Image.Image:
        """
        The function `_get_assets_image` retrieves an image from a specified URL using requests and
        returns it as a PIL Image object, handling various exceptions that may occur during the process.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param url (str)  - The `url` parameter in the `_get_assets_image` function is a string that
        represents the URL from which an image asset is fetched.
        
        .-.-.-.
        
        
        
        @ returns The function `_get_assets_image` returns an `Image.Image` object, which is an image
        representation typically used in image processing libraries like PIL (Pillow).
        
        .-.-.-.
        
        
        """
        headers = LoginManager._header_formater()
        session = LoginManager._create_retry_session()
        try:
            response = session.get(url, headers=headers, timeout=(5, 15))
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except UnidentifiedImageError as e:
            raise AssetFetchError(f"Unrecognized image format from assets: {url}", url=url, original_exception=e) from e
        except OSError as e:
            raise AssetFetchError(f"OS or PIL error opening image from assets: {url}", url=url, original_exception=e) from e
        except requests.exceptions.RequestException as e:
            raise AssetFetchError(f"Request failed for asset image: {url}", url=url, original_exception=e) from e
        finally:
            session.close()

    @staticmethod
    def _fetch_image_from_url(url: str) -> Image.Image:
        """
        This function fetches an image from a given URL and handles various exceptions that may occur
        during the process.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param url (str)  - The `url` parameter in the `_fetch_image_from_url` function is a string
        that represents the URL from which an image is fetched.
        
        .-.-.-.
        
        
        
        @ returns The function `_fetch_image_from_url` is returning an image object of type
        `Image.Image` fetched from the provided URL.
        
        .-.-.-.
        
        
        """
        try:
            response = requests.get(url, timeout=(5,15), headers={'User-Agent': LoginManager._header_formater()['User-Agent']})
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except UnidentifiedImageError as e:
            raise AssetFetchError(f"Unrecognized image format from icon URL: {url}", url=url, original_exception=e) from e
        except OSError as e:
            raise AssetFetchError(f"OS or PIL error opening image from icon URL: {url}", url=url, original_exception=e) from e
        except requests.exceptions.RequestException as e:
            raise AssetFetchError(f"Request failed for icon image: {url}", url=url, original_exception=e) from e
    
    @staticmethod
    def _time_formater(time_unix_str: str) -> str:
        """
        The function `_time_formater` converts a Unix timestamp to a human-readable format indicating
        the time remaining until the target time.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param time_unix_str (str)  - The function `_time_formater` takes a Unix timestamp as input in
        the form of a string (`time_unix_str`). It converts this Unix timestamp to a human-readable
        format representing the time difference between the input timestamp and the current time in
        days, hours, and minutes.
        
        .-.-.-.
        
        
        
        @ returns The function `_time_formater` returns a formatted string representing the time
        difference between the current time and a target time specified in Unix timestamp format. The
        returned string indicates the remaining time in days, hours, and minutes until the target time
        is reached. If the target time has already passed or is imminent, it returns "Refresh passed /
        imminent". If the remaining time is less than a minute, it
        
        .-.-.-.
        
        
        """
        try:
            input_time_unix = int(time_unix_str)
        except ValueError as e:
            logger.error(f"Invalid time string for _time_formater: {time_unix_str}")
            raise ValueError(f"Invalid time string for _time_formater: {time_unix_str}") from e 
            
        now_utc = datetime.now(timezone.utc)
        target_time_utc = datetime.fromtimestamp(input_time_unix, timezone.utc) 
        delta_to_refresh = target_time_utc - now_utc

        if delta_to_refresh.total_seconds() <= 0:
            return "Refresh passed / imminent" 

        days = delta_to_refresh.days
        hours, remainder = divmod(int(delta_to_refresh.total_seconds()), 3600)
        hours = hours % 24
        minutes, _ = divmod(remainder % 3600, 60)

        if days > 0 :
             return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return "<1m (Soon)"

    def _api_request(self, method: str, url: str, cookie: Optional[str] = None, 
        
                     links_for_game_ctx: Optional[Dict[str,str]] = None,
                     params: Optional[Dict] = None, json_payload: Optional[Dict] = None) -> Dict:
        """
        This function sends API requests using the specified method (GET or POST) with optional
        parameters and handles various exceptions that may occur during the request.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param method (str)  - The `method` parameter in the `_api_request` function specifies the HTTP
        method to be used for the API request. It can be either "GET" or "POST" to indicate whether the
        request should be a GET or POST request, respectively.
        
        .-.-.-.
        
        @ param url (str)  - The `url` parameter in the `_api_request` method is a string that
        represents the URL to which the API request will be sent. This URL specifies the location of the
        API endpoint that the method will interact with.
        
        .-.-.-.
        
        @ param cookie (Optional[str])  - The `cookie` parameter in the `_api_request` method is used to
        pass a cookie value for the HTTP request headers. It is an optional parameter, so you can
        provide a cookie value if needed for authentication or session management. If not provided, the
        cookie parameter will default to `None`.
        
        .-.-.-.
        
        @ param links_for_game_ctx (Optional[Dict[str,str]])  - The `links_for_game_ctx` parameter in
        the `_api_request` method is a dictionary that contains links related to the game context. It is
        an optional parameter, meaning it can be provided but is not required. The dictionary should
        have keys and values where the keys represent some context information related to the
        
        .-.-.-.
        
        @ param params (Optional[Dict])  - The `params` parameter in the `_api_request` method is used
        to pass a dictionary of parameters to be sent in the query string of the HTTP request. These
        parameters are typically used for GET requests to include additional data that the server can
        use to process the request.
        
        .-.-.-.
        
        @ param json_payload (Optional[Dict])  - The `json_payload` parameter in the `_api_request`
        method is used to pass a dictionary containing data that will be sent as a JSON payload in the
        request body when the HTTP method is "POST". This data will be serialized to JSON format before
        being sent in the request.
        
        .-.-.-.
        
        
        
        @ returns A dictionary containing the JSON response from the API request is being returned.
        
        .-.-.-.
        
        
        """
        headers = self._header_formater(cookie=cookie, links_for_game=links_for_game_ctx)
        response_text_preview = None
        session = self._create_retry_session()
        try:
            if method.upper() == "GET":
                response = session.get(url, headers=headers, params=params, timeout=(5,15))
            elif method.upper() == "POST":
                response = session.post(url, headers=headers, params=params, json=json_payload, timeout=(5,15))
            else:
                raise ValueError(f"Unsupported HTTP method used in _api_request: {method}")
            
            response_text_preview = response.text 
            response.raise_for_status() 
            return response.json()
        except requests.exceptions.Timeout as e:
            raise APIRequestError("API request timed out", url=url, original_exception=e) from e
        except requests.exceptions.HTTPError as e:
            raise APIRequestError(f"HTTP Error {e.response.status_code}", url=url, 
                                  status_code=e.response.status_code, 
                                  response_text=e.response.text, original_exception=e) from e
        except requests.exceptions.RequestException as e:
            raise APIRequestError("API request failed (network or other issue)", url=url, original_exception=e) from e
        except json.JSONDecodeError as e:
            raise APIRequestError("Failed to decode JSON response", url=url, 
                                  response_text=response_text_preview, original_exception=e) from e
        finally:
            session.close()

    def _reward_info(self, cookie: str, links: Dict[str, str]) -> List[Dict[str, str]]:
        """
        The function `_reward_info` retrieves and validates reward information from an API response
        based on provided links and cookie.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param cookie (str)  - The `cookie` parameter in the `_reward_info` method is expected to be a
        string. It is used for making API requests and authenticating the user session.
        
        .-.-.-.
        
        @ param links (Dict[str, str])  - The `links` parameter is a dictionary containing key-value
        pairs where the key is a string and the value is also a string. In the provided code snippet,
        the `links` parameter is used to retrieve a URL for rewards information. The `reward_info` key
        is specifically used to fetch the URL
        
        .-.-.-.
        
        
        
        @ returns A list of dictionaries containing reward information is being returned. Each
        dictionary in the list represents a reward with key-value pairs providing details about the
        reward.
        
        .-.-.-.
        
        
        """
        rewards_url = links.get('reward_info')
        if not rewards_url: raise APIDataError("'reward_info' URL missing in links configuration.")
        
        response_data = self._api_request("GET", rewards_url, cookie=cookie, links_for_game_ctx=links)
        
        if response_data.get('retcode') != 0:
            raise APIDataError(f"API error for reward_info", retcode=response_data.get('retcode'), 
                               api_message=response_data.get('message'), api_response_preview=str(response_data)[:200])
        
        data_payload = response_data.get('data')
        if not data_payload or 'awards' not in data_payload:
            raise APIDataError("'data' or 'awards' field missing in reward_info response", 
                               api_response_preview=str(response_data)[:200])
        if not isinstance(data_payload['awards'], list):
            raise APIDataError("'awards' field is not a list in reward_info response",
                               api_response_preview=str(response_data)[:200])
        return data_payload['awards']

    def _day_counter(self, cookie: str, links: Dict[str, str]) -> int:
        """
        This function retrieves the total number of days signed in a day counter API response and
        handles various error scenarios.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param cookie (str)  - The `cookie` parameter in the `_day_counter` method is a string that
        represents the cookie value used for authentication or session management in the API request. It
        is typically sent in the headers of the HTTP request to authenticate the user's session.
        
        .-.-.-.
        
        @ param links (Dict[str, str])  - The `links` parameter in the `_day_counter` method is expected
        to be a dictionary containing key-value pairs where the key is a string and the value is also a
        string. The method retrieves the 'day_counter' URL from the `links` dictionary and uses it to
        make an API request.
        
        .-.-.-.
        
        
        
        @ returns The `_day_counter` method returns an integer value representing the total number of
        days signed in the response data obtained from an API request to the 'day_counter' URL.
        
        .-.-.-.
        
        
        """
        day_count_url = links.get('day_counter')
        if not day_count_url: raise APIDataError("'day_counter' URL missing in links configuration.")

        response_data = self._api_request("GET", day_count_url, cookie=cookie, links_for_game_ctx=links)
        
        if response_data.get('retcode') != 0:
            raise APIDataError(f"API error for day_counter", retcode=response_data.get('retcode'), 
                               api_message=response_data.get('message'), api_response_preview=str(response_data)[:200])
        
        data_payload = response_data.get('data')
        if not data_payload or 'total_sign_day' not in data_payload:
            if data_payload and data_payload.get('total_sign_day') is None and 'is_sign' in data_payload:
                 logger.info("'total_sign_day' missing but 'is_sign' present, assuming 0 days signed.")
                 return 0
            raise APIDataError("'data' or 'total_sign_day' field missing in day_counter response",
                               api_response_preview=str(response_data)[:200])
        try:
            return int(data_payload['total_sign_day'])
        except (ValueError, TypeError) as e:
            raise APIDataError(f"Invalid 'total_sign_day' format: {data_payload.get('total_sign_day')}",
                               api_response_preview=str(response_data)[:200]) from e

    def _time_info(self, cookie: str, links: Dict[str, str]) -> str:
        """
        The function `_time_info` retrieves and returns the refresh time from a specified URL in the
        provided links dictionary, handling various error cases.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param cookie (str)  - The `cookie` parameter in the `_time_info` method is a string that
        represents the cookie value used for authentication or session management in the API request. It
        is typically sent in the headers of the HTTP request to authenticate the user's session.
        
        .-.-.-.
        
        @ param links (Dict[str, str])  - The `links` parameter in the `_time_info` method is expected
        to be a dictionary containing key-value pairs. The method retrieves the 'time_info' URL from the
        `links` dictionary and makes an API request to that URL. If the 'time_info' URL is missing in
        the `links
        
        .-.-.-.
        
        
        
        @ returns The function `_time_info` is returning the value of the 'refresh_time' key from the
        'data' payload in the response data.
        
        .-.-.-.
        
        
        """
        time_url = links.get('time_info')
        if not time_url: raise APIDataError("'time_info' URL missing in links configuration.")

        response_data = self._api_request("GET", time_url, cookie=cookie, links_for_game_ctx=links)
        if response_data.get('retcode') != 0:
            raise APIDataError(f"API error for time_info", retcode=response_data.get('retcode'),
                               api_message=response_data.get('message'), api_response_preview=str(response_data)[:200])
        data_payload = response_data.get('data')
        if not data_payload or 'refresh_time' not in data_payload:
            if links.get("short_name") == "gi" and data_payload and 'resign_time' in data_payload:
                 logger.warning("Using 'resign_time' as 'refresh_time' for Genshin Impact time_info.")
                 return data_payload['resign_time']
            raise APIDataError("'data' or 'refresh_time' missing in time_info response",
                               api_response_preview=str(response_data)[:200])
        return data_payload['refresh_time']
        
    def _signin_check(self, cookie: str, links: Dict[str, str]) -> bool:
        """
        The function `_signin_check` checks the sign-in status by making an API request and handling
        various response scenarios and errors with retries.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param cookie (str)  - The `cookie` parameter in the `_signin_check` method is a string that
        represents the cookie value used for authentication in the API request. It is passed along with
        the API request to authenticate the user's session.
        
        .-.-.-.
        
        @ param links (Dict[str, str])  - The `links` parameter in the `_signin_check` method is a
        dictionary containing URLs related to the sign-in check process. It should have keys like
        'signin_check' and 'day_counter' which are used to construct the URL for the sign-in check
        endpoint. If any of these keys are missing
        
        .-.-.-.
        
        
        
        @ returns The `_signin_check` method returns a boolean value indicating whether the user is
        signed in or not.
        
        .-.-.-.
        
        
        """
        signin_check_url = links.get('signin_check', links.get('day_counter'))
        if not signin_check_url: raise APIDataError("'signin_check' or 'day_counter' URL missing in links configuration.")

        max_retries = 2 # Try once, then retry once for specific error
        for attempt in range(max_retries + 1):
            try:
                response_data = self._api_request("GET", signin_check_url, cookie=cookie, links_for_game_ctx=links)
                
                if response_data.get('retcode') == 0:
                    data_payload = response_data.get('data')
                    if data_payload is None:
                        logger.info(f"Signin_check: 'data' is null, assuming not signed in. Response: {response_data}")
                        return False
                    if 'is_sign' not in data_payload:
                        if data_payload.get('total_sign_day', -1) == 0:
                            logger.info(f"Signin_check: 'is_sign' missing, but 'total_sign_day' is 0. Assuming not signed in.")
                            return False
                        raise APIDataError("'is_sign' missing in signin_check response and cannot infer status.",
                                        key_missing='is_sign', api_response_preview=str(response_data)[:200])
                    return bool(data_payload['is_sign'])
                
                elif response_data.get('retcode') == -500001 and attempt < max_retries :
                    logger.warning(f"Retrying signin_check for {links.get('name', 'game')} ({links.get('short_name')}) due to retcode -500001 (Attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(3 * (attempt + 1)) 
                    continue
                else:
                    raise APIDataError(f"API error for signin_check", retcode=response_data.get('retcode'),
                                    api_message=response_data.get('message'), api_response_preview=str(response_data)[:200])
            except APIRequestError as e: 
                if attempt < max_retries:
                    logger.warning(f"Retrying signin_check for {links.get('name', 'game')} ({links.get('short_name')}) due to APIRequestError: {e} (Attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(3 * (attempt + 1))
                    continue
                else:
                    raise 
        return False

    def _signin(self, cookie: str, links: Dict[str, str]) -> bool:
        """
        The `_signin` function sends a POST request to a specified URL with a cookie and payload,
        handling different response scenarios based on the returned data.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param cookie (str)  - The `cookie` parameter is a string that represents the cookie value used
        for authentication in the API request. It is passed to the `_signin` method to authenticate the
        user before making the API call.
        
        .-.-.-.
        
        @ param links (Dict[str, str])  - The `_signin` method takes in a `cookie` parameter of type
        `str` and a `links` parameter of type `Dict[str, str]`. The `links` parameter is expected to
        contain keys such as 'signin', 'id', and 'lang'.
        
        .-.-.-.
        
        
        
        @ returns The `_signin` method returns a boolean value - `True` if the sign-in operation was
        successful, and raises exceptions (`APIDataError` or `SigninError`) if there are specific errors
        encountered during the sign-in process.
        
        .-.-.-.
        
        
        """
        signin_url = links.get('signin')
        act_id = links.get('id')
        if not signin_url or not act_id: 
            raise APIDataError("'signin' URL or 'id' missing in links configuration.")
        
        payload = {"act_id": act_id, "lang": links.get("lang", "en-us")} 
        
        response_data = self._api_request("POST", signin_url, cookie=cookie, 
                                          links_for_game_ctx=links, json_payload=payload)
        
        retcode = response_data.get('retcode')
        api_msg = response_data.get('message', '').lower()

        if retcode == 0 and "ok" in api_msg:
            return True
        elif retcode == -5003 or ("already signed in" in api_msg or "claimed" in api_msg):
            logger.info(f"Sign-in API reported already signed in/claimed (retcode {retcode}): {api_msg}")
            return True
        else:
            gt_result = response_data.get('data', {}).get('gt_result', {})
            gt_risk_code = gt_result.get('risk_code') if isinstance(gt_result, dict) else None
            
            if gt_risk_code is not None and gt_risk_code != 0 :
                 raise SigninError("Sign-in failed due to captcha/risk control.", 
                                   retcode=retcode, api_message=api_msg, gt_risk_code=gt_risk_code)
            raise SigninError(f"Sign-in API call failed: {api_msg}", 
                              retcode=retcode, api_message=api_msg)

    def _data_parser(self, rewards: List[Dict[str, str]], day_count_from_api: int, 
                     refresh_time_formatted: str, is_already_checked_in: bool) -> Dict[str, Any]:
        """
        The function `_data_parser` parses reward data based on the current day index and other
        parameters, handling cases where rewards list is empty or index is out of bounds.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param rewards (List[Dict[str, str]])  - The `_data_parser` function takes in several
        parameters:
        
        .-.-.-.
        
        @ param day_count_from_api (int)  - `day_count_from_api` is an integer representing the current
        day count received from an API.
        
        .-.-.-.
        
        @ param refresh_time_formatted (str)  - The `refresh_time_formatted` parameter in the
        `_data_parser` function is expected to be a string that represents the formatted time for
        refreshing data. This string should follow a specific format that is suitable for display
        purposes, such as "HH:MM:SS" or "YYYY-MM-DD HH:MM
        
        .-.-.-.
        
        @ param is_already_checked_in (bool)  - The `is_already_checked_in` parameter in the
        `_data_parser` function is a boolean flag that indicates whether the user has already checked
        in. If `is_already_checked_in` is `True`, it means the user has already checked in for the
        current day. If it is `False`, it
        
        .-.-.-.
        
        
        
        @ returns The `_data_parser` function returns a dictionary containing information about rewards
        for the current day and potentially the next day. The dictionary includes keys such as "icon_1",
        "name_1", "cnt_1" for the current day's reward data, and "icon_2", "name_2", "cnt_2" for the
        next day's reward data if it's not the
        
        .-.-.-.
        
        
        """
        current_day_idx = day_count_from_api
        if is_already_checked_in:
            if current_day_idx == 0 :
                 logger.warning(f"Data parser: checked_in is true, but day_count_api is 0. Using 0 as current_day_idx.")
            else:
                current_day_idx = day_count_from_api - 1

        if not rewards:
            raise APIDataError("Cannot parse data: rewards list is empty.")
        if not (0 <= current_day_idx < len(rewards)):
            raise APIDataError(f"Calculated reward index {current_day_idx} is out of bounds for rewards (len {len(rewards)}). day_count_api: {day_count_from_api}, checked_in: {is_already_checked_in}")

        today_reward_data = rewards[current_day_idx]
        is_end_of_month_for_display = (current_day_idx + 1) >= len(rewards)

        data_to_return: Dict[str, Any] = {
            "icon_1": today_reward_data.get("icon"), 
            "name_1": today_reward_data.get("name"), 
            "cnt_1": today_reward_data.get("cnt"), 
            "end_of_month": is_end_of_month_for_display,
            "days": current_day_idx + 1,
            "refresh": refresh_time_formatted
        }

        if not is_end_of_month_for_display:
            next_reward_data = rewards[current_day_idx + 1]
            data_to_return.update({
                "icon_2": next_reward_data.get("icon"), 
                "name_2": next_reward_data.get("name"), 
                "cnt_2": next_reward_data.get("cnt")
            })
        return data_to_return

    def _get_asset_with_fallback(self, asset_category: str, asset_name_template: str, 
                                item_identifier: Any, primary_game_short_name: str) -> Optional[Image.Image]:
        """
        This function retrieves an asset image with a fallback option if the primary asset fails to
        load.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param asset_category (str)  - The `asset_category` parameter in the `_get_asset_with_fallback`
        method represents the category of the asset you are trying to retrieve. It could be something
        like "characters", "weapons", "backgrounds", etc. This parameter helps in constructing the URL
        path to locate the specific asset within the
        
        .-.-.-.
        
        @ param asset_name_template (str)  - The `asset_name_template` parameter is a string that
        represents the template for the asset name. It is used to construct the final URL for fetching
        the asset image. The template may contain placeholders that will be replaced with actual values
        during the URL construction process.
        
        .-.-.-.
        
        @ param item_identifier (Any)  - The `item_identifier` parameter is used as an identifier for
        the specific asset you are trying to retrieve. It could be a unique identifier such as an ID or
        name that helps in locating the asset within the game assets.
        
        .-.-.-.
        
        @ param primary_game_short_name (str)  - The `primary_game_short_name` parameter in the
        `_get_asset_with_fallback` method is used to specify the short name of the primary game for
        which the asset is being retrieved. This parameter helps in determining the asset folder path
        for the primary game from the `GAME_ASSET_PATHS` dictionary
        
        .-.-.-.
        
        
        
        @ returns The method `_get_asset_with_fallback` returns an optional `Image.Image` object or
        `None`.
        
        .-.-.-.
        
        
        """
        primary_game_asset_folder = self.GAME_ASSET_PATHS.get(primary_game_short_name, self.GAME_ASSET_PATHS["default_gi"])
        gi_asset_folder = self.GAME_ASSET_PATHS["gi"]

        primary_url_template = f'{self.CDN_BASE_URL}{primary_game_asset_folder}{asset_category}/{asset_name_template}'
        gi_fallback_url_template = f'{self.CDN_BASE_URL}{gi_asset_folder}{asset_category}/{asset_name_template}'
        
        primary_url = primary_url_template.format(game=primary_game_short_name, id=item_identifier)
        try:
            return self._get_assets_image(primary_url)
        except AssetFetchError as e_primary:
            logger.warning(f"Failed to load primary asset '{primary_url}': {e_primary}. Trying GI fallback.")
            gi_fallback_url = gi_fallback_url_template.format(game="gi", id=item_identifier)
            if primary_url == gi_fallback_url: # Already tried GI or GI was primary
                logger.error(f"GI fallback URL is same as primary and failed: {gi_fallback_url}")
                return None
            try:
                return self._get_assets_image(gi_fallback_url)
            except AssetFetchError as e_fallback:
                logger.error(f"Failed to load GI fallback asset '{gi_fallback_url}': {e_fallback}")
                return None

    def _card_generator(self, card_data: Dict[str, Any], game_short_name: str) -> Optional[Image.Image]:
        """
        The `_card_generator` function generates a card image with various elements based on input data
        and game information.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param card_data (Dict[str, Any])  - The `card_data` parameter is a dictionary containing
        information about the card to be generated. It includes details such as the names and quantities
        of rewards, icons for the card, whether it is the end of the month, and other relevant data for
        creating the card image.
        
        .-.-.-.
        
        @ param game_short_name (str)  - The `game_short_name` parameter is a string that represents the
        short name or identifier of a game. It is used within the `_card_generator` method to retrieve
        specific assets related to the game being processed.
        
        .-.-.-.
        
        
        
        @ returns The `_card_generator` function returns an image (`Image.Image`) that is generated
        based on the input `card_data` and `game_short_name`. If any errors occur during the card
        generation process, it will return `None`.
        
        .-.-.-.
        
        
        """
        if not self.default_font or not self.reward_font:
            logger.error("Essential fonts not loaded in LoginManager, cannot generate card text.")
            return None

        try:
            base_number = random.randint(1, 9)
            base_img = self._get_asset_with_fallback("cards", "{game}_cards_{id}.png", base_number, game_short_name)
            if not base_img:
                logger.error(f"Failed to load ANY base card image for {game_short_name} or GI fallback.")
                return None # Cannot proceed without a base image
            base_img = base_img.convert('RGB')

            frame_img = self._get_assets_image("https://cdn.hoyohelper.com/frame/frame_1.png")
            if frame_img:
                frame_img = frame_img.convert("RGBA") if frame_img.mode != "RGBA" else frame_img
                base_img.paste(frame_img, (20, 68), frame_img)
                base_img.paste(frame_img, (20, 284), frame_img)
            else:
                logger.warning("Failed to load frame image for card.")
            
            if card_data.get('icon_1'):
                try:
                    icon_1_img = self._fetch_image_from_url(card_data['icon_1'])
                    if icon_1_img:
                        icon_1_img = icon_1_img.resize((100, 100), Image.Resampling.LANCZOS)
                        if icon_1_img.mode != 'RGBA': icon_1_img = icon_1_img.convert('RGBA')
                        base_img.paste(icon_1_img, (40, 88), icon_1_img)
                except (AssetFetchError, KeyError) as e_icon1:
                     logger.warning(f"Failed to load or process icon_1 ({card_data.get('icon_1')}): {e_icon1}")

            if not card_data.get('end_of_month', False) and card_data.get('icon_2'):
                try:
                    icon_2_img = self._fetch_image_from_url(card_data['icon_2'])
                    if icon_2_img:
                        icon_2_img = icon_2_img.resize((100, 100), Image.Resampling.LANCZOS)
                        if icon_2_img.mode != 'RGBA': icon_2_img = icon_2_img.convert('RGBA')
                        base_img.paste(icon_2_img, (40, 304), icon_2_img)
                except (AssetFetchError, KeyError) as e_icon2:
                    logging.warning(f"Failed to load or process icon_2 ({card_data.get('icon_2')}): {e_icon2}")

            d = ImageDraw.Draw(base_img)
            text_fill_main = "Pink"; text_fill_shadow = "Black"; text_fill_alternate = "Purple"

            d.text((180, 80), "Today you got:", font=self.day_title_font, fill=text_fill_shadow)
            reward1_text = f"{card_data.get('name_1','?')} x{card_data.get('cnt_1','?')}"
            d.text((179, 119), reward1_text, font=self.reward_font, fill=text_fill_shadow) 
            d.text((180, 120), reward1_text, font=self.reward_font, fill=text_fill_alternate)   

            if card_data.get('end_of_month', False):
                sticker_number = random.randint(2, 153)
                sticker_img = self._get_asset_with_fallback("stickers", "{game}_stickers_{id}.png", sticker_number, game_short_name)
                if sticker_img:
                    sticker_img = sticker_img.resize((100, 100), Image.Resampling.LANCZOS)
                    if sticker_img.mode != 'RGBA': sticker_img = sticker_img.convert('RGBA')
                    base_img.paste(sticker_img, (40, 304), sticker_img)
                else:
                    logger.warning(f"Failed to load sticker for {game_short_name} or GI fallback.")
                
                d.text((180, 300), "No More rewards this month!", font=self.day_title_font, fill=text_fill_shadow)
                eom_text_l1 = "You have claimed all rewards this month!"
                eom_text_l2 = f"Come back in {card_data.get('refresh','soon')}\nto see next month's rewards!"
                small_multiline_font = self.default_font.font_variant(size=18) if self.default_font else ImageFont.load_default()
                d.text((179, 339), eom_text_l1 + "\n" + eom_text_l2, font=small_multiline_font, fill=text_fill_main)
                d.text((180, 340), eom_text_l1 + "\n" + eom_text_l2, font=small_multiline_font, fill=text_fill_shadow)
            elif 'name_2' in card_data:
                d.text((180, 300), f"In {card_data.get('refresh','soon')} you will get:", font=self.day_title_font, fill=text_fill_shadow)
                reward2_text = f"{card_data.get('name_2','?')} x{card_data.get('cnt_2','?')}"
                d.text((179, 339), reward2_text, font=self.reward_font, fill=text_fill_shadow)
                d.text((180, 340), reward2_text, font=self.reward_font, fill=text_fill_alternate)

            days_value = card_data.get('days', 0)
            days_text = str(days_value if days_value != 0 else '?')
            day_label = "day" if days_value == 1 else "days"
            
            d.text((865, 20), "Checked in", font=self.small_text_font, fill=text_fill_shadow)
            day_num_width = d.textlength(days_text, font=self.large_day_font)
            day_num_x_shadow = (900 + 924 - day_num_width) / 2 - 1; day_num_x_main = day_num_x_shadow + 1
            d.text((day_num_x_shadow , 59), days_text, font=self.large_day_font, fill=text_fill_main)
            d.text((day_num_x_main , 60), days_text, font=self.large_day_font, fill=text_fill_shadow)
            d.text((835, 100), f"{day_label} this month!", font=self.small_text_font, fill=text_fill_shadow)

            portrait_number = random.randint(2, 32)
            portrait_img = self._get_asset_with_fallback("car_dec", "{game}_car_dec_{id}.png", portrait_number, game_short_name)
            if portrait_img:
                if portrait_img.mode != 'RGBA': portrait_img = portrait_img.convert('RGBA')
                base_img.paste(portrait_img, (630, 422), portrait_img)
            else:
                logger.warning(f"Failed to load portrait for {game_short_name} or GI fallback.")
            return base_img
        except Exception as e:
            logger.error(f"An unexpected error occurred during card generation: {e}", exc_info=True)
            return None # Return None on any unexpected card generation error

    def process_account(self, cookie: str, account_name: str, game_links: Dict[str, str], 
                        game_short_name: str, account_webhook_url: Optional[str] = None) -> bool:
        """
        The `process_account` function processes account information for a specific game, handling
        various checks, actions, and error scenarios, with optional webhook notifications.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param cookie (str)  - The `process_account` method you provided seems to be a comprehensive
        function for handling account processing in a gaming context. It covers various scenarios such
        as checking sign-in status, generating reward cards, sending webhooks for notifications, and
        handling different types of errors that may occur during the process.
        
        .-.-.-.
        
        @ param account_name (str)  - The `process_account` method takes in several parameters to handle
        the processing of an account for a game. Here's a breakdown of the parameters:
        
        .-.-.-.
        
        @ param game_links (Dict[str, str])  - The `process_account` method you provided seems to be a
        part of a larger system for managing game accounts. It takes several parameters and performs
        various operations related to processing an account.
        
        .-.-.-.
        
        @ param game_short_name (str)  - The `game_short_name` parameter in the `process_account` method
        is a string that represents the short name or abbreviation of the game associated with the
        account being processed. It is used for logging and generating messages related to the specific
        account and game.
        
        .-.-.-.
        
        @ param account_webhook_url (Optional[str])  - The `account_webhook_url` parameter in the
        `process_account` method is an optional URL where webhook notifications will be sent for account
        processing updates. If provided, the method will attempt to send notifications to this URL
        during various stages of the account processing. If not provided, the method will still execute
        
        .-.-.-.
        
        
        
        @ returns A boolean value is being returned from the `process_account` method. It returns `True`
        if the account processing is successful, and `False` if there are any errors or issues during
        the processing.
        
        .-.-.-.
        
        
        """
        full_account_name_for_logs = f"{account_name} ({game_short_name})"
        if not cookie or not game_links or not account_name or not game_short_name:
            logger.critical(f"CRITICAL: Missing parameters for processing {full_account_name_for_logs}. This is a bug.")
            try:
                self.webhook_manager.send(f"CRITICAL BUG: Missing parameters for {full_account_name_for_logs}. Cannot proceed.", url=account_webhook_url)
            except Exception as e_wh:
                logger.error(f"Failed to send critical bug webhook: {e_wh}")
            return False

        try:
            is_already_signed_in = self._signin_check(cookie, game_links)
            logger.info(f"{full_account_name_for_logs}: Already signed in: {is_already_signed_in}")

            rewards_list = self._reward_info(cookie, game_links)
            day_count_api = self._day_counter(cookie, game_links)
            refresh_time_unix = self._time_info(cookie, game_links)
            refresh_time_formatted = self._time_formater(refresh_time_unix) 

            parsed_card_data = self._data_parser(rewards_list, day_count_api, refresh_time_formatted, is_already_signed_in)
            card_image = None
            try:
                card_image = self._card_generator(parsed_card_data, game_short_name)
                if card_image is None: # Explicitly check if card_generator returned None
                    logger.warning(f"{full_account_name_for_logs}: Card image generation resulted in None, will proceed without card image.")
            except CardGenerationError as e_card_gen:
                logger.error(f"{full_account_name_for_logs}: Failed to generate reward card due to CardGenerationError: {e_card_gen}", exc_info=True)
                self.webhook_manager.send(f"WARNING: {full_account_name_for_logs} - Could not generate reward card ({e_card_gen.message}). Sign-in will proceed.", url=account_webhook_url)
            except Exception as e_card_unexpected: # Catch any other unexpected error from card_generator
                logger.error(f"{full_account_name_for_logs}: Unexpected error during card generation: {e_card_unexpected}", exc_info=True)
                self.webhook_manager.send(f"WARNING: {full_account_name_for_logs} - Unexpected error generating reward card. Sign-in will proceed.", url=account_webhook_url)


            if is_already_signed_in:
                logger.info(f"{full_account_name_for_logs} has already signed in today.")
                message = f"{full_account_name_for_logs} has already signed in today. Current rewards:"
                self.webhook_manager.send(message, card_image, url=account_webhook_url)
                return True
            else: 
                logger.info(f"{full_account_name_for_logs} has not signed in today. Attempting sign-in...")
                message_before_signin = f"{full_account_name_for_logs} is attempting to sign in. Today's expected reward:"
                self.webhook_manager.send(message_before_signin, card_image, url=account_webhook_url)

                time.sleep(random.uniform(1, 3))
                signin_successful = self._signin(cookie, game_links) 
                time.sleep(random.uniform(1, 2))

                if signin_successful:
                    final_check_signed_in = self._signin_check(cookie, game_links) 
                    if final_check_signed_in:
                        logger.info(f"{full_account_name_for_logs} successfully signed in and verified.")
                        self.webhook_manager.send(f"SUCCESS: {full_account_name_for_logs} has successfully signed in and claimed their reward!", url=account_webhook_url) 
                        return True
                    else:
                        logger.warning(f"{full_account_name_for_logs}: Sign-in API reported success/already done, but subsequent check shows not signed in. State is inconsistent.")
                        self.webhook_manager.send(f"WARNING: {full_account_name_for_logs} - Sign-in status is inconsistent after attempt. Please check manually.", url=account_webhook_url)
                        return False 
                else: # Should ideally be caught by SigninError from _signin
                    logger.warning(f"{full_account_name_for_logs}: _signin returned False without raising an exception. This is unexpected.")
                    self.webhook_manager.send(f"ERROR: {full_account_name_for_logs} - Sign-in attempt failed (unexpected return).", url=account_webhook_url)
                    return False

        except APIRequestError as e:
            logger.error(f"{full_account_name_for_logs}: Failed during API request: {e}", exc_info=True)
            self.webhook_manager.send(f"ERROR: {full_account_name_for_logs} - API Request Error: {e.message}", url=account_webhook_url)
            return False
        except APIDataError as e:
            logger.error(f"{full_account_name_for_logs}: Failed due to API data issue: {e}", exc_info=True)
            self.webhook_manager.send(f"ERROR: {full_account_name_for_logs} - API Data Error: {e.message}", url=account_webhook_url)
            return False
        except SigninError as e:
            logger.error(f"{full_account_name_for_logs}: Sign-in process failed: {e}", exc_info=True)
            self.webhook_manager.send(f"ERROR: {full_account_name_for_logs} - Sign-in Failed: {e.message}", url=account_webhook_url)
            return False
        except ValueError as e: # Catch string to int conversion errors, etc.
            logger.error(f"{full_account_name_for_logs}: Invalid data encountered: {e}", exc_info=True)
            self.webhook_manager.send(f"ERROR: {full_account_name_for_logs} - Invalid Data: {e}", url=account_webhook_url)
            return False
        except LoginManagerError as e: 
            logger.error(f"{full_account_name_for_logs}: A login process error occurred: {e}", exc_info=True)
            self.webhook_manager.send(f"ERROR: {full_account_name_for_logs} - Login Process Error: {e.message}", url=account_webhook_url)
            return False
        except Exception as e:
            logger.critical(f"{full_account_name_for_logs}: An UNEXPECTED error occurred in process_account: {e}", exc_info=True)
            try:
                self.webhook_manager.send(f"CRITICAL UNEXPECTED ERROR: {full_account_name_for_logs} - {type(e).__name__}: {str(e)[:100]}. Check server logs!", url=account_webhook_url)
            except Exception as e_wh_crit:
                logger.error(f"Failed to send CRITICAL UNEXPECTED error webhook: {e_wh_crit}")
            return False