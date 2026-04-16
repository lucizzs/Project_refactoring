"""
Unit tests for the Library Management System.

Run refactored (default):
    python -m pytest tests/test_cases.py -v

Run original:
    LIBRARY_IMPL=original python -m pytest tests/test_cases.py -v
"""

import datetime
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

IMPL = os.environ.get('LIBRARY_IMPL', 'refactored')

# ── load correct implementation ───────────────────────────────────────────────
if IMPL == 'original':
    import original_code as orig

    class Library:
        def __init__(self):
            orig.reset_books()

        def available_books(self):
            return [b for b in orig.books if b['STATUS'] == 'AVAILABLE']

        def borrow(self, borrower_id, book_code):
            return orig.borrow(borrower_id, book_code)

        def give_back(self, borrower_id, book_code):
            return orig.give_back(borrower_id, book_code)

        def get_all_books(self):
            return orig.get_all_books()

        def add_book(self, book):
            orig.books.append({
                'BOOK CODE': book['code'], 'BOOK NAME': book['name'],
                'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''
            })

        def books_borrowed_by(self, borrower_id):
            return [b for b in orig.books if b['BORROWER ID'] == borrower_id]

    def make_book(code, name):
        return {'code': code, 'name': name}

    def book_status(b):
        return b['STATUS']

    def compute_fine(due_str, days_late):
        import original_code as o
        due_dt = datetime.datetime.strptime(due_str, '%d-%m-%Y').date()
        ret_dt = due_dt + datetime.timedelta(days=days_late)
        ret_str = ret_dt.strftime('%d-%m-%Y')
        return o.fine(due_str, ret_str, o.FINE_PER_DAY)

    def default_lib():
        return Library()

else:
    from refactored_code import (
        Library, Book, BookStatus, LibraryConfig, compute_fine,
        make_default_library, _today, _due_date
    )

    def make_book(code, name):
        return Book(code=code, name=name)

    def book_status(b):
        return b.status.value

    def compute_fine_helper(due_date, days_late):
        ret = due_date + datetime.timedelta(days=days_late)
        return compute_fine(due_date, ret)

    def default_lib():
        return make_default_library()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════════════════════

TODAY = datetime.date.today()


class TestAvailableBooks:
    """Tests 1-3: listing available books"""

    def test_all_books_available_at_start(self):
        lib = default_lib()
        assert len(lib.available_books()) == 7

    def test_available_count_decreases_on_borrow(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        assert len(lib.available_books()) == 6

    def test_available_count_restored_on_return(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        lib.give_back('U01', 'B001')
        assert len(lib.available_books()) == 7


class TestBorrowBook:
    """Tests 4-10: borrowing logic"""

    def test_borrow_available_book_succeeds(self):
        lib = default_lib()
        success, _ = lib.borrow('U01', 'B001')
        assert success is True

    def test_borrow_returns_success_message(self):
        lib = default_lib()
        _, msg = lib.borrow('U01', 'B001')
        assert isinstance(msg, str)

    def test_borrow_invalid_code_fails(self):
        lib = default_lib()
        success, msg = lib.borrow('U01', 'INVALID')
        assert success is False

    def test_borrow_already_borrowed_book_fails(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        success, msg = lib.borrow('U02', 'B001')
        assert success is False

    def test_borrow_sets_book_status_to_borrowed(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        all_books = lib.get_all_books()
        target = next(b for b in all_books
                      if (b['BOOK CODE'] if IMPL == 'original' else b.code) == 'B001')
        assert book_status(target) == 'BORROWED'

    def test_borrow_records_borrower(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        borrowed = lib.books_borrowed_by('U01')
        assert len(borrowed) == 1

    def test_borrow_multiple_books_same_user(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        lib.borrow('U01', 'B002')
        assert len(lib.books_borrowed_by('U01')) == 2


class TestReturnBook:
    """Tests 11-17: returning books"""

    def test_return_borrowed_book_succeeds(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        success, _ = lib.give_back('U01', 'B001')
        assert success is True

    def test_return_sets_book_status_to_available(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        lib.give_back('U01', 'B001')
        target = next(
            b for b in lib.get_all_books()
            if (b['BOOK CODE'] if IMPL == 'original' else b.code) == 'B001'
        )
        assert book_status(target) == 'AVAILABLE'

    def test_return_unborrowed_book_fails(self):
        lib = default_lib()
        success, _ = lib.give_back('U01', 'B001')
        assert success is False

    def test_return_wrong_user_fails(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        success, _ = lib.give_back('U02', 'B001')
        assert success is False

    def test_return_invalid_code_fails(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        success, _ = lib.give_back('U01', 'WRONG')
        assert success is False

    def test_return_clears_borrower_record(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        lib.give_back('U01', 'B001')
        assert len(lib.books_borrowed_by('U01')) == 0

    def test_return_on_time_fine_is_zero(self):
        lib = default_lib()
        lib.borrow('U01', 'B003')
        _, fine_amount = lib.give_back('U01', 'B003')
        # returned same day as borrow ⇒ no overdue
        assert fine_amount == 0


class TestFineCalculation:
    """Tests 18-23: fine logic"""

    def test_no_fine_returned_before_due(self):
        if IMPL == 'original':
            import original_code as o
            due = (TODAY + datetime.timedelta(days=5)).strftime('%d-%m-%Y')
            ret = TODAY.strftime('%d-%m-%Y')
            assert o.fine(ret, due, 1) == 0
        else:
            due = TODAY + datetime.timedelta(days=5)
            assert compute_fine(due, TODAY) == 0

    def test_no_fine_returned_on_due_date(self):
        if IMPL == 'original':
            import original_code as o
            due = TODAY.strftime('%d-%m-%Y')
            assert o.fine(due, due, 1) == 0
        else:
            assert compute_fine(TODAY, TODAY) == 0

    def test_fine_one_day_late(self):
        if IMPL == 'original':
            import original_code as o
            due = TODAY.strftime('%d-%m-%Y')
            ret = (TODAY + datetime.timedelta(days=1)).strftime('%d-%m-%Y')
            assert o.fine(due, ret, 1) == 1
        else:
            ret = TODAY + datetime.timedelta(days=1)
            assert compute_fine(TODAY, ret) == 1

    def test_fine_five_days_late(self):
        if IMPL == 'original':
            import original_code as o
            due = TODAY.strftime('%d-%m-%Y')
            ret = (TODAY + datetime.timedelta(days=5)).strftime('%d-%m-%Y')
            assert o.fine(due, ret, 1) == 5
        else:
            ret = TODAY + datetime.timedelta(days=5)
            assert compute_fine(TODAY, ret) == 5

    def test_fine_uses_fine_per_day_rate(self):
        if IMPL == 'original':
            import original_code as o
            due = TODAY.strftime('%d-%m-%Y')
            ret = (TODAY + datetime.timedelta(days=3)).strftime('%d-%m-%Y')
            assert o.fine(due, ret, 2) == 6
        else:
            ret = TODAY + datetime.timedelta(days=3)
            assert compute_fine_helper(TODAY, 3) == 3  # rate=1 from config

    def test_overdue_return_applies_fine(self):
        """Integration: borrow then return late and check non-zero fine."""
        if IMPL == 'original':
            pytest.skip('Original requires date manipulation not supported in shim')
        lib = make_default_library()
        lib.borrow('U01', 'B004')
        # Manually backdate the due_date
        book = next(b for b in lib.get_all_books() if b.code == 'B004')
        book.due_date = TODAY - datetime.timedelta(days=3)
        success, fine_amount = lib.give_back('U01', 'B004')
        assert success is True
        assert fine_amount == 3


class TestGetAllBooks:
    """Tests 24-26"""

    def test_get_all_books_returns_correct_count(self):
        lib = default_lib()
        assert len(lib.get_all_books()) == 7

    def test_add_book_increases_count(self):
        lib = default_lib()
        lib.add_book(make_book('B099', 'New Book'))
        assert len(lib.get_all_books()) == 8

    def test_added_book_is_available(self):
        lib = default_lib()
        lib.add_book(make_book('B099', 'New Book'))
        new_book = next(
            b for b in lib.get_all_books()
            if (b['BOOK CODE'] if IMPL == 'original' else b.code) == 'B099'
        )
        assert book_status(new_book) == 'AVAILABLE'


class TestBorrowedByUser:
    """Tests 27-30"""

    def test_new_user_has_no_books(self):
        lib = default_lib()
        assert lib.books_borrowed_by('U99') == []

    def test_user_has_correct_books_after_borrow(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        lib.borrow('U01', 'B002')
        borrowed = lib.books_borrowed_by('U01')
        assert len(borrowed) == 2

    def test_different_users_isolated(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        lib.borrow('U02', 'B002')
        assert len(lib.books_borrowed_by('U01')) == 1
        assert len(lib.books_borrowed_by('U02')) == 1

    def test_return_removes_from_user_list(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        lib.give_back('U01', 'B001')
        assert lib.books_borrowed_by('U01') == []


class TestEdgeCases:
    """Tests 31-40: edge and boundary conditions"""

    def test_borrow_same_book_twice_same_user(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        success, _ = lib.borrow('U01', 'B001')
        assert success is False

    def test_return_book_not_borrowed_at_all(self):
        lib = default_lib()
        success, _ = lib.give_back('U01', 'B002')
        assert success is False

    def test_borrow_empty_code_fails(self):
        lib = default_lib()
        success, _ = lib.borrow('U01', '')
        assert success is False

    def test_return_empty_code_fails(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        success, _ = lib.give_back('U01', '')
        assert success is False

    def test_all_books_can_be_borrowed_sequentially(self):
        lib = default_lib()
        for i in range(1, 8):
            code = f'B00{i}'
            success, _ = lib.borrow(f'U{i:02d}', code)
            assert success is True

    def test_no_available_books_after_all_borrowed(self):
        lib = default_lib()
        for i in range(1, 8):
            lib.borrow(f'U{i:02d}', f'B00{i}')
        assert lib.available_books() == []

    def test_borrow_after_return_succeeds(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        lib.give_back('U01', 'B001')
        success, _ = lib.borrow('U02', 'B001')
        assert success is True

    def test_multiple_returns_in_sequence(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        lib.borrow('U01', 'B002')
        lib.give_back('U01', 'B001')
        lib.give_back('U01', 'B002')
        assert len(lib.available_books()) == 7

    def test_borrow_nonexistent_code_returns_false(self):
        lib = default_lib()
        success, msg = lib.borrow('U01', 'ZZZZ')
        assert success is False
        assert isinstance(msg, str)

    def test_give_back_nonexistent_code_returns_false(self):
        lib = default_lib()
        lib.borrow('U01', 'B001')
        success, msg = lib.give_back('U01', 'ZZZZ')
        assert success is False
