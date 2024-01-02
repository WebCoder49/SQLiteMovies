import sqlite3

conn = sqlite3.connect("movies.db")
cur = conn.cursor()


def exec(statement: str, parameters: tuple = tuple()):
    """Execute an SQL statement"""
    cur.execute(statement, parameters)


def display():
    if cur.description == None:
        print("\x1b[90mNo data fetched.\x1b[0m")
        return None

    """Print the result of the previous SQL statement to the console as a pretty table; return the data in the table"""
    rows = cur.fetchall()

    # Get names of columns and initially make wide enough to hold these names
    column_names = list(item[0] for item in cur.description)
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
    print("\x1b[47m\x1b[30m", end="")  # Green background, black text
    for x in range(len(column_names)):
        print(column_names[x] + " " * (
                column_widths[x] + 3 - len(column_names[x])
        ), end="")
    print("\x1b[0m")  # Newline, reset formatting
    for y in range(len(rows)):
        for x in range(len(column_names)):
            escape_color = "\x1b[40m" if (y % 2) == 1 else "\x1b[0m"  # So chessboard pattern

            if type(rows[y][x]) == bytes:
                str_value = str(rows[y][x].hex())
            else:
                str_value = str(rows[y][x])
            print(escape_color + str_value + " " * (
                    column_widths[x] + 3 - len(str_value)
            ), end="")
        print("\x1b[0m")  # Newline, reset formatting

    return rows


def done():
    """Commit the result of the previous SQL statements to the database"""
    conn.commit()
    conn.close()