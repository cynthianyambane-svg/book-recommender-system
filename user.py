# ============================================================
# user.py — User Profile & History Management
# AI-Powered Book Recommendation System — Person 3
# Name: Bakhita Wanjiru | Student Number: 222593
#
# DATA STRUCTURES:
#   - Stack        → Reading history  (ReadingHistoryStack)
#   - Queue        → Reading list     (ReadingQueue)
#   - Linked List  → Preferences      (PreferenceLinkedList)
#   - Dictionary   → Profile & ratings (UserProfile.profile)
# ============================================================

from collections import deque
from book import Book
import datetime
import json


# ╔══════════════════════════════════════════════════════════════╗
# ║          1. LINKED LIST — User Preferences                  ║
# ╚══════════════════════════════════════════════════════════════╝

class PreferenceNode:
    """A single node in the preferences linked list."""
    def __init__(self, preference: str, weight: int = 1):
        self.preference = preference   # e.g. "Fantasy", "George Orwell"
        self.weight     = weight       # strength of preference (1–5)
        self.next       = None         # pointer to next node


class PreferenceLinkedList:
    """
    Singly Linked List storing user genre/author preferences.

    Why Linked List?
      Preferences are added and removed frequently with no need for
      index-based access. Insertions at head are O(1).

    Operations:
      add_preference    → O(n) — scans for duplicates first
      remove_preference → O(n) — must find the node to remove
      get_top_preferences → O(n log n) — sort by weight
    """

    def __init__(self):
        self.head = None
        self.size = 0

    def add_preference(self, preference: str, weight: int = 1):
        """
        Add a new preference or boost weight if it already exists.
        Cap weight at 5.
        """
        current = self.head
        while current:
            if current.preference.lower() == preference.lower():
                current.weight = min(5, current.weight + 1)
                print(f"   ↑ '{preference}' weight boosted to {current.weight}")
                return
            current = current.next

        # Not found — insert at head (O(1))
        new_node      = PreferenceNode(preference, weight)
        new_node.next = self.head
        self.head     = new_node
        self.size    += 1
        print(f"   + Preference added: '{preference}' (weight: {weight})")

    def remove_preference(self, preference: str):
        """Remove a preference by name."""
        if not self.head:
            print("   [WARN] No preferences to remove.")
            return

        # Edge case: removing the head node
        if self.head.preference.lower() == preference.lower():
            self.head  = self.head.next
            self.size -= 1
            print(f"   - Preference removed: '{preference}'")
            return

        current = self.head
        while current.next:
            if current.next.preference.lower() == preference.lower():
                current.next = current.next.next   # bypass node
                self.size   -= 1
                print(f"   - Preference removed: '{preference}'")
                return
            current = current.next

        print(f"   [WARN] Preference '{preference}' not found.")

    def get_top_preferences(self, n: int = 3) -> list:
        """Return top-n preferences sorted by weight descending."""
        all_prefs = self.to_list()
        sorted_prefs = sorted(all_prefs, key=lambda x: x[1], reverse=True)
        return sorted_prefs[:n]

    def to_list(self) -> list:
        """Convert linked list to list of (preference, weight) tuples."""
        result  = []
        current = self.head
        while current:
            result.append((current.preference, current.weight))
            current = current.next
        return result

    def display(self):
        """Visualise the linked list."""
        if not self.head:
            print("   [empty preferences]")
            return
        current = self.head
        parts   = []
        while current:
            parts.append(f"[{current.preference} (w:{current.weight})]")
            current = current.next
        print("   " + " → ".join(parts) + " → NULL")


# ╔══════════════════════════════════════════════════════════════╗
# ║              2. STACK — Reading History                     ║
# ╚══════════════════════════════════════════════════════════════╝

class ReadingHistoryStack:
    """
    Stack (LIFO) tracking books the user has finished.
    Most recently read book is always on top.

    Why Stack?
      Last read is most relevant for recommendations.
      Push on finish, pop to undo, peek to see latest.

    Operations: push O(1), pop O(1), peek O(1)
    """

    def __init__(self, max_size: int = 50):
        self._stack   = []
        self.max_size = max_size

    def push(self, book_dict: dict):
        """Push a finished book (as dict) onto the stack."""
        if len(self._stack) >= self.max_size:
            self._stack.pop(0)   # remove oldest to stay within limit
            print("   [WARN] History full - oldest entry removed.")

        self._stack.append(book_dict)
        print(f"   [HISTORY] Added to history: '{book_dict['title']}' by {book_dict['author']}")

    def pop(self) -> dict:
        """Remove and return the most recently read book."""
        if self.is_empty():
            print("   [WARN] Reading history is empty.")
            return None
        return self._stack.pop()

    def peek(self) -> dict:
        """View the most recently read book without removing it."""
        return self._stack[-1] if not self.is_empty() else None

    def is_empty(self) -> bool:
        return len(self._stack) == 0

    def size(self) -> int:
        return len(self._stack)

    def get_all(self) -> list:
        """Return all history, most recent first."""
        return list(reversed(self._stack))

    def get_genres_read(self) -> dict:
        """Count occurrences of each genre in history."""
        genre_count = {}
        for book in self._stack:
            genre = book.get("genre", "Unknown")
            genre_count[genre] = genre_count.get(genre, 0) + 1
        return genre_count

    def get_average_rating(self) -> float:
        """Average rating across all rated books in history."""
        ratings = [b.get("rating") for b in self._stack if b.get("rating")]
        return round(sum(ratings) / len(ratings), 2) if ratings else 0.0

    def display(self):
        """Print history with most recent on top."""
        if self.is_empty():
            print("   [no reading history]")
            return
        print(f"   {'─'*55}")
        print(f"   {'TOP (most recent)':^55}")
        print(f"   {'─'*55}")
        for i, book in enumerate(reversed(self._stack)):
            stars = "⭐" * (book.get("rating") or 0)
            print(f"   [{i+1}] '{book['title']}' — {book['author']}")
            print(f"        Genre: {book['genre']} | Rating: {stars} | {book.get('date_finished','')}")
        print(f"   {'─'*55}")
        print(f"   {'BOTTOM (oldest)':^55}")


# ╔══════════════════════════════════════════════════════════════╗
# ║           3. QUEUE — Reading List (Want-to-Read)            ║
# ╚══════════════════════════════════════════════════════════════╝

class ReadingQueue:
    """
    Queue (FIFO) for the user's planned reading list.
    Books are read in the order they were added.

    Why Queue?
      Preserves the user's intended reading order.
      First queued = first to read next.

    Uses collections.deque for O(1) enqueue and dequeue.
    """

    def __init__(self):
        self._queue = deque()

    def enqueue(self, book_dict: dict):
        """Add a book to the back of the reading list."""
        book_dict["date_added"] = str(datetime.date.today())
        self._queue.append(book_dict)
        print(f"   📖 Queued: '{book_dict['title']}' by {book_dict['author']}")

    def dequeue(self) -> dict:
        """Remove and return the next book to read (front of queue)."""
        if self.is_empty():
            print("   ⚠ Reading list is empty.")
            return None
        book = self._queue.popleft()
        print(f"   [OK] Starting: '{book['title']}' - removed from queue.")
        return book

    def peek_next(self) -> dict:
        """View the next book without removing it."""
        return self._queue[0] if not self.is_empty() else None

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def size(self) -> int:
        return len(self._queue)

    def contains(self, title: str) -> bool:
        """Check if a title is already in the reading list."""
        return any(b["title"].lower() == title.lower() for b in self._queue)

    def remove_by_title(self, title: str):
        """Remove a specific book from the queue by title."""
        self._queue = deque(
            b for b in self._queue
            if b["title"].lower() != title.lower()
        )

    def display(self):
        """Print the queue front to back."""
        if self.is_empty():
            print("   [reading list is empty]")
            return
        print(f"   {'─'*50}")
        print(f"   {'NEXT TO READ':^50}")
        print(f"   {'─'*50}")
        for i, book in enumerate(self._queue):
            print(f"   [{i+1}] '{book['title']}' by {book['author']} ({book['genre']})")
        print(f"   {'─'*50}")
        print(f"   {'(end of list)':^50}")


# ╔══════════════════════════════════════════════════════════════╗
# ║         4. USER PROFILE — ties all structures together      ║
# ╚══════════════════════════════════════════════════════════════╝

class UserProfile:
    """
    Full user profile combining:
      Dictionary   → core info + O(1) ratings lookup
      Stack        → reading history
      Queue        → reading list
      Linked List  → preferences
    """

    def __init__(self, user_id: str, name: str, email: str):
        # Core profile — dictionary
        self.profile = {
            "user_id"    : user_id,
            "name"       : name,
            "email"      : email,
            "created_at" : str(datetime.date.today()),
            "ratings"    : {}   # {title: rating}  — O(1) lookup
        }

        # Data structures
        self.history      = ReadingHistoryStack(max_size=50)
        self.reading_list = ReadingQueue()
        self.preferences  = PreferenceLinkedList()

    # ── Getters ───────────────────────────────────────────────

    def get_id(self)    -> str: return self.profile["user_id"]
    def get_name(self)  -> str: return self.profile["name"]
    def get_email(self) -> str: return self.profile["email"]

    def update_email(self, new_email: str):
        self.profile["email"] = new_email
        print(f"   ✔ Email updated to: {new_email}")

    # ── Reading History (Stack) ───────────────────────────────

    def mark_as_read(self, book: Book, rating: int):
        """
        Finish a book:
          1. Validate and set rating on the Book object
          2. Push to history stack
          3. Store rating in dictionary (O(1) lookup later)
          4. Auto-update preferences if rating >= 4
          5. Remove from reading list if it was queued
        """
        try:
            book.mark_finished(rating)
        except ValueError as e:
            print(f"   [WARN] {e}")
            return

        book_dict = book.to_dict()
        self.history.push(book_dict)

        # O(1) rating storage
        self.profile["ratings"][book.title] = rating

        # Auto-boost preferences for highly rated books
        if rating >= 4:
            self.preferences.add_preference(book.genre,  weight=rating - 2)
            self.preferences.add_preference(book.author, weight=rating - 3)

        # Remove from reading list if present
        if self.reading_list.contains(book.title):
            self.reading_list.remove_by_title(book.title)
            print(f"   [REMOVED] '{book.title}' removed from reading list.")

    def undo_last_read(self):
        """Pop the last entry off the history stack."""
        book = self.history.pop()
        if book:
            self.profile["ratings"].pop(book["title"], None)
            print(f"   [UNDO] Undone: '{book['title']}' removed from history.")

    def get_last_read(self) -> dict:
        return self.history.peek()

    # ── Reading List (Queue) ──────────────────────────────────

    def add_to_reading_list(self, book: Book):
        """Enqueue a book onto the reading list."""
        if self.has_read(book.title):
            print(f"   [WARN] You've already read '{book.title}'.")
            return
        if self.reading_list.contains(book.title):
            print(f"   [WARN] '{book.title}' is already in your reading list.")
            return
        self.reading_list.enqueue(book.to_dict())

    def start_next_book(self) -> dict:
        """Dequeue the next planned book."""
        return self.reading_list.dequeue()

    def whats_next(self) -> dict:
        return self.reading_list.peek_next()

    # ── Preferences (Linked List) ─────────────────────────────

    def add_preference(self, preference: str, weight: int = 1):
        self.preferences.add_preference(preference, weight)

    def remove_preference(self, preference: str):
        self.preferences.remove_preference(preference)

    def get_top_preferences(self, n: int = 3) -> list:
        return self.preferences.get_top_preferences(n)

    # ── Ratings (Dictionary) ──────────────────────────────────

    def get_rating(self, title: str) -> int:
        """O(1) rating lookup."""
        return self.profile["ratings"].get(title)

    def has_read(self, title: str) -> bool:
        """O(1) check."""
        return title in self.profile["ratings"]

    # ── Summary & Export ──────────────────────────────────────

    def get_summary(self) -> dict:
        """
        Structured summary for Person 2 (Recommendation Algorithm).
        Contains everything needed to suggest the next book.
        """
        return {
            "user_id"          : self.get_id(),
            "name"             : self.get_name(),
            "books_read"       : self.history.size(),
            "avg_rating"       : self.history.get_average_rating(),
            "genres_read"      : self.history.get_genres_read(),
            "top_preferences"  : self.get_top_preferences(5),
            "reading_list_size": self.reading_list.size(),
            "next_book"        : self.whats_next(),
            "last_read"        : self.get_last_read()
        }

    def export_to_json(self, filename: str = None):
        """Export full profile to JSON for persistence."""
        filename = filename or f"user_{self.get_id()}.json"
        data = {
            "profile"     : self.profile,
            "history"     : self.history.get_all(),
            "reading_list": list(self.reading_list._queue),
            "preferences" : self.preferences.to_list()
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"   [SAVE] Profile saved to '{filename}'")

    def display_full_profile(self):
        """Pretty-print the complete user profile."""
        print(f"\n{'═'*60}")
        print(f"  USER PROFILE")
        print(f"{'═'*60}")
        print(f"  Name    : {self.get_name()}")
        print(f"  ID      : {self.get_id()}")
        print(f"  Email   : {self.get_email()}")
        print(f"  Joined  : {self.profile['created_at']}")

        print(f"\n  STATS")
        print(f"  Books Read   : {self.history.size()}")
        print(f"  Avg Rating   : {self.history.get_average_rating()} ⭐")
        print(f"  Reading List : {self.reading_list.size()} book(s) queued")

        print(f"\n  TOP PREFERENCES (Linked List):")
        top = self.get_top_preferences(5)
        if top:
            for pref, weight in top:
                bar = "█" * weight + "░" * (5 - weight)
                print(f"    {pref:<20} [{bar}] {weight}/5")
        else:
            print("    (none yet)")

        print(f"\n  READING HISTORY (Stack):")
        self.history.display()

        print(f"\n  📋 READING LIST (Queue):")
        self.reading_list.display()

        print(f"{'═'*60}\n")


# ╔══════════════════════════════════════════════════════════════╗
# ║         5. USER PROFILE MANAGER — multi-user support        ║
# ╚══════════════════════════════════════════════════════════════╝

class UserProfileManager:
    """
    Registry of all user profiles.
    Dictionary {user_id: UserProfile} for O(1) lookup.
    Exposed to Person 5 (UI & Integration).
    """

    def __init__(self):
        self._users = {}

    def create_user(self, user_id: str, name: str, email: str) -> UserProfile:
        if user_id in self._users:
            print(f"[WARN] User '{user_id}' already exists.")
            return self._users[user_id]
        profile = UserProfile(user_id, name, email)
        self._users[user_id] = profile
        print(f"[OK] User created: {name} (ID: {user_id})")
        return profile

    def get_user(self, user_id: str) -> UserProfile:
        user = self._users.get(user_id)
        if not user:
            print(f"⚠ User '{user_id}' not found.")
        return user

    def delete_user(self, user_id: str):
        if user_id in self._users:
            del self._users[user_id]
            print(f"[DELETED] User '{user_id}' deleted.")
        else:
            print(f"⚠ User '{user_id}' not found.")

    def list_all_users(self):
        print(f"\n{'─'*40}")
        print(f"  REGISTERED USERS ({len(self._users)} total)")
        print(f"{'─'*40}")
        for uid, user in self._users.items():
            print(f"  [{uid}] {user.get_name()} — {user.get_email()}")
        print(f"{'─'*40}\n")

    def get_all_summaries(self) -> list:
        """All user summaries — for Person 2 (Recommendation Algorithm)."""
        return [user.get_summary() for user in self._users.values()]