If you don't know what Snips is, start here: https://snips.gitbook.io/getting-started/ 
Everything that follows assumes you know what Snips, skills, intents, and MQTT are.

A lot of the base code for this was borrowed from here - https://github.com/tschmidty69/homeassistant-config/blob/master/snips/snips_listener.py

# Basic Snips Listener
A basic snips handler with dynamic module loading.  

What is dynamic module loading, you ask?  Basically, instead of creating a new function or set of functions in your handler to deal with each intent, you just create a new python script that is called dynamically by the handler whenever the intent is recognized by the Snips-NLU engine.

# Setup
Create a sub-directory called 'snips_skills'
Create an empty file called '__init__.py'
Update the snipsDefaults.py file that contains your snips IP address and MQTT port as well as any other common data elements you want available to your Snips skills (e.g. a Home Assistant IP address, Spotify credentials, etc)

# Module setup
Each module in your snips_skills directory should have a base function called 'run' that is what kicks off your skill code.  It should accept a data element called "data" that will contain the intent message from Snips in json format.  Import json if you intend to do any data processing with the slots from the intent.  Reference the exampleSkill.py for the minimum required content.

Your module name should match the name of the intent you want to call minus your snips user name.  So, if your skill is called 'snipsuser:turnOnLights', your module name should be 'turnOnLights.py'
