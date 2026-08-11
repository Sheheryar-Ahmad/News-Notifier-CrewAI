from http.server import BaseHTTPRequestHandler
import json
from crew import run_news_crew

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Run your CrewAI pipeline here
            run_news_crew()
            
            # Send a success response back to Vercel
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_data = {"status": "success", "message": "CrewAI pipeline executed successfully!"}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            # Handle any errors during execution
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_data = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(error_data).encode('utf-8'))
        return