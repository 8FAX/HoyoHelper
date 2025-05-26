# -------------------------------------------------------------------------------------
# HoYo Helper - a hoyolab helper tool
# Made with ♥ by 8FA (Uilliam.com)

# Copyright (C) 2024 copyright.Uilliam.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see https://github.com/8FAX/HoyoHelper/blob/main/LICENSE.md.
# SPDX-License-Identifier: AGPL-3.0-or-later
# do not remove this notice

# This file is part of HoYo Helper.
# -------------------------------------------------------------------------------------

FILE_VERSION = "0.1.0"

import os
import logging
import time
import asyncio
from typing import Optional

from lib.database import DatabaseManager, Account
from lib.login_manager import LoginManager
from lib.webhook_manager import WebhookManager
from lib.exceptions import HoyoHelperError, WebhookError
from lib.cookie import get_cookie as get_daily_login_cookie_async, format_cookies
from lib.encrypt import decrypt
from lib.settings import ConfigManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - [%(name)s] %(message)s")
logger = logging.getLogger(__name__)

GAME_LINKS_MAP = {
    "gi": {
        "reward_info": "https://sg-hk4e-api.hoyolab.com/event/sol/home?lang=en-us&act_id=e202102251931481",
        "day_counter": "https://sg-hk4e-api.hoyolab.com/event/sol/info?lang=en-us&act_id=e202102251931481",
        "time_info": "https://sg-hk4e-api.hoyolab.com/event/sol/recommend/info?act_id=e202102251931481&plat=PT_PC&lang=en-us",
        "signin_check": "https://sg-hk4e-api.hoyolab.com/event/sol/info?lang=en-us&act_id=e202102251931481",
        "signin": "https://sg-hk4e-api.hoyolab.com/event/sol/sign?lang=en-us",
        "id": "e202102251931481",
        "short_name": "gi",
        "name": "Genshin Impact",
        "lang": "en-us"
    },
    "hsr": {
        "reward_info": "https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/home?lang=en-us&act_id=e202303301540311",
        "day_counter": "https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/info?lang=en-us&act_id=e202303301540311",
        "time_info": "https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/recommend?act_id=e202303301540311&plat=PT_PC&lang=en-us",
        "signin_check": "https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/info?lang=en-us&act_id=e202303301540311",
        "signin": "https://sg-public-api.hoyolab.com/event/luna/hkrpg/os/sign",
        "id": "e202303301540311",
        "short_name": "hkrpg",
        "name": "Honkai: Star Rail",
        "lang": "en-us"
    },
    "zzz": {
        "reward_info": "https://sg-public-api.hoyolab.com/event/luna/zzz/os/home?lang=en-us&act_id=e202406031448091",
        "day_counter": "https://sg-public-api.hoyolab.com/event/luna/zzz/os/info?lang=en-us&act_id=e202406031448091",
        "time_info": "https://sg-public-api.hoyolab.com/event/luna/zzz/os/recommend?act_id=e202406031448091&lang=en-us&plat=PT_M",
        "signin_check": "https://sg-public-api.hoyolab.com/event/luna/zzz/os/info?lang=en-us&act_id=e202406031448091",
        "signin": "https://sg-public-api.hoyolab.com/event/luna/zzz/os/sign",
        "id": "e202406031448091",
        "short_name": "zzz",
        "name": "Zenless Zone Zero",
        "lang": "en-us"
    }
}


class WindolessApp:
    def __init__(self):
        logger.info("Initializing WindolessApp...")
        self.runtime_environment = os.getenv('APP_RUNTIME', 'os').lower()
        
        self.config_manager = ConfigManager(runtime=self.runtime_environment)
        
        try:
            self.database_manager = DatabaseManager(runtime=self.runtime_environment)
            logger.info(f"DatabaseManager initialized. Database file is at: {self.database_manager.database_file}")
        except Exception as e:
            logger.critical(f"CRITICAL: Failed to initialize DatabaseManager: {e}", exc_info=True)
            try:
                temp_webhook_mgr = WebhookManager()
                temp_webhook_mgr.send(f"CRITICAL ALERT: Failed to initialize DatabaseManager: {e}. HoYo Helper cannot run.")
            except Exception as wh_e_crit:
                logger.error(f"Also failed to send critical DatabaseManager init error webhook: {wh_e_crit}")
            raise SystemExit(f"DatabaseManager initialization failed: {e}") from e

        self.webhook_mgr = WebhookManager()
        self.login_mgr = LoginManager(self.webhook_mgr)

        if self.config_manager.get_app_first():
            logger.info("First run detected for ConfigManager. Loading defaults.")
            self.config_manager.load_defaults()
            self.config_manager.set_app_first(False)
        
        self.game_links_map = GAME_LINKS_MAP
        try:
            self.default_encryption_key = self.config_manager.get_default_encryption_key()
            if not self.default_encryption_key:
                logger.error("Default encryption key is not set in config. Aborting.")
                raise ValueError("Default encryption key is missing.")
        except Exception as e:
            logger.critical(f"Failed to load essential configuration (encryption key): {e}")
            raise SystemExit(f"Essential configuration missing, cannot start: {e}") from e

        self.accounts: list[Account] = []
        logger.info("WindolessApp initialized successfully.")

    async def _get_and_update_cookie_if_needed_async(self, account: Account, account_webhook_url: Optional[str]) -> Optional[str]:
        nickname = account["nickname"]
        current_cookie_daily_login = account.get("cookie_daily_login")

        if current_cookie_daily_login:
            logger.info(f"Account {nickname}: Using existing daily login cookie.")
            return current_cookie_daily_login

        logger.warning(f"Account {nickname}: No daily login cookie found. Attempting to generate.")
        try:
            self.webhook_mgr.send(f"INFO: Account {nickname} - No daily login cookie. Attempting to generate now.", url=account_webhook_url)
        except WebhookError as e:
            logger.warning(f"Could not send cookie generation notice webhook for {nickname}: {e}")

        
        encrypted_pass = account.get("encrypted_password")
        username = account.get("username")

        if not encrypted_pass or not username:
            err_msg = f"Missing username or encrypted password for account {nickname}. Cannot generate cookie."
            logger.error(err_msg)
            try:
                self.webhook_mgr.send(f"ERROR: Account {nickname} - {err_msg}", url=account_webhook_url)
            except WebhookError as e: logger.warning(f"Webhook failed for: {err_msg} - {e}")
            return None

        try:
            decrypted_password = decrypt(self.default_encryption_key, encrypted_pass)
            if not decrypted_password:
                raise ValueError("Decryption resulted in empty password.")
        except Exception as e:
            err_msg = f"Failed to decrypt password for account {nickname}: {e}"
            logger.error(err_msg, exc_info=True)
            try:
                self.webhook_mgr.send(f"ERROR: Account {nickname} - {err_msg}", url=account_webhook_url)
            except WebhookError as wh_e: logger.warning(f"Webhook failed for: {err_msg} - {wh_e}")
            return None

        try:
            raw_cookie_list = await get_daily_login_cookie_async(username, decrypted_password)
            if not raw_cookie_list:
                raise ValueError("get_daily_login_cookie_async returned no cookie or False.")
        except Exception as e:
            err_msg = f"Failed to get raw cookie for account {nickname} via login: {e}"
            logger.error(err_msg, exc_info=True)
            try:
                self.webhook_mgr.send(f"ERROR: Account {nickname} - {err_msg}", url=account_webhook_url)
            except WebhookError as wh_e: logger.warning(f"Webhook failed for: {err_msg} - {wh_e}")
            return None
        
        try:
            formatted_cookies = format_cookies(raw_cookie_list)
            if not formatted_cookies:
                raise ValueError("format_cookies returned no formatted cookie.")
        except Exception as e:
            err_msg = f"Failed to format cookie for account {nickname}: {e}"
            logger.error(err_msg, exc_info=True)
            try:
                self.webhook_mgr.send(f"ERROR: Account {nickname} - {err_msg}", url=account_webhook_url)
            except WebhookError as wh_e: logger.warning(f"Webhook failed for: {err_msg} - {wh_e}")
            return None
        
        logger.info(f"Successfully generated and formatted cookie for account {nickname}.")
        
        account_to_update: Account = {
            "id": account["id"],
            "nickname": nickname,
            "username": username,
            "encrypted_password": encrypted_pass,
            "games": account.get("games", []),
            "cookie_daily_login": formatted_cookies,
            "cookie_codes": account["cookie_codes"],
            "passing": account.get("passing", False),
            "webhook": account_webhook_url
        }
        
        if self.database_manager.update_account(account_to_update):
            logger.info(f"Successfully updated cookie for account {nickname} in the database.")
        else:
            err_msg = f"Failed to save newly generated cookie for {nickname} to database. Using in-memory cookie for this session."
            logger.error(err_msg)
            try:
                self.webhook_mgr.send(f"ERROR: Account {nickname} - {err_msg}", url=account_webhook_url)
            except WebhookError as wh_e: logger.warning(f"Webhook failed for: {err_msg} - {wh_e}")
            
        return formatted_cookies


    async def run_account_async(self, account: Account):
        nickname = account.get("nickname", "UnknownAccount")
        account_id = account.get("id", "N/A")
        logger.info(f"--- Running for account: {nickname} (ID: {account_id}) ---")

        account_webhook_url = account.get("webhook")
        if not account_webhook_url:
            logger.warning(f"Account {nickname}: No webhook URL configured. Notifications for this account will use default or be skipped.")
        else:
            logger.info(f"Account {nickname}: Using webhook URL: {account_webhook_url[:25]}...")

        games_to_process = account.get("games")
        if not games_to_process:
            logger.warning(f"Account {nickname}: No games linked. Skipping account processing.")
            try:
                self.webhook_mgr.send(f"WARNING: Account {nickname} - No games linked. Skipping.", url=account_webhook_url)
            except WebhookError as e: logger.warning(f"Webhook failed for no games linked msg: {e}")
            return

        daily_cookie = await self._get_and_update_cookie_if_needed_async(account, account_webhook_url)
        if not daily_cookie:
            logger.error(f"Account {nickname}: No daily login cookie available. Skipping game processing for this account.")
            return

        logger.info(f"Account {nickname}: Processing {len(games_to_process)} game(s).")

        for game_code in games_to_process:
            game_code = game_code.strip().lower()
            if not game_code: continue

            logger.info(f"Account {nickname}: Processing game code '{game_code}'...")
            if game_code in self.game_links_map:
                game_specific_links = self.game_links_map[game_code]
                game_display_name = game_specific_links.get('name', game_code.upper())
                game_short_name_for_lm = game_specific_links.get('short_name', game_code)

                logger.info(f"Account {nickname}: Attempting daily check-in for {game_display_name} (using short_name: {game_short_name_for_lm}).")
                
                try:
                    success = self.login_mgr.process_account(
                        cookie=daily_cookie,
                        account_name=f"{nickname}",
                        game_links=game_specific_links,
                        game_short_name=game_short_name_for_lm, 
                        account_webhook_url=account_webhook_url
                    )
                    
                    if success:
                        logger.info(f"Account {nickname}: Successfully processed {game_display_name}.")
                    else:
                        logger.warning(f"Account {nickname}: Failed to process {game_display_name}. See LoginManager logs/webhooks for details.")
                except HoyoHelperError as hhe:
                    logger.error(f"Account {nickname}: A controllable error occurred processing {game_display_name}: {hhe}", exc_info=True)
                    try:
                        self.webhook_mgr.send(f"ERROR: Account {nickname} ({game_display_name}) - Processing error: {hhe.message}", url=account_webhook_url)
                    except WebhookError as e: logger.warning(f"Webhook failed for HoyoHelperError msg: {e}")
                except Exception as e:
                    logger.error(f"Account {nickname}: An UNEXPECTED error occurred while calling process_account for {game_display_name}: {e}", exc_info=True)
                    try:
                        self.webhook_mgr.send(f"CRITICAL: Account {nickname} ({game_display_name}) - Unexpected error during processing: {str(e)[:100]}", url=account_webhook_url)
                    except WebhookError as wh_e: logger.warning(f"Webhook failed for critical error msg: {wh_e}")
                
                await asyncio.sleep(1)

            else:
                logger.warning(f"Account {nickname}: Game code '{game_code}' not found in GAME_LINKS_MAP. Skipping this game.")
                try:
                    self.webhook_mgr.send(f"WARNING: Account {nickname} - Game code '{game_code}' is configured but not recognized. Skipping.", url=account_webhook_url)
                except WebhookError as e: logger.warning(f"Webhook failed for game code not found msg: {e}")
        
        logger.info(f"--- Finished processing games for account: {nickname} ---")


    async def main_async(self):
        logger.info("Starting Windoless App daily processing...")
        

        try:
            self.accounts = self.database_manager.load_accounts()
        except Exception as e:
            logger.critical(f"Failed to load accounts from database: {e}", exc_info=True)
            try:
                self.webhook_mgr.send("CRITICAL ALERT: Failed to load accounts from database. HoYo Helper cannot process accounts.")
            except WebhookError as wh_e: logger.warning(f"Webhook failed for critical db load error: {wh_e}")
            return

        if not self.accounts:
            logger.info("No accounts found in the database to process.")
            try:
                self.webhook_mgr.send("INFO: No accounts configured in HoYo Helper for processing.")
            except WebhookError as e: logger.warning(f"Webhook failed for no accounts msg: {e}")
            return
        
        logger.info(f"Loaded {len(self.accounts)} accounts for processing.")
        
        for account_data in self.accounts:
            try:
                await self.run_account_async(account_data)
            except Exception as e:
                account_nickname = account_data.get("nickname", "UnknownAccount")
                logger.critical(f"A critical unhandled error occurred while running account {account_nickname}: {e}", exc_info=True)
                account_specific_wh = account_data.get("webhook")
                msg = f"CRITICAL UNHANDLED ERROR processing account {account_nickname}: {str(e)[:100]}. See server logs."
                try:
                    self.webhook_mgr.send(msg, url=account_specific_wh)
                    if not account_specific_wh and self.webhook_mgr.default_url:
                         self.webhook_mgr.send(msg)
                except WebhookError as wh_e_critical:
                    logger.error(f"Failed to send critical error webhook for {account_nickname}: {wh_e_critical}")
            
            logger.info("Waiting before processing next account...")
            await asyncio.sleep(5)
        
        logger.info("Windoless App finished processing all accounts.")
        try:
            self.webhook_mgr.send("INFO: HoYo Helper has completed its daily processing cycle for all accounts.")
        except WebhookError as e: logger.warning(f"Webhook failed for completion msg: {e}")


if __name__ == "__main__":
    try:
        app = WindolessApp()
        asyncio.run(app.main_async())
    except SystemExit as se:
        logger.critical(f"Application exiting due to SystemExit: {se}")
    except Exception as e:
        logger.critical(f"A critical error occurred at the application level: {e}", exc_info=True)
        try:
            emergency_webhook_mgr = WebhookManager() 
            if emergency_webhook_mgr.default_url:
                emergency_webhook_mgr.send(f"CRITICAL APP STARTUP FAILURE: {type(e).__name__} - {str(e)[:150]}. HoYo Helper did not start.")
        except Exception as final_wh_e:
            logger.error(f"Additionally, failed to send emergency startup failure webhook: {final_wh_e}")