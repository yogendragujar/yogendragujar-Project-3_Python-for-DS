import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pickle

from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['FLASK_ENV'] = 'development'
app.config['SECRET_KEY'] = 'ItShouldBeALongStringOfRandomCharacters'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Y0gendrA@localhost:3306/loan-registration'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
model = pickle.load(open('model.pkl', 'rb'))
app.app_context().push()
scaler = StandardScaler()


class LoginTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)


db.create_all()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/home')
def homePage():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        textPassword = request.form.get('password')
        newlogin = LoginTable(username=request.form.get('username'),
                              password=bcrypt.generate_password_hash(textPassword))

        db.session.add(newlogin)
        db.session.commit()
    else:
        return f"<h2> Error Creating user name and password</h2>"

    return redirect(url_for('enter_details'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        userName = request.form.get('username')
        try:
            validUser = LoginTable.query.filter_by(username=userName).first()
            if bcrypt.check_password_hash(validUser.password, request.form.get('password')):
                session['name'] = userName
                return redirect(url_for('enter_details'))
            else:
                return f"<h2>Invalid Username or password!</h2>"
        except Exception as dbSearchException:
            print(str(dbSearchException))
            return f"<h2>user does not exist</h2>"
    else:
        return f"<h2> Invalid Username or Password</h2>"


@app.route('/enter-details')
def enter_details():
    return render_template('predict.html')


@app.route('/predict', methods=['POST'])
def predict():
    gender = int(request.form['gender'])
    married = int(request.form['married'])
    dependents = int(request.form['dependents'])
    education = int(request.form['education'])
    self_employed = int(request.form['self-employed'])
    applicantincome = float(request.form['applicant-income'])
    coapplicantincome = float(request.form['co-applicant-income'])
    loanamount = float(request.form['loan-amount'])
    loan_amount_term = int(request.form['loan-amount-term'])
    credit_history = int(request.form['credit-history'])
    property_area = int(request.form['property-area'])

    total_income = applicantincome + coapplicantincome
    # loanamount = scaler.fit_transform(iloanamount.reshape(-1, 1))
    # loanamount = scaler.fit_transform(np.array(iloanamount).reshape(1,-1))
    # total_income = scaler.fit_transform(np.array(itotal_income).reshape(1,-1))
    # loan_amount_term = scaler.fit_transform(np.array(iloan_amount_term).reshape(1,-1))

    print(gender, married, dependents, education, self_employed, loanamount, loan_amount_term, credit_history,
          property_area, total_income)
    prediction = model.predict(
        [[gender, married, dependents, education, self_employed, loanamount,
          loan_amount_term, credit_history, property_area, total_income]])

    # prediction = model.predict([[gender, married, dependents, education, self_employed, loanamount,
    #                                      loan_amount_term, credit_history, property_area, total_income]])

    output = prediction[0]
    print(prediction)
    print(output)
    if output == 1:
        return render_template('predict.html', prediction_text="Congrats!! You are eligible for the loan")
    else:
        return render_template('predict.html', prediction_text="Sorry, You are Not eligible for the loan")


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('name', default=None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
