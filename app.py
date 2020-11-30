#import modules
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

#setting base and variables
db = automap_base()
db.prepare(engine, reflect=True)
db.classes.keys()
Measurement = db.classes.measurement
Station = db.classes.station
session = Session(engine)

#setting flask
app = Flask(__name__)

#declaring variables
latestDate = (session.query(Measurement.date)
                .order_by(Measurement.date.desc())
                .first())
latestDate = list(np.ravel(latestDate))[0]

latestDate = dt.datetime.strptime(latestDate, '%Y-%m-%d')
latestYear = int(dt.datetime.strftime(latestDate, '%Y'))
latestMonth = int(dt.datetime.strftime(latestDate, '%m'))
latestDay = int(dt.datetime.strftime(latestDate, '%d'))

yearBefore = dt.date(latestYear, latestMonth, latestDay) - dt.timedelta(days=365)
yearBefore = dt.datetime.strftime(yearBefore, '%Y-%m-%d')

@app.route("/")
def home():
    return (f"SQLAlchemy API<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitaton<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"Start and End Dates are in following format: (yyyy-mm-dd)<br/>"
            f"/api/v1.0/<start><br/>"
            f"/api/v1.0/<start>/<end><br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())
    
    predata = []
    for result in results:
        predict = {result.date: result.prcp, "Station": result.station}
        predata.append(predict)

    return jsonify(predata)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    statdata = list(np.ravel(results))
    return jsonify(statdata)

@app.route("/api/v1.0/tobs")
def tobs():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())

    tobsdata = []
    for result in results:
        tobsdict = {result.date: result.tobs, "Station": result.station}
        tobsdata.append(tobsdict)

    return jsonify(tobsdata)

@app.route('/api/v1.0/<start>')
def start(start):
    calc = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*calc)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
                       .group_by(Measurement.date)
                       .all())

    datedata = []                       
    for result in results:
        datedict = {}
        datedict["Date"] = result[0]
        datedict["Low Temp"] = result[1]
        datedict["Avg Temp"] = result[2]
        datedict["High Temp"] = result[3]
        datedata.append(datedict)
    return jsonify(datedata)

@app.route('/api/v1.0/<start>/<end>')
def startEnd(start, end):
    calc = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*calc)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= end)
                       .group_by(Measurement.date)
                       .all())

    datedata = []                       
    for result in results:
        datedict = {}
        datedict["Date"] = result[0]
        datedict["Low Temp"] = result[1]
        datedict["Avg Temp"] = result[2]
        datedict["High Temp"] = result[3]
        datedata.append(datedict)
    return jsonify(datedata)

if __name__ == "__main__":
    app.run(debug=True)