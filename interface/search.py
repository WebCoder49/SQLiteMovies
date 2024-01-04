"""User-access interface components"""
import db

def getSearchTokens(query:str):
    """Return the tokens with wildcards (to be used with LIKE in SQL) from the search query, then the negative tokens to exclude"""
    sections = query.split("\"")
    tokens = []
    negativeTokens = []
    exactPhrase = False
    for section in sections:
        if exactPhrase:
            # Section enclosed in double quotes
            tokens.append("%" + section + "%")
        else:
            # Each word
            for word in section.split():
                if word[0] == "-":
                    negativeTokens.append("%"+word[1:]+"%") # Remove '-'
                else:
                    tokens.append("%"+word+"%")
        exactPhrase = not exactPhrase

    return tokens, negativeTokens

def searchMovieReturnID():
    print()
    print("\x1b[93m\x1b[7m Search Movies \x1b[0m")

    data = []
    while len(data) != 1:
        tokens, negativeTokens = getSearchTokens(input("Movie search query (enter to show all, keywords otherwise, double quotes around a phrase to match it exactly, prefix a word with - to remove results with it): "))

        if len(tokens) == 0 and len(negativeTokens) == 0:
            query = "SELECT movieID, title, releaseYear, genre, minimumAge FROM Movie"
        else:
            query = "SELECT movieID, title, releaseYear, genre, minimumAge FROM Movie WHERE " + ('title LIKE ? AND ' * len(tokens) + 'NOT title LIKE ? AND ' * len(negativeTokens))[:-4] # Remove final AND

        print(query, tokens+negativeTokens)
        db.exec(query, tokens+negativeTokens)
        data = db.display()
        print("Once you've retrieved a single specific movie by search you will see more information about it.")
        print()

    return data[0][0] # movieID