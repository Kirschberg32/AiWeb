"""
point guessing game bot
"""

"""
Ideas: 
- Testen was bei mehreren Spielern passiert. 
- ReadMe

x y Hyperplane

Hint:
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
        self.guesses = [ [(20,2), "Eo"], [(2,3), "Fabian"],]
    
    def apply(self, input : str, sender : str = ""): # input = "Ich schätze 10"
        """ 
        gets as input the user input and responses with a string
        """

        input = input.lower()

        # check if there are important commands in the input text
        if "start" in input:
            return self.start()
        elif "help" in input:
            return self.help()
        elif "max_value" in input:
            digit = [i for i in input.split() if i.lstrip('-+').isdigit()]
            if len(digit) == 1:
                self.max_value = int(digit[0])
                self.start()
                return f"The maximum value was changed. <br>You can guess a point in the square ( - {self.max_value},- {self.max_value})  to ({self.max_value},{self.max_value}) now."
            return f"Please give exactly one possible value for max_value."
        elif self.point == []:
            return "No active game. Type <b>'start'</b> to start a game."
        elif "reveal" in input:
            correct = self.point

            # Analize guesses
            for g in self.guesses:
                dist = np.linalg.norm(np.array([g[0][0],g[0][1]])-np.array(self.point))
                g.insert(0,dist)
            self.guesses.sort()

            ranking = f"""<h2> Ranking </h2>"""

            for i,g in enumerate(self.guesses):
                ranking += f"<pre>{i+1}. <b>{g[2].ljust(15)}</b> guessed {str(g[1]).ljust(9)} with a distance of {g[0].round(2)}<br></pre>"

            print(ranking)

            # delete old game
            self.point = []
            self.hints = []
            self.guesses = []

            return f"The correct point is {correct}. {ranking} <br>Type <b>'start'</b> to start a new game. "

        digit = [i for i in input.split() if i.lstrip('-+').isdigit()]
        string = [i for i in input.split() if not i.lstrip('-+').isdigit()]

        if len(string) == 0 and len(digit) == 2:
            x,y = int(digit[0]), int(digit[1])
            self.append_guess(sender, (x,y))
            return f"Thank you for your guess {sender}."

        # check if 2 numbers
        if len(digit) == 0:
            return f"There was no number in your input {sender}. For information about the game type <b>'help'</b>. "
        if len(digit) == 1:
            return f"There was only one number in your input {sender}. For information about the game type <b>'help'</b>."
        if len(digit) > 2:
            return f"There were too many numbers in your input {sender}. For information about the game type <b>'help'</b>."

        # find the first hint command
        hint = ""
        for s in string:
            if s in self.hints:
                hint = s
                self.hints.remove(s)
                break

        x,y = int(digit[0]), int(digit[1])

        if hint == "":
            self.append_guess(sender, (x,y))
            return  f"Thank you for your guess {sender}."
        
        # check if in right quadrant
        if hint == "quadrant":
            if (np.sign([x,y]) == np.sign(self.point)).all():
                return f"Your entered point {(x,y)} is located in the same quadrant as the point to guess."
            return f"Your entered point {(x,y)} is located in a different quadrant than the point to guess."

        # check if on the same line or in what relation to line
        if hint == "hyperplane":
            steigung = y/x
            if self.point[1] == steigung * self.point[0]:
                return f"The point to guess is located on the line through the origin and your entered point {(x,y)}."
            # check which half
            elif self.point[1] > steigung * self.point[0]:
                return f"The point to guess is located above the hyperplane in the y dimension running through your entered point {(x,y)}."
            return f"The point to guess is located below the hyperplane in the y dimension running through your entered point {(x,y)}."

        # check how far from input point
        if hint == "distance":
            dist = np.linalg.norm(np.array([x,y])-np.array(self.point))
            if dist < self.max_value/3:
                return f"The point to guess is less than {self.max_value/3} away from {(x,y)}."
            return f"The point to guess is more than {self.max_value/3} away from {(x,y)}."
        
        return "Something went wrong."
        
    def start(self):
        """
        starts a game of point guessing
        """
        self.point = [ random.randint(- self.max_value,self.max_value), random.randint(-self.max_value,self.max_value) ]
        self.hints = ["hyperplane", "distance", "quadrant"]
        return f"You can get 3 hints before you have to make your final guess. They are <b>'hyperplane'</b>, <b>'distance'</b> and <b>'quadrant'</b>. For more information and a sample input type <b>'help'</b>. Each hint is based on a point entered by you. When you gave your final guess type <b>'reveal'</b> to get the correct point."
    
    def start_message(self):
        """
        Returns a message with the most important rules and how to start. 
        """
        return_string = f"This is a point guessing game. You can guess a point in the square ( - {self.max_value},- {self.max_value})  to ({self.max_value},{self.max_value})."
        return_string += f"<br>You can change the maximum value for x and y by typing <b>'max_value n'</b>. Replace n with a number. The x and y coordinates of the point to guess are whole numbers. <br>The game starts when you type <b>'start'</b>."
        return return_string
    
    def is_start(self,message : str):
        """
        Bot checks whether the message is a start message.
        """

        if message == self.start_message():
            return True 
        return False
    
    def append_guess(self, sender : str, guess : str):

        for g in self.guesses:
            if g[1] == sender:
                self.guesses.remove(g)

        self.guesses.append([guess,sender])
    
    def help(self): 
        """
        Information about:

        - Goal of the game
        - How to start the game.
        - Which hints, what do they do & how to use them. 
        - How to guess.
        - How to reveal the correct point. 
        """

        return_string = f""" This is a point guessing game. The goal is to guess a 2D point in the square ( - {self.max_value},- {self.max_value})  to ({self.max_value},{self.max_value}), or rather to be as close as possible to it. The x and y coordinates of the point to guess are whole numbers.
        <br>{self.max_value} is the maximum value and the difficulty of the game depends on it. It can be changed by typing <b>'max_value n'</b>. Replace n with a number.
        <br>To start the game type <b>'start'</b>. You can also use this command to restart the game at any time. Be aware that the correct point will be changed. 

        <h2> Hints </h2>
        To be able to make a better guess, you can get 3 hints before making your final guess and 'reveal' the solution. They are 'hyperplane', 'distance' and 'quadrant'. You can use each of them exactly one time. To ask for a hint simply type the name of the hint with the coordinates of a point in the same message separated by a space, as each hint depends on a point (Example: <b>'1 1 hyperplane'</b>).
        <br><b>'hyperplane':</b> Imagine a straight line through your entered point and the origin (0,0). This is the hyperplane. Your hint will be whether the searched point is located on this line, or in the y dimension above or below the line. 
        <br><b>'distance':</b> You will get information about whether the point to guess is less or more than max_value / 3 away from your entered point. 
        <br><b>'quadrant':</b> You will get the information if your entered point is located in the same quadrant of the coordinate system as the point to guess. If it is, this means, that both coordinates of the point to guess have the same signs as the ones from your entered point. 
        
        <br><br>After getting all the hints you want, you can make a final guess. If you want you can send it in the chat simply by sending two numbers separated by a space (<b>'3 3'</b>). If you are done guessing you can reveal the correct point and the ranking by typing <b>'reveal'</b>. The closest guess wins. 
        """
        return return_string