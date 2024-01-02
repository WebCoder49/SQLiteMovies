"""User-access interface components"""

def getMovieSearchStatement(query:str):
    sections = query.split("\"")
    tokens = []
    exactPhrase = False
    for section in sections:
        if exactPhrase:
            # Section enclosed in double quotes
            tokens.append(section)
        else:
            # Each word
            tokens += section.split()
        exactPhrase = not exactPhrase

    print(tokens)

print(getMovieSearchStatement('"Harry Potter" Goblet of Fire'))
# Todo make give query ...WHERE title LIKE "%Harry Potter%" AND title LIKE "%Goblet%" AND title LIKE "%of%"...