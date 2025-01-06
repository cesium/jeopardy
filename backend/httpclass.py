from http.server import BaseHTTPRequestHandler
import json
import httpcontroller
import globals

def playertodic(player):
    pass 

def jsonstate():
    dicionario = {
        "currentPlayer": globals.state.get_current_player().toDict(),
        "state":globals.state.state,     
        "players":[playertodic(p)for p in globals.state.playersController.players]
    }
    return json.dumps(dicionario)


# Create a custom HTTPRequestHandler class by subclassing BaseHTTPRequestHandler
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def __post_body__(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        return json.loads(post_body.decode("utf-8")) #TODO: Error handling invalid format


    def do_OPTIONS(self):
        self.send_response(200)
            
        # Set headers
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.end_headers()

    # Define the do_GET method to handle GET requests
    def do_GET(self):
        status = 404
        content = '{"error": "Not found"}'

        with globals.state_condition:
            if self.path == "/state":
                status = 200
                content = jsonstate()
            elif self.path == "/questions":
                status, content = httpcontroller.get_questions()
            elif self.path == "/winners":
                status, content = httpcontroller.get_winners()
            elif self.path == "/players":
                status, content = httpcontroller.get_players()
            elif self.path.startswith("/question/"):
                id = self.path.removeprefix("/question/")
                status = 200
                content = json.dumps(globals.state.questions[int(id)].toDict())

        # Set response status code
        self.send_response(status)
        
        # Set headers
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.end_headers()

        # Write the response body
        self.wfile.write(content.encode("utf-8"))
    

    def do_POST(self):
        status = 404
        content = '{"error": "Not found"}'

        with globals.state_condition:
            globals.state.playCorrectSound = False
            globals.state.playWrongSound = False
            if self.path == "/answer":
                status, content = httpcontroller.post_answer(self.__post_body__())
            elif self.path == "/skip":
                status, content = httpcontroller.post_skip()
            elif self.path == "/question":
                status, content = httpcontroller.set_question(self.__post_body__())
            elif self.path == "/players":
                status, content = httpcontroller.post_players(self.__post_body__())
            elif self.path == "/buzz":
                status, content = httpcontroller.post_buzz(self.__post_body__())
            elif self.path == "/buzz_start":
                status, content = httpcontroller.post_start_question()
                with globals.buzz_condition:
                    globals.buzz_condition.notify_all()

            if status // 100 == 2:
                globals.state_condition.notify_all()

        # Set response status code
        self.send_response(status)
        
        # Set headers
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        
        self.end_headers()

        # Write the response body
        self.wfile.write(content.encode("utf-8"))