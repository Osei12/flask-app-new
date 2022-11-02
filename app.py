

from flask import Flask,render_template,request,redirect,flash,get_flashed_messages,url_for,Response,make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid as uuid
import io
import pdfkit


app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///manage.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:O26Ijle7CaiSZJogzN9W@containers-us-west-34.railway.app:6781/railway'
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



@app.route('/<int:id>/update' , methods=['GET','POST'])
def update(id):
    member = Records.query.get_or_404(id)
    
    if request.method=='POST':
        if member:
            member.name=request.form['name']
            member.email=request.form['email']
            if request.files['file']:
                member.profile=request.files['file']
                pic_filename = secure_filename( member.profile.filename)
                pic_name = str(uuid.uuid1()) + " _ " + pic_filename
                saver = request.files['file']
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                # pic_path=os.path.join(app.root_path,'static/profile',pic_filename)
                member.profile=pic_name 
                # member.profile.save(pic_path)               
                db.session.commit()
                flash('Updated succesfuly')
                return render_template('update.html' , member=member)
            else:
                db.session.commit()
                flash('Updated succesfuly')
                return render_template('update.html' , member=member)
        
    return render_template('update.html' , member=member)

@app.route('/<int:id>/delete' , methods=['GET','POST'])
def delete(id):
    member = Records.query.get_or_404(id)
    if member:
        db.session.delete(member)
        db.session.commit()
        member = Records.query.all()
        flash('Deleted Succesfully')
        return redirect(url_for('view'))
    return render_template('view.html' , member=member)


@app.route('/<int:id>/report', methods=['GET','POST'])
def get_member_detail(id):
    member=Records.query.get_or_404(id)
    
    return render_template('get_member_report.html',member=member)




# @app.route('/downlaod/report/excel')
# def download_report():
#     all_members = Records.query.all()
#     output = io.BytesIO()
    
#     workbook = xlwt.Workbook(encoding="UTF-8")
    
#     sh = workbook.add_sheet('Member Report')
#     sh.write(0, 0, 'Id')
#     sh.write(0, 1, 'Name')
#     sh.write(0, 2, 'Email')


    
#     idx=0
#     for member in all_members:
#         sh.write(idx+1, 0, str(member.id))
#         sh.write(idx+1, 1,  member.name)
#         sh.write(idx+1, 2, member.email)



    
#         idx+= 1
        
#     workbook.save(output)
#     output.seek(0)
#     return Response(output, mimetype="application/ms-excel",headers={"Content-Disposition":"attachment;filename=member_reports.xls"} )


if __name__=='__main__':
    app.run()