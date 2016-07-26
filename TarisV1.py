#####################################################################
# TarisV1.py:
#   The first version of the iGEM 2016 bioreactor flask program
#
# Date: July 7, 2016
#
# Written by:
#   Austin York
#   Henry Hinton
#   Collin Hortman
#   Andrew Blair
#   Hannah Meyers
#
# Henry Fill this in...
# Description:
#   Runs the web site that interacts with the TarisV1 bioreactor via a raspberry pie
#
#
#
#
#####################################################################

from flask import Flask, render_template, request, url_for
from bokeh.plotting import figure, output_file, show, save
import pandas as pd
from bokeh.embed import components
import shutil
import pickle


app = Flask(__name__)

class Taris_SW:


    '''def __init__ (self, script, div):
        Taris_SW.script1 = script
        Taris_SW.div1 = div
    '''

    @app.route('/', methods=['GET','POST'])
    def homePage():
        '''GETS and POSTS the main homepage of the website along with the data info'''
        if request.method == "POST":

            ph = request.form['ph']
            temp = request.form['temp']

        else:
            '''default params/values'''
            ph = 7
            temp = 89


        return render_template('index.html', ph=ph, temp=temp)

    @app.route('/console')
    def consolePage():
        '''GETS the console page via website'''
        return render_template('console.html')

    @app.route('/plots')
    def plotPage():
        '''GETS the plot page'''

        return render_template('plots.html')

    @app.route('/plotsPH')
    def phPage():
        pHdiv = pickle.load(open('pHdiv.p', 'rb'))
        pHScript = pickle.load(open('pHscript.p', 'rb'))
        return render_template('plotsPH.html', phDiv = pHdiv, phScript = pHScript)


    @app.route('/plotsTemp')
    def tempPage():

        return render_template('tempPlots.html')

    @app.route('/plotsMotors')
    def motorsPage():

        return render_template('plotsMotor.html')

    @app.route('/plotsHeater')
    def heaterPage():

        return render_template('plotsHeater.html')

    @app.route('/params')
    def paramsPage():
        '''GETS parameter page'''

        return render_template('params.html')


myTaris=Taris_SW()




if __name__ == '__main__':
    app.run()