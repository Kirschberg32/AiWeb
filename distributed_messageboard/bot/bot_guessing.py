"""
guessing game bot
by Eosandra Grund & Fabian Kirsch
"""

import random


class GuessingBot:

    def __init__(self):

        self.max_value = 10
        self.name = "GUESSING BOT"
        self.start()
    
    def apply(self, input : str): # input = "Ich schätze 10"
        """
        Use this method to apply the bot to a message. It will return the answer

        Args:
            input (str): The user input to answer to

        Returns:
            answer (str): The message to send back
        """

        string = [i for i in input.split() if i.isdigit()]

        # check if one number
        if len(string) == 0:
            return "There was no number in your input."
        if len(string)> 1:
            return "There were too many numbers."
        n = int(string[0])

        # check if max value should be changed # -20
        if "max_value" in input:
            self.max_value = n
            self.start()
            return f"The maximum value was changed. <br>You can guess a number between 1 and {self.max_value} now."

        # check if in range
        if n < 1 or n > self.max_value:
            return f"{n} is a bad guess. Then number is between 1 and {self.max_value}."
        
        # check if correct 
        if n == self.number:
            self.start()
            return f"{n} is the correct number. <br>You can guess a new number between 1 and {self.max_value} now."
        if n < self.number:
            return f"{n} is too small."
        if n > self.number:
            return f"{n} is too big."
        return "Something went wrong."
        
    def start(self):
        """
        Used to start or restart a game. Returns the start message of the bot.
        
        """
        self.number = random.randint(1,self.max_value)
        return f"Guess a number between 1 and {self.max_value}. <br>You can change the maximum value by typing <b>'max_value n'</b>. Replace n with a number."
    
    def is_start(self,message):
        """
        Bot checks whether the message is a start message.
        """

        if "number between 1 and 10" in message:
            return True 
        return False