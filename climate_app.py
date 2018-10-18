import numpy as np
import datetime as dt
import pandas as pd

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy import and_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct, String

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """ Query for the dates and temperature observations from the last year.
        Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
        Return the JSON representation of your dictionary. """

    """ Latest Date on record in string format"""
    last_measurement_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    """ Break down the latest date into interget year, month and day components """
    last_measurement_year   = int(last_measurement_date[0:4])
    last_measurement_month  = int(last_measurement_date[5:7])
    last_measurement_day    = int(last_measurement_date[8:11])

    """ Get the date 12 months ago from the lasest date on record """   
    last_year = dt.date(last_measurement_year, last_measurement_month, last_measurement_day) - dt.timedelta(days=365)

    """" Retrieve the last 12 months of precipitation data. """
    last_12_months_prcp = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= last_year).filter(and_(Measurement.date) <= last_measurement_date)


    # Create a dictionary from the row data and append to a list of all_passengers
    all_prcps = []

    for prcp in last_12_months_prcp:
        prcp_dict = {}

        prcp_dict["date"]           = prcp.date
        prcp_dict["precipitation"]  = prcp.prcp
        all_prcps.append(prcp_dict)

    return jsonify(all_prcps)

@app.route("/api/v1.0/stations")
def stations():
    """ Return a JSON list of stations from the dataset. """

    stations = session.query(Station)
    
    """ Create a dictionary from the row data """
    all_stations = []

    for station in stations:
        station_dict = {}

        station_dict["id"]          = station.id
        station_dict["station"]     = station.station
        station_dict["name"]        = station.name
        station_dict["latitude"]    = station.latitude
        station_dict["longitude"]   = station.longitude
        station_dict["elevation"]   = station.elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """ Return a JSON list of Temperature Observations (tobs) for the previous year."""

    """ Latest Date on record in string format"""
    last_measurement_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    """ Break down the latest date into interget year, month and day components """
    last_measurement_year   = int(last_measurement_date[0:4])
    last_measurement_month  = int(last_measurement_date[5:7])
    last_measurement_day    = int(last_measurement_date[8:11])

    """ Get the date 12 months ago from the lasest date on record """   
    last_year = dt.date(last_measurement_year, last_measurement_month, last_measurement_day) - dt.timedelta(days=365)
    
    """ Query the last 12 months of temperature observation """
    last_12_months_tobs = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
                                        filter(Measurement.date >= last_year).\
                                        filter(and_(Measurement.date) <= last_measurement_date)

 
 
    """ Save the query results as a Pandas DataFrame and set the index to the date column and drop 
        rows with missing data """
    temps_df = pd.DataFrame(last_12_months_tobs[:],columns = ["date", "station", "temperature"]).dropna()
    
    """ Convert the dataframe to dict """
    temps_dict = temps_df.to_dict(orient="records")

    return jsonify(temps_dict)

""" ------------------------------------------------------------------------------------------ """
if __name__ == '__main__':
    app.run(debug=True)