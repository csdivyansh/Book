import io, os, random, string
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Entity, Client
from PIL import  Image, ImageDraw, ImageFont
from flask import Response
from datetime import datetime
from sqlalchemy import or_

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Database setup
engine = create_engine('sqlite:///zdb.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

#Login manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(client_id):
    return db_session.get(Client, client_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to access this page.', 'error')
    return redirect(url_for('login'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validate username and password
        client = db_session.query(Client).filter_by(username=username).first()
        if client and check_password_hash(client.password, password):
            login_user(client)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db_session.query(Client).filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('login'))
        hashed_password = generate_password_hash(password)

        new_client = Client(username=username, password=hashed_password, role='client')
        db_session.add(new_client)
        db_session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('login.html')

# For Users
@login_required
@app.route('/')
def home():
    now = datetime.now()
    formatted_date = now.strftime("%d-%m-%Y")
    formatted_datetime = now.strftime("%d-%m-%Y %H:%M:%S")
    return render_template('index.html')

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    if request.method == 'POST':
        client = current_user
        description = request.form['description']
        date = request.form['date']
        size = request.form['size']
        try:
            new_entity = Entity(
                client=client,
                description=description,
                date=datetime.strptime(date, '%Y-%m-%d'),
                size=size
            )
            db_session.add(new_entity)
            db_session.commit()
            flash('Booking successful!')
        except Exception as e:
            db_session.rollback()
            flash(f'Error: {str(e)}')
    return render_template('book.html')

@app.route('/view', methods=['GET', 'POST'])
@login_required
def view():
    bookings = []
    selected_date = None

    if request.method == 'POST':
        date_str = request.form['date']
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if current_user.role == 'Admin':
                bookings = db_session.query(Entity).filter(Entity.date == selected_date).all()
            else:
                bookings = db_session.query(Entity).filter(
                    Entity.date == selected_date,
                    Entity.client_id == current_user.id
                ).all()
        except Exception as e:
            flash(f"Error: {str(e)}")

    return render_template('view.html', bookings=bookings, selected_date=selected_date)

@app.route('/delete/<int:booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):
    booking = db_session.query(Entity).filter_by(id=booking_id).first()
    if booking:
        db_session.delete(booking)
        db_session.commit()
        flash("Booking deleted successfully.")
    else:
        flash("Booking not found.")
    return redirect(url_for('view'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)