from flask import Flask,request,redirect,render_template,session,url_for,flash
from models import db,User,Subject



app =Flask(__name__)

app.secret_key = "patilruchika2005"

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    adminexist =User.query.filter_by(role="Admin").first()
    if not adminexist:
        admin=User(email="admin@gmail.com",username="Admin",date_of_birth='15-07-2005',qualification='Engineer',role="Admin",password="1111")
        db.session.add(admin)
        db.session.commit()


@app.route('/')
def login_page():
    return redirect('/login')


@app.route('/admin_dashboard',methods=['GET','POST'])
def admin_dashboard():
    if request.method=='GET':
        id=session.get('id')
        user =User.query.filter_by(id=id).first()
        return render_template("admin_dashboard.html",user=user)
    
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        
        userexist =User.query.filter_by(email=email).first()
        if not userexist:
            flash("Email not found.","warning")
            return redirect(url_for('register'))
        else: 
            if userexist.password==password:
                session['id']=userexist.id
                if userexist.role=="Student":
                    return redirect('/student_dashboard')
                else:
                    return redirect('/admin_dashboard')
            else:
                flash("Incorrect Password.","warning")
                return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='GET':
        return render_template("register.html")
    if request.method=='POST':
        email=request.form.get('email')
        user =User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists","danger")
            return redirect(url_for('register'))
        username=request.form.get('username')
        password=request.form.get('password')
        qualification=request.form.get('qualification')
        dob=request.form.get('date_of_birth')
        new_user=User(email=email,password=password,username=username,qualification=qualification,date_of_birth=dob)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

@app.route('/student_dashboard')
def student_dashboard():
    
    user_id=session.get('id')
    user =User.query.get(user_id)

    return render_template("student_dashboard.html",user=user)
    

if __name__=='__main__':
    app.run(debug=True)