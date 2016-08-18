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
from datetime import datetime

from setupDB import bioDec, changeLog, Base, logBase
from setupDB import makeBioreactorSession, makeChangeSession, getProtocol, getValues, getLast
from setupDB import graphicBR, mydatetimer, getBetweenDatetime


app = Flask(__name__)


class Taris_SW:
    def __init__(self):
        pass

    @app.route('/', methods=['GET'])
    def homePage():
        '''
        GETS and POSTS the main homepage of the website along with the data info
        :return: index.html with passed currentSetPH
        #CHANGE_WHEN# The database names or columns are changed.
        '''
        print('Going to homePage (index.html)')
        try: # Get the last protocol that was changed by user (setTo values
            lastData = getProtocol() #TEST# print('got lastData')
            currentSetPH = lastData.setPH
            currentSetTemp = lastData.setTemp #TEST#print('last data ph and temp grabbed')
        except:
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
        except: #Set to zero; zero is the standard error.
            currentpH = 0
            currentTemp = 0
            inflowPWM = 0
            filtermLs = 0
            outflowPWM = 0
            basePWM = 0
            print('Error thown in second try block of / (homepage)')
        #TEST to see if render temp is wrong #print('rendering index.html')
        return render_template('index.html', setPH = currentSetPH, setTemp = currentSetTemp,
                               ph=currentpH, temp=currentTemp, basePWM = basePWM,
                               inflowPWM = inflowPWM, filtermLs = filtermLs, outflowPWM = outflowPWM
                               )

    @app.route('/currentPost')
    def hello_world():
        try:
            lastProto = getProtocol()
            loadSetPH = lastProto.setPH
            loadSetTemp = lastProto.setTemp
            loadUser = lastProto.username
        except:
            print('Data failed to load from DB in /currentPost')
            loadSetTemp = 'FAIL'
            loadSetPH = 'FAIL'
        postThis = {
            'comment' : "Hey bioreactor, this is the current desired things and user info.",
            'header' : {'toPIfromServer_sendSensorParams': True, 'date': time.strftime('%D %H:%M:%S')},
            'payload' : {'des_pH': loadSetPH, 'des_temp': loadSetTemp, 'user_changing': loadUser}
        }

        print(postThis)
        return jsonify(postThis)

    @app.route('/currentRecieve', methods=["POST"])
    def currentRecieve():
        '''
        currentRecieve is called when the Raspberry Pi sends a json to the server
        This post request is handled by loading the json data and committing it to the Bioreactor.DB
        :return: A string 'success' is returned as a check that the data was sent to the server
        '''
        #TEST# print('Recieved data at: /currentRecieve.')
        # Process a JSON. Put JSON data in a database.
        try:
            stringJSON = request.get_json(force=True)  # myJSON is string not json #TEST#print('request contained a json')
            realJSON = json.loads(stringJSON) #TEST#print('json loaded')
            ######### Put things into the DB ###############--#
            mytime = time.strftime('%D %H:%M:%S')  # get server time
            mytime = mydatetimer(mytime)

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

            new_data = bioDec(temperature= temp, pH = mypH, timeData= mytime, inPWM = inPWM, inCurrent= inCurrent,
                              outPWM = outPWM, outCurrent = outCurrent, naohPWM = naohPWM, naohCurrent = naohCurrent,
                              filterPWM = filterPWM, filterCurrent= filterCurrent)
            #TEST# print('new data made')
            session = makeBioreactorSession()
            session.add(new_data)
            session.commit()
            print('Recieved data added to database.')
        except:
            print("currentRecieve was called but the data was not sent to the database.")
        #TEST# print('I finished currentRecieve')  # Test case, if printed either the return is wrong or the POST call is.
        return 'success'


    #############################################################################################

    @app.route('/console')
    def consolePage():
        '''GETS the console page via website'''
        return render_template('console.html')


    ################################### Data Visualization Tabs ####################################
    @app.route('/plots')
    def plotPage():
        '''GETS the plot page'''
        ## make both pH and temp plots and display ## #TEST# print('Making pH plot and temp plot')
        minsOfData = 5 # How many minutes of data do you want? <-- Default
        end =  mydatetimer(time.strftime('%D %H:%M:%S')) # End with the most current time
        begin = datetime(year=end.year, month=end.month, day=end.day,
                         hour=end.hour, minute=end.minute - minsOfData, second=end.second) # End - minsOfData minutes
        lastMinsOfData = getBetweenDatetime(begin, end) #list of db entries between the spedified times
        xVals, pHVals, tempVals = [], [], []
        for data in lastMinsOfData:
            '''Put all relevant data in lists'''
            pHVals.append(data.pH) #TEST#print('append pH success')
            tempVals.append(data.temperature)
            xVals.append(data.timeData)
        pHGraphObject = graphicBR('pH', xVals, pHVals)
        tempGraphObject = graphicBR('Temperature', xVals, tempVals) # Graph lists using class found in setupDB
        pHScript, pHDiv = pHGraphObject.makeLineGraph() #TEST#print(pHDiv)
        tempScript, tempDiv = tempGraphObject.makeLineGraph() #TEST#print(pHDiv)
        return render_template('plots.html', pHScript = pHScript, pHDiv = pHDiv,
                               tempScript = tempScript, tempDiv = tempDiv
                                )

    @app.route('/plotsPH')
    def phPage():
        '''Make and display a pH plot vs time''' #TEST# print('pH plot requested')
        minsOfData = 5 # How many minutes of data do you want? <-- Default
        end =  mydatetimer(time.strftime('%D %H:%M:%S')) # End with the most current time
        begin = datetime(year=end.year, month=end.month, day=end.day,
                         hour=end.hour, minute=end.minute - minsOfData, second=end.second) # End - minsOfData minutes
        lastTwoData = getBetweenDatetime(begin, end)
        xVals, yVals = [], []
        for data in lastTwoData:
            '''Put all relevant data in lists'''
            yVals.append(data.pH) #TEST#print('append pH success')
            xVals.append(data.timeData)
        # Graph lists of data using class found in setupDB
        myGraphObject = graphicBR('pH', xVals, yVals)
        pHScript, pHDiv = myGraphObject.makeLineGraph() #TEST#print(pHDiv)
        return render_template('plotsPHbokeh.html', pHDiv = pHDiv, pHScript = pHScript)

    @app.route('/plotsTemp')
    def tempPage():
        '''Make and display a temp plot vs time'''
        #TEST# print('temp plot requested')
        minsOfData = 5 # How many minutes of data do you want? <-- Default
        end =  mydatetimer(time.strftime('%D %H:%M:%S')) # End with the most current time
        begin = datetime(year=end.year, month=end.month, day=end.day,
                         hour=end.hour, minute=end.minute - minsOfData, second=end.second) # End - minsOfData minutes
        lastTwoData = getBetweenDatetime(begin, end) #print('got last five mins of BR data')
        xVals, yVals = [], []
        for data in lastTwoData:
            '''Put all relevant data in lists'''
            yVals.append(data.temperature) #TEST# print('append pH success')
            xVals.append(data.timeData)
        myGraphObject = graphicBR('Temperature', xVals, yVals) # Graph lists using class found in setupDB
        tempScript, tempDiv = myGraphObject.makeLineGraph() #TEST# print(pHDiv)
        return render_template('tempPlotBokeh.html', tempDiv = tempDiv, tempScript = tempScript)

    @app.route('/plotsMotors')
    def motorsPage():
        '''Make and display a temp plot vs time''' #TEST# print('motor plots requested')
        minsOfData = 5  # How many minutes of data do you want? <-- Default
        end = mydatetimer(time.strftime('%D %H:%M:%S'))  # End with the most current time
        begin = datetime(year=end.year, month=end.month, day=end.day,
                         hour=end.hour, minute=end.minute - minsOfData, second=end.second)  # End - minsOfData minutes
        lastTwoData = getBetweenDatetime(begin, end)  # print('got last five mins of BR data')
        xVals, inflowPWMs, outflowPWMs, naohPWMs, filterPWMs = [], [], [], [], []
        for data in lastTwoData:
            '''Put all relevant data in lists'''
            inflowPWMs.append(data.inPWM)  # TEST# print('append pH success')
            outflowPWMs.append(data.outPWM)
            naohPWMs.append(data.naohPWM)
            filterPWMs.append(data.filterPWM)
            xVals.append(data.timeData)
        inFlowGraphObject = graphicBR('In Flow Motor PWM', xVals,
                                      inflowPWMs)  # Graph lists using class found in setupDB
        inFlowScript, inFlowDiv = inFlowGraphObject.makeLineGraph()
        outFlowGO = graphicBR('Out Flow Motor PWM', xVals, outflowPWMs)
        outFlowScript, outFlowDiv = outFlowGO.makeLineGraph()
        naohGO = graphicBR('NaOH Motor PWM', xVals, naohPWMs)
        naohScript, naohDiv = naohGO.makeLineGraph()
        filterGO = graphicBR('Filter Motor PWM', xVals, outflowPWMs)
        filterScript, filterDiv = filterGO.makeLineGraph()

        return render_template('plotsMotor.html', inFlowDiv=inFlowDiv, inFlowScript=inFlowScript,
                               naohDiv=naohDiv, naohScript=naohScript,
                               outFlowDiv=outFlowDiv, outFlowScript=outFlowScript,
                               filterDiv=filterDiv, filterScript=filterScript)

    @app.route('/plotsHeater')
    def heaterPage():
        # There is no data on the heater so nothing we can do here yet.
        return render_template('plotsHeater.html')

    ################################### Data Visualization Tabs ####################################

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
        try: # try the passcode
            if request.form.get('pass') == 'pavlesucks':  # Check to see if the user knows the password.
                # If the user is validated by the password then do the following (get and set data):
                setPH = request.form.get('pH')
                setTemp = request.form.get('temp')
                user = request.form.get('user') #TEST# print('ph, temp, and hold time were got')
                ######### Put things into the DB ###############--#
                mytime = time.strftime('%D %H:%M:%S')  # get server time in String form #TEST# print('server time was got:' + mytime)
                passcode, timeHold = 'KingPickler', 1 #Placeholders

                # Create changeLog.db object to be added
                new_data = changeLog(timeLog=mytime, username=user, password=passcode, setPH=setPH, setTemp=setTemp,
                                     timeHold=timeHold)
                #TEST# print('new data made for changeLog.db')
                session = makeChangeSession()  # Get a session from the method that makes sessions #TEST# print('Making session to connect to changeLog.db')
                session.add(new_data)  # Add data to changeLog database #TEST# print('data added to changelog db, please commit')
                try:
                    session.commit() #TEST# print('Recieved data added to changeLog.db.')
                    print('Set values/protocol changed by: ' + user)
                except:
                    print('Error in committing data.')
            else: # The password is false
                print('The password was incorrect')
        except:
            print('Data was not added because an error was thrown in /setProtocol')
        #TEST# print('I finished currentRecieve')  # The server mangager now knows that this method has finished.
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
    app.run()
