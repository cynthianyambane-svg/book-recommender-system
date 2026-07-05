# ============================================================
# book.py — Book Data Class
# AI-Powered Book Recommendation System — Person 3
# Name: Bakhita Wanjiru | Student Number: 222593 
# ============================================================

import datetime


class Book:
    """
    Represents a single book in the system.
    Used by UserProfile when marking books as read or adding to reading list.
    Serializable (all fields are basic Python types) so it can be
    stored in stacks, queues, and exported to JSON easily.
    """

    def __init__(self, title: str, author: str, genre: str):
        self.title       = title
        self.author      = author
        self.genre       = genre
        self.date_added  = str(datetime.date.today())
        self.rating      = None        # set when marked as read
        self.date_finished = None      # set when marked as read

    def mark_finished(self, rating: int):
        """Record that the user finished this book with a rating (1–5)."""
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5.")
        self.rating        = rating
        self.date_finished = str(datetime.date.today())

    def to_dict(self) -> dict:
        """Convert to dictionary — used for stack/queue storage and JSON export."""
        return {
            "title"         : self.title,
            "author"        : self.author,
            "genre"         : self.genre,
            "rating"        : self.rating,
            "date_added"    : self.date_added,
            "date_finished" : self.date_finished
        }

    def __str__(self):
        stars = ("⭐" * self.rating) if self.rating else "unrated"
        return f"'{self.title}' by {self.author} [{self.genre}] — {stars}"

    def __repr__(self):
        return f"Book(title={self.title!r}, author={self.author!r}, genre={self.genre!r})"