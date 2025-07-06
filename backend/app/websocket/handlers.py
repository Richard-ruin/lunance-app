
# app/websocket/handlers.py
from flask_socketio import emit, join_room, leave_room
from app import socketio
import logging

logger = logging.getLogger(__name__)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connected', {'message': 'Terhubung ke server Lunance'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

@socketio.on('join_room')
def handle_join_room(data):
    """Handle client joining room"""
    room = data.get('room')
    if room:
        join_room(room)
        emit('room_joined', {'room': room, 'message': f'Bergabung ke room {room}'})
        logger.info(f'Client joined room: {room}')

@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle client leaving room"""
    room = data.get('room')
    if room:
        leave_room(room)
        emit('room_left', {'room': room, 'message': f'Keluar dari room {room}'})
        logger.info(f'Client left room: {room}')

@socketio.on('budget_update')
def handle_budget_update(data):
    """Handle budget update notifications"""
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        emit('budget_updated', {
            'message': 'Budget Anda telah diperbarui',
            'data': data
        }, room=room)

@socketio.on('expense_added')
def handle_expense_added(data):
    """Handle new expense notifications"""
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        emit('expense_notification', {
            'message': 'Pengeluaran baru telah ditambahkan',
            'data': data
        }, room=room)

@socketio.on('budget_alert')
def handle_budget_alert(data):
    """Handle budget alert notifications"""
    user_id = data.get('user_id')
    if user_id:
        room = f"user_{user_id}"
        emit('budget_alert', {
            'message': 'Peringatan budget: ' + data.get('alert_message', ''),
            'data': data
        }, room=room)