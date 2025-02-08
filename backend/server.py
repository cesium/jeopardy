# pylint: disable=too-few-public-methods
"""Module responsable for hosting the api to comunicate with frontend"""

from asyncio import Lock
from typing import List
import logging
import os
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
from saves import get_last_save, get_saves_names, load_save, save_state
from gamestate.gamestate import GameState

# Initialize FastAPI app
app = FastAPI()

app.my_clients = set()
app.my_clients_lock = Lock()
app.my_state = None


class StateConditionMiddleware(BaseHTTPMiddleware):
    """Middleware for executing actions before and after each request"""

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST":
            app.my_state.reset_sound()
        response = await call_next(request)

        if request.method == "POST" and response.status_code // 100 == 2:
            logging.info("Propagating state")
            await send_to_clients(
                app.my_state.to_dict(), request.url.path.replace("/", "")
            )

        return response


app.add_middleware(StateConditionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def catch_multiple_exceptions(_: Request, exc: Exception) -> JSONResponse:
    """handling exceptions in fastapi request functions

    Args:
        request (Request): the request that was done
        exc (Exception): the exception raised

    Returns:
        JSONResponse: the JSON response that should be given acording to the exception type
    """
    if isinstance(exc, (ValueError, AssertionError)):
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)},
        )
    # Handle other exceptions (optional)
    logging.error(str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )


class Team(BaseModel):
    """JSON representation of a team"""

    names: List[str]
    balance: int


class Question(BaseModel):
    """JSON representation of a question"""

    id: int
    statement: str
    answer: str
    image: str
    value: int
    category: str
    answered: bool


class State(BaseModel):
    """JSON representation of answering a question"""

    currentTeam: Team
    state: int
    teams: List[Team]


class Answer(BaseModel):
    """JSON representation of answering a question"""

    correct: bool


class AnswerResponse(BaseModel):
    """JSON representation of a response to answering a question"""

    skip: bool


class BasicResponse(BaseModel):
    """JSON representation of a status response"""

    status: str


class SetQuestion(BaseModel):
    """JSON representation of selecting a question"""

    id: int


class SetTeams(BaseModel):
    """JSON representation of setting name of the teams"""

    teams: List[List[str]]


class Buzzer(BaseModel):
    """JSON representation of someone pressing the Buzz"""

    controller: int
    color: str


@app.get("/state", response_model=State)
def get_state() -> dict:
    """get the state of the game

    Returns:
        dict: JSON response
    """
    return {
        "currentTeam": app.my_state.get_current_team(),
        "state": app.my_state.state,
        "teams": [p.to_dict() for p in app.my_state.list_teams()],
    }


@app.get("/questions", response_model=list[list[Question]])
def get_questions() -> list:
    """list all questions

    Returns:
        list: JSON response
    """
    questions = app.my_state.list_questions()
    categories = list({q.category for q in questions})
    return [[q.to_dict() for q in questions if q.category == c] for c in categories]


@app.get("/winners", response_model=list[Team])
def get_winners() -> list:
    """list the game winners

    Returns:
        list: JSON response
    """
    return [
        t.to_dict()
        for t in sorted(
            app.my_state.list_teams(), key=lambda p: p.balance, reverse=True
        )
    ]


@app.get("/teams", response_model=list[Team])
def get_teams() -> list:
    """list teams

    Returns:
        list: JSON response
    """
    return [p.to_dict() for p in app.my_state.list_teams()]


@app.get("/question/{idx}", response_model=Question)
def get_question(idx: int) -> dict:
    """_summary_

    Args:
        idx (int): _description_

    Returns:
        dict: JSON response
    """
    print(idx)
    q = app.my_state.get_question(idx)
    if q is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return q.to_dict()


@app.post("/answer", response_model=AnswerResponse)
def post_answer(body: Answer) -> dict:
    """someone answered the question

    Args:
        body (Answer): is the answer correct

    Returns:
        dict: JSON response
    """
    app.my_state.answer_question(body.correct)
    return {"skip": (app.my_state.state != 2)}


@app.post("/skip", response_model=BasicResponse)
def post_skip() -> dict:
    """skip the current question

    Returns:
        dict: JSON response
    """
    app.my_state.skip_question()
    return {"status": "success"}


@app.post("/question", response_model=BasicResponse)
def post_set_question(body: SetQuestion) -> dict:
    """select a question

    Args:
        body (SetTeams): id of the question selected

    Returns:
        dict: JSON response
    """
    app.my_state.select_question(body.id)
    return {"status": "success"}


@app.post("/teams", response_model=BasicResponse)
def post_teams(body: SetTeams) -> dict:
    """set the name of the teams

    Args:
        body (SetTeams): the name of the teams

    Returns:
        dict: JSON response
    """
    app.my_state.set_teams(body.teams)
    return {"status": "success"}


@app.post("/buzz", response_model=BasicResponse)
def post_buzz(body: Buzzer) -> dict:
    """set as someone pressing the buzz button

    Args:
        body (Buzzer): id of pressed buzz controller

    Returns:
        dict: JSON response
    """
    app.my_state.buzz(body.controller, body.color)
    return {"status": "success"}


@app.post("/buzz_start", response_model=BasicResponse)
def post_buzz_start() -> dict:
    """start accepting buzz inputs

    Returns:
        dict: JSON response
    """
    app.my_state.set_answering()
    return {"status": "success"}


@app.post("/stop_timer", response_model=BasicResponse)
def post_stop_timer() -> dict:
    """stop accepting buzz inputs

    Returns:
        dict: JSON response
    """
    app.my_state.stop_countdown_timer()
    return {"status": "success"}


@app.post("/show_sos", response_model=BasicResponse)
def post_show_sos() -> dict:
    """show SOS

    Returns:
        dict: JSON response
    """
    app.my_state.show_sos()
    return {"status": "success"}


@app.post("/end", response_model=BasicResponse)
def post_end() -> dict:
    """end the game

    Returns:
        dict: JSON response
    """
    app.my_state.end_game()
    return {"status": "success"}


class FixPoints(BaseModel):
    """JSON representation needing to alter a team's points"""

    team_id: int
    points: int


@app.post("/fix/points/", response_model=BasicResponse)
def post_fix_pontos(body: FixPoints) -> dict:
    """add/subtract points to a team

    Args:
        body (FixPoints): body of the request

    Returns:
        dict: JSON response
    """
    app.my_state.add_points(body.team_id, body.points)
    return {"status": "success"}


class FixState(BaseModel):
    """JSON representation needing to alter a team's points"""

    state: int


@app.post("/fix/state/", response_model=BasicResponse)
def post_fix_state(body: FixState) -> dict:
    """change the state of the game

    Args:
        body (FixState): body of the request

    Returns:
        dict: JSON response
    """
    app.my_state.set_state(body.state)
    return {"status": "success"}


class FixSelecting(BaseModel):
    """JSON representation needing to alter a team's points"""

    team_id: int


@app.post("/fix/selecting/", response_model=BasicResponse)
def post_fix_selecting(body: FixSelecting) -> dict:
    """change the selecting team of the game

    Args:
        body (FixSelecting): body of the request

    Returns:
        dict: JSON response
    """
    app.my_state.set_selecting(body.team_id)
    return {"status": "success"}


@app.get("/fix/saves/", response_model=list[str])
def get_fix_saves() -> list:
    """list all saved game states

    Returns:
        list: JSON response
    """
    return list(map(lambda x: x[1], get_saves_names()))


class FixSave(BaseModel):
    """JSON representation for reverting to a saved game state"""

    name: str


@app.post("/fix/saves/", response_model=BasicResponse)
def post_fix_saves(body: FixSave) -> dict:
    """revert to a saved game state

    Args:
        body (FixSave): body of the request

    Returns:
        dict: JSON response
    """
    state = load_save(body.name)
    if state is None:
        raise HTTPException(status_code=404, detail="Save not found")
    app.my_state = state
    return {"status": "success"}


async def send_to_clients(message: str | dict, action: str):
    """Broadcast a message to every websocket connected

    Args:
        message (str|dict): the message to broadcast
        action (str): the action that triggered the message
    """
    async with app.my_clients_lock:
        for client in list(app.my_clients):
            if isinstance(message, str):
                await client.send_text(message)
            elif isinstance(message, dict):
                await client.send_json(message)
    app.my_state.reset_sound()
    save_state(app.my_state, action)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Handle websocket connections

    Args:
        ws (WebSocket): websocket connection
    """
    await ws.accept()
    async with app.my_clients_lock:
        app.my_clients.add(ws)
    await ws.send_json(app.my_state.to_dict())
    try:
        while True:
            message = await ws.receive_text()
            send_to_clients(message, "ws_message_recieved")
    except WebSocketDisconnect:
        async with app.my_clients_lock:
            app.my_clients.remove(ws)


def start(host: str, port: int, controllers_port: int):
    """fuction to start webserver

    Args:
        host (str): host server will run on
        port (int): port server will run on
    """
    if not os.path.exists("backend/saves"):
        os.mkdir("backend/saves")

    app.my_state = get_last_save()
    if app.my_state is None:
        app.my_state = GameState("localhost", controllers_port)

    uvicorn.run(app, host=host, port=port, ws="websockets")
