import db
"""Create the tables in the database"""
db.exec("""CREATE TABLE User (
    userID INTEGER PRIMARY KEY,
    emailAddress VARCHAR(320),
    passwordHashAndSalt BINARY(36),
    firstName VARCHAR(50),
    lastName VARCHAR(50),
    dateOfBirth DATE
)""")
db.exec("""CREATE TABLE Review (
        reviewID INTEGER PRIMARY KEY,
        userID INTEGER,
        movieID INTEGER,
        starRating DECIMAL(2,1),
        comment VARCHAR(5000)
    )""") # DECIMAL(2,1) means 2 digits total with 1 after decimal place
db.exec("""CREATE TABLE Movie (
            movieID INTEGER PRIMARY KEY,
            title VARCHAR(100),
            releaseYear INTEGER,
            genre VARCHAR(30),
            minimumAge INTEGER
        )""")
db.exec("""CREATE TABLE ActorRole (
                actorRoleID INTEGER PRIMARY KEY,
                movieID INTEGER,
                actorID INTEGER,
                characterName VARCHAR(100)
            )""")
db.exec("""CREATE TABLE Actor (
                actorID INTEGER PRIMARY KEY,
                stageName VARCHAR(100)
        )""")
db.done()