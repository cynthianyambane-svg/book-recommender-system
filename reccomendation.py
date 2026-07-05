"""
recommendation.py
Person 2 — Recommendation Algorithm Module
AI-Powered Book Recommendation System

Wired against the REAL interfaces already committed to the repo:
  - Person 1 (P1Data_layer.py): BookDatabase.get_all_books() -> list[Book]
        Book fields: book_id, title, author, genre (single string), year,
        rating, tags (list)
  - Person 3 (user.py): UserProfile.get_summary() -> dict, and
        UserProfile.has_read(title) -> bool
        get_summary()["top_preferences"] is a list of (name, weight) tuples
        where `name` can be EITHER a genre or an author (Person 3's
        PreferenceLinkedList mixes both together).

Data Structures used here:
  1. Hash Map (dict)            -> O(1) preference-weight lookup per book
  2. Graph (dict of sets)       -> book-to-book similarity network

Algorithms used here:
  1. Weighted Scoring Algorithm (content-based filtering)
  2. Graph Traversal — BFS (collaborative-style "related books")
"""

from collections import deque, defaultdict


# ---------------------------------------------------------
# 1. WEIGHTED SCORING ALGORITHM (Content-Based Filtering)
# ---------------------------------------------------------
class WeightedRecommender:
    """
    Scores every book in the catalogue for a given user based on:
      - overlap with the user's weighted preferences (Person 3's linked
        list mixes genres + authors together, so we check a book's genre
        AND author against the same preference map)
      - the book's own average rating
      - a small recency boost

    Data structure: dict (hash map) turns the user's O(n) preference
    list into an O(1)-lookup structure, so scoring n books against
    m preferences is O(n) instead of O(n * m).
    """

    def __init__(self, weight_preference=0.6, weight_rating=0.3, weight_recency=0.1):
        self.weights = {
            "preference": weight_preference,
            "rating": weight_rating,
            "recency": weight_recency,
        }

    def _preferences_to_map(self, top_preferences: list) -> dict:
        """
        Converts Person 3's [(name, weight), ...] list into a
        {lowercase_name: weight} hash map for O(1) lookup.
        """
        return {name.lower(): weight for name, weight in top_preferences}

    def score_book(self, book, pref_map: dict) -> float:
        """
        book: a Person-1 Book object (book_id, title, author, genre,
              year, rating, tags)
        pref_map: output of _preferences_to_map()
        """
        score = 0.0

        # --- Preference match: check both genre and author against
        #     the same hash map, take whichever signal is stronger ---
        genre_weight = pref_map.get(book.genre.lower(), 0)
        author_weight = pref_map.get(book.author.lower(), 0)
        pref_score = max(genre_weight, author_weight) / 5   # weights are 1-5
        score += pref_score * self.weights["preference"]

        # --- Rating (normalised out of 5) ---
        rating_score = (book.rating or 0) / 5
        score += rating_score * self.weights["rating"]

        # --- Recency (small boost for books from the last ~10 years) ---
        recency_score = 1.0 if (book.year or 0) >= 2015 else 0.3
        score += recency_score * self.weights["recency"]

        return round(score, 4)

    def recommend(self, catalogue, user, top_n: int = 5, exclude_read: bool = True) -> list:
        """
        catalogue : Person 1's BookDatabase instance
        user      : Person 3's UserProfile instance (live object, not just
                    the summary dict) — we need user.has_read() to filter
                    out books they've already finished.

        Returns list of (book_id, title, score) tuples, highest score first.
        """
        summary = user.get_summary()
        pref_map = self._preferences_to_map(summary.get("top_preferences", []))

        scored = []
        for book in catalogue.get_all_books():
            if exclude_read and user.has_read(book.title):
                continue
            s = self.score_book(book, pref_map)
            scored.append((book.book_id, book.title, s))

        # Sort algorithm: Python's built-in Timsort, O(n log n)
        scored.sort(key=lambda x: x[2], reverse=True)
        return scored[:top_n]


# ---------------------------------------------------------
# 2. GRAPH + BFS TRAVERSAL ("Because you read X, try Y")
# ---------------------------------------------------------
class BookGraph:
    """
    A graph where each book is a node, and an edge exists between two
    books if they share a genre, share an author, or share at least
    one tag.

    Data structure: adjacency list using a dict of sets:
        { book_id: {neighbour_id, neighbour_id, ...} }

    Algorithm: Breadth-First Search (BFS) to find related books up to
    a given 'depth' (degrees of similarity) from a starting book.
    """

    def __init__(self):
        self.adjacency = defaultdict(set)   # hash map of sets

    def build_graph(self, catalogue):
        """
        catalogue : Person 1's BookDatabase instance
        O(n^2) pairwise comparison — acceptable for a coursework-sized
        catalogue. For a much larger catalogue this would instead be
        built by indexing on genre/author (reusing Person 1's
        _by_genre / _by_author hash maps) to avoid comparing every pair.
        """
        books = catalogue.get_all_books()
        for i in range(len(books)):
            for j in range(i + 1, len(books)):
                b1, b2 = books[i], books[j]
                same_genre = b1.genre.lower() == b2.genre.lower()
                same_author = b1.author.lower() == b2.author.lower()
                shared_tags = bool(set(b1.tags) & set(b2.tags))
                if same_genre or same_author or shared_tags:
                    self.adjacency[b1.book_id].add(b2.book_id)
                    self.adjacency[b2.book_id].add(b1.book_id)

    def related_books_bfs(self, start_book_id, depth: int = 1) -> list:
        """
        BFS traversal from a book node, exploring up to `depth` levels
        (1 = direct neighbours only, 2 = neighbours-of-neighbours, etc.)

        Time complexity: O(V + E) within the visited region.
        Space complexity: O(V) for the visited set + queue.
        """
        if start_book_id not in self.adjacency:
            return []

        visited = {start_book_id}
        queue = deque([(start_book_id, 0)])
        related = []

        while queue:
            node, level = queue.popleft()
            if level >= depth:
                continue
            for neighbour in self.adjacency[node]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    related.append(neighbour)
                    queue.append((neighbour, level + 1))

        return related


# ---------------------------------------------------------
# QUICK DEMO / TEST
# Uses the REAL Person 1 + Person 3 modules exactly as they exist in
# the repo. Run with:  python recommendation.py
# ---------------------------------------------------------
if __name__ == "__main__":
    from P1Data_layer import BookDatabase
    from user import UserProfileManager

    # --- Person 1's catalogue ---
    db = BookDatabase()
    db.load_sample_data()

    # --- Person 3's user + preferences ---
    manager = UserProfileManager()
    alice = manager.create_user("U001", "Alice Kamau", "alice@gmail.com")
    alice.add_preference("Sci-Fi", weight=5)
    alice.add_preference("J.R.R. Tolkien", weight=4)
    alice.add_preference("Fantasy", weight=3)

    print("--- Weighted Recommendations for Alice ---")
    recommender = WeightedRecommender()
    for book_id, title, score in recommender.recommend(db, alice, top_n=5):
        print(f"  [{book_id}] {title}: {score}")

    print("\n--- Graph-Based Related Books (BFS from 'Dune', id=1) ---")
    graph = BookGraph()
    graph.build_graph(db)
    related_ids = graph.related_books_bfs(1, depth=2)
    related_titles = [db.get_by_id(bid).title for bid in related_ids]
    print(" ", related_titles)
  
