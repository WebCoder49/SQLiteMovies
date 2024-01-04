"""User-login interface components"""
from getpass import getpass
import re
from hashlib import sha256
from random import randbytes

import db

def deleteAccount(userID:int):
    db.exec("DELETE FROM User WHERE userID = ?", (userID,))
    db.exec("DELETE FROM Review WHERE userID = ?", (userID,))
    db.conn.commit()

def loginOrRegister():
    """Show the login/register interface and return the user ID of the logged-in user,
    or None if no user is logged in."""
    print("\x1b[92m\x1b[7m Login or Register \x1b[0m")

    emailAddress = ""
    while not isValidEmail(emailAddress):
        emailAddress = input("Email Address: ")

    db.exec("SELECT passwordHashAndSalt FROM User WHERE emailAddress = ?;", [emailAddress])
    passwordHashAndSalt = db.cur.fetchone()
    if passwordHashAndSalt is None:
        print("Registering a new account.")
        password = input("Password: ")
        confirmedPassword = input("Retype Password: ")
        while password != confirmedPassword:
            print("Those passwords didn't match; please try again.")
            password = input("Password: ")
            confirmedPassword = input("Retype Password: ")

        firstName = input("First Name (50 characters max): ").strip()
        while firstName == "" or len(firstName) > 50:
            firstName = input("First Name: ").strip()

        lastName = input("Last Name (50 characters max): ").strip()
        while lastName == "" or len(lastName) > 50:
            lastName = input("Last Name: ").strip()

        dob = input("Date of Birth [yyyy-mm-dd]: ").strip()
        while not isValidDOB(dob):
            dob = input("Date of Birth [yyyy-mm-dd]: ").strip()

        passwordSalt = randbytes(4)
        passwordHashAndSalt = sha256(password.encode('utf-8') + passwordSalt).digest() + passwordSalt


        db.exec(
            "INSERT INTO User (emailAddress, passwordHashAndSalt, firstName, lastName, dateOfBirth) VALUES (?, ?, ?, ?, ?);",
            [emailAddress, passwordHashAndSalt, firstName, lastName, dob]
            )
    else:
        print("Logging in.")
        passwordHashAndSalt = passwordHashAndSalt[0] # Fetch from tuple

        password = input("Password: ")
        passwordHashCorrect = passwordHashAndSalt[:-4]
        passwordSalt = passwordHashAndSalt[-4:]
        passwordHashGiven = sha256(password.encode('utf-8') + passwordSalt).digest()
        if passwordHashCorrect != passwordHashGiven:
            return None

    db.exec("SELECT userID FROM User WHERE emailAddress = ?;", [emailAddress])
    db.conn.commit()

    print("\n\x1b[0m", end="")
    return db.cur.fetchone()[0]

"""EMAIL REGEX: https://www.mailboxvalidator.com/resources/articles/acceptable-email-address-syntax-rfc/"""
# \w is word character for internationalisation

# Matches a character that can always be in the local part.
REGEX_EMAIL_LOCALANYWHERECHARACTERS = r"[\w!#$%&'*+\-/=?^`{|}~]"
# Matches 1 to 64 characters, each one being in the LOCALANYWHERECHARACTERS set or a dot,
# not preceded by a start-of-string, not followed by an end-of-localpart(@), and not followed by a dot.
REGEX_EMAIL_LOCALPART = r"("+REGEX_EMAIL_LOCALANYWHERECHARACTERS+r"|(?<!^)\.(?!\.)(?!@)){1,64}"
REGEX_EMAIL_DOMAINANYWHERECHARACTERS = r"(?!_)\w"
# Characters which must be seen at least once in the top-level domain
REGEX_EMAIL_TLDATLEASTONECHARACTERS = r"(?!_)(?![0-9])\w"
# Like LOCALPART but must consist of no hyphens touching the start(.)/end(end-of-string or .) of the domain part.
REGEX_EMAIL_DNSLABEL = r"("+REGEX_EMAIL_DOMAINANYWHERECHARACTERS+r"|(?<!.)\-(?!\.)(?!$)){1,63}"
REGEX_EMAIL_TLD = REGEX_EMAIL_DOMAINANYWHERECHARACTERS+r"*"+REGEX_EMAIL_TLDATLEASTONECHARACTERS+REGEX_EMAIL_DOMAINANYWHERECHARACTERS+r"*"
REGEX_EMAIL_DOMAINPART = r"("+REGEX_EMAIL_DNSLABEL+r"\.)+"+REGEX_EMAIL_TLD
REGEX_EMAIL = re.compile(REGEX_EMAIL_LOCALPART+r"@"+REGEX_EMAIL_DOMAINPART)
def isValidEmail(email: str):
    """Return True if the email address is a valid email address, and False otherwise"""
    return REGEX_EMAIL.fullmatch(email) != None # Whole string matches - https://docs.python.org/3/library/re.html#re.Pattern.fullmatch

def isValidDOB(dob:str):
    """Return True if the email address is a valid yyyy-mm-dd date of birth, and False otherwise"""
    numbers = dob.split("-")

    if len(numbers) != 3: return False

    for number in numbers:
        try:
            int(number)
        except ValueError:
            return False

    if int(numbers[1]) < 1 or int(numbers[1]) > 12 or int(numbers[2]) < 1 or int(numbers[2]) > 31:
        return False

    return True