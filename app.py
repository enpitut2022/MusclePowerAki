from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///muscle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# データベースのmemberテーブルの定義
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

@app.route('/')
def index():
    members = Member.query.all()
    return render_template('index.html', ms=members)

@app.route('/addname', methods=["post"])
def addname():
    name = request.form["name"]
    newMember = Member(name=name)
    db.session.add(newMember)
    db.session.commit()
    return redirect("/")

## おまじない
if __name__ == "__main__":
    app.run(debug=True)