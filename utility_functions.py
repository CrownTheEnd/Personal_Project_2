import random
import json
import pyzipper
import os
from io import BytesIO

def write_to_fighters(fighter):
    file = open('./fighter_dictionary.txt', "w")
    file.write(str(fighter))
    file.close()
    return True

def generate_token(length):
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    token = ''.join(random.choice(characters) for _ in range(length))
    return token


