import os
import shutil
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import socket

class FTPClientGUI:
    def __init__(self, root):
        """Initialize the FTP Client GUI."""
        self.root = root
        self.root.title("Send File or Folder via FTP")

        # Host Entry
        self.host_label = tk.Label(root, text="Host:")
        self.host_label.grid(row=0, column=0, sticky="e")
        self.host_entry = tk.Entry(root)
        self.host_entry.grid(row=0, column=1, padx=10, pady=5)
        self.host_entry.insert(0, "127.0.0.1")

        # Port Entry
        self.port_label = tk.Label(root, text="Port:")
        self.port_label.grid(row=1, column=0, sticky="e")
        self.port_entry = tk.Entry(root)
        self.port_entry.grid(row=1, column=1, padx=10, pady=5)
        self.port_entry.insert(0, "21")

        # Username Entry
        self.username_label = tk.Label(root, text="Username:")
        self.username_label.grid(row=2, column=0, sticky="e")
        self.username_entry = tk.Entry(root)
        self.username_entry.grid(row=2, column=1, padx=10, pady=5)

        # Password Entry
        self.password_label = tk.Label(root, text="Password:")
        self.password_label.grid(row=3, column=0, sticky="e")
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=5)

        # File/Folder Path Entry
        self.file_path_label = tk.Label(root, text="Folder Path:")
        self.file_path_label.grid(row=4, column=0, sticky="e")
        self.selected_path_entry = tk.Entry(root)
        self.selected_path_entry.grid(row=4, column=1, padx=10, pady=5)
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_file_or_folder)
        self.browse_button.grid(row=4, column=2, padx=10, pady=5, sticky="e")

        # Send Button
        self.send_button = tk.Button(root, text="Send File", command=self.send_file)
        self.send_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

    def browse_file_or_folder(self):
        """Open a file dialog to browse and select a file or folder."""
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            self.selected_path_entry.delete(0, tk.END)
            self.selected_path_entry.insert(0, folder_path)

    def send_file(self):
        """Send the selected file or folder via FTP."""
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        username = self.username_entry.get()
        password = self.password_entry.get()
        selected_path = self.selected_path_entry.get()

        # Check if username and password are provided
        if not all([username, password]):
            tk.messagebox.showerror("Error", "Please fill all fields")
            return

        # Check if a file or folder is selected
        if not selected_path:
            tk.messagebox.showerror("Error", "Please select a file or folder")
            return

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((host, port))
            client_socket.sendall((username + "\r\n").encode())
            response = client_socket.recv(1024).decode()

            client_socket.sendall((password + "\r\n").encode())
            response = client_socket.recv(1024).decode()

            if "User logged in" in response:
                try:
                   
                   # Get the desktop backup directory path
                    desktop_backup_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'Backup')
                    destination_folder = os.path.join(desktop_backup_path, username)

                    if not os.path.exists(destination_folder):
                        os.makedirs(destination_folder)
                    if os.path.isfile(selected_path):
                        shutil.copy(selected_path, destination_folder)
                    elif os.path.isdir(selected_path):
                        shutil.copytree(selected_path, os.path.join(destination_folder, os.path.basename(selected_path)))

                    tk.messagebox.showinfo("Success", "File or folder sent successfully")
                except Exception as e:
                    tk.messagebox.showerror("Error", f"An error occurred: {e}")
                return
            elif "Invalid password" in response:
                tk.messagebox.showinfo("Error", response)
                return
            else:
                tk.messagebox.showinfo("Error", "Invalid username")
                return

        except Exception as e:
            print("Error:", e)
            messagebox.showerror("Error", f"Failed to send file: {e}")
            return
        finally:
            client_socket.close()

def main():
    root = tk.Tk()
    ftp_client_gui = FTPClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
