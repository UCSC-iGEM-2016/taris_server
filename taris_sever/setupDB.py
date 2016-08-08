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
#
#
#
################################################################




from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
 
app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Bioreactor.db'
db = SQLAlchemy(app)

class bioDec (db.Model):

    #Create the tablename that will be used to query the columns and rows later.
    __tablename__ = 'bio_Data'

    #Create the columns that will be used to input data from the parsed JSON file.
    #Primary key is a field in a table which uniquely identifies each row/record in a
    #database table. Primary keys must contain unique values. A primary value column cannot
    #have null values. A null value indicates that the value is unkown.
    timeData = db.Column('time', db.String, primary_key=True)
    temperature = db.Column('temperature', db.Integer)
    pH = db.Column('pH', db.Integer)
    NaOH = db.Column('NaOH', db.Integer)
    heater = db.Column('heater', db.Integer)
    inFlow = db.Column('inflow', db.Integer)
    outFlow = db.Column('outFlow', db.Integer)
    purifier = db.Column('purifier', db.Integer)

    def __init__(self, timeData, temperature, pH, NaOH, heater, inFlow, outFlow, purifier):
        '''
        Constructor method that allows user to create new example objects to add to database.
        '''
        self.timeData = timeData
        self.temperature = temperature
        self.pH = pH
        self.NaOH = NaOH
        self.heater = heater
        self.inFlow = inFlow
        self.outFlow = outFlow
        self.purifier = purifier

	#Creates the bio_Data database
    db.create_all()



app2 = Flask (__name__)
app2.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///changeLog.db'
db2 = SQLAlchemy(app2)

class changeLog(db2.Model):
	'''
	user_Log creates a database that will hold the name of the person that edits a parameter for the bioreactor.
	'''

	__tablename__ = 'userInfo'

	# timeLog will take the server time when a user changes a parameter. Similar to timeData in bioDec.
	timeLog = db2.Column('timeLog', db2.Integer, primary_key=True, )
	username = db2.Column('username', db2.String)
	password = db2.Column('password', db2.String)
	timeOn = db2.Column('timeOn', db2.String)
	changeValue = db2.Column('changeValue', db2.String)
	valueSet_to = db2.Column('valueSet_to',db2.String)

	def __init__(self, timeLog, username, password, timeOn, changeValue, valueSet_to):
		'''
		Constructor method that allows user to create new example objects to add to database.
		'''
		self.timeLog = timeLog
		self.username = username
		self.password = password
		self.timeOn = timeOn
		self.changeValue = changeValue
		self.valueSet_to = valueSet_to

	db2.create_all()