from flask import Flask, request, jsonify
import sqlite3
import base64
import bcrypt
import string
import random
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from flask import request, jsonify, render_template, send_file
# from weasyprint import HTML
import smtplib
from email.message import EmailMessage
import tempfile
from fastapi import FastAPI
from fastapi.responses import FileResponse
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
import sqlite3
import uuid
from pydantic import BaseModel
from flask_cors import CORS
from flask import send_from_directory

app = Flask(__name__)
CORS(app)

class ApplicationRequest(BaseModel):
    application_id: int

env = Environment(loader=FileSystemLoader("templates"))

DB = 'user.db'
app = Flask(__name__)

def q(sql, args=(), one=False):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cur = con.execute(sql, args)
    rows = cur.fetchall()
    con.commit()
    con.close()
    return (rows[0] if rows else None) if one else rows
@app.route("/")
def index():
    return send_from_directory("web", "index.html")

@app.post('/register')
def register():
    data = request.json
    email = data.get('email')
    pw = data.get('password')

    password = bcrypt.generate_password_hash(pw).decode('utf-8')

    q("INSERT INTO Users (Email_Address, Password) VALUES (?, ?)", (email, password))
    return jsonify(success=True)

@app.post('/login')
def login():
    data = request.json or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify(success=False, error="Email and password are required"), 400

    # Fetch user from DB
    user = q(
        "SELECT * FROM Users WHERE Email_Address=?",
        (email,),
        one=True
    )

    if not user:
        return jsonify(success=False, error="User not found"), 404

    stored_hash = user['Password']  # This is a string, like "$2b$12$7/MU7f..."

    print(type(stored_hash))

    try:
        # bcrypt needs bytes, so encode both
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return jsonify(success=True)
        else:
            return jsonify(success=False, error="Invalid password"), 401
    except ValueError as e:
        # Handle invalid hash format
        return jsonify(success=False, error=f"Hash error: {str(e)}"), 500

@app.get('/applications')
def list_apps():
    email = request.args.get('email')
    rows = q("SELECT * FROM applications WHERE Email_Address=?", (email,))
    return jsonify([dict(r) for r in rows])

@app.post('/apply')
def apply():
    d = request.json
    length = 10
    chars = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(chars, k=length))
    current_date = datetime.now()
    formatted_datetime = current_date.strftime('%Y-%m-%d %H:%M:%S')
    q(
        "INSERT INTO applications (Email_Address, Name, department, submission_lvl, SAP_ID, Apply_Date, From_Date," 
        "To_Date, Total_Days, Accomodation, Transport, Additional, Destination, Purpose, application_id, created_at, updated_at, Status)"
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (d['email'],d['name'], d['department'], "Level 1", d['sapID'], d['apply_date'], d['start_date'],  d['end_date'], d['total_days'], d['accommodation_pay_by_applicant'], d['travellingmode'], d['additional50'], d['destination'], d['purpose'], random_string, formatted_datetime, formatted_datetime, "Pending")
    )

    rows = q(
        "SELECT Position FROM Users WHERE Email_Address = ?",
        (d['email'],),
        one=True
    )
    if rows:
        user_position = rows[0][0]

    if user_position == '1':
        pos = 'Executive & Manager'
    else:
        pos = 'General Manager'

    print(d['department'])
    print(pos)

    rows = q(
        "SELECT level1, level2, level3 FROM approval_matrix WHERE department = ? AND position = ?",
        (d['department'], pos),
        one=True
    )
    if rows:
        approvers = rows

    print(approvers)
    print(rows)

    level1_email, level2_email, level3_email = approvers

    email_reply = level1_email

    if level1_email is None: 
        email_reply =  level2_email

    rows = q(
        "SELECT Name FROM Approvers WHERE Email_Address = ?",
        (email_reply,),
        one=True
    )
    if rows:
        Approvers_Name = rows[0][0]

    email_subject = f"Business Travelling Request Application submitted - Your ticket No is #{random_string}"

    email_body = generate_email_body(d['name'], random_string)

    # send_email(d['email'], email_subject, email_body)

    email_subject_approvers = f"Business Travelling Request Approval Required – Ticket No #{random_string}"

    email_body_approvers = generate_email_body_approvers(d['name'], random_string, Approvers_Name)

    # send_email([email_reply], email_subject_approvers, email_body_approvers)

    for level, email in enumerate([level1_email, level2_email, level3_email], start=1):
        if email:  # Skip if email is None or empty
            q(
                "INSERT INTO approvals (application_id, Name, approver_email, approval_level, status, created_at)"
                "VALUES (?, ?, ?, 'Pending', ?)",
                (random_string, d['name'], email, level, formatted_datetime)
            )

    return jsonify(success=True)

@app.get('/approvals')
def approvals():
    email = request.args.get('email')
    rows = q("""
        SELECT a.*
        FROM approvals a
        WHERE a.approver_email = ?
        AND a.status = 'Pending'
        AND NOT EXISTS (
            SELECT 1
            FROM approvals prev
            WHERE prev.application_id = a.application_id
            AND prev.approval_level < a.approval_level
            AND prev.status != 'Approved'
        )
    """, (email,))
    return jsonify([dict(r) for r in rows])

@app.post('/upload_file')
def upload_file():
    d = request.json
    fid = d['application_id']
    blob = base64.b64decode(d['file_data'])
    con = sqlite3.connect(DB)
    con.execute("UPDATE applications SET attachment=? WHERE id=?", (blob, fid))
    con.commit()
    con.close()
    return jsonify(success=True)

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

@app.route("/decide", methods=["POST"])
def decide_application():
    d = request.json
    application_id = d["application_id"]
    decision = d["decision"]       # "Approved" or "Rejected"
    approver_email = d["approver"]

    formatted_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print("Testing")

    print(application_id)

    # 1️⃣ Get department of the application
    row = q(
        "SELECT Department, Name, Email_Address FROM applications WHERE application_id = ?",
        (application_id,),
        one=True
    )
    if not row:
        return jsonify({"success": False, "error": "Application not found"}), 404

    department = row[0]
    applicant_name = row[1]
    applicant_email = row[2]


    # 2️⃣ Get approval level
    level = get_user_approval_level(department, approver_email)

    if decision == "Approved":

        # 3️⃣ Update approvals table
        q(
            '''UPDATE approvals
            SET status = ?, approved_at = ?
            WHERE application_id = ? AND approval_level = ? AND approver_email = ?''',
            (decision, datetime.now(), application_id, level, approver_email)
        )

        # 4️⃣ Count total approval levels for this application
        total_levels_row = q(
            "SELECT COUNT(*) FROM approvals WHERE application_id = ?",
            (application_id,),
            one=True
        )
        total_levels = total_levels_row[0]

        # 5️⃣ Count how many are approved
        approved_count_row = q(
            "SELECT COUNT(*) FROM approvals WHERE application_id = ? AND status = 'Approved'",
            (application_id,),
            one=True
        )
        approved_count = approved_count_row[0]

        # 6️⃣ If all levels approved, update application status
        if approved_count == total_levels:
            q(
                "UPDATE applications SET status = 'Approved', updated_at = ? WHERE application_id = ?",
                (formatted_datetime, application_id)
            )
        else:

            # 8️⃣ Get next approver
            next_approver_row = q(
                '''SELECT approval_level, approver_email
                FROM approvals
                WHERE application_id = ? AND approval_level > ? AND status = 'Pending'
                ORDER BY approval_level ASC
                LIMIT 1''',
                (application_id, level),
                one=True
            )

            if next_approver_row:
                next_level, next_approver_email = next_approver_row
                subject = f"Approval - Business Travel Application #{application_id}"
                body = f"""
                <p>Dear Approver,</p>
                <p>You have received a request requires immediate attention.</p>
                <p>Ticket No #{application_id} submitted by {applicant_name} is currently pending your approval.</p>
                <p>Kindly review the request and take necessary action by approving or rejecting it at your earliest convenience.</p>
                <p>
                <a href="http://172.26.37.177:8802/login" target="_blank">
                    Click here to log in and view the request
                </a>
                </p>
                <p>Thank you for your prompt response.</p>
                """
                # send_email([next_approver_email], subject, body)
    elif decision == "Rejected":
        # 8️⃣ Mark application as Rejected
        q(
            "UPDATE applications SET status = 'Rejected', updated_at = ? WHERE application_id = ?",
            (formatted_datetime, application_id)
        )
        # 9️⃣ Mark all approvals as Rejected
        q(
            "UPDATE approvals SET status = 'Rejected' WHERE application_id = ?",
            (application_id,)
        )
        # 10️⃣ Send rejection email to applicant
        subject = f"Business Application Request Rejected - Application #{application_id}"
        body = f"""
        <p>Dear {applicant_name},</p>
        <p>Your business travel application request #{application_id} has been rejected by {approver_email}.</p>
        <p>
        <a href="http://172.26.37.177:8802/login" target="_blank">
            Click here to log in and view the request
        </a>
        </p>
        """
        # send_email([applicant_email], subject, body)



    return jsonify({"success": True})

@app.get('/application/<application_id>')
def get_application_detail(application_id):
    row = q(
        "SELECT * FROM applications WHERE application_id = ?",
        (application_id,),
        one=True
    )

    if not row:
        return jsonify({"success": False, "error": "Not found"}), 404

    return jsonify(dict(row))

@app.route("/generate-document", methods=["POST"])
def generate_document():

    data = request.json
    application_id = data.get("application_id")

    # fetch data from database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM applications WHERE application_id = ?",
        (application_id,)
    )

    row = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM approvals WHERE application_id = ?",
        (application_id,)
    )
    approvals = cursor.fetchall()

    conn.close()

    # data = {
    #     "name": row[0],
    #     "amount": row[1],
    #     "date": row[2]
    # }

    approval_data = {}
    for row2 in approvals:
        level = row2['approval_level']
        if isinstance(row2['created_at'], str):
            created_at = datetime.strptime(row2['created_at'], '%Y-%m-%d %H:%M:%S')  # or your actual format
        else:
            created_at = row2['created_at']

        approval_data[level] = {
            'email': row2['approver_email'],
            'status': row2['status'],
            'date': created_at.strftime('%Y-%m-%d')
        }

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

    # render HTML
    template = env.get_template("print.html")
    html = template.render(applicant)

    filename = f"{uuid.uuid4()}.pdf"

    # convert HTML → PDF
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.set_content(html)

        page.pdf(
            path=filename,
            format="A4",
            print_background=True
        )

        browser.close()

    return send_file(
    filename,
    mimetype="application/pdf",
    as_attachment=True,
    download_name="application.pdf"
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
