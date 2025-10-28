import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socketio
import threading
import json
from datetime import datetime

class ChatClient:
    def __init__(self):
        self.sio = socketio.Client()
        self.current_user = ""
        self.server_url = "https://your-app-name.railway.app"  # Înlocuiește cu URL-ul tău
        self.setup_socket_events()
        
        # Creare fereastra principala
        self.root = tk.Tk()
        self.root.title("Chat Application - Cloud Edition")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        self.setup_login_screen()
        self.setup_chat_screen()
        
        self.show_login_screen()
    
    def setup_socket_events(self):
        """Configurează event-urile Socket.IO"""
        @self.sio.event
        def connect():
            print("Conectat la server cloud")
            self.add_system_message("✅ Conectat la serverul cloud")
        
        @self.sio.event
        def disconnect():
            print("Deconectat de la server")
            self.add_system_message("❌ Deconectat de la server")
        
        @self.sio.event
        def connect_error(data):
            print("Eroare de conectare:", data)
            self.add_system_message("❌ Eroare de conectare la server")
        
        @self.sio.event
        def user_joined(data):
            self.add_system_message(f"👋 {data['username']} s-a alăturat chat-ului")
        
        @self.sio.event
        def user_left(data):
            self.add_system_message(f"👋 {data['username']} a părăsit chat-ul")
        
        @self.sio.event
        def users_update(data):
            self.update_users_list(data['users'])
        
        @self.sio.event
        def new_message(data):
            self.display_message(data)
        
        @self.sio.event
        def message_history(data):
            for message in data['messages']:
                self.display_message(message)
    
    def setup_login_screen(self):
        """Setup ecranul de login"""
        self.login_frame = tk.Frame(self.root, bg='#2c3e50')
        
        # Titlu
        title_label = tk.Label(
            self.login_frame,
            text="💬 Chat Application - Cloud",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(pady=30)
        
        # Server info
        server_label = tk.Label(
            self.login_frame,
            text=f"Server: {self.server_url}",
            font=('Arial', 10),
            fg='#bdc3c7',
            bg='#2c3e50'
        )
        server_label.pack(pady=10)
        
        # Frame pentru input
        input_frame = tk.Frame(self.login_frame, bg='#2c3e50')
        input_frame.pack(pady=20)
        
        # Label și input pentru username
        username_label = tk.Label(
            input_frame,
            text="Nume de utilizator:",
            font=('Arial', 12),
            fg='white',
            bg='#2c3e50'
        )
        username_label.grid(row=0, column=0, padx=5, pady=10, sticky='e')
        
        self.username_entry = tk.Entry(
            input_frame,
            font=('Arial', 12),
            width=20
        )
        self.username_entry.grid(row=0, column=1, padx=5, pady=10)
        self.username_entry.bind('<Return>', lambda e: self.login())
        
        # Buton login
        login_btn = tk.Button(
            input_frame,
            text="Intră în Chat",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            command=self.login,
            width=15,
            height=1
        )
        login_btn.grid(row=1, column=0, columnspan=2, pady=20)
    
    def setup_chat_screen(self):
        """Setup ecranul principal de chat"""
        self.chat_frame = tk.Frame(self.root, bg='#2c3e50')
        
        # Header cu buton de logout
        header_frame = tk.Frame(self.chat_frame, bg='#34495e')
        header_frame.pack(fill='x', padx=10, pady=10)
        
        self.user_label = tk.Label(
            header_frame,
            text="",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#34495e'
        )
        self.user_label.pack(side='left')
        
        logout_btn = tk.Button(
            header_frame,
            text="Ieși din Chat",
            font=('Arial', 10),
            bg='#e74c3c',
            fg='white',
            command=self.logout
        )
        logout_btn.pack(side='right')
        
        # Main content frame
        main_frame = tk.Frame(self.chat_frame, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Lista utilizatori (stânga)
        users_frame = tk.Frame(main_frame, bg='#34495e')
        users_frame.pack(side='left', fill='y', padx=(0, 10))
        
        users_label = tk.Label(
            users_frame,
            text="👥 Utilizatori Online",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#34495e'
        )
        users_label.pack(pady=10)
        
        # Listbox pentru utilizatori
        self.users_listbox = tk.Listbox(
            users_frame,
            font=('Arial', 10),
            bg='#2c3e50',
            fg='white',
            width=20,
            height=20
        )
        self.users_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Zona de chat (dreapta)
        chat_area_frame = tk.Frame(main_frame, bg='#2c3e50')
        chat_area_frame.pack(side='right', fill='both', expand=True)
        
        # Mesaje
        messages_label = tk.Label(
            chat_area_frame,
            text="💬 Mesaje",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        messages_label.pack(anchor='w')
        
        # Scrolled text pentru mesaje
        self.messages_text = scrolledtext.ScrolledText(
            chat_area_frame,
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#2c3e50',
            width=50,
            height=20,
            state='disabled'
        )
        self.messages_text.pack(fill='both', expand=True, pady=5)
        
        # Input frame
        input_frame = tk.Frame(chat_area_frame, bg='#2c3e50')
        input_frame.pack(fill='x', pady=10)
        
        self.message_entry = tk.Entry(
            input_frame,
            font=('Arial', 12),
            bg='white',
            fg='#2c3e50'
        )
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        send_btn = tk.Button(
            input_frame,
            text="Trimite",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            command=self.send_message
        )
        send_btn.pack(side='right')
    
    def show_login_screen(self):
        """Arată ecranul de login"""
        self.chat_frame.pack_forget()
        self.login_frame.pack(fill='both', expand=True)
    
    def show_chat_screen(self):
        """Arată ecranul principal de chat"""
        self.login_frame.pack_forget()
        self.chat_frame.pack(fill='both', expand=True)
    
    def login(self):
        """Conectare la chat"""
        username = self.username_entry.get().strip()
        
        if not username:
            messagebox.showerror("Eroare", "Te rog introdu un nume de utilizator!")
            return
        
        try:
            # Conectare la server CLOUD
            self.sio.connect(self.server_url)
            self.current_user = username
            
            # Trimite cerere de join
            self.sio.emit('join', {'username': username})
            
            # Actualizează interfața
            self.user_label.config(text=f'Bun venit, {username}! (Cloud)')
            self.show_chat_screen()
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Nu mă pot conecta la serverul cloud: {e}")
    
    def logout(self):
        """Deconectare din chat"""
        if self.sio.connected:
            self.sio.disconnect()
        
        self.current_user = ""
        self.username_entry.delete(0, tk.END)
        self.messages_text.config(state='normal')
        self.messages_text.delete(1.0, tk.END)
        self.messages_text.config(state='disabled')
        self.users_listbox.delete(0, tk.END)
        
        self.show_login_screen()
    
    def send_message(self):
        """Trimite mesaj"""
        message = self.message_entry.get().strip()
        
        if message and self.sio.connected:
            self.sio.emit('send_message', {'text': message})
            self.message_entry.delete(0, tk.END)
    
    def display_message(self, message_data):
        """Afișează un mesaj în chat"""
        self.messages_text.config(state='normal')
        
        # Formatare mesaj
        timestamp = message_data.get('timestamp', '')
        username = message_data.get('username', 'Unknown')
        text = message_data.get('text', '')
        
        # Adaugă mesajul
        self.messages_text.insert(tk.END, f"[{timestamp}] {username}: {text}\n")
        
        # Scroll la ultimul mesaj
        self.messages_text.see(tk.END)
        self.messages_text.config(state='disabled')
    
    def add_system_message(self, message):
        """Adaugă un mesaj de sistem"""
        self.messages_text.config(state='normal')
        self.messages_text.insert(tk.END, f"⚡ {message}\n")
        self.messages_text.see(tk.END)
        self.messages_text.config(state='disabled')
    
    def update_users_list(self, users):
        """Actualizează lista de utilizatori"""
        self.users_listbox.delete(0, tk.END)
        
        for user in users:
            self.users_listbox.insert(tk.END, user)
            
            # Marchează utilizatorul curent
            if user == self.current_user:
                self.users_listbox.itemconfig(tk.END, {'bg': '#3498db', 'fg': 'white'})
    
    def run(self):
        """Rulează aplicația"""
        self.root.mainloop()

if __name__ == "__main__":
    print("Pornire client chat...")
    print("Asigură-te că serverul cloud rulează!")
    
    client = ChatClient()
    client.run()