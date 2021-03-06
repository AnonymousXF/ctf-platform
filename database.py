from peewee import *
db = SqliteDatabase("dev.db")

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
	username = CharField()
	password = CharField()
	email = CharField()
	email_confirmed = BooleanField(default=False)
	email_confirmation_key = CharField()		
		
class Team(BaseModel):
    name = CharField()
    affiliation = CharField()
    eligible = BooleanField()
    eligibility_locked = BooleanField(default=False)
    first_login = BooleanField(default=True)
    restricts = TextField(default="")
    team_confirmed=BooleanField(default=False)
    team_leader = ForeignKeyField(User, related_name='leader')
	
    def solved(self, challenge):
        return ChallengeSolve.select().where(ChallengeSolve.team == self, ChallengeSolve.challenge == challenge).count()

    @property
    def score(self):
        challenge_points = sum([i.challenge.points for i in self.solves])
        adjust_points = sum([i.value for i in self.adjustments])
        return challenge_points + adjust_points

class TeamMember(BaseModel):
	team = ForeignKeyField(Team, related_name='members')
	member = ForeignKeyField(User, related_name='members')		
	member_confirmed = BooleanField(default=False)
	class Meta:
		primary_key=CompositeKey('team', 'member')

	
class UserAccess(BaseModel):
    user = ForeignKeyField(User, related_name='accesses')
    ip = CharField()
    time = DateTimeField()

class Challenge(BaseModel):
    name = CharField()
    category = CharField()
    author = CharField()
    description = TextField()
    points = IntegerField()
    breakthrough_bonus = IntegerField(default=0)
    enabled = BooleanField(default=True)
    flag = TextField()

class Vmachine(BaseModel):
    name = CharField()
    memory = IntegerField()
    cpu = IntegerField()
    status = CharField()

class ChallengeSolve(BaseModel):
    team = ForeignKeyField(Team, related_name='solves')
    challenge = ForeignKeyField(Challenge, related_name='solves')
    time = DateTimeField()

    class Meta:
        primary_key = CompositeKey('team', 'challenge')

class ChallengeFailure(BaseModel):
    team = ForeignKeyField(Team, related_name='failures')
    challenge = ForeignKeyField(Challenge, related_name='failures')
    attempt = CharField()
    time = DateTimeField()

class NewsItem(BaseModel):
    title = CharField()
    content = TextField()
    time = DateTimeField()

class TroubleTicket(BaseModel):
    team = ForeignKeyField(Team, related_name='tickets')
    summary = CharField()
    description = TextField()
    active = BooleanField(default=True)
    opened_at = DateTimeField()

class TicketComment(BaseModel):
    ticket = ForeignKeyField(TroubleTicket, related_name='comments')
    comment_by = CharField()
    comment = TextField()
    time = DateTimeField()

class Notification(BaseModel):
    team = ForeignKeyField(Team, related_name='notifications')
    notification = TextField()

class ScoreAdjustment(BaseModel):
    team = ForeignKeyField(Team, related_name='adjustments')
    value = IntegerField()
    reason = TextField()

class AdminUser(BaseModel):
    username = CharField()
    password = CharField()
    secret = CharField()
