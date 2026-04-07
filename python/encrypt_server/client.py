"""
=============================================================
  Encrypted Server Client
=============================================================
"""
import os
import base64
import tkinter as tk
from tkinter import ttk
import socket
import traceback
import threading

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

from Crypto.Cipher import AES as _AES
from Crypto.Util.Padding import pad as _pad, unpad as _unpad
from Crypto.Random import get_random_bytes as _rand_bytes

from enc_utils import send_with_size, recv_by_size, dph_cli, rsa_cli

# ── Color palette ─────────────────────────────
BG      = "#1e1e2e"
SURFACE = "#2a2a3e"
ACCENT  = "#7c6af7"
ACCENT2 = "#5a4fcf"
TEXT    = "#cdd6f4"
SUCCESS = "#a6e3a1"
ERROR   = "#f38ba8"
MUTED   = "#6c7086"
WARN    = "#f9e2af"

encryption_key = ""
KEY_FILE = "client_rsa_private.pem"


# ── RSA E2E key management ────────────────────
def load_or_generate_rsa_keys():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )
        print("[RSA] Loaded existing key pair from file")
    else:
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        with open(KEY_FILE, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        print("[RSA] Generated new key pair, saved to file")
    return private_key, private_key.public_key()


def rsa_encrypt_for_peer(public_key, message: str) -> str:
    ct = public_key.encrypt(
        message.encode("utf-8"),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(), label=None)
    )
    return ct.hex()


def rsa_decrypt_from_peer(private_key, hex_ct: str) -> str:
    ct = bytes.fromhex(hex_ct)
    pt = private_key.decrypt(
        ct,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(), label=None)
    )
    return pt.decode("utf-8")


def aes_encrypt_msg(key_bytes: bytes, plaintext: str) -> tuple[str, str]:
    """Returns (iv_hex, ciphertext_hex)"""
    iv     = _rand_bytes(16)
    cipher = _AES.new(key_bytes, _AES.MODE_CBC, iv)
    ct     = cipher.encrypt(_pad(plaintext.encode(), _AES.block_size))
    return iv.hex(), ct.hex()


def aes_decrypt_msg(key_bytes: bytes, iv_hex: str, ct_hex: str) -> str:
    iv     = bytes.fromhex(iv_hex)
    ct     = bytes.fromhex(ct_hex)
    cipher = _AES.new(key_bytes, _AES.MODE_CBC, iv)
    return _unpad(cipher.decrypt(ct), _AES.block_size).decode()


# ── Labeled entry helper ──────────────────────
def labeled_entry(parent, label: str, show: str = "") -> tuple[tk.Frame, tk.Entry]:
    frame = tk.Frame(parent, bg=SURFACE)
    tk.Label(frame, text=label, bg=SURFACE, fg=MUTED,
             font=("Segoe UI", 9)).pack(anchor="w", padx=4)
    entry = tk.Entry(frame, show=show, bg="#1a1a2e", fg=TEXT,
                     insertbackground=TEXT, relief="flat",
                     font=("Segoe UI", 11), bd=4)
    entry.pack(fill="x", padx=4, pady=(0, 6), ipady=4)
    return frame, entry


# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.crypto_var = tk.StringVar(value="DPH")
        self.title("Encrypted Server – Phase A")
        self.geometry("980x660")
        self.configure(bg=BG)
        self.resizable(True, True)

        # E2E RSA
        self.my_private_key, self.my_public_key = load_or_generate_rsa_keys()
        self.peer_public_keys = {}   # {username: public_key_object}
        self.chat_histories  = {}    # {username: [(sender, text), ...]}
        self.logged_in_username  = ""
        self.pending_login_username = ""

        self.session_keys = {}

        self.cli_sock = None
        self._build_ui()

    # ── Build UI ──────────────────────────────
    def _build_ui(self):
        self._build_header()
        center = tk.Frame(self, bg=BG)
        center.pack(fill="both", expand=True, padx=14, pady=10)
        left = tk.Frame(center, bg=BG)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(center, bg=BG, width=300)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)
        self._build_connection_panel(left)
        self._build_tabs(left)
        self._build_right_panel(right)

    # ── Header ────────────────────────────────
    def _build_header(self):
        header = tk.Frame(self, bg=ACCENT2, pady=10)
        header.pack(fill="x")
        tk.Label(header, text="🔐  Encrypted Server Client",
                 bg=ACCENT2, fg="white",
                 font=("Segoe UI", 16, "bold")).pack()

    # ── Connection panel ──────────────────────
    def _build_connection_panel(self, parent):
        frame = tk.LabelFrame(parent, text=" Server Connection ",
                              bg=SURFACE, fg=ACCENT,
                              font=("Segoe UI", 10, "bold"),
                              bd=2, relief="groove")
        frame.pack(fill="x", pady=(0, 10))

        row1 = tk.Frame(frame, bg=SURFACE)
        row1.pack(fill="x", padx=8, pady=4)
        tk.Label(row1, text="Host:", bg=SURFACE, fg=TEXT, font=("Segoe UI", 10)).pack(side="left")
        self.host_entry = tk.Entry(row1, width=14, bg="#1a1a2e", fg=TEXT,
                                   insertbackground=TEXT, relief="flat")
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(side="left", padx=4)
        tk.Label(row1, text="Port:", bg=SURFACE, fg=TEXT, font=("Segoe UI", 10)).pack(side="left")
        self.port_entry = tk.Entry(row1, width=6, bg="#1a1a2e", fg=TEXT,
                                   insertbackground=TEXT, relief="flat")
        self.port_entry.insert(0, "5555")
        self.port_entry.pack(side="left", padx=4)
        self.btn_connect = tk.Button(row1, text="Connect", command=self._on_connect,
                                     bg=ACCENT, fg="white",
                                     font=("Segoe UI", 10, "bold"), padx=12)
        self.btn_connect.pack(side="left", padx=8)
        self.status_lbl = tk.Label(row1, text="● Not Connected", bg=SURFACE, fg=ERROR,
                                   font=("Segoe UI", 10, "bold"))
        self.status_lbl.pack(side="left")

        row2 = tk.Frame(frame, bg=SURFACE)
        row2.pack(fill="x", padx=8, pady=(0, 8))
        tk.Label(row2, text="Method:", bg=SURFACE, fg=TEXT, font=("Segoe UI", 10)).pack(side="left")
        tk.Radiobutton(row2, text="DPH", variable=self.crypto_var, value="DPH",
                       bg=SURFACE, fg=TEXT, selectcolor=BG,
                       activebackground=SURFACE).pack(side="left", padx=10)
        tk.Radiobutton(row2, text="RSA", variable=self.crypto_var, value="RSA",
                       bg=SURFACE, fg=TEXT, selectcolor=BG,
                       activebackground=SURFACE).pack(side="left")

    # ── Tabs ──────────────────────────────────
    def _build_tabs(self, parent):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=SURFACE, foreground=MUTED,
                        font=("Segoe UI", 10), padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT2)],
                  foreground=[("selected", "white")])
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)
        self._build_login_tab()
        self._build_signup_tab()
        self._build_forgot_tab()

    # ── Login tab ─────────────────────────────
    def _build_login_tab(self):
        tab = tk.Frame(self.notebook, bg=SURFACE)
        self.notebook.add(tab, text="  🔑 Login  ")
        inner = tk.Frame(tab, bg=SURFACE)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(inner, text="Sign In to Your Account", bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(0, 14))
        f1, self.login_user = labeled_entry(inner, "Username")
        f1.pack(fill="x", pady=4)
        f2, self.login_pass = labeled_entry(inner, "Password", show="●")
        f2.pack(fill="x", pady=4)
        self.btn_login = tk.Button(inner, text="Login  →", command=self._on_login,
                                   state="disabled", bg=ACCENT, fg="white", relief="flat",
                                   font=("Segoe UI", 11, "bold"), cursor="hand2",
                                   padx=20, pady=6)
        self.btn_login.pack(pady=14)
        tk.Label(inner, text="Forgot password?", bg=SURFACE, fg=ACCENT,
                 font=("Segoe UI", 9, "underline"), cursor="hand2").pack()

    # ── Sign Up tab ───────────────────────────
    def _build_signup_tab(self):
        tab = tk.Frame(self.notebook, bg=SURFACE)
        self.notebook.add(tab, text="  📋 Sign Up  ")
        canvas = tk.Canvas(tab, bg=SURFACE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        inner = tk.Frame(canvas, bg=SURFACE)
        win = canvas.create_window((0, 0), window=inner, anchor="n")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        wrapper = tk.Frame(inner, bg=SURFACE)
        wrapper.pack(padx=60, pady=20)
        tk.Label(wrapper, text="Create a New Account", bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(0, 12))
        fields = [
            ("Username", "", "su_user"), ("Password", "●", "su_pass"),
            ("First Name", "", "su_name"), ("Last Name", "", "su_last"),
            ("Email", "", "su_email"), ("Phone", "", "su_phone"),
        ]
        for label, show, attr in fields:
            f, entry = labeled_entry(wrapper, label, show)
            f.pack(fill="x", pady=3)
            setattr(self, attr, entry)
        tk.Button(wrapper, text="Register  →", command=self._on_signup,
                  bg=SUCCESS, fg="#1e1e2e", relief="flat",
                  font=("Segoe UI", 11, "bold"), cursor="hand2",
                  padx=20, pady=6).pack(pady=14)

    # ── Forgot Password tab ───────────────────
    def _build_forgot_tab(self):
        tab = tk.Frame(self.notebook, bg=SURFACE)
        self.notebook.add(tab, text="  🔒 Forgot Password  ")
        inner = tk.Frame(tab, bg=SURFACE)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(inner, text="Reset Your Password", bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(0, 14))
        f1, self.fp_user  = labeled_entry(inner, "Username")
        f1.pack(fill="x", pady=4)
        f2, self.fp_email = labeled_entry(inner, "Email")
        f2.pack(fill="x", pady=4)
        f3, self.fp_pass  = labeled_entry(inner, "New Password", show="●")
        f3.pack(fill="x", pady=4)
        tk.Button(inner, text="Reset Password  →", command=self._on_forgot,
                  bg="#fab387", fg="#1e1e2e", relief="flat",
                  font=("Segoe UI", 11, "bold"), cursor="hand2",
                  padx=20, pady=6).pack(pady=14)

    # ── Right panel ───────────────────────────
    def _build_right_panel(self, parent):
        # Online Users
        users_frame = tk.LabelFrame(parent, text=" 🟢 Online Users ",
                                    bg=BG, fg=SUCCESS,
                                    font=("Segoe UI", 10, "bold"),
                                    bd=2, relief="groove")
        users_frame.pack(fill="x", pady=(0, 8))
        self.online_count_lbl = tk.Label(users_frame, text="0 online",
                                         bg=BG, fg=MUTED, font=("Segoe UI", 8))
        self.online_count_lbl.pack(anchor="e", padx=6)
        ulf = tk.Frame(users_frame, bg=BG)
        ulf.pack(fill="x", padx=4, pady=(0, 6))
        usb = tk.Scrollbar(ulf)
        usb.pack(side="right", fill="y")
        self.online_box = tk.Listbox(ulf, yscrollcommand=usb.set,
                                     bg="#12121e", fg=SUCCESS,
                                     selectbackground=ACCENT2,
                                     font=("Consolas", 9),
                                     relief="flat", bd=0,
                                     activestyle="none", height=5)
        self.online_box.pack(fill="x")
        usb.config(command=self.online_box.yview)

        # Log / Chat notebook
        right_nb = ttk.Notebook(parent)
        right_nb.pack(fill="both", expand=True)

        log_tab = tk.Frame(right_nb, bg=BG)
        right_nb.add(log_tab, text=" 📋 Log ")
        self._build_log_tab(log_tab)

        chat_tab = tk.Frame(right_nb, bg=SURFACE)
        right_nb.add(chat_tab, text=" 💬 Chat ")
        self._build_chat_tab(chat_tab)

    # ── Log tab ───────────────────────────────
    def _build_log_tab(self, parent):
        log_frame = tk.Frame(parent, bg=BG)
        log_frame.pack(fill="both", expand=True)
        sb = tk.Scrollbar(log_frame)
        sb.pack(side="right", fill="y")
        self.log_box = tk.Listbox(log_frame, yscrollcommand=sb.set,
                                  bg="#12121e", fg=TEXT,
                                  selectbackground=ACCENT2,
                                  font=("Consolas", 9),
                                  relief="flat", bd=0, activestyle="none")
        self.log_box.pack(fill="both", expand=True)
        sb.config(command=self.log_box.yview)
        for msg in ["[--] Waiting for connection...", "[--] Activity will appear here"]:
            self.log_box.insert("end", msg)
        tk.Button(parent, text="Clear Log",
                  command=lambda: self.log_box.delete(0, "end"),
                  bg=MUTED, fg="white", relief="flat",
                  font=("Segoe UI", 9), cursor="hand2").pack(fill="x", pady=(4, 0))

    # ── Chat tab ──────────────────────────────
    def _build_chat_tab(self, parent):
        # Recipient dropdown
        sel = tk.Frame(parent, bg=SURFACE)
        sel.pack(fill="x", padx=6, pady=6)
        tk.Label(sel, text="To:", bg=SURFACE, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left")
        self.chat_target_var = tk.StringVar(value="")
        self.chat_dropdown = ttk.Combobox(sel, textvariable=self.chat_target_var,
                                          state="readonly", font=("Segoe UI", 9), width=16)
        self.chat_dropdown.pack(side="left", fill="x", expand=True, padx=4)
        self.chat_dropdown.bind("<<ComboboxSelected>>", self._on_chat_user_selected)

        # Chat display (Text widget so we can colour-tag messages)
        disp_frame = tk.Frame(parent, bg=BG)
        disp_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        chat_sb = tk.Scrollbar(disp_frame)
        chat_sb.pack(side="right", fill="y")
        self.chat_display = tk.Text(disp_frame, yscrollcommand=chat_sb.set,
                                    bg="#12121e", fg=TEXT,
                                    font=("Consolas", 9),
                                    relief="flat", bd=0,
                                    state="disabled", wrap="word")
        self.chat_display.pack(fill="both", expand=True)
        self.chat_display.tag_config("me",   foreground=ACCENT)
        self.chat_display.tag_config("them", foreground=SUCCESS)
        self.chat_display.tag_config("sys",  foreground=MUTED)
        chat_sb.config(command=self.chat_display.yview)

        # Message entry + Send button
        entry_frame = tk.Frame(parent, bg=SURFACE)
        entry_frame.pack(fill="x", padx=4, pady=4)
        self.chat_entry = tk.Entry(entry_frame, bg="#1a1a2e", fg=TEXT,
                                   insertbackground=TEXT, relief="flat",
                                   font=("Segoe UI", 10))
        self.chat_entry.pack(side="left", fill="x", expand=True,
                             padx=(0, 4), ipady=4)
        self.chat_entry.bind("<Return>", lambda e: self._send_private_msg())
        tk.Button(entry_frame, text="Send", command=self._send_private_msg,
                  bg=ACCENT, fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold"), padx=8).pack(side="right")

    # ── Online users helpers ──────────────────
    def _set_online_users(self, users):
        self.online_box.delete(0, "end")
        for u in users:
            if u:
                self.online_box.insert("end", f"  👤 {u}")
        self._update_online_count()
        self._update_chat_dropdown()

    def _add_online_user(self, username):
        self.online_box.insert("end", f"  👤 {username}")
        self._update_online_count()
        self._update_chat_dropdown()

    def _remove_online_user(self, username):
        for i in range(self.online_box.size()):
            if self.online_box.get(i).strip() == f"👤 {username}":
                self.online_box.delete(i)
                break
        self._update_online_count()
        self._update_chat_dropdown()

    def _update_online_count(self):
        self.online_count_lbl.config(text=f"{self.online_box.size()} online")

    def _update_chat_dropdown(self):
        users = []
        for i in range(self.online_box.size()):
            u = self.online_box.get(i).strip().replace("👤 ", "")
            if u and u != self.logged_in_username:
                users.append(u)
        self.chat_dropdown["values"] = users

    # ── Chat helpers ──────────────────────────
    def _on_chat_user_selected(self, _event=None):
        self._render_chat(self.chat_target_var.get())

    def _render_chat(self, username):
        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", "end")
        history = self.chat_histories.get(username, [])
        if not history:
            self.chat_display.insert("end", "No messages yet.\n", "sys")
        for sender, msg in history:
            if sender == self.logged_in_username:
                self.chat_display.insert("end", f"You: {msg}\n", "me")
            else:
                self.chat_display.insert("end", f"{sender}: {msg}\n", "them")
        self.chat_display.config(state="disabled")
        self.chat_display.see("end")

    def _append_chat_message(self, peer, sender, msg):
        self.chat_histories.setdefault(peer, []).append((sender, msg))
        if self.chat_target_var.get() == peer:
            self._render_chat(peer)

    def _send_private_msg(self):
        target = self.chat_target_var.get()
        msg = self.chat_entry.get().strip()
        if not target or not msg:
            return
        if target not in self.peer_public_keys:
            self._append_chat_message(target, "⚠ system",
                                      "No public key yet — try again in a moment")
            return

        # Make sure we have (or just created) a session key
        self._ensure_session_key(target)

        if target not in self.session_keys:
            self._append_chat_message(target, "⚠ system",
                                      "Session key not ready yet")
            return

        try:
            iv_hex, ct_hex = aes_encrypt_msg(self.session_keys[target], msg)
            send_with_size(self.cli_sock,
                           f"PRIV_MSG~{target}~{iv_hex}~{ct_hex}".encode(),
                           encryption_key)
            self._append_chat_message(target, self.logged_in_username, msg)
            self.chat_entry.delete(0, "end")
        except Exception:
            print(traceback.format_exc())

    # ── Button handlers ───────────────────────
    def _on_connect(self):
        global encryption_key
        host   = self.host_entry.get().strip()
        port   = self.port_entry.get().strip()
        method = self.crypto_var.get()
        self.log_box.insert("end", f"[-->] Connecting via {method} to {host}:{port} ...")
        self.log_box.see("end")
        sock = socket.socket()
        try:
            sock.connect((host, int(port)))
            self.cli_sock = sock
            if method == "DPH":
                encryption_key = dph_cli(sock)
            elif method == "RSA":
                encryption_key = rsa_cli(sock)
            self.status_lbl.config(text="● Connected", fg=SUCCESS)
            self.btn_connect.config(state="disabled", bg=MUTED)
            self.btn_login.config(state="normal")
            threading.Thread(target=self._listen_to_server, daemon=True).start()
        except Exception:
            self.log_box.insert("end", "[X] Connection Failed")
            print(traceback.format_exc())

    def _on_login(self):
        self.pending_login_username = self.login_user.get().strip()
        password = self.login_pass.get()
        self.log_box.insert("end", f"[-->] LOGIN request for: {self.pending_login_username}")
        self.log_box.see("end")
        send_with_size(self.cli_sock,
                       f"LOG_IN~{self.pending_login_username}~{password}~".encode(),
                       encryption_key)

    def _on_signup(self):
        username = self.su_user.get().strip()
        self.log_box.insert("end", f"[-->] SIGNUP request for: {username}")
        self.log_box.see("end")
        msg = (f"SIGNUP~{username}~{self.su_pass.get()}~{self.su_name.get()}"
               f"~{self.su_last.get()}~{self.su_email.get()}~{self.su_phone.get()}")
        send_with_size(self.cli_sock, msg.encode(), encryption_key)
        self._open_otp_window(username, "sign")

    def _on_forgot(self):
        username = self.fp_user.get().strip()
        self.log_box.insert("end", f"[-->] FORGOT_PASSWORD request for: {username}")
        self.log_box.see("end")
        msg = f"FORGOT~{username}~{self.fp_email.get()}~{self.fp_pass.get()}"
        send_with_size(self.cli_sock, msg.encode(), encryption_key)
        self._open_otp_window(username, "forg")

    def _ensure_session_key(self, peer: str):
        """
        If we don't have an AES session key with this peer yet,
        generate one, encrypt it with their RSA public key, and send it.
        """
        if peer in self.session_keys:
            return  # already established
        if peer not in self.peer_public_keys:
            return  # don't have their public key yet

        aes_key = _rand_bytes(32)  # AES-256
        self.session_keys[peer] = aes_key

        # Encrypt the raw AES key with peer's RSA public key
        enc_key_hex = rsa_encrypt_for_peer(self.peer_public_keys[peer],
                                           aes_key.hex())  # send as hex string
        send_with_size(self.cli_sock,
                       f"SESSION_INIT~{peer}~{enc_key_hex}".encode(),
                       encryption_key)
        self.log_box.insert("end", f"[🔑] AES session key sent to {peer}")

    # ── Server listener ───────────────────────
    def _listen_to_server(self):
        while True:
            try:
                data = recv_by_size(self.cli_sock, encryption_key).decode()

                # Presence
                if data.startswith("U_LIST~"):
                    users = [u for u in data.split("~")[1:] if u]
                    self.after(0, self._set_online_users, users)
                    self.log_box.insert("end", f"[👥] Online: {', '.join(users)}")

                elif data.startswith("U_JOIN~"):
                    username = data.split("~", 1)[1]
                    self.after(0, self._add_online_user, username)
                    self.log_box.insert("end", f"[+] {username} joined")
                    self.log_box.itemconfig("end", fg=SUCCESS)

                elif data.startswith("U_LEFT~"):
                    username = data.split("~", 1)[1]
                    self.after(0, self._remove_online_user, username)
                    self.log_box.insert("end", f"[-] {username} left")
                    self.log_box.itemconfig("end", fg=WARN)

                # Successful login → publish our public key
                elif data.startswith("LOG_OK"):
                    self.logged_in_username = self.pending_login_username
                    pub_pem = self.my_public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                    b64_pem = base64.b64encode(pub_pem).decode()
                    send_with_size(self.cli_sock,
                                   f"PUB_KEY~{self.logged_in_username}~{b64_pem}".encode(),
                                   encryption_key)
                    self.log_box.insert("end", "[🔑] Published our public key")
                    self.log_box.insert("end", f"[<--] {data}")

                # Receive a peer's public key
                elif data.startswith("PUB_KEY~"):
                    _, peer, b64_pem = data.split("~", 2)
                    pub_key = serialization.load_pem_public_key(
                        base64.b64decode(b64_pem), backend=default_backend()
                    )
                    self.peer_public_keys[peer] = pub_key
                    self.log_box.insert("end", f"[🔑] Got public key from {peer}")

                # Receive a private (E2E encrypted) message
                elif data.startswith("PRIV_MSG~"):
                    _, from_user, iv_hex, ct_hex = data.split("~", 3)
                    if from_user not in self.session_keys:
                        self.log_box.insert("end",
                                            f"[X] No session key for {from_user} — cannot decrypt")
                    else:
                        try:
                            plain = aes_decrypt_msg(self.session_keys[from_user], iv_hex, ct_hex)
                            self.after(0, self._append_chat_message, from_user, from_user, plain)
                            self.log_box.insert("end", f"[💬] Private msg from {from_user}")
                            self.log_box.itemconfig("end", fg=ACCENT)
                        except Exception:
                            self.log_box.insert("end",
                                                f"[X] Could not decrypt message from {from_user}")
                            print(traceback.format_exc())

                elif data.startswith("SESSION_INIT~"):
                    _, from_user, enc_key_hex = data.split("~", 2)
                    try:
                        aes_key_hex = rsa_decrypt_from_peer(self.my_private_key, enc_key_hex)
                        self.session_keys[from_user] = bytes.fromhex(aes_key_hex)
                        self.log_box.insert("end", f"[🔑] AES session established with {from_user}")
                        self.log_box.itemconfig("end", fg=SUCCESS)
                    except Exception:
                        self.log_box.insert("end", f"[X] Failed to decrypt session key from {from_user}")
                        print(traceback.format_exc())

                else:
                    self.log_box.insert("end", f"[<--] {data}")

                self.log_box.see("end")

            except Exception:
                print(traceback.format_exc())
                break

    # ── OTP window ────────────────────────────
    def _open_otp_window(self, username, type):
        otp_win = tk.Toplevel(self)
        otp_win.title("Email Verification")
        otp_win.geometry("300x200")
        otp_win.configure(bg=SURFACE)
        tk.Label(otp_win, text="Enter code sent to email:",
                 bg=SURFACE, fg=TEXT, font=("Segoe UI", 10)).pack(pady=10)
        otp_entry = tk.Entry(otp_win, bg="#1a1a2e", fg=TEXT, font=("Segoe UI", 12))
        otp_entry.pack(pady=5, padx=20)

        def submit_code():
            code = otp_entry.get().strip()
            num = 1 if type == "sign" else 2
            send_with_size(self.cli_sock,
                           f"VERIFY{num}~{username}~{code}".encode(),
                           encryption_key)
            otp_win.destroy()

        tk.Button(otp_win, text="Verify", command=submit_code,
                  bg=ACCENT, fg="white", font=("Segoe UI", 10, "bold")).pack(pady=20)


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.destroy)
    app.mainloop()