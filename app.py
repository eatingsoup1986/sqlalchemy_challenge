from operator import and_
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
#save reference tables
Measurement = Base.classes.measurement
Station = Base.classes.station


#Flask Routes
app = Flask(__name__)

# Create routes
@app.route("/")
def welcome():
    return """
    Welcome to the SQLAlchemy Challenge Hawaii Climate API!
    Available routes: <br>
    /api/v1.0/rain <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/&lt;start&gt; where start is a date in YYYY-MM-DD format <br> 
    /api/v1.0/&lt;start&gt;/&lt;end&gt; where start and end are dates in YYYY-MM-DD format
    """

#Route created for all rain data to be displayed
@app.route("/api/v1.0/rain")
def rain():
    session = Session(engine)

    results =   session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

    prcp_date_list = []

    for date, prcp in results:
        new_dict = {}
        new_dict[date] = prcp
        prcp_date_list.append(new_dict)

    session.close()

    return jsonify(prcp_date_list)

#Route created for all stations to be shown    
# Query all stations
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    stations = {}

    results = session.query(Station.station, Station.name).all()
    for s,name in results:
        stations[s] = name

    session.close()
 
    return jsonify(stations)


#route created for tobs
# Query for the dates and temperature values
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Get the last date contained in the dataset and date from one year ago
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year_date = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') \
                    - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    results =   session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= last_year_date).\
                order_by(Measurement.date).all()

    # Convert to list of dictionaries
    tobs_date_list = []

    for date, tobs in results:
        new_dict = {}
        new_dict[date] = tobs
        tobs_date_list.append(new_dict)

    session.close()

    return jsonify(tobs_date_list)


#route create from start date for temperature min/avg/max
@app.route("/api/v1.0/<start>")
def temp_range_start(start):
    """TMIN, TAVG, and TMAX per date starting from a starting date.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    session = Session(engine)

    return_list = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(return_list)


#route created for between two dates for temperature min/avg/max
@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start,end):
    """TMIN, TAVG, and TMAX per date for a date range.
    
    Args:
        start (string): A date string in the format %Y-%m-%d
        end (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    session = Session(engine)

    return_list = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(and_(Measurement.date >= start, Measurement.date <= end)).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(return_list)

if __name__ == '__main__':
    app.run(debug=True)