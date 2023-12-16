from http.server import BaseHTTPRequestHandler, HTTPServer
from gamestate import GameState
import json

state = GameState()

def playertodic(player):
    pass 

def jsonstate():
    dicionario = {
        
        "currentPlayer": state.currentPlayer,
        "state":state.state,     
        "players":[playertodic(p)for p in state.players]
    }
    return json.dumps(dicionario).encode("utf-8")


# Create a custom HTTPRequestHandler class by subclassing BaseHTTPRequestHandler
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    # Define the do_GET method to handle GET requests
    def do_GET(self):
        if self.path == "/state":

            # Set response status code
            self.send_response(200)
            
            # Set headers
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Write the response body
            self.wfile.write(jsonstate())
        else:
            
            # Set response status code
            self.send_response(404)
            
            # Set headers
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # Write the response body
            self.wfile.write(b'{"error":"not found"}')

# Set the host and port for the server
host = 'localhost'
port = 8000

# Create an instance of HTTPServer with the defined host and port, and the custom handler
httpd = HTTPServer((host, port), SimpleHTTPRequestHandler)
print(f"Server running on {host}:{port}")

# Start the server and keep it running until interrupted
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.server_close()
    print("\nServer stopped")