
import json

# 1. THE Book OBJECT
# ---------------------------------------------------------------------
class Book:
    """A single book record. Plain data holder used everywhere."""

    def __init__(self, book_id, title, author, genre, year=None,
                 rating=0.0, tags=None):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year
        self.rating = rating          # average rating
        self.tags = tags or []        # list of keywords

    def to_dict(self):
        """Convert to a plain dict — handy for JSON / UI (Person 5)."""
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "year": self.year,
            "rating": self.rating,
            "tags": self.tags,
        }

    @staticmethod
    def from_dict(d):
        """Build a Book back from a dict (e.g. loaded from JSON)."""
        return Book(
            book_id=d["book_id"],
            title=d["title"],
            author=d["author"],
            genre=d["genre"],
            year=d.get("year"),
            rating=d.get("rating", 0.0),
            tags=d.get("tags", []),
        )

    def __repr__(self):
        return f"<Book {self.book_id}: '{self.title}' by {self.author}>"


# 2. THE DATABASE (hash maps + array)
# ---------------------------------------------------------------------
class BookDatabase:
   

    def __init__(self):
        self._catalogue = []      # list of all Book objects
        self._by_id = {}          # hash map: id  Book
        self._by_title = {}       # hash map: lowercase title 
        self._by_author = {}      # hash map: lowercase author 
        self._by_genre = {}       # hash map: lowercase genre 

    # ---------- WRITE OPERATIONS ----------

    def add_book(self, book: Book):
        """Add a book and index it in every hash map. O(1)."""
        if book.book_id in self._by_id:
            raise ValueError(f"Book id {book.book_id} already exists.")

        self._catalogue.append(book)
        self._by_id[book.book_id] = book
        self._by_title[book.title.lower()] = book
        self._by_author.setdefault(book.author.lower(), []).append(book)
        self._by_genre.setdefault(book.genre.lower(), []).append(book)

    def remove_book(self, book_id):
        """Remove a book by id from the catalogue and all hash maps."""
        book = self._by_id.pop(book_id, None)
        if not book:
            return False

        self._catalogue.remove(book)
        self._by_title.pop(book.title.lower(), None)
        self._by_author[book.author.lower()].remove(book)
        self._by_genre[book.genre.lower()].remove(book)
        return True

    # ---------- READ OPERATIONS ----------

    def get_all_books(self):
        """Return the full catalogue as a list. O(1)."""
        return self._catalogue

    def get_by_id(self, book_id):
        """O(1) hash map lookup."""
        return self._by_id.get(book_id)

    def get_by_title(self, title):
        """O(1) hash map lookup, case-insensitive."""
        return self._by_title.get(title.lower())

    def get_by_author(self, author):
        """O(1) hash map lookup, case-insensitive. Returns list[Book]."""
        return self._by_author.get(author.lower(), [])

    def get_by_genre(self, genre):
        """O(1) hash map lookup, case-insensitive. Returns list[Book]."""
        return self._by_genre.get(genre.lower(), [])

    def count(self):
        return len(self._catalogue)

    def to_dict_list(self):
        """Whole catalogue as list of plain dicts (easy for UI / JSON)."""
        return [b.to_dict() for b in self._catalogue]

    # ---------- LOADING DATA ----------

    def load_from_json(self, filepath):
        """Load books from a JSON file: a list of book dicts."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            self.add_book(Book.from_dict(entry))

    def save_to_json(self, filepath):
        """Save the current catalogue out to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict_list(), f, indent=2)

    def load_sample_data(self):
        """Quick built-in sample dataset, useful for testing/demo without a file."""
        sample_books = [
            Book(1, "Dune", "Frank Herbert", "Sci-Fi", 1965, 4.8,
                 ["desert", "politics", "epic"]),
            Book(2, "The Hobbit", "J.R.R. Tolkien", "Fantasy", 1937, 4.7,
                 ["adventure", "dragons"]),
            Book(3, "1984", "George Orwell", "Dystopian", 1949, 4.9,
                 ["surveillance", "politics"]),
            Book(4, "The Fellowship of the Ring", "J.R.R. Tolkien",
                 "Fantasy", 1954, 4.8, ["adventure", "friendship"]),
            Book(5, "Foundation", "Isaac Asimov", "Sci-Fi", 1951, 4.6,
                 ["empire", "future"]),
            Book(6, "Brave New World", "Aldous Huxley", "Dystopian", 1932,
                 4.5, ["society", "control"]),
            Book(7, "The Name of the Wind", "Patrick Rothfuss", "Fantasy",
                 2007, 4.7, ["magic", "coming-of-age"]),
            Book(8, "Neuromancer", "William Gibson", "Sci-Fi", 1984, 4.3,
                 ["cyberpunk", "hacking"]),
        ]
        for b in sample_books:
            self.add_book(b)



# 3. QUICK SELF-TEST (only runs if you execute this file directly)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    db = BookDatabase()
    db.load_sample_data()

    print(f"Total books loaded: {db.count()}\n")

    print("Lookup by id (3):", db.get_by_id(3))
    print("Lookup by title ('dune'):", db.get_by_title("dune"))
    print("Lookup by author ('J.R.R. Tolkien'):", db.get_by_author("J.R.R. Tolkien"))
    print("Lookup by genre ('sci-fi'):", db.get_by_genre("sci-fi"))

    print("\nFull catalogue:")
    for book in db.get_all_books():
        print(" ", book)

  
