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
#version 0.1.5
# -------------------------------------------------------------------------------------

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from typing import Tuple

def derive_key(password: str, salt: bytes) -> bytes:
    """
    The function `derive_key` takes a password and a salt, derives a key using PBKDF2HMAC with SHA256
    algorithm, and returns the key as bytes.
    
    Author - Liam Scott
    Last update - 10/28/2024
    
    @ param password (str)  - The `derive_key` function takes a password as a string and a salt as
    bytes. It uses the PBKDF2HMAC key derivation function with SHA256 hashing algorithm, a key length of
    32 bytes, 100,000 iterations, and the default backend.
    @ param salt (bytes)  - A salt is a random sequence of bytes that is used as an additional input to
    a key derivation function (KDF). It helps protect against dictionary attacks and rainbow table
    attacks by ensuring that even if two users have the same password, their derived keys will be
    different due to the unique salt used during the
    
    @ returns The function `derive_key` takes a password as a string and a salt as bytes, then uses
    PBKDF2HMAC with SHA256 hashing algorithm to derive a key of length 32 bytes using 100,000
    iterations. The derived key is then printed in hexadecimal format and returned as bytes.
    
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,       
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    print(f"Derived key: {key.hex()}")
    return key


def encrypt(password: str, plaintext: str) -> Tuple[bytes, bytes]:
    """
    The function encrypts plaintext using AES encryption with a given password and returns the salt, IV,
    and ciphertext.
    
    Author - Liam Scott
    Last update - 10/28/2024
    
    @ param password (str)  - The `password` parameter is a string that will be used to derive a key for
    encryption.
    @ param plaintext (str)  - The `encrypt` function you provided seems to be encrypting the plaintext
    using AES encryption in CBC mode with a randomly generated salt and IV. The key is derived from the
    password using a function `derive_key` which is not shown in the code snippet.
    
    @ returns The `encrypt` function returns a tuple containing two bytes objects: the `salt`, `iv`, and
    `ciphertext` concatenated together.
    
    """
    backend = default_backend()
    salt = os.urandom(16) 
    key = derive_key(password, salt)
    
    iv = os.urandom(16)  
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return salt + iv + ciphertext



def decrypt(password: str, encrypted_data: bytes) -> str:
    """
    The function decrypts encrypted data using a password and returns the decrypted plaintext.
    
    Author - Liam Scott
    Last update - 10/28/2024
    
    @ param password (str)  - The `decrypt` function you provided seems to be decrypting data using AES
    encryption with CBC mode. It derives a key from the password and decrypts the encrypted data using
    the key, salt, and IV.
    @ param encrypted_data (bytes)  - The `decrypt` function you provided is used to decrypt data that
    has been encrypted using AES encryption with a specific password. The function extracts the salt,
    IV, and ciphertext from the encrypted data, derives a key using the provided password and salt, and
    then decrypts the ciphertext using AES in CBC mode
    
    @ returns The `decrypt` function returns a decrypted string obtained from the encrypted data using
    the provided password. If the decryption is successful, it returns the decrypted plaintext as a
    UTF-8 decoded string. If there are any errors during decryption, it prints an error message and
    returns an empty string.
    
    """
    backend = default_backend()
    salt = encrypted_data[:16]  
    iv = encrypted_data[16:32]  
    ciphertext = encrypted_data[32:]  
    
    key = derive_key(password, salt)  
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    
    #print(f"Decrypting with salt: {salt.hex()}, iv: {iv.hex()}, and derived key: {key.hex()}")

    try:
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext.decode('utf-8')
    except UnicodeDecodeError:
        print("Decryption failed: Non-UTF-8 compatible bytes in decrypted data.")
        return plaintext
    except ValueError as e:
        print(f"Decryption failed: {e}")
        return ""

def database_decrypt(key: str, ciphertext: bytes) -> str:
    """
    The function decrypts a ciphertext using AES encryption with a given key and returns the decrypted
    plaintext.
    
    Author - Liam Scott
    Last update - 09/5/2024
    @ param key (str) - The `key` parameter is the encryption key used to decrypt the ciphertext. It
    should be a string that represents the key in UTF-8 encoding.
    @ param ciphertext (bytes) - It seems like you forgot to provide the value for the `ciphertext`
    parameter. Please provide the ciphertext value so that I can assist you with decrypting it using the
    given `decrypt` function.
    @ returns The function decrypts the ciphertext using the provided key and returns the decrypted
    plaintext as a string.
    
    """
    from .database import load_accounts, update_account
    backend = default_backend()
    key = key.encode('utf-8')
    key = key.ljust(32)[:32]
    
    accounts = load_accounts()
    for account in accounts:
        account_id = account['id']
        encrypted_password = account['encrypted_password']
        encrypted_name = account['nickname']
        encrypted_cookie = account['cookie']
        encrypted_webhook = account['webhook']

        encrypted_list = [encrypted_password, encrypted_name, encrypted_cookie, encrypted_webhook]

        for encrypted in encrypted_list:
            decripted_list = []
            if encrypted:
                iv = encrypted[:16] 
                actual_ciphertext = encrypted[16:]
                
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
                decryptor = cipher.decryptor()
                
                padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
                
                unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
                plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
                
                decripted_list.append(plaintext.decode('utf-8'))
            else:
                decripted_list.append(None)
        update_account(account_id, decripted_list[0], decripted_list[1], decripted_list[2], decripted_list[3])
    return True

def database_encrypt(key: str) -> str:
    """
    The function decrypts a ciphertext using AES encryption with a given key and returns the decrypted
    plaintext.
    
    Author - Liam Scott
    Last update - 09/5/2024
    @ param key (str) - The `key` parameter is the encryption key used to decrypt the ciphertext. It
    should be a string that represents the key in UTF-8 encoding.
    @ param ciphertext (bytes) - It seems like you forgot to provide the value for the `ciphertext`
    parameter. Please provide the ciphertext value so that I can assist you with decrypting it using the
    given `decrypt` function.
    @ returns The function decrypts the ciphertext using the provided key and returns the decrypted
    plaintext as a string.
    
    """
    from .database import load_accounts, update_account
    backend = default_backend()
    key = key.encode('utf-8')
    key = key.ljust(32)[:32]
    
    accounts = load_accounts()
    for account in accounts:
        account_id = account['id']
        encrypted_password = account['encrypted_password']
        encrypted_name = account['nickname']
        encrypted_cookie = account['cookie']
        encrypted_webhook = account['webhook']

        encrypted_list = [encrypted_password, encrypted_name, encrypted_cookie, encrypted_webhook]

        for encrypted in encrypted_list:
            encripted_list = []
            if encrypted:
                iv = os.urandom(16)  
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
                encryptor = cipher.encryptor()
                
                padder = padding.PKCS7(algorithms.AES.block_size).padder()
                padded_data = padder.update(encrypted.encode('utf-8')) + padder.finalize()
                
                ciphertext = encryptor.update(padded_data) + encryptor.finalize()
                encripted_list.append(iv + ciphertext)
            else:
                encripted_list.append(None)
        update_account(account_id, encripted_list[0], encripted_list[1], encripted_list[2], encripted_list[3])
    return True
