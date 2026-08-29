"""
Socket.IO realtime layer for AsperRide.
Event names mirror the frontend socketService so client & server stay aligned.

Rooms:
  ride:<ride_id>   -> everyone tracking a ride (rider + assigned driver)
  driver:<driver_id> -> a single driver's private channel

Client -> Server events:
  join_ride            {ride_id}
  leave_ride           {ride_id}
  driver_location      {ride_id, lat, lng, bearing}
  ride_bid             {ride_id, driver_id, price, eta_min}
  chat_message         {ride_id, from, text}
  ride_status          {ride_id, status}

Server -> Client events:
  driver_moved         {ride_id, lat, lng, bearing}
  new_bid              {ride_id, driver_id, price, eta_min}
  chat_message         {ride_id, from, text, ts}
  status_changed       {ride_id, status}
"""
import socketio
from app.config import settings

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_list if settings.cors_list != ["*"] else "*",
)


def _ride_room(ride_id: str) -> str:
    return f"ride:{ride_id}"


@sio.event
async def connect(sid, environ, auth):
    await sio.emit("connected", {"sid": sid}, to=sid)


@sio.event
async def disconnect(sid):
    pass


@sio.on("join_ride")
async def join_ride(sid, data):
    ride_id = str(data.get("ride_id"))
    await sio.enter_room(sid, _ride_room(ride_id))
    await sio.emit("joined", {"ride_id": ride_id}, to=sid)


@sio.on("leave_ride")
async def leave_ride(sid, data):
    ride_id = str(data.get("ride_id"))
    await sio.leave_room(sid, _ride_room(ride_id))


@sio.on("driver_location")
async def driver_location(sid, data):
    ride_id = str(data.get("ride_id"))
    await sio.emit("driver_moved", {
        "ride_id": ride_id,
        "lat": data.get("lat"),
        "lng": data.get("lng"),
        "bearing": data.get("bearing", 0),
    }, room=_ride_room(ride_id), skip_sid=sid)


@sio.on("ride_bid")
async def ride_bid(sid, data):
    ride_id = str(data.get("ride_id"))
    await sio.emit("new_bid", {
        "ride_id": ride_id,
        "driver_id": data.get("driver_id"),
        "price": data.get("price"),
        "eta_min": data.get("eta_min"),
    }, room=_ride_room(ride_id))


@sio.on("chat_message")
async def chat_message(sid, data):
    import time
    ride_id = str(data.get("ride_id"))
    await sio.emit("chat_message", {
        "ride_id": ride_id,
        "from": data.get("from"),
        "text": data.get("text"),
        "ts": int(time.time() * 1000),
    }, room=_ride_room(ride_id))


@sio.on("ride_status")
async def ride_status(sid, data):
    ride_id = str(data.get("ride_id"))
    await sio.emit("status_changed", {
        "ride_id": ride_id,
        "status": data.get("status"),
    }, room=_ride_room(ride_id))
