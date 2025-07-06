# app/websocket/manager.py
import socketio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",  # Configure for production
    logger=True,
    engineio_logger=True
)

# Connected users storage
connected_users: Dict[str, str] = {}  # session_id -> user_id

@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f'Client {sid} connected')
    await sio.emit('connected', {
        'message': 'Terhubung ke server Lunance',
        'session_id': sid
    }, room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f'Client {sid} disconnected')
    # Remove from connected users
    if sid in connected_users:
        del connected_users[sid]

@sio.event
async def join_user_room(sid, data):
    """Handle user joining their personal room"""
    try:
        user_id = data.get('user_id')
        if user_id:
            room = f"user_{user_id}"
            await sio.enter_room(sid, room)
            connected_users[sid] = user_id
            
            await sio.emit('room_joined', {
                'room': room,
                'message': f'Bergabung ke room personal'
            }, room=sid)
            
            logger.info(f'User {user_id} joined room: {room}')
    except Exception as e:
        logger.error(f'Error joining user room: {e}')

@sio.event
async def leave_user_room(sid, data):
    """Handle user leaving their personal room"""
    try:
        user_id = data.get('user_id')
        if user_id:
            room = f"user_{user_id}"
            await sio.leave_room(sid, room)
            
            await sio.emit('room_left', {
                'room': room,
                'message': f'Keluar dari room personal'
            }, room=sid)
            
            logger.info(f'User {user_id} left room: {room}')
    except Exception as e:
        logger.error(f'Error leaving user room: {e}')

# Helper functions for sending notifications
async def send_budget_update(user_id: str, data: Dict[str, Any]):
    """Send budget update notification to user"""
    room = f"user_{user_id}"
    await sio.emit('budget_updated', {
        'message': 'Budget Anda telah diperbarui',
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)

async def send_expense_notification(user_id: str, data: Dict[str, Any]):
    """Send expense notification to user"""
    room = f"user_{user_id}"
    await sio.emit('expense_notification', {
        'message': 'Pengeluaran baru telah ditambahkan',
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)

async def send_budget_alert(user_id: str, data: Dict[str, Any]):
    """Send budget alert notification to user"""
    room = f"user_{user_id}"
    await sio.emit('budget_alert', {
        'message': f"Peringatan budget: {data.get('alert_message', '')}",
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)

async def send_income_notification(user_id: str, data: Dict[str, Any]):
    """Send income notification to user"""
    room = f"user_{user_id}"
    await sio.emit('income_notification', {
        'message': 'Pendapatan baru telah ditambahkan',
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)

async def send_goal_achievement(user_id: str, data: Dict[str, Any]):
    """Send goal achievement notification to user"""
    room = f"user_{user_id}"
    await sio.emit('goal_achievement', {
        'message': f"Selamat! Anda telah mencapai target: {data.get('goal_name', '')}",
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)