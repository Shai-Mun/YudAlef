import socket
import tkinter as tk
from tkinter import messagebox
import enc_utils

class SQLClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Client GUI - Secured")
        self.root.geometry("450x650")

        self.encryption_key = ""
        self.cli_s = socket.socket()

        # Connect and exchange keys
        try:
            self.cli_s.connect(("127.0.0.1", 33445))
            self.encryption_key = enc_utils.dph_cli(self.cli_s)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server:\n{e}")
            # Schedule window destruction safely without crashing mainloop
            self.root.after(10, self.root.destroy)
            return

        # Bind closing handler ONLY if connection succeeds
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.build_login_frame()
        self.build_main_frame()
        self.main_frame.pack_forget()

    def on_closing(self):
        try:
            self.cli_s.close()
        except Exception:
            pass
        self.root.destroy()

    def build_login_frame(self):
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0, pady=5)
        self.login_user = tk.Entry(self.login_frame)
        self.login_user.grid(row=0, column=1, pady=5)

        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0, pady=5)
        self.login_pass = tk.Entry(self.login_frame, show="*")
        self.login_pass.grid(row=1, column=1, pady=5)

        # Split the buttons across columns 0 and 1
        tk.Button(self.login_frame, text="Login", command=self.attempt_login).grid(row=2, column=0, pady=10)
        tk.Button(self.login_frame, text="Register", command=self.open_register_window).grid(row=2, column=1, pady=10)

    def build_main_frame(self):
        self.main_frame = tk.Frame(self.root)

        self.entries = {}
        fields = ["Username", "Password", "First Name", "Last Name", "Address", "Phone", "Email"]

        for idx, field in enumerate(fields):
            tk.Label(self.main_frame, text=field + ":").grid(row=idx, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(self.main_frame, width=30)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            self.entries[field] = entry

        button_frame = tk.Frame(self.main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)

        tk.Button(button_frame, text="Insert User", command=self.insert_user, width=12).grid(row=0, column=0, padx=5,
                                                                                             pady=5)
        tk.Button(button_frame, text="Update User", command=self.update_user, width=12).grid(row=0, column=1, padx=5,
                                                                                             pady=5)
        tk.Button(button_frame, text="Delete User", command=self.delete_user, width=12).grid(row=1, column=0, padx=5,
                                                                                             pady=5)
        tk.Button(button_frame, text="Get All Users", command=self.get_users, width=12).grid(row=1, column=1, padx=5,
                                                                                             pady=5)

        tk.Label(self.main_frame, text="Server Response:").grid(row=len(fields) + 1, column=0, columnspan=2, sticky="w",
                                                                padx=10)
        self.console = tk.Text(self.main_frame, height=10, width=50, state="disabled")
        self.console.grid(row=len(fields) + 2, column=0, columnspan=2, padx=10, pady=5)

    def open_register_window(self):
        reg_win = tk.Toplevel(self.root)
        reg_win.title("Register New User")
        reg_win.geometry("350x350")

        reg_entries = {}
        fields = ["Username", "Password", "First Name", "Last Name", "Address", "Phone", "Email"]

        # Build entry fields matching the main frame structure
        for idx, field in enumerate(fields):
            tk.Label(reg_win, text=field + ":").grid(row=idx, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(reg_win, width=30)
            if field == "Password":
                entry.config(show="*")
            entry.grid(row=idx, column=1, padx=10, pady=5)
            reg_entries[field] = entry

        def submit_registration():
            # Format matches your existing insert_user method
            data = f"INSUSR|{reg_entries['Username'].get()}|{reg_entries['Password'].get()}|{reg_entries['First Name'].get()}|{reg_entries['Last Name'].get()}|{reg_entries['Address'].get()}|{reg_entries['Phone'].get()}|{reg_entries['Email'].get()}"

            try:
                # Encrypt and send using the established connection and key
                ct, iv = enc_utils.aes_cbc_encrypt(data.encode(), self.encryption_key)
                enc_utils.send_msg(self.cli_s, iv + ct)

                resp_enc = enc_utils.recv_msg(self.cli_s)
                if not resp_enc:
                    messagebox.showerror("Error", "Server disconnected.", parent=reg_win)
                    return

                iv_resp, ct_resp = resp_enc[:16], resp_enc[16:]
                response = enc_utils.aes_cbc_decrypt(ct_resp, iv_resp, self.encryption_key).decode()

                messagebox.showinfo("Server Response", response, parent=reg_win)
                if "OK" in response or "Success" in response:  # Adjust based on your server's success message
                    reg_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Registration failed: {e}", parent=reg_win)

        tk.Button(reg_win, text="Submit", command=submit_registration).grid(row=len(fields), column=0, columnspan=2,
                                                                            pady=15)

    def attempt_login(self):
        user = self.login_user.get()
        pwd = self.login_pass.get()

        plaintext_msg = f"LOGIN|{user}|{pwd}"
        print(f"Client Sending (Plaintext): {plaintext_msg}")

        ct, iv = enc_utils.aes_cbc_encrypt(plaintext_msg.encode(), self.encryption_key)
        enc_utils.send_msg(self.cli_s, iv + ct)

        resp_enc = enc_utils.recv_msg(self.cli_s)
        iv_resp, ct_resp = resp_enc[:16], resp_enc[16:]
        resp = enc_utils.aes_cbc_decrypt(ct_resp, iv_resp, self.encryption_key).decode()

        print(f"Client Received (Plaintext): {resp}")

        if resp == "LOGIN_OK":
            self.login_frame.pack_forget()
            self.main_frame.pack(pady=10)
        else:
            messagebox.showerror("Error", "Invalid Login")

    def log_response(self, text):
        self.console.config(state="normal")
        self.console.insert(tk.END, text + "\n")
        self.console.see(tk.END)
        self.console.config(state="disabled")

    def send_and_receive(self, data):
        try:
            ct, iv = enc_utils.aes_cbc_encrypt(data.encode(), self.encryption_key)
            enc_utils.send_msg(self.cli_s, iv + ct)

            resp_enc = enc_utils.recv_msg(self.cli_s)
            if not resp_enc:
                self.log_response("Error: Server disconnected.")
                return

            iv_resp, ct_resp = resp_enc[:16], resp_enc[16:]
            response = enc_utils.aes_cbc_decrypt(ct_resp, iv_resp, self.encryption_key)
            self.log_response(f"Got>> {response.decode()}")
        except Exception as e:
            self.log_response(f"Socket Error: {e}")

    def insert_user(self):
        data = f"INSUSR|{self.entries['Username'].get()}|{self.entries['Password'].get()}|{self.entries['First Name'].get()}|{self.entries['Last Name'].get()}|{self.entries['Address'].get()}|{self.entries['Phone'].get()}|{self.entries['Email'].get()}"
        self.send_and_receive(data)

    def update_user(self):
        data = f"UPDUSR|{self.entries['Username'].get()}|{self.entries['Password'].get()}|{self.entries['First Name'].get()}|{self.entries['Last Name'].get()}|{self.entries['Address'].get()}|{self.entries['Phone'].get()}|{self.entries['Email'].get()}|0"
        self.send_and_receive(data)

    def delete_user(self):
        data = f"DELUSR|{self.entries['Username'].get()}"
        self.send_and_receive(data)

    def get_users(self):
        self.send_and_receive("GETUSR")


if __name__ == "__main__":
    root = tk.Tk()
    app = SQLClientGUI(root)
    root.mainloop()