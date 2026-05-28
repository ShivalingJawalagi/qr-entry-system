# app.py

from flask import Flask, render_template, request, redirect, send_from_directory
import pandas as pd
import os
import random
import qrcode
from datetime import datetime
import cv2
from pyzbar.pyzbar import decode

app = Flask(__name__)

# CREATE CSV FILES

try:
    pd.read_csv('users.csv')
except:
    pd.DataFrame(columns=['ID', 'Name']).to_csv('users.csv', index=False)

try:
    pd.read_csv('entries.csv')
except:
    pd.DataFrame(columns=['ID', 'Name', 'Time']).to_csv('entries.csv', index=False)

# CREATE QR FOLDER

if not os.path.exists('qrcodes'):
    os.makedirs('qrcodes')

# HOME PAGE

@app.route('/')
def home():
    return render_template('index.html')

# ADMIN PANEL

@app.route('/admin')
def admin():

    users = pd.read_csv('users.csv')
    entries = pd.read_csv('entries.csv')

    users_data = users.values.tolist()
    entries_data = entries.values.tolist()

    return render_template(
        'admin.html',
        users=users_data,
        entries=entries_data
    )

# REGISTER USER

@app.route('/register', methods=['POST'])
def register():

    name = request.form['name']

    user_id = 'USR' + str(random.randint(1000, 9999))

    users = pd.read_csv('users.csv')

    users.loc[len(users)] = [user_id, name]

    users.to_csv('users.csv', index=False)

    # GENERATE QR

    qr = qrcode.make(user_id)

    qr.save(f'qrcodes/{user_id}.png')

    return render_template(
        'success.html',
        name=name,
        user_id=user_id
    )

# SAVE ENTRY

def save_entry(user_id):

    users = pd.read_csv('users.csv')

    user = users[users['ID'] == user_id]

    if len(user) == 0:
        return "User Not Found"

    name = user.iloc[0]['Name']

    current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    entries = pd.read_csv('entries.csv')

    entries.loc[len(entries)] = [
        user_id,
        name,
        current_time
    ]

    entries.to_csv('entries.csv', index=False)

    return f"Entry Saved For {name}"

# MANUAL ENTRY

@app.route('/manual', methods=['POST'])
def manual():

    user_id = request.form['userid']

    result = save_entry(user_id)

    return render_template(
        'message.html',
        message=result
    )

# QR SCANNER

@app.route('/scan')
def scan():

    camera = cv2.VideoCapture(0)

    while True:

        success, frame = camera.read()

        if not success:
            break

        for qr in decode(frame):

            qr_data = qr.data.decode('utf-8')

            result = save_entry(qr_data)

            camera.release()

            cv2.destroyAllWindows()

            return render_template(
                'message.html',
                message=result
            )

        cv2.imshow("QR Scanner", frame)

        if cv2.waitKey(1) == 27:
            break

    camera.release()

    cv2.destroyAllWindows()

    return redirect('/')

# SHOW QR IMAGE

@app.route('/qrcodes/<filename>')
def get_qr(filename):
    return send_from_directory('qrcodes', filename)

# RUN APP

if __name__ == "__main__":
    app.run(debug=True)