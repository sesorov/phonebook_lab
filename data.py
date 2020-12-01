import warnings
import json
import os
import re
from additional import Text, GColor
from datetime import datetime
from errors import DuplicateNote
warnings.filterwarnings("ignore")  # FuzzyWuzzy argues on SequenceMatcher using instead of python-Levenshtein
from fuzzywuzzy import fuzz


class Book:

    def __init__(self, path: str = None):
        self.path = "book.json"
        # self.operations = ["ADD", "EDIT", "DELETE", "NEXT_BIRTHDAY"]
        if path is not None:
            self.path = path
        else:
            if not os.path.isfile(self.path) or os.stat(self.path).st_size == 0:
                with open(self.path, "w") as handle:
                    json.dump([], handle)

    def _add(self, note: dict) -> None:
        """ Adds a single note to a Book. """
        if not self._exists(note):
            with open(self.path, "r") as handle:
                data = json.load(handle)
                data.append(note)
            with open(self.path, "w") as handle:
                json.dump(data, handle, indent=2)
        else:
            raise DuplicateNote

    def _exists(self, note):
        """ Returns true if a note already exists in a Book, false if not. """
        with open(self.path, "r") as handle:
            data = json.load(handle)
            for book_note in data:
                if book_note["name"] == note["name"] and book_note["surname"] == note["surname"]:
                    return True
            return False

    def _del(self, note_id: int):
        """ Deletes a note by its ID from Book. """
        with open(self.path, "r") as handle:
            data = json.load(handle)
            data.pop(note_id)
        with open(self.path, "w") as handle:
            json.dump(data, handle, indent=2)

    def _edit(self, _id: int, to_edit: dict):
        """ Applies all to_edit dict's keys to a note by ID to edit its values. """
        with open(self.path, "r") as handle:
            data = json.load(handle)
            for key, value in to_edit.items():
                data[_id][key] = value
        with open(self.path, "w") as handle:
            json.dump(data, handle, indent=2)

    def _age(self, note_id: int) -> dict:
        """ Returns age in person via a dict with two keys: years and months. """
        with open(self.path, "r") as handle:
            birth_date = tuple(map(int, json.load(handle)[note_id]['birth_date'].split('.')))
            days_amount = datetime.now() - datetime(day=int(birth_date[0]),
                                                    month=int(birth_date[1]),
                                                    year=int(birth_date[2]))
            return {'years': days_amount.days // 365, 'months': (days_amount.days % 365) // 30}

    def _get(self, note_id: int) -> dict:
        """ Returns a single note by its ID. """
        with open(self.path, "r") as handle:
            data = json.load(handle)
            return data[note_id]

    def _get_all(self):
        """ Returns all notes. """
        with open(self.path, "r") as handle:
            return json.load(handle)

    def _gap(self, date: tuple):
        """ Returns an amount of days remaining before a given date. """
        gap = (datetime(day=date[0], month=date[1], year=datetime.now().year) - datetime.now()).days
        if gap < 0:
            return 365 + gap + 1
        else:
            return gap + 1

    def get_birthday_in(self, days: int = 30):
        """ Returns all notes whose birthday will be within a given amount of days. """
        with open(self.path, "r") as handle:
            data = json.load(handle)
            near = []
            for id, note in enumerate(data):
                try:
                    date = tuple(map(int, note['birth_date'].split('.')))
                except KeyError:
                    continue
                note["id"] = id
                if self._gap(date=date) <= days:
                    note["gap"] = self._gap(date=date)
                    near.append(note)
            near = sorted(near, key=lambda x: x["gap"])
            return near

    def __len__(self):
        """ Returns the size of a Book. """
        with open(self.path, "r") as handle:
            data = json.load(handle)
            return len(data)

    def view(self):
        """ Prints all Book's notes. """
        green = GColor.RGB(15, 155, 43)
        print(green + Text.BOLD + f"**********PHONEBOOK {self.path}**********" + Text.END)
        with open(self.path, "r") as handle:
            data = json.load(handle)
            for id, note in enumerate(data):
                print("-----------------------------" + "-" * len(self.path))
                print(f"ID:\t\t\t\t{id}")
                print(f"NAME:\t\t\t{note['name']}")
                print(f"SURNAME:\t\t{note['surname']}")
                print(f"PHONE NUMBER:\t{note['phone']}")
                try:
                    print(f"DATE OF BIRTH:\t{note['birth_date']}")
                except KeyError:
                    pass
                print("-----------------------------" + "-" * len(self.path))
        print(green + Text.BOLD + "*****************************" + "*" * len(self.path) + Text.END)

    def search(self, name: str = None, surname: str = None, phone_number: str = None, date: str = None,
               output_range: int = None, is_strict: bool = False) -> list or int:
        """ Searches notes in a Book by multiple parameters.
            If is_strict, function will return only one note ID, which meets all the requirements.
            If is_strict == false, function will search for most satisfying notes, including fuzzy
            search by name and surname, and return a list of IDs."""
        with open(self.path, "r") as handle:
            data = json.load(handle)
            output_range = len(data) if (output_range is None or output_range > len(data)) else output_range
            if is_strict:
                useless_notes = []
                for i, note in enumerate(data):
                    note["id"] = i
                    if name and note['name'] != name:
                        useless_notes.append(i)
                        continue
                    if surname and note['surname'] != surname:
                        useless_notes.append(i)
                        continue
                    if phone_number and note['phone'] != Book.correct_phone(phone_number):
                        useless_notes.append(i)
                        continue
                    if Book.is_date(date) and note['birth_date'] != date:
                        useless_notes.append(i)
                        continue
                for i, _index in enumerate(useless_notes):
                    del data[_index - i]
                if len(data) == 0:
                    return -1
                else:
                    return data[0]["id"]
            else:
                for i, note in enumerate(data):
                    note["id"] = i
                    note["score"] = 0.0
                    if name is not None:
                        note["score"] += note['name'] == name if is_strict else fuzz.ratio(name, note["name"])
                    if surname is not None:
                        note["score"] += note['surname'] == surname if is_strict else fuzz.ratio(surname,
                                                                                                 note["surname"])
                    if phone_number is not None:
                        if note["phone"] == Book.correct_phone(phone_number):
                            note["score"] += 1
                    if date is not None:
                        if Book.is_date(date):
                            if note["birth_date"] == date:
                                note["score"] += 1
                        else:
                            print("NOT A DATE")
                            pass  # USER ACTION REQUIRED TODO: add user action!
                data = sorted(data, key=lambda x: x["score"], reverse=True)
                if data[0]['score'] == 0:
                    return -1
                found = [note['id'] for note in data]# if note['score'] == data[0]['score']]
                return found[:output_range]

    def print(self, notes_ids: list = None, notes: list = None, mark_first: bool = False) -> None:
        """ Prints provided notes by IDs or from list. """
        if notes is None:
            with open(self.path, "r") as handle:
                data = json.load(handle)
                notes = [data[i] for i in notes_ids]
        green_bold = Text.BOLD + GColor.RGB(15, 155, 43)
        color = Text.BOLD + GColor.RGB(15, 155, 43) if mark_first else Text.YELLOW
        for id, note in enumerate(notes):
            print((color if id == 1 else Text.YELLOW) +
                  "------------------------------" + "-" * len(self.path))
            print((color if id == 1 else Text.YELLOW) +
                  f"ID:\t\t\t\t{note['id'] if 'id' in note else id}")
            print((color if id == 1 else Text.YELLOW) +
                  f"NAME:\t\t\t{note['name']}")
            print((color if id == 1 else Text.YELLOW) +
                  f"SURNAME:\t\t{note['surname']}")
            print((color if id == 1 else Text.YELLOW) +
                  f"PHONE NUMBER:\t{note['phone']}")
            print((color if id == 1 else Text.YELLOW) +
                  f"DATE OF BIRTH:\t{note['birth_date']}" + Text.END +
                  (green_bold + f" ({note['gap']} days remaining)" + Text.END) if "gap" in note else '')
            print((color if id == 1 else Text.YELLOW) +
                  "------------------------------" + "-" * len(self.path) + Text.END)

    @staticmethod
    def is_date(check_date: str):
        """ Checks if a date is valid. """
        if check_date is None:
            return False
        try:
            raw = tuple(map(int, check_date.split('.')))
            temp = datetime(day=raw[0], month=raw[1], year=raw[2])
            return True
        except ValueError:
            return False

    @staticmethod
    def is_name(name: str):
        """ Checks if a name is valid. """
        pattern = re.compile("^([A-Z]{1}[a-z0-9\s]+)$")
        if pattern.match(name):
            return True
        else:
            return False

    @staticmethod
    def correct_phone(phone: str) -> str:
        """Checks if a phone is valid and unifies format."""
        _phone = '8' + phone.replace('+', '')[1:]
        pattern = re.compile("^[0-9]{11}$")
        if pattern.match(_phone):
            return _phone
        else:
            return "phone_error"
