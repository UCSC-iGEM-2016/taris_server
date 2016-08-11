#####################################################################
#
# TarisV1.py:
#   The first version of Taris pushed to the GitHub
#
# Date: July 27, 2016
# Updated: continually (latest update: August 3, 2016)
#
# Written by:
#   Austin York
#   Colin Hortman
#   Andrew Blair
#   Henry Hinton
#   Lon Blauvelt
#
# Packages:
#   JustGage - animated gauges using RaphaelJS
#           Check http://www.justgage.com for official releases
#           Licensed under MIT.
#           @author Bojan Djuricic (@Toorshia)
#
#
# Description:
#   Runs the web site that interacts with the TarisV1 bioreactor.
#     The goal of Taris_SW is to be the server that allows users to change bioreactor
#     controls as well as looks at current levels in the bioreactor
#
#   To Be Continued...
#
#####################################################################

from flask import Flask, render_template, request, jsonify
import json
import time

from setupDB import bioDec, changeLog, Base, logBase
from setupDB import makeBioreactorSession, makeChangeSession, getProtocol, getValues, getLast
from setupDB import graphicBR, mydatetimer


app = Flask(__name__)


class Taris_SW:
    def __init__(self):
        pass

    @app.route('/', methods=['GET'])
    def homePage():
        '''
        GETS and POSTS the main homepage of the website along with the data info
        :return: index.html with passed currentSetPH
        '''
        print('Going to homePage (index.html)')
        try: # Get the last protocol that was changed by user (setTo values
            lastData = getProtocol()
            #print('got lastData')
            currentSetPH = lastData.setPH
            currentSetTemp = lastData.setTemp
            #print('last data ph and temp grabbed')
        except:
            print('Could not query data in /  (home)')
            currentSetPH = 7
            currentSetTemp = 50
            print('setting the ph to 7 and temp to 50 because error in /')
            pass
        try: # Get the most rececnt bioreactor data
            lastBRdata = getLast()
            print('getLast succes')
            if lastBRdata == None:
                print('No data has been sent from PI, please add to DB ')
            currentpH = lastBRdata.pH
            currentTemp = lastBRdata.temperature
        except:
            currentpH = 777
            currentTemp = 777
            print('Error thown in second try block of / (homepage)')
        print('rendering index.html')
        return render_template('index.html', setPH = currentSetPH, setTemp = currentSetTemp, ph=currentpH, temp=currentTemp)

    @app.route('/receive')
    def hello_world():
        global data
        return jsonify(data)

    @app.route('/currentRecieve', methods=["POST"])
    def currentRecieve():
        '''
        currentRecieve is called when the Raspberry Pi sends a json to the server
        This post request is handled by loading the json data and committing it to the Bioreactor.DB
        :return: A string 'success' is returned as a check that the data was sent to the server
        '''
        print('Recieved data at: /currentRecieve.')
        # Process a JSON. Put JSON data in a database.
        try:
            myJSON = request.get_json(force=True)  # myJSON is string not json
            print('request contained a json')
            # myJSON.json()
            realJSON = json.loads(myJSON)
            print('json loaded')
            # attachME = str(realJSON['payload']['pH'])
            # print('myJSON[payload][pH] is:' + attachME) # insert to test

            ######### Put things into the DB ###############--#
            mytime = time.strftime('%D %H:%M:%S')  # get server time

            temp = realJSON['payload']['temp']
            mypH = realJSON['payload']['pH']
            NaOH = 1
            heater = 1
            inFlow = 1
            outFlow = 1
            purifier = 1

            new_data = bioDec(temperature=temp, pH=mypH, timeData=mytime,
                              NaOH=NaOH, heater=heater, inFlow=inFlow,
                              outFlow=outFlow, purifier=purifier)
            print('new data made')
            # mydatetime = mydatetimer(mytime)
            # new_data = Bioreactor_Data(temperature= temp,pH = mypH,timedata=mydatetime)
            session = makeBioreactorSession()
            session.add(new_data)
            # session.add(new_data)
            session.commit()
            print('Recieved data added to database.')
        except:
            print("currentRecieve was called but the data was not sent to the database.")

        print('I finished currentRecieve')  # The server mangager now knows that this method has finished.
        return 'success'

    @app.route('/setToPIREAD')
    def setToPIREAD():
        '''
        Get the last value in changeLog, tell the pi what to set to
        '''
        pass

    #############################################################################################

    @app.route('/console')
    def consolePage():
        '''GETS the console page via website'''
        return render_template('console.html')

    @app.route('/plots')
    def plotPage():
        '''GETS the plot page'''

        return render_template('plots.html')

    #############################################################
    #   The following methods contain the route calls for the graphic display if
    #   we wish to continue moving in that direction

    @app.route('/plotsPH')
    def phPage():
        '''Make and display a pH plot vs time'''
        print('pH plot requested')
        allBRdata = getValues() # replace with last 2 mins, not all
        print('got the all of BR data')
        xVals, yVals = [], []
        for data in allBRdata:
            '''Put all relevant data in lists'''
            yVals.append(data.pH)
            print('append pH success')
            datotimer = mydatetimer(data.timeData)
            print("datotimer made")
            xVals.append(datotimer)
        # Graph lists using class found in setupDB
        myGraphObject = graphicBR('pH', xVals, yVals)
        pHScript, pHDiv = myGraphObject.makeLineGraph()
        #print(pHDiv)
        return render_template('plotsPHbokeh.html', pHDiv = pHDiv, pHScript = pHScript)

    @app.route('/plotsTemp')
    def tempPage():

        return render_template('tempPlots.html')

    @app.route('/plotsMotors')
    def motorsPage():

        return render_template('plotsMotor.html')

    @app.route('/plotsHeater')
    def heaterPage():

        return render_template('plotsHeater.html')

    #############################################################

    @app.route('/params')
    def paramsPage():
        '''GETS parameter page'''
        try:
            lastProto = getProtocol()
            loadSetPH = lastProto.setPH
            loadSetTemp = lastProto.setTemp
        except:
            print('Data failed to load from DB.')
            loadSetTemp = 'FAIL'
            loadSetPH = 'FAIL'

        return render_template('testParams.html', setPH=loadSetPH, loadTemp=loadSetTemp)

    @app.route('/setProtocol', methods=['POST'])
    def setProtocol():
        '''
        setProtocol is the POST method of the paramas page.
        if the password is correct then the data will be committed to the changeLogDB.
        :return: A string 'success' is returned as a check that the data was processed to the db
        '''
        try:
            # try the passcode
            if request.form.get('pass') == 'pavlesucks':  # Check to see if the user knows the password.
                # If the user is validated by the password then
                setPH = request.form.get('pH')
                setTemp = request.form.get('temp')
                timeHold = request.form.get('timeHoldFor')
                user = request.form.get('user')
                # print('ph, temp, and hold time were got')
                ######### Put things into the DB ###############--#
                mytime = time.strftime('%D %H:%M:%S')  # get server time in String form
                # print('server time was got:' + mytime)
                passcode = 'KingPickler'
                # Create changeLog.db object to be added
                new_data = changeLog(timeLog=mytime, username=user, password=passcode, setPH=setPH, setTemp=setTemp,
                                     timeHold=timeHold)
                # print('new data made for changeLog.db')
                session = makeChangeSession()  # Get a session from the method that makes sessions
                # print('Making session to connect to changeLog.db')
                session.add(new_data)  # Add data to changeLog database
                # print('data added to changelog db, please commit')
                # session.add(new_data)
                try:
                    session.commit()
                    # print('Recieved data added to changeLog.db.')
                    currentUser = 'Colin'
                    print('Set values/protocol changed by: ' + user)
                except:
                    print('Error in committing data.')
            else:
                # The password is false
                print('The password was incorrect')
                # Play a gif that is about getting passwords wrong
        except:
            print('Data was not added because an error was thrown in /setProtocol')
        print('I finished currentRecieve')  # The server mangager now knows that this method has finished.
        return 'success'


    @app.route('/dataHistory')
    def dataHistory():
        return render_template('dataHistory.html')


    @app.route('/getHistoryData', methods=['POST'])
    def getHistroyData():
        #  data: {day: $("#day").val(), start: $("#start").val(), end:$("#end").val()},
        day = request.form.get('day')
        start = request.form.get('start')
        end = request.form.get('end')
        interval = request.form.get('interval')

        print("requested data from: " + str(day) + " " + str(start) + " " + str(end))
        return 'success'


myTaris = Taris_SW()

if __name__ == '__main__':
    app.run('0.0.0.0')
