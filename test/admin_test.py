# -*- coding: utf-8 -*-
import unittest
import os,sys
import peewee
import re
from datetime import datetime
import random

sys.path.append("../")
from modules import admin
from app import app
from database import *
import config
import utils.admin

Vname = 'FreeDOS'
config.debug=True
TEST_ADMIN_NAME = 'nana'
TEST_ADMIN_PASSWORD = 'nana'
r = random.SystemRandom()
secret = "".join([r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for i in range(16)])
pwhash = utils.admin.create_password(TEST_ADMIN_PASSWORD)

class FlaskrTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		tables = [User, Team, TeamMember, UserAccess, Challenge, Vmachine, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.create_table() for i in tables]

	def tearDown(self):
		tables = [User, Team, TeamMember, UserAccess, Challenge, Vmachine, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.drop_table() for i in tables]

	def login(self, username, password):
		#Get csrf_token
		html = self.app.get('/admin/login/',follow_redirects=True).data
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
		#Post data
		data = dict(username = username, password = password, _csrf_token = csrf_token)
		return self.app.post('/admin/login/',data = data,follow_redirects=True)
	
	def logout(self):
		return self.app.get('/admin/logout/',follow_redirects = True)

	def test_root(self):
		response = self.app.get('/admin/', content_type = 'html/text',follow_redirects=True)
		self.assertEqual(200, response.status_code)
		AdminUser.create(username=TEST_ADMIN_NAME, password=pwhash, secret=secret)
		rv = self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		self.assertIn(TEST_ADMIN_NAME, rv.data)
		rv = self.app.get('/admin/', content_type = 'html/text',follow_redirects=True)
		self.assertIn(TEST_ADMIN_NAME, rv.data)
		rv = self.logout()
		self.assertIn(b'登录',rv.data)

	def test_login_and_logout(self):
		# create admin
		AdminUser.create(username=TEST_ADMIN_NAME, password=pwhash, secret=secret)
		# correct data
		rv = self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		self.assertIn(TEST_ADMIN_NAME, rv.data)
		rv = self.logout()
		self.assertIn(b'登录',rv.data)
		#Wrong data
		rv = self.login('', '')
		self.assertIn(b'You have made a terrible mistake.', rv.data)
		rv = self.login(TEST_ADMIN_NAME+'111', TEST_ADMIN_PASSWORD+'111')
		self.assertIn(b'You have made a terrible mistake.', rv.data)
		# if admin_username in serects
		f = open("secrets",'a+')
		f.write("\nadmin_username: admin\nadmin_password: admin")
		f.close
		rv = self.login('admin', 'admin')
		self.assertIn('admin', rv.data)
		f = open("secrets",'w+')
		f.truncate()
		f.write("mailgun_url: https://api.mailgun.net/v3/sandboxeb3737e47fe647d49f550d2c2639dfcf.mailgun.org\n")
		f.write("mailgun_key: key-3c8c7ea77b5a2d71607c4b0bdcd656cc\n")
		f.write("recaptcha_key: asdlkfjhasdlkjfhlsdakjfh\n")
		f.write("recaptcha_secret: sdakjfhsdalkfjhsdalkfjh\n")
		f.write("key: nana")
		f.close

	def test_login_dashboard(self):
		# create admin
		AdminUser.create(username=TEST_ADMIN_NAME, password=pwhash, secret=secret)
		# not login
		rv = self.app.get('/admin/dashboard/',follow_redirects = True)
		self.assertIn('You must be an admin to access that page.', rv.data)
		# login
		rv = self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		self.assertIn(TEST_ADMIN_NAME, rv.data)
		rv = self.app.get('/admin/dashboard/',follow_redirects = True)
		self.assertIn('待审核队伍', rv.data)

	#test /team_add/
	def test_team_add(self):
		# register a team
		User.create(username='user', password=pwhash, email='357989@qq.com', email_confirmation_key='12345678956565', email_confirmed=True)
		html = self.app.get('/login/',follow_redirects=True).data
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
		data = dict(user_name = 'user', user_pwd = 'nana', _csrf_token = csrf_token)
		rv = self.app.post('/login/',data = data,follow_redirects=True)
		data = dict(team_name = 'test',
					affiliation = 'hust',
					team_eligibility = True,
					_csrf_token = csrf_token)
		rv = self.app.post('/team_register/',data = data, follow_redirects = True)
		self.assertIn(b'The request has send to admin.',rv.data)
		self.app.get('/logout/',follow_redirects = True)
		# only choose one
		AdminUser.create(username=TEST_ADMIN_NAME, password=pwhash, secret=secret)
		rv = self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		rv = self.app.post('/admin/team_add/', data=dict(a1='checked', a1a='checked', _csrf_token=csrf_token), follow_redirects = True)
		self.assertIn(b'You can only choose one!',rv.data)
		self.logout()
		# reject
		rv = self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		rv = self.app.post('/admin/team_add/', data=dict(a1a='checked', _csrf_token=csrf_token), follow_redirects = True)
		self.assertIn(b'reject',rv.data)
		self.logout()
		# agree
		html = self.app.get('/login/',follow_redirects=True).data
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',html)[0]
		data = dict(user_name = 'user', user_pwd = 'nana', _csrf_token = csrf_token)
		rv = self.app.post('/login/',data = data,follow_redirects=True)
		data = dict(team_name = 'test',
					affiliation = 'hust',
					team_eligibility = True,
					_csrf_token = csrf_token)
		rv = self.app.post('/team_register/',data = data, follow_redirects = True)
		self.assertIn(b'The request has send to admin.',rv.data)
		self.app.get('/logout/',follow_redirects = True)
		rv = self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		csrf_token = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		rv = self.app.post('/admin/team_add/', data=dict(a1='checked', _csrf_token=csrf_token), follow_redirects = True)
		self.assertIn(b'agree',rv.data)
		self.logout()

	def test_login_tickets(self):
		# create admin
		AdminUser.create(username=TEST_ADMIN_NAME, password=pwhash, secret=secret)
		# create a team
		User.create(username='nana', password=pwhash, email='56565@qq.com', email_confirmed=True, email_confirmation_key='12345678956565')
		user = User.get(User.username=='nana')
		team = Team.create(name='test1', affiliation='hust', eligible=True, team_leader=user)
		TeamMember.create(team=team, member=user, member_confirmed=True)
		# create a ticket
		opened_at = datetime.now()
		ticket = TroubleTicket.create(team=team, summary='test ticket', description='test test test', opened_at=opened_at)
		#not login
		rv = self.app.get('/admin/tickets/',follow_redirects = True)
		self.assertIn('You must be an admin to access that page.', rv.data)
		# login
		rv = self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		self.assertIn(TEST_ADMIN_NAME, rv.data)
		rv = self.app.get('/admin/tickets/',follow_redirects = True)
		self.assertIn('Trouble tickets', rv.data)
		# test /tickets/<int:ticket>/ and /tickets/<int:ticket>/comment/
		try:

			ticket = TroubleTicket.get(TroubleTicket.id=='1')
			if ticket:
				# test /tickets/<int:ticket>/
				rv = self.app.get('/admin/tickets/'+str(ticket.id)+'/', follow_redirects = True)
				self.assertIn('Ticket #1', rv.data)
				csrf = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
				#  test /tickets/<int:ticket>/comment/
				#  comment is null 
				comment = ''
				if ticket.active:
					#  ticket.active and "resolved" not in request.form
					rv = self.app.post('/admin/tickets/'+str(ticket.id)+'/comment/', data=dict(comment=comment, _csrf_token=csrf), follow_redirects = True)
					self.assertIn('Ticket #1', rv.data)
					self.assertNotIn('Comment added.', rv.data)
					self.assertNotIn('Ticket closed.', rv.data)
					self.assertNotIn('Ticket reopened.', rv.data)
					# ticket.active and "resolved" in request.form
					rv = self.app.post('/admin/tickets/'+str(ticket.id)+'/comment/', data=dict(comment=comment, _csrf_token=csrf, resolved='on'), follow_redirects = True)
					self.assertIn('Ticket closed.', rv.data)
					self.assertNotIn('Comment added.', rv.data)
					self.assertNotIn('Ticket reopened.', rv.data)
					# not ticket.active and "resolved" not in request.form
					rv = self.app.post('/admin/tickets/'+str(ticket.id)+'/comment/',data=dict(comment=comment, _csrf_token=csrf),  follow_redirects = True)
					self.assertIn('Ticket reopened.', rv.data)
					self.assertNotIn('Comment added.', rv.data)
					self.assertNotIn('Ticket closed.', rv.data)
				# comment is not null
				comment = 'Just for test'
				if ticket.active:
					# ticket.active and "resolved" not in request.form
					rv = self.app.post('/admin/tickets/'+str(ticket.id)+'/comment/', data=dict(comment=comment, _csrf_token=csrf), follow_redirects = True)
					self.assertIn('Comment added.', rv.data)
					self.assertNotIn('Ticket closed.', rv.data)
					self.assertNotIn('Ticket reopened.', rv.data)
					# ticket.active and "resolved" in request.form
					rv = self.app.post('/admin/tickets/'+str(ticket.id)+'/comment/', data=dict(comment=comment, _csrf_token=csrf, resolved='on'), follow_redirects = True)
					self.assertIn('Ticket closed.', rv.data)
					self.assertIn('Comment added.', rv.data)
					self.assertNotIn('Ticket reopened.', rv.data)
					# not ticket.active and "resolved" not in request.form
					rv = self.app.post('/admin/tickets/'+str(ticket.id)+'/comment/',data=dict(comment=comment, _csrf_token=csrf),  follow_redirects = True)
					self.assertIn('Ticket reopened.', rv.data)
					self.assertIn('Comment added.', rv.data)
					self.assertNotIn('Ticket closed.', rv.data)

		except TroubleTicket.DoesNotExist:
			pass
		
	def test_login_team(self):
		# create admin
		AdminUser.create(username=TEST_ADMIN_NAME, password=pwhash, secret=secret)
		#create a team
		User.create(username='nana', password=pwhash, email='56565@qq.com', email_confirmed=True, email_confirmation_key='12345678956565')
		user = User.get(User.username=='nana')
		team = Team.create(name='test1', affiliation='hust', eligible=True, team_leader=user)
		TeamMember.create(team=team, member=user, member_confirmed=True)
		# not login
		# test /team/<int:tid>/
		rv = self.app.get('/admin/team/1/', follow_redirects = True)
		self.assertIn('You must be an admin to access that page.', rv.data)
		csrf = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		# test /team/<int:tid>/<csrf>/toggle_eligibility_lock/
		rv = self.app.get('/admin/team/1/'+csrf+'/toggle_eligibility_lock/', follow_redirects = True)
		self.assertIn('You must be an admin to access that page.', rv.data)
		# login
		rv = self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		self.assertIn(TEST_ADMIN_NAME, rv.data)
		try:
			team = Team.get(Team.id == '1')
			if team:
				# test /team/<int:tid>/
				rv = self.app.get('/admin/team/'+str(team.id)+'/', follow_redirects = True)
				#csrf = re.findall(r'<a href="/admin/team/1/(.*))/toggle_eligibility/">',rv.data)[0]
				self.assertIn('计算分数', rv.data)
				# test /team/<int:tid>/<csrf>/toggle_eligibility/
				rv = self.app.get('/admin/team/'+str(team.id)+'/'+csrf+'/toggle_eligibility/', follow_redirects = True)
				self.assertIn('Eligibility set to', rv.data)
				# test /team/<int:tid>/<csrf>/toggle_eligibility_lock/
				rv = self.app.get('/admin/team/'+str(team.id)+'/'+csrf+'/toggle_eligibility_lock/', follow_redirects = True)
				self.assertIn('Eligibility lock set to', rv.data)
				# test /team/<int:tid>/adjust_score/
				data = dict(value = '10', reason = 'Test adjuse_score', _csrf_token = csrf)
				rv = self.app.post('/admin/team/'+str(team.id)+'/adjust_score/', data = data,follow_redirects = True)
				self.assertIn('Score adjusted.', rv.data)
		except Team.DoesNotExist:
			pass

	def test_login_notice(self):
		# create admin
		AdminUser.create(username=TEST_ADMIN_NAME, password=pwhash, secret=secret)
		# not login
		rv = self.app.get('/admin/notice/', follow_redirects=True)
		self.assertIn('You must be an admin to access that page.', rv.data)
		#login
		self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		rv = self.app.get('/admin/notice/', follow_redirects=True)
		csrf = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />', rv.data)[0]
		self.assertIn('发布通知', rv.data)
		#publish a notice
		TEST_TITLE = "Test Title"
		TEST_CONTENT = "Test Content"
		data = dict(title=TEST_TITLE,content=TEST_CONTENT,_csrf_token = csrf)
		rv = self.app.post('/admin/notice/',data=data,follow_redirects=True)
		self.assertIn("Publish Success!", rv.data)
		#paginate test
		for i in range(8):
			data = dict(title=TEST_TITLE+'_'+str(i),content=TEST_CONTENT+'_'+str(i),_csrf_token = csrf)
			self.app.post('/admin/notice/', data=data, follow_redirects=True)
		rv = self.app.get('/admin/notice/?page=2', follow_redirects=True)
		self.assertNotIn(TEST_TITLE+'_', rv.data)

	def test_login_challenge(self):
		challenge = Challenge.create(name='test',category='Web',author='nana',description='test,test,test',points='120',flag='flag{whatever}')
		# create admin
		AdminUser.create(username=TEST_ADMIN_NAME, password=pwhash, secret=secret)
		# not login
		rv = self.app.get('/admin/challenge/', follow_redirects=True)
		self.assertIn('You must be an admin to access that page.', rv.data)
		#login test challenge.html
		rv = self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		csrf = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />', rv.data)[0]
		rv = self.app.get('/admin/challenge/', follow_redirects=True)
		self.assertIn('管理题目', rv.data)
		# test set challenge enabled
		rv = self.app.get('/admin/challenge/'+str(challenge.id)+'/'+csrf+'/enable_challenge/', follow_redirects = True)
		self.assertIn('Enabled set to', rv.data)

	def test_login_vmachine(self):
		# create admin
		AdminUser.create(username=TEST_ADMIN_NAME, password=pwhash, secret=secret)
		# not login
		rv = self.app.get('/admin/challenge/', follow_redirects=True)
		self.assertIn('You must be an admin to access that page.', rv.data)
		challenge = Challenge.create(name=Vname,category='Web',author='nana',description='test,test,test',points='120',flag='flag{whatever}')
		rv = self.app.get('/admin/challenge/', follow_redirects=True)
		#login test challenge.html
		rv = self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		csrf = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />', rv.data)[0]
		rv = self.app.get('/admin/challenge/', follow_redirects=True)
		self.assertIn('连接服务器', rv.data)
		# test get_url 
		# wrong url
		# rv = self.app.post('/admin/geturl/', data=dict(url="qemu://222.0.0.1/system",xml="/etc/libvirt/qemu/", _csrf_token = csrf), follow_redirects=True)
		# self.assertIn("连接服务器", rv.data)
		# correct url
		rv = self.app.post('/admin/geturl/', data=dict(url="qemu:///system",xml="/home/nana/Vmachine/FreeDOS/",_csrf_token = csrf), follow_redirects=True)
		self.assertIn("虚拟机名", rv.data)
		# edit vmachine
		vmachine = Vmachine.get(Vmachine.name==Vname)
		rv = self.app.get('/admin/vmachine/'+str(vmachine.id)+'/', follow_redirects=True)
		self.assertIn('修改虚拟机', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status ='shutdown',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('shutdown', rv.data)
		data = dict(vmachine_memory='10aa',vmachine_cpu='1',vmachine_status='shutdown',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('must be digital', rv.data)
		data = dict(vmachine_memory='1025',vmachine_cpu='1',vmachine_status='shutdown',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('1025', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status='shutdown',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('1024', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='a',vmachine_status='shutdown',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('must be digital', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='0',vmachine_status='shutdown',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('cpu should between 1 and 4', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='5',vmachine_status='shutdown',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('cpu should between 1 and 4', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='2',vmachine_status='shutdown',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('2', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status='shutdown',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('1', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status='suspend',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('error', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status='resume',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('error', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status='running',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('running', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status='resume',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('error', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status='suspend',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('suspend', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status='shutdown',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('error', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status='running',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('error', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status='resume',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('running', rv.data)
		data = dict(vmachine_memory='1024',vmachine_cpu='1',vmachine_status='shutdown',_csrf_token = csrf)
		rv = self.app.post('/admin/vmachine/'+str(vmachine.id)+'/', data=data, follow_redirects=True)
		self.assertIn('shutdown', rv.data)




if __name__ == '__main__':
	unittest.main()
