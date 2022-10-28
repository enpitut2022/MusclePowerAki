from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///muscle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
now = datetime.datetime.now()

# データベースのmemberテーブルの定義
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    status = db.Column(db.String(10), default="start")
    days = db.Column(db.Integer, default=1)
    date = db.Column(db.DateTime, default=now)

@app.route('/')
def index():
    members = Member.query.filter_by(status = "start").all()
    membersNumber = len(members)
    allmember = Member.query.all()
    return render_template('index.html', ms=members, mn = membersNumber ,am =allmember)

@app.route('/addname', methods=["post"])
def addname():
    nowdate = datetime.datetime.now()
    name = request.form["name"]
    memberSearch = Member.query.filter_by(name = name).first()
    if memberSearch == None:
        newMember = Member(name=name)
        db.session.add(newMember)
    else:
        lastdate = memberSearch.date
        diff = nowdate - lastdate
        # if diff.seconds >= 236060 and diff.seconds <= 256060:
        if diff.seconds >= 30 and diff.seconds <= 60:
            memberSearch.status = "start"
            memberSearch.days += 1
            memberSearch.date = nowdate
        # elif diff.seconds > 256060:
        elif diff.seconds > 60:
            memberSearch.status = "start"
            memberSearch.days = 1
            memberSearch.date = nowdate

    db.session.commit()
    return redirect("/")

## おまじない
if __name__ == "__main__":
    app.run(debug=True)
