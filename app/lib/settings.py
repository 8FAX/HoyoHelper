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
#version 0.1.2
# -------------------------------------------------------------------------------------

FILE_VERSION = "0.1.0"

import json
import secrets
import os
import sys
import base64
from typing import Tuple

class ConfigManager:
    def __init__(self, config_file='settings.json', runtime='os'):
        
        if runtime == 'os':
            if os.name == 'nt':
                self.config_file = os.path.join(os.getenv('APPDATA'), 'HoyoHelper', 'data', 'settings', config_file)
            else:
                self.config_file = os.path.join(os.getenv('HOME'), '.config', 'HoyoHelper', 'data', 'settings', config_file)
            self.config_data = self.load_config()
            print(f"Configuration loaded from {self.config_file}.")

            #dev only
            if os.name == 'nt':
                os.system(f"start notepad {self.config_file}")
            elif sys.platform == 'darwin': 
                os.system(f"open {self.config_file}")
            else:
                os.system(f"xdg-open {self.config_file}")
        
        elif runtime == 'docker':
            self.config_file = os.path.join('/app', 'data', 'settings', config_file)
            self.config_data = self.load_config()
            print(f"Configuration loaded from {self.config_file}.")

    def load_config(self):
        try:
            with open(self.config_file, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
                self.load_defaults()
                self.set_default_encryption_key(self.generate_encryption_key())
                return self.load_config()

    def save_config(self):
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
    
        with os.fdopen(os.open(self.config_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as json_file:
            json.dump(self.config_data, json_file, indent=4)
        print(f"Configuration saved to {self.config_file}.")


    # Getters
    def get_version(self):
        return self.config_data.get("Version", "")

    def get_database_type(self):
        return self.config_data["Database"].get("type", "")

    def get_database_path(self):
        return self.config_data["Database"].get("Path", "")

    def get_database_encrypt(self):
        return self.config_data["Database"].get("encrypt", False)

    def get_app_style(self):
        return self.config_data["App"].get("Style", "")

    def get_app_rest(self):
        return self.config_data["App"].get("rest", "")

    def get_app_first(self):
        return self.config_data["App"].get("first", "")
    
    def get_default_encryption_key(self):
        return self.config_data["Database"].get("default_encryption_key", "")
    
    def get_use_default_encryption_key(self):
        return self.config_data["Database"].get("use_default_encryption_key", True)
    
    def get_valadation_truth(self):
        return self.config_data["App"].get("valadation_truth", "")
    
    def get_valadation(self) -> Tuple[bytes, bytes]:
        valadation_base64 = self.config_data["App"].get("valadation", "")
        salt_base64 = self.config_data["App"].get("salt", "")

        if valadation_base64 and salt_base64:
            return base64.b64decode(valadation_base64), base64.b64decode(salt_base64)
        return b"", b""
    
    def get_salt(self) -> bytes:
        salt_base64 = self.config_data["App"].get("salt", "")
        if salt_base64:
            return base64.b64decode(salt_base64)
        return b""

    # Setters
    def set_version(self, version):
        self.config_data["Version"] = version
        self.save_config()

    def set_database_type(self, db_type):
        self.config_data["Database"]["type"] = db_type
        self.save_config()

    def set_database_path(self, db_path):
        self.config_data["Database"]["Path"] = db_path
        self.save_config()

    def set_database_encrypt(self, encrypt):
        self.config_data["Database"]["encrypt"] = encrypt
        self.save_config()

    def set_app_style(self, style):
        self.config_data["App"]["Style"] = style
        self.save_config()

    def set_app_rest(self, rest):
        self.config_data["App"]["rest"] = rest
        self.save_config()

    def set_app_first(self, first):
        self.config_data["App"]["first"] = first
        self.save_config()

    def set_default_encryption_key(self, key):
        self.config_data["Database"]["default_encryption_key"] = key
        self.save_config()

    def set_use_default_encryption_key(self, use):
        self.config_data["Database"]["use_default_encryption_key"] = use
        self.save_config()

    def set_valadation_truth(self, truth):
        self.config_data["App"]["valadation_truth"] = truth
        self.save_config()

    def set_valadation(self, valadation: bytes, salt: bytes):

        valadation_base64 = base64.b64encode(valadation).decode('utf-8')
        salt_base64 = base64.b64encode(salt).decode('utf-8')
        
        self.config_data["App"]["valadation"] = valadation_base64
        self.config_data["App"]["salt"] = salt_base64 # we may not need the set_salt method anymore... or i should break this method up...
        self.save_config()
    
    def set_salt(self, salt: bytes):
        salt_base64 = base64.b64encode(salt).decode('utf-8')
        self.config_data["App"]["salt"] = salt_base64
        self.save_config()

    # other methods

    def load_defaults(self):
        self.config_data = {
            "Version": "1.0",
            "Database": {
                "type": "sqlite",
                "Path": "/data/database/",
                "encrypt": False,
                "default_encryption_key": "_KEY_DID_NOT_SET_",
                "use_default_encryption_key": True
                
            },
            "App": {
                "Style": "dark",
                "rest": "10",
                "first": True,
                "valadation_truth": "ciphercheck",
                "valadation": "ciphercheck",
                "salt": "ciphercheck"

            }
        }
        self.save_config()
        self.generate_encryption_key()

    def reset_defaults(self):
        os.remove(self.config_file)
        self.load_defaults()

    def generate_encryption_key(self):
        key = secrets.token_hex(32)  

        self.set_default_encryption_key(key)

        return key
    
    def check_database_path(self) -> bool:
        if self.get_database_path() == "":
            return False
        if not os.path.exists(self.get_database_path()+"accounts.db") and not os.path.exists(self.get_database_path()+"info.db"):
            return False
        return True

    def check_encryption_default_key(self) -> bool:
        if self.get_use_default_encryption_key():
            return False
        if self.get_default_encryption_key() == "_KEY_DID_NOT_SET_":
            return False
        return True
    
    def check_valadation(self, key: str) -> bool:
        from lib.encrypt import decrypt

        encrypted_validation, salt = self.get_valadation()
        
        if not encrypted_validation or not salt:
            print("Validation token or salt is empty.")
            return False

        try:
            decrypted_validation = decrypt(key, encrypted_validation)
            print(f"Decrypted validation: {decrypted_validation}")
            
            return decrypted_validation == self.get_valadation_truth()
        except UnicodeDecodeError:
            print("Decryption failed due to Unicode decoding error.")
            return False
        except ValueError as e:
            print(f"Decryption failed: {e}")
            return False

        

