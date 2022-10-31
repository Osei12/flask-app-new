
from flask import Flask,render_template,request,redirect,flash,get_flashed_messages,url_for,Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid as uuid
import io
import xlwt
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///manage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'jkhdgcyggHFHFHTHF65464^$^&'

import os
UPLOAD_FOLDER = 'static/images/profile/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db= SQLAlchemy()
db.init_app(app)


############################## MODELS
class Records(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=True)
    email = db.Column(db.String(),nullable=True)
    profile = db.Column(db.String(), nullable=True)
    date_created = db.Column(db.String(), default=datetime.utcnow)
    
    
    def __init__(self, name,email,profile):
        self.name=name
        self.email=email
        self.profile=profile
        
    def __repr__(self):
        return f"{self.name}:{self.email}"

with app.app_context():
    db.create_all()

############################## ROUTES

@app.route('/', methods=['GET','POST'])
def home():
    return render_template('index.html')

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method=='GET':
        return render_template('add.html')
    if request.method=='POST':
        name = request.form['name']
        email = request.form['email']
        profile = request.files['file']
        
        pic_filename = secure_filename(profile.filename)
        pic_name = str(uuid.uuid1()) + " _ " + pic_filename
        saver = request.files['file']
        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        profile=pic_name
        
        new_record = Records(
            name=name,
            email=email,
            profile=profile
        )
        db.session.add(new_record)
        db.session.commit()
        flash('New record added successfully !!')
        return redirect(url_for('add'))
    return render_template('add.html')


@app.route('/view_list', methods=['GET','POST'])
def view():
    members = Records.query.all()
    return render_template('view.html',members=members)

@app.route('/downlaod/report/excel')
def download_report():
    all_members = Records.query.all()
    output = io.BytesIO()
    
    workbook = xlwt.Workbook(encoding="UTF-8")
    
    sh = workbook.add_sheet('Member Report')
    sh.write(0, 0, 'Id')
    sh.write(0, 1, 'Name')
    sh.write(0, 2, 'Email')


    
    idx=0
    for member in all_members:
        sh.write(idx+1, 0, str(member.id))
        sh.write(idx+1, 1,  member.name)
        sh.write(idx+1, 2, member.email)



    
        idx+= 1
        
    workbook.save(output)
    output.seek(0)
    return Response(output, mimetype="application/ms-excel",headers={"Content-Disposition":"attachment;filename=member_reports.xls"} )


if __name__=='__main__':
    app.run()