from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import mysql.connector

# --- MySQL Connection Setup ---
conn = mysql.connector.connect(
    host="localhost",
    user="phpmyadmin",
    password="test@123",
    database="pythonscripts"
)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100)
    )
""")

# --- HTTP Handler ---
class SimpleHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open("form.html", "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/submit":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_vars = urllib.parse.parse_qs(post_data.decode())

            name = post_vars.get("name", [""])[0]
            email = post_vars.get("email", [""])[0]

            try:
                cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
                conn.commit()

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Form submitted successfully.")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Database error: {e}".encode())
        else:
            self.send_error(404)

# --- Run Server ---
if __name__ == "__main__":
    print("Server started at http://localhost:8000")
    server = HTTPServer(("localhost", 8000), SimpleHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()
        conn.close()
