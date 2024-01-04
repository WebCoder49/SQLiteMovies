print("\x1b[7m Main Interface - View and Rate Actors in Movies! \x1b[0m")
print("Login with admin@webcoder49.dev and password 'password' for arbitrary SQL and updating the movies/actors available.\nRegister an account to see and write reviews.\n")

"""Main interface for users"""

from interface.user import loginOrRegister, deleteAccount
from interface.search import searchMovieReturnID
from interface.reviews import showReviewPage, allowWriteReview
from adminPopulate import adminShell

import db

while True:
    print()
    # TODO: Test
    userID = loginOrRegister()
    db.conn.commit()

    if userID == -1:
        adminShell()
    else:
        while True:
            print("1. Search for a movie and view its reviews, or even write a review yourself.\n2. Logout\n3. Delete your account")
            choice = 0
            while choice < 1 or choice > 3:
                try:
                    choice = int(input("Choose a number for an option above: "))
                except ValueError:
                    choice = 0
            if choice == 1:
                id = searchMovieReturnID()
                showReviewPage(id)
                allowWriteReview(id, userID)
            elif choice == 2:
                break
            else:
                if input("Type 'delete' to delete your account: ").upper() == "DELETE":
                    deleteAccount(userID)
                    print("Your account has been deleted along with your reviews.")
                else:
                    print("Your account still exists.")
                break