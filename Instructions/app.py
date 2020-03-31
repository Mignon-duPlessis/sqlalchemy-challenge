import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite",
connect_args={'check_same_thread': False}, echo=True)


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    return (
        f"Trip to Hawaii!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Docstring
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from the last data point in the database

    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation scores

    prcp_scores = (session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        order_by(Measurement.date).\
        all())# Query for the date and precipitation for the last year

    # Make a dictironary
    dict_precip = {date: prcp for date, prcp in prcp_scores}
    # JSONIFY the dictionary
    return jsonify(dict_precip)


@app.route("/api/v1.0/stations")
def stations():
    #Docstring
    """Return a list of stations."""
    stations = session.query(Station.station).all()

    # Convert into a list
    list_stations = list(np.ravel(stations))
    # JSONIFY the stations list
    return jsonify(list_stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    #Docstring
    """Return the dates and temperature observations from a year from
    the last data point"""

    # Calculate the date 1 year ago from the last data point

    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Looking at the station with highest observations
    temp_freq= session.query(Measurement.tobs).\
                                filter(Measurement.station=='USC00519281').\
                                filter(Measurement.date >= year_ago).\
                                all()

    # Convert into a list
    frequency_list = list(np.ravel(temp_freq))

    # JSONIFY the list and return
    return jsonify(frequency_list)


@app.route("/api/v1.0/<start>")
def start(start=None):
   # Docstring
   """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

   from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
   from_start_list=list(from_start)
   return jsonify(from_start_list)



@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
   # Docstring
   """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""

   between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
   between_dates_list=list(between_dates)
   return jsonify(between_dates_list)


if __name__ == "__main__":
    app.run(debug=True)