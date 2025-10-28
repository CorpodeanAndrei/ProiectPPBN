from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret!')
CORS(app)

# FORȚEAZĂ POLLING pentru Play-with-Docker
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',  # Schimbă de la 'eventlet'
    logger=True,
    engineio_logger=True,
    transports=['polling', 'websocket']  # Adaugă polling primul
)

users = []
messages = []

@app.route('/')
def index():
    return {
        "status": "online", 
        "message": "Chat Server is running!",
        "users_online": len(users),
        "total_messages": len(messages)
    }

@app.route('/health')
def health():
    return {"status": "healthy"}

@socketio.on('connect')
def handle_connect():
    print('Client connected:', request.sid)
    emit('connected', {'message': 'Connected to server!'})

@socketio.on('disconnect')
def handle_disconnect():
    user = next((u for u in users if u['sid'] == request.sid), None)
    if user:
        users[:] = [u for u in users if u['sid'] != request.sid]
        emit('user_left', {'username': user['username']}, broadcast=True)
        emit('users_update', {'users': [u['username'] for u in users]}, broadcast=True)

@socketio.on('join')
def handle_join(data):
    username = data['username']
    
    if any(u['username'] == username for u in users):
        emit('join_error', {'message': 'Username already taken'})
        return
    
    user_data = {'sid': request.sid, 'username': username}
    users.append(user_data)
    
    emit('user_joined', {'username': username}, broadcast=True)
    emit('users_update', {'users': [u['username'] for u in users]}, broadcast=True)
    emit('message_history', {'messages': messages[-50:]})

@socketio.on('send_message')
def handle_message(data):
    user = next((u for u in users if u['sid'] == request.sid), None)
    if user:
        message_data = {
            'id': len(messages) + 1,
            'username': user['username'],
            'text': data['text'],
            'timestamp': datetime.datetime.now().strftime('%H:%M:%S')
        }
        messages.append(message_data)
        emit('new_message', message_data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    print(f"🚀 Server running on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)