import unittest
import json
import errors
import random
from data import Book
from datetime import datetime


def mocked_get_now():
    return datetime(2020, 1, 1, 10, 10, 10)


class TestCard(unittest.TestCase):

    def setUp(self):
        self.path = "test_book_standard.json"
        with open(self.path, "w") as handle:
            json.dump([], handle)
        self.book = Book(path=self.path)
        with open(self.path, "r") as handle:
            self.data = json.load(handle)

    def tearDown(self):
        with open(self.path, "w") as handle:
            json.dump(self.data, handle, indent=2)

    def test_add_common(self):
        note = {"name": "Testname", "surname": "Testsurname", "phone": "88126215634", "birth_date": "01.01.1991"}
        self.book._add(note=note)
        self.assertTrue(self.book._exists(note=note))

    def test_add_existing(self):
        note = {"name": "Testname", "surname": "Testsurname", "phone": "88126215634", "birth_date": "01.01.1991"}
        self.book._add(note=note)
        with self.assertRaises(errors.DuplicateNote):
            self.book._add(note=note)

    def test_edit_name(self):
        note = {"name": "Testname", "surname": "Testsurname", "phone": "88126215634", "birth_date": "01.01.1991"}
        self.book._add(note=note)
        self.book._edit(_id=-1, to_edit={'name': "Editedname"})
        self.assertTrue(self.book._get(note_id=-1)['name'] == 'Editedname')

    def test_edit_all(self):
        note = {"name": "Testname", "surname": "Testsurname", "phone": "88126215634", "birth_date": "01.01.1991"}
        self.book._add(note=note)
        edited = {"name": "Editedname", "surname": "Editedsurname", "phone": "89361954672", "birth_date": "12.12.2009"}
        self.book._edit(_id=-1, to_edit=edited)
        self.assertDictEqual(self.book._get(note_id=-1), edited)

    def test_age(self):
        note = {"name": "Testname", "surname": "Testsurname", "phone": "88126215634", "birth_date": "01.01.1991"}
        self.book._add(note=note)
        self.assertEqual(self.book._age(note_id=-1)['years'], 29)

    def test_get(self):
        note = {"name": "Testname", "surname": "Testsurname", "phone": "88126215634", "birth_date": "01.01.1991"}
        self.book._add(note=note)
        self.assertDictEqual(self.book._get(note_id=-1), note)

    def test_get_all(self):
        with open(self.path, "r") as handle:
            read_json = json.load(handle)
            self.assertListEqual(read_json, self.book._get_all())

    def test_gap(self):
        self.assertEqual(self.book._gap(date=(datetime.now().day, datetime.now().month, datetime.now().year)), 365)

    def test_get_birthday_in(self):
        with open(self.path, "w") as handle:
            json.dump([], handle, indent=2)
        correct = []
        for i in range(10):
            day = (datetime.now().day + random.randint(0, 10)) % 30 + 1
            month = (datetime.now().month - random.randint(0, 1))
            date = ''.join(f"{day}.{month}.{datetime.now().year}")
            note = {"name": f"Testname_{i}",
                    "surname": f"Testsurname_{i}",
                    "phone": f"8812621563{i}",
                    "birth_date": date}
            if datetime.now().month == month:
                correct.append(note['name'])
            self.book._add(note=note)
        self.assertEqual(set([got['name'] for got in self.book.get_birthday_in(30)]), set(correct))

    def test_is_date_correct(self):
        self.assertTrue(self.book.is_date('01.01.2001'))

    def test_is_date_incorrect(self):
        self.assertFalse(self.book.is_date('56.01.2001'))

    def test_is_date_nodate(self):
        self.assertFalse(self.book.is_date('abc'))

    def test_phone_correct_1(self):
        self.assertEqual(self.book.correct_phone("+71234567890"), "81234567890")

    def test_phone_correct_2(self):
        self.assertEqual(self.book.correct_phone("+81234567890"), "81234567890")

    def test_phone_correct_3(self):
        self.assertEqual(self.book.correct_phone("71234567890"), "81234567890")

    def test_phone_incorrect_1(self):
        self.assertEqual(self.book.correct_phone("+712345678900"), "phone_error")

    def test_phone_incorrect_2(self):
        self.assertEqual(self.book.correct_phone("+71234"), "phone_error")

    def test_phone_incorrect_3(self):
        self.assertEqual(self.book.correct_phone("abcd"), "phone_error")

    def test_is_name_correct(self):
        self.assertTrue(self.book.is_name("Alex"))

    def test_is_name_correct_digits(self):
        self.assertTrue(self.book.is_name("Alex123"))

    def test_is_name_correct_spaces(self):
        self.assertTrue(self.book.is_name("Al ex"))

    def test_is_name_correct_short(self):
        self.assertTrue(self.book.is_name("Al"))

    def test_is_name_correct_spaces_digits(self):
        self.assertTrue(self.book.is_name("Al ex 34"))

    def test_is_name_incorrect(self):
        self.assertFalse(self.book.is_name("543"))

    def test_is_name_incorrect_lower(self):
        self.assertFalse(self.book.is_name("alex"))

    def test_is_name_incorrect_upper(self):
        self.assertFalse(self.book.is_name("ALEX"))

    def test_is_name_incorrect_middle_upper(self):
        self.assertFalse(self.book.is_name("AlEx"))

    def test_is_name_incorrect_empty(self):
        self.assertFalse(self.book.is_name(""))

    def test_is_name_incorrect_single(self):
        self.assertFalse(self.book.is_name("A"))

    def test_search_name_strict(self):
        for i in range(10):
            day = (datetime.now().day + random.randint(0, 10)) % 30 + 1
            month = (datetime.now().month - random.randint(0, 1))
            date = ''.join(f"{day}.{month}.{datetime.now().year}")
            note = {"name": f"Testname_{i}",
                    "surname": f"Testsurname_{i}",
                    "phone": f"8812621563{i}",
                    "birth_date": date}
            self.book._add(note=note)
        self.assertEqual(self.book.search(name='Testname_3', is_strict=True), 3)

    def test_search_surname_strict(self):
        for i in range(10):
            day = (datetime.now().day + random.randint(0, 10)) % 30 + 1
            month = (datetime.now().month - random.randint(0, 1))
            date = ''.join(f"{day}.{month}.{datetime.now().year}")
            note = {"name": f"Testname_{i}",
                    "surname": f"Testsurname_{i}",
                    "phone": f"8812621563{i}",
                    "birth_date": date}
            self.book._add(note=note)
        self.assertEqual(self.book.search(surname='Testsurname_2', is_strict=True), 2)

    def test_search_phone_strict(self):
        for i in range(10):
            day = (datetime.now().day + random.randint(0, 10)) % 30 + 1
            month = (datetime.now().month - random.randint(0, 1))
            date = ''.join(f"{day}.{month}.{datetime.now().year}")
            note = {"name": f"Testname_{i}",
                    "surname": f"Testsurname_{i}",
                    "phone": f"8812621563{i}",
                    "birth_date": date}
            self.book._add(note=note)
        self.assertEqual(self.book.search(phone_number='88126215632', is_strict=True), 2)

    def test_search_date_strict(self):
        _date = ''
        for i in range(10):
            day = (datetime.now().day + random.randint(0, 10)) % 30 + 1
            month = (datetime.now().month - random.randint(0, 1))
            date = ''.join(f"{day}.{month}.{datetime.now().year}")
            if i == 2:
                _date = date
            note = {"name": f"Testname_{i}",
                    "surname": f"Testsurname_{i}",
                    "phone": f"8812621563{i}",
                    "birth_date": date}
            self.book._add(note=note)
        self.assertEqual(self.book.search(date=_date, is_strict=True), 2)

    def test_search_name_fuzzy(self):
        for i in range(10):
            day = (datetime.now().day + random.randint(0, 10)) % 30 + 1
            month = (datetime.now().month - random.randint(0, 1))
            date = ''.join(f"{day}.{month}.{datetime.now().year}")
            note = {"name": f"Testname_{i}",
                    "surname": f"Testsurname_{i}",
                    "phone": f"8812621563{i}",
                    "birth_date": date}
            note_2 = {"name": f"Nonono_{i}",
                    "surname": f"Testsurname_{i}",
                    "phone": f"8812621563{i}",
                    "birth_date": date}
            self.book._add(note=note)
            self.book._add(note=note_2)
        self.assertEqual(self.book.search(name='Testname_1', is_strict=False, output_range=3), [2, 0, 4])
