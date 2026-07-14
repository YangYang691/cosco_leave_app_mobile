from flask import Flask, render_template, request, redirect, url_for, Blueprint, send_from_directory, flash, jsonify, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import sqlite3
import os
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
import random
import string
from datetime import datetime, timedelta
from db_con import get_db_connection
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

bp = Blueprint('api', __name__)

app = Flask(__name__)
app.secret_key = 'TravelApps'
bcrypt = Bcrypt(app)
app.debug= True

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --------------------------
# Database Setup
# --------------------------
DB_FILE = 'user.db'

app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'database', DB_FILE)

@bp.route('/list.html')
def serve_list():
    return render_template('list.html')

@app.route('/reset-password', methods=['GET', 'POST'])
@login_required
def reset_password():
    if request.method == 'POST':
        current_password = request.form['CurrentPassword']
        new_password = request.form['NewPassword']
        confirm_password = request.form['ConfirmPassword']

        # user_email = session.get('user_email')  # assuming the user is logged in and email is stored in session
        user_email = current_user.username

        if not user_email:
            flash("User not logged in", "error")
            return redirect('/login')

        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()

        # Fetch current hashed password
        c.execute("SELECT password FROM Users WHERE Email_Address = ?", (user_email,))
        result = c.fetchone()

        if not result:
            flash("User not found", "error")
            return redirect('/reset-password')

        current_hashed_pw = result[0]

        if not bcrypt.check_password_hash(current_hashed_pw, current_password):
            flash("Current password is incorrect", "error")
            return redirect('/reset-password')

        if new_password != confirm_password:
            flash("New passwords do not match", "error")
            return redirect('/reset-password')

        new_hashed_pw = generate_password_hash(new_password)
        c.execute("UPDATE Users SET password = ? WHERE Email_Address = ?", (new_hashed_pw, user_email))
        conn.commit()
        conn.close()

        flash("Password updated successfully", "success")
        return redirect(url_for('dashboard'))  # or home page

    return render_template('reset-password.html')

@app.route('/History.html')
@login_required
def serve_history():
    return render_template('History.html')

@app.route('/dashboard.html')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/approval.html')
@login_required
def approval():
    return render_template('approval.html')

@bp.route('/print.html')
def print_list():
    app_id = request.args.get('id')
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM applications WHERE id = ?', (app_id,))
    row = c.fetchone()

    # Step 2: Get the actual application_id string to use in the approvals table
    app_identifier = row['application_id']  # Assuming column is named application_id

    c.execute('''
        SELECT a.approver_email as approver_email, a.approval_level, a.status, a.created_at, u.Name AS approver_name
        FROM approvals a
        JOIN Approvers u ON a.approver_email = u.Email_Address
        WHERE a.application_id = ?
    ''', (app_identifier,))
    approvals = c.fetchall()
    conn.close()

    approval_data = {}
    for row2 in approvals:
        level = row2['approval_level']
        if isinstance(row2['created_at'], str):
            created_at = datetime.strptime(row2['created_at'], '%Y-%m-%d %H:%M:%S')  # or your actual format
        else:
            created_at = row2['created_at']

        approval_data[level] = {
            'email': row2['approver_email'],
            'name': row2['approver_name'],  # in case you're joining name
            'status': row2['status'],
            'date': created_at.strftime('%Y-%m-%d')
        }

    print(approval_data)

    applicant = {
        'name': row['Name'],
        'applydate': row['created_at'],
        'sapid': row['SAP_ID'],
        'department': row['Department'],
        'fromdate': row['From_Date'],
        'todate': row['To_Date'],
        'travellingdays': row['Total_Days'],
        'accomodation': row['Accomodation'],
        'transportation': row['Transport'],
        'addiotional50': row['Additional'],
        'destination': row['Destination'],
        'purpose': row['Purpose'],
        'level1_email': approval_data.get('1', {}).get('name'),
        'level1_status': approval_data.get('1', {}).get('status'),
        'level1_date': approval_data.get('1', {}).get('date'),
        'level2_email': approval_data.get('2', {}).get('name'),
        'level2_status': approval_data.get('2', {}).get('status'),
        'level2_date': approval_data.get('2', {}).get('date'),
        'level3_email': approval_data.get('3', {}).get('name'),
        'level3_status': approval_data.get('3', {}).get('status'),
        'level3_date': approval_data.get('3', {}).get('date')
    }

    return render_template('print.html', applicant=applicant, approval_data=approval_data)


# --------------------------
# Routes
# --------------------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT Email_Address, Password FROM Users WHERE Email_Address = ?", (uname,))
        row = cursor.fetchone()
        conn.close()
        if row:
            hashed_pw = row[1]  # the hashed password from DB
            if bcrypt.check_password_hash(hashed_pw, pwd):
                user_obj = User(id=row[0], username=row[1])
                login_user(user_obj)
                return redirect(url_for('dashboard'))
            else:
                return "Invalid login credentials", 401
    return render_template('index.html')

@app.route('/application/<app_id>')
def application_detail(app_id):
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enables dict-like access
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM applications WHERE id = ?', (app_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        applicant = {
            'name': row['Name'],
            'applydate': row['Apply_Date'],
            'sapid': row['SAP_ID'],
            'department': row['department'],
            'fromdate': row['From_Date'],
            'todate': row['To_Date'],
            'travellingdays': row['Total_Days'],
            'accomodation': row['Accomodation'],
            'transportation': row['Transport'],
            'addiotional50': row['Additional'],
            'destination': row['Destination'],
            'purpose': row['Purpose']
        }
        return render_template('printer.html', applicant=applicant)
    else:
        return "Application not found", 404

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['password']
        department = request.form['Department']
        EmpID = request.form['EmpID']
        Authorative = "User"

        password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT 1 FROM Users WHERE Email_Address = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return "Email already registered", 400

        cursor.execute("INSERT INTO Users (EmployeeID, Email_Address, Password,Department, Authority_Level) VALUES (?, ?, ?, ?, ?)", (EmpID, email, password, department, Authorative))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    current_user.web_token = None
    current_user.web_token_timestamp = None
    # db.session.commit()
    logout_user()
    return redirect(url_for('login'))

def get_user_approval_level(department, user_name):
    approver_lookup = {
        "EQS": {
            "1": ["cas@coscon.com", "catherin@coscon.com", "sunlg@coscon.com"],
            "2": ["", "catherin@coscon.com", "sunlg@coscon.com"]
        },
        "SM": {
            "1": ["maylow1@coscon.com", "xujm2@coscon.com", "sunlg@coscon.com"],
            "2": ["", "xujm2@coscon.com", "sunlg@coscon.com"]
        },
        "CS": {
            "1": ["yapwm@coscon.com", "xujm2@coscon.com", "sunlg@coscon.com"],
            "2": ["", "xujm2@coscon.com", "sunlg@coscon.com"]
        },
        "Finance": {
            "1": ["lamml@coscon.com", "zhangxi6@coscon.com", "sunlg@coscon.com"],
            "2": ["", "zhangxi6@coscon.com", "sunlg@coscon.com"]
        },
        "OP": {
            "1": ["sahak@coscon.com", "jimooi@coscon.com", "sunlg@coscon.com"],
            "2": ["", "jimooi@coscon.com", "sunlg@coscon.com"]
        },
        "Documentation": {
            "1": ["jesstan@coscon.com", "jimooi@coscon.com", "sunlg@coscon.com"],
            "2": ["", "jimooi@coscon.com", "sunlg@coscon.com"]
        },
        "Kuching": {
            "1": ["elchong@coscon.com", "jimooi@coscon.com", "sunlg@coscon.com"],
            "2": ["", "jimooi@coscon.com", "sunlg@coscon.com"]
        },
        "Johor": {
            "1": ["", "vinchan@coscon.com", "sunlg@coscon.com"],
            "2": ["", "vinchan@coscon.com", "sunlg@coscon.com"]
        },
        "Penang": {
            "1": ["neohcp@coscon.com", "", "sunlg@coscon.com"],
            "2": ["", "", "sunlg@coscon.com"]
        },
        "GMD": {
            "1": ["euniceho@coscon.com", "", "sunlg@coscon.com"],
            "2": ["", "", "sunlg@coscon.com"]
        },
        # Add other departments...
    }

    if department in approver_lookup:
        for position, approvers in approver_lookup[department].items():
            if user_name in approvers:
                return approvers.index(user_name) + 1  # +1 for Level 1, 2, 3
    return None  # Not an approver


# Approve function button
@bp.route('/api/application/<int:app_id>/approve', methods=['POST'])
def approve_application(app_id):
    user_id = current_user.username
    current_date = datetime.now()
    formatted_datetime = current_date.strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()

    c.execute("SELECT application_id FROM applications WHERE id = ?", (app_id,))
    application_id = c.fetchone()[0]

    c.execute("SELECT Department FROM applications WHERE id = ?", (app_id,))
    row = c.fetchone()
    if row:
        department = row[0]

    level = get_user_approval_level(department, current_user.username)

    c.execute('''
        UPDATE approvals
        SET status = 'Approved', approved_at = ?
        WHERE application_id = ? AND approval_level = ? AND approver_email = ?
    ''', (datetime.now(), application_id, level, current_user.username))

    c.execute('''
        SELECT COUNT(*) FROM approvals
        WHERE application_id = ?
    ''', (application_id,))
    total_levels = c.fetchone()[0]

    # Check if all 3 levels are approved
    c.execute('''
        SELECT COUNT(*) FROM approvals
        WHERE application_id = ? AND status = 'Approved'
    ''', (application_id,))
    approved_count = c.fetchone()[0]

    if approved_count == total_levels:
        # Update application status
        c.execute('UPDATE applications SET status = "Approved", updated_at = ? WHERE application_id = ?', (formatted_datetime, application_id,))
    else:
        c.execute('''
            SELECT Name FROM applications
            WHERE application_id = ?
        ''', (application_id,))
        Name = c.fetchone()

        c.execute('''
            SELECT approval_level, approver_email FROM approvals
            WHERE application_id = ? AND approval_level > ? AND status='Pending'
            ORDER BY approval_level ASC LIMIT 1
        ''', (application_id, level,))
        next_approver_row = c.fetchone()

        if next_approver_row:
            next_level, next_approver_email = next_approver_row
            subject = f"Approval - Business Travel Application #{application_id}"
            body = f"""
            <p>Dear Approver,</p>
            <p>You have received a request requires immediate attention.</p>
            <p>Ticket No #{application_id} submitted by {Name} is currently pending your approval.</p>
            <p>Kindly review the request and take necessary action by approving or rejecting it at your earliest convenience.</p>
            <p>
            <a href="http://172.26.37.177:8802/login" target="_blank">
                Click here to log in and view the request
            </a>
            </p>
            <p>Thank you for your prompt response.</p>
            """
            send_email(['hdanial@coscon.com'], subject, body)

    conn.commit()
    conn.close()

    return jsonify({"success": True,"redirect_url": "/dashboard.html"})

#Reject function button
@bp.route('/api/application/<int:app_id>/reject', methods=['POST'])
def reject_application(app_id):
    user_id = current_user.username
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()

    print(app_id)

    # You can do similar logic as approve, or just mark as Rejected
    rejected_status = "Rejected"
    c.execute('UPDATE applications SET status = ? WHERE id = ?', (rejected_status, app_id))

    c.execute('''
        SELECT application_id, Name, Email_Address FROM applications
        WHERE id = ?
    ''', (app_id,))

    row = c.fetchone()  # Fetch one row only once

    if row:  # Check that a row was returned
        application_id = row[0]
        Name = row[1]
        Email = row[2]

    c.execute('UPDATE approvals SET status = ? WHERE application_id = ?', (rejected_status, application_id, ))

    subject = f"Business Application Request Rejected - Application #{application_id}"
    body = f"""
    <p>Dear {Name},</p>
    <p>Your business travel application request #{application_id} has been rejected by {user_id}.</p>
    <p>
            <a href="http://172.26.37.177:8802/login" target="_blank">
                Click here to log in and view the request
            </a>
        </p>
    """
    send_email([Email], subject, body)

    conn.commit()
    conn.close()

    return jsonify({"success": True,"redirect_url": "/dashboard.html"})


# --------------------------
# User Loader
# --------------------------
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT EmployeeID, Email_Address FROM Users WHERE Email_Address = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(id=row[0], username=row[1])
    return None

@app.route('/application/<application_id>')
def generate_pdf(application_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('SELECT Name, Apply_Date, SAP_ID, Department, From_Date, To_Date, Total_Days, '
              'Accomodation, Transport, Additional, Destination, Purpose, '
              'HOD_Approval, HOD_Date, Management_Approval, Management_Date, '
              'Director_Approval, Director_Date '
              'FROM applications WHERE application_id = ?', (application_id,))
    
    row = c.fetchone()
    conn.close()

    if row:
        applicant = {
            "name": row[0],
            "apply_date": row[1],
            "sap_id": row[2],
            "department": row[3],
            "from_date": row[4],
            "to_date": row[5],
            "total_days": row[6],
            "accommodation": row[7],
            "transport": row[8],
            "additional_50": row[9],
            "destination": row[10],
            "purpose": row[11],
            "hod_approval": row[12],
            "hod_date": row[13],
            "management_approval": row[14],
            "management_date": row[15],
            "director_approval": row[16],
            "director_date": row[17]
        }

        return render_template('application_report.html', applicant=applicant)
    else:
        return "Application not found", 404

# @login_manager.user_loader
@app.route('/submit', methods=['POST'])
def submit_application():
    # Debug : print all form keys
    print("All form keys:", list(request.form.keys()))

    user_id = current_user.username

    # Collect form values
    # form_data = {
    name = request.form['name']
    apply_date = request.form['applyDate']
    sap_id = request.form['sapId']
    from_date = request.form['fromDate']
    department = request.form['department']
    to_date = request.form['toDate']
    total_days = request.form['daysOfTravel']
    accommodation = request.form['accomodationPay']
    transport = request.form['transport']
    additional_50 = request.form['additional50']
    destination = request.form['destination']
    purpose = request.form['purpose']
    # }

    # ✅ Correct department mapping
    # department_code = form_data['department']
    # department_id = get_department_id(department_code)

    length = 10
    chars = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(chars, k=length))

    current_date = datetime.now()
    formatted_datetime = current_date.strftime('%Y-%m-%d %H:%M:%S')


    submitted_by = 1  # Simulated user ID
    submission_level = "Level 1"

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        INSERT INTO applications (Email_Address, Name, department, submission_lvl, SAP_ID, Apply_Date, From_Date, 
        To_Date, Total_Days, Accomodation, Transport, Additional, Destination, Purpose, application_id, created_at, updated_at, Status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        name,
        department,
        submission_level,
        sap_id,
        apply_date,
        from_date,
        to_date,
        total_days,
        accommodation,
        transport,
        additional_50,
        destination,
        purpose,
        random_string,
        formatted_datetime,
        formatted_datetime,
        'Pending'
    ))

    conn.commit()
    conn.close()

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    d = conn.cursor()
    d.execute('''
        SELECT Position FROM Users
        WHERE Email_Address = ?
    ''', (user_id, ))

    row = d.fetchone()

    Position = row[0]
    conn.commit()
    conn.close()

    if Position == '1':
        pos = 'Executive & Manager'
    else:
        pos = 'General Manager'

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    e = conn.cursor()
    e.execute('''
        SELECT level1, level2, level3 FROM approval_matrix
        WHERE department = ? AND position = ?
    ''', (department, pos))

    approvers = e.fetchone()
    conn.commit()
    conn.close()

    level1_email, level2_email, level3_email = approvers

    email_reply = level1_email

    if level1_email is None: 
        email_reply =  level2_email

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    d = conn.cursor()
    d.execute('''
        SELECT Name FROM Approvers
        WHERE Email_Address = ?
    ''', (email_reply, ))

    row = d.fetchone()

    Approvers_Name = row[0]
    conn.commit()
    conn.close()

    email_subject = f"Business Travelling Request Application submitted - Your ticket No is #{random_string}"

    email_body = generate_email_body(name, random_string)

    send_email([user_id], email_subject, email_body)

    email_subject_approvers = f"Business Travelling Request Approval Required – Ticket No #{random_string}"

    email_body_approvers = generate_email_body_approvers(name, random_string, Approvers_Name)

    send_email([email_reply], email_subject_approvers, email_body_approvers)

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    f = conn.cursor()
    
    for level, email in enumerate([level1_email, level2_email, level3_email], start=1):
        if email:  # Skip if email is None or empty
            f.execute('''
                INSERT INTO approvals (application_id, approver_email, approval_level, status, created_at)
                VALUES (?, ?, ?, 'Pending', ?)
            ''', (random_string, email, level, formatted_datetime))

    conn.commit()
    conn.close()
    flash("Business Travelling Request Application submitted successfully!", "success")

    return redirect(url_for('dashboard'))

@bp.route('/api/notifications')
def get_notifications():
    current_user_email = current_user.username

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()

    # Get approvals where:
    # - User is the approver
    # - Approval is still pending
    # - All **lower levels are already approved**
    c.execute('''
        SELECT a.application_id, a.Name, a.status, a.created_at, a.id
        FROM applications a
        WHERE a.Email_Address = ? ORDER BY a.updated_at
    ''', (current_user_email,))

    rows = c.fetchall()
    conn.close()

    notifications = []
    for row in rows:
        app_id = row[0]
        Name = row[1]
        status = row[2]
        # form_data = json.loads(row[3])  # form_data is stored as JSON
        timestamp = row[3] if row[3] else "Unknown time"
        id = row[4]

        try:
            time_str = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y')
        except:
            time_str = timestamp

        notifications.append({
            "id": app_id,
            "text": f"#{app_id} - Travel request submitted",
            "status": status,
            "time": time_str,
            "icon": "fa-file-text-o",
            "notice_id" : id
        })
    return jsonify(notifications)

@bp.route('/api/history')
def get_history():

    current_user_email = current_user.username

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()

    # Get approvals where:
    # - User is the approver
    # - Approval is still pending
    # - All **lower levels are already approved**
    c.execute('''
        SELECT a.application_id, a.Name, a.approval_level, a.created_at
        FROM approvals a
        WHERE a.approver_email = ?
          AND a.status = 'Pending'
          AND NOT EXISTS (
              SELECT 1 FROM approvals sub
              WHERE sub.application_id = a.application_id
                AND sub.approval_level < a.approval_level
                AND sub.status != 'Approved'
          )
    ''', (current_user_email,))

    rows = c.fetchall()
    conn.close()

    history = []
    for row in rows:
        app_id = row[0]
        Name = row[1]
        submission_lvl = row[2]
        # form_data = json.loads(row[3])  # form_data is stored as JSON
        timestamp = row[3] if row[3] else "Unknown time"

        try:
            time_str = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%d %b %Y')
        except:
            time_str = timestamp

        history.append({
            "id": app_id,
            "text": f"#{app_id} - Travel request submitted",
            "time": time_str,
            "icon": "fa-file-text-o"
        })

    return jsonify(history)

# For list page
@bp.route('/api/applications')
def get_applications():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT id, Name, created_at, submission_lvl, Destination, status FROM applications ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()

    result = []
    for row in rows:
        app_id = row[0]
        # form_data = json.loads(row[1])
        status = row[5]
        created_at = row[2]
        name = row[1]
        destination = row[4]

        result.append({
            "id": app_id,
            "name": name,
            "destination": destination,
            "status": status if status else "0/3",  # default if NULL
            "created_at": created_at
        })
    
    return jsonify(result)

# For History page
@bp.route('/api/History')
def get_History():
    current_user_email = current_user.username

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
    SELECT id, Name, created_at, submission_lvl, Destination, status
    FROM applications
    WHERE Email_Address = ?
    ORDER BY created_at DESC
""", (current_user_email,))
    rows = c.fetchall()
    conn.close()

    result = []
    for row in rows:
        app_id = row[0]
        # form_data = json.loads(row[1])
        status = row[5]
        created_at = row[2]
        name = row[1]
        destination = row[4]

        result.append({
            "id": app_id,
            "name": name,
            "destination": destination,
            "status": status if status else "0/3",  # default if NULL
            "created_at": created_at
        })
    
    return jsonify(result)

def send_email(email_to, email_subject, email_body):
    # Setting
    # _env = EnvMan().get()
    _email = "mysnoreply@coscon.com"
    # Email configuration
    smtp_port = 587  # Change port if necessary
    smtp_server   = "mail.coscon.com"
    smtp_username = "mysnoreply@coscon.com"
    smtp_password = "RPA#250825#"

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = "mysnoreply@coscon.com"
    msg['To'] = ', '.join(email_to)
    msg['Subject'] = email_subject

    # Check if email_body is not None before encoding
    if email_body is not None:
        # Ensure proper encoding of the email body
        email_body_encoded = email_body.encode('utf-8')

        # Attach the HTML email body
        msg.attach(MIMEText(email_body_encoded, 'html', 'utf-8'))
    else:
        # Handle the case where email_body is None (if needed)
        pass

    # Connect to SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Secure the connection
    server.login(smtp_username, smtp_password)

    # Send email
    recipients = email_to
    server.sendmail("mysnoreply@coscon.com", recipients, msg.as_string())

    # Close connection
    server.quit()

def generate_email_body(name, id):
    email_body = f"""
        <p>Hi {name}</p>
        <p>Your business travelling request application form has been successfully submitted.</p>
        <p>Ticket No #{id}</p>
        <p>You may track the status and updates of your request through the notifications section within the application.</p>
        <p>
            <a href="http://172.26.37.177:8802/login" target="_blank">
                Click here to log in and view the request
            </a>
        </p>
        """
    email_body += "<br/>"
    return email_body

def generate_email_body_approvers(name, id, approvers_name):
    email_body = f"""
        <p>Hi {name}</p>
        <p>You have received a business travelling request requires immediate attention.</p>
        <p>Ticket No #{id} submitted by {name} is currently pending your approval.</p>
        <p>Kindly review the request and take necessary action by approving or rejecting it at your earliest convenience.</p>
        <p>
            <a href="http://172.26.37.177:8802/login" target="_blank">
                Click here to log in and view the request
            </a>
        </p>
        <p>Thank you for your prompt response.</p>
        """
    email_body += "<br/>"
    return email_body

# Register routes
app.register_blueprint(bp)

# --------------------------
# Run App
# --------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8802)
