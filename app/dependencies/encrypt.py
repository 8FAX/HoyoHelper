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
#version 0.1.1
# -------------------------------------------------------------------------------------

import os
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from database import load_accounts, update_account

def encrypt(key: str, plaintext: str) -> bytes:
    """
    The function encrypts a plaintext using AES encryption in CBC mode with a given key and returns the
    initialization vector concatenated with the ciphertext.
    
    Author - Liam Scott
    Last update - 07/19/2024
    @param key (str) - The `key` parameter is the encryption key used to encrypt the plaintext. In the
    provided code snippet, the key is expected to be a string that will be encoded to UTF-8 format and
    then padded or truncated to a length of 32 bytes (256 bits) to match the AES encryption key
    @param plaintext (str) - The `encrypt` function you provided takes a key and plaintext as input,
    encrypts the plaintext using AES encryption in CBC mode, and returns the initialization vector (IV)
    concatenated with the ciphertext.
    @returns The `encrypt` function returns the initialization vector (IV) concatenated with the
    ciphertext after encrypting the plaintext using the AES encryption algorithm in CBC mode with the
    provided key.
    
    """
    backend = default_backend()
    key = key.encode('utf-8')
    key = key.ljust(32)[:32]  
    
    iv = os.urandom(16)  
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return iv + ciphertext  
        
def decrypt(key: str, ciphertext: bytes) -> str:
    """
    The function decrypts a ciphertext using AES encryption with a given key and returns the decrypted
    plaintext.
    
    Author - Liam Scott
    Last update - 07/19/2024
    @param key (str) - The `key` parameter is the encryption key used to decrypt the ciphertext. It
    should be a string that represents the key in UTF-8 encoding.
    @param ciphertext (bytes) - It seems like you forgot to provide the value for the `ciphertext`
    parameter. Please provide the ciphertext value so that I can assist you with decrypting it using the
    given `decrypt` function.
    @returns The function decrypts the ciphertext using the provided key and returns the decrypted
    plaintext as a string.
    
    """
    backend = default_backend()
    key = key.encode('utf-8')
    key = key.ljust(32)[:32]  
    
    iv = ciphertext[:16] 
    actual_ciphertext = ciphertext[16:]
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    
    padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
    
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    return plaintext.decode('utf-8')

def database_decript(key: str, ciphertext: bytes) -> str:
    """
    The function decrypts a ciphertext using AES encryption with a given key and returns the decrypted
    plaintext.
    
    Author - Liam Scott
    Last update - 09/5/2024
    @param key (str) - The `key` parameter is the encryption key used to decrypt the ciphertext. It
    should be a string that represents the key in UTF-8 encoding.
    @param ciphertext (bytes) - It seems like you forgot to provide the value for the `ciphertext`
    parameter. Please provide the ciphertext value so that I can assist you with decrypting it using the
    given `decrypt` function.
    @returns The function decrypts the ciphertext using the provided key and returns the decrypted
    plaintext as a string.
    
    """
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

def database_encript(key: str) -> str:
    """
    The function decrypts a ciphertext using AES encryption with a given key and returns the decrypted
    plaintext.
    
    Author - Liam Scott
    Last update - 09/5/2024
    @param key (str) - The `key` parameter is the encryption key used to decrypt the ciphertext. It
    should be a string that represents the key in UTF-8 encoding.
    @param ciphertext (bytes) - It seems like you forgot to provide the value for the `ciphertext`
    parameter. Please provide the ciphertext value so that I can assist you with decrypting it using the
    given `decrypt` function.
    @returns The function decrypts the ciphertext using the provided key and returns the decrypted
    plaintext as a string.
    
    """
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
