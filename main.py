import sys
from interface import BookInterface
from additional import Text, GColor

PhoneBook = BookInterface()
GREEN = GColor.RGB(15, 155, 43)


def main_menu():
    print(GREEN + Text.BOLD + '*' * 18 + " MAIN MENU " + '*' * 18 + Text.END)
    print("Please, select an action by choosing its index.\nOperations:")
    print("[1] Add a new record to a phone book")
    print("[2] Edit an existing record in a phone book")
    print("[3] Delete a record from a phone book")
    print("[4] Show people whose birthday is the next")
    print("[5] View the whole book")
    print("[6] View person's age")
    print("[7] View people older/younger than N years")
    print("[8] Quit")
    user_input = input("Please, enter the number: ")
    while user_input not in "12345678":
        user_input = input(Text.RED + "Please, select a valid number: " + Text.END)
    if user_input == '1':
        PhoneBook.add_note()
    elif user_input == '2':
        PhoneBook.edit_note()
    elif user_input == '3':
        PhoneBook.del_note()
    elif user_input == '4':
        PhoneBook.get_closest_birthday()
    elif user_input == '5':
        PhoneBook.view_all()
    elif user_input == '6':
        PhoneBook.view_age()
    elif user_input == '7':
        PhoneBook.view_people_aged()
    elif user_input == '8':
        sys.exit()


while True:
    main_menu()
