from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    # socketio.run wraps Flask's dev server so both REST routes and the
    # WebSocket chat/notification events work from the same port.
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
