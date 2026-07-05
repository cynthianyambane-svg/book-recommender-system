

from flask import Flask, render_template, request, jsonify

from search_filter_module import SearchFilterModule, Book

app = Flask(__name__)
module = SearchFilterModule()

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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/catalog")
def catalog():
    """Full catalogue, sorted by title via BST in-order traversal."""
    books = module.list_all_sorted_by_title()
    return jsonify({"books": [b.to_dict() for b in books], "count": len(books)})


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
    _seed_sample_books()
    app.run(debug=True, port=5000)
