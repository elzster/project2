# import necessary libraries
import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sqlite3
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import json
from flask import url_for
from sqlalchemy import func
from sqlalchemy import or_

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Maps Setup
#################################################
mapkey = os.environ.get('MAPKEY', '') or "CREATE MAPKEY ENV"

#################################################
# Database Setup
#################################################

from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/nyc.sqlite"
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or "sqlite:///db/nyc.sqlite"
db = SQLAlchemy(app)
from .models import crashdata
Base = automap_base()
Base.prepare(db.engine, reflect=True)

###############################################
#########Html Routes for Web Server ###########
###############################################
####Landing Page####
@app.route("/")
def home():

    return render_template("dash.html")

###DashBoard MainPage####
@app.route("/dash/")
def dash():

    return render_template("dash.html")
###Comparison Page###
@app.route("/boroughcomp/")
def boroughcomp():

    return render_template("boroughcomp.html")

###Scope Description Page####
@app.route("/scope/")
def scope():

    return render_template("scope.html")
###HeatMap Page###
@app.route("/heatmap/")
def heatmap():
    return render_template("heatmap.html")
###Top 10 Roads Page###
@app.route("/top10/")
def bargraph():
    return render_template("topten.html")

###Contributing Factors Page###
@app.route("/contrib/")
def contrib():
    
    return render_template('contrib.html')

@app.route("/retrieval/")
def retrieval():
    
    return render_template('retrieval.html')

@app.route("/clusters/")
def clusters():
    
    return render_template('clusters.html')

@app.route("/team/")
def team():
    
    return render_template('team.html')

@app.route("/testing/")
def testing():
    
    return render_template('testing1.html')

@app.route("/sunburst/")
def sunburst():
    
    return render_template('sunburst.html')
################################################
##Route for GeoJson Data for Cloropleth Maps ###
################################################
#this route renders and reads geojson file
@app.route("/geojson/")
def showjson():

    filename = os.path.join(app.static_folder, 'js', 'cartodb.geojson')

    with open(filename) as test_file:
        data = json.load(test_file)
        
        return (data)
################################################
####Route for Cloropleth Data File Needed  #####
################################################
#this route renders and reads geojson file
@app.route("/bounds/")
def bounds():

    filename = os.path.join(app.static_folder, 'js', 'nyc.geojson')

    with open(filename) as test_file:
        data = json.load(test_file)
        
        return (data)
##############################################
############Master Datafile Set ##############
##############################################
@app.route("/datafile1/")
def datafile1():
    """Return the list of records in Table"""
    # Use Pandas to perform the sql query
    stmt = db.session.query(crashdata).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    json = df.to_json(orient='records')
    return (json)

##########################
##Dynamic Route for Borough ###
##########################
@app.route("/borough/<city>/")
def city_borough(city):
    """Return the list of records in Table"""
    resultsData = db.session.query(crashdata).\
                filter(crashdata.borough == (city[0].upper()+city[1:].lower())).all()

    listData = []
    # citylist = []
    # for city in db.session.query(crashdata.borough).distinct():
    #     citylist.append(city)

    for x in resultsData:
        list_dict = {}
        list_dict['borough'] = x.borough
        list_dict['on_street_name'] = x.on_street_name
        list_dict['latitude'] = x.latitude
        list_dict['longitude'] = x.longitude
        list_dict['zip_code'] = x.zip_code
        listData.append(list_dict)

    return jsonify(listData)


#########################################
###########NO NULL BOROUGHS##############
#########################################

#This route just gets the Boroughs and Lat and Long Coordinates
@app.route("/borough/")
def no_null():
    """Return the list of records in Table"""

    # results = db.session.query(nyc.borough, nyc.on_street_name, nyc.).\
    #     order_by(nyc.score.desc()).\
    #     limit(10).all()
    resultsNoNull = db.session.query(crashdata).\
        filter(or_(crashdata.borough=="Queens", crashdata.borough=="Brooklyn", crashdata.borough=="Manhattan", crashdata.borough=="Staten Island", crashdata.borough=="Bronx")).all()

    streetsNyc = []

    for x in resultsNoNull:
        list_dict = {}
        list_dict['borough'] = x.borough
        list_dict['on_street_name'] = x.on_street_name
        list_dict['latitude'] = x.latitude
        list_dict['longitude'] = x.longitude
        list_dict['zip_code'] = x.zip_code
        streetsNyc.append(list_dict)

    return jsonify(streetsNyc)
    
#####################################################
##############Different Values Testing###############
#####################################################
@app.route("/events/<miguel>/")
def variable_list(miguel):
    vartar = (miguel[0].upper()+miguel[1:].lower())
    """Return the list of records in Table"""
    #     order_by(nyc.score.desc()).\
    #     limit(10).all()
    queryresults = db.session.query(crashdata).\
        filter(crashdata.borough==vartar).all()

    streets = []

    list_dict = {}
    list_dict['borough'] = vartar
    list_dict['crash_events_killed'] = db.session.query(func.sum(crashdata.number_of_persons_killed)).\
    filter(crashdata.borough==vartar).all()
    list_dict['crash_events_injuries'] = db.session.query(func.sum(crashdata.number_of_persons_injured)).\
    filter(crashdata.borough==vartar).all()

    list_dict['total_injuries'] = db.session.query(func.count(crashdata.number_of_persons_injured)).\
    filter(crashdata.borough==vartar).all()

    list_dict['total_crashes'] = db.session.query(func.count(crashdata.id)).\
    filter(crashdata.borough==vartar).all()
    streets.append(list_dict)

    return jsonify(streets[0])

##################################################
############Summary Data Sheets###################
##################################################
#Summary Table Call
@app.route("/summary/<elie>/")
def the_room(elie):
    vartar = (elie[0].upper()+elie[1:].lower())
    
    """Return the list of records in Table"""
    
    #hmm... List of unique boroughs.
    # citylist = []
    # for city in db.session.query(crashdata.borough).distinct():
    #     citylist.append(city)


#Group By SQLAlchemy
    values = db.session.query(crashdata).\
        filter(crashdata.borough==vartar).\
        group_by(crashdata.zip_code).all()

    streets = []

    # for x in values:
    list_dict = {}
    list_dict['cyclist'] ={}
    list_dict['motorist']={}
    list_dict['pedestrian']={}
    list_dict['total']={}
    list_dict['borough'] = vartar

    #Queries to Add totals to List Object
    list_dict['borough_crashes'] = db.session.query(crashdata).\
    filter(crashdata.borough==vartar).count()

    list_dict['cyclist']['injured'] = db.session.query(func.sum(crashdata.number_of_cyclist_injured)).\
    filter(crashdata.borough==vartar).all()

    list_dict['cyclist']['killed'] = db.session.query(func.sum(crashdata.number_of_cyclist_killed)).\
    filter(crashdata.borough==vartar).all()

    list_dict['motorist']['injured'] = db.session.query(func.sum(crashdata.number_of_motorist_injured)).\
    filter(crashdata.borough==vartar).all()

    list_dict['motorist']['killed'] = db.session.query(func.sum(crashdata.number_of_motorist_killed)).\
    filter(crashdata.borough==vartar).all()

    list_dict['pedestrian']['injured'] = db.session.query(func.sum(crashdata.number_of_pedestrian_injured)).\
    filter(crashdata.borough==vartar).all()

    list_dict['pedestrian']['killed'] = db.session.query(func.sum(crashdata.number_of_pedestrian_killed)).\
    filter(crashdata.borough==vartar).all()

    list_dict['total']['injured'] = db.session.query(func.sum(crashdata.number_of_persons_injured)).\
    filter(crashdata.borough==vartar).all()

    list_dict['total']['killed'] = db.session.query(func.sum(crashdata.number_of_persons_killed)).\
    filter(crashdata.borough==vartar).all()

    streets.append(list_dict)
    #returns list of cities that can be used for plotly variables?
    return jsonify(streets)

##################################################################    
###Route to Pull Summary up On Staten Island due to string issues.    
@app.route("/summary/statenisland/")
def staten():
    vartar = "Staten Island"
#Group By SQLAlchemy
    values = db.session.query(crashdata).\
        filter(crashdata.borough==vartar).\
        group_by(crashdata.zip_code).all()

    streets = []

    # for x in values:
    list_dict = {}
    list_dict['cyclist'] ={}
    list_dict['motorist']={}
    list_dict['pedestrian']={}
    list_dict['total']={}
    list_dict['borough'] = vartar

    #Queries to Add totals to List Object
    list_dict['borough_crashes'] = db.session.query(crashdata).\
    filter(crashdata.borough==vartar).count()

    list_dict['cyclist']['injured'] = db.session.query(func.sum(crashdata.number_of_cyclist_injured)).\
    filter(crashdata.borough==vartar).all()

    list_dict['cyclist']['killed'] = db.session.query(func.sum(crashdata.number_of_cyclist_killed)).\
    filter(crashdata.borough==vartar).all()

    list_dict['motorist']['injured'] = db.session.query(func.sum(crashdata.number_of_motorist_injured)).\
    filter(crashdata.borough==vartar).all()

    list_dict['motorist']['killed'] = db.session.query(func.sum(crashdata.number_of_motorist_killed)).\
    filter(crashdata.borough==vartar).all()

    list_dict['pedestrian']['injured'] = db.session.query(func.sum(crashdata.number_of_pedestrian_injured)).\
    filter(crashdata.borough==vartar).all()

    list_dict['pedestrian']['killed'] = db.session.query(func.sum(crashdata.number_of_pedestrian_killed)).\
    filter(crashdata.borough==vartar).all()

    list_dict['total']['injured'] = db.session.query(func.sum(crashdata.number_of_persons_injured)).\
    filter(crashdata.borough==vartar).all()

    list_dict['total']['killed'] = db.session.query(func.sum(crashdata.number_of_persons_killed)).\
    filter(crashdata.borough==vartar).all()

    streets.append(list_dict)
    #returns list of cities that can be used for plotly variables?
    return jsonify(streets)

##################################################################    
###Route to Pull Top Ten RoadWays in Dataset###################### 
################################################################## 

@app.route("/topten/")
def roadways():
    # values = db.session.query(crashdata).\
    # group_by(crashdata.zip_code).all()
    roads = []

    list_dict = {}
    list_dict['top_ten'] = {}

    list_dict['top_ten'] = db.session.query(func.count(crashdata.on_street_name), crashdata.on_street_name, crashdata.latitude, crashdata.longitude, crashdata.borough).\
    group_by(crashdata.on_street_name).\
    order_by(func.count(crashdata.on_street_name).desc()).limit(10).all()
    
    roads.append(list_dict)

    return jsonify(roads) 

##################################################################  
############ Top 10 Contributing Factors #########################
##################################################################    
@app.route("/factors/")
def factoid():
    # values = db.session.query(crashdata).\
    # group_by(crashdata.zip_code).all()
    factors = []

    list_dict={}

    list_dict['factors'] = {}

    list_dict['factors'] = db.session.query(func.count(crashdata.contributing_factors), crashdata.contributing_factors, func.sum(crashdata.number_of_persons_injured), func.sum(crashdata.number_of_persons_killed),crashdata.borough).\
    group_by(crashdata.contributing_factors).\
    order_by(func.count(crashdata.contributing_factors).desc()).limit(10).all()
    
    del list_dict['factors'][1:3]

    factors.append(list_dict)

    

    return jsonify(factors) 

@app.route("/totals_boroughs/")
def totals_boro():
    
    
    borough_total = []

    list_dict = {}
    list_dict['borough_total'] = {}

    list_dict['borough_total'] = db.session.query(func.sum(crashdata.id), crashdata.borough).\
    group_by(crashdata.borough).\
    order_by(func.sum(crashdata.borough).desc()).all()
    
    borough_total.append(list_dict)

    return jsonify(borough_total) 

if __name__ == "__main__":
    app.run()