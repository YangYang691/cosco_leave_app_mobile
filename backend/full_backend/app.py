from flask import Flask, request, jsonify
import sqlite3
import base64

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

@app.post('/register')
def register():
    data = request.json
    email = data.get('email')
    pw = data.get('password')
    q("INSERT INTO Users (Email_Address, Password) VALUES (?, ?)", (email, pw))
    return jsonify(success=True)

@app.post('/login')
def login():
    d = request.json
    r = q("SELECT * FROM Users WHERE Email_Address=? AND Password=?", (d['email'], d['password']), one=True)
    return jsonify(success=(r is not None))

@app.get('/applications')
def list_apps():
    email = request.args.get('email')
    rows = q("SELECT * FROM applications WHERE applicant_email=?", (email,))
    return jsonify([dict(r) for r in rows])

@app.post('/apply')
def apply():
    d = request.json
    q(
        "INSERT INTO applications (applicant_email, department, reason, level1_status, level2_status, final_status) "
        "VALUES (?, ?, ?, 'pending', 'pending', 'pending')",
        (d['email'], d['department'], d['reason'])
    )
    return jsonify(success=True)

@app.get('/approvals')
def approvals():
    email = request.args.get('email')
    rows = q("SELECT * FROM approvals WHERE approver_email=?", (email,))
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
