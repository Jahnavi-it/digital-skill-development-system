"""
Real-time layer for Chat + live Notification delivery.

Design (kept deliberately simple for a CSP project):
- Each logged-in browser tab opens one Socket.IO connection and passes its
  JWT as `auth: { token }` on connect.
- On connect, the server verifies the JWT and puts that socket in a private
  room named `user_<id>`. Sending to that room = sending to that one user,
  on any device/tab they have open.
- `send_message` persists the message to MySQL (via ChatMessage) and then
  emits it into both the sender's and receiver's rooms, so both sides'
  UIs update instantly without polling.
"""
from flask import request
from flask_socketio import join_room, leave_room, emit, disconnect
from flask_jwt_extended import decode_token

from app import socketio, db
from app.models import ChatMessage, User

# Track which user_id owns which socket connection (per-process; fine for a
# single-server student deployment).
_socket_user_map = {}


def _authenticate(auth):
    token = (auth or {}).get("token")
    if not token:
        return None
    try:
        decoded = decode_token(token)
        return decoded["sub"]  # user id, stored as identity string
    except Exception:
        return None


@socketio.on("connect")
def handle_connect(auth):
    user_id = _authenticate(auth)
    if not user_id:
        disconnect()
        return False
    _socket_user_map[request.sid] = user_id
    join_room(f"user_{user_id}")
    emit("connected", {"message": "Connected to DSDS chat/notifications"})


@socketio.on("disconnect")
def handle_disconnect():
    user_id = _socket_user_map.pop(request.sid, None)
    if user_id:
        leave_room(f"user_{user_id}")


@socketio.on("send_message")
def handle_send_message(data):
    sender_id = _socket_user_map.get(request.sid)
    if not sender_id:
        return

    receiver_id = data.get("receiver_id")
    text = (data.get("message") or "").strip()
    if not receiver_id or not text:
        return

    msg = ChatMessage(sender_id=sender_id, receiver_id=receiver_id, message=text)
    db.session.add(msg)
    db.session.commit()

    payload = {
        "id": msg.id, "sender_id": msg.sender_id, "receiver_id": msg.receiver_id,
        "message": msg.message, "sent_at": msg.sent_at.isoformat(),
    }
    # deliver to both sides so open tabs update immediately
    emit("new_message", payload, room=f"user_{receiver_id}")
    emit("new_message", payload, room=f"user_{sender_id}")

    sender = User.query.get(sender_id)
    from app.routes.notifications import create_notification
    create_notification(receiver_id, f"New message from {sender.name if sender else 'a user'}")


@socketio.on("typing")
def handle_typing(data):
    sender_id = _socket_user_map.get(request.sid)
    receiver_id = data.get("receiver_id")
    if sender_id and receiver_id:
        emit("typing", {"sender_id": sender_id}, room=f"user_{receiver_id}")


# ------------------------------------------------------------------
# Phase 5 — Live Classes: simplified WebRTC signaling
#
# This server never touches audio/video itself — it only relays the
# small JSON "signal" messages (SDP offers/answers + ICE candidates)
# that browsers need to exchange before they can open a *direct*
# peer-to-peer media connection. Each live class has its own
# `call_<room_code>` room used purely for presence (who's in the
# call); the actual offer/answer/candidate messages are routed
# directly to one target user via their `user_<id>` room, which
# keeps this simple mesh approach easy to follow for a student demo.
# ------------------------------------------------------------------

# room_code -> set of user_ids currently in that call
_call_rooms = {}


@socketio.on("join_call")
def handle_join_call(data):
    user_id = _socket_user_map.get(request.sid)
    room_code = data.get("room_code")
    name = data.get("name", "Participant")
    if not user_id or not room_code:
        return

    join_room(f"call_{room_code}")
    existing = list(_call_rooms.get(room_code, set()))
    _call_rooms.setdefault(room_code, set()).add(user_id)

    # tell the newcomer who is already in the room, so they can initiate offers
    emit("existing_peers", {"peers": existing})
    # tell everyone already there that a new peer joined
    emit("peer_joined", {"user_id": user_id, "name": name}, room=f"call_{room_code}", include_self=False)


@socketio.on("webrtc_signal")
def handle_webrtc_signal(data):
    """Relays an SDP offer/answer or ICE candidate to one specific peer."""
    sender_id = _socket_user_map.get(request.sid)
    target_id = data.get("target_id")
    signal = data.get("signal")
    if not sender_id or not target_id or signal is None:
        return
    emit("webrtc_signal", {"sender_id": sender_id, "signal": signal}, room=f"user_{target_id}")


@socketio.on("leave_call")
def handle_leave_call(data):
    user_id = _socket_user_map.get(request.sid)
    room_code = data.get("room_code")
    if not user_id or not room_code:
        return
    leave_room(f"call_{room_code}")
    _call_rooms.get(room_code, set()).discard(user_id)
    emit("peer_left", {"user_id": user_id}, room=f"call_{room_code}", include_self=False)


@socketio.on("call_chat_message")
def handle_call_chat_message(data):
    """Lightweight in-call text chat, separate from the 1:1 DM system —
    broadcast only to people currently on the call, not persisted to DB."""
    user_id = _socket_user_map.get(request.sid)
    room_code = data.get("room_code")
    text = (data.get("message") or "").strip()
    name = data.get("name", "Participant")
    if not user_id or not room_code or not text:
        return
    emit("call_chat_message", {"user_id": user_id, "name": name, "message": text},
         room=f"call_{room_code}")
