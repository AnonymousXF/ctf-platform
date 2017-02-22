# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_paginate import Pagination,get_page_args
from database import AdminUser, User, TeamMember, TeamAccess, Team, Challenge, ChallengeSolve, ChallengeFailure, ScoreAdjustment, TroubleTicket, TicketComment, Notification, NewsItem
import utils
import utils.admin
import utils.scoreboard
from utils.decorators import admin_required, csrf_check
from utils.notification import make_link
from datetime import datetime
from config import secret
import redis

admin = Blueprint("admin", "admin", url_prefix="/admin")

@admin.route("/")
def admin_root():
    if "admin" in session:
        return redirect(url_for(".admin_dashboard"))
    else:
        return redirect(url_for(".admin_login"))

@admin.route("/login/", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin/login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        if getattr(secret, "admin_username", False):
            if username == secret.admin_username and password == secret.admin_password:
                session["admin"] = username
                return redirect(url_for(".admin_dashboard"))
        else:
            try:
                user = AdminUser.get(AdminUser.username == username)
                result = utils.admin.verify_password(user, password)
                if result:
                    session["admin"] = user.username
                    return redirect(url_for(".admin_dashboard"))
            except AdminUser.DoesNotExist:
                pass
        flash("You have made a terrible mistake.")
        return render_template("admin/login.html")

@admin.route("/team_add/", methods=["POST"])   #审核创建队伍请求
@admin_required
def admin_team_add():
    team_notconfirmed = Team.select().where(Team.team_confirmed==False)
    for i in team_notconfirmed:
        agree = 'a'+str(i.id) 
        reject = 'a'+str(i.id)+'a'
        if agree in request.form and reject in request.form:
            flash("You can only choose one!")
            return redirect(url_for('.admin_dashboard'))
        elif agree in request.form:
            i.team_confirmed = True
            teammember = TeamMember.get(TeamMember.member==i.team_leader)
            teammember.member_confirmed = True
            teammember.save()
            i.save()   
            flash("agree")
        elif reject in request.form:
            TeamMember.delete().where(TeamMember.member==i.team_leader).execute()
            Team.delete().where(Team.id==i.id).execute()
            TeamAccess.delete().where(TeamAccess.team==i).execute()
            flash("reject")
    return redirect(url_for('.admin_dashboard'))

@admin.route("/dashboard/")
@admin_required
def admin_dashboard():
    team_confirmed = Team.select().where(Team.team_confirmed==True)
    team_notconfirmed = Team.select().where(Team.team_confirmed==False)
    team_notconfirmed_leader = User.select().join(Team).where(Team.team_confirmed==False)
    solves = ChallengeSolve.select(ChallengeSolve, Challenge).join(Challenge)
    adjustments = ScoreAdjustment.select()
    scoredata = utils.scoreboard.get_all_scores(team_confirmed, solves, adjustments)
    lastsolvedata = utils.scoreboard.get_last_solves(team_confirmed, solves)
    tickets = list(TroubleTicket.select().where(TroubleTicket.active == True))
    challenges = Challenge.select()
    return render_template("admin/dashboard.html", team_notconfirmed_leader=team_notconfirmed_leader, team_confirmed=team_confirmed, team_notconfirmed=team_notconfirmed,scoredata=scoredata, lastsolvedata=lastsolvedata, tickets=tickets, challenges=challenges)

@admin.route("/notice/", methods=["GET", "POST"])
@admin_required
def admin_notice():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        publish_time = datetime.now()
        notice = NewsItem.create(title=title, content=content, time=publish_time)
        flash("Publish Success!")
        return redirect(url_for("admin.admin_notice"))
    else:
        all_record_num = NewsItem.select().count()
        page, per_page, offset = get_page_args()
        per_page = 8
        notices = NewsItem.select().order_by(-NewsItem.time).paginate(page, per_page)
        pagination = Pagination(page=page, total=all_record_num, per_page=per_page, record_name='notices',
                                format_total=True, format_number=True)
        return render_template("admin/notice.html",notices=notices, pagination=pagination)

@admin.route("/tickets/")
@admin_required
def admin_tickets():
    tickets = list(TroubleTicket.select(TroubleTicket, Team).join(Team).order_by(TroubleTicket.id.desc()))
    return render_template("admin/tickets.html", tickets=tickets)

@admin.route("/tickets/<int:ticket>/")
@admin_required
def admin_ticket_detail(ticket):
    ticket = TroubleTicket.get(TroubleTicket.id == ticket)
    comments = list(TicketComment.select().where(TicketComment.ticket == ticket).order_by(TicketComment.time))
    return render_template("admin/ticket_detail.html", ticket=ticket, comments=comments)

@admin.route("/tickets/<int:ticket>/comment/", methods=["POST"])
@admin_required
def admin_ticket_comment(ticket):
    ticket = TroubleTicket.get(TroubleTicket.id == ticket)
    if request.form["comment"]:
        TicketComment.create(ticket=ticket, comment_by=session["admin"], comment=request.form["comment"], time=datetime.now())
        Notification.create(team=ticket.team, notification="A response has been added for {}.".format(make_link("ticket #{}".format(ticket.id), url_for("team_ticket_detail", ticket=ticket.id))))
        flash("Comment added.")

    if ticket.active and "resolved" in request.form:
        ticket.active = False
        ticket.save()
        Notification.create(team=ticket.team, notification="{} has been marked resolved.".format(make_link("Ticket #{}".format(ticket.id), url_for("team_ticket_detail", ticket=ticket.id))))
        flash("Ticket closed.")

    elif not ticket.active and "resolved" not in request.form:
        ticket.active = True
        ticket.save()
        Notification.create(team=ticket.team, notification="{} has been reopened.".format(make_link("Ticket #{}".format(ticket.id), url_for("team_ticket_detail", ticket=ticket.id))))
        flash("Ticket reopened.")

    return redirect(url_for(".admin_ticket_detail", ticket=ticket.id))

@admin.route("/challenge/<int:tid>", methods=["GET", "POST"])
@admin_required
def admin_edit_challenge(tid):
    if request.method == "GET":
        challenge = Challenge.get(Challenge.id == tid)
        return render_template("admin/challenge.html", challenge=challenge)
    else:
        challenge = Challenge.get(Challenge.id == tid)
        challenge.name = request.form["challenge_name"].strip()
        challenge.category = request.form["challenge_category"].strip()
        challenge.author = request.form["challenge_author"].strip()
        challenge.description = request.form["challenge_des"].strip()
        challenge.points = int(request.form["challenge_points"])
        challenge.flag = request.form["challenge_flag"].strip()
        challenge.enabled = "challenge_enabled" in request.form
        challenge.save()
        r = redis.StrictRedis()
        for chal in Challenge.select():
            r.hset("solves", chal.id, chal.solves.count())
        flash("change successfully.")
        return redirect(url_for('.admin_dashboard'))

@admin.route("/challenge/add/", methods=["GET", "POST"])
@admin_required
def admin_add_challenge():
    if request.method == "GET":
        return render_template("admin/challenge_add.html")
    else:
        challenge_name = request.form["challenge_name"].strip()
        challenge_category = request.form["challenge_category"].strip()
        challenge_author = request.form["challenge_author"].strip()
        challenge_des = request.form["challenge_des"].strip()
        challenge_points = int(request.form["challenge_points"])
        challenge_flag = request.form["challenge_flag"].strip()
        if "challenge_enabled" in request.form:
            challenge_enabled = True
        else:
            challenge_enabled = False
        Challenge.create(name=challenge_name,category=challenge_category,author=challenge_author,description=challenge_des
            ,points=challenge_points,flag=challenge_flag,enabled=challenge_enabled)
        r = redis.StrictRedis()
        for chal in Challenge.select():
            r.hset("solves", chal.id, chal.solves.count())
        flash("create successfully.")
        return redirect(url_for('.admin_dashboard'))

@admin.route("/team/<int:tid>/")
@admin_required
def admin_show_team(tid):
    team = Team.get(Team.id == tid)
    return render_template("admin/team.html", team=team)

@admin.route("/team/<int:tid>/<csrf>/toggle_eligibility/")
@csrf_check
@admin_required
def admin_toggle_eligibility(tid):
    team = Team.get(Team.id == tid)
    team.eligible = not team.eligible
    team.save()
    flash("Eligibility set to {}".format(team.eligible))
    return redirect(url_for(".admin_show_team", tid=tid))

@admin.route("/team/<int:tid>/<csrf>/toggle_eligibility_lock/")
@csrf_check
@admin_required
def admin_toggle_eligibility_lock(tid):
    team = Team.get(Team.id == tid)
    team.eligibility_locked = not team.eligibility_locked
    team.save()
    flash("Eligibility lock set to {}".format(team.eligibility_locked))
    return redirect(url_for(".admin_show_team", tid=tid))

@admin.route("/team/<int:tid>/adjust_score/", methods=["POST"])
@admin_required
def admin_score_adjust(tid):
    value = int(request.form["value"])
    reason = request.form["reason"]
    team = Team.get(Team.id == tid)
    ScoreAdjustment.create(team=team, value=value, reason=reason)
    flash("Score adjusted.")
    return redirect(url_for(".admin_show_team", tid=tid))

@admin.route("/logout/")
def admin_logout():
    del session["admin"]
    return redirect(url_for('.admin_login'))
