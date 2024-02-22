Message Channel and Client by Eosandra Grund and Fabian Kirsch

# Channel
We created a Chat Channel with a Chatbot for the course "Artificial Intelligence and the Web"(WS23/24). The Channel and the Client are running on a university server. 

## The Chatbot of The 2D Point Guessing Game
It is a point guessing game. The goal is to guess a 2D point in the square ( - {self.max_value},- {self.max_value})  to ({self.max_value},{self.max_value}), or rather to be as close as possible to it. The x and y coordinates of the point to guess are whole numbers.
        <br>{self.max_value} is the maximum value and the difficulty of the game depends on it. It can be changed by typing <b>'max_value n'</b>. Replace n with a number.
        <br>To start the game type <b>'start'</b>. You can also use this command to restart the game at any time. Be aware that the correct point will be changed. 

        <h2> Hints </h2>
        To be able to make a better guess, you can get 3 hints before making your final guess and 'reveal' the solution. They are 'hyperplane', 'distance' and 'quadrant'. You can use each of them exactly one time. To ask for a hint simply type the name of the hint with the coordinates of a point in the same message separated by a space, as each hint depends on a point (Example: <b>'1 1 hyperplane'</b>).
        <br><b>'hyperplane':</b> Imagine a straight line through your entered point and the origin (0,0). This is the hyperplane. Your hint will be whether the searched point is located on this line, or in the y dimension above or below the line. 
        <br><b>'distance':</b> You will get information about whether the point to guess is less or more than max_value / 3 away from your entered point. 
        <br><b>'quadrant':</b> You will get the information if your entered point is located in the same quadrant of the coordinate system as the point to guess. If it is, this means, that both coordinates of the point to guess have the same signs as the ones from your entered point. 
        
        <br><br>After getting all the hints you want, you can make a final guess. If you want you can send it in the chat simply by sending two numbers separated by a space (<b>'3 3'</b>). If you are done guessing you can reveal the correct point and the ranking by typing <b>'reveal'</b>. The closest guess wins. 


##  The Chatbot of The Simple Number Guessing Game
It is a simple guessing game, of a number between 0 and n. Where n can be changed the same way as in 'The 2D Point Guessing Game' but has 10 as the default value. 


## Run Developmental Server
Install the requirements. Let the hub, the client and the wanted channel run in separated consoles. The register the channel with the hub by running ```flask --app channelfilename.py register```. Then you have a developmental version of the programm running on your computer. 

## Files: 
### Folders:
* [static](static): Contains static files, like images or .css files
* [templates](templates): Contains the html templates for the Client app. 
* [wsgi_files](wsgi_files): Contains the wsgi files for the server & the code with changed paths for the server.
* [data](data): Contains two example chats. 
* [bot](bot): Contains all the code for the bots

### Files:
* [hub.py](hub.py): Contains a hub, for developmental purposes
* [client.py](client.py): Contains the flask app of the Client
* [channel_guess.py](channel_guess.py): Contains the Channel flask app for 'The Simple Number Guessing Game'.
* [channel_guess2.py](channel_guess2.py): Contains the Channel flask app for 'The 2D Point Guessing Game'.
* [requirements.txt](requirements.txt): list of dependencies