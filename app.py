from flask import Flask,request,redirect,render_template,session,url_for,flash
from models import db,User,Subject,Quiz,Question,Chapter,Score
from datetime import datetime,date
from sqlalchemy.sql import func
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import os
import numpy as np


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


@app.route('/admin_dashboard')
def admin_dashboard():
    id=session.get('id')
    user =User.query.filter_by(id=id).first()
    subjects =Subject.query.all()
    return render_template("admin_dashboard.html",user=user,subjects=subjects)
    



@app.route('/add_subject',methods=['GET','POST'])
def add_subject():
    if request.method=='GET':
        return render_template("add_subject.html")
    if request.method=='POST':
        id=request.form.get('id')
        subject =Subject.query.filter_by(id=id).first()
        if subject:
            flash("Id already exists","danger")
            return redirect(url_for('add_subject'))
        name=request.form.get('name')
        description=request.form.get('description')
        new_subject=Subject(id=id,name=name,description=description)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

@app.route('/add_chapter/<subject_id>',methods=['GET','POST'])
def add_chapter(subject_id):
    if request.method=='GET':
        return render_template("add_chapter.html",subject_id=subject_id)
    if request.method=='POST':
        id=request.form.get('id')
        chapter =Chapter.query.filter_by(id=id).first()
        if chapter:
            flash("Id already exists","danger")
            return redirect(url_for('add_chapter',subject_id=subject_id))
        name=request.form.get('name')
        description=request.form.get('description')
        new_chapter=Chapter(id=id,name=name,description=description,subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for('manage_chapter',subject_id=subject_id))
    
@app.route('/add_quiz',methods=['GET','POST'])
def add_quiz():
    if request.method=='GET':
        chapters =Chapter.query.all()
        return render_template("add_quiz.html",chapters=chapters)
    if request.method=='POST':
        id=request.form.get('id')
        quiz =Quiz.query.filter_by(id=id).first()
        if quiz:
            flash("Id already exists","danger")
            return redirect(url_for('add_quiz'))
        remarks=request.form.get('remarks')
        quiz_date_str=request.form.get('quiz_date')
        time_dur_str=request.form.get('time_dur')
        chapter_id=request.form.get('chapter_id')
        quiz_date=datetime.strptime(quiz_date_str,'%Y-%m-%d').date()
        time_dur=datetime.strptime(time_dur_str,'%H:%M').strftime("%H:%M")
        new_quiz=Quiz(id=id,remarks=remarks,quiz_date=quiz_date,time_dur=time_dur,chapter_id=chapter_id)
        db.session.add(new_quiz)
        db.session.commit()
        return redirect(url_for('manage_quiz',chapter_id=chapter_id))
    
@app.route('/add_question/<quiz_id>',methods=['GET','POST'])
def add_question(quiz_id):
    if request.method=='GET':
        return render_template("add_question.html",quiz_id=quiz_id)
    if request.method=='POST':
        id=request.form.get('id')
        question =Question.query.filter_by(id=id).first()
        if question:
            flash("Id already exists","danger")
            return redirect(url_for('add_question',quiz_id=quiz_id))
        que=request.form.get('que')
        o_a=request.form.get('o_a')
        o_b=request.form.get('o_b')
        o_c=request.form.get('o_c')
        o_d=request.form.get('o_d')
        correct_o=request.form.get('correct_o')
        new_question=Question(id=id,que=que,o_a=o_a,o_b=o_b,o_c=o_c,o_d=o_d,correct_o=correct_o,quiz_id=quiz_id)
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('manage_question',quiz_id=quiz_id))
    
@app.route('/admin_summary')
def admin_summary():
    
    subjects1=(db.session.query(Subject.name,db.func.max(Score.tot_score/func.coalesce(db.session.query( func.count(Question.id)).filter(Question.quiz_id==Score.quiz_id).scalar_subquery(),1)*100))
    .join(Chapter,Chapter.subject_id==Subject.id)
    .join(Quiz,Quiz.chapter_id==Chapter.id)
    .join(Score,Score.quiz_id==Quiz.id)
    .group_by(Subject.id).all())

    

    sub_names1=[subject[0] for subject in subjects1]
    max_score=[subject[1] for subject in subjects1]
    

    if not sub_names1:
        flash("No quiz data available","warning")
        return render_template('admin_summary.html',img_path1=None)
    
    

    static_folder=os.path.join(os.getcwd(),"static")

    img_path1=os.path.join(static_folder,f"summary_chart_max_score_vs_subject.png")
    if sub_names1:
        plt.figure(figsize=(10,5))
        plt.bar(sub_names1,max_score,color='skyblue')
        plt.xlabel("Subjects")
        plt.ylabel("Max Score")
        plt.title("Subjects vs Max Score")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(img_path1)
        plt.close()
    else:
        img_path1=None

    
    return render_template("admin_summary.html",img_path1=url_for('static',filename=f'summary_chart_max_score_vs_subject.png')if img_path1 else None)
                           


    
    return render_template("admin_summary.html")
@app.route('/delete_user/<id>',methods=['POST'])
def delete_user(id):
    user =User.query.filter_by(id=id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    
    return redirect(url_for('manage_user'))


@app.route('/delete_subject/<subject_id>',methods=['POST'])
def delete_subject(subject_id):
    subject =Subject.query.get(subject_id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_chapter/<chapter_id>/<subject_id>',methods=['POST'])
def delete_chapter(chapter_id,subject_id):
    chapter =Chapter.query.get(chapter_id)
    if chapter:
        db.session.delete(chapter)
        db.session.commit()
    
    return redirect(url_for('manage_chapter',subject_id=subject_id))

@app.route('/delete_quiz/<quiz_id>',methods=['POST'])
def delete_quiz(quiz_id):
    quiz =Quiz.query.get(quiz_id)
    if quiz:
        db.session.delete(quiz)
        db.session.commit()
    
    return redirect(url_for('manage_quiz'))

@app.route('/delete_question/<question_id>/<quiz_id>',methods=['POST'])
def delete_question(question_id,quiz_id):
    question =Question.query.get(question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
    
    return redirect(url_for('manage_question',quiz_id=quiz_id))

@app.route('/edit_quiz/<quiz_id>',methods=['POST','GET'])
def edit_quiz(quiz_id):
    quiz=Quiz.query.get(quiz_id)
    if request.method=='POST':
        quiz.remarks=request.form['remarks']
        quiz.chapter_id=request.form['chapter_id']
        quiz.quiz_date=datetime.strptime(request.form['quiz_date'],'%Y-%m-%d').date()
        quiz.time_dur=datetime.strptime(request.form['time_dur'],'%H:%M').strftime("%H:%M")
            
        db.session.commit()
        return redirect(url_for('manage_quiz'))
    else:
        chapters=Chapter.query.all()
        return render_template("edit_quiz.html",quiz=quiz,chapters=chapters)
    
@app.route('/edit_subject/<subject_id>',methods=['POST','GET'])
def edit_subject(subject_id):
    subject =Subject.query.get(subject_id)
    if request.method=='POST':
        subject.name=request.form['name']
        subject.description=request.form['description']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template("edit_subject.html",subject=subject)

@app.route('/edit_chapter/<chapter_id>/<subject_id>',methods=['POST','GET'])
def edit_chapter(chapter_id,subject_id):
    chapter =Chapter.query.get(chapter_id)
    if request.method=='POST':
        chapter.name=request.form['name']
        chapter.description=request.form['description']
        db.session.commit()
        return redirect(url_for('manage_chapter',subject_id=subject_id))
    else:
        return render_template("edit_chapter.html",chapter=chapter,subject_id=subject_id)
    
@app.route('/edit_question/<question_id>/<quiz_id>',methods=['POST','GET'])
def edit_question(question_id,quiz_id):
    question=Question.query.get(question_id)
    if request.method=='POST':
        question.que=request.form['que']
        question.o_a=request.form['o_a']
        question.o_b=request.form['o_b']
        question.o_c=request.form['o_c']
        question.o_d=request.form['o_d']
        question.correct_o=request.form['correct_o']
        db.session.commit()
        return redirect(url_for('manage_question',quiz_id=quiz_id))
    else:
        return render_template("edit_question.html",question=question,quiz_id=quiz_id)


    
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
            
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


            
@app.route('/manage_user')
def manage_user():
    users =User.query.filter(User.role=="Student").all()
    return render_template("manage_user.html",users=users)

@app.route('/manage_chapter/<subject_id>')
def manage_chapter(subject_id):
    chapters =Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template("manage_chapter.html",chapters=chapters,subject_id=subject_id)

@app.route('/manage_quiz')
def manage_quiz():
    quizzes =Quiz.query.all()
    return render_template("manage_quiz.html",quizzes=quizzes)

@app.route('/manage_question/<quiz_id>')
def manage_question(quiz_id):
    questions =Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template("manage_question.html",questions=questions,quiz_id=quiz_id)

@app.route('/quiz',methods=['GET','POST'])
def quiz():
    subjects =Subject.query.all()
    selected_subject_id=request.form.get('subject')
    
    selected_chapter_id=request.form.get('chapter')
    chapters =Chapter.query.filter_by(subject_id=selected_subject_id).all() if selected_subject_id else []
    quizzes= Quiz.query.filter(Quiz.chapter_id==selected_chapter_id , Quiz.quiz_date == date.today()).all() if selected_chapter_id else []
    upcoming_quizzes= Quiz.query.filter(Quiz.quiz_date > date.today()).order_by(Quiz.quiz_date).all()

    return render_template('quiz.html', subjects=subjects, chapters=chapters, quizzes=quizzes, upcoming_quizzes=upcoming_quizzes,selected_subject_id=selected_subject_id, selected_chapter_id=selected_chapter_id)

@app.route('/quiz_history/<user_id>')
def quiz_history(user_id):
    q_history=Score.query.filter_by(user_id=user_id).order_by(Score.attempt_timing.desc()).all()
    q_attempted=len(q_history)
    tot_obt_marks=sum(q.tot_score for q in q_history)
    out_off=sum(len(q.quiz.questions) for q in q_history)
    avg_per=(tot_obt_marks/out_off)*100  if out_off>0 else 0
    avg_per=f"{avg_per:.2f}"
    q_history=Score.query.filter_by(user_id=user_id).order_by(Score.attempt_timing.desc()).all()
    return render_template("quiz_history.html",q_history=q_history,q_attempted=q_attempted,avg_per=avg_per)


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

    q_history=Score.query.filter_by(user_id=user_id).order_by(Score.attempt_timing.desc()).all()
    q_attempted=len(q_history)
    tot_obt_marks=sum(q.tot_score for q in q_history)
    out_off=sum(len(q.quiz.questions) for q in q_history)
    avg_per=(tot_obt_marks/out_off)*100  if out_off>0 else 0
    avg_per=f"{avg_per:.2f}"
    return render_template("student_dashboard.html",user=user,q_attempted=q_attempted,avg_per=avg_per,q_history=q_history)


@app.route('/student_summary')
def student_summary():
    user_id=session['id']
    subjects1=(db.session.query(Subject.name,db.func.count(Quiz.id))
    .join(Chapter,Chapter.subject_id==Subject.id)
    .join(Quiz,Quiz.chapter_id==Chapter.id)
    .join(Score,Score.quiz_id==Quiz.id)
    .filter(Score.user_id==user_id)
    .group_by(Subject.id).all())

    subjects2 = (db.session.query(Subject.name,func.avg(Score.tot_score/func.coalesce(db.session.query( func.count(Question.id)).filter(Question.quiz_id==Score.quiz_id).scalar_subquery(),1)*100).label ("avg_score"))
    .join(Chapter, Chapter.subject_id == Subject.id)
    .join(Quiz, Quiz.chapter_id == Chapter.id)
    .join(Score, Score.quiz_id == Quiz.id)
    .filter(Score.user_id == user_id)
    .group_by(Subject.id)
    .all())

    sub_names1=[subject[0] for subject in subjects1]
    q_count=[subject[1] for subject in subjects1]

    sub_names2=[subject[0] for subject in subjects2]
    perform=[subject[1] for subject in subjects2]

    if not sub_names1:
        flash("No quiz data available","warning")
        return render_template('student_summary.html',img_path1=None)
    
    if not sub_names2:
        flash("No quiz data available","warning")
        return render_template('student_summary.html',img_path2=None)

    static_folder=os.path.join(os.getcwd(),"static")

    img_path1=os.path.join(static_folder,f"{user_id}_summary_chart_no_of_quizzes_vs_subject.png")
    if sub_names1:
        plt.figure(figsize=(10,5))
        plt.bar(sub_names1,q_count,color='skyblue')
        plt.xlabel("Subjects")
        plt.ylabel("No. of Quizzes")
        plt.title("Subjects vs No. of quizzes")
        plt.xticks(rotation=45)
        max_y=max(q_count) if q_count else 1
        plt.yticks(np.arange(0,max_y+1,1))
        plt.tight_layout()
        plt.savefig(img_path1)
        plt.close()
    else:
        img_path1=None

    img_path2=os.path.join(static_folder,f"{user_id}_summary_chart_performance_vs_subject.png")
    if sub_names2:
        plt.figure(figsize=(10,5))
        plt.bar(sub_names2,perform,color='skyblue')
        plt.xlabel("Subjects")
        plt.ylabel("Performance")
        plt.title("Subjects vs Performance")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(img_path2)
        plt.close()
    else:
        img_path2=None
    
    

    return render_template("student_summary.html",img_path1=url_for('static',filename=f'{user_id}_summary_chart_no_of_quizzes_vs_subject.png')if img_path1 else None
                           ,img_path2=url_for('static',filename=f'{user_id}_summary_chart_performance_vs_subject.png')if img_path2 else None)
    

@app.route('/start_quiz/<quiz_id>')
def start_quiz(quiz_id):
    quiz =Quiz.query.get(quiz_id)
    questions=Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template("start_quiz.html",quiz=quiz,questions=questions)

@app.route('/submit_quiz/<quiz_id>',methods=['POST'])
def submit_quiz(quiz_id):
    quiz=Quiz.query.get(quiz_id)
    user_id=session.get('id')
    questions=Question.query.filter_by(quiz_id=quiz_id).all()
    score=0
    for question in questions:
        user_ans=request.form.get(f'{question.id}')
        if user_ans and user_ans==question.correct_o:
            score+=1
    new_score=Score(quiz_id=quiz_id,user_id=user_id,tot_score=score)
    db.session.add(new_score)
    db.session.commit()
    score=Score.query.order_by(Score.id.desc()).first()
    return redirect(url_for('user_result',score_id=score.id))

@app.route('/search')
def search():
    search=request.args.get('search')
    user=User.query.filter_by(id=search).first()
    if user:
        return redirect(url_for('search_user',user_id=user.id))
    subject=Subject.query.filter_by(id=search).first()
    if subject:
        return redirect(url_for('search_subject',subject_id=subject.id))
    quiz=Quiz.query.filter_by(id=search).first()
    if quiz:
        return redirect(url_for('search_quiz',quiz_id=quiz.id))
        
    return "Invalid Input"

@app.route('/search_user/<user_id>')
def search_user(user_id):
    user=User.query.filter_by(id=user_id).first()
    return render_template("search_user.html",user=user)

@app.route('/search_subject/<subject_id>')
def search_subject(subject_id):
    subject=Subject.query.filter_by(id=subject_id).first()
    return render_template("search_subject.html",subject=subject)

@app.route('/search_quiz/<quiz_id>')
def search_quiz(quiz_id):
    quiz=Quiz.query.filter_by(id=quiz_id).first()
    return render_template("search_quiz.html",quiz=quiz)

@app.route('/user_search')
def user_search():
    search=request.args.get('search')
    
    subject=Subject.query.filter_by(id=search).first()
    if subject:
        return redirect(url_for('user_search_subject',subject_id=subject.id))
    chapter=Chapter.query.filter_by(id=search).first()
    if chapter:
        return redirect(url_for('user_search_chapter',chapter_id=chapter.id))
    quiz=Quiz.query.filter_by(id=search).first()
    if quiz:
        return redirect(url_for('user_search_quiz',quiz_id=quiz.id))
    return "Invalid Input"

@app.route('/user_search_chapter/<chapter_id>')
def user_search_chapter(chapter_id):
    chapter=Chapter.query.filter_by(id=chapter_id).first()
    return render_template("user_search_chapter.html",chapter=chapter)

@app.route('/user_search_subject/<subject_id>')
def user_search_subject(subject_id):
    subject=Subject.query.filter_by(id=subject_id).first()
    return render_template("user_search_subject.html",subject=subject)

@app.route('/user_search_quiz/<quiz_id>')
def user_search_quiz(quiz_id):
    quiz=Quiz.query.filter_by(id=quiz_id).first()
    return render_template("user_search_quiz.html",quiz=quiz)


@app.route('/user_result/<score_id>')
def user_result(score_id):
    score=Score.query.filter_by(id=score_id).first()
    questions=Question.query.filter_by(quiz_id=score.quiz_id).all()
    return render_template("user_result.html",score=score,questions=questions)

@app.route('/view_detail_user/<score_id>')
def view_detail_user(score_id):
    score=Score.query.filter_by(id=score_id).first()
    questions=Question.query.filter_by(quiz_id=score.quiz_id).all()
    return render_template("view_detail_user.html",score=score,questions=questions)

@app.route('/view_detail/<score_id>')
def view_detail(score_id):
    score=Score.query.filter_by(id=score_id).first()
    questions=Question.query.filter_by(quiz_id=score.quiz_id).all()
    return render_template("view_detail.html",score=score,questions=questions)



if __name__=='__main__':
    app.run(debug=True)