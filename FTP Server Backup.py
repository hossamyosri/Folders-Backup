import os
import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

class FTPServerGUI:
    def __init__(self, root):
        """Initialize FTP Server GUI."""
        self.root = root
        self.root.title("FTP Server Settings")
        self.root.geometry("400x400")

        self.user_folders = {}

        # Host entry
        self.host_label = tk.Label(root, text="Host:", font=("Arial", 12))
        self.host_label.grid(row=0, column=0, padx=10, pady=5)
        self.host_entry = tk.Entry(root, font=("Arial", 12))
        self.host_entry.grid(row=0, column=1, padx=10, pady=5)
        self.host_entry.insert(0, "127.0.0.1")

        # Port entry
        self.port_label = tk.Label(root, text="Port:", font=("Arial", 12))
        self.port_label.grid(row=1, column=0, padx=10, pady=5)
        self.port_entry = tk.Entry(root, font=("Arial", 12))
        self.port_entry.grid(row=1, column=1, padx=10, pady=5)
        self.port_entry.insert(0, "21")

        # User list
        self.user_list_label = tk.Label(root, text="User List:", font=("Arial", 12))
        self.user_list_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        self.user_list_text = tk.Text(root, width=30, height=10, font=("Arial", 13))
        self.user_list_text.grid(row=3, column=0, columnspan=2, padx=10, pady=5)
        self.user_list_text.config(state=tk.DISABLED)

        # Add user button
        self.add_user_button = tk.Button(root, text="Add User", command=self.add_user, font=("Arial", 12))
        self.add_user_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        # Connect button
        self.connect_button = tk.Button(root, text="Connect", command=self.start_ftp_server, font=("Arial", 12))
        self.connect_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        self.users = {}

    def add_user(self):
        """Add a new user."""
        username = tk.simpledialog.askstring("Add User", "Username:")
        if username:
            password = tk.simpledialog.askstring("Add User", "Password:", show='*')
            if password:
                self.users[username] = password
                self.user_list_text.config(state=tk.NORMAL)
                self.user_list_text.insert(tk.END, f"User: {username} | Password: {password}\n")
                self.user_list_text.config(state=tk.DISABLED)
                print(f"New user added: {username}")
                self.create_user_folder(username)

    def start_ftp_server(self):
        """Start the FTP server."""
        host = self.host_entry.get()
        port = int(self.port_entry.get())

        try:
            # Start the FTP server in a new thread
            server_thread = threading.Thread(target=self.run_ftp_server, args=(host, port))
            server_thread.start()
        except Exception as e:
            print(f"An error occurred while starting the server: {e}")

    def run_ftp_server(self, host, port):
        """Run the FTP server."""
        try:
            # Setup the server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen(1)
            print(f"Server is ready to listen on port {port}")

            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Connection received from {client_address}")

                # Handle FTP requests
                ftp_handler = FTPHandler(client_socket, self.users)
                ftp_handler.handle()

        except Exception as e:
            print(f"An error occurred while running the server: {e}")

        finally:
            server_socket.close()

    def create_user_folder(self, username):
        """Create a folder for the user."""
        desktop_backup_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'Backup')
        user_folder = os.path.join(desktop_backup_path, username)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        self.user_folders[username] = user_folder


class FTPHandler:
    def __init__(self, client_socket, users):
        self.client_socket = client_socket
        self.users = users

    def handle(self):
        """Handle FTP requests."""
        try:
            self.client_socket.sendall(" FTP server ready\r\n".encode())

            # Authenticate user
            username = self.client_socket.recv(1024).decode().strip()
            if username not in self.users:
                self.client_socket.sendall("Invalid username\r\n".encode())
                return

            password = self.client_socket.recv(1024).decode().strip()
            if self.users[username] != password:
                self.client_socket.sendall("Invalid password\r\n".encode())
                return

            self.client_socket.sendall("User logged in\r\n".encode())

        except Exception as e:
            print(f"An error occurred while processing the request: {e}")

        finally:
            self.client_socket.close()

def main():
    root = tk.Tk()
    ftp_server_gui = FTPServerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

