#############################################################
# setupDB.py:
#   The first application that creates our Bioreactor and changeLog databases.
#
#Date: August 8, 2016
#
#Written by:
#   Andrew Blair
#   Colin Hortman
#   Austin York
#   Lon Blauvelt
#   Henry Hinton
#
#Description:
#   This application creates two separate databases
#
#
#
################################################################
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite import DATETIME

Base = declarative_base()

class bioDec(Base):
    '''
    bioDec creates a database that will hold the parsed JSON files sent from the raspberry pi.
    '''
    # Create the tablename that will be used to query the columns and rows later.
    __tablename__ = 'bio_Data'

    # Create the columns that will be used to input data from the parsed JSON file.
    # Primary key is a field in a table which uniquely identifies each row/record in a
    # database table. Primary keys must contain unique values. A primary value column cannot
    # have null values. A null value indicates that the value is unkown.
    timeData = Column('time', DATETIME, primary_key=True)
    temperature = Column('temperature', Integer)
    pH = Column('pH', Integer)
    NaOH = Column('NaOH', Integer)
    heater = Column('heater', Integer)
    inFlow = Column('inflow', Integer)
    outFlow = Column('outFlow', Integer)
    purifier = Column('purifier', Integer)


logBase = declarative_base()
class changeLog(logBase):
    '''
	changeLog creates a database that will hold the updated parameters for the bioreactor.
	'''
    __tablename__ = 'userInfo'

    # timeLog will take the server time when a user changes a parameter. Similar to timeData in bioDec.
    timeLog = Column('timeLog', String, primary_key=True)
    username = Column('username', String)
    password = Column('password', String)
    setPH = Column('setPH', Integer)
    setTemp = Column('setTemp', Integer)
    timeHold = Column('timeHold', Integer)

# Create Databse
bioreactorEngine = create_engine('sqlite:///Bioreactor.db')
runBio = Base.metadata.create_all(bioreactorEngine)

logEngine = create_engine('sqlite:///changeLog.db')
changeLogEngine = logBase.metadata.create_all(logEngine)


##########################$$$ Database Access Methods $$$##########################
# These methods will imported into TarisV1.py with setupDB.py, allowing users to connect and work with the different databases.

def makeBioreactorSession():
    '''
    session maker for Bioreactor.db
    return: database session for Bioreactor.db
    '''
    global bioreactorEngine
    Base.metadata.bind = bioreactorEngine
    DBSession = sessionmaker(bind=bioreactorEngine)
    BioreactorDBsession = DBSession()
    return BioreactorDBsession


def makeChangeSession():
    '''
    session maker for changeLog.db
    return: database session for changLog.db
    '''
    global logEngine
    logBase.metadata.bind = logEngine
    DBSession = sessionmaker(bind=logEngine)
    changeSession = DBSession()
    return changeSession



#########
#Access and Query the database for last entries for the two datbases.

def getProtocol():
    '''
    Returns the last protocol that was committed. (most recent set ph and temp here)
    :return: current protocol in the changelog DB
    '''
    session = makeChangeSession()
    # http://stackoverflow.com/questions/8551952/how-to-get-last-record
    # last was inspired/copied from Stackoverflow user: miku, thank you miku
    last = session.query(changeLog).order_by(changeLog.timeLog.desc()).first()
    return last


def getValues():
    '''
    WARNING : Gets all values of the database
    return: all database entries
    '''
    valSession = makeBioreactorSession()
    allBioData = valSession.query(bioDec).all()
    return allBioData

def getLast():
    '''
    Gets the last entry in the database.
    return: last entry in the databsee
    '''
    lastSession = makeBioreactorSession()
    # http://stackoverflow.com/questions/8551952/how-to-get-last-record
    # last was inspired/copied from Stackoverflow user: miku, thank you miku
    last = lastSession.query(bioDec).order_by(bioDec.timeData.desc()).first()
    return last

def getBetweenDatetime(begin, end):
   '''
   Gets entries between two DATETIMES
   :param begin: DATETIME object startTime
   :param end: DATETIME object startTime
   :return: all entries between the two specified times
   '''
   bioDecSesh = makeBioreactorSession()
   #betweenData = bioDecSesh.query(bioDec).filter(and_(bioDec.timeData <= begin, bioDec.timeData>=end))
   #betweenData = bioDecSesh.query(bioDec).filter(bioDec.timeData.between(begin, end))
   betweenData = bioDecSesh.query(bioDec).filter(bioDec.timeData >= begin).filter(bioDec.timeData <= end)

   return betweenData


### Datetime object #####
from datetime import datetime

def mydatetimer(mytime):
    '''
    Uses import datetime
    Input String: from: time.strftime('%D %H:%M:%S')
    :return: A datetime object of the time passed in.
    '''
    year = int(mytime.split(' ')[0][6:])
    month = int(mytime.split(' ')[0][0:2])
    day = int(mytime.split(' ')[0][3:5])
    hour = int(mytime.split(' ')[1][0:2])
    minute = int(mytime.split(' ')[1][3:5])
    second = int(mytime.split(' ')[1][-2:])
    mydatetime = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    return mydatetime

####### graphicBR Imports ########
from bokeh.plotting import figure
from bokeh.embed import components

class graphicBR:
    '''
    This class aims to make graphs given a type, and two lists of data.
    '''
    def __init__(self, type, xVals, yVals, ):
        self.type = type
        self.xVals = xVals
        self.yVals = yVals

    def makeLineGraph(self):
        p = figure(plot_width=400, plot_height=400, x_axis_type='datetime', title=str(self.type) +" History")
        p.title_text_color = 'blue'
        p.xaxis.axis_label = 'Time (Zoom to Change)'
        p.xaxis.axis_label_text_color = 'blue'
        p.yaxis.axis_label = str(self.type)
        p.yaxis.axis_label_text_color = 'blue'
        p.line(self.xVals, self.yVals, line_width=2)
        script, div = components(p)
        return script, div

