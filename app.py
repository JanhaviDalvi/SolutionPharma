from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# database stuff
client = MongoClient('mongodb+srv://janhavidalvi3008:MJVDpMPK0lqmss08@cluster0.39gujyb.mongodb.net/?retryWrites=true&w=majority')
print(client)
db = client['pharmacy_db']

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/sales')
def sales():
    # Fetch the medicine names from the 'medicines' collection
    cursor = db.medicines.find({})
    medicines = list(cursor)
    print(len(medicines))
    for i in medicines:
        print(i)
    return render_template('sales.html', medicines=medicines)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the entered username and password from the form
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username and password are valid (you can replace this with your authentication logic)
        if username == 'admin' and password == 'password':
            # Redirect to the home page or dashboard upon successful login
            return redirect(url_for('home'))
        else:
            # If the credentials are invalid, show an error message on the login page
            error_message = 'Invalid username or password'
            return render_template('login.html', error_message=error_message)
    
    # Render the login page template
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
