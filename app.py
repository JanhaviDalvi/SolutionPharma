from flask import Flask, render_template, redirect, flash, url_for, request, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from bson import ObjectId
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import re
from forms import RegistrationForm, LoginForm

# Load environment variables from .env file and access them
load_dotenv() 
mongodb_uri = os.getenv('MONGODB_URI')
secret_key = os.getenv('SECRET_KEY')

# app configurations
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# MongoDB stuff
client = MongoClient(mongodb_uri)
db = client['pharmacy_db']

def insert_customer(customer_name, customer_phone):
	# Check if customer with the given phone number already exists
	existing_customer = db.customer.find_one({"customer_phone": customer_phone})
	if not existing_customer:
		customer = {
			"customer_name": customer_name,
			"customer_phone": customer_phone
		}
		db.customer.insert_one(customer)
	customer_id = db.customer.find_one({"customer_phone": customer_phone})['_id']
	return customer_id

# User class that satisfies the requirements of Flask-Login. The User class should inherit from UserMixin, which provides default implementations for the required methods.
class User(UserMixin):
	def __init__(self, user_id, username, email):
		self.id = user_id
		self.username = username
		self.email = email

	# This method is required by Flask-Login's UserMixin class. It returns the string representation of the user's ID, which is used for user authentication and session management.
	def get_id(self):
		return str(self.id)

#  user loader function that Flask-Login will use to load the user from the database based on the user ID
@login_manager.user_loader
def load_user(user_id):
	# Query the database to find the user by ID
	user = db.user.find_one({'_id': ObjectId(user_id)})
	# Return the user object
	return User(user['_id'], user['username'], user['email'])

@app.route('/')
@login_required
def home():
	cursor = db.medicines.find({})
	medicines = list(cursor)
	print(len(medicines))
	for i in medicines:
		print(i)
	return render_template('dashboard.html', medicines=medicines)

@app.route('/search_medicine', methods=["POST"])
@login_required
def search_medicine():
	search_term = request.form.get('searchMedicine')
	regex_pattern = re.compile(f".*{search_term}.*", re.IGNORECASE)
	query = {
        '$or': [
            {'mdcn_name': regex_pattern},
            {'mdcn_description': regex_pattern}
        ]
    }
	results = db.medicines.find(query)
	results = list(results)
	return render_template('dashboard.html', medicines=results)


@app.route('/sales')
@login_required
def sales():
	# Fetch the medicine names from the 'medicines' collection
	cursor = db.medicines.find({})
	medicines = list(cursor)
	print(len(medicines))
	for i in medicines:
		print(i)
	return render_template('sales.html', medicines=medicines)

@app.route('/billing', methods=["POST"])
@login_required
def billing():
	medicine_names = request.form.getlist('medicine_name[]')
	medicine_quantities = request.form.getlist('medicine_quantity[]')
	medicine_prices = request.form.getlist('medicine_price[]')
	medicine_total_costs = request.form.getlist('medicine_totalCost[]')
	medicines = []
	customer_name = request.form.get("customer_name")
	customer_phone = request.form.get("customer_phone")
	total_amount = request.form.get("total_amount")
	payment_method = request.form.get("payment_method")
	billing_date = datetime.now()
	for name, quantity, price, total_cost in zip(medicine_names, medicine_quantities, medicine_prices, medicine_total_costs):
		medicine = {
			'medicine_name': name,
			'medicine_quantity': quantity,
			'medicine_price': price,
			'medicine_total_cost': total_cost
		}
		medicines.append(medicine)
	customer_id = insert_customer(customer_name, customer_phone)
	sale = {
		'medicines': medicines,
		'total_amount': total_amount,
		'billing_date': billing_date,
		'payment_method': payment_method,
		'customer_id': customer_id
	}
	db.sales.insert_one(sale)
	return render_template('billing.html', medicines=medicines, customer_name=customer_name, total_amount=total_amount, payment_method=payment_method, billing_date=billing_date)

@app.route('/add_medicine', methods=["POST", "GET"])
@login_required
def add_medicine():
	current_datetime = datetime.now()
	if request.method == 'POST':
		medicine_name = request.form.get("medicine_name")
		medicine_type = request.form.get("medicine_type")
		medicine_description = request.form.get("medicine_description")
		stock_count = request.form.get("stock_count")
		medicine_mfg = request.form.get("medicine_mfg")
		medicine_exp = request.form.get("medicine_exp")
		medicine_company = request.form.get("medicine_company")
		medicine_price = request.form.get("medicine_price")
		existing_medicine = db.medicines.find_one({"mdcn_name": medicine_name})
		if not existing_medicine:
			medicine = {
			"mdcn_name": medicine_name,
			"mdcn_type": medicine_type,
			"mdcn_description": medicine_description,
			"mdcn_mfg": medicine_mfg,
			"mdcn_exp": medicine_exp,
			"mdcn_company": medicine_company,
			"stock_count": int(stock_count),
			"mdcn_price": round(float(medicine_price), 2)
			}
			db.medicines.insert_one(medicine)
			flash("Medicine has been added!", "success")
			return redirect(url_for('add_medicine'))
		
	return render_template("add_medicine.html", current_datetime=current_datetime)


@app.route('/stock_report', methods=['GET', 'POST'])
@login_required
def stock_report():
	medicines = db.medicines.distinct("mdcn_name")
	companies = db.medicines.distinct("mdcn_company") 
	result = columns = None
	if request.method == "POST":
		report_by = request.form.get("stock_report_type")
		value = request.form.get(report_by)
		if report_by == 'company':
			result = db.medicines.find({'mdcn_company': value}, {'_id': 0, 'mdcn_company': 0})
			columns = result[0].keys()
		elif report_by == 'medicine':
			result = db.medicines.find({'mdcn_name': value}, {'_id': 0, 'mdcn_name': 0})
			columns = result[0].keys()

	return render_template('stock_report.html', medicines=medicines, companies=companies, result=result, columns=columns)

@app.route('/sales_report', methods=['GET', 'POST'])
@login_required
def sales_report():
	current_datetime = datetime.now()
	results = [] 
	if request.method == 'POST':
		report_by = request.form.get("report_type")
		value = request.form.get(report_by)
		if report_by == "billing_date":
			# Convert the value date string to a datetime object
			selected_date = datetime.strptime(value, '%Y-%m-%d')
			# Query the collection based on the selected date
			res = db.sales.find({
				'billing_date': {
					'$gte': selected_date,
					'$lt': selected_date + timedelta(days=1)
				}
			})
			for i in res:
				results.append(dict(i))

		elif report_by == "mdcn_company":
			medicines = db.medicines.find({'mdcn_company': value}, 	{'mdcn_name': 1})
			for each_medicine in medicines:
				sales = db.sales.find({'medicines.medicine_name': each_medicine["mdcn_name"]})
				for i in sales:
					results.append(i)

	total_sale = round(sum(float(item['total_amount']) for item in results), 2)

	return render_template('sales_report.html', current_datetime=current_datetime, results=results, total_sale=total_sale)


@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm(db) # Passing the db object to the form
	if form.validate_on_submit():
		# encrypting the password
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		print(hashed_password)
		# to insert the user
		new_user = {
			'email': form.email.data,
			'username': form.username.data,
			'password': hashed_password
		}
		db.user.insert_one(new_user) #inserting in 'user' collection

		flash(f"Account has been created for '{form.username.data}'!", "success")
		return redirect(url_for('home'))
	return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = db.user.find_one({'username': form.username.data})
		if user and bcrypt.check_password_hash(user['password'], form.password.data):
			# Create a User object from the retrieved data
			user_obj = User(user['_id'], user['username'], user['email'])
			login_user(user_obj, remember=form.remember.data)  # Login the user
			flash('You have been logged in!', 'success')
			return redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check username and password', 'danger')
	return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
	logout_user()  
	flash('You have been logged out!', 'success')
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(debug=True)