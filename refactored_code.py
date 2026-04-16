# Library Management System - Refactored Code
# Applies 10 refactoring techniques to the legacy version from:
# https://github.com/Uthpal-p/Library-Management-system-using-Python

# ─── REFACTORING #1: Move Import to Top Level ────────────────────────────────
# Technique: Move Import to Top Level
# Original had `import datetime` and `from datetime import datetime` inside
# function bodies (getDate and fine), which re-executes on every call and
# hides dependencies from readers.
import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ─── REFACTORING #2: Replace Magic Number with Symbolic Constant ─────────────
# Technique: Replace Magic Number with Named Constant
# The two module-level "constants" were already named but their VALUES
# appeared inline in string operations and fine logic.
# Centralised into a single config object.
class LibraryConfig:
    FINE_PER_DAY: int = 1       # Rupees per overdue day
    BORROW_PERIOD_DAYS: int = 15
    DATE_FORMAT: str = '%d-%m-%Y'


# ─── REFACTORING #3: Replace Type Code with Enum ─────────────────────────────
# Technique: Replace Type Code with Enum
# Original used raw strings 'AVAILABLE' / 'BORROWED' — a typo silently passes.
class BookStatus(Enum):
    AVAILABLE = 'AVAILABLE'
    BORROWED  = 'BORROWED'


# ─── REFACTORING #4: Introduce Value Object ──────────────────────────────────
# Technique: Introduce Value Object (Extract Class)
# Original stored books as plain dicts with string keys.
# A dataclass gives type safety, IDE completion, and clear schema.
@dataclass
class Book:
    code: str
    name: str
    status: BookStatus = BookStatus.AVAILABLE
    borrower_id: str = ''
    due_date: Optional[datetime.date] = None

    def is_available(self) -> bool:
        return self.status == BookStatus.AVAILABLE

    def is_borrowed_by(self, borrower_id: str) -> bool:
        return self.status == BookStatus.BORROWED and self.borrower_id == borrower_id


# ─── REFACTORING #5: Replace String Date with datetime Object ────────────────
# Technique: Replace Primitive with Object
# Original serialised dates as 'dd-mm-yyyy' strings and parsed them back
# for every fine calculation. Storing datetime.date objects eliminates
# the fragile manual concatenation and repeated parsing.
def _today() -> datetime.date:
    return datetime.date.today()

def _due_date() -> datetime.date:
    return _today() + datetime.timedelta(days=LibraryConfig.BORROW_PERIOD_DAYS)


# ─── REFACTORING #6: Extract Method — compute_fine ───────────────────────────
# Technique: Extract Method
# The fine calculation was an isolated block of date arithmetic buried inside
# give_back(). Extracting it makes it independently testable.
def compute_fine(due: datetime.date, returned: datetime.date) -> int:
    overdue_days = (returned - due).days
    return max(0, overdue_days * LibraryConfig.FINE_PER_DAY)


# ─── REFACTORING #7: Replace Global State with Encapsulated Class ────────────
# Technique: Encapsulate Variable (Replace Global with Class)
# The original used a module-level `books` list mutated by free functions.
# Every test had to call reset_books() to undo side-effects.
# Encapsulating state in a class makes each instance independent.
class Library:
    def __init__(self, books: list[Book] = None):
        # ─── REFACTORING #8: Rename Variables ────────────────────────────────
        # Technique: Rename Variable
        # a, b, d1, d2, diff, Fine, l, x, col → descriptive names throughout.
        self._books: list[Book] = books if books is not None else []

    # ── private helpers ───────────────────────────────────────────────────────
    def _find_by_code(self, code: str) -> Optional[Book]:
        return next((b for b in self._books if b.code == code), None)

    # ─── REFACTORING #9: Remove Redundant Conditional ────────────────────────
    # Technique: Remove Redundant Conditional
    # Original give_back() had:
    #   if borrower_id not in l:   ...
    #   elif borrower_id in l:     ...   ← always True, 'else' is dead code
    # Replaced with a simple if/else.
    def _books_borrowed_by(self, borrower_id: str) -> list[Book]:
        return [b for b in self._books if b.is_borrowed_by(borrower_id)]

    # ── public API ────────────────────────────────────────────────────────────
    def available_books(self) -> list[Book]:
        return [b for b in self._books if b.is_available()]

    # ─── REFACTORING #10: Replace Nested Recursive Validator with Loop ────────
    # Technique: Replace Nested Function / Recursion with Iteration
    # Original had a nested function `validd()` that called itself on bad input,
    # creating infinite recursion risk. Replaced with a simple boolean guard.
    def borrow(self, borrower_id: str, book_code: str) -> tuple[bool, str]:
        book = self._find_by_code(book_code)
        if book is None:
            return False, 'Invalid book code.'
        if not book.is_available():
            return False, 'This book is already borrowed.'
        book.status = BookStatus.BORROWED
        book.borrower_id = borrower_id
        book.due_date = _due_date()
        return True, 'Book borrowed successfully.'

    # ─── REFACTORING #9 continued: Eliminate Duplicate Borrower Lookup ───────
    # Technique: Consolidate Duplicate Code
    # Both borrow() and give_back() repeated the same borrower-lookup pattern.
    # Extracted into _books_borrowed_by() above.
    def give_back(self, borrower_id: str, book_code: str) -> tuple[bool, int | str]:
        borrowed_by_user = self._books_borrowed_by(borrower_id)
        if not borrowed_by_user:
            return False, 'No books have been borrowed!'
        book = next((b for b in borrowed_by_user if b.code == book_code), None)
        if book is None:
            return False, 'Please enter valid book code.'
        return_date = _today()
        late_fine = compute_fine(book.due_date, return_date)
        book.status = BookStatus.AVAILABLE
        book.borrower_id = ''
        book.due_date = None
        return True, late_fine

    def get_all_books(self) -> list[Book]:
        return list(self._books)

    def add_book(self, book: Book) -> None:
        self._books.append(book)

    def books_borrowed_by(self, borrower_id: str) -> list[Book]:
        return self._books_borrowed_by(borrower_id)


# ── factory helper used by tests ──────────────────────────────────────────────
def make_default_library() -> Library:
    return Library([
        Book('B001', 'Algorithms'),
        Book('B002', 'Sherlock Holmes'),
        Book('B003', 'Django'),
        Book('B004', 'HTML Notes'),
        Book('B005', 'Python Notes'),
        Book('B006', 'C++ Notes'),
        Book('B007', 'Java Notes'),
    ])
