# Bokeh 0.11.0 NOT 12.0
#
# pickle 20 (two-zero)

from Bioreactor_Dec import Bioreactor_Data, Base

from sqlalchemy import create_engine

# Create engine to access bioreactor.db
engine = create_engine('sqlite:///Bioreactor.db')  #databaseName.db goes here
Base.metadata.bind = engine

from sqlalchemy.orm import sessionmaker

#myPHs contains a list of all the pH & time put into the DB

from bokeh.plotting import figure, output_file, show, save, curdoc
from bokeh.embed import components
import time
from datetime import datetime
import shutil

import pickle

from bokeh.models import Range1d
from numpy import asarray, cumprod, convolve, exp, ones
#from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, Slider, Select
from bokeh.driving import count



myPHScript = ''



class myDataHistory():
    def __init__(self, type):
        self.type = type #will be of type string : pH, temp, media flow
        self.myScript = ''
        self.myDiv= ''


    def mydatetimer(self, mytime):
        '''
        :return: A datetime object that is from: time.strftime('%D %H:%M:%S') that is passed in.
        '''
        year = int(mytime.split(' ')[0][6:])
        month = int(mytime.split(' ')[0][0:2])
        day = int(mytime.split(' ')[0][3:5])
        hour = int(mytime.split(' ')[1][0:2])
        minute = int(mytime.split(' ')[1][3:5])
        second = int(mytime.split(' ')[1][-2:])
        mydatetime = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
        return mydatetime

    def getValues(self):
        DBSession = sessionmaker()
        DBSession.bind = engine
        session = DBSession()
        session.query(Bioreactor_Data)
        myBioData = session.query(Bioreactor_Data).all()
        return myBioData

    def getLast(self):
        engine = create_engine('sqlite:///Bioreactor.db')
        DBSession = sessionmaker()
        DBSession.bind = engine
        session = DBSession()
        # http://stackoverflow.com/questions/8551952/how-to-get-last-record
        # last was inspired/copied from Stackoverflow user: miku, thank you miku
        last = session.query(Bioreactor_Data).order_by(Bioreactor_Data.timedata.desc()).first()
        return last


    def getOneValue(self):
        DBSession = sessionmaker()
        DBSession.bind = engine
        session = DBSession()
        session.query(Bioreactor_Data)
        currentPHdata = session.query(Bioreactor_Data).order_by(Bioreactor_Data.pH.desc()).first()
        return currentPHdata


    def getLastxMins(self, x):
        '''
        Gets the proper amount of data objects from when the user requsted to the las
        :param fromWhatTime: The timestamp that formatted: time.strftime('%D %H:%M:%S') this means date (year, month, day), hours, mins, secs
                x: last how many minutes of data
        :return: Last x mins of data (database objects in a list that still must be parsed).


        # Example Call
        last5Data = getLastxMins(5)
        xVals, yVals = [], []
        for data in last5Data:
            xVals.append(data.pH)
            yVals.append(data.timedata)
        graph(x,y)
        #
        '''
        engine = create_engine('sqlite:///Bioreactor.db')
        DBSession = sessionmaker()
        DBSession.bind = engine
        session = DBSession()
        # http://stackoverflow.com/questions/8551952/how-to-get-last-record
        # last was inspired/copied from Stackoverflow user: miku, thank you miku
        # get last entry:
        last = session.query(Bioreactor_Data).order_by(Bioreactor_Data.timedata.desc()).first()
        #important note: how many entries are there since the last

        secsOfData = x * 60
        lastXdata = session.query(Bioreactor_Data).order_by(Bioreactor_Data.timedata.desc())[0:secsOfData]
        return lastXdata



    def makeLineGraph(self, xVals, yVals, type):

        p = figure(plot_width=400, plot_height=400, x_axis_type='datetime', title=type +' History')

        p.title_text_color = 'blue'
        p.xaxis.axis_label = 'Time (Bokeh Format - Zoom to Change)'
        p.xaxis.axis_label_text_color = 'blue'
        p.yaxis.axis_label = type
        p.yaxis.axis_label_text_color = 'blue'

        p.line(xVals, yVals, line_width=2)

        return p


    def spinSpin(self):
        i = 0  #to keep track of how many times this loop loops
        while True:

            #output_file('myFirstPlot.html')

            xVals = []
            yPHVals, yTempVals = [], []
            last5data = self.getLastxMins(1)
            for data in last5data:
              yPHVals.append(data.pH)
              yTempVals.append(data.temperature)
              xVals.append(self.mydatetimer(data.timedata))


            #Create

            pHfig = self.makeLineGraph(xVals, yPHVals, 'pH')
            pHScript, pHDiv = components(pHfig)

            pickle.dump(pHScript, open('pHscript.p', 'wb')) #create pickle to use in other file
            pickle.dump(pHDiv, open('pHdiv.p', 'wb')) # ''  ''

            tempFig = self.makeLineGraph(xVals, yTempVals, 'Temperature')
            tempScript, tempDiv = components(tempFig)
            pickle.dump(tempScript, open('tempScript.p', 'wb'))
            pickle.dump(tempDiv, open('tempDiv.p', 'wb'))

            time.sleep(1)
            print(i)
            i += 1 # count loops

myPHthings = myDataHistory('pH')
myPHthings.spinSpin()
