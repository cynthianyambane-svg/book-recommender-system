
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict


# ---------------------------------------------------------------------------
# Core data model
# ---------------------------------------------------------------------------

@dataclass
class Book:
    book_id: str
    title: str
    author: str
    genre: str
    available: bool = True

    def __repr__(self):
        status = "available" if self.available else "borrowed"
        return f"[{self.book_id}] {self.title} — {self.author} ({self.genre}) [{status}]"

    def to_dict(self) -> dict:
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "available": self.available,
        }



# 1. Binary Search Tree — keyed by title


class _BSTNode:
    __slots__ = ("book", "left", "right")

    def __init__(self, book: Book):
        self.book = book
        self.left: Optional["_BSTNode"] = None
        self.right: Optional["_BSTNode"] = None


class TitleBST:
   

    def __init__(self):
        self.root: Optional[_BSTNode] = None
        self._size = 0

    def __len__(self):
        return self._size

    def insert(self, book: Book) -> None:
        self.root = self._insert(self.root, book)
        self._size += 1

    def _insert(self, node: Optional[_BSTNode], book: Book) -> _BSTNode:
        if node is None:
            return _BSTNode(book)
        key = book.title.lower()
        node_key = node.book.title.lower()
        if key < node_key:
            node.left = self._insert(node.left, book)
        elif key > node_key:
            node.right = self._insert(node.right, book)
        else:
            # Duplicate title — replace book at this node (or you could
            # chain duplicates in a list; keep it simple here).
            node.book = book
        return node

    def search(self, title: str) -> Optional[Book]:
        """Exact title match. O(log n) average."""
        node = self.root
        key = title.lower()
        while node is not None:
            node_key = node.book.title.lower()
            if key == node_key:
                return node.book
            node = node.left if key < node_key else node.right
        return None

    def search_prefix(self, prefix: str) -> List[Book]:
   
        results: List[Book] = []
        prefix = prefix.lower()

        def visit(node: Optional[_BSTNode]):
            if node is None:
                return
            node_key = node.book.title.lower()
            # Only descend left if it's possible smaller titles could
            # still start with the prefix.
            if node_key >= prefix:
                visit(node.left)
            if node_key.startswith(prefix):
                results.append(node.book)
            if node_key <= prefix or node_key.startswith(prefix):
                visit(node.right)
            elif node_key > prefix:
                visit(node.right)

        visit(self.root)
        return results

    def in_order(self) -> List[Book]:
        """Return all books sorted alphabetically by title. O(n)."""
        result: List[Book] = []

        def visit(node):
            if node is None:
                return
            visit(node.left)
            result.append(node.book)
            visit(node.right)

        visit(self.root)
        return result

    def delete(self, title: str) -> bool:
        """Delete by exact title. O(log n) average."""
        self.root, deleted = self._delete(self.root, title.lower())
        if deleted:
            self._size -= 1
        return deleted

    def _delete(self, node: Optional[_BSTNode], key: str):
        if node is None:
            return None, False
        node_key = node.book.title.lower()
        if key < node_key:
            node.left, deleted = self._delete(node.left, key)
            return node, deleted
        if key > node_key:
            node.right, deleted = self._delete(node.right, key)
            return node, deleted

        # Found the node to delete
        if node.left is None:
            return node.right, True
        if node.right is None:
            return node.left, True
        # Two children: replace with in-order successor
        successor = node.right
        while successor.left is not None:
            successor = successor.left
        node.book = successor.book
        node.right, _ = self._delete(node.right, successor.book.title.lower())
        return node, True



# 2. Hash Table — keyed by genre / author (Python dict, plus a manual
#    chained version in case your rubric wants the internals shown)


class GenreAuthorIndex:


    def __init__(self):
        self._by_genre: Dict[str, List[Book]] = {}
        self._by_author: Dict[str, List[Book]] = {}

    def insert(self, book: Book) -> None:
        self._by_genre.setdefault(book.genre.lower(), []).append(book)
        self._by_author.setdefault(book.author.lower(), []).append(book)

    def by_genre(self, genre: str) -> List[Book]:
        return list(self._by_genre.get(genre.lower(), []))

    def by_author_exact(self, author: str) -> List[Book]:
        return list(self._by_author.get(author.lower(), []))

    def all_authors_sorted(self) -> List[str]:
        return sorted(self._by_author.keys())

    def delete(self, book: Book) -> None:
        bucket = self._by_genre.get(book.genre.lower(), [])
        if book in bucket:
            bucket.remove(book)
        bucket = self._by_author.get(book.author.lower(), [])
        if book in bucket:
            bucket.remove(book)


class SimpleHashTable:

    def __init__(self, capacity: int = 16):
        self.capacity = capacity
        self.buckets: List[List] = [[] for _ in range(capacity)]
        self.count = 0

    def _hash(self, key: str) -> int:
        return sum(ord(c) for c in key) % self.capacity

    def insert(self, key: str, value) -> None:
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)  # overwrite
                return
        bucket.append((key, value))
        self.count += 1
        if self.count / self.capacity > 0.75:
            self._resize()

    def get(self, key: str):
        bucket = self.buckets[self._hash(key)]
        for k, v in bucket:
            if k == key:
                return v
        return None

    def _resize(self) -> None:
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.count = 0
        for bucket in old_buckets:
            for k, v in bucket:
                self.insert(k, v)


# ---------------------------------------------------------------------------
# 3. Doubly Linked List — search history with back/forward navigation
# ---------------------------------------------------------------------------

@dataclass
class SearchEntry:
    """One recorded search: what was searched, how, and what came back."""
    query: str
    search_type: str          # "title", "title_prefix", "genre", "author"
    results: List[Book] = field(default_factory=list)

    def __repr__(self):
        return f"<{self.search_type}: '{self.query}' -> {len(self.results)} result(s)>"

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "search_type": self.search_type,
            "result_count": len(self.results),
            "results": [b.to_dict() for b in self.results],
        }


class _DLLNode:
    __slots__ = ("entry", "prev", "next")

    def __init__(self, entry: SearchEntry):
        self.entry = entry
        self.prev: Optional["_DLLNode"] = None
        self.next: Optional["_DLLNode"] = None


class SearchHistory:
 

    def __init__(self):
        self.head: Optional[_DLLNode] = None
        self.tail: Optional[_DLLNode] = None
        self.current: Optional[_DLLNode] = None
        self._size = 0

    def __len__(self):
        return self._size

    def record(self, entry: SearchEntry) -> None:
        new_node = _DLLNode(entry)

        if self.current is None:
            # Empty history, or history was fully reset
            self.head = self.tail = self.current = new_node
            self._size = 1
            return

        # If we're not at the tail (user had gone "back"), drop the
        # abandoned forward branch — mirrors real browser behaviour.
        if self.current.next is not None:
            self.current.next = None
            self.tail = self.current
            self._recount()

        new_node.prev = self.current
        self.current.next = new_node
        self.tail = new_node
        self.current = new_node
        self._size += 1

    def back(self) -> Optional[SearchEntry]:
        """Step to the previous search. O(1)."""
        if self.current is None or self.current.prev is None:
            return None
        self.current = self.current.prev
        return self.current.entry

    def forward(self) -> Optional[SearchEntry]:
        """Step to the next search (only valid after back()). O(1)."""
        if self.current is None or self.current.next is None:
            return None
        self.current = self.current.next
        return self.current.entry

    def current_entry(self) -> Optional[SearchEntry]:
        return self.current.entry if self.current else None

    def recent(self, n: int = 5) -> List[SearchEntry]:
        """Most recent n searches, newest first. O(n)."""
        out = []
        node = self.tail
        while node is not None and len(out) < n:
            out.append(node.entry)
            node = node.prev
        return out

    def full_timeline(self) -> List[SearchEntry]:
        """Every recorded search, oldest first. O(n)."""
        out = []
        node = self.head
        while node is not None:
            out.append(node.entry)
            node = node.next
        return out

    def status(self) -> dict:
   
        timeline = self.full_timeline()
        current_index = None
        node = self.head
        i = 0
        while node is not None:
            if node is self.current:
                current_index = i
                break
            node = node.next
            i += 1
        return {
            "timeline": timeline,
            "current_index": current_index,
            "can_back": self.current.prev is not None if self.current else False,
            "can_forward": self.current.next is not None if self.current else False,
        }

    def _recount(self) -> None:
        count = 0
        node = self.head
        while node is not None:
            count += 1
            node = node.next
        self._size = count


# ---------------------------------------------------------------------------
# 4. Algorithms — Merge Sort + Binary Search (used for author search path)
# ---------------------------------------------------------------------------

def merge_sort(books: List[Book], key=lambda b: b.author.lower()) -> List[Book]:
 
    if len(books) <= 1:
        return books[:]
    mid = len(books) // 2
    left = merge_sort(books[:mid], key)
    right = merge_sort(books[mid:], key)
    return _merge(left, right, key)


def _merge(left: List[Book], right: List[Book], key) -> List[Book]:
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def binary_search_by_author(sorted_books: List[Book], author: str) -> List[Book]:
    """
    Binary search for the first matching author in a list sorted by
    author (produced by merge_sort). Then scans outward to collect
    all books by that author, since duplicates cluster together in
    sorted order. O(log n) to find + O(k) to collect k matches.
    """
    target = author.lower()
    lo, hi = 0, len(sorted_books) - 1
    found_index = -1

    while lo <= hi:
        mid = (lo + hi) // 2
        mid_key = sorted_books[mid].author.lower()
        if mid_key == target:
            found_index = mid
            break
        elif mid_key < target:
            lo = mid + 1
        else:
            hi = mid - 1

    if found_index == -1:
        return []

    # Expand left and right to catch all books by this author
    results = [sorted_books[found_index]]
    i = found_index - 1
    while i >= 0 and sorted_books[i].author.lower() == target:
        results.append(sorted_books[i]); i -= 1
    i = found_index + 1
    while i < len(sorted_books) and sorted_books[i].author.lower() == target:
        results.append(sorted_books[i]); i += 1
    return results


# ---------------------------------------------------------------------------
# 5. Public facing module — this is what your UI/API teammate calls
# ---------------------------------------------------------------------------

class SearchFilterModule:


    def __init__(self):
        self._title_bst = TitleBST()
        self._index = GenreAuthorIndex()
        self._all_books: List[Book] = []
        self._author_sorted_cache: Optional[List[Book]] = None  # lazy
        self._history = SearchHistory()

    # ---- CRUD-ish entry points ----

    def add_book(self, book: Book) -> None:
        self._title_bst.insert(book)
        self._index.insert(book)
        self._all_books.append(book)
        self._author_sorted_cache = None  # invalidate cache

    def remove_book(self, title: str) -> bool:
        book = self._title_bst.search(title)
        if book is None:
            return False
        self._title_bst.delete(title)
        self._index.delete(book)
        self._all_books.remove(book)
        self._author_sorted_cache = None
        return True

    # ---- Search paths ----

    def search_by_title(self, title: str) -> Optional[Book]:
        """BST exact search. O(log n) average. Recorded in history."""
        result = self._title_bst.search(title)
        results_list = [result] if result else []
        self._history.record(SearchEntry(title, "title", results_list))
        return result

    def search_by_title_prefix(self, prefix: str) -> List[Book]:
        """BST prefix search, results sorted alphabetically. Recorded in history."""
        results = self._title_bst.search_prefix(prefix)
        self._history.record(SearchEntry(prefix, "title_prefix", results))
        return results

    def filter_by_genre(self, genre: str) -> List[Book]:
        """Hash table bucket lookup. O(1) average. Recorded in history."""
        results = self._index.by_genre(genre)
        self._history.record(SearchEntry(genre, "genre", results))
        return results

    def search_by_author(self, author: str) -> List[Book]:
        """
        Two valid paths are shown here so you can compare them in
        your report:
          (a) direct hash lookup — O(1) average, used by default
          (b) merge sort + binary search — O(n log n) once, then
              O(log n) per query; use this path if you specifically
              need to demonstrate the sort/search algorithm pair
        Recorded in history either way.
        """
        results = self._index.by_author_exact(author)
        self._history.record(SearchEntry(author, "author", results))
        return results

    def search_by_author_via_sort(self, author: str) -> List[Book]:
        """Explicit merge-sort + binary-search path (algorithm demo)."""
        if self._author_sorted_cache is None:
            self._author_sorted_cache = merge_sort(self._all_books)
        results = binary_search_by_author(self._author_sorted_cache, author)
        self._history.record(SearchEntry(author, "author_sort", results))
        return results

    def list_all_sorted_by_title(self) -> List[Book]:
        return self._title_bst.in_order()

    # ---- Search history navigation (doubly linked list) ----

    def history_back(self) -> Optional[SearchEntry]:
        """Step to the previous search, like a browser back button. O(1)."""
        return self._history.back()

    def history_forward(self) -> Optional[SearchEntry]:
        """Step to the next search (only after having gone back). O(1)."""
        return self._history.forward()

    def current_search(self) -> Optional[SearchEntry]:
        return self._history.current_entry()

    def recent_searches(self, n: int = 5) -> List[SearchEntry]:
        """Most recent n searches, newest first. O(n)."""
        return self._history.recent(n)

    def history_status(self) -> dict:
        """Full history state for UI rendering (see SearchHistory.status)."""
        return self._history.status()

    def history_status_for_json(self) -> dict:
        """Same as history_status(), but with SearchEntry objects converted
        to plain dicts so it can be passed straight to jsonify()/json.dumps()."""
        raw = self._history.status()
        return {
            "timeline": [e.to_dict() for e in raw["timeline"]],
            "current_index": raw["current_index"],
            "can_back": raw["can_back"],
            "can_forward": raw["can_forward"],
        }


# ---------------------------------------------------------------------------
# Demo / manual test — run this file directly to see it work
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    module = SearchFilterModule()

    sample_books = [
        Book("B001", "The Hobbit", "J.R.R. Tolkien", "Fantasy"),
        Book("B002", "The Fellowship of the Ring", "J.R.R. Tolkien", "Fantasy"),
        Book("B003", "Dune", "Frank Herbert", "Sci-Fi"),
        Book("B004", "Foundation", "Isaac Asimov", "Sci-Fi"),
        Book("B005", "I, Robot", "Isaac Asimov", "Sci-Fi"),
        Book("B006", "1984", "George Orwell", "Dystopian"),
        Book("B007", "Animal Farm", "George Orwell", "Dystopian"),
    ]
    for b in sample_books:
        module.add_book(b)

    print("--- Search by exact title (BST) ---")
    print(module.search_by_title("Dune"))

    print("\n--- Search by title prefix 'the' (BST) ---")
    for b in module.search_by_title_prefix("the"):
        print(" ", b)

    print("\n--- Filter by genre 'Sci-Fi' (hash table) ---")
    for b in module.filter_by_genre("Sci-Fi"):
        print(" ", b)

    print("\n--- Search by author 'Isaac Asimov' (hash table) ---")
    for b in module.search_by_author("Isaac Asimov"):
        print(" ", b)

    print("\n--- Search by author 'George Orwell' (merge sort + binary search) ---")
    for b in module.search_by_author_via_sort("George Orwell"):
        print(" ", b)

    print("\n--- All books sorted by title (BST in-order traversal) ---")
    for b in module.list_all_sorted_by_title():
        print(" ", b)

    print("\n--- Search history (doubly linked list) ---")
    print("Recent searches, newest first:")
    for entry in module.recent_searches(10):
        print(" ", entry)

    print("\nStepping back through history:")
    print(" current:", module.current_search())
    print(" back()  ->", module.history_back())
    print(" back()  ->", module.history_back())
    print(" forward()->", module.history_forward())

    print("\nNew search after stepping back truncates abandoned forward branch:")
    module.filter_by_genre("Fantasy")
    print(" recent searches now:", [str(e) for e in module.recent_searches(3)])
