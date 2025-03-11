# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine)

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
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON of precipitation data for the last 12 months."""
    
    # Find the most recent date in the dataset
    latest_date = session.query(func.max(Measurement.date)).first()[0]
    latest_date = dt.datetime.strptime(latest_date, "%Y-%m-%d")
    one_year_ago = latest_date - dt.timedelta(days=365)

    # Query precipitation data
    precipitation_data = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )

    # Convert results into dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    
    stations_query = session.query(Station.station).all()

    # Convert results into a list
    stations_list = [station[0] for station in stations_query]

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return JSON of temperature observations for the most active station for the last year."""
    
    # Find the most active station
    most_active_station = (
        session.query(Measurement.station)
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()[0]
    )

    # Find the most recent date
    latest_date = session.query(func.max(Measurement.date)).first()[0]
    latest_date = dt.datetime.strptime(latest_date, "%Y-%m-%d")
    one_year_ago = latest_date - dt.timedelta(days=365)

    # Query temperature data for the most active station
    temp_data = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == most_active_station)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )

    # Convert results into a list of dictionaries
    temp_list = [{date: tobs} for date, tobs in temp_data]

    return jsonify(temp_list)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    """Return JSON of TMIN, TAVG, and TMAX for a given date range."""
    
    # If no end date is provided, query for all dates greater than or equal to start
    if not end:
        temp_query = (
            session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs),
            )
            .filter(Measurement.date >= start)
            .all()
        )
    else:
        temp_query = (
            session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs),
            )
filter(Measurement.date >= start)
            .filter(Measurement.date <= end)
            .all()
        )

    # Convert results into a dictionary
    temp_dict = {
        "TMIN": temp_query[0][0],
        "TAVG": temp_query[0][1],
        "TMAX": temp_query[0][2],
    }

    return jsonify(temp_dict)


# Run the Flask app
if name == "__main__":
    app.run(debug=True)

