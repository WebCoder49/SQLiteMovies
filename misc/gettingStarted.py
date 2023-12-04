import random
import re
from datetime import date
import sqlite3
from hashlib import sha256


def print_table(table_description, rows):
    """Print the results of an SQL query as a table that looks nice."""
    # Get names of columns and initially make wide enough to hold these names
    column_names = list(item[0] for item in table_description)
    column_widths = list(len(name) for name in column_names)

    # Make columns wider for data in them
    for x in range(len(column_names)):
        for y in range(len(rows)):
            if type(rows[y][x]) == bytes:
                len_text = len(str(rows[y][x].hex()))
            else:
                len_text = len(str(rows[y][x]))
            if (len_text > column_widths[x]):
                # Make column wider
                column_widths[x] = len_text

    # Print out table
    print("\x1b[47m\x1b[30m", end="") # Green background, black text
    for x in range(len(column_names)):
        print(column_names[x] + " " * (
                column_widths[x] + 3 - len(column_names[x])
        ), end="")
    print("\x1b[0m")  # Newline, reset formatting
    for y in range(len(rows)):
        for x in range(len(column_names)):
            escape_color = "\x1b[40m" if (y%2)==1 else "\x1b[0m" # So chessboard pattern

            if type(rows[y][x]) == bytes:
                str_value = str(rows[y][x].hex())
            else:
                str_value = str(rows[y][x])
            print(escape_color + str_value + " " * (
                    column_widths[x] + 3 - len(str_value)
            ), end="")
        print("\x1b[0m")  # Newline, reset formatting

def get_new_user_id(cursor: sqlite3.Cursor, fname: str, lname: str, gender: str, joining: date, email: str, password: str):
    if not is_valid_email(email):
        raise ValueError("Email address '"+email+"' not valid")

    password_salt = random.randbytes(4)
    password_hash_and_salt = sha256(password.encode('utf-8') + password_salt).digest() + password_salt
    cursor.execute(
        """INSERT INTO users (fname,lname,gender,joining,email,password_hash_and_salt) VALUES (?, ?, ?, ?, ?, ?);""",
        (fname, lname, gender, f"{('0000'+str(joining.year))[-4:]}-{('00'+str(joining.month))[-2:]}-{('00'+str(joining.day))[-2:]}", email, password_hash_and_salt) # Padding date with 0s
    )


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

print(REGEX_EMAIL)

def is_valid_email(email: str):
    """Return True if the email address is a valid email address, and False otherwise"""
    return REGEX_EMAIL.fullmatch(email) != None # Whole string matches - https://docs.python.org/3/library/re.html#re.Pattern.fullmatch

print(is_valid_email("abc.1.23!.#$%&'*+-/=?^_`{|}~"))

def login_valid(cursor: sqlite3.Cursor, email: str, password: str):
    """Return True if the email and password match a user, and False otherwise"""

    cursor.execute(
        """SELECT password_hash_and_salt FROM users WHERE email = ?;""",
        (email,)
    )
    password_hash_and_salt = cursor.fetchone()
    if password_hash_and_salt is None:
        return False
    password_hash_and_salt = password_hash_and_salt[0] # Extract from tuple

    password_hash_correct = password_hash_and_salt[:-4]
    password_salt = password_hash_and_salt[-4:]
    password_hash_given = sha256(password.encode('utf-8') + password_salt).digest()

    if password_hash_given == password_hash_correct:
        return True
    return False



# create .db file or connect to it if it exists
connection = sqlite3.connect("database.db")

# A cursor is an object used to make the connection for executing SQL queries.
cursor = connection.cursor()

# Create the table, read the article below if you
# are unsure of what VARCHAR etc. mean
# https://www.w3schools.com/sql/sql_datatypes.asp
create_table_statement = """CREATE TABLE IF NOT EXISTS users (
  staff_number INTEGER PRIMARY KEY,
  fname VARCHAR(20),
  lname VARCHAR(30),
  gender CHAR(1),
  joining DATE,
  email VARCHAR(320),
  password_hash_and_salt BINARY(36)
);""" # password_hash_and_salt: https://en.wikipedia.org/wiki/Salt_(cryptography)

cursor.execute(create_table_statement)

# Insert a demo user into our database
get_new_user_id(cursor, "Bat", "Man", "M", date(2014, 3, 28), "theSuperhero@bat.example.com", "HelloWorld")
print(("theSuperhero@bat.example.com", "HelloWorld"), login_valid(cursor, "theSuperhero@bat.example.com", "HelloWorld"))
print(("theSuperhero@bat.example.com", "HelloDatabase"), login_valid(cursor, "theSuperhero@bat.example.com", "HelloDatabase"))
get_new_user_id(cursor, "Spider", "Man", "M", date(2015, 11, 3), "spiderman2015@example.net", "HelloWorld")
print(("spiderman2015@example.net", "HelloWorld"), login_valid(cursor, "spiderman2015@example.net", "HelloWorld"))
print(("spiderman2015@example.net", "HelloDatabase"), login_valid(cursor, "spiderman2015@example.net", "HelloDatabase"))
get_new_user_id(cursor, "Wonder", "Woman", "F", date(2023, 10, 11), "wonder.woman@example.com", "HelloDatabase")
print(("wonder.woman@example.com", "HelloWorld"), login_valid(cursor, "wonder.woman@example.com", "HelloWorld"))
print(("wonder.woman@example.com", "HelloDatabase"), login_valid(cursor, "wonder.woman@example.com", "HelloDatabase"))

# Fetch the data
cursor.execute("SELECT * FROM users")

# Store + print the fetched data
print_table(cursor.description, cursor.fetchall())

# Remember to save + close
connection.commit()
connection.close()
