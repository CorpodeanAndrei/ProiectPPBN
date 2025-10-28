import tkinter as tk
from tkinter import scrolledtext, messagebox
import socketio
import requests

class ChatClient:
    def __init__(self):
        # FORȚEAZĂ POLLING pentru Play-with-Docker
        self.sio = socketio.Client(engineio_logger=True)
        self.current_user = ""
        # SCHIMBĂ CU URL-UL TĂU REAL din Play-with-Docker
        self.server_url = "http://ip172-18-0-86-d409j4ol2o9000bn6hig-5000.direct.labs.play-with-docker.com"  # ⚠️ SCHIMBĂ ASTA
        self.setup_socket_events()
        
        self.root = tk.Tk()
        self.root.title("Chat App - Docker Cloud")
        self.root.geometry("700x500")
        self.setup_ui()
        
    def setup_socket_events(self):
        @self.sio.event
        def connect():
            print("✅ Connected to server")
            self.add_system_message("✅ Connected to server")
            
        @self.sio.event
        def connect_error(data):
            print("❌ Connection error:", data)
            self.add_system_message("❌ Connection failed - trying polling only")
            # Reîncearcă doar cu polling
            self.retry_with_polling_only()
            
        @self.sio.event
        def disconnect():
            self.add_system_message("❌ Disconnected from server")
            
        @self.sio.event
        def user_joined(data):
            self.add_system_message(f"👋 {data['username']} joined")
            
        @self.sio.event
        def user_left(data):
            self.add_system_message(f"👋 {data['username']} left")
            
        @self.sio.event
        def users_update(data):
            self.update_users_list(data['users'])
            
        @self.sio.event
        def new_message(data):
            self.display_message(data)
            
        @self.sio.event
        def message_history(data):
            for msg in data['messages']:
                self.display_message(msg)
    
    def retry_with_polling_only(self):
        """Reîncearcă conexiunea folosind doar polling"""
        try:
            if self.sio.connected:
                self.sio.disconnect()
            
            # Forțează doar polling
            self.sio.connect(self.server_url, transports=['polling'])
            if self.current_user:
                self.sio.emit('join', {'username': self.current_user})
                
        except Exception as e:
            print("Polling also failed:", e)
            self.add_system_message("❌ Cannot connect to server")
    
    def setup_ui(self):
        # Login Frame
        self.login_frame = tk.Frame(self.root)
        tk.Label(self.login_frame, text="Server: " + self.server_url, 
                font=('Arial', 9), fg='gray').pack(pady=5)
        tk.Label(self.login_frame, text="Username:", font=('Arial', 12)).pack(pady=5)
        self.username_entry = tk.Entry(self.login_frame, font=('Arial', 12), width=20)
        self.username_entry.pack(pady=5)
        self.username_entry.bind('<Return>', lambda e: self.login())
        tk.Button(self.login_frame, text="Join Chat", command=self.login, 
                 font=('Arial', 12), bg='green', fg='white').pack(pady=10)
        self.login_frame.pack(pady=50)
        
        # Chat Frame
        self.chat_frame = tk.Frame(self.root)
        
        # Header
        header = tk.Frame(self.chat_frame)
        self.status_label = tk.Label(header, text="Not connected", font=('Arial', 10))
        self.status_label.pack(side='left')
        tk.Button(header, text="Leave", command=self.logout, bg='red', fg='white').pack(side='right')
        header.pack(fill='x', pady=5)
        
        # Main content
        main_content = tk.Frame(self.chat_frame)
        
        # Users list
        users_frame = tk.Frame(main_content)
        tk.Label(users_frame, text="Online Users", font=('Arial', 11, 'bold')).pack()
        self.users_listbox = tk.Listbox(users_frame, width=20, height=15)
        self.users_listbox.pack(fill='both', expand=True)
        users_frame.pack(side='left', fill='y', padx=5)
        
        # Chat area
        chat_frame = tk.Frame(main_content)
        self.messages_area = scrolledtext.ScrolledText(chat_frame, width=50, height=15, state='disabled')
        self.messages_area.pack(fill='both', expand=True)
        
        input_frame = tk.Frame(chat_frame)
        self.message_entry = tk.Entry(input_frame, width=40)
        self.message_entry.pack(side='left', fill='x', expand=True)
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        tk.Button(input_frame, text="Send", command=self.send_message).pack(side='right')
        input_frame.pack(fill='x', pady=5)
        
        chat_frame.pack(side='right', fill='both', expand=True)
        main_content.pack(fill='both', expand=True)
        
    def login(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter username")
            return
            
        try:
            # Încearcă mai întâi cu polling
            self.sio.connect(self.server_url, transports=['polling', 'websocket'])
            self.current_user = username
            self.sio.emit('join', {'username': username})
            self.login_frame.pack_forget()
            self.chat_frame.pack(fill='both', expand=True)
            self.status_label.config(text=f"Connected as: {username}")
        except Exception as e:
            messagebox.showerror("Connection Error", 
                               f"Cannot connect to server.\n\nError: {e}\n\n"
                               f"Server URL: {self.server_url}")
    
    def logout(self):
        if self.sio.connected:
            self.sio.disconnect()
        self.chat_frame.pack_forget()
        self.login_frame.pack(pady=50)
        self.messages_area.config(state='normal')
        self.messages_area.delete(1.0, tk.END)
        self.messages_area.config(state='disabled')
        self.users_listbox.delete(0, tk.END)
    
    def send_message(self):
        msg = self.message_entry.get().strip()
        if msg and self.sio.connected:
            self.sio.emit('send_message', {'text': msg})
            self.message_entry.delete(0, tk.END)
    
    def display_message(self, data):
        self.messages_area.config(state='normal')
        self.messages_area.insert(tk.END, f"[{data['timestamp']}] {data['username']}: {data['text']}\n")
        self.messages_area.see(tk.END)
        self.messages_area.config(state='disabled')
    
    def add_system_message(self, msg):
        self.messages_area.config(state='normal')
        self.messages_area.insert(tk.END, f"⚡ {msg}\n")
        self.messages_area.see(tk.END)
        self.messages_area.config(state='disabled')
    
    def update_users_list(self, users):
        self.users_listbox.delete(0, tk.END)
        for user in users:
            self.users_listbox.insert(tk.END, user)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = ChatClient()
    client.run()