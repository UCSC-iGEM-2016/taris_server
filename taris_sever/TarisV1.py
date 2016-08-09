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
import pickle
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setupDB import bioDec, changeLog, Base, logBase

setData = {
  'pH': '5',
  'temp': '6',
  'timeHoldFor': '60'
}
# Equivalent to getting info from DB
try:
  myUserData = pickle.load(open('mySetThings.p', 'rb'))
  setData['pH'] = myUserData['pH']
  setData['temp'] = myUserData['temp']
  tryLoad = True
except:
  pickle.dump(setData, open('mySetThings.p', 'wb'))
  print('Created mySetThings.p pickle.') 
  pass



app = Flask(__name__)

class Taris_SW:


    def __init__ (self):
        pass

    @app.route('/', methods=['GET'])
    def homePage():
      '''
      GETS and POSTS the main homepage of the website along with the data info
      :return: index.html with passed currentSetPH
      '''
      print('Going to homePage (index.html)')
      try:
          # Get the last data that was changed by user
          lastData = Taris_SW.getProtocol()
          print('got lastData')
          currentSetPH = lastData.setPH
          currentSetTemp = lastData.setTemp
          print('last data ph and temp grabbed')
      except:
          print('Could not query data in /  (home)')
          currentSetPH = 7
          currentSetTemp = 50
          print('setting the ph to 7 and temp to 50 because no database')
          pass

      print('rendering index.html')
      return render_template('index.html', ph=currentSetPH, temp=currentSetTemp)

    #############################################################################################
    #This part of the program was inspired by Simba.
    # /receive and /send aim to post data to the dictionary we have
    #
    # This is a test to see if we can make code the user enters save into the global dictionary/

    @app.route('/receive')
    def hello_world():
        global data
        return jsonify(data)

    @app.route('/setProtocol', methods=['POST'])
    def setProtocol():
      '''
      setProtocol is the POST method of the paramas page.
      if the password is correct then the data will be committed to the changeLogDB.
      :return: A string 'success' is returned as a check that the data was processed to the db
      '''
      # Process a JSON. Put JSON data in a database.
      try:
        # try the passcode
        if request.form.get('pass') == 'pavlesucks':  # Check to see if the user knows the password.
          # If the user is validated by the password then
          setPH = request.form.get('pH')
          setTemp = request.form.get('temp')
          timeHold = request.form.get('timeHoldFor')
          #print('ph, temp, and hold time were got')
          ######### Put things into the DB ###############--#
          mytime = time.strftime('%D %H:%M:%S')  # get server time in String form
          #print('server time was got:' + mytime)
          user = 'colintest'
          passcode = 'KingPickler'
          # Create changeLog.db object to be added
          new_data = changeLog(timeLog=mytime, username=user, password=passcode, setPH=setPH, setTemp=setTemp, timeHold=timeHold)
          #print('new data made for changeLog.db')
          session = Taris_SW.makeChangeEngine()  # Get a session from the method that makes sessions
          #print('Making session to connect to changeLog.db')
          session.add(new_data)  # Add data to changeLog database
          #print('data added to changelog db, please commit')
          # session.add(new_data)
          try:
            session.commit()
            #print('Recieved data added to changeLog.db.')
            currentUser = 'Colin'
            print('Set values/protocol changed by: ' + currentUser)
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
            myJSON = request.get_json(force=True) # myJSON is string not json
            print('request contained a json')
            #myJSON.json()
            realJSON = json.loads(myJSON)
            print('json loaded')
            #attachME = str(realJSON['payload']['pH'])
            #print('myJSON[payload][pH] is:' + attachME) # insert to test

            ######### Put things into the DB ###############--#
            mytime = time.strftime('%D %H:%M:%S') # get server time

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
            session = Taris_SW.makeBioreactorEngine()
            session.add(new_data)
            #session.add(new_data)
            session.commit()
            print('Recieved data added to database.')
        except:
            print("currentRecieve was called but the data was not sent to the database.")

        print('I finished currentRecieve') # The server mangager now knows that this method has finished.
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

        return render_template('plotsPH.html')

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
          lastProto = Taris_SW.getProtocol()
          loadSetPH = lastProto.setPH
          loadSetTemp = lastProto.setTemp
        except:
          print('Data failed to load from DB.')
          loadSetTemp = 'FAIL'
          loadSetPH = 'FAIL'
          
        return render_template('testParams.html', setPH = loadSetPH, loadTemp = loadSetTemp )

##########################$$$ Database Access Methods $$$##########################
    # These methods are database engines and access, see descriptions
    def makeBioreactorEngine():
        '''
        session maker for Bioreactor.db
        return: database session for Bioreactor.db
        '''
        engine = create_engine('sqlite:///Bioreactor.db')  # databaseName.db goes here
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        BioreactorDBsession = DBSession()
        return BioreactorDBsession
    
    def makeChangeEngine():
        '''
        session maker for changeLog.db
        return: database session for changLog.db
        '''
        newEngine = create_engine('sqlite:///changeLog.db')
        logBase.metadata.bind = newEngine
        DBSession = sessionmaker(bind=newEngine)
        changeSession = DBSession()
        return changeSession
    def getProtocol():
      '''
      Returns the last protocol that was committed. (most recent set ph and temp here)
      :return: current protocol in the changelog DB
      '''
      session = Taris_SW.makeChangeEngine()
      # http://stackoverflow.com/questions/8551952/how-to-get-last-record
      # last was inspired/copied from Stackoverflow user: miku, thank you miku
      last = session.query(changeLog).order_by(changeLog.timeLog.desc()).first()
      return last

    def getValues():
        '''
        WARNING : Gets all values of the database
        return: all database entries
        '''
        session = Taris_SW.makeBioreactorEngine()
        allBioData = session.query(bioDec).all()
        return allBioData

    def getLast():
        '''
        Gets the last entry in the database.
        return: last entry in the databsee
        '''
        session = Taris_SW.makeBioreactorEngine()
        # http://stackoverflow.com/questions/8551952/how-to-get-last-record
        # last was inspired/copied from Stackoverflow user: miku, thank you miku
        last = session.query(bioDec).order_by(bioDec.timedata.desc()).first()
        return last
##########################$$$ Database Access Methods $$$##########################

 


myTaris=Taris_SW()


if __name__ == '__main__':
    app.run()
