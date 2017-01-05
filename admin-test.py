import unittest
import os
from app import app
from database import *
import peewee
import config
import re
import admin
from datetime import datetime
import random
import utils.admin

TEST_ADMIN_NAME = 'nana'
TEST_ADMIN_PASSWORD = 'nana'
r = random.SystemRandom()
secret = "".join([r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for i in range(16)])
pwhash = utils.admin.create_password(TEST_ADMIN_PASSWORD)

class BasicTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		os.system('python D:/ctf-platform/ctftool create-tables')
		

	def tearDown(self):
		tables = [Team, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
		[i.drop_table() for i in tables]

	def test_index(self):
		response = self.app.get('/admin/', content_type = 'html/text',follow_redirects=True)
		self.assertEqual(200, response.status_code)

	def test_databse(self):
		tester = os.path.exists("dev.db")
		self.assertTrue(tester)

class FlaskrTestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		os.system('python D:/ctf-platform/ctftool create-tables')

	def tearDown(self):
		tables = [Team, TeamAccess, Challenge, ChallengeSolve, ChallengeFailure, NewsItem, TroubleTicket, TicketComment, Notification, ScoreAdjustment, AdminUser]
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
	
	def test_login_and_logout(self):
		# create admin
		AdminUser.create(username=TEST_ADMIN_NAME, password=pwhash, secret=secret)
		# correct data
		rv = self.login(TEST_ADMIN_NAME, TEST_ADMIN_PASSWORD)
		self.assertIn(TEST_ADMIN_NAME, rv.data)
		rv = self.logout()
		self.assertIn(b'Login',rv.data)
		#Wrong data
		rv = self.login('', '')
		self.assertIn(b'You have made a terrible mistake.', rv.data)
		rv = self.login(TEST_ADMIN_NAME+'111', TEST_ADMIN_PASSWORD+'111')
		self.assertIn(b'You have made a terrible mistake.', rv.data)
	
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
		self.assertIn('Score', rv.data)

	def test_login_tickets(self):
		# create admin
		AdminUser.create(username=TEST_ADMIN_NAME, password=pwhash, secret=secret)
		# create a team
		team = Team.create(name='test_team', email='358693294@qq.com', eligible=True, affiliation='Hust', key='tjctf_87rfu0nwhtk0a5nc6tnzx5z8eoyr9hxu',
                            email_confirmation_key='6b654twftg4vjzpl8zzpw6y0g5ilh08ti2ytczo323ajmua7')
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
		team = Team.create(name='test_team', email='358693294@qq.com', eligible=True, affiliation='Hust', key='tjctf_87rfu0nwhtk0a5nc6tnzx5z8eoyr9hxu',
                            email_confirmation_key='6b654twftg4vjzpl8zzpw6y0g5ilh08ti2ytczo323ajmua7')
		# not login
		# test /team/<int:tid>/
		rv = self.app.get('/admin/team/1/', follow_redirects = True)
		self.assertIn('You must be an admin to access that page.', rv.data)
		csrf = re.findall(r'<input name="_csrf_token" type="hidden" value="(.*)" />',rv.data)[0]
		# test /team/<int:tid>/<csrf>/impersonate/
		rv = self.app.get('/admin/team/1/'+csrf+'/impersonate/', follow_redirects = True)
		self.assertIn('You must be an admin to access that page.', rv.data)
		# test /team/<int:tid>/<csrf>/toggle_eligibility/
		rv = self.app.get('/admin/team/1/'+csrf+'/impersonate/', follow_redirects = True)
		self.assertIn('You must be an admin to access that page.', rv.data)
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
				csrf = re.findall(r'<a href="/admin/team/1/(.*)/impersonate/">Impersonate team</a><br />',rv.data)[0]
				self.assertIn('Score adjustment', rv.data)
				# test /team/<int:tid>/<csrf>/impersonate/
				rv = self.app.get('/admin/team/'+str(team.id)+'/'+csrf+'/impersonate/', follow_redirects = True)
				self.assertIn('Score progression', rv.data)
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

if __name__ == '__main__':
	unittest.main()