# Import required modules
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
import os

# Initialize Flask app
app = Flask(__name__)

# Configure SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "habits.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Habit model


class Habit(db.Model):
    __tablename__ = 'habit'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_check_in = db.Column(db.Date)
    logs = db.relationship('HabitLog', backref='habit',
                           lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Habit {self.name}>'

    def calculate_streak(self):
        logs = HabitLog.query.filter_by(
            habit_id=self.id).order_by(HabitLog.date.desc()).all()
        if not logs:
            return 0

        streak = 1
        today = date.today()

        # If the most recent log isn't from today or yesterday, streak is just 0 or 1
        if logs[0].date != today and logs[0].date != today - timedelta(days=1):
            # Return 1 if checked in today, otherwise 0
            return 1 if logs[0].date == today else 0

        # Count consecutive days
        for i in range(len(logs) - 1):
            # If this log and the next one are consecutive days
            if logs[i].date - logs[i+1].date == timedelta(days=1):
                streak += 1
            else:
                # Break the streak when we find a gap
                break

        return streak

# HabitLog model


class HabitLog(db.Model):
    __tablename__ = 'habit_log'
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey(
        'habit.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<HabitLog for habit_id {self.habit_id} on {self.date}>'

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
        # Check if this habit already has a log for today
        existing_log = HabitLog.query.filter_by(
            habit_id=habit.id, date=today).first()
        if not existing_log:
            # Create a new log entry
            log = HabitLog(habit_id=habit.id, date=today)
            db.session.add(log)
            habit.last_check_in = today
            db.session.commit()

    return redirect(url_for('index'))


@app.route('/habit/<int:habit_id>')
def habit_detail(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    logs = HabitLog.query.filter_by(
        habit_id=habit.id).order_by(HabitLog.date.desc()).all()

    # Get data for last 7 days for display
    today = date.today()
    last_7_days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        completed = any(log.date == day for log in logs)
        last_7_days.append({'date': day, 'completed': completed})

    return render_template('habit_detail.html', habit=habit, logs=logs, last_7_days=last_7_days)


@app.route('/delete/<int:habit_id>')
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    db.session.delete(habit)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
