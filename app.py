from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habits.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Habit model
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    streak = db.Column(db.Integer, default=0)
    last_check_in = db.Column(db.Date)

    def __repr__(self):
        return f'<Habit {self.name}>'

# Create all database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    habits = Habit.query.all()
    today = date.today()
    return render_template('index.html', habits=habits, today=today)

@app.route('/add_habit', methods=['POST'])
def add_habit():
    name = request.form['name']
    new_habit = Habit(name=name)
    db.session.add(new_habit)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/check_in/<int:habit_id>')
def check_in(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    today = date.today()
    
    if habit.last_check_in != today:
        if habit.last_check_in is None or (today - habit.last_check_in).days == 1:
            habit.streak += 1
        elif (today - habit.last_check_in).days > 1:
            habit.streak = 1
        habit.last_check_in = today
        db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/delete/<int:habit_id>')
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    db.session.delete(habit)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)