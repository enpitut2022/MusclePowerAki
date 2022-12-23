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
    status = db.Column(db.String(10), default="finish")
    days = db.Column(db.Integer, default=1)
    max_days = db.Column(db.Integer, default=1)
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
    return render_template('index.html')

@app.route('/name_submit', methods=['post'])
def name_submit():
    username = request.form['name']
    memberSearch = Member.query.filter_by(name = username).first()
    if (memberSearch == None):
        teamdata = Team.query.all()
        return render_template('team.html', td = teamdata, username = username)
    else:
        teamid = memberSearch.teamid
        # 現在時刻の取得
        nowdate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        ## デバッグ用(1日経過させる)
        ## nowdate = datetime.datetime.utcnow() + datetime.timedelta(hours=9) + datetime.timedelta(days = 1)
        # 分以下を補正
        nowdate_rep = nowdate.replace(minute=0, second=0, microsecond=0)
        # 基準となる時刻
        teamsearch = Team.query.filter_by(id = teamid).first()
        baseDate = teamsearch.date
        # 基準となる時刻との差分を取る
        diff_rep = nowdate_rep - baseDate
        # 差分が23時間だった場合
        if diff_rep.seconds == 23 * 60 * 60:
            # 1時間加える
            nowdate_rep = nowdate_rep + datetime.timedelta(hours = 1)
        
        # その名前のメンバーのステータスがfinish(startでない)とき
        if memberSearch.status == "finish":
            # その名前のメンバーの最終運動日時を取得
            lastdate = memberSearch.date
            # 現在時刻と最終運動日時を比較
            diff_nl = nowdate_rep - lastdate
            # 1日と1時間(25時間以内)もしくは0日と23時間の範囲にdiffが収まったとき
            # すなわち、最後に運動した日の翌日に運動するとき
            if (diff_nl.seconds < 60 * 60 and diff_nl.days == 1) or (diff_nl.seconds >= 23 * 60 * 60 and diff_nl.days == 0):
                # そのMemberをstart状態にして連続日数を1追加し、最終運動日時を更新する
                memberSearch.status = "start"
                memberSearch.days += 1
                memberSearch.date = nowdate_rep
                # 最大継続日数の更新
                if (memberSearch.days > memberSearch.max_days):
                    memberSearch.max_days = memberSearch.days
            # diffの範囲が設定された時間の前後1時間に収まり、かつ最後に運動した日から2日以上経過しているとき
            elif (diff_nl.seconds <= 60 * 60 and diff_nl.days >= 2) or (diff_nl.seconds >= 23 * 60 * 60 and diff_nl.days >= 1):
                # そのMemberをstart状態にして連続日数を初期化し、最終運動日時を更新する
                memberSearch.status = "start"
                memberSearch.days = 1
                memberSearch.date = nowdate_rep
                
        db.session.commit()
        return redirect(url_for("detail",id =teamid))

@app.route('/teamchoice', methods=['post'])
def teamchoice():
    username = request.form['username']
    # ここでusernameと一致するメンバーをもう一度検索しないと、Fumioが大量発生してしまう！
    memberSearch = Member.query.filter_by(name = username).first()
    if memberSearch == None:
        teamid = int(request.form['teamid'])
        teamsearch = Team.query.get(teamid)
        baseDate = teamsearch.date
        newMember = Member(name=username, date=baseDate, teamid=teamid)
        db.session.add(newMember)
        db.session.commit()
    member_data = Member.query.filter_by(name=username).first()
    team_data = Team.query.get(member_data.teamid)
    return render_template('team_decide.html', un=username, td=team_data)

@app.route('/detail/<int:id>')
def detail(id):
    teamdata = Team.query.get(id)
    # start状態のメンバー全員を取得
    members = Member.query.filter_by(teamid = id).filter_by(status = "start").order_by(Member.date).all()
    # start状態のメンバー数をカウント
    membersNumber = len(members)
    # 状態関係なくメンバー全員を取得
    allmember = Member.query.filter_by(teamid = id).order_by(Member.days.desc()).all()
    # 現在時刻の取得
    nowdate = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).date()
    nowdate_str = nowdate.strftime('%Y-%m-%d')
    # 新着コメントを取得
    comments = Comment.query.filter_by(teamid = id).filter(Comment.date.contains(nowdate_str)).order_by(Comment.id.desc()).all()
    # index.htmlに値を渡し、表示
    return render_template('detail.html',td = teamdata, ms = members, mn = membersNumber, am = allmember, cm = comments)

@app.route('/workstart', methods=["post"])
def workstart():
    teamid = int(request.form["teamid"])
    # 現在時刻の取得
    nowdate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    ## デバッグ用(1日経過させる)
    ## nowdate = datetime.datetime.utcnow() + datetime.timedelta(hours=9) + datetime.timedelta(days = 1)
    # 分以下を補正
    nowdate_rep = nowdate.replace(minute=0, second=0, microsecond=0)
    # 基準となる時刻
    teamsearch = Team.query.filter_by(id = teamid).first()
    baseDate = teamsearch.date
    # 基準となる時刻との差分を取る
    diff_rep = nowdate_rep - baseDate
    # 差分が23時間だった場合
    if diff_rep.seconds == 23 * 60 * 60:
        # 1時間加える
        nowdate_rep = nowdate_rep + datetime.timedelta(hours = 1)
    # formで入力された名前(name)を受け取る
    name = request.form["name"]
    # 入力された名前をDBから検索
    memberSearch = Member.query.filter_by(name = name).first()
    # DBに名前がなかった場合
    if memberSearch == None:
        # 基準となる時刻と現在時刻の差を取る(絶対値)
        diff_dn = abs(baseDate - nowdate)
        # その差の秒数
        diff_dn_sec = diff_dn.seconds
        # 秒数が1時間未満または23時間以上なら設定された日時の前後1時間以内とみなす
        if diff_dn_sec < 60 * 60 or diff_dn_sec >= 23 * 60 * 60:
            # 新しくメンバーを追加
            newMember = Member(name=name, date=nowdate_rep, teamid=teamid)
            db.session.add(newMember)
    # DBに名前があった場合
    else:
        if memberSearch.teamid == teamid:
        # その名前のメンバーのステータスがfinish(startでない)とき
            if memberSearch.status == "finish":
                # その名前のメンバーの最終運動日時を取得
                lastdate = memberSearch.date
                # 現在時刻と最終運動日時を比較
                diff_nl = nowdate_rep - lastdate
                # 1日と1時間(25時間以内)もしくは0日と23時間の範囲にdiffが収まったとき
                # すなわち、最後に運動した日の翌日に運動するとき
                if (diff_nl.seconds < 60 * 60 and diff_nl.days == 1) or (diff_nl.seconds >= 23 * 60 * 60 and diff_nl.days == 0):
                    # そのMemberをstart状態にして連続日数を1追加し、最終運動日時を更新する
                    memberSearch.status = "start"
                    memberSearch.days += 1
                    memberSearch.date = nowdate_rep
                    # 最大継続日数の更新
                    if (memberSearch.days > memberSearch.max_days):
                        memberSearch.max_days = memberSearch.days
                # diffの範囲が設定された時間の前後1時間に収まり、かつ最後に運動した日から2日以上経過しているとき
                elif (diff_nl.seconds <= 60 * 60 and diff_nl.days >= 2) or (diff_nl.seconds >= 23 * 60 * 60 and diff_nl.days >= 1):
                    # そのMemberをstart状態にして連続日数を初期化し、最終運動日時を更新する
                    memberSearch.status = "start"
                    memberSearch.days = 1
                    memberSearch.date = nowdate_rep
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
    if (request.form["comment"] != ""):
        comment = request.form["comment"]
        # 新しくコメントを追加
        newComment = Comment(name=name, date=dt, comment=comment, teamid=teamid)
        db.session.add(newComment)
    db.session.commit()
    return redirect(url_for("detail", id =teamid))

@app.route('/profile/<int:id>')
def profile(id):
    # プロフィールの表示
    member_data = Member.query.get(id)
    return render_template('profile.html', member = member_data)

@app.route('/profile_edit', methods=["post"])
def profile_edit():
    id = request.form["user_id"]
    goal = request.form["goal"]
    training_detail = request.form["training_detail"]
    member_data = Member.query.get(id)
    # 目標に値が入力されていたら、更新する
    if (goal != ""):
        member_data.goal = goal
    # 運動内容に値が入力されていたら、更新する
    if (training_detail != ""):
        member_data.training_detail = training_detail
    db.session.commit()
    return redirect(url_for("profile", id =id))

@app.route('/allcomment/<int:id>')
def allcomment(id):
    teamdata = Team.query.get(id)
    comments = Comment.query.filter_by(teamid = id).order_by(Comment.id.desc()).all()
    return render_template('comment.html', td = teamdata, cm = comments)

@app.route('/comment_detail', methods=["post"])
def add_allcomment():
    teamid = int(request.form["teamid"])
    # 現在時刻の取得
    nowdate = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    # 秒の小数点以下切り捨て
    dt = nowdate.replace(microsecond = 0)
    # formで入力された名前(name)を受け取る
    name = request.form["name"]
    # formで入力されたコメント(comment)を受け取る
    if (request.form["comment"] != ""):
        comment = request.form["comment"]
        # 新しくコメントを追加
        newComment = Comment(name=name, date=dt, comment=comment, teamid=teamid)
        db.session.add(newComment)
    db.session.commit()
    return redirect(url_for("allcomment", id =teamid))

## おまじない
if __name__ == "__main__":
    app.run()

