

from flask import Flask, render_template, request, jsonify

from search_filter_module import SearchFilterModule, Book
from book import Book as UserBook
from user import UserProfileManager
import P1Data_layer
from reccomendation import WeightedRecommender, BookGraph

app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="")
module = SearchFilterModule()
user_manager = UserProfileManager()
p1_db = P1Data_layer.BookDatabase()
recommender = WeightedRecommender()
book_graph = BookGraph()

# Metadata shown in the UI next to results, so the grader/demo audience
# sees exactly which data structure / algorithm handled each query.
SEARCH_META = {
    "title": {
        "label": "Exact title match",
        "structure": "Binary Search Tree",
        "complexity": "O(log n) average, O(n) worst case",
    },
    "title_prefix": {
        "label": "Title starts with...",
        "structure": "Binary Search Tree (prefix walk)",
        "complexity": "O(log n) to locate + O(k) to collect k matches",
    },
    "genre": {
        "label": "Genre filter",
        "structure": "Hash Table (dict bucket by genre)",
        "complexity": "O(1) average",
    },
    "author": {
        "label": "Author (hash lookup)",
        "structure": "Hash Table (dict bucket by author)",
        "complexity": "O(1) average",
    },
    "author_sort": {
        "label": "Author (sort + binary search)",
        "structure": "Merge Sort + Binary Search",
        "complexity": "O(n log n) to sort (cached) + O(log n) per query",
    },
}


def _seed_sample_books():
    sample = [
        ("B001", "The Hobbit", "J.R.R. Tolkien", "Fantasy"),
        ("B002", "The Fellowship of the Ring", "J.R.R. Tolkien", "Fantasy"),
        ("B003", "Dune", "Frank Herbert", "Sci-Fi"),
        ("B004", "Foundation", "Isaac Asimov", "Sci-Fi"),
        ("B005", "I, Robot", "Isaac Asimov", "Sci-Fi"),
        ("B006", "1984", "George Orwell", "Dystopian"),
        ("B007", "Animal Farm", "George Orwell", "Dystopian"),
        ("B008", "Brave New World", "Aldous Huxley", "Dystopian"),
        ("B009", "The Hunger Games", "Suzanne Collins", "Dystopian"),
        ("B010", "Children of Dune", "Frank Herbert", "Sci-Fi"),
    ]
    for book_id, title, author, genre in sample:
        module.add_book(Book(book_id, title, author, genre))


_seed_sample_books()


def _seed_sample_users():
    alice = user_manager.create_user("U001", "Alice Kamau", "alice@gmail.com")
    bob = user_manager.create_user("U002", "Bob Odhiambo", "bob@gmail.com")
    alice.add_preference("Fantasy", weight=4)
    alice.add_preference("Sci-Fi", weight=3)
    bob.add_preference("Dystopian", weight=3)
    bob.add_preference("Mystery", weight=2)


def _seed_p1_database():
    p1_db.load_sample_data()
    book_graph.build_graph(p1_db)


_seed_sample_users()
_seed_p1_database()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/catalog")
def catalog():
    """Full catalogue, sorted by title via BST in-order traversal."""
    books = module.list_all_sorted_by_title()
    return jsonify({"books": [b.to_dict() for b in books], "count": len(books)})


@app.route("/api/users")
def list_users():
    users = user_manager.get_all_summaries()
    return jsonify({"users": users})


@app.route("/api/users/<user_id>")
def get_user(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"user": user.get_summary()})


@app.route("/api/users/<user_id>/reading_list")
def get_user_reading_list(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"reading_list": list(user.reading_list._queue)})


@app.route("/api/users/<user_id>/history")
def get_user_history(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"history": user.history.get_all()})


@app.route("/api/users/<user_id>/preferences")
def get_user_preferences(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"preferences": user.preferences.to_list()})


@app.route("/api/users/<user_id>/enqueue", methods=["POST"])
def enqueue_book(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    data = request.get_json(force=True)
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    genre = (data.get("genre") or "").strip()
    if not title or not author or not genre:
        return jsonify({"error": "title, author and genre are required"}), 400

    book = UserBook(title, author, genre)
    user.add_to_reading_list(book)
    return jsonify({"reading_list": list(user.reading_list._queue)}), 201


@app.route("/api/users/<user_id>/mark_read", methods=["POST"])
def mark_book_read(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    data = request.get_json(force=True)
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    genre = (data.get("genre") or "").strip()
    rating = data.get("rating")
    if not title or not author or not genre or not isinstance(rating, int):
        return jsonify({"error": "title, author, genre and integer rating are required"}), 400

    book = UserBook(title, author, genre)
    user.mark_as_read(book, rating)
    return jsonify({"last_read": user.get_last_read(), "history": user.history.get_all()}), 201


@app.route("/api/users/<user_id>/undo", methods=["POST"])
def undo_last_read(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    user.undo_last_read()
    return jsonify({"history": user.history.get_all()})


@app.route("/api/p1/catalog")
def p1_catalog():
    return jsonify({"books": [b.to_dict() for b in p1_db.get_all_books()]})


@app.route("/api/users/<user_id>/recommendations")
def get_user_recommendations(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    recs = recommender.recommend(p1_db, user, top_n=6)
    return jsonify({
        "recommendations": [
            {"book_id": bid, "title": title, "score": score}
            for bid, title, score in recs
        ]
    })


@app.route("/api/users/<user_id>/related_books")
def get_related_books(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    last_read = user.get_last_read()
    if not last_read:
        return jsonify({"related_books": []})

    book = p1_db.get_by_title(last_read.get("title") or "")
    if not book:
        return jsonify({"related_books": []})

    related_ids = book_graph.related_books_bfs(book.book_id, depth=2)
    related_books = [p1_db.get_by_id(bid) for bid in related_ids if p1_db.get_by_id(bid)]
    return jsonify({"related_books": [b.to_dict() for b in related_books]})


@app.route("/api/books", methods=["POST"])
def add_book():
    """CREATE — insert a new book into the BST and hash indexes."""
    data = request.get_json(force=True)
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    genre = (data.get("genre") or "").strip()
    if not title or not author or not genre:
        return jsonify({"error": "title, author and genre are all required"}), 400

    book_id = f"B{len(module.list_all_sorted_by_title()) + 1:03d}"
    book = Book(book_id, title, author, genre)
    module.add_book(book)
    return jsonify({"book": book.to_dict()}), 201


@app.route("/api/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    """DELETE — remove a book by title (BST delete + hash cleanup)."""
    data = request.get_json(force=True) if request.data else {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title required to delete"}), 400
    removed = module.remove_book(title)
    if not removed:
        return jsonify({"error": "book not found"}), 404
    return jsonify({"deleted": True})


@app.route("/api/search")
def search():
    """
    Single search entry point used by the UI.
    Query params: type = title | title_prefix | genre | author | author_sort
                  q    = the search text
    """
    search_type = request.args.get("type", "title")
    query = (request.args.get("q") or "").strip()

    if not query:
        return jsonify({"error": "missing query"}), 400

    if search_type == "title":
        result = module.search_by_title(query)
        results = [result] if result else []
    elif search_type == "title_prefix":
        results = module.search_by_title_prefix(query)
    elif search_type == "genre":
        results = module.filter_by_genre(query)
    elif search_type == "author":
        results = module.search_by_author(query)
    elif search_type == "author_sort":
        results = module.search_by_author_via_sort(query)
    else:
        return jsonify({"error": f"unknown search type '{search_type}'"}), 400

    meta = SEARCH_META.get(search_type, {})
    return jsonify({
        "query": query,
        "search_type": search_type,
        "meta": meta,
        "results": [b.to_dict() for b in results],
        "count": len(results),
        "history": module.history_status_for_json(),
    })


@app.route("/api/history")
def history():
    return jsonify(module.history_status_for_json())


@app.route("/api/history/back", methods=["POST"])
def history_back():
    entry = module.history_back()
    entry_dict = entry.to_dict() if entry else None
    if entry_dict:
        entry_dict["meta"] = SEARCH_META.get(entry.search_type, {})
    return jsonify({
        "entry": entry_dict,
        "history": module.history_status_for_json(),
    })


@app.route("/api/history/forward", methods=["POST"])
def history_forward():
    entry = module.history_forward()
    entry_dict = entry.to_dict() if entry else None
    if entry_dict:
        entry_dict["meta"] = SEARCH_META.get(entry.search_type, {})
    return jsonify({
        "entry": entry_dict,
        "history": module.history_status_for_json(),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
