from src.presentation.web.app import app, socketio, bot_service
import threading

# Required for Render to pick up the app
# Gunicorn will look for 'app' here

if __name__ == "__main__":
    # Start monitor if running directly
    bot_service.start()
    
    socketio.run(app, host='0.0.0.0', port=8888)
else:
    # When imported by Gunicorn, start the background thread
    bot_service.start()
