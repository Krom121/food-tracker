from flask import Flask, render_template, request, g
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

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/view')
def view():
    return render_template('day.html')

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
        # create a cursor to query the database to enbale displying of data in
        # html template
    cur = db.execute('select name, protein, carbohydrates, fat, calories from food')
    results = cur.fetchall()
    return render_template('add_food.html', results=results)



if __name__ == '__main__':
    app.run(debug=True)