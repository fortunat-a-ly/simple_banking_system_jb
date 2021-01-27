import random
import sqlite3


# create a Connection object that represents the database
conn = sqlite3.connect('card.s3db')
# create a Cursor object to call its execute() method for performing SQL queries
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance FLOAT DEFAULT 0);")
conn.commit()  # commit changes to the database


class Card:
    def __init__(self, number=None):
        # create a class instance of the existing card or create a new one
        if number is not None and Card.exists(number):
            self.number = str(number)
            self.balance = self.__get_balance()
        else:
            self.number = self.create_number()
            self.pin = self.create_pin()
            self.balance = 0
            cur.execute(f'INSERT INTO card (number, pin) VALUES ({self.number}, {self.pin});')
            conn.commit()

    def __get_balance(self) -> float:
        cur.execute(f'SELECT balance FROM card WHERE number = {self.number};')
        conn.commit()
        return cur.fetchone()[0]

    def add_income(self, income_: float):
        self.balance += income_
        cur.execute(f"UPDATE card SET balance = {self.balance} WHERE number = {self.number};")
        conn.commit()

    def transfer_money(self, number: str, amount: float):
        if transfer_money > self.balance:
            print("Not enough money!")
        else:
            Card(number).add_income(amount)
            self.add_income(-amount)
            print("Success")

    def close(self):
        cur.execute(f"DELETE FROM card WHERE number = {self.number};")
        conn.commit()

    @staticmethod
    def create_pin() -> str:
        return "{}{}{}{}".format(random.randrange(0, 10), random.randrange(0, 10), random.randrange(0, 10),
                                 random.randrange(0, 10))

    @staticmethod
    def create_number() -> str:
        number = Card.__luhn_algorithm()

        cur.execute("SELECT number FROM card;")
        conn.commit()
        numbers = cur.fetchall()

        already_exists = True
        while already_exists:
            already_exists = False
            for i in numbers:
                if i[0] == number:
                    already_exists = True
                    number = Card.__luhn_algorithm()
                    break
        return number

    @staticmethod
    def check_last_digit(number: str) -> bool:
        result = 0
        for i in range(0, 15, 2):
            result += int(number[i]) * 2 - 9 if int(number[i]) * 2 > 9 else int(number[i]) * 2
        for i in range(1, 15, 2):
            result += int(number[i])
        return str((10 - result % 10) % 10) == number[15]

    @staticmethod
    def __luhn_algorithm() -> str:
        number = str(400000000000000 + random.randint(0, 999999999))
        result = 0
        for i in range(0, 15, 2):
            result += int(number[i]) * 2 - 9 if int(number[i]) * 2 > 9 else int(number[i]) * 2
        for i in range(1, 15, 2):
            result += int(number[i])
        return number + str((10 - result % 10) % 10)

    @staticmethod
    def exists(number: str) -> bool:
        cur.execute(f"SELECT count(number) FROM card WHERE number={number};")
        conn.commit()
        return cur.fetchone()[0]

    @staticmethod
    def __check_credentials(number: str, pin: str) -> bool:
        if Card.exists(number):
            cur.execute(f"SELECT pin FROM card WHERE number = {number};")
            conn.commit()
            return pin == cur.fetchone()[0]
        return False

    @staticmethod
    def log_in(number: str, pin: str) -> bool:
        return Card.__check_credentials(number, pin)


first_menu = """1. Create an account
2. Log into account
0. Exit"""

second_menu = """1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit"""

print(first_menu)
input_ = int(input())

while input_ != 0:
    if input_ == 1:
        card = Card()   # generate card number and pin and add it to the database
        print("Your card has been created")
        print("Your card number:", card.number, sep="\n")
        print("Your card PIN:", card.pin, sep="\n")
    elif input_ == 2:
        card_number = input("Enter your card number:")
        pin_input = input("Enter your PIN:")

        if Card.log_in(card_number, pin_input):
            card = Card(card_number)   # create an instance of the card which already exists in the database
            print("You have successfully logged in!")
            print(second_menu)
            input_ = int(input())
            while input_ != 0:
                if input_ == 1:
                    print(f"Balance: {card.balance}")
                elif input_ == 2:
                    income = int(input("Enter income:"))
                    card.add_income(income)
                    print("Income was added!")
                elif input_ == 3:
                    print("Transfer")
                    receiver_number = input("Enter card number:")
                    if receiver_number == card.number:
                        print("You can't transfer money to the same account!")
                    elif not Card.check_last_digit(receiver_number):
                        print("Probably you made a mistake in the card number. Please try again!")
                    elif not Card.exists(receiver_number):
                        print("Such a card does not exist.")
                    else:
                        transfer_money = float(input("Enter how much money you want to transfer:"))
                        card.transfer_money(receiver_number, transfer_money)
                elif input_ == 4:
                    card.close()
                    print("The account has been closed!")
                    break
                elif input_ == 5:
                    print("You have successfully logged out!")
                    break
                print(second_menu)
                input_ = int(input())
            else:
                print("Bye")
                break
        else:
            print("Wrong card number or PIN!")
    print(first_menu)
    input_ = int(input())
else:
    print("Bye")
