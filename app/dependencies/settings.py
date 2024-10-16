import json
import secrets
import os

class ConfigManager:
    def __init__(self, config_file='settings.json'):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print(f"{self.config_file} not found. Creating a new config.")
            return {
                "Version": "",
                "Database": {
                    "type": "",
                    "Path": "",
                    "encrypt": False
                },
                "App": {
                    "Style": "",
                    "rest": "",
                    "first": ""
                }
            }

    def save_config(self):
        with open(self.config_file, 'w') as json_file:
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

    # other methods

    def load_defaults(self):
        self.config_data = {
            "Version": "1.0",
            "Database": {
                "type": "sqlite",
                "Path": "data.db",
                "encrypt": False,
                "default_encryption_key": "_KEY_DID_NOT_SET_"
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