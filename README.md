# HCD-chatApp

## Steps to install/run the chatApp

### All these steps are to be executed within the terminal/CMD(obviously)

### Before you start

a. Check if you have python installed by typing ```python``` in CMD.
If a python terminal ```>>``` doesn't show, proceed to https://www.python.org/downloads/

b. Check if you have pip installed by typing ```pip -version``` in CMD. 
If you you see its version, you are good to continue.

c. Now, check if pipenv is installed by typing ```pipenv -h``` in CMD/terminal.
IF YOU GET AN ERROR ALONG THE LINES "pipenv is not recognized as an internal or external command", 
then you need to check how to add ```pipenv``` on PATH in Windows.

1. Clone the project with the github link I sent: ```git clone https://github.com/izamha/hcd-chatApp.git```

2. ```cd``` into the project folder

3. Activate the pipenv shell: ```pipenv shell```

4. After the shell has been activated type ```pipenv install``` to install all the project dependencies.

5. If that throws an error about the python version, navigate into the project and look for a file called ```Pipfile``` then change the python version to whatever you installed. i.e ```python_version = "3.8"``` to ```python_version = "3.9"```

6. To stop/exit the pipenv shell, type: ```CTRL + C```

You made it down here?
Cheers!
