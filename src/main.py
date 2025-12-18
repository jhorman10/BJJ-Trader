from src.presentation.web.app import app, socketio, background_monitor
import threading

# Required for Render to pick up the app
# Gunicorn will look for 'app' here

if __name__ == "__main__":
    # Start monitor if running directly
    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    socketio.run(app, host='0.0.0.0', port=8888)
else:
    # When imported by Gunicorn, start the background thread
    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
