import sqlite3
from datetime import datetime, timedelta
import os

# Set correct path to the database in the instance folder
db_path = os.path.join(
    '/workspaces/guided-prompt-engineering-junior/instance', 'habits.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get yesterday's date instead of today
today = datetime.now().date()
yesterday = today - timedelta(days=1)

# Get the maximum date from habit_log as reference date
cursor.execute("SELECT MAX(date) FROM habit_log")
max_date_str = cursor.fetchone()[0]
reference_date = datetime.strptime(max_date_str, '%Y-%m-%d').date()

# Calculate days between reference and yesterday
days_difference = (yesterday - reference_date).days

# Get all records from habit_log
cursor.execute("SELECT id, date FROM habit_log")
records = cursor.fetchall()

print(f"Found {len(records)} records to update")
print(
    f"Shifting dates by {days_difference} days (from {reference_date} to {yesterday})")
print(f"Using database at: {db_path}")

# Update each record with a new date
for record_id, old_date in records:
    # Convert string date to datetime object
    old_date_obj = datetime.strptime(old_date, '%Y-%m-%d').date()

    # Add the difference in days
    new_date_obj = old_date_obj + timedelta(days=days_difference)

    # Convert back to string
    new_date = new_date_obj.strftime('%Y-%m-%d')

    # Update the record
    cursor.execute("UPDATE habit_log SET date = ? WHERE id = ?",
                   (new_date, record_id))
    print(f"Updated record {record_id}: {old_date} → {new_date}")

# Commit changes and close connection
conn.commit()
conn.close()

print("All dates updated successfully!")
