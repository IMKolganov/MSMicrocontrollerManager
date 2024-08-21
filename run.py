# run.py

import signal
import sys
from app.main import create_app

app = create_app()

def handle_shutdown_signal(signum, frame):
    print("Shutdown signal received. Stopping the message processing and Flask server...")
    # Add any cleanup code here if needed, such as closing connections
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    
    print("Starting Flask app...")
    app.run(debug=True, host='0.0.0.0', port=4000)