FILE_VERSION = "0.1.0"

import requests
import os
import logging
from PIL import Image
from io import BytesIO
from typing import Optional, Dict, Tuple

from .exceptions import WebhookError 

class WebhookManager:
    def __init__(self, default_url: Optional[str] = None):
        self.default_url = default_url
        if not self.default_url:
            self.default_url = os.getenv("DISCORD_WEBHOOK")
        
        if not self.default_url:
            logging.warning("WebhookManager initialized without a default URL and DISCORD_WEBHOOK env var is not set.")

    def _target_url_display(self, url_string: Optional[str]) -> str:
        if url_string and len(url_string) > 30:
            return url_string[:15] + "..." + url_string[-15:]
        return str(url_string)

    def send(self, message: str, card: Optional[Image.Image] = None, url: Optional[str] = None) -> bool:
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