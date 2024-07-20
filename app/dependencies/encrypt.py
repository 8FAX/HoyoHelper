import os
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

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