#####################################################################
#
# TarisV1.py:
#   GitHub: https://github.com/UCSC-iGEM-2016/taris_server
#
# Date: July 27, 2016
# Updated: Continually (latest update: August 22, 2016)
#
# Written by:
#   Austin York
#   Colin Hortman
#   Andrew Blair
#   Henry Hinton
#   Lon Blauvelt
# Advisor:
#   Simba Khadder
#
# Packages:
#   JustGage - animated gauges using RaphaelJS
#           Check http://www.justgage.com for official releases
#           Licensed under MIT.
#           @author Bojan Djuricic (@Toorshia)
#
# Description:
#   Runs the web site that interacts with the TarisV1 bioreactor.
#     The goal of Taris_SW is to be the server that allows users to change bioreactor
#     controls as well as looks at current levels in the bioreactor
#
# Open Source Goal:
#   This is a senior design project for the authors listed above.  The students listed are participating in a
#  competition that requires the code to be published as open source.  We hope that you find this code valuable
#  and it helps further your knowledge of the power of Python, creating a Flask server, and many other applications.
#####################################################################

from flask import Flask, render_template, request, jsonify, redirect
import json
import time
from datetime import datetime, timedelta

from setupDB import Base, changeHistory, brStatusHistory
from setupDB import makeBioreactorSession, getProtocol, getValues, getLast
from setupDB import graphicBR, mydatetimer, getBetweenDatetime

historyLog = {'customGraphpH': False,
              'customGraphtemp': False,
              'customGraphmotors': False,
              'customGraphall': False
              } #Global Variable for all to use. Esp used in the data history method, and specified graphs!

app = Flask(__name__)

class Taris_SW:
    def __init__(self):
        pass

    @app.route('/', methods=['GET'])
    def homePage():
        '''
        Gets the main homepage of the website.  The method first gets the most recent bioreactor status to display
        in gauges.  If it fails to get values it sets the gauges to zero - this allows the page to load rather than
        crash if the load fails.
        :return: index.html with current values
        #CHANGE_WHEN# The database names or columns are changed.
        '''
        # print('Going to homePage (index.html)') #A test case to see if the homepage can be directed to.
        try: # Get the last protocol that was changed by user (setTo values
            lastData = getProtocol() #TEST# print('got lastData')
            currentSetPH = lastData.setPH
            currentSetTemp = lastData.setTemp #TEST# print('last data ph and temp grabbed')
        except: # Set the set pH and temp to 0 instead of crashing.
            print('Could not one or more of: -- getProtocol, set ph, temp from last data')
            currentSetPH = 0
            currentSetTemp = 0
            print('setting the ph to 0 and temp to 0 because error in /')
            pass
        try: # Get the most rececnt bioreactor data
            lastBRdata = getLast() #TEST# print('getLast succes')
            if lastBRdata == None:
                print('No data has been sent from PI, please add to DB ')
            currentpH = lastBRdata.pH
            currentTemp = lastBRdata.temperature
            inflowPWM = lastBRdata.inPWM
            filtermLs = lastBRdata.filterPWM
            outflowPWM = lastBRdata.outPWM
            basePWM = lastBRdata.naohPWM
        except: #Set to zero if the loading fails; zero is the standard error.
            currentpH = 0
            currentTemp = 0
            inflowPWM = 0
            filtermLs = 0
            outflowPWM = 0
            basePWM = 0
            print('Error thown in second try block of / (homepage)') # Print useful information when an error occurs.
        #print('rendering index.html')   # TEST # to see if render temp is wrong, but everything else is complete
        return render_template('index.html', setPH = currentSetPH, setTemp = currentSetTemp,
                               ph=currentpH, temp=currentTemp, basePWM = basePWM,
                               inflowPWM = inflowPWM, filtermLs = filtermLs, outflowPWM = outflowPWM
                               )

    @app.route('/currentPost')
    def currentPost():
        '''
        This is the URL that the bioreactor's raspberry pi reads from.  This method is used by the reactor to get
        the most recent user set values.
        :return: A JSON file that can be read by the pi. Contains set to values.
        '''
        try: # Load the last 'protocol' (last accepted change to the reactor) and pull the pH, temp, and user.
            lastProto = getProtocol()
            loadSetPH = lastProto.setPH
            loadSetTemp = lastProto.setTemp
            loadUser = lastProto.username
        except: # If the load fails, set values to FAIL so the BR will not change values.
            print('Data failed to load from DB in /currentPost') # Print useful error message
            loadSetTemp = 'FAIL'
            loadSetPH = 'FAIL'
            loadUser = 'FAIL'
        # postThis will be the format of the JSON that is read by the pi.
        postThis = {
            'comment' : "Hey bioreactor, this is the current desired things and user info.",
            'header' : {'toPIfromServer_sendSensorParams': True, 'date': time.strftime('%D %H:%M:%S')},
            'payload' : {'des_pH': loadSetPH, 'des_temp': loadSetTemp, 'user_changing': loadUser}
        }
        #print(postThis) # A test to see what postThis looks like (what the recieving end will see).
        return jsonify(postThis) # JSONify turns the Python object into a human readable object.

    @app.route('/currentRecieve', methods=["POST"])
    def currentRecieve():
        '''
        currentRecieve is called when the Raspberry Pi sends a json to the server.
        This post request is handled by loading the json data from request and committing it to the database
        with the associated information, in our case: Bioreactor.db (SQLalchemy database).
        :return: A string 'success' is returned as a check that the data was sent to the server
        '''
        #TEST# print('Recieved data at: /currentRecieve.')
        # Process a JSON. Put JSON data in a database.
        try:
            stringJSON = request.get_json(force=True)  # myJSON is string not json #TEST#print('request contained a json')
            realJSON = json.loads(stringJSON) #TEST#print('json loaded')
            ######### Put things into the DB ###############--#
            mytime = time.strftime('%D %H:%M:%S')  # Get server time.
            mytime = mydatetimer(mytime) # Make a datetime object to be stored in the database.

            temp = realJSON['payload']['temp']
            mypH = realJSON['payload']['pH']

            inPWM = realJSON['payload']['inMotor']['PWM']
            inCurrent = realJSON['payload']['inMotor']['current']
            outPWM = realJSON['payload']['outMotor']['PWM']
            outCurrent = realJSON['payload']['outMotor']['current']
            naohPWM = realJSON['payload']['naohMotor']['PWM']
            naohCurrent = realJSON['payload']['naohMotor']['current']
            filterPWM = realJSON['payload']['filterMotor']['PWM']
            filterCurrent = realJSON['payload']['filterMotor']['current']
            # Create a new data item to be added to the database.
            new_data = brStatusHistory(temperature= temp, pH = mypH, timeData= mytime, inPWM = inPWM, inCurrent= inCurrent,
                              outPWM = outPWM, outCurrent = outCurrent, naohPWM = naohPWM, naohCurrent = naohCurrent,
                              filterPWM = filterPWM, filterCurrent= filterCurrent)
            #TEST# print('new data made')
            session = makeBioreactorSession() # Open a session for the database.
            session.add(new_data) # Add new data to the database.
            session.commit() # Commit data into the database.
            #print('Recieved data added to database.') #TEST to see if the try block is working.
        except:
            print("currentRecieve was called but the data was not sent to the database.") # Usefull error message
            return 'failure' # Return failure allows for the calling method to see that the request was not handled as expected
        #TEST# print('I finished currentRecieve')  # Test case, if printed either the return is wrong or the POST call is.
        return 'success' # If no error are thrown, then return 'success' (string) because the caller can read this.

    ####################### Console page with debugging functionality ###################################

    @app.route('/console')
    def consolePage():
        '''GETS the console page via website'''
        return render_template('console.html')

    ################################### Data Visualization Tabs ####################################

    @app.route('/plots')
    def plotPage():
        '''
        Makes all the plots, this is a tad slow.
        Look at other graph routes to understand how graphs are made!
        '''
        ## make both pH and temp plots and display ## #TEST# print('Making pH plot and temp plot')
        global historyLog
        if historyLog['customGraphall'] == False: # Check to see if user has requested a time range
            minsOfData = 5 # How many minutes of data do you want as your default history? <-- Default
            end =  mydatetimer(time.strftime('%D %H:%M:%S')) # End with the most current time
            begin = end - timedelta(minutes=minsOfData)
            histData = getBetweenDatetime(begin, end) #list of db entries between the spedified times
            title  = ': Last 5 Minutes History'
        if historyLog['customGraphall'] == True: # Check to see if user has requested a time range
            histData = historyLog['histDataall']
            title  = ': Requested History'
        xVals, pHVals, tempVals = [], [], []
        inflowPWMs, outflowPWMs, naohPWMs, filterPWMs = [], [], [], []
        for data in histData:
            '''Put all relevant data in lists'''
            pHVals.append(data.pH) #TEST#print('append pH success')
            tempVals.append(data.temperature)
            xVals.append(data.timeData)
            inflowPWMs.append(data.inPWM)  # TEST# print('append pH success')
            outflowPWMs.append(data.outPWM)
            naohPWMs.append(data.naohPWM)
            filterPWMs.append(data.filterPWM)
        pHGraphObject = graphicBR('pH', xVals, pHVals, title)
        tempGraphObject = graphicBR('Temperature', xVals, tempVals, title) # Graph lists using class found in setupDB
        pHScript, pHDiv = pHGraphObject.makeLineGraph(800, 250) #TEST#print(pHDiv)
        tempScript, tempDiv = tempGraphObject.makeLineGraph(800, 250) #TEST#print(pHDiv)
        # Load up plots for the plots homepage and pass them in.
        inFlowGraphObject = graphicBR('In Flow Motor PWM', xVals, inflowPWMs, title)  # Make graphic object for inflow PWM.
        inFlowScript, inFlowDiv = inFlowGraphObject.makeLineGraph(800, 250) # Make line graph from the object.
        outFlowGO = graphicBR('Out Flow Motor PWM', xVals, outflowPWMs, title)
        outFlowScript, outFlowDiv = outFlowGO.makeLineGraph(800, 250)
        naohGO = graphicBR('NaOH Motor PWM', xVals, naohPWMs, title)
        naohScript, naohDiv = naohGO.makeLineGraph(800, 250)
        filterGO = graphicBR('Filter Motor PWM', xVals, outflowPWMs, title)
        filterScript, filterDiv = filterGO.makeLineGraph(800, 250)
        # Pass all of the graphs of the motors to plotsMotor.html to display.
        return render_template('plots.html', pHScript = pHScript, pHDiv = pHDiv,
                               tempScript = tempScript, tempDiv = tempDiv, inFlowDiv=inFlowDiv, inFlowScript=inFlowScript,
                               naohDiv=naohDiv, naohScript=naohScript,
                               outFlowDiv=outFlowDiv, outFlowScript=outFlowScript,
                               filterDiv=filterDiv, filterScript=filterScript
                                )

    @app.route('/plotsPH')
    def phPage():
        '''
        Make and display a pH plot vs time.
        :return: graph of pH, either specified or default of last 5 mins
        ''' #TEST# print('pH plot requested')
        global historyLog
        if historyLog['customGraphpH'] == False: # Check to see if user has requested a time range, proceed if not
            minsOfData = 5 # How many minutes of data do you want? <-- Default
            end =  mydatetimer(time.strftime('%D %H:%M:%S')) # End with the most current time
            begin = end - timedelta(minutes=minsOfData)
            histData = getBetweenDatetime(begin, end)
            title = ': Last 5 Minutes History'
        if historyLog['customGraphpH'] == True: # Check to see if user has requested a time range, proceed if so
            histData = historyLog['histDatapH']
            title  = ': Requested History'
        xVals, yVals = [], []
        for data in histData:
            '''Put all relevant data in lists'''
            yVals.append(data.pH) #TEST#print('append pH success')
            xVals.append(data.timeData)
        # Graph lists of data using class found in setupDB
        myGraphObject = graphicBR('pH', xVals, yVals, title)
        pHScript, pHDiv = myGraphObject.makeLineGraph(800, 300) #TEST#print(pHDiv)
        return render_template('plotsPHbokeh.html', pHDiv = pHDiv, pHScript = pHScript)

    @app.route('/plotsTemp')
    def tempPage():
        '''Make and display a temp plot vs time'''
        #TEST# print('temp plot requested')
        if historyLog['customGraphtemp'] == False:
            minsOfData = 5 # How many minutes of data do you want? <-- Default
            end =  mydatetimer(time.strftime('%D %H:%M:%S')) # End with the most current time
            begin = end - timedelta(minutes=minsOfData)
            histData = getBetweenDatetime(begin, end) #print('got last five mins of BR data')
            title  = ': Last 5 Minutes History'
        if historyLog['customGraphtemp'] == True:
            histData = historyLog['histDatatemp']
            title  = ': Requested History'
        xVals, yVals = [], []
        for data in histData:
            '''Put all relevant data in lists'''
            yVals.append(data.temperature) #TEST# print('append pH success')
            xVals.append(data.timeData)
        myGraphObject = graphicBR('Temperature', xVals, yVals, title) # Graph lists using class found in setupDB
        tempScript, tempDiv = myGraphObject.makeLineGraph(800, 300) #TEST# print(pHDiv)
        return render_template('tempPlotBokeh.html', tempDiv = tempDiv, tempScript = tempScript)

    @app.route('/plotsMotors')
    def motorsPage():
        '''Make and display all the motors' PWMs vs time''' #TEST# print('motor plots requested')
        if historyLog['customGraphmotors'] == True:
            histData = historyLog['histDatamotors']
            title  = ': Requested History'
        if historyLog['customGraphmotors'] == False:
            minsOfData = 5  # How many minutes of data do you want? <-- Default
            end = mydatetimer(time.strftime('%D %H:%M:%S'))  # End with the most current time
            begin = end - timedelta(minutes=minsOfData)
            histData = getBetweenDatetime(begin, end)  #print('got last five mins of BR data') #TEST query call#
            title  = ': Last 5 Minutes History'
        xVals, inflowPWMs, outflowPWMs, naohPWMs, filterPWMs = [], [], [], [], [] # Empty lists for x and y values.
        for data in histData:
            '''Put all relevant data in lists'''
            inflowPWMs.append(data.inPWM)  # TEST# print('append value from histData success')
            outflowPWMs.append(data.outPWM)
            naohPWMs.append(data.naohPWM)
            filterPWMs.append(data.filterPWM)
            xVals.append(data.timeData) # Time data: datetime object (graphicBR will only plot with a datetime object).
        inFlowGraphObject = graphicBR('In Flow Motor PWM', xVals, inflowPWMs, title)  # Make graphic object for inflow PWM.
        inFlowScript, inFlowDiv = inFlowGraphObject.makeLineGraph(800, 250) # Make line graph from the object.
        outFlowGO = graphicBR('Out Flow Motor PWM', xVals, outflowPWMs, title)
        outFlowScript, outFlowDiv = outFlowGO.makeLineGraph(800, 250)
        naohGO = graphicBR('NaOH Motor PWM', xVals, naohPWMs, title)
        naohScript, naohDiv = naohGO.makeLineGraph(800, 250)
        filterGO = graphicBR('Filter Motor PWM', xVals, outflowPWMs, title)
        filterScript, filterDiv = filterGO.makeLineGraph(800, 250)
        # Pass all of the graphs of the motors to plotsMotor.html to display.
        return render_template('plotsMotor.html', inFlowDiv=inFlowDiv, inFlowScript=inFlowScript,
                               naohDiv=naohDiv, naohScript=naohScript,
                               outFlowDiv=outFlowDiv, outFlowScript=outFlowScript,
                               filterDiv=filterDiv, filterScript=filterScript)

    @app.route('/plotChange', methods=['POST'])
    def plotChange():
        start = request.form.get('start') # Must be in: hh/mm/ss  to create a datetime object.
        end = request.form.get('end')
        type = request.form.get('type') # Specify the type of graph that you want to change
        startDT, endDT = mydatetimer(start), mydatetimer(end)
        requestData = getBetweenDatetime(startDT, endDT)
        global historyLog
        historyLog['histData' + type] = requestData # only change the specific graph
        historyLog['customGraph' + type] = True # only change the specific graph
        return 'success'

    @app.route('/defaultGraph', methods=['POST'])
    def defaultGraph():
        global historyLog #TEST# print('resetting')
        type = request.form.get('type') #TEST# print('reset: ' + type)
        historyLog['customGraph' + type] = False # only reset the specific graph
        return 'success' #if using href rather than button: redirect('/plotsPH', code=302)

    ################################### Data Visualization Tabs End ####################################

    @app.route('/params')
    def paramsPage():
        '''
        The params page has a form in the html that is rendered that allows a user to make a change to the bioreactor.
        :return: Render a template with the last set values as the default.
        '''
        try: # Load the last user set pH and temp.
            lastProto = getProtocol()
            loadSetPH = lastProto.setPH
            loadSetTemp = lastProto.setTemp
        except: # Print an error message to the server, do not crash by setting the temp and ph to fail.
            print('Data failed to load from DB in /params.')
            loadSetTemp = 'FAIL'
            loadSetPH = 'FAIL'
        return render_template('testParams.html', setPH=loadSetPH, loadTemp=loadSetTemp)

    @app.route('/setProtocol', methods=['POST'])
    def setProtocol():
        '''
        setProtocol is the POST method of the paramas page.
        If the password is correct then the data will be committed to the changeLogDB.
        :return: A string 'success' is returned as a check that the data was processed to the db
        '''
        try: # Try the passcode and committing new data to the database.
            if request.form.get('pass') == 'pavlesucks':  # Check to see if the user knows the password.
                # If the user is validated by the password then do the following (get and set data):
                setPH = request.form.get('pH')
                setTemp = request.form.get('temp')
                user = request.form.get('user') #TEST# print('ph, temp, and hold time were got')
                ######### Put things into the DB ###############--#
                mytime = time.strftime('%D %H:%M:%S')  # get server time in String form #TEST# print('server time was got:' + mytime)
                passcode, timeHold = 'KingPickler', 1 #Placeholders

                # Create changeLog.db object to be added
                new_data = changeHistory(timeLog=mytime, username=user, password=passcode, setPH=setPH, setTemp=setTemp,
                                     timeHold=timeHold)
                #TEST# print('new data made for changeLog.db')
                session = makeBioreactorSession()  # Get a session from the method that makes sessions #TEST# print('Making session to connect to changeLog.db')
                session.add(new_data)  # Add data to changeLog database #TEST# print('data added to changelog db, please commit')
                try:
                    session.commit() #TEST# print('Recieved data added to changeLog.db.')
                    print('Set values/protocol changed by: ' + user)
                except:
                    print('Error in committing data.')
                    return 'bad commit' #Informative return to caller.
            else: # The password is false
                print('The password was incorrect')
                return 'bad password' # Informative return to caller.
        except:
            print('Data was not added because an error was thrown in /setProtocol')
            return 'exception hit' # Do not return sucess if an error was thrown.
        #TEST# print('I finished currentRecieve')  # The server mangager now knows that this method has finished.
        return 'success' # If the password was correct, and the data was committed.

myTaris = Taris_SW()

if __name__ == '__main__':
    app.run()
