#!/usr/bin/env python3
"""
Simple HTTP Server for Dummy Bol.com Tracking Test
Run this to serve the HTML file locally for testing user tracking and event logging.
"""

import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, parse_qs
import datetime

class TrackingHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for analytics tracking"""
        if self.path in ['/api/analytics/events', '/analytics']:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # Handle both single events and batch events
                if 'events' in data:
                    # Batch events from sendEvents()
                    events = data.get('events', [])
                    session_id = events[0].get('sessionId') if events else 'unknown'
                    user_id = events[0].get('userId') if events else 'unknown'
                elif 'type' in data:
                    # Single event from test button
                    events = [data]
                    session_id = 'test_session'
                    user_id = 'test_user'
                else:
                    events = [data]
                    session_id = data.get('sessionId', 'unknown')
                    user_id = data.get('userId', 'unknown')
                
                # Log the received tracking data
                timestamp = datetime.datetime.now().isoformat()
                log_entry = {
                    'timestamp': timestamp,
                    'sessionId': session_id,
                    'userId': user_id,
                    'events': events
                }
                
                # Save to file for analysis
                self.save_tracking_data(log_entry)
                
                # Print to console
                print(f"\n🎯 TRACKING DATA RECEIVED at {timestamp}")
                print(f"Session ID: {session_id}")
                print(f"User ID: {user_id}")
                print(f"Number of events: {len(events)}")
                for event in events:
                    event_type = event.get('eventType') or event.get('type', 'unknown')
                    event_data = event.get('data', event.get('message', 'no data'))
                    print(f"  - {event_type}: {event_data}")
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {'status': 'success', 'message': f'Successfully logged {len(events)} events'}
                self.wfile.write(json.dumps(response).encode())
                
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
            except Exception as e:
                print(f"Error processing tracking data: {e}")
                self.send_error(500, "Internal server error")
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def save_tracking_data(self, log_entry):
        """Save tracking data to a structured txt file"""
        log_file = 'tracking_events.txt'
        
        try:
            # Format the log entry as structured text
            log_text = self.format_log_entry(log_entry)
            
            # Append to txt file
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_text + '\n')
            
            print(f"📝 Tracking data saved to {log_file}")
            
        except Exception as e:
            print(f"❌ Error saving tracking data: {e}")
    
    def format_log_entry(self, log_entry):
        """Format log entry as structured text"""
        timestamp = log_entry.get('timestamp', 'Unknown')
        session_id = log_entry.get('sessionId', 'Unknown')
        user_id = log_entry.get('userId', 'Unknown')
        events = log_entry.get('events', [])
        
        # Create structured log text
        log_lines = []
        log_lines.append("=" * 80)
        log_lines.append(f"BATCH_TIMESTAMP: {timestamp}")
        log_lines.append(f"SESSION_ID: {session_id}")
        log_lines.append(f"USER_ID: {user_id}")
        log_lines.append(f"TOTAL_EVENTS: {len(events)}")
        log_lines.append("-" * 40)
        
        # Add each event
        for i, event in enumerate(events, 1):
            event_type = event.get('eventType') or event.get('type', 'unknown')
            event_data = event.get('data', event.get('message', 'no data'))
            event_timestamp = event.get('timestamp', 'unknown')
            event_url = event.get('url', 'unknown')
            
            log_lines.append(f"EVENT_{i}:")
            log_lines.append(f"  Type: {event_type}")
            log_lines.append(f"  Timestamp: {event_timestamp}")
            log_lines.append(f"  URL: {event_url}")
            
            # Format data based on type
            if isinstance(event_data, dict):
                log_lines.append(f"  Data: {json.dumps(event_data, indent=6)}")
            else:
                log_lines.append(f"  Data: {event_data}")
            log_lines.append("")
        
        log_lines.append("=" * 80)
        log_lines.append("")  # Empty line for separation
        
        return '\n'.join(log_lines)

def main():
    PORT = 8000
    
    print("🚀 Starting Dummy Bol.com Tracking Server...")
    print(f"🌐 Server will run on http://localhost:{PORT}")
    print("📁 Make sure index.html is in the current directory")
    print("🎯 Tracking data will be saved to tracking_events.txt")
    print("📋 Server accepts both /api/analytics/events and /analytics endpoints")
    print("⚠️  If events fail, disable ad blockers and browser extensions")
    print("⏹️  Press Ctrl+C to stop the server\n")
    
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        with socketserver.TCPServer(("", PORT), TrackingHandler) as httpd:
            print(f"✅ Server started successfully!")
            print(f"🔗 Open http://localhost:{PORT} in your browser")
            print("📊 Watch this console for real-time tracking events")
            print("🧪 Use the 'Test API' button to verify connection\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 10048:  # Port already in use on Windows
            print(f"❌ Port {PORT} is already in use. Try a different port or close the application using it.")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
