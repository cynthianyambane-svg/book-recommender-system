# ============================================================
# main.py — Entry Point & Demo
# AI-Powered Book Recommendation System — Person 3
# Name: Bakhita Wanjiru | Student Number: 222593 | Date: 2026-06-29
#
# Run this file to see the full demo:
#   python main.py
# ============================================================

from book import Book
from user import UserProfileManager


def main():
    print("\n" + "═"*60)
    print("  PERSON 3 — User Profile & History Management")
    print("  AI-Powered Book Recommendation System")
    print("═"*60)

    # ─────────────────────────────────────────────────────────
    # 1. SET UP MANAGER & CREATE USERS
    # ─────────────────────────────────────────────────────────
    manager = UserProfileManager()

    print("\n📌 Creating users...")
    alice = manager.create_user("U001", "Alice Kamau",  "alice@gmail.com")
    bob   = manager.create_user("U002", "Bob Odhiambo", "bob@gmail.com")

    manager.list_all_users()

    # ─────────────────────────────────────────────────────────
    # 2. ALICE — ADD MANUAL PREFERENCES (Linked List)
    # ─────────────────────────────────────────────────────────
    print("📌 Alice sets her initial preferences:")
    alice.add_preference("Fantasy",      weight=4)
    alice.add_preference("Sci-Fi",       weight=3)
    alice.add_preference("Mystery",      weight=2)
    alice.add_preference("J.K. Rowling", weight=3)

    print("\n   Preference Linked List:")
    alice.preferences.display()

    # ─────────────────────────────────────────────────────────
    # 3. ALICE — BUILD READING LIST (Queue)
    # ─────────────────────────────────────────────────────────
    print("\n📌 Alice adds books to her reading list (Queue — FIFO):")

    b1 = Book("Dune",         "Frank Herbert",    "Sci-Fi")
    b2 = Book("The Hobbit",   "J.R.R. Tolkien",   "Fantasy")
    b3 = Book("Gone Girl",    "Gillian Flynn",     "Mystery")
    b4 = Book("Ender's Game", "Orson Scott Card",  "Sci-Fi")

    alice.add_to_reading_list(b1)
    alice.add_to_reading_list(b2)
    alice.add_to_reading_list(b3)
    alice.add_to_reading_list(b4)

    print("\n   Reading Queue:")
    alice.reading_list.display()

    # ─────────────────────────────────────────────────────────
    # 4. ALICE — START & FINISH BOOKS (Stack + Queue)
    # ─────────────────────────────────────────────────────────
    print("\n📌 Alice reads books one by one:")

    # Dequeue → read → push to history
    alice.start_next_book()                          # dequeue Dune
    alice.mark_as_read(b1, rating=5)                # push to stack, update prefs

    alice.start_next_book()                          # dequeue The Hobbit
    alice.mark_as_read(b2, rating=4)

    alice.start_next_book()                          # dequeue Gone Girl
    alice.mark_as_read(b3, rating=3)

    # ─────────────────────────────────────────────────────────
    # 5. READING HISTORY DISPLAY (Stack)
    # ─────────────────────────────────────────────────────────
    print("\n📌 Alice's reading history (Stack — most recent on TOP):")
    alice.history.display()

    # ─────────────────────────────────────────────────────────
    # 6. REMAINING READING LIST (Queue)
    # ─────────────────────────────────────────────────────────
    print("\n📌 Alice's remaining reading list:")
    alice.reading_list.display()

    # ─────────────────────────────────────────────────────────
    # 7. DICTIONARY LOOKUPS — O(1)
    # ─────────────────────────────────────────────────────────
    print("\n📌 Fast dictionary lookups (O(1)):")
    print(f"   Has Alice read 'Dune'?        → {alice.has_read('Dune')}")
    print(f"   Has Alice read 'Harry Potter'? → {alice.has_read('Harry Potter')}")
    print(f"   Alice's rating for 'Dune':    → {alice.get_rating('Dune')} ⭐")
    print(f"   Alice's rating for 'The Hobbit': → {alice.get_rating('The Hobbit')} ⭐")

    # ─────────────────────────────────────────────────────────
    # 8. EDGE CASES
    # ─────────────────────────────────────────────────────────
    print("\n📌 Edge case — try to add an already-read book:")
    alice.add_to_reading_list(b1)   # Dune already read

    print("\n📌 Edge case — try to add a duplicate to the queue:")
    alice.add_to_reading_list(b4)   # Ender's Game already in list
    alice.add_to_reading_list(b4)   # try again

    print("\n📌 Undo last read (Stack pop):")
    alice.undo_last_read()           # removes Gone Girl

    # ─────────────────────────────────────────────────────────
    # 9. PREFERENCES AFTER READING (Linked List)
    # ─────────────────────────────────────────────────────────
    print("\n📌 Updated preference linked list (auto-boosted from ratings):")
    alice.preferences.display()

    print("\n📌 Top 3 preferences (for Person 2 — Recommendation Engine):")
    for pref, weight in alice.get_top_preferences(3):
        bar = "█" * weight + "░" * (5 - weight)
        print(f"   {pref:<20} [{bar}] {weight}/5")

    print("\n📌 Genres Alice has read:")
    for genre, count in alice.history.get_genres_read().items():
        print(f"   {genre}: {count} book(s)")

    # ─────────────────────────────────────────────────────────
    # 10. BOB'S QUICK ACTIVITY
    # ─────────────────────────────────────────────────────────
    print("\n\n📌 Bob's activity:")
    bob.add_preference("Thriller", weight=4)

    b5 = Book("1984",                             "George Orwell",  "Dystopian")
    b6 = Book("Animal Farm",                      "George Orwell",  "Political")
    b7 = Book("The Girl with the Dragon Tattoo",  "Stieg Larsson",  "Thriller")

    bob.mark_as_read(b5, rating=5)
    bob.mark_as_read(b6, rating=4)
    bob.add_to_reading_list(b7)

    print("\n   Bob's reading queue:")
    bob.reading_list.display()

    # ─────────────────────────────────────────────────────────
    # 11. FULL PROFILE DISPLAY
    # ─────────────────────────────────────────────────────────
    alice.display_full_profile()
    bob.display_full_profile()

    # ─────────────────────────────────────────────────────────
    # 12. SUMMARY FOR RECOMMENDATION ENGINE (Person 2)
    # ─────────────────────────────────────────────────────────
    print("📌 Alice's summary — exported to Person 2 (Recommendation Algorithm):")
    summary = alice.get_summary()
    for key, val in summary.items():
        print(f"   {key:<22}: {val}")

    # ─────────────────────────────────────────────────────────
    # 13. JSON EXPORT (Persistence)
    # ─────────────────────────────────────────────────────────
    alice.export_to_json("alice_profile.json")
    bob.export_to_json("bob_profile.json")

    # ─────────────────────────────────────────────────────────
    # 14. ALL USERS SUMMARY (Person 5 — UI Integration)
    # ─────────────────────────────────────────────────────────
    print("\n📌 All user summaries (for Person 5 — UI & Integration):")
    all_summaries = manager.get_all_summaries()
    for s in all_summaries:
        print(f"\n   [{s['user_id']}] {s['name']}")
        print(f"   Books read: {s['books_read']} | Avg rating: {s['avg_rating']}")
        print(f"   Top preference: {s['top_preferences'][0] if s['top_preferences'] else 'None'}")

    print("\n\n✅ All done! Files generated: alice_profile.json, bob_profile.json\n")


if __name__ == "__main__":
    main()