import json
import os
from additional import GColor
from data import Book
from additional import Text
from errors import DuplicateNote, NoSuchNote, WrongDateError


class BookInterface(Book):

    def __init__(self, path: str = None):
        super().__init__(path)

    def get_user_data(self, is_name: bool = True, is_surname: bool = True,
                      is_phone: bool = True, is_birth_date: bool = True, strict_data=True) -> dict:
        note = dict()
        if is_name:
            note['name'] = input("Name: ")
            if note['name'] == '' and not strict_data:
                note.pop('name')
            else:
                while not self.is_name(name=note['name']):
                    print(Text.RED
                          + "Error: name must contain only characters, spaces and digits and begin with a capital letter."
                          + Text.END)
                    note['name'] = input("Name: ")
        if is_surname:
            note['surname'] = input("Surname: ")
            if note['surname'] == '' and not strict_data:
                note.pop('surname')
            else:
                while not self.is_name(name=note['surname']):
                    print(Text.RED
                          + "Error: surname must contain only characters, spaces and digits and begin with a capital "
                            "letter. "
                          + Text.END)
                    note['surname'] = input("Surname: ")
        if is_phone:
            user_input = input("Phone (11 digits): ")
            if user_input == '' and not strict_data:
                pass
            else:
                note['phone'] = self.correct_phone(user_input)
                while note['phone'] == "phone_error":
                    print(Text.RED
                          + "Error: phone should contain only 11 digits."
                          + Text.END)
                    note['phone'] = self.correct_phone(input("Phone (11 digits): "))
        if is_birth_date:
            note['birth_date'] = input("Birth date DD.MM.YYYY (may be left empty, just press Enter): ")
            if note['birth_date'] == '':
                note.pop('birth_date')
                return note
            while note['birth_date'] and not self.is_date(note['birth_date']):
                print(Text.RED
                      + "Error: birth date is not valid. Use DD.MM.YYYY (including dots)."
                      + Text.END)
                note['birth_date'] = input("Birth date DD.MM.YYYY (may be left empty, just press Enter): ")
        return note

    def add_note(self):
        green = GColor.RGB(15, 155, 43)
        print(green + Text.BOLD + '*' * 14 + " ADDING RECORD " + '*' * 14 + Text.END)
        note = self.get_user_data()
        if self._exists(note):
            user_input = input("The record with the same name and surname already exists. Rewrite/Abort (Y/N): ")
            while user_input != 'Y' and user_input != 'N':
                print(Text.RED
                      + "Error: use only Y (for rewriting existing data) or N (for aborting addition)"
                      + Text.END)
                user_input = input("The record with the same name and surname already exists. Rewrite/Abort (Y/N): ")
            if user_input == 'Y':
                self._edit(_id=self.search(note['name'], note['surname'], is_strict=True), to_edit=note)
                print(green + "Successfully edited." + Text.END)
                return None
            else:
                print(green + "Adding a new record was cancelled by user." + Text.END)
                return None
        self._add(note=note)
        print(green + "Successfully added." + Text.END)

    def del_note(self):
        green = GColor.RGB(15, 155, 43)
        print(green + Text.BOLD + '*' * 14 + " REMOVING RECORD " + '*' * 14 + Text.END)
        print("How do you want to choose a record to be deleted?")
        print("1. By name and surname")
        print("2. By phone")
        user_input = input("Please, choose action number: ")
        while user_input != '1' and user_input != '2':
            user_input = input(Text.RED + "Please, use only 1 or 2: " + Text.END)
        if user_input == '1':
            note = self.get_user_data(is_phone=False, is_birth_date=False)
            _id = self.search(**note, is_strict=True)
            if _id == -1:
                print("Sorry, the record with such name and surname was not found. Please, select further action:")
                print("1. Try again with another name and surname")
                print("2. View the whole phonebook and select note by ID to be deleted")
                print("3. Delete note by phone")
                print("4. Quit to the main menu")
                user_input = input("Select a number: ")
                while user_input not in "1234":
                    user_input = input(Text.RED + "Please, select a valid number: " + Text.END)
                if user_input == '1':
                    self.del_note()
                elif user_input == '2':
                    self.view()
                    _id = input("Please, select an ID of a record to be deleted or write Q to return to main menu: ")
                    while _id != 'Q':
                        if _id.isdigit():
                            if 0 < int(_id) <= len(self):
                                break
                        else:
                            _id = input(Text.RED + "Please, select a valid ID: " + Text.END)
                    if _id == 'Q':
                        return None
                    else:
                        current = self._get(note_id=int(_id))
                        if self.verify_del(name=current['name'], surname=current['surname']):
                            print(f"Deleting {current['name']} {current['surname']}...")
                            self._del(note_id=int(_id))
                            print(green + "Successfully deleted." + Text.END)
                        else:
                            return None
                elif user_input == '3':
                    self.del_note_by_phone()
                else:
                    return None
            else:
                current = self._get(note_id=int(_id))
                if self.verify_del(name=current['name'], surname=current['surname']):
                    print(f"Deleting {current['name']} {current['surname']}")
                    self._del(note_id=int(_id))
                    print(green + "Successfully deleted." + Text.END)
        else:
            self.del_note_by_phone()

    def del_note_by_phone(self) -> None:
        user_input = input("Phone: ")
        while self.correct_phone(phone=user_input) == "phone_error" and user_input != 'Q':
            user_input = input("Please, write valid phone (11 digits) or type Q to abort operation: ")
        if user_input == 'Q':
            return None
        else:
            _ids = self.search(phone_number=user_input, is_strict=False)
            if len(_ids) == 0:
                print("Couldn't find any records with such a phone number. Try again?")
                user_input = input("Y/N: ")
                while user_input != 'Y' and user_input != 'N':
                    user_input = input("Please, use only Y or N: ")
                if user_input == 'Y':
                    self.del_note_by_phone()
                else:
                    return None
            else:
                if len(_ids) == 1:
                    note = self._get(note_id=_ids[0])
                    print(f"Found a record with this phone: {note['name']} {note['surname']}")
                    if self.verify_del(name=note['name'], surname=note['surname']):
                        self._del(note_id=_ids[0])
                        print(Text.GREEN + "The record has been successfully deleted." + Text.END)
                    else:
                        return None
                else:
                    print(Text.GREEN + "There were several matches by phone number:")
                    self.print(notes_ids=_ids, mark_first=False)
                    user_input = input("Enter record ID or Q to exit to main menu: ")
                    while user_input != 'Q' and (not user_input.isdigit() or not 0 <= int(user_input) < len(_ids)):
                        print(Text.RED + "Check if the data is entered correctly." + Text.END)
                        user_input = input("Enter record ID or Q to exit to main menu: ")
                    if user_input == 'Q':
                        return None
                    else:
                        _id = _ids[int(user_input)]
                        note = self._get(note_id=_id)
                        if self.verify_del(name=note['name'], surname=note['surname']):
                            self._del(note_id=_id)
                            print(Text.GREEN + "The record has been successfully deleted." + Text.END)

    def verify_del(self, name: str, surname: str) -> bool:
        print(Text.RED + f"Are you sure you want to delete the record "
                         f"(name: {name}, surname: {surname})?" + Text.END)
        if input(
                "Enter record's last name to confirm deletion or other characters to cancel. Please note that the action is irreversible: ") == surname:
            return True
        else:
            user_input = input("Error: Action was not confirmed. Want to try again? (Y/N)")
            while user_input != "Y" and user_input != "N":
                print(Text.RED + "Please, use only Y or N.")
                user_input = input("Error: Action was not confirmed. Want to try again? (Y/N)")
            if user_input == "Y":
                return self.verify_del(name=name, surname=surname)
            elif user_input == 'N':
                print(Text.GREEN + "The deletion was canceled by the user." + Text.END)
                return False
        return False

    def edit_note(self):
        green = GColor.RGB(15, 155, 43)
        print(green + Text.BOLD + '*' * 14 + " EDITING RECORD " + '*' * 14 + Text.END)
        note = self.get_user_data(is_phone=False, is_birth_date=False)
        _id = self.search(**note, is_strict=True)
        if _id == -1:
            print("Sorry, the record with such name and surname was not found. Please, select further action:")
            print("1. Search again with another name an surname")
            print("2. Add a new record with such name and surname")
            print("3. View the whole phonebook and select note by ID to be edited")
            user_input = input("Select a number: ")
            while user_input != '1' and user_input != '2' and user_input != '3':
                user_input = input(Text.RED + "Please, select a valid number: " + Text.END)
            if user_input == '1':
                self.edit_note()
            elif user_input == '2':
                print("Adding a new record. Please, fill the remaining fields: ")
                additional = self.get_user_data(is_name=False, is_surname=False)
                self._add({**note, **additional})
            elif user_input == '3':
                self.view()
                _id = input("Please, select an ID of a record to be edited or write Q to return to main menu: ")
                while _id != 'Q':
                    if _id.isdigit():
                        if 0 < int(_id) <= len(self):
                            break
                    else:
                        _id = input(Text.RED + "Please, select a valid ID: " + Text.END)
                if _id == 'Q':
                    return None
                else:
                    current = self._get(note_id=int(_id))
                    print(f"Editing {current['name']} {current['surname']}")
                    self.edit_particular(_id=int(_id))
        else:
            self.edit_particular(_id=int(_id))

    def edit_particular(self, _id: int):
        green = GColor.RGB(15, 155, 43)
        print(
            green + "Fill in only the fields which  you want to edit. If you want something to be left as is, just press Enter." + Text.END)
        note = self.get_user_data(strict_data=False)
        try:
            found = self.search(name=note['name'], surname=note['surname'], is_strict=True)
            if found:
                while found > 0:
                    print(Text.RED + "Error: a record with such name and surname already exists. Try again?" + Text.END)
                    user_input = input("Type Y to choose another name and surname or N to exit to the main menu: ")
                    while user_input != 'Y' and user_input != 'N':
                        user_input = input("Please, use only Y/N.")
                    if user_input == 'Y':
                        print(
                            green + "Fill in only the fields which  you want to edit. If you want something to be left as is, just press Enter." + Text.END)
                        note = self.get_user_data(strict_data=False)
                        found = self.search(name=note['name'], surname=note['surname'], is_strict=True)
                    else:
                        return None
        except KeyError:
            pass
        self._edit(_id=int(_id), to_edit=note)
        print(green + "Successfully edited." + Text.END)

    def get_closest_birthday(self, days: int = None):
        green = GColor.RGB(15, 155, 43)
        if days is None:
            print(green + Text.BOLD + '*' * 14 + " NEXT BIRTHDAYS " + '*' * 14 + Text.END)
            days = 30
        print(green + f"List of people who have birthday in next {days} days:" + Text.END)
        notes = self.get_birthday_in(days=days)
        if len(notes) == 0:
            print(f"Sorry, there are no birthdays in next {days} days.")
        else:
            self.print(notes=notes)
        user_input = input("Please, click Enter to get back to Main Menu or type amount of days to search for birthdays: ")
        while user_input != "" and (not user_input.isdigit() or int(user_input) > 365 or int(user_input) < 0):
            user_input = input(Text.RED + "Please, use only valid (0 < amount < 365) amount to search or press Enter to quit: " + Text.END)
        if user_input.isdigit():
            self.get_closest_birthday(days=int(user_input))

    def view_all(self):
        green = GColor.RGB(15, 155, 43)
        self.view()
        input(green + "Press Enter to return to main menu." + Text.END)

    def view_age(self):
        green_bold = Text.BOLD + GColor.RGB(15, 155, 43)
        data = self.get_user_data(is_phone=False, is_birth_date=False)
        try:
            _id = self.search(name=data['name'], surname=data['surname'], is_strict=True)
            if _id == -1:
                raise KeyError
            age_info = self._age(note_id=_id)
            print(green_bold
                  + f"{data['name']} {data['surname']}, age: {age_info['years']} years and {age_info['months']} months."
                  + Text.END)
            input(green_bold + "Press Enter to return to main menu." + Text.END)
        except KeyError:
            print(Text.RED + "Sorry, this person doesn't have birth date info or doesn't exist." + Text.END)
            user_input = input("Do you want to try with different name and surname (Y/N): ")
            while user_input not in "YN":
                user_input = input(Text.RED + "Please, use only Y/N: " + Text.END)
            if user_input == 'Y':
                self.view_age()
            else:
                return None

    def view_people_aged(self):
        green = GColor.RGB(15, 155, 43)
        age = input("Please, type age border: ")
        while not age.isdigit():
            age = input(Text.RED + "Please, use only digits: " + Text.END)
        is_older = input(f"Do you need people older/younger than {age}? Use O/Y: ").upper()
        while is_older not in "OY":
            is_older = input(Text.RED + f"Please, use only O/Y: " + Text.END)
        if is_older == 'O':
            is_older = True
        else:
            is_older = False
        target = []
        for _id, note in enumerate(self._get_all()):
            note['id'] = _id
            try:
                if is_older:
                    if self._age(_id)['years'] > int(age):
                        target.append(note)
                else:
                    if self._age(_id)['years'] < int(age):
                        target.append(note)
            except KeyError:
                continue
        print(Text.BOLD + '*' * 14 + F" PEOPLE {'OLDER' if is_older else 'YOUNGER'} {age} " + '*' * 14 + Text.END)
        if len(target) == 0:
            print(Text.RED + "Not found." + Text.END)
        else:
            self.print(notes=target)
        input(green + "Press Enter to get back to Main Menu." + Text.END)
