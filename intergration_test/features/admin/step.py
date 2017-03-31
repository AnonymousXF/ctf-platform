# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("../")
import time
from lettuce import step, world, before, after
from nose.tools import assert_equals,assert_in
from app import app
from database import *
import utils
import re
import random
import redis

@before.all
def before_all():
    app.config['TESTING'] = True
    world.app = app.test_client()
    tables = [User, Team, TeamMember, UserAccess, Challenge, Vmachine, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
    [i.create_table() for i in tables]

@step("I visit admin system")
def visit_system(step):
	world.app.response = world.app.get('/admin',follow_redirects=True)

@step("I watch the vmachine")
def watch_vmachine(step):
	world.app.response = world.app.get('/admin/challenge/',follow_redirects=True)

@step("there is a admin in database with \"(.*)\",\"(.*)\"")
def admin_in_database(step,admin_name,admin_pwd):
	r = random.SystemRandom()
	secret = "".join([r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for i in range(16)])
	pwhash = utils.admin.create_password(admin_pwd.encode())
	AdminUser.create(username=admin_name, password=pwhash, secret=secret)

@step("I fill the register information with \"(.*)\",\"(.*)\",\"(.*)\",\"(.*)\"")
def register(step,user_name,user_email,user_pwd,pwd_confirmed):
	html = world.app.get('/register/',follow_redirects=True).data
	csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
	data = dict(user_name = user_name,
					user_email = user_email,
					user_pwd = user_pwd,
					pwd_confirmed = pwd_confirmed,
					_csrf_token = csrf_token)
	world.app.response = world.app.post('/register/',data = data, follow_redirects = True)

@step("there is a user in database with \"(.*)\",\"(.*)\",\"(.*)\"")
def user_in_database(step,user_name,user_email,user_pwd):
	pwhash = utils.admin.create_password(user_pwd.encode())
	User.create(username=user_name, password=pwhash, email=user_email, email_confirmation_key='12345678956565')

@step("there is a challenge in database with \"(.*)\",\"(.*)\",\"(.*)\",\"(.*)\",\"(.*)\",\"(.*)\"")
def challenge_in_database(step,name,category,description,points,flag,author):
	world.app.chal = Challenge.create(name="Challenge Test", category="Test", description="Test", points=100, flag="Test", author="Test")
	r = redis.StrictRedis()
	r.hset("solves", world.app.chal.id, world.app.chal.solves.count())

@step("I confirm my email")
def confirm_email(step):
	confirmation_key = User.get(User.username == world.app.name).email_confirmation_key
	data = dict(confirmation_key = confirmation_key, _csrf_token = world.app.csrf_token)
	world.app.response = world.app.post('/confirm_email/',data = data, follow_redirects=True)

@step("I register a team with \"(.*)\",\"(.*)\",\"(.*)\"")
def register_team(step,team_name,affiliation,elig):
	if elig == "True":
		elig = True
	else:
		elig = False
	data = dict(team_name = team_name,
					affiliation = affiliation,
					team_eligibility = elig,
					_csrf_token = world.app.csrf_token)
	world.app.response = world.app.post('/team_register/',data = data, follow_redirects = True)

@step("I login with \"(.*)\",\"(.*)\"")
def login(step,user_name, user_pwd):
	html = world.app.get('/login/',follow_redirects=True).data
	world.app.csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
	data = dict(user_name = user_name, user_pwd = user_pwd, _csrf_token = world.app.csrf_token)
	world.app.name = user_name
	world.app.response = world.app.post('/login/',data = data,follow_redirects=True)

@step("I login admin with \"(.*)\",\"(.*)\"")
def admin_login(step,admin_name,admin_pwd):
	world.app.name = admin_name
	html = world.app.get('/admin/login/',follow_redirects=True).data
	world.app.csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
	data = dict(username = admin_name, password = admin_pwd, _csrf_token = world.app.csrf_token)
	world.app.response = world.app.post('/admin/login/',data = data,follow_redirects=True)

@step("I agree a team with \"(.*)\"")
def agree_team(step,team_name):
	team = Team.get(Team.name == team_name)
	if str(team.id) == "1":
		data = dict(a1='checked', _csrf_token=world.app.csrf_token)
	else:
		data = dict(a2='checked', _csrf_token=world.app.csrf_token)
	world.app.response = world.app.post('/admin/team_add/', data=data, follow_redirects = True)

@step("I reject a team with \"(.*)\"")
def agree_team(step,team_name):
	team = Team.get(Team.name == team_name)
	if str(team.id) == "1":
		data = dict(a1a='checked', _csrf_token=world.app.csrf_token)
	else:
		data = dict(a2a='checked', _csrf_token=world.app.csrf_token)
	world.app.response = world.app.post('/admin/team_add/', data=data, follow_redirects = True)

@step("I agree and reject a team with \"(.*)\"")
def agree_reject_team(step,team_name):
	team = Team.get(Team.name == team_name)
	if str(team.id) == "1":
		data = dict(a1='checked', a1a='checked', _csrf_token=world.app.csrf_token)
	else:
		data = dict(a2='checked', a2a='checked',_csrf_token=world.app.csrf_token)
	world.app.response = world.app.post('/admin/team_add/', data=data, follow_redirects = True)

@step("I watch a team with \"(.*)\"")
def watch_team(step,team_name):
	team = Team.get(Team.name == team_name)
	world.app.response = world.app.get('/admin/team/'+str(team.id)+'/', follow_redirects = True)

@step("I set toggle_eligibility of a team with \"(.*)\"")
def watch_team(step,team_name):
	team = Team.get(Team.name == team_name)
	world.app.response = world.app.get('/admin/team/'+str(team.id)+'/'+world.app.csrf_token+'/toggle_eligibility/', follow_redirects = True)

@step("I set toggle_eligibility_lock of a team with \"(.*)\"")
def watch_team(step,team_name):
	team = Team.get(Team.name == team_name)
	world.app.response = world.app.get('/admin/team/'+str(team.id)+'/'+world.app.csrf_token+'/toggle_eligibility_lock/', follow_redirects = True)

@step("I adjust_score of a team with \"(.*)\" to \"(.*)\",\"(.*)\"")
def watch_team(step,team_name,value,reason):
	team = Team.get(Team.name == team_name)
	data = dict(value = value, reason = reason, _csrf_token = world.app.csrf_token)
	world.app.response = world.app.post('/admin/team/'+str(team.id)+'/adjust_score/', data = data,follow_redirects = True)

@step("I close a challenge with id \"(.*)\"")
def close_challenge(step,id):
	world.app.response = world.app.get('/admin/challenge/'+str(id)+'/'+world.app.csrf_token+'/enable_challenge/', follow_redirects = True)

@step("I create a ticket with \"(.*)\",\"(.*)\"")
def create_ticket(step,summary,description):
	time.sleep(30)
	data = dict(summary=summary,description=description, _csrf_token=world.app.csrf_token)
	world.app.response = world.app.post('/tickets/new/', data=data, follow_redirects=True)

@step("I watch a ticket with id \"(.*)\"")
def watch_ticket(step,id):
	world.app.response = world.app.get('/admin/tickets/'+str(id)+'/', follow_redirects = True)

@step("I comment a ticket with id \"(.*)\" with \"(.*)\"")
def comment_ticket(step,id,comment):
	data=dict(comment=comment,_csrf_token=world.app.csrf_token)
	world.app.response = world.app.post('/admin/tickets/'+id+'/comment/',data=data,follow_redirects=True)

@step("I close a ticket with id \"(.*)\"")
def close_ticket(step,id):
	data=dict(comment="test",_csrf_token=world.app.csrf_token,resolved='on')
	world.app.response = world.app.post('/admin/tickets/'+id+'/comment/',data=data,follow_redirects=True)

@step("I connect with \"(.*)\",\"(.*)\"")
def connect(step,url,xml):
	data=dict(url=url,xml=xml,_csrf_token = world.app.csrf_token)
	world.app.response = world.app.post('/admin/geturl/', data=data, follow_redirects=True)

@step("I modify a vmachine with id \"(.*)\" with \"(.*)\",\"(.*)\",\"(.*)\"")
def modify_vmachine(step,Vname,memory,cpu,status):
	vmachine = Vmachine.get(Vmachine.name==Vname)
	data=dict(vmachine_memory=memory,vmachine_cpu=cpu,vmachine_status =status,_csrf_token = world.app.csrf_token)
	world.app.response = world.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)

@step("I should see \"(.*)\"")
def should_see(step,str):
	assert_in(str, world.app.response.data)

@step("I admin logout")
def logout(step):
	world.app.response = world.app.get('/admin/logout/',follow_redirects = True)

@step("I logout")
def logout(step):
	world.app.response = world.app.get('/logout/',follow_redirects = True)

@after.all
def after_all(total):
	tables = [User, Team, TeamMember, UserAccess, Challenge, Vmachine, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
	[i.drop_table() for i in tables]