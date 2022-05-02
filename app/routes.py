"""Module to handle the routes.

Author: Qinyun Luo, 2022
"""

from cmath import nan
from flask import render_template
from app import app
from app.forms import SearchForm
from pymongo import MongoClient
from datetime import datetime, timedelta
import psycopg2

#Connect to mongodb
client = MongoClient('localhost',27017)
db = client.termproject5400
collection = db.restaurantall

#Connect to postgresql
conn = psycopg2.connect(
    host="localhost",
    port='5432',
    database="termproject5400",
    user="postgres",
    password="123")

#route for seach page
@app.route('/', methods=['GET', 'POST'])
def home():
    """Render the home page."""
    form = SearchForm()
    search_results = None
    search_count = None
    last_update_date = str(list(collection.find({},{"_id":0, "record_date":1}).sort("record_date", -1).limit(1)))[18:28]
    if form.validate_on_submit():
        #variables
        name_term = form.name.data
        zipcode_term = form.zipcode.data
          #variable - boro
        if form.boro.data == "-- ALL --":
            boro_term = "Manhattan|Bronx|Brooklyn|Queens|Staten Island|0"
        else:
            boro_term = form.boro.data
          #variable - critical
        if form.critical.data == "-- ALL --":
            critical_term = ["Critical","Not Critical","Not Applicable"]
        else:
            critical_term = [form.critical.data]
          #variable - sorting
        if form.sorting.data == "Restaurant Name":
            sorting_term = "dba"
        elif form.sorting.data == "Boro":
            sorting_term = "boro"
        elif form.sorting.data == "Zipcode":
            sorting_term = "zipcode"
        elif form.sorting.data == "Cuisine Type":
            sorting_term = "cuisine_description"
        else:
            sorting_term = "inspection_date"
          #variable - order
        if form.order.data == "Descending Order":
            order_term = -1
        else:
            order_term = 1
        startdate = form.startdate.data
        enddate = form.enddate.data
        #query
        query={"$and":[{"dba":{"$regex": name_term,"$options" :'i'}},
                       {"zipcode":{"$regex": zipcode_term,"$options" :'i'}},
                       {"boro":{"$regex": boro_term,"$options" :'i'}},
                       {"critical_flag": {"$in": critical_term}},
                       {"inspection_date": {"$gte": datetime.strptime(startdate.strftime('%Y-%m-%d'), '%Y-%m-%d')}},
                       {"inspection_date": {"$lte": datetime.strptime(enddate.strftime('%Y-%m-%d'), '%Y-%m-%d')}}
                       ]}
        #query results
        search_results = collection.find(query, sort=[(sorting_term, order_term)])
        #results count
        search_count = collection.count_documents(query)  
    return render_template(
        "home.html", form=form, search_results=search_results,search_count=search_count, last_update_date=last_update_date)


#route for analysis page
@app.route('/anlysis')
def analysis():
    cur = conn.cursor()
    #restaurant count
    cur.execute(f"SELECT COUNT(camis) FROM restaurants")
    restaurant_count = cur.fetchone()[0]
    #restaurant by boro
    cur.execute(f"SELECT boro, COUNT(DISTINCT camis) FROM restaurants GROUP BY boro ORDER BY COUNT(camis) DESC")
    restaurant_boro = cur.fetchall()
    r_boros = []
    r_boros_values = []
    for i in restaurant_boro:
        if i[0] != "0":
            r_boros.append(i[0])
            r_boros_values.append(i[1])
    #restaurant by cuisine
    cur.execute(f"SELECT cuisine_description, COUNT(DISTINCT camis) FROM restaurants GROUP BY cuisine_description ORDER BY COUNT(camis) DESC LIMIT 11")
    restaurant_cuisine = cur.fetchall()
    r_cuisine = []
    r_cuisine_values = []
    for i in restaurant_cuisine:
        if i[0] != None:
            r_cuisine.append(i[0])
            r_cuisine_values.append(i[1])
    #inspection count
    cur.execute(f"SELECT COUNT(id) FROM inspections")
    inspection_count = cur.fetchone()[0]
    #inspection count by year
    cur.execute(f"SELECT CAST(EXTRACT(YEAR FROM inspection_date) AS FLOAT) AS year, COUNT(id) FROM inspections GROUP BY year ORDER BY year ASC")
    inspection_count_year = cur.fetchall()
    i_year = []
    i_year_values = []
    for i in inspection_count_year:
        i_year.append(i[0])
        i_year_values.append(i[1])
    #inspection count by critical
    cur.execute(f"SELECT critical_flag, COUNT(id) FROM inspections GROUP BY critical_flag ORDER BY COUNT(id) DESC")
    inspection_count_critical = cur.fetchall()
    i_critical = []
    i_critical_values = []
    for i in inspection_count_critical:
        i_critical.append(i[0])
        i_critical_values.append(i[1])
    #inspection avg
    cur.execute(f"SELECT CAST(ROUND(AVG(score),2) AS FLOAT) FROM inspections")
    inspection_avg = cur.fetchone()[0]
    #inspection avg by boro
    cur.execute(f"SELECT r.boro, CAST(ROUND(AVG(i.score),2) AS FLOAT) FROM inspections i LEFT JOIN restaurants r ON i.camis=r.camis GROUP BY r.boro ORDER BY AVG(i.score) ASC")
    inspection_avg_boro = cur.fetchall()
    i_boros = []
    i_boros_values = []
    for i in inspection_avg_boro:
        if i[0] != "0":
            i_boros.append(i[0])
            i_boros_values.append(i[1])
    cur.close()
    i_boros = []
    i_boros_values = []
    for i in inspection_avg_boro:
        if i[0] != "0":
            i_boros.append(i[0])
            i_boros_values.append(i[1])
    cur.close()

    return render_template("analysis.html",restaurant_count=restaurant_count,
                            restaurant_boro=restaurant_boro,r_boros=r_boros,r_boros_values=r_boros_values,
                            restaurant_cuisine=restaurant_cuisine,r_cuisine=r_cuisine,r_cuisine_values=r_cuisine_values,
                            inspection_count=inspection_count, inspection_avg=inspection_avg, 
                            inspection_count_year=inspection_count_year,i_year=i_year,i_year_values=i_year_values,
                            inspection_count_critical=inspection_count_critical,i_critical=i_critical,i_critical_values=i_critical_values,
                            inspection_avg_boro=inspection_avg_boro,i_boros=i_boros,i_boros_values=i_boros_values)
