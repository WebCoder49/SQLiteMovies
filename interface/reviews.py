import db

def showReviewPage(movieID:int):
    db.exec("""SELECT title, releaseYear, genre, minimumAge
                FROM Movie
                WHERE movieID = ?""", (movieID,))
    movieData = db.cur.fetchone()

    db.exec("""SELECT Actor.stageName, ActorRole.characterName
                    FROM ActorRole INNER JOIN Movie ON Movie.movieID = ActorRole.movieID INNER JOIN Actor ON Actor.actorID = ActorRole.actorID
                    WHERE Movie.movieID = ?""", (movieID,))
    roleData = db.cur.fetchall()

    db.exec("""SELECT User.firstName, User.lastName, Review.starRating, Review.comment
                        FROM Review INNER JOIN Movie ON Movie.movieID = Review.movieID INNER JOIN User ON User.userID = Review.userID
                        WHERE Movie.movieID = ?""", (movieID,))
    reviewData = db.cur.fetchall()

    print(f"\x1b[7m\t{movieData[0]} \x1b[0m")
    print(f"\x1b[7m \x1b[0m\tReleased in {movieData[1]} • {movieData[2]} • Suitable for ages {movieData[3]}+")
    print("\x1b[7m \x1b[0m\tStarring: ")
    for role in roleData:
        print(f"\x1b[7m \x1b[0m\t •\t{role[0]} as {role[1]}")
    print("\x1b[7m \x1b[0m\tReviews: ")

    totalStars = 0;
    for review in reviewData:
        print(f"\x1b[7m \x1b[0m\t •\t{review[0]} {review[1]}: {review[2]} stars\t{review[3]}")
        totalStars += review[2]
    if(len(reviewData) == 0):
        print("\x1b[7m \x1b[0m\t\tNo reviews.")
        print(f"\x1b[7m\tWhy don't you write a review? \x1b[0m")
    else:
        meanStars = totalStars / len(reviewData)
        print(f"\x1b[7m {round(meanStars*10)/10} stars on average. \x1b[0m")
    print()

def allowWriteReview(movieID:int, userID:int):
    if(input("Do you want to write a review for this movie? Answer Yes or just press enter to refuse: ").upper() == "YES"):
        print()
        print("\x1b[94m\x1b[7m Write a Review \x1b[0m")
        numStars = -1
        while numStars == -1 or numStars > 5 or numStars < 0 or numStars % 0.5 != 0:
            try:
                numStars = float(input("How many stars you give the movie (half-stars are allowed, from 0 to 5): "))
            except ValueError:
                numStars = -1

        comment = ""
        while comment == "" or len(comment) > 5000:
            comment = input("Enter your review text here (5000 characters max): ")
        print()

        db.exec("INSERT INTO Review (userID, movieID, starRating, comment) VALUES (?, ?, ?, ?)", (userID, movieID, numStars, comment))
        db.conn.commit()