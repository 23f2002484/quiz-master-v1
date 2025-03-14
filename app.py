from flask import Flask
from models import db,User



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
if __name__=='__main__':
    app.run(debug=True)