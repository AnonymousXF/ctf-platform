from database import Challenge, ChallengeSolve, ChallengeFailure
from flask import g
from ctferror import *
from datetime import datetime
import config

def submit_flag(team, challenge, flag):
    if g.redis.get("rl{}".format(team.id)):
        delta = config.competition_end - datetime.now()
        if delta.total_seconds() > (config.flag_rl * 6):
            return FLAG_SUBMISSION_TOO_FAST

    if team.solved(challenge):
        return FLAG_SUBMITTED_ALREADY
    elif not challenge.enabled:
        return FLAG_CANNOT_SUBMIT_WHILE_DISABLED
    elif flag != challenge.flag:     # delete strip().lower()
        g.redis.set("rl{}".format(team.id), str(datetime.now()), config.flag_rl)
        ChallengeFailure.create(team=team, challenge=challenge, attempt=flag, time=datetime.now())
        return FLAG_INCORRECT
    else:
        g.redis.hincrby("solves", challenge.id, 1)
        if config.immediate_scoreboard:
            g.redis.delete("scoreboard")
            g.redis.delete("graph")
        ChallengeSolve.create(team=team, challenge=challenge, time=datetime.now())
        return SUCCESS
