import sqlite3
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate(r"C:\Users\ngyyang\Desktop\cosco_Travel_Apps\cosco_leave_app\backend\cosco-mobile-application-firebase-adminsdk-fbsvc-af4e3a66f4.json")
firebase_admin.initialize_app(cred)

db_fs = firestore.client()

conn = sqlite3.connect(r'C:\Users\ngyyang\Desktop\cosco_Travel_Apps\cosco_leave_app\backend\user.db')
cursor = conn.cursor()

# cursor.execute("SELECT Authority_Level, Email_Address, Password, Department, Created_At, Date_Modified, Position FROM Users")
# users = cursor.fetchall()

# for user in users:
#     Authority_Level, email, password, position, Department, Created_At, Date_Modified  = user
#     db_fs.collection('users').document(email).set({
#         'Authority_Level' : Authority_Level,
#         'email': email,
#         'password': password,
#         'position': position,
#         'Department': Department,
#         'Created_At': Created_At,
#         'Date_Modified': Date_Modified
#     })

cursor.execute("""
SELECT application_id, Email_Address, Name, department, SAP_ID, Apply_Date, From_Date, To_Date, Total_Days,
       Accomodation, Transport, Additional, Destination, Purpose, Status
FROM applications
""")
applications = cursor.fetchall()

for app in applications:
    (app_id, email, name, dept, sap, apply_date, from_date, to_date,
     total_days, accom, transport, addi, dest, purpose, status) = app
     
    db_fs.collection('applications').document(app_id).set({
        'email': email,
        'name': name,
        'department': dept,
        'sap_id': sap,
        'apply_date': apply_date,
        'from_date': from_date,
        'to_date': to_date,
        'total_days': total_days,
        'accommodation': accom,
        'transport': transport,
        'additional': addi,
        'destination': dest,
        'purpose': purpose,
        'status': status
    })