from flask import Flask, render_template, request, g
from datetime import datetime
import sqlite3

app = Flask(__name__)

def connect_db():
    # Connect to database
    sql = sqlite3.connect('food_log.db')
    # return the results as a dictionaries instead of tuples
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    # check to see if sqlite3 exsits
    if not hasattr(g, 'sqlite3_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    # close db at end of each request
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    date_results = []
    db = get_db()
    # Search by date function on index search bar
    if request.method == 'POST':
        date = request.form['date'] # date format in YYYY-MM-DD
        dt = datetime.strptime(date, '%Y-%m-%d')
        # new date format
        database_date = datetime.strftime(dt, '%Y%m%d')
        #return database_date/ returned to make sure new format works before saving to database
        db.execute('insert into log_date (entry_date) values (?)', [database_date])
        db.commit()

        # Query date from database for use in the index page
        cur = db.execute('select entry_date from log_date order by entry_date desc')
        # Get all dates from database
        results = cur.fetchall()
        

        for i in results:
            single_date = {}

            d = datetime.strptime(str(i['entry_date']), '%Y%m%d')
            single_date['entry_date'] = datetime.strftime(d, '%B %d, %Y')

            date_results.append(single_date)
        
    return render_template('home.html', title='Welcome', results=date_results)

@app.route('/view/<date>', methods=['GET', 'POST'])
def view(date):
    db = get_db()
    # query the datebase for log_date table to recive entry_date
    cur = db.execute('select id, entry_date from log_date where entry_date = ?', [date])
    # GET the result
    date_result = cur.fetchone()

    if request.method == 'POST':
    # POST food id and log_date_id into food_date table
        db.execute('insert into food_date (food_id, log_date_id) values (?, ?)', \
            [request.form['food-select'], date_result['id']])
        db.commit()
    # format the date from 20200419 to April 19, 2020
    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    result_date = datetime.strftime(d, '%B %d, %Y')
    # query database for foods in database
    food_cur = db.execute('select id, name from food')
    # GET all foods from datebase
    food_results = food_cur.fetchall()
    # Join log food date table with log date table then to join to the food table
    log_cur = db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id where log_date.entry_date = ?', [date])
    # Get all joined table data
    log_results = log_cur.fetchall()

    # Add food totals together
    totals = {}
    # start at 0
    totals['protein'] = 0
    totals['carbohydrates'] = 0
    totals['fat'] = 0
    totals['calories'] = 0

    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']


    return render_template('day.html', title='Food By Date', date=result_date, food_results=food_results, log_results=log_results, totals=totals)

@app.route('/food', methods=['GET', 'POST'])
def food():
    # create instance of db
    db = get_db()
    if request.method == 'POST':
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])
        # below calaculating the valuse for the total amount of calories
        calories = protein * 4 + carbohydrates * 4 + fat * 9
        # insert values into db
        db.execute('insert into food (name, protein, carbohydrates, fat, calories) values (?, ?, ?, ?, ?)', \
            [name, protein, carbohydrates, fat, calories])
        db.commit()
        '''
        The return below was used to test the form was being submit correctly
        by checking the values.
        return '<h1>Name: {} Protein: {} Carbs: {} Fat: {}</h1>'.format(request.form['food-name'], request.form['protein'], \
        request.form['carbohydrates'], request.form['fat'])
        '''
        # create a cursor to query the database to enbale displaying of data in
        # html template
    cur = db.execute('select name, protein, carbohydrates, fat, calories from food')
    # fetch all results from database to be able to disply them in template
    results = cur.fetchall()
    return render_template('add_food.html', title='Add Your Foods', results=results)



if __name__ == '__main__':
    app.run(debug=True)