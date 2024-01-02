"""User-login interface components"""
from getpass import getpass

import db

def loginOrRegister():
    print("\x1b[7m Login or Register \x1b[0m")
    emailAddress = input("Email Address: ")
    password = getpass("Password: ")
