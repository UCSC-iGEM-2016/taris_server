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
import pickle

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
        '''GETS and POSTS the main homepage of the website along with the data info'''

        tryLoad = False
        try:
            myUserData = pickle.load(open('mySetThings.p', 'rb'))           #loads the current 'mySetThings.p' pickle
            ph = myUserData['pH']                                           #that was originally created
            temp = myUserData['temp']
            tryLoad = True
        except:
            pass
        if tryLoad == False:
            ph = 7
            temp = 50


        return render_template('index.html', ph=ph, temp=temp)

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
        #This method will be ran on request of the Params page.
        # This method will change the global setData variable and will create
        # a pickle to store it as well.
        #   The
        global setData
        setData['userdata'] = request.form.get('data')
        setData['pH'] = request.form.get('pH')
        setData['temp'] = request.form.get('temp')
        setData['timeHoldFor'] = request.form.get('timeHoldFor')

        pickle.dump(setData, open('mySetThings.p', 'wb'))


        #goGetUser = someGetOnlineUserCall()
        currentUser = 'Colin'
        print('Set values/protocol changed by: ' + currentUser)
        return 'success'

    @app.route('/currentRecieve')
    def currentRecieve():
        pass


    @app.route('/setToPIREAD')
    def setToPIREAD():
        global setData
        mySetToData= pickle.load(open('mySetThings.p', 'rb'))
        return jsonify(setData)
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
        #setPH = pickle.load()
        try:
            myUserData = pickle.load(open('mySetThings.p', 'rb'))
            loadSetPH = myUserData['pH']
            loadSetTemp = myUserData['temp']
            tryLoad = True
        except:
            print('No pickle found. /params')
            loadSetTemp = 1000
            loadSetPH = 77
            pass

        return render_template('paramsAJAX727.html', setPH = loadSetPH, loadTemp = loadSetTemp )


myTaris=Taris_SW()


if __name__ == '__main__':
    app.run()
