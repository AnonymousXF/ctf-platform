# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_paginate import Pagination,get_page_args
from database import AdminUser, User, TeamMember, TeamAccess, Team, Challenge, Vmachine, ChallengeSolve, ChallengeFailure, ScoreAdjustment, TroubleTicket, TicketComment, Notification, NewsItem
import utils
import utils.admin
import utils.scoreboard
import utils.Vmanager
from utils.decorators import admin_required, csrf_check
from utils.notification import make_link
from datetime import datetime
from config import secret
import config
import redis
from flask import current_app

url = ""
xml = ""#"/etc/libvirt/qemu"
#xml=''
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
                current_app.logger.info(username+"(admin) logined")
                return redirect(url_for(".admin_dashboard"))
        else:
            try:
                user = AdminUser.get(AdminUser.username == username)
                result = utils.admin.verify_password(user, password)
                if result:
                    session["admin"] = user.username
                    current_app.logger.info(username+"(admin) logined")
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
            current_app.logger.info(session["admin"]+"agree team ,team_name is "+i.name)   
            flash("agree")
        elif reject in request.form:
            current_app.logger.info(session["admin"]+"reject team ,team_name is "+i.name)  
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
        current_app.logger.info(session["admin"]+"publish a notice ,notice_name is "+title)
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

@admin.route("/challenge/")
@admin_required
def admin_challenge():
    global url
    challenges = Challenge.select()
    if not url:
        conn = False
        return render_template("admin/challenge.html",challenges=challenges,conn=conn)
    else:
        conn = utils.Vmanager.createConnection(url)
        if not conn:
            url = ''
            current_app.logger.info(session["admin"]+" connect server failed.")
            flash("连接失败")
            return redirect(url_for(".admin_challenge"))
        else: 
            current_app.logger.info(session["admin"]+" connect server successful.")
            challenges = Challenge.select()
            vmachines = Vmachine.select()
            for vmachine in vmachines:
                if not utils.Vmanager.isexist(conn,vmachine.name):
                    Vmachine.delete().where(Vmachine.name==vmachine.name).execute()
                    continue
                memory,cpu,status = utils.Vmanager.getDomInfoByName(conn, vmachine.name)
                if status == "5":
                    status = "shutdown"
                elif status == "1":
                    status = "running"
                else:
                    status = "suspend"
                vmachine.memory = memory
                vmachine.cpu = cpu
                vmachine.status = status
                vmachine.save()
            vmachines = Vmachine.select()
            utils.Vmanager.closeConnection(conn)
            return render_template("admin/challenge.html",challenges=challenges,vmachines=vmachines,conn=conn)

@admin.route("/challenge/<int:tid>/<csrf>/enable_challenge/")
@csrf_check
@admin_required
def admin_enable_challenge(tid):
    challenge = Challenge.get(Challenge.id == tid)
    challenge.enabled = not challenge.enabled
    challenge.save()
    current_app.logger.info(session["admin"]+" set challenge "+challenge.name + "enabled set to {}".format(challenge.enabled))
    flash("Enabled set to {}".format(challenge.enabled))
    return redirect(url_for(".admin_challenge"))

@admin.route("/geturl/", methods=["POST"])
@admin_required
def admin_get_url():
    global url
    global xml
    url = request.form["url"]
    xml = request.form["xml"]
    return redirect(url_for(".admin_challenge"))

@admin.route("/vmachine/<int:tid>/", methods=["GET", "POST"])
@admin_required
def admin_edit_vmachine(tid):
    if request.method == "GET":
        vmachine = Vmachine.get(Vmachine.id == tid)
        if vmachine.status == "shutdown":
            run = False
            sus = False
            shut = True
        elif vmachine.status == "running":
            run = True
            sus = False
            shut = False
        else:
            run = False
            sus = True
            shut = False
        return render_template("admin/vmachine.html", vmachine=vmachine,running=run,suspend=sus,shutdown=shut)
    else:
        conn = utils.Vmanager.createConnection(url)
        vmachine = Vmachine.get(Vmachine.id == tid)
        memory = request.form["vmachine_memory"].strip()
        cpu = request.form["vmachine_cpu"].strip()
        status = request.values.get("vmachine_status")
        if not memory == str(vmachine.memory):
            if not memory.isdigit():
                flash("must be digital")
                return redirect(url_for('.admin_edit_vmachine' ,tid=vmachine.id))
            if not utils.Vmanager.modify_memory(conn,vmachine.name,int(memory)*1024,xml):
                flash("modify memory failed.")
        if not cpu == str(vmachine.cpu):
            if not cpu.isdigit():
                flash("must be digital")
                return redirect(url_for('.admin_edit_vmachine' ,tid=vmachine.id))
            if cpu < '1' or cpu > '4':
                flash("cpu should between 1 and 4") 
                return redirect(url_for('.admin_edit_vmachine' ,tid=vmachine.id))
            if not utils.Vmanager.modify_cpu(conn,vmachine.name,int(cpu),xml):
                flash("modify cpu failed.")
        if not status == vmachine.status:
            if status == "running":
                if vmachine.status == "shutdown":
                    utils.Vmanager.startDom(conn,vmachine.name,xml)
                else:
                    flash("error")
                    return redirect(url_for('.admin_edit_vmachine' ,tid=vmachine.id))
            if status == "suspend":
                if vmachine.status == "running":
                    utils.Vmanager.suspendDom(conn,vmachine.name)
                else:
                    flash("error")
                    return redirect(url_for('.admin_edit_vmachine' ,tid=vmachine.id))
            if status == "resume":
                if vmachine.status == "suspend":
                    utils.Vmanager.resumeDom(conn,vmachine.name)
                else:
                    flash("error")
                    return redirect(url_for('.admin_edit_vmachine' ,tid=vmachine.id))
            if status == "shutdown":
                if vmachine.status == "running":
                    utils.Vmanager.destroyDom(conn,vmachine.name)
                else:
                    flash("error")
                    return redirect(url_for('.admin_edit_vmachine' ,tid=vmachine.id))
        utils.Vmanager.closeConnection(conn)
        return redirect(url_for('.admin_challenge'))

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
        current_app.logger.info(session["admin"]+" comment ticket,ticket id is "+str(ticket))
        flash("Comment added.")

    if ticket.active and "resolved" in request.form:
        ticket.active = False
        ticket.save()
        Notification.create(team=ticket.team, notification="{} has been marked resolved.".format(make_link("Ticket #{}".format(ticket.id), url_for("team_ticket_detail", ticket=ticket.id))))
        current_app.logger.info(session["admin"]+" close ticket,ticket id is "+str(ticket))
        flash("Ticket closed.")

    elif not ticket.active and "resolved" not in request.form:
        ticket.active = True
        ticket.save()
        Notification.create(team=ticket.team, notification="{} has been reopened.".format(make_link("Ticket #{}".format(ticket.id), url_for("team_ticket_detail", ticket=ticket.id))))
        current_app.logger.info(session["admin"]+" reopene ticket,ticket id is "+str(ticket))
        flash("Ticket reopened.")

    return redirect(url_for(".admin_ticket_detail", ticket=ticket.id))

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
    current_app.logger.info(session["admin"]+" set team "+team.name + "Eligibility set to {}".format(team.eligible))
    flash("Eligibility set to {}".format(team.eligible))
    return redirect(url_for(".admin_show_team", tid=tid))

@admin.route("/team/<int:tid>/<csrf>/toggle_eligibility_lock/")
@csrf_check
@admin_required
def admin_toggle_eligibility_lock(tid):
    team = Team.get(Team.id == tid)
    team.eligibility_locked = not team.eligibility_locked
    team.save()
    current_app.logger.info(session["admin"]+" set team "+team.name + "Eligibility lock set to {}".format(team.eligibility_locked))
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
    current_app.logger.info(session["admin"]+" adjust score ,team name is "+team.name)
    return redirect(url_for(".admin_show_team", tid=tid))

@admin.route("/logout/")
def admin_logout():
    del session["admin"]
    return redirect(url_for('.admin_login'))
