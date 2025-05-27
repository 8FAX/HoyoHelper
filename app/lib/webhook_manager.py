FILE_VERSION = "0.1.1"

import requests
import os
import logging
from PIL import Image
from io import BytesIO
from typing import Optional, Dict, Tuple

from .exceptions import WebhookError 

class WebhookManager:
    def __init__(self, default_url: Optional[str] = None):
        """
        This Python function initializes a `default_url` attribute with a provided value or an
        environment variable, logging a warning if neither is available.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param default_url (Optional[str])  - The `default_url` parameter in the `__init__` method is a
        string that represents the default URL for a webhook. If no `default_url` is provided when
        initializing an instance of the class, it will attempt to retrieve the URL from the environment
        variable `DISCORD_WEBHOOK`. If
        
        .-.-.-.
        
        
        """
        self.default_url = default_url
        if not self.default_url:
            self.default_url = os.getenv("DISCORD_WEBHOOK")
        
        if not self.default_url:
            logging.warning("WebhookManager initialized without a default URL and DISCORD_WEBHOOK env var is not set.")

    def _target_url_display(self, url_string: Optional[str]) -> str:
        """
        This function truncates a URL string to 15 characters from the start and end if the length
        exceeds 30 characters.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param url_string (Optional[str])  - The `url_string` parameter is a string that represents a
        URL.
        
        .-.-.-.
        
        
        
        @ returns The function `_target_url_display` takes in a URL string as input and returns a
        modified version of the URL string. If the input URL string is not empty and its length is
        greater than 30 characters, it returns the first 15 characters of the URL followed by an
        ellipsis (...) and the last 15 characters of the URL. If the input URL string is empty or its
        length is not
        
        .-.-.-.
        
        
        """
        if url_string and len(url_string) > 30:
            return url_string[:15] + "..." + url_string[-15:]
        return str(url_string)

    def send(self, message: str, card: Optional[Image.Image] = None, url: Optional[str] = None) -> bool:
        """
        This Python function sends a webhook message with an optional image attachment to a specified
        URL.
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        Author - Liam Scott
        Last update - 05/26/2025
        
        .-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
        
        @ param message (str)  - The `send` method you provided is a function that sends a message,
        along with an optional image card and URL, via a webhook. The function first determines the
        target URL to send the webhook to, either using the provided URL or a default URL if none is
        specified. It then prepares the message
        
        .-.-.-.
        
        @ param card (Optional[Image.Image])  - The `card` parameter in the `send` method is an optional
        parameter that accepts an image file. If provided, the method will attempt to prepare the image
        for sending in the webhook request. The image will be saved in PNG format and included in the
        request as a file named 'Card.png'.
        
        .-.-.-.
        
        @ param url (Optional[str])  - The `url` parameter in the `send` method is used to specify the
        target URL where the webhook message will be sent. If a specific URL is not provided, the method
        will use a default URL specified by `self.default_url`. If neither a specific URL nor a default
        URL is set,
        
        .-.-.-.
        
        
        
        @ returns A boolean value indicating whether the webhook was sent successfully or not.
        
        .-.-.-.
        
        
        """
        target_url = url if url is not None else self.default_url

        if not target_url:
            err_msg = "Target URL not specified and no default is set."
            logging.error(f"Webhook send: {err_msg}")
            raise WebhookError(err_msg)

        data: Dict[str, str] = {'content': message}
        files: Optional[Dict[str, Tuple[str, BytesIO, str]]] = None
        buffer_for_card: Optional[BytesIO] = None


        if card:
            buffer_for_card = BytesIO()
            try:
                card.save(buffer_for_card, format="PNG")
                buffer_for_card.seek(0)
                files = {'file': ('Card.png', buffer_for_card, 'image/png')}
            except Exception as e:
                logging.error(f"Error preparing card image for webhook: {e}")
                card = None 
                if buffer_for_card:
                    buffer_for_card.close()
                    buffer_for_card = None


        try:
            logging.debug(f"Attempting to send webhook to {self._target_url_display(target_url)} with message: \"{message[:70]}...\"")
            if files:
                response = requests.post(target_url, data=data, files=files, timeout=15)
            else:
                response = requests.post(target_url, data=data, timeout=10)
            response.raise_for_status()
            logging.info(f"Webhook sent successfully to {self._target_url_display(target_url)}.")
            return True
        except requests.exceptions.Timeout as e:
            err_msg = "Request timed out."
            logging.error(f"Failed to send webhook notification to {self._target_url_display(target_url)}: {err_msg}")
            raise WebhookError(err_msg, url=target_url, original_exception=e) from e
        except requests.exceptions.HTTPError as e:
            err_msg = f"HTTP error {e.response.status_code}."
            logging.error(f"Failed to send webhook notification to {self._target_url_display(target_url)}: {err_msg} - {e.response.text[:100]}")
            raise WebhookError(err_msg, url=target_url, original_exception=e) from e
        except requests.exceptions.RequestException as e:
            err_msg = "Network or request error."
            logging.error(f"Failed to send webhook notification to {self._target_url_display(target_url)}: {err_msg} - {e}")
            raise WebhookError(err_msg, url=target_url, original_exception=e) from e
        finally:
            if buffer_for_card and not buffer_for_card.closed:
                buffer_for_card.close()