FILE_VERSION = "0.1.0"

import argparse
import os
import subprocess
import sys
import logging
import asyncio
from typing import List, Optional

project_root = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(project_root, "app")
if app_path not in sys.path:
    sys.path.insert(0, app_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from lib.database import DatabaseManager, Account
    from lib.cookie import get_cookie as get_daily_login_cookie_async, format_cookies as format_daily_cookies
    from lib.cookie_for_codes import get_cookie as get_codes_cookie_async, format_cookies as format_codes_cookies
    from lib.encrypt import encrypt
    from lib.settings import ConfigManager
    from playwright.async_api import async_playwright
except ImportError as e:
    print(f"Error importing necessary modules: {e}")
    print("Please ensure this script is in the project root or paths are correctly set.")
    print("Required structure: project_root/app/lib/...")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - [%(name)s] %(message)s")
logger = logging.getLogger("TempDBLoader")

def open_file_explorer(path: str):
    """Opens the file explorer to the specified path."""
    try:
        dir_path = os.path.dirname(path) if os.path.isfile(path) else path
        if not os.path.exists(dir_path):
            logger.warning(f"Directory to open does not exist: {dir_path}")
            db_parent_dir = os.path.dirname(os.path.dirname(path))
            if os.path.exists(db_parent_dir):
                dir_path = db_parent_dir
            else:
                dir_path = path


        if os.name == 'nt':
            subprocess.run(['explorer', os.path.normpath(dir_path)], check=True)
            logger.info(f"Opened Windows Explorer at: {dir_path}")
        elif sys.platform == 'darwin':
            subprocess.run(['open', dir_path], check=True)
            logger.info(f"Opened Finder at: {dir_path}")
        else:
            subprocess.run(['xdg-open', dir_path], check=True)
            logger.info(f"Opened file manager at: {dir_path}")
    except Exception as e:
        logger.error(f"Could not open file explorer for path '{path}': {e}")
        logger.info(f"The database should be located at/near: {path}")
        config_manager_for_path = ConfigManager(runtime='os')
        config_dir = ""
        if config_manager_for_path.config_file:
            config_dir = os.path.dirname(os.path.dirname(config_manager_for_path.config_file))
        if config_dir:
             logger.info(f"Try looking in the HoyoHelper config root: {config_dir}")


async def main_async():
    parser = argparse.ArgumentParser(description="Temporary Database Loader for HoYo Helper Accounts.")
    parser.add_argument("--email", required=True, help="Account email/username for login.")
    parser.add_argument("--password", required=True, help="Account password for login.")
    parser.add_argument("--games", required=True, help="Comma-separated list of game codes (e.g., gi,hsr,zzz).")
    parser.add_argument("--nickname", help="Nickname for the account (defaults to email prefix).")
    parser.add_argument("--webhook", help="Optional Discord webhook URL for this account.", default=None)
    parser.add_argument("--runtime", help="Runtime environment ('os' or 'docker')", default='os')

    args = parser.parse_args()

    email = args.email
    password = args.password
    games_str = args.games
    nickname = args.nickname if args.nickname else email.split('@')[0]
    webhook_url = args.webhook
    runtime_env = args.runtime.lower()

    if runtime_env not in ['os', 'docker']:
        logger.error("Invalid runtime. Must be 'os' or 'docker'.")
        sys.exit(1)

    logger.info(f"Attempting to add account for: {email} with nickname: {nickname}")

    try:
        config_manager = ConfigManager(runtime=runtime_env)
        if config_manager.get_app_first():
            logger.info("ConfigManager: First run, loading defaults.")
            config_manager.load_defaults()
            config_manager.set_app_first(False)
        
        encryption_key = config_manager.get_default_encryption_key()
        if not encryption_key:
            logger.error("Could not retrieve encryption key from ConfigManager. Ensure configuration is set up.")
            sys.exit(1)
        logger.info("Successfully retrieved encryption key.")
    except Exception as e:
        logger.error(f"Error initializing ConfigManager or getting encryption key: {e}", exc_info=True)
        sys.exit(1)
    async with async_playwright() as playwright_instance:
        logger.info("Generating daily login cookie...")
        try:
            raw_daily_cookie_list = await get_daily_login_cookie_async(password, email)
            if not raw_daily_cookie_list:
                logger.error("Failed to generate daily login cookie. Check credentials and cookie.py.")
                sys.exit(1)
            cookie_daily_login = format_daily_cookies(raw_daily_cookie_list)
            if not cookie_daily_login:
                logger.error("Failed to format daily login cookie.")
                sys.exit(1)
            logger.info("Daily login cookie generated and formatted successfully.")
        except Exception as e:
            logger.error(f"Error during daily login cookie generation: {e}", exc_info=True)
            sys.exit(1)

        logger.info("Generating codes cookie...")
        try:
            raw_codes_cookie_list = await get_codes_cookie_async(password, email, playwright_instance)
            if not raw_codes_cookie_list:
                logger.error("Failed to generate codes cookie. Check credentials and cookie_for_codes.py.")
                sys.exit(1)
            cookie_codes = format_codes_cookies(raw_codes_cookie_list)
            if not cookie_codes:
                logger.error("Failed to format codes cookie.")
                sys.exit(1)
            logger.info("Codes cookie generated and formatted successfully.")
        except Exception as e:
            logger.error(f"Error during codes cookie generation: {e}", exc_info=True)
            sys.exit(1)

    logger.info("Encrypting password...")
    try:
        encrypted_password = encrypt(encryption_key, password)
        if not encrypted_password:
            logger.error("Failed to encrypt password.")
            sys.exit(1)
        logger.info("Password encrypted successfully.")
    except Exception as e:
        logger.error(f"Error during password encryption: {e}", exc_info=True)
        sys.exit(1)

    game_list: List[str] = [game.strip().lower() for game in games_str.split(',') if game.strip()]
    if not game_list:
        logger.error("No valid games provided.")
        sys.exit(1)

    account_data: Account = {
        "nickname": nickname,
        "username": email,
        "encrypted_password": encrypted_password,
        "games": game_list,
        "cookie_daily_login": cookie_daily_login,
        "cookie_codes": cookie_codes,
        "passing": False,
        "webhook": webhook_url
    }

    logger.info("Saving account to database...")
    db_manager: Optional[DatabaseManager] = None
    db_file_path_for_explorer = ""
    try:
        db_manager = DatabaseManager(runtime=runtime_env)
        db_file_path_for_explorer = db_manager.database_file
        
        existing_accounts = db_manager.load_accounts()
        for acc in existing_accounts:
            if acc['username'] == email:
                logger.warning(f"Account with email/username '{email}' already exists (ID: {acc.get('id', 'N/A')}). Skipping save.")
                logger.info("If you want to update, use a different tool or manage the DB directly.")
                config_root_path = os.path.dirname(os.path.dirname(os.path.dirname(db_file_path_for_explorer)))
                open_file_explorer(config_root_path)
                sys.exit(0)

        saved_id = db_manager.save_account(account_data)
        if saved_id:
            logger.info(f"Account for '{nickname}' (Email: {email}) saved successfully with ID: {saved_id}!")
        else:
            logger.error("Failed to save account to database. save_account returned None.")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error during database operation: {e}", exc_info=True)
        if db_file_path_for_explorer:
            config_root_path = os.path.dirname(os.path.dirname(os.path.dirname(db_file_path_for_explorer)))
            open_file_explorer(config_root_path)
        sys.exit(1)

    if db_file_path_for_explorer:
        config_root_path = os.path.dirname(os.path.dirname(os.path.dirname(db_file_path_for_explorer)))
        open_file_explorer(config_root_path)
    else:
        logger.warning("Database manager path was not determined, attempting to guess config path to open.")
        temp_config_for_path = ConfigManager(runtime='os')
        if temp_config_for_path.config_file:
            hoyo_helper_root = os.path.dirname(os.path.dirname(temp_config_for_path.config_file))
            open_file_explorer(hoyo_helper_root)
        else:
            logger.warning("Could not determine config path to open file explorer.")


if __name__ == "__main__":
    asyncio.run(main_async())