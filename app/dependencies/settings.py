import json
import secrets
import os
import sys 

class ConfigManager:
    def __init__(self, config_file='settings.json'):
        if os.name == 'nt':
            self.config_file = os.path.join(os.getenv('APPDATA'), 'PasswordManager', 'data', 'settings', config_file)
        else:
            self.config_file = os.path.join(os.getenv('HOME'), '.config', 'PasswordManager', 'data', 'settings', config_file)
        self.config_data = self.load_config()
        print(f"Configuration loaded from {self.config_file}.")

        #dev only
        if os.name == 'nt':
            os.system(f"start notepad {self.config_file}")
        elif sys.platform == 'darwin': 
            os.system(f"open {self.config_file}")
        else:
            os.system(f"xdg-open {self.config_file}")

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
                "first": False
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
