from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///muscle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)

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
    nowdate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    name = request.form["name"]
    memberSearch = Member.query.filter_by(name = name).first()
    if memberSearch == None:
        # baseDate = datetime.datetime(2022, 10, 28, 22, 0, 0)
        # ↓デバッグ用
        baseDate = datetime.datetime(2022, 10, 28, 17, 30, 30)
        diff_a = abs(baseDate - nowdate)
        diff_a_sec = diff_a.seconds % (24 * 60 * 60)
        if diff_a_sec < 60 * 60 or diff_a_sec >= 23 * 60 * 60:
            newMember = Member(name=name)
            db.session.add(newMember)
    else:
        if memberSearch.status == "finish":
            lastdate = memberSearch.date
            diff = nowdate - lastdate
            # if diff.seconds >= 23 * 60 * 60 and diff.seconds <= 25 * 60 * 60:
            # ↓デバッグ用
            if diff.seconds >= 30 and diff.seconds <= 60:
                memberSearch.status = "start"
                memberSearch.days += 1
                memberSearch.date = nowdate
            # elif diff.seconds > 25*60*60:
            # ↓デバッグ用
            elif diff.seconds > 60:
                diff_b_sec = diff.seconds % (24 * 60 * 60)
                if diff_b_sec < 60 * 60 or diff_b_sec >= 23 * 60 * 60:
                    memberSearch.status = "start"
                    memberSearch.days = 1
                    memberSearch.date = nowdate
    db.session.commit()
    return redirect("/")

## おまじない
if __name__ == "__main__":
    app.run(debug=True)
