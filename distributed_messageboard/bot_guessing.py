"""
guessing game bot

Ideas:
- variable end number
"""

"""

Bot ideas: 
https://www.geeksforgeeks.org/convert-text-speech-python/
https://stackoverflow.com/questions/64501684/how-can-i-play-playing-a-mp3-sound-with-flask
- > channel.html müsste verändert werden für mp3 wie besonders für den einen channel. 
- > text to speech on and off for all channels


"""

import random


class GuessingBot:

    def __init__(self):

        self.max_value = 10
        self.name = "GUESSING BOT"

        self.start()
    
    def apply(self, input : str): # input = "Ich schätze 10"

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
            return f"The maximum value was changed. \nYou can guess a number between 1 and {self.max_value} now."

        # check if in range
        if n < 1 or n > self.max_value:
            return f"{n} is a bad guess. Then number is between 1 and {self.max_value}."
        
        # check if correct 
        if n == self.number:
            self.start()
            return f"{n} is the correct number. \nYou can guess a new number between 1 and {self.max_value} now."
        if n < self.number:
            return f"{n} is too small."
        if n > self.number:
            return f"{n} is too big."
        return "Something went wrong."
        
    def start(self):
        self.number = random.randint(1,self.max_value)
        return f"Guess a number between 1 and {self.max_value}. \nYou can change the maximum value by typing 'max_value = <n>'"
    
    def is_start(self,message):
        """
        Bot checks whether the message is a start message.
        """

        if "number between 1 and 10" in message:
            return True 
        return False