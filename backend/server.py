from http.server import HTTPServer
from httpclass import SimpleHTTPRequestHandler


def webserver_thread():
    # Set the host and port for the server
    host = '0.0.0.0'
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