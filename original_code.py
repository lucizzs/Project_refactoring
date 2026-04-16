# Library Management System - Original (Legacy) Code
# Source: https://github.com/Uthpal-p/Library-Management-system-using-Python (0 stars)
# Adapted: CSV/pandas replaced with in-memory dicts to allow unit testing.
# All original code smells are preserved faithfully.

# SMELL #1: Magic numbers used as module-level "constants" but still repeated inline
FINE_PER_DAY = 1
BORROW_PERIOD = 15

import datetime

# SMELL #2: Global mutable state — entire "database" is a module-level list
books = [
    {'BOOK CODE': 'B001', 'BOOK NAME': 'Algorithms',      'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
    {'BOOK CODE': 'B002', 'BOOK NAME': 'Sherlock Holmes',  'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
    {'BOOK CODE': 'B003', 'BOOK NAME': 'Django',           'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
    {'BOOK CODE': 'B004', 'BOOK NAME': 'HTML Notes',       'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
    {'BOOK CODE': 'B005', 'BOOK NAME': 'Python Notes',     'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
    {'BOOK CODE': 'B006', 'BOOK NAME': 'C++ Notes',        'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
    {'BOOK CODE': 'B007', 'BOOK NAME': 'Java Notes',       'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
]


# SMELL #3: Import inside function — re-imports on every call
def getDate(a):
    import datetime                         # import inside function
    now = datetime.datetime.now() + datetime.timedelta(days=a)
    # SMELL #4: Inefficient string concatenation instead of single format string
    return now.strftime('%d') + '-' + now.strftime('%m') + '-' + now.strftime('%Y')


# SMELL #5: Poor variable names — a, b, d1, d2, diff
# SMELL #6: Inconsistent naming — local var 'Fine' uses CamelCase, rest is snake_case
def fine(a, b, cost_per_day):
    from datetime import datetime           # SMELL #3 again: import inside function
    date_format = '%d-%m-%Y'
    d1 = datetime.strptime(a, date_format)
    d2 = datetime.strptime(b, date_format)
    diff = d2 - d1
    Fine = diff.days * cost_per_day        # SMELL #6: CamelCase local variable
    if Fine < 0:
        return 0
    else:
        return Fine


# SMELL #7: Function name 'aval' collides with local variable 'aval' inside itself
def aval():
    print('The available books are:')
    aval = []                               # local var shadows the function name
    for i in range(len(books)):
        if books[i]['STATUS'] == 'AVAILABLE':
            aval.append(books[i]['BOOK NAME'])
    print(aval)
    return aval


# SMELL #8: Nested function used as recursive input validator — infinite recursion risk
# SMELL #9: Duplicate code — same borrower-lookup pattern repeated verbatim in give_back()
def borrow(borrower_id, book_code):
    # SMELL #5: l, x — meaningless names
    l = [b['BORROWER ID'] for b in books]
    if borrower_id in l:
        print('The borrowed books are:')
        for x in [i for i, v in enumerate(l) if v == borrower_id]:
            print(books[x])

    # SMELL #8: nested validator (in original it called itself recursively)
    def validd(code):
        all_codes = [b['BOOK CODE'] for b in books]
        if code not in all_codes:
            print('Please enter valid book code.')
            return False
        return True

    if not validd(book_code):
        return False, 'Invalid book code'

    # SMELL #5: col — cryptic name
    col = next((i for i, b in enumerate(books) if b['BOOK CODE'] == book_code), None)
    if books[col]['STATUS'] == 'BORROWED':
        return False, 'This book is already borrowed.'
    else:
        books[col]['STATUS'] = 'BORROWED'
        books[col]['BORROWER ID'] = borrower_id
        books[col]['DUE DATE'] = getDate(BORROW_PERIOD)
        print(books[col])
        print('Book borrowed successfully.')
        return True, 'Book borrowed successfully.'


# SMELL #9: Duplicate borrower-lookup (copy-paste from borrow())
# SMELL #10: Redundant elif — the elif condition is always True when the if was False
def give_back(borrower_id, book_code):
    l = [b['BORROWER ID'] for b in books]  # SMELL #9: same pattern as in borrow()
    if borrower_id not in l:
        return False, 'No books have been borrowed!'
    elif borrower_id in l:                  # SMELL #10: always True here; else suffices
        borrowed = [books[i] for i, v in enumerate(l) if v == borrower_id]
        print('The borrowed books are:')
        for b in borrowed:
            print(b)

        valid_codes = [b['BOOK CODE'] for b in borrowed]
        if book_code not in valid_codes:
            return False, 'Please enter valid book code.'

        col = next((i for i, b in enumerate(books) if b['BOOK CODE'] == book_code), None)
        books[col]['STATUS'] = 'AVAILABLE'
        today = getDate(0)
        late_fine = fine(books[col]['DUE DATE'], today, FINE_PER_DAY)
        books[col]['BORROWER ID'] = ''
        books[col]['DUE DATE'] = ''
        print('Book returned successfully.')
        print('LATE SUBMISSION FINE:', late_fine, 'Rupees')
        return True, late_fine
    else:
        return False, 'Unknown error'


def get_all_books():
    return books


def reset_books():
    """Reset global state between tests — the need for this helper IS the smell."""
    global books
    books = [
        {'BOOK CODE': 'B001', 'BOOK NAME': 'Algorithms',     'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
        {'BOOK CODE': 'B002', 'BOOK NAME': 'Sherlock Holmes', 'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
        {'BOOK CODE': 'B003', 'BOOK NAME': 'Django',          'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
        {'BOOK CODE': 'B004', 'BOOK NAME': 'HTML Notes',      'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
        {'BOOK CODE': 'B005', 'BOOK NAME': 'Python Notes',    'STATUS': 'AVAILABLE', 'BORROWER ID': '', 'DUE DATE': ''},
    ]
