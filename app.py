from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

# DBのURI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///muscle.db'
# おまじない
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# データベースのmemberテーブルの定義
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    status = db.Column(db.String(10), default="start")
    days = db.Column(db.Integer, default=1)
    max_days = db.Column(db.Integer, defalut=1)
    date = db.Column(db.DateTime)
    teamid = db.Column(db.Integer)
    goal = db.Column(db.String(150))
    training_detail = db.Column(db.String(150))

# データベースのcommentテーブルの定義
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    comment = db.Column(db.String(256))
    teamid = db.Column(db.Integer)

# データベースのteamテーブルの定義
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    description = db.Column(db.String(128))

@app.route('/')
def index():
    team = Team.query.all()
    return render_template('index.html', tm =team)

@app.route('/detail/<int:id>')
def detail(id):
    teamdata = Team.query.get(id)
    # start状態のメンバー全員を取得
    members = Member.query.filter_by(teamid = id).filter_by(status = "start").order_by(Member.date).all()
    # start状態のメンバー数をカウント
    membersNumber = len(members)
    # 状態関係なくメンバー全員を取得
    allmember = Member.query.filter_by(teamid = id).order_by(Member.days.desc()).all()
    # コメントすべてを取得
    comments = Comment.query.filter_by(teamid = id).all()
    # index.htmlに値を渡し、表示
    return render_template('detail.html',td = teamdata, ms = members, mn = membersNumber, am = allmember, cm = comments)

@app.route('/workstart', methods=["post"])
def workstart():
    teamid = int(request.form["teamid"])
    # 現在時刻の取得
    nowdate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    ## デバッグ用(1日経過させる)
    ## nowdate = datetime.datetime.utcnow() + datetime.timedelta(hours=9) + datetime.timedelta(days = 1)
    # formで入力された名前(name)を受け取る
    name = request.form["name"]
    # 入力された名前をDBから検索
    memberSearch = Member.query.filter_by(name = name).first()
    # DBに名前がなかった場合
    if memberSearch == None:
        # 基準となる時刻
        teamsearch = Team.query.filter_by(id = teamid).first()
        baseDate = teamsearch.date
        ## ↓デバッグ用(デモの日時)
        ## baseDate = datetime.datetime(2022, 10, 28, 12, 30, 0)
        # 基準となる時刻と現在時刻の差を取る(絶対値)
        diff_a = abs(baseDate - nowdate)
        # その差の秒数
        diff_a_sec = diff_a.seconds
        # 秒数が1時間未満または23時間以上なら設定された日時の前後1時間以内とみなす
        if diff_a_sec < 60 * 60 or diff_a_sec >= 23 * 60 * 60:
            # 新しくメンバーを追加
            newMember = Member(name=name, date=nowdate, teamid=teamid)
            db.session.add(newMember)
    # DBに名前があった場合
    else:
        if memberSearch.teamid == teamid:
        # その名前のメンバーのステータスがfinish(startでない)とき
            if memberSearch.status == "finish":
                # その名前のメンバーの最終運動日時を取得
                lastdate = memberSearch.date
                # 現在時刻と最終運動日時を比較
                diff = nowdate - lastdate
                # 1日と1時間(25時間以内)もしくは0日と23時間の範囲にdiffが収まったとき
                # すなわち、最後に運動した日の翌日に運動するとき
                if (diff.seconds <= 60 * 60 and diff.days == 1) or (diff.seconds >= 23 * 60 * 60 and diff.days == 0):
                    # そのMemberをstart状態にして連続日数を1追加し、最終運動日時を更新する
                    memberSearch.status = "start"
                    memberSearch.days += 1
                    memberSearch.date = nowdate
                # diffの範囲が設定された時間の前後1時間に収まり、かつ最後に運動した日から2日以上経過しているとき
                elif (diff.seconds <= 60 * 60 and diff.days >= 2) or (diff.seconds >= 23 * 60 * 60 and diff.days >= 1):
                    # そのMemberをstart状態にして連続日数を初期化し、最終運動日時を更新する
                    memberSearch.status = "start"
                    memberSearch.days = 1
                    memberSearch.date = nowdate
    db.session.commit()
    return redirect(url_for("detail",id =teamid))

@app.route('/comment', methods=["post"])
def addcomment():
    teamid = int(request.form["teamid"])
    # 現在時刻の取得
    nowdate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    # 秒の小数点以下切り捨て
    dt = nowdate.replace(microsecond = 0)
    # formで入力された名前(name)を受け取る
    name = request.form["name"]
    # formで入力されたコメント(comment)を受け取る
    comment = request.form["comment"]
    # 新しくコメントを追加
    newComment = Comment(name=name, date=dt, comment=comment, teamid=teamid)
    db.session.add(newComment)
    db.session.commit()
    return redirect(url_for("detail", id =teamid))

@app.route('/profile/<int:id>')
def profile(id):
    member_data = Member.query.get(id)
    return render_template('profile.html', member = member_data)

## おまじない
if __name__ == "__main__":
    app.run()
