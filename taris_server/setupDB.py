#############################################################
# setupDB.py:
#   This application creates a database Bioreactor.db; it contains methods that can access and commit new data to
#  the database.
#   This application also contains a helper class that does graphing and a helper method that converts a specific string
#  to a DATETIME object.
#
# Date: September 8, 2016
#
# Written by:
#   Andrew Blair
#   Colin Hortman
#   Austin York
#   Lon Blauvelt
#   Henry Hinton
#
# Description:
#   This application creates one database with two tables.
################################################################
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite import DATETIME

################################### Set Up the Database ###################################

bioreactorEngine = create_engine('sqlite:///Bioreactor.db') # Engines are used to create and access the database.
Base = declarative_base() # A base is used to tie tables (classes that follow) to the same database.

class brStatusHistory(Base): #brStatus means bioreactor status
    '''
    brStatusHistory is a table that has a Base in the Bioreactor.db that will hold the parsed JSON files sent from the
    raspberry pi.
    It will hold every status that is sent from the bioreactor.
    '''
    __tablename__ = 'br_status' # Tablename will be used to query the columns and rows later.
    # Create the columns that will be used to input data from the parsed JSON file.
    # Primary key is a field in a table which uniquely identifies each row/record in a
    # database table. Primary keys must contain unique values. A primary value column cannot
    # have null values. A null value indicates that the value is unknown.
    timeData = Column('time', DATETIME, primary_key=True)
    temperature = Column('temperature', Integer)
    pH = Column('pH', Integer)
    heater = Column('heater', Integer)
    inPWM = Column('inPWM', Integer)
    inCurrent = Column ('inCurrent', Integer)
    outPWM = Column('outPWM', Integer)
    outCurrent = Column ('outCurrent', Integer)
    naohPWM = Column('naohPWM', Integer)
    naohCurrent = Column('naohCurrent', Integer)
    filterPWM = Column('filterPWM', Integer)
    filterCurrent = Column('filterCurrent', Integer)

class changeHistory(Base):
    '''
	changeHistory is a table responsible for storing all change requests.
	It will only record requests that are verified by a password.
	This table will be accessed to grab the updated parameters for the bioreactor. (Last Entry)
	'''
    __tablename__ = 'changeEntry'

    # timeLog will take the server time when a user changes a parameter. Similar to timeData in bioDec.
    timeLog = Column('timeLog', String, primary_key=True)
    username = Column('username', String)
    password = Column('password', String)
    setPH = Column('setPH', Integer)
    setTemp = Column('setTemp', Integer)
    timeHold = Column('timeHold', Integer)

runBio = Base.metadata.create_all(bioreactorEngine) # Creates Database
################################### End Database Set Up ###################################
############################ Access and Query Database Methods ############################
# These methods will imported into TarisV1.py with setupDB.py, allowing users to connect and work with the database
# and the tables within.

def makeBioreactorSession():
    '''
    A database session opens a connection to the database and allows for query or inserting data.
    return: database session for Bioreactor.db
    '''
    global bioreactorEngine
    Base.metadata.bind = bioreactorEngine
    DBSession = sessionmaker(bind=bioreactorEngine)
    BioreactorDBsession = DBSession()
    return BioreactorDBsession

def getProtocol():
    '''
    Returns the last protocol that was committed. (most recent set ph and temp here)
    :return: Most recent approved protocol/parameters stored.
    '''
    session = makeBioreactorSession()
    # http://stackoverflow.com/questions/8551952/how-to-get-last-record
    # last was inspired/copied from Stackoverflow user: miku, thank you miku
    last = session.query(changeHistory).order_by(changeHistory.timeLog.desc()).first()
    return last

def getValues():
    '''
    WARNING : Gets all values of the database
    return: all database entries
    '''
    valSession = makeBioreactorSession()
    allBioData = valSession.query(brStatusHistory).all()
    return allBioData

def getLast():
    '''
    Gets the last entry in the database.
    return: last entry in the database
    '''
    lastSession = makeBioreactorSession()
    # http://stackoverflow.com/questions/8551952/how-to-get-last-record
    # last was inspired/copied from Stackoverflow user: miku, thank you miku
    last = lastSession.query(brStatusHistory).order_by(brStatusHistory.timeData.desc()).first()
    return last

def getBetweenDatetime(begin, end):
   '''
   Gets entries between two DATETIMES in the brStatusHistory Table.
   :param begin: DATETIME object startTime
   :param end: DATETIME object endTime
   :return: all entries between the two specified times
   '''
   bioDecSesh = makeBioreactorSession()
   #betweenData = bioDecSesh.query(bioDec).filter(and_(bioDec.timeData <= begin, bioDec.timeData>=end))
   #betweenData = bioDecSesh.query(bioDec).filter(bioDec.timeData.between(begin, end))
   betweenData = bioDecSesh.query(brStatusHistory).filter(brStatusHistory.timeData >= begin).filter(brStatusHistory.timeData <= end)
   return betweenData

################################### End Access and Query Database Methods ###################################
### Datetime object #####
from datetime import datetime

def mydatetimer(mytime):
    '''
    A conversion to datetime from a string in this format : time.strftime('%D %H:%M:%S')
    :return: A datetime object of the time/date passed in.
    '''
    year = int(mytime.split(' ')[0][6:])
    month = int(mytime.split(' ')[0][0:2])
    day = int(mytime.split(' ')[0][3:5])
    hour = int(mytime.split(' ')[1][0:2])
    minute = int(mytime.split(' ')[1][3:5])
    second = int(mytime.split(' ')[1][-2:])
    mydatetime = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    return mydatetime

################################### Graphing Methods ###################################
from bokeh.plotting import figure
from bokeh.embed import components

class graphicBR:
    '''
    This class aims to make graphs given a type, and two lists of data.
    '''
    def __init__(self, type, xVals, yVals, title = ': Last 5 Minutes History'):
        self.type = type
        self.xVals = xVals
        self.yVals = yVals
        self.title = title

    def makeLineGraph(self, width=600, height=600):
        p = figure(plot_width=width, plot_height=height, x_axis_type='datetime', title=str(self.type) + self.title)
        p.title_text_color = 'blue'
        p.xaxis.axis_label = 'Time (Zoom to Change)'
        p.xaxis.axis_label_text_color = 'blue'
        p.yaxis.axis_label = str(self.type)
        p.yaxis.axis_label_text_color = 'blue'
        p.line(self.xVals, self.yVals, line_width=2)
        script, div = components(p)
        return script, div

################################### End Graphing Methods ###################################