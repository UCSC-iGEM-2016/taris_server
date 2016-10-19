# Taris Bioreactor Server Software

This is the Taris bioreactor web interface and the associated backend for the code powering the 2016 UCSC iGEM team.


Acknowledgements
----------------

Many thanks to the iGEM software/bioreactor teams:

* Austin York
* Colin Hortman
* Andrew Blair
* Lon Blauvelt


Use and Explanation of the Taris Server Code (TarisV1.py and setupDB.py)
------------------------------------------------------------------------
Taris_SW is the name of the class that holds the Flask routes and functions, which is the backend of the server (found in TarisV1.py)

To understand the functionality of the server and how to add or remove functionality of this file, please become familiar with the following modules, database structures, and/or tutorials:
Flask: Homepage, instalation, basic use: http://flask.pocoo.org/ AND through Step 6: http://flask.pocoo.org/docs/0.11/tutorial/
SQLalchemy: Homepage http://www.sqlalchemy.org/ AND through Part 6: http://pythoncentral.io/introductory-tutorial-python-sqlalchemy/
Bokeh (0.11.0): Homepage: http://bokeh.pydata.org/en/0.11.0/ AND at least: http://bokeh.pydata.org/en/0.11.0/docs/user_guide/plotting.html
 
Data Flow, Storage and Recall  
-----------------------------
A high level flow of information is: from some source (Raspberri Pi in our case), the source makes a POST request containing a json file.  This json file is parsed, information is collected and stored in the SQLalchemy database (Bioreactor.db), which contains a table called brStatusHistory (where the status of the bioreactor is stored).

First, in the TarisV1 Server file, there are several imports.  Second, There is a global dictionary, used entirely for user specifications.  Third, the main component is the Flask app.

We will skip directly to the third component because if you are reading farther than here, you are a programmer.  If you are not, you will find this dull and this is a good place to stop reading.  The program is comprised of an empty initialization and many routes.  The routes handle GET and POST requests from users and display our HTML web pages.  The POST requests are used for: collecting data, changing plot sizes, and setting the bioreactor to its conditions.

First we will discuss routes and their functionality.  Next we will dive into how POSTs work for reading and writing to the server.  There are three kinds of POSTs that will be discussed, two of these are communication with the bioreactor via the Raspberri Pi, the other is a POST that is called by an AJAX method within the params page.

Route Usage and Passing Database Information
---------------------------------------------
	Simple route requests such as those solely rendering a template are easy and require just one, return render_template(prettypage.html).  This however, is rarely as simple as it gets.  Commonly, you will want to display, or add, values that are stored in a server database.  
	Displaying data from the database (see database retrieval methods) in an html file is quite easy.  When a template is rendered, a number, string, or other objects can be passed through, into the html.  A name must be specified so that in the html it can be displayed.  For example, the home page ‘/’, look at the objects that are set in the render_template(‘index.html’, setPH = currentSetPH, setTemp = currentSetTemp, …).  setPH will become the name for the object that holds the value of currentSetPH.  currentSetPH is an object from Python that was grabbed from the database table ‘changeEntry’; it is the most recent pH that the user asked for.  By grabbing this value, and passing it through the render template, the site manager can now use ‘{{setPH}}’ inside of the index.html file.  This allows the server to display current and stored values from the database to a user.

Taris POSTing Usage and Intended Usefulnesss
--------------------------------------------
	The method POST is specified when a site manager would like to receive data from some source or change some server side object value.  In our case, we receive data from the Raspberri Pi that is hooked up to the circuit board that takes measurements.  What makes the POSTing really easy is JSON files.  JSON files are a file type that are used across many programming languages.  Between the method of POST and the highly used JSON, figuring out how to send and receive data to the bioreactor was not too hard.
	The easiest explanation of when to use a POST is examples.  There will be three examples presented: /currentRecieve (where the bioreactor’s Rasp. Pi sends to) and /currentPost (where the bioreactor reads from, for updated temperature and pH settings).  Pull up the github for TarisV1.py to follow along and understan POST methods.
	The Raspberri Pi (RP) is a powerful yet small computer that is capable of running feedback loops while sending current data to the server simultaneously.  The RP makes a POST request to the server and sends a JSON file; it POSTs this JSON to a place called ‘request.’  Looking inside the /currentRecieve method, inside the try block, the first executed line of code is stringJSON = request.get_json(force=True),what this means is get the JSON from the request handler and process it as a JSON.  The JSON is then loaded from its string form and you can follow the rest of the code to see how it is put into the database.  More discussion on how to put information into the database follows this section.
	The RP is also responsible for checking to see if a user has changed the bioreactor settings.  The settings that are allowed for the user to change are pH and temperature; this is to control the growth and production phases of our engineered bacterium.  The /currentPost shows how data is read from the server.  Again the use of JSON makes this a simple process.  When the method is called, the first try block loads in the most recent protocol data and extracts the pH, Temp and user data.  Then a dictionary (JSON is a type of dictionary with certain specified formatting such as comment and header keys).  The final line returns a josnified, if you will, dictionary.  By using this built in method, the dictionary is jsonified and POSTed to the request as before.  The RP reads from the request and processes this information, more is written on the RP and its exact code in another section.
	The final type of POST is for changing the global variable as well as the data that is displayed in the plots.  The two methods to look at while reading this paragraph are the /defaultGraph and /plotChange.  There are methods called AJAX discussed in the HTML explanation portion that call on these methods.  When called, the /defaultGraph method changes the boolean value held in the global dictionary to False.  True is the default and displays the last five minutes of data, while if False then there is user specification for how much data to veiw.  When the AJAX calls /plotChange, data is retrieved between the two specified time ranges and stored in the global variable.  What this allows is for the plots tabs to use the stored data if the boolean is False or go get the last five minutes if it is True.  By doing this, it is allows the users of the website to see informative graphs for the time ranges they desire.
