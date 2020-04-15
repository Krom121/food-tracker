from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)

def connect_db():
    # Connect to database
    sql = sqlite3.connect('\C:\sites\cal_tracker\food_log.db')
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

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/view')
def view():
    return render_template('day.html')

@app.route('/add_food')
def add_food():
    return render_template('add_food.html')



if __name__ == '__main__':
    app.run(debug=True)