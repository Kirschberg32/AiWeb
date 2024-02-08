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
        self.start()
        self.name = "GUESSING BOT"
    
    def apply(self, input : str): # input = "Ich schätze 10"

        string = [i for i in input.split() if i.isdigit()]

        # check if one number
        if len(string) == 0:
            return "There was no number in your input."
        if len(string)> 1:
            return "There were too many numbers."
        n = int(string[0])

        # check if in range
        if n < 1 or n > 10:
            return f"{n} is a bad guess. Then number is between 1 and 10."
        
        # check if correct 
        if n == self.number:
            self.start()
            return f"{n} is the correct number. \nYou can guess a new number between 1 and 10 now."
        if n < self.number:
            return f"{n} is too small."
        if n > self.number:
            return f"{n} is too big."
        return "Something went wrong."
        
    def start(self):
        self.number = random.randint(1,10)
        return "Guess a number between 1 and 10."