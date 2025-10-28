# 💬 Chat Application - Cloud Edition

O aplicație de chat în timp real construită cu Python, Flask-SocketIO și Tkinter, deployată în cloud.

## 🚀 Caracteristici

- Chat în timp real
- Listă automată cu utilizatori online
- Notificări join/leave
- Istoric mesaje
- Interfață desktop cu Tkinter
- Deploy cloud cu Railway

## 🏗️ Structura Proiectului

chat-app/
├── server/ # Backend Flask-SocketIO
├── client/ # Client Tkinter
└── README.md


## 🛠️ Instalare și Rulare

### Server (Cloud)
1. Deploy automat pe Railway.app
2. Serverul rulează pe: `https://your-app-name.railway.app`

### Client (Local)
```bash
cd client
pip install -r requirements.txt
python chat_client.py