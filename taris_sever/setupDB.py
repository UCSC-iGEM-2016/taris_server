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
    timeData = Column('time', String, primary_key=True)
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


