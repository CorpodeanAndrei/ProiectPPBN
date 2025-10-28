import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time
import requests
import json

class ChatClient:
    def __init__(self):
        # SCHIMBĂ ACEST URL CU CEL DIN PLAY-WITH-DOCKER
        self.base_url = "http://ip172-18-0-19-d40gf0k69qi000cqmle0-8080.direct.labs.play-with-docker.com/api/chat"
        self.current_user = ""
        self.last_message_id = 0
        self.running = False
        self.setup_ui()
        
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Chat App - Java EE REST Client")
        self.root.geometry("700x500")
        
        # Login Frame
        self.login_frame = tk.Frame(self.root)
        tk.Label(self.login_frame, text="Server URL:", font=('Arial', 10)).pack(pady=2)
        tk.Label(self.login_frame, text=self.base_url, font=('Arial', 9), fg='gray', wraplength=400).pack(pady=2)
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
        
    def join_server(self, username):
        """Înregistrează utilizatorul pe server"""
        try:
            response = requests.post(
                f"{self.base_url}/join",
                json={"username": username},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Join response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                return True
            elif response.status_code == 409:
                messagebox.showerror("Error", "Username deja folosit!")
                return False
            else:
                messagebox.showerror("Error", f"Eroare server: {response.status_code}\n{response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Nu mă pot conecta la server!")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Eroare: {e}")
            return False
    
    def send_message_to_server(self, text):
        """Trimite mesaj către server"""
        try:
            response = requests.post(
                f"{self.base_url}/send",
                json={
                    "username": self.current_user,
                    "text": text
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Send response: {response.status_code} - {response.text}")
            return response.status_code == 200
                
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def get_updates(self):
        """Verifică mesaje noi de la server"""
        try:
            response = requests.get(
                f"{self.base_url}/updates",
                params={
                    "lastMessageId": self.last_message_id,
                    "username": self.current_user
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Get updates error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting updates: {e}")
            return None
    
    def polling_thread(self):
        """Thread pentru polling updates"""
        while self.running:
            try:
                updates = self.get_updates()
                if updates:
                    # Procesează mesaje noi
                    new_messages = updates.get("messages", [])
                    for message in new_messages:
                        self.display_message(message)
                        # Actualizează ultimul ID de mesaj
                        if message["id"] > self.last_message_id:
                            self.last_message_id = message["id"]
                    
                    # Actualizează lista de utilizatori
                    active_users = updates.get("users", [])
                    self.update_users_list(active_users)
                
                time.sleep(2)  # Poll la fiecare 2 secunde
                
            except Exception as e:
                print(f"Error in polling thread: {e}")
                time.sleep(3)
    
    def login(self):
        """Conectare la chat"""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Te rog introdu un nume de utilizator!")
            return
        
        if self.join_server(username):
            self.current_user = username
            self.running = True
            self.last_message_id = 0
            
            # Pornește thread-ul de polling
            self.polling_thread_instance = threading.Thread(target=self.polling_thread)
            self.polling_thread_instance.daemon = True
            self.polling_thread_instance.start()
            
            # Schimbă interfața
            self.login_frame.pack_forget()
            self.chat_frame.pack(fill='both', expand=True)
            self.status_label.config(text=f"Conectat ca: {username}")
            self.add_system_message("✅ Conectat la server")
    
    def logout(self):
        """Deconectare din chat"""
        self.running = False
        
        # Anunță serverul că pleci
        if self.current_user:
            try:
                requests.post(
                    f"{self.base_url}/leave",
                    json={"username": self.current_user},
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )
            except:
                pass  # Ignoră erorile la deconectare
        
        self.current_user = ""
        self.chat_frame.pack_forget()
        self.login_frame.pack(pady=50)
        self.messages_area.config(state='normal')
        self.messages_area.delete(1.0, tk.END)
        self.messages_area.config(state='disabled')
        self.users_listbox.delete(0, tk.END)
    
    def send_message(self):
        """Trimite mesaj"""
        message_text = self.message_entry.get().strip()
        if message_text and self.running:
            if self.send_message_to_server(message_text):
                self.message_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Nu s-a putut trimite mesajul!")
    
    def display_message(self, message_data):
        """Afișează un mesaj în chat"""
        self.messages_area.config(state='normal')
        username = message_data.get("username", "Unknown")
        text = message_data.get("text", "")
        timestamp = message_data.get("timestamp", "")[:19]
        
        self.messages_area.insert(tk.END, f"[{timestamp}] {username}: {text}\n")
        self.messages_area.see(tk.END)
        self.messages_area.config(state='disabled')
    
    def add_system_message(self, msg):
        """Adaugă un mesaj de sistem"""
        self.messages_area.config(state='normal')
        self.messages_area.insert(tk.END, f"⚡ {msg}\n")
        self.messages_area.see(tk.END)
        self.messages_area.config(state='disabled')
    
    def update_users_list(self, users):
        """Actualizează lista de utilizatori"""
        self.users_listbox.delete(0, tk.END)
        for user in users:
            self.users_listbox.insert(tk.END, user)
    
    def run(self):
        """Rulează aplicația"""
        self.root.mainloop()

if __name__ == "__main__":
    client = ChatClient()
    client.run()