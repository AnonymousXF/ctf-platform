import os
from datetime import datetime

ctf_name = "HUSTCTF"
#IRC Channel
ctf_chat_channel = "#tjctf"
ctf_home_url = "http://tjctf.org"
eligibility = "In order to be eligible for prizes, all members of your team must be in high school, and you must not have more than four team members."
tagline = "a cybersecurity competition created by TJHSST students"

cdn = False
apisubmit = True
registration = True
debug = True
proxied_ip_header = "X-Forwarded-For"

flag_rl = 5
teams_on_graph = 10
team_members = 4

immediate_scoreboard = True

# IPs that are allowed to confirm teams by posting to /teamconfirm/
# Useful for verifying resumes and use with resume server.
confirm_ip = []

static_prefix = "http://127.0.0.1/tjctf-static/"
static_dir = "{}/static/".format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
custom_stylesheet = "tjctf.css"

interval = 1
competition_begin = datetime(1970, 1, 1, 0, 0)
competition_end = datetime(2018, 1, 1, 0, 0)

# Are you using a resume server?
resumes = True
# If yes, where's it hosted? Otherwise, just put None.
resume_server = "https://resumes.tjctf.org"

disallowed_domain = "tjctf.org"

email_sender = os.environ.get('MAIL_USERNAME')
email_pass = os.environ.get('MAIL_PASSWORD')
email_host = os.environ.get('MAIL_HOST')

def competition_is_running():
    return competition_begin < datetime.now() < competition_end

# Don't touch these. Instead, copy secrets.example to secrets and edit that.
import yaml
from collections import namedtuple
with open("secrets") as f:
    _secret = yaml.load(f)
    secret = namedtuple('SecretsDict', _secret.keys())(**_secret)
