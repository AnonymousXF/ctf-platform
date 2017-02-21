# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, redirect, url_for, request, g, flash, jsonify
from flask_paginate import Pagination,get_page_args
app = Flask(__name__)

from database import User, Team, TeamMember, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, ScoreAdjustment, TroubleTicket, TicketComment, Notification, NewsItem, db
from datetime import datetime
from peewee import fn

from utils import user, decorators, flag, cache, misc, sendemail,dynamics
import utils.scoreboard

import config
import utils
import redis
import requests
import socket

app.secret_key = config.secret.key

import logging
logging.basicConfig(level=logging.WARNING)

@app.before_request
def make_info_available():
    if "user_id" in session:
        g.user = User.get(User.id == session["user_id"])
    if "team_id" in session:
        g.team = Team.get(Team.id == session["team_id"])
        g.team_restricts = g.team.restricts.split(",")

@app.context_processor     #环境处理器,相当于定义全局变量
def scoreboard_variables():
    var = dict(config=config)
    var["user_teamed"] = False     #user_teamed用户属于某个队伍
    var["user_requested"] = False   #user_requested用户申请加入某个队伍
    var["team_requested"] = False   #team_requested用户申请创建某个队伍
    if "user_id" in session:
        var["logged_in"] = True
        var["user"] = g.user
        try:
            if (TeamMember.get(TeamMember.member == g.user.id).member_confirmed):
                var["user_teamed"] = True
        except:
            var["user_teamed"] = False
        try:
            if (not TeamMember.get(TeamMember.member == g.user.id).member_confirmed):
                var["user_requested"] = True
        except:
            var["user_requested"] = False
        try:
            if (not Team.get(Team.team_leader == g.user.id).team_confirmed):
                var["team_requested"] = True
        except:
            var["team_requested"] = False
    else:
        var["logged_in"] = False
        var["notifications"] = []

    if "team_id" in session:
        g.team = Team.get(Team.id == session["team_id"])
        var["team"] = g.team
        if (g.user.id == g.team.team_leader.id):
            var["user_leader"] = True        #用户是队长
        else:
            var["user_leader"] = False
        var["notifications"] = Notification.select().where(Notification.team == g.team)
    else:
        var["notifications"] = []
    return var

# Blueprints
import api, admin
app.register_blueprint(api.api)
app.register_blueprint(admin.admin)

# Publically accessible things

@app.route('/')
def root():
    return redirect(url_for('scoreboard'))

# @app.route('/chat/')
# def chat():
#     return render_template("chat.html")

@app.route('/scoreboard/')
def scoreboard():
    data = cache.get_complex("scoreboard")
    graphdata = cache.get_complex("graph")
    if data is None or graphdata is None:
        if config.immediate_scoreboard:
            data = utils.scoreboard.calculate_scores()
            graphdata = utils.scoreboard.calculate_graph(data)
            utils.cache.set_complex("scoreboard", data, config.interval)
            utils.cache.set_complex("graph", graphdata, config.interval)
        else:
            return "No scoreboard data available. Please contact an organizer."

    return render_template("scoreboard.html", data=data, graphdata=graphdata)

@app.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form["user_name"]
        password = request.form["user_pwd"]
        try:
            user = User.get(User.username == username)
            result = utils.user.verify_password(user, password)
            if result:
                session["user_id"] = user.id
                try:
                    teammember = TeamMember.get(TeamMember.member == user.id)
                    session["team_id"] = teammember.team.id
                except TeamMember.DoesNotExist:
                    pass
                flash("Login successful.")
                return redirect(url_for('team_dashboard'))
            else:
                flash("Wrong pwd!")
                return render_template("login.html")
        except User.DoesNotExist:
            flash("Not exist!")
            return render_template("login.html")

@app.route('/forget_pwd/', methods=["GET", "POST"])
def forget_pwd():
    if request.method == "GET":
        return render_template("forget_pwd.html")
    else:
        user_name =request.form['user_name']
        try:
            user = User.get(User.username==user_name)
            if user.email_confirmed:
                confirmation_key = misc.generate_confirmation_key()
                #sendemail.send_confirmation_email(user.email, confirmation_key)
                user.email_confirmation_key = confirmation_key
                user.save()
                flash("The confirmed code has been send to your email")
                return render_template("forget_pwd.html")
            else:
                flash("Your email has not confirmed,you can input the confirmed code in your email")
                return render_template("forget_pwd.html")
        except User.DoesNotExist:
            flash("Not exist!")
            return render_template("forget_pwd.html")

@app.route('/confirm_code/', methods=["POST"])
def confirm_code():
    if request.method == "POST":
        user_name = request.form['user_name1']
        confirm_code = request.form['confirm_code']
        try:
            user = User.get(User.username==user_name)
            if user.email_confirmation_key==confirm_code:
                flash("correct!")
                session['user_id'] = user.id
                g.user = user
                return render_template("reset_pwd.html")
            else:
                flash("wrong!")
                return render_template("forget_pwd.html")
        except User.DoesNotExist:
            flash("Not exist!")
            return render_template("forget_pwd.html")

@app.route('/reset_pwd/',methods=["POST"])
@decorators.login_required
def reset_pwd():
    if request.method == "POST":
        user_pwd = request.form["user_pwd"].strip()
        pwd_confirmed = request.form["pwd_confirmed"].strip()
        user = User.get(User.username==g.user.username)
        if not user_pwd ==pwd_confirmed:
            flash("Entered passwords differs")
            return render_template("reset_pwd.html")
        if not utils.user.check_Password(user_pwd):
            flash("wrong pwd format.")
            return render_template("reset_pwd.html")
        pwhash = utils.user.create_password(user_pwd.encode())
        g.user.password = pwhash
        g.user.save()
        flash("Success")
        session.pop("user_id")
        return redirect(url_for('login'))

@app.route('/register/', methods=["GET", "POST"])
def register():
    if not config.registration:
        if "admin" in session and session["admin"]:
            pass
        else:
            return "抱歉，现在暂时无法注册。有问题请联系hustctf@163.com"

    if request.method == "GET":
        return render_template("user_register.html")
    else:
        #error, message = captcha.verify_captcha()
        #if error:
            #flash(message)
            #return render_template("user_register.html")

        user_name = request.form["user_name"].strip()
        user_email = request.form["user_email"].strip()
        user_pwd = request.form["user_pwd"].strip()
        pwd_confirmed = request.form["pwd_confirmed"].strip()
        if user_pwd != pwd_confirmed:
            flash("Entered passwords differs")
            return render_template("user_register.html")

        elif not utils.user.check_Password(user_pwd):
            flash("wrong pwd format.")
            return render_template("user_register.html")
		

        try:
            if(User.get(User.username == user_name)):
			    flash("The name has been used!")
			    return render_template("user_register.html")		
        except User.DoesNotExist:		
				pass

        try:
            if(User.get(User.email == user_email)):
			    flash("The email has been used!")
			    return render_template("user_register.html")		
        except User.DoesNotExist:		
				pass
				
        if len(user_name) > 50 or not user_name:
            flash("wrong name format.")
            return render_template("user_register.html")

        if not (user_email and "." in user_email and "@" in user_email):
            flash("wrong email format.")
            return render_template("user_register.html")


        if not sendemail.is_valid_email(user_email):
            flash("You are lying")
            return render_template("user_register.html")
			
        confirmation_key = misc.generate_confirmation_key()
        pwhash = utils.user.create_password(user_pwd.encode())
		
        user = User.create(username=user_name, email=user_email, password=pwhash, 
                           email_confirmation_key=confirmation_key)

        sendemail.send_confirmation_email(user_email, confirmation_key)

        session["user_id"] = user.id
        flash("register successfully.")
        return redirect(url_for('team_dashboard'))

@app.route('/logout/')
def logout():
    session.pop("user_id")
    if "team_id" in session:
        session.pop("team_id")
    flash("You have successfully logged out.")
    return redirect(url_for('root'))

# Things that require a team

@app.route('/confirm_email/', methods=["POST"])
@decorators.login_required
def confirm_email():
    if request.form["confirmation_key"] == g.user.email_confirmation_key:
        flash("confirmed!")
        g.user.email_confirmed = True
        g.user.save()
    else:
        flash("wrong.")
    return redirect(url_for('dashboard'))

@app.route('/team_register/', methods=["GET","POST"])
@decorators.login_required
@decorators.confirmed_email_required
def team_register():
    if request.method == "GET":
        return redirect(url_for('team_dashboard'))
    else:
        team_name = request.form["team_name"].strip()
        team_elig = "team_eligibility" in request.form
        affiliation = request.form["affiliation"].strip()

        try:
            if (Team.get(Team.name == team_name)):
                flash("The team name has been used.")
                return redirect(url_for('team_dashboard'))
        except Team.DoesNotExist:
            pass

        if len(team_name) > 50 or not team_name:
            flash("wrong team name format!")
            return redirect(url_for('team_dashboard'))
        if not affiliation or len(affiliation) > 100:
            affiliation = "No affiliation"
        team_leader = User.get(User.id == g.user.id)
        team = Team.create(name=team_name, eligible=team_elig, affiliation=affiliation, team_leader=team_leader)
        TeamMember.create(team=team,member=team_leader,member_confirmed=False)
        if not config.debug:
            TeamAccess.create(team=team, ip=misc.get_ip(), time=datetime.now())
        session["team_id"] = team.id
        flash("The request has send to admin.")
        return redirect(url_for('team_dashboard'))

@app.route('/team_modify/', methods=["POST"])
@decorators.login_required
@decorators.confirmed_email_required
def team_modify():
    if request.method == "POST":
        team_name = request.form["team_name"].strip()
        team_elig = "team_eligibility" in request.form
        affiliation = request.form["affiliation"].strip()
        name_changed = (team_name!=g.team.name)
        affi_changed = (affiliation!=g.team.affiliation)
        elig_changed = (team_elig!=g.team.eligible)
        if not name_changed and not affi_changed and not elig_changed:
            flash("nothig changed!")
            return redirect(url_for('team_dashboard'))
        if name_changed:
            try:
                if (Team.get(Team.name == team_name)):
                    flash("The team name has been used.")
                    return redirect(url_for('team_dashboard'))
            except Team.DoesNotExist:
                pass

            if len(team_name) > 50 or not team_name:
                flash("wrong team name format!")
                return redirect(url_for('team_dashboard'))

        if affi_changed:
            if not affiliation or len(affiliation) > 100:
                affiliation = "No affiliation"

        g.team.name = team_name
        g.team.affiliation = affiliation
        g.team.eligible = team_elig
        g.team.save()
        flash("change successfully.")
        return redirect(url_for('team_dashboard'))

@app.route('/team_join/', methods=["POST"])
@decorators.login_required
@decorators.confirmed_email_required
def team_join():
    if request.method == "POST":
        team_name = request.form["team_name"].strip()
        try:
            team=Team.get(Team.name == team_name)
            if not team.team_confirmed:
                flash("The team has not be agreed by admin.Please wait,or join another team!")
                return redirect(url_for('team_dashboard'))
            else:
                TeamMember.create(team=team.id, member=g.user.id)
                flash("The request has sent to leader!")
                return redirect(url_for('team_dashboard'))
        except Team.DoesNotExist:
            flash("team name don not exist!")
            return redirect(url_for('team_dashboard'))

@app.route('/user_add/', methods=["POST"])   #审核加入队伍请求
@decorators.login_required
@decorators.confirmed_email_required
def user_add():
    if request.method == "POST":
        users = TeamMember.select().where(TeamMember.team == g.team)
        # count the number of team_member
        number = 0
        for i in users:
            if i.member_confirmed == True:
                number = number+1
        for i in users:
            agree = 'a'+str(i.member.id)
            reject = 'a'+str(i.member.id)+'a'
            if agree in request.form and reject in request.form:
                flash("You can only choose one!")
                return redirect(url_for('team_dashboard'))
            if agree in request.form:
                if number < config.team_members:
                    number = number+1
                    i.member_confirmed = True
                    i.save()
                    flash("agree")
                else:
                    flash("The count of member must be less of 5")
            if reject in request.form:
                TeamMember.delete().where(TeamMember.member==i.member).execute()
                flash("reject")
        return redirect(url_for('team_dashboard'))

@app.route('/user/', methods=["GET", "POST"])
@decorators.login_required
def dashboard():
    if request.method == "GET":
        return render_template("dashboard.html")

    else:
        if g.redis.get("ul{}".format(session["user_id"])):
            flash("too fast!")
            return redirect(url_for('dashboard'))

        user_name = request.form["user_name"].strip()
        user_email = request.form["user_email"].strip()
        email_changed = (user_email != g.user.email)
        name_changed = (user_name != g.user.username)
        if not email_changed and not name_changed:
            flash("nothing changed!")
            return redirect(url_for('dashboard'))
        if name_changed:
            try:
                if (User.get(User.username == user_name)):
                    flash("The name has been used!")
                    return redirect(url_for('dashboard'))
            except User.DoesNotExist:
                pass

            if len(user_name) > 50 or not user_name:
                flash("wrong name format.")
                return redirect(url_for('dashboard'))
        g.user.username = user_name
        g.user.email = user_email

        g.redis.set("ul{}".format(session["user_id"]), str(datetime.now()), config.interval)

        if email_changed:
            if not sendemail.is_valid_email(user_email):
                flash("You are lying")
                return redirect(url_for('dashboard'))
            if not (user_email and "." in user_email and "@" in user_email):
                flash("wrong email format.")
                return redirect(url_for('dashboard'))
            try:
                if (User.get(User.email == user_email)):
                    flash("The email has been used!")
                    return redirect(url_for('dashboard'))
            except User.DoesNotExist:
                pass

            g.user.email_confirmation_key = misc.generate_confirmation_key()
            g.user.email_confirmed = False

            sendemail.send_confirmation_email(user_email, g.user.email_confirmation_key)
            flash("please confirme email")
        else:
            flash("save change.")
        g.user.save()
        return redirect(url_for('dashboard'))

@app.route('/team/', methods=["GET", "POST"])
@decorators.login_required
def team_dashboard():
    if request.method == "GET":
        if "team_id" in session:
            team_solves = ChallengeSolve.select(ChallengeSolve, Challenge).join(Challenge).where(
            ChallengeSolve.team == g.team)
            team_adjustments = ScoreAdjustment.select().where(ScoreAdjustment.team == g.team)
            team_score = sum([i.challenge.points for i in team_solves] + [i.value for i in team_adjustments])
            first_login = False
            if g.team.first_login:
                first_login = True
                g.team.first_login = False
                g.team.save()
            if g.team.team_leader.id == g.user.id:
                team_members = User.select().join(TeamMember).join(Team).where(Team.id == g.team.id)
                users = TeamMember.select().where(TeamMember.team == g.team)
                return render_template("team_dashboard.html", team_solves=team_solves, team_adjustments=team_adjustments,
        team_score=team_score, first_login=first_login, team_members=team_members, users=users)
            else:
                return render_template("team_dashboard.html", team_solves=team_solves, team_adjustments=team_adjustments,
        team_score=team_score, first_login=first_login)
        else:
            return render_template("team_dashboard.html")

@app.route('/teamconfirm/', methods=["POST"])
def teamconfirm():
    if utils.misc.get_ip() in config.confirm_ip:
        team_name = request.form["team_name"].strip()
        team_key = request.form["team_key"].strip()
        try:
            team = Team.get(Team.name == team_name)
        except Team.DoesNotExist:
            return "invalid", 403
        if team.key == team_key:
            return "ok", 200
        else:
            return "invalid", 403
    else:
        return "unauthorized", 401

@app.route('/dynamic_display/')
@decorators.competition_running_required
@decorators.confirmed_email_required
def dynamic_display():
    chal_failed = ChallengeFailure.select()
    chal_solved = ChallengeSolve.select()
    submits = dynamics.sort(chal_failed,chal_solved)
    results = dynamics.handle_solving(submits)

    result = []
    page,per_page,offset=get_page_args()
    if int(page) == int(len(results)/per_page) + 1:
        for i in range((page-1)*per_page, len(results)):
            if results[i] is not None:
                result.append(results[i])
    else:
        for i in range((page-1)*per_page, page*per_page):
            if results[i] is not None:
                result.append(results[i])
    pagination = Pagination(page=page,total=len(results),per_page=per_page,record_name='result')

    notices = NewsItem.select().order_by(-NewsItem.time)
    return render_template("dynamics.html", notices=notices, result=result, pagination=pagination)

@app.route('/challenges/')
@decorators.must_be_allowed_to("view challenges")
@decorators.competition_running_required
@decorators.confirmed_email_required
def challenges():
    chals = Challenge.select().order_by(Challenge.points, Challenge.name)
    solved = Challenge.select().join(ChallengeSolve).where(ChallengeSolve.team == g.team)
    solves = {i: int(g.redis.hget("solves", i).decode()) for i in [k.id for k in chals]}
    categories = sorted(list({chal.category for chal in chals}))
    return render_template("challenges.html", challenges=chals, solved=solved, categories=categories, solves=solves)

@app.route('/challenges/<int:challenge>/solves/')
@decorators.must_be_allowed_to("view challenge solves")
@decorators.must_be_allowed_to("view challenges")
@decorators.competition_running_required
@decorators.confirmed_email_required
def challenge_show_solves(challenge):
    chal = Challenge.get(Challenge.id == challenge)
    solves = ChallengeSolve.select(ChallengeSolve, Team).join(Team).order_by(ChallengeSolve.time).where(ChallengeSolve.challenge == chal)
    return render_template("challenge_solves.html", challenge=chal, solves=solves)

@app.route('/submit/<int:challenge>/', methods=["POST"])
@decorators.must_be_allowed_to("solve challenges")
@decorators.must_be_allowed_to("view challenges")
@decorators.competition_running_required
@decorators.confirmed_email_required
def submit(challenge):
    chal = Challenge.get(Challenge.id == challenge)
    flagval = request.form["flag"]

    code, message = flag.submit_flag(g.team, chal, flagval)
    flash(message)
    return redirect(url_for('challenges'))

# Trouble tickets

@app.route('/tickets/')
@decorators.must_be_allowed_to("view tickets")
@decorators.login_required
def team_tickets():
    return render_template("tickets.html", tickets=list(g.team.tickets))

@app.route('/tickets/new/', methods=["GET", "POST"])
@decorators.must_be_allowed_to("submit tickets")
@decorators.must_be_allowed_to("view tickets")
@decorators.login_required
def open_ticket():
    if request.method == "GET":
        return render_template("open_ticket.html")
    else:
        if g.redis.get("ticketl{}".format(session["team_id"])):
            return "You're doing that too fast."
        g.redis.set("ticketl{}".format(g.team.id), "1", 30)
        summary = request.form["summary"]
        description = request.form["description"]
        opened_at = datetime.now()
        ticket = TroubleTicket.create(team=g.team, summary=summary, description=description, opened_at=opened_at)
        flash("Ticket #{} opened.".format(ticket.id))
        return redirect(url_for("team_ticket_detail", ticket=ticket.id))

@app.route('/tickets/<int:ticket>/')
@decorators.must_be_allowed_to("view tickets")
@decorators.login_required
def team_ticket_detail(ticket):
    try:
        ticket = TroubleTicket.get(TroubleTicket.id == ticket)
    except TroubleTicket.DoesNotExist:
        flash("Could not find ticket #{}.".format(ticket))
        return redirect(url_for("team_tickets"))

    if ticket.team != g.team:
        flash("That is not your ticket.")
        return redirect(url_for("team_tickets"))

    comments = TicketComment.select().where(TicketComment.ticket == ticket).order_by(TicketComment.time)
    return render_template("ticket_detail.html", ticket=ticket, comments=comments)

@app.route('/tickets/<int:ticket>/comment/', methods=["POST"])
@decorators.must_be_allowed_to("comment on tickets")
@decorators.must_be_allowed_to("view tickets")
def team_ticket_comment(ticket):
    if g.redis.get("ticketl{}".format(session["team_id"])):
        return "You are doing that too fast."
    g.redis.set("ticketl{}".format(g.team.id), "1", 30)
    try:
        ticket = TroubleTicket.get(TroubleTicket.id == ticket)
    except TroubleTicket.DoesNotExist:
        flash("Could not find ticket #{}.".format(ticket))
        return redirect(url_for("team_tickets"))

    if ticket.team != g.team:
        flash("That is not your ticket.")
        return redirect(url_for("team_tickets"))

    if request.form["comment"]:
        TicketComment.create(ticket=ticket, comment_by=g.team.name, comment=request.form["comment"], time=datetime.now())
        flash("Comment added.")

    if ticket.active and "resolved" in request.form:
        ticket.active = False
        ticket.save()
        flash("Ticket closed.")

    elif not ticket.active and "resolved" not in request.form:
        ticket.active = True
        ticket.save()
        flash("Ticket re-opened.")

    return redirect(url_for("team_ticket_detail", ticket=ticket.id))

# Debug
@app.route('/debug/')
def debug_app():
    return jsonify(hostname=socket.gethostname())

# Manage Peewee database sessions and Redis

@app.before_request
def before_request():
    db.connect()
    g.redis = redis.StrictRedis()

@app.teardown_request
def teardown_request(exc):
    db.close()
    g.redis.connection_pool.disconnect()

# CSRF things

@app.before_request
def csrf_protect():
    csrf_exempt = ['/teamconfirm/']

    if request.method == "POST":
        token = session.get('_csrf_token', None)
        if (not token or token != request.form["_csrf_token"]) and not request.path in csrf_exempt:
            return "非法的CSRF令牌！"

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = misc.generate_random_string(64)
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

if __name__ == '__main__':
    app.run(debug=True, port=8001)
