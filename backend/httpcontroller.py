import globals

import json

#########################################################################
#########################################################################
###########################      GETS      ##############################
#########################################################################
#########################################################################

def get_questions():
    questions = globals.state.questions
    categories = list(set([q.category for q in questions]))
    byCategory = [[q.__dict__ for q in questions if q.category == c] for c in categories]

    return 200, json.dumps(byCategory)


def get_winners():
    winners = sorted(globals.state.players, key=lambda p: -1 * p.balance)
    return 200, json.dumps([w.__dict__ for w in winners])


def get_players():
    players = globals.state.players
    return 200, json.dumps([p.__dict__ for p in players])

#########################################################################
#########################################################################
############################     POSTS      #############################
#########################################################################
#########################################################################

def post_players(body):
    if "players" not in body or type(body["players"]) != type([""]):
        return 400, '{"error": "bad request"}'
    
    try:
        globals.state.setPlayers(body["players"])
        return 200, '{"status": "success"}'
    except AssertionError as e:
        return 422, '{"error": "' + str(e) + '"}'
    
def post_start_question():
    globals.state.setAnswering()
    return 200, '{"status": "success"}'

def post_skip():
    globals.state.skipQuestion()
    return 200, '{"status": "success"}'

def post_answer(body):
    if "correct" not in body or type(body["correct"]) != type(True):
        return 400, '{"error": "bad request"}'
    
    try:
        globals.state.answerQuestion(body["correct"])
        return 200, f'{{"skip": {str(globals.state.state != 2).lower()}}}'
    except ValueError as e:
        return 422, '{"error": "' + str(e) + '"}'
    
def post_buzz(body):
    if "player" not in body or type(body["player"]) != type(1):
        return 400, '{"error": "bad request"}'

    try:
        globals.state.setCurrentPlayer(body["player"])
        return 200, '{"status": "success"}'
    except ValueError as e:
        return 422, '{"error": "' + str(e) + '"}'

def set_question(body):
    print(body)
    if "id" not in body or type(body["id"]) != type(1):
        return 400, '{"error": "bad request"}'
    
    try:
        globals.state.selectQuestion(body["id"])
        return 200, '{"status": "success"}'
    except ValueError as e:
        return 422, '{"error": "' + str(e) + '"}'