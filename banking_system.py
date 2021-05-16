from random import randint
from math import ceil
from sys import exit
from textwrap import dedent
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
conn.commit()
card_table = """ CREATE TABLE IF NOT EXISTS card (
                                                    id INTEGER,
                                                    number TEXT,
                                                    pin TEXT,
                                                    balance INTEGER DEFAULT 0
)"""

cur.execute(card_table)
conn.commit()

class ATM():
    """Displays the menu, creating new account, checks the credentials and respons to choices when to run"""
    def __init__(self, account):
        self.account = account

    def menu(self):
        while True:

            print(dedent("""
            1. Create an account
            2. Log into account
            0. Exit"""))

            menu_choice = input()

            if menu_choice == '1':
                self.generate_account()
            elif menu_choice == '2':
                self.security(input('Enter your card number:\n'), input('Enter your PIN:\n'))
            elif menu_choice == '0':
                exit()

    def pin_generation(self):
        return ''.join([str(randint(0,9)) for i in range(4)])

    def card_number_generator(self):
        """"Implement Luhn Algorithm to generate card number """
        first_digits = [4,0,0,0,0,0]
        for i in range(9):
            first_digits.append(randint(0,9))
        first_step = [num * 2 if i % 2 == 0 else num for i, num in enumerate(first_digits)]
        second_step = [i - 9 if i > 9 else i for i in first_step]
        first_digits.append(int(ceil(sum(second_step)/ 10) * 10) - sum(second_step))

        return''.join([str(i) for i in first_digits])

    def generate_account(self):
        """Generate pin and card numbers for the new user and save them into the database"""
        card_number = self.card_number_generator()
        pin_number = self.pin_generation()
        insert = "INSERT INTO card (number, pin) VALUES (?,?)"
        generated_numbers = card_number, pin_number
        cur.execute(insert, generated_numbers)
        conn.commit()

        print(dedent(f"""
        Your card has been created
        Your card number:
        {card_number}
        Your card PIN:
        {pin_number}"""))

    def security(self, g_number, g_pin):
        """Check the credentials"""
        cur.execute('SELECT * FROM card')

        first_line = cur.fetchone()
        try:
            first_line[1] == g_number
        except TypeError:
            print('Wrong card number or PIN!')
        else:
            if first_line[1] == g_number and first_line[2] == g_pin:
                print('You have successfully logged in!')
                self.account.open_menu()
            else:
                print('Wrong card number or PIN!')

class Account():
    """Responsible for account users account manipulations"""
    def __init__(self):
        self.atm = ATM(self)

    def open_menu(self):
        while True:
            print(dedent("""
            1. Balance
            2. Add income
            3. Do transfer
            4. Close account
            5. Log out
            0. Exit"""))

            choice = input()

            if choice == '1':
                self.balance()
            elif choice == '2':
                self.add_income(int(input('Enter income:\n')))
            elif choice == '3':
                self.transfer(input('Transfer\nEnter card number\n :'))
            elif choice == '4':
                self.delete()
            elif choice == '5':
                self.atm.menu()
            elif choice == '0':
                print('Bye!')
                exit(1)

    def balance(self):
        cur.execute('SELECT * FROM card')
        details = cur.fetchone()
        print(f'Balance: {details[3]}')
        self.open_menu()

    def add_income(self, income):
        cur.execute('SELECT * FROM card')
        details = cur.fetchone()
        updated_balance = income + details[3]
        cur.execute('UPDATE card SET balance = (?) WHERE number = (?)', (updated_balance, details[1]))
        conn.commit()
        print("Income added!")
        self.open_menu()

    def transfer(self, tran_card):
        cur.execute('SELECT * FROM card')
        details = cur.fetchone()
        w = cur.execute("SELECT * FROM card WHERE number = (?)", (tran_card,)).fetchall()

        if tran_card != details[1]:
            first_step = [int(num) * 2 if i % 2 == 0 else int(num) for i, num in enumerate(tran_card[:-1])]
            second_step = [i - 9 if i > 9 else i for i in first_step]
            x = sum(second_step) + int(tran_card[-1])


            if x % 10 == 0:
                if w != []:
                    amount = int(input('Enter how much money you want to transfer:\n'))
                    if amount <= details[3]:
                        new_balance = details[3] - amount
                        cur.execute('UPDATE card SET balance = (?) WHERE number = (?)', (new_balance, details[1]))
                        cur.execute(('UPDATE card SET balance = (?) WHERE number = (?)'), (amount, tran_card))
                        conn.commit()
                        self.open_menu()
                    else:
                        print('Not enough money!')
                        self.open_menu()
                else:
                    print('Such a card does not exist.')
            else:
                print("Probably you made a mistake in the card number. Please try again!")
                self.open_menu()
        else:
            print("You can't transfer money to the same account!")
            self.open_menu()

    def delete(self):
        cur.execute('SELECT * FROM card')
        details = cur.fetchone()
        cur.execute('DELETE FROM card WHERE number=(?)', (details[1],))
        conn.commit()
        print('The account has been closed!')
        self.atm.menu()


account = Account()
action = ATM(account)
action.menu()
conn.close()
