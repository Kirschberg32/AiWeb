"""
guessing game bot

Ideas:
- variable end number
"""

"""

x y Hyperplane

Tipp:
- Hyperplane
- Distance
- Quadrant
- 
"""

import random
import numpy as np

class GuessingBot2:

    def __init__(self):

        self.max_value = 4
        self.name = "GUESSING BOT"

        self.point = []
        self.hints = []
    
    def apply(self, input : str): # input = "Ich schätze 10"

        input = input.lower()

        if "start" in input:
            return self.start()
        elif "help" in input:
            return self.help()
        elif "max_value" in input:
            digit = [i for i in input.split() if i.isdigit()]
            if len(digit) == 1:
                self.max_value = int(digit[0])
                self.start()
                return f"The maximum value was changed. \nYou can guess a point in the square ( - {self.max_value},- {self.max_value})  to ({self.max_value},{self.max_value}) now."
            return f"Please give exactly one possible value for max_value."
        elif self.point == []:
            return "No active game. Send 'start' to start a game."

        digit = [i for i in input.split() if i.isdigit()]
        string = [i for i in input.split() if not i.isdigit()]

        if len(string) == 0 and len(digit) == 2:
            return "Thank you for your guess."

        # check if tow number
        if len(digit) == 0:
            if "reveal" in input:
                return f"The correct point is {self.point}"
            return "There was no number in your input."
        if len(digit) == 1:
            return "There was only one number in your input."
        if len(digit) > 2:
            return "There were too many numbers in your input."

        hint = ""
        for s in string:
            if s in self.hints:
                hint = s
                self.hints.remove(s)
                break

        if hint == "":
            return  "Thank you for your guess."
        
        x,y = int(digit[0]), int(digit[1])
        
        # check if in right quadrant
        if hint == "quadrant":
            if (np.sign([x,y]) == np.sign(self.point)).all():
                return "In correct quadrant"
            return "Not in right quadrant."

        # check if on the same line
        if hint == "hyperplane":
            if y/x == self.point[1]/self.point[0]:
                return "The point is on the same line through the origin as your guess."
            # check which half

        if hint == "distance":
            dist = np.linalg.norm(np.array([x,y])-np.array(self.point))
            if dist < self.max_value/3:
                return f"The point is less than {self.max_value/3} away from {(x,y)}."
            return f"The point is more than {self.max_value/3} away from {(x,y)}."
        
        return "Something went wrong."
        
    def start(self):
        self.point = [ random.randint(- self.max_value,self.max_value), random.randint(-self.max_value,self.max_value) ]
        self.hints = ["hyperplane", "distance", "quadrant"]
        return f"You can get 3 hints before you have to make your final guess. They are 'hyperplane', 'distance' and 'quadrant'. For a sample input type 'help'. Each hint is based on a point given by you. When you did you final guess type 'reveal' to get the correct point."
    
    def start_message(self):
        return_string = f"This is a point guessing game. You can guess a point in the square ( - {self.max_value},- {self.max_value})  to ({self.max_value},{self.max_value})."
        return_string += f"\nYou can change the maximum value for x and y by typing 'max_value = <n>'. \nx and y are whole numbers. \nThe game starts when you type 'start'."
        return return_string
    
    def is_start(self,message):
        """
        Bot checks whether the message is a start message.
        """

        if message == self.start_message():
            return True 
        return False
    
    def help(self):
        return ""