import sqlite3

import db

import re

"""Populate the tables in the database with data - interactive admin 'shell'"""

def insertRecord(tableName:str, level:int):
    """Insert a record into the table tableName through a
    user interface, ensuring referential integrity. level is the
    level of indentation. Return the primary key."""
    # Removes SQL injection characters from tableName as normal
    # question-mark based insertion doesn't work for table names.
    tableName = re.sub("(?![a-zA-Z]).", "", tableName)
    db.exec(
        f"SELECT * FROM {tableName}"
    );

    records = db.display()
    if records is not None and len(records) > 0:
        lastRecord = records[-1]
    else:
        lastRecord = None

    availableFieldNames = db.cur.description
    fieldNames = []
    fieldValues = []
    for i in range(len(availableFieldNames)): # List of 7-tuples
        field = availableFieldNames[i][0]
        if lastRecord is None:
            lastValue = ""
        else:
            lastValue = lastRecord[i]

        if(field.lower() == tableName.lower() + "id"):
            # Primary key
            continue
        elif(field.lower()[-2:] == "id"):
            # Foreign key
            foreignTableName = field[0].upper() + field[1:-2] # So PascalCase
            choice = input(
                "\t"*level+"How do you want to get foreign key for " + foreignTableName + f"? ([D]efault{'' if lastValue == '' else (', [L]ast = ' + str(lastValue))}, [S]how {foreignTableName}s): ")
            if choice.upper() == "L": value = lastValue
            elif choice.upper() == "D": continue
            else:
                db.exec(
                    f"SELECT * FROM {foreignTableName}"
                );
                records = db.display()
                try:
                    value = int(input("\t"*level+"Choose primary key, or enter nothing to add a new record: "))
                except ValueError:
                    insertRecord(foreignTableName, level+1)
                    value = len(records)
        else:
            value = input("\t"*level+"Input value for " + field + f" (blank means default{'' if lastValue == '' else (', # means '+str(lastValue))}): ")

            if value == "#": value = lastValue
            if value == "": continue
        fieldNames.append(field)
        fieldValues.append(value)

    if len(fieldValues) > 0:
        db.exec(
            f"INSERT INTO {tableName} ({', '.join(fieldNames)}) VALUES (?{', ?' * (len(fieldValues) - 1)})",
            fieldValues
        );

    db.conn.commit()

def adminShell():
    print()
    print("\x1b[93m\x1b[7m Admin Shell \x1b[0m")

    while True:
        tableName = input("[ User | Review | Movie | ActorRole | Actor ]\nEnter a table name from above to populate, or type 'SQL' to run a custom SQL command, or type 'Logout' to return to normal-user view: ")
        print()

        tableName = tableName.strip()
        if tableName.upper() == "LOGOUT":
          return
        elif tableName.upper() == "SQL":
            try:
                db.exec(input("SQL Statement: "))
                db.display()
                db.conn.commit()
            except (sqlite3.OperationalError, sqlite3.Warning) as err:
                print(f"You caused an error: {err}")
        else:
            try:
                insertRecord(tableName, level=1)
            except sqlite3.OperationalError as err:
                print(f"\x1b[31m{err}\x1b[0m")

        print("\n\x1b[0m", end="")
        print()

if __name__ == "__main__":
    adminShell()