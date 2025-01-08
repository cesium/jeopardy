# pylint: disable=too-few-public-methods
"""Module responsable for hosting the api to comunicate with frontend"""

from asyncio import Lock
from typing import List
import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import shared_globals

# Initialize FastAPI app
app = FastAPI()

app.my_clients = set()
app.my_clients_lock = Lock()


class StateConditionMiddleware(BaseHTTPMiddleware):
    """Middleware for executing actions before and after each request"""

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST":
            shared_globals.state.reset_sound()
        response = await call_next(request)

        if request.method == "POST" and response.status_code // 100 == 2:
            logging.info("Propagating state")
            await send_to_clients(shared_globals.state.to_dict())

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
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )


class Player(BaseModel):
    """JSON representation of a player"""

    name: str
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

    currentPlayer: Player
    state: int
    players: List[Player]


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


class SetPlayers(BaseModel):
    """JSON representation of setting name of the players"""

    players: List[str]


class Buzz(BaseModel):
    """JSON representation of someone pressing the Buzz"""

    player: int


@app.get("/state", response_model=State)
def get_state() -> dict:
    """get the state of the game

    Returns:
        dict: JSON response
    """
    return {
        "currentPlayer": shared_globals.state.get_current_player(),
        "state": shared_globals.state.state,
        "players": [None for p in shared_globals.state.list_players()],
    }


@app.get("/questions", response_class=List[Question])
def get_questions() -> list:
    """list all questions

    Returns:
        list: JSON response
    """
    questions = shared_globals.state.list_questions()
    categories = list({q.category for q in questions})
    return [[q for q in questions if q.category == c] for c in categories]


@app.get("/winners", response_class=List[Player])
def get_winners() -> list:
    """list the game winners

    Returns:
        list: JSON response
    """
    return sorted(
        shared_globals.state.list_players(), key=lambda p: p.balance, reverse=True
    )


@app.get("/players", response_class=List[Player])
def get_players() -> list:
    """list players

    Returns:
        list: JSON response
    """
    return [p.to_dict() for p in shared_globals.state.list_players()]


@app.get("/question/{idx}", response_model=Question)
def get_question(idx: int) -> dict:
    """_summary_

    Args:
        idx (int): _description_

    Returns:
        dict: JSON response
    """
    return shared_globals.state.get_question(idx).to_dict()


@app.post("/answer", response_model=AnswerResponse)
def post_answer(body: Answer) -> dict:
    """someone answered the question

    Args:
        body (Answer): is the answer correct

    Returns:
        dict: JSON response
    """
    shared_globals.state.answer_question(body.correct)
    return {"skip": (shared_globals.state.state != 2)}


@app.post("/skip", response_model=BasicResponse)
def post_skip() -> dict:
    """skip the current question

    Returns:
        dict: JSON response
    """
    shared_globals.state.skip_question()
    return {"status": "success"}


@app.post("/question", response_model=BasicResponse)
def post_set_question(body: SetQuestion) -> dict:
    """select a question

    Args:
        body (SetPlayers): id of the question selected

    Returns:
        dict: JSON response
    """
    shared_globals.state.select_question(body.id)
    return {"status": "success"}


@app.post("/players", response_model=BasicResponse)
def post_players(body: SetPlayers) -> dict:
    """set the name of the players

    Args:
        body (SetPlayers): the name of the players

    Returns:
        dict: JSON response
    """
    shared_globals.state.set_players(body.players)
    return {"status": "success"}


@app.post("/buzz", response_model=BasicResponse)
def post_buzz(body: Buzz) -> dict:
    """set as someone pressing the buzz button

    Args:
        body (Buzz): id of pressed buzz controller

    Returns:
        dict: JSON response
    """
    shared_globals.state.set_current_player(body.player)
    return {"status": "success"}


@app.post("/buzz_start", response_model=BasicResponse)
def post_buzz_start() -> dict:
    """start accepting buzz inputs

    Returns:
        dict: JSON response
    """
    shared_globals.state.set_answering()
    with shared_globals.buzz_condition:
        shared_globals.buzz_condition.notify_all()
    return {"status": "success"}


async def send_to_clients(message: str | dict):
    """Broadcast a message to every websocket connected

    Args:
        message (str|dict): the message to broadcast
    """
    async with app.my_clients_lock:
        for client in list(app.my_clients):
            if isinstance(message, str):
                await client.send_text(message)
            elif isinstance(message, dict):
                await client.send_json(message)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Handle websocket connections

    Args:
        ws (WebSocket): websocket connection
    """
    await ws.accept()
    async with app.my_clients_lock:
        app.my_clients.add(ws)
    await ws.send_json(shared_globals.state.to_dict())
    try:
        while True:
            message = await ws.receive_text()
            send_to_clients(message)
    except WebSocketDisconnect:
        async with app.my_clients_lock:
            app.my_clients.remove(ws)
    finally:
        await ws.close()


def webserver_thread(host: str, port: int):
    """fuction to start webserver

    Args:
        host (str): host server will run on
        port (int): port server will run on
    """

    print(f"Server running on {host}:{port}")
    uvicorn.run(app, host=host, port=port, ws="websockets")
