import os
from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # socketio.run wraps Flask's dev server so both REST routes and the
    # WebSocket chat/notification events work from the same port.
    socketio.run(app, debug=False, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)