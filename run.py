import os
from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    is_production = os.environ.get("RAILWAY_ENVIRONMENT") is not None
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=not is_production,
        allow_unsafe_werkzeug=True,
    )
