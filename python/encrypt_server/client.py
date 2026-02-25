"""
=============================================================
  Encrypted Server Client – GUI Template (Phase A)
  Pure UI layout – no networking logic included
=============================================================
"""
import random
import tkinter as tk
from tkinter import ttk
import socket
import traceback
import threading

from tcp_by_size import send_with_size, recv_by_size


# ── Color palette ─────────────────────────────
BG      = "#1e1e2e"
SURFACE = "#2a2a3e"
ACCENT  = "#7c6af7"
ACCENT2 = "#5a4fcf"
TEXT    = "#cdd6f4"
SUCCESS = "#a6e3a1"
ERROR   = "#f38ba8"
MUTED   = "#6c7086"


# ─────────────────────────────────────────────
#  Helper: labeled entry widget
# ─────────────────────────────────────────────
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
#  Main Application Window
# ─────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.crypto_var = tk.StringVar(value="DPH")
        self.title("Encrypted Server – Phase A")
        self.geometry("860x620")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._build_ui()
        self.cli_sock = None

    # ── Build UI ──────────────────────────────
    def _build_ui(self):
        self._build_header()

        center = tk.Frame(self, bg=BG)
        center.pack(fill="both", expand=True, padx=14, pady=10)

        left = tk.Frame(center, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(center, bg=BG, width=280)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        self._build_connection_panel(left)
        self._build_tabs(left)
        self._build_log_panel(right)

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

        # שורה ראשונה: Host ו-Port
        row1 = tk.Frame(frame, bg=SURFACE)
        row1.pack(fill="x", padx=8, pady=4)

        tk.Label(row1, text="Host:", bg=SURFACE, fg=TEXT, font=("Segoe UI", 10)).pack(side="left")
        self.host_entry = tk.Entry(row1, width=14, bg="#1a1a2e", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(side="left", padx=4)

        tk.Label(row1, text="Port:", bg=SURFACE, fg=TEXT, font=("Segoe UI", 10)).pack(side="left")
        self.port_entry = tk.Entry(row1, width=6, bg="#1a1a2e", fg=TEXT, insertbackground=TEXT, relief="flat")
        self.port_entry.insert(0, "5555")
        self.port_entry.pack(side="left", padx=4)

        self.btn_connect = tk.Button(row1, text="Connect", command=self._on_connect,
                                     bg=ACCENT, fg="white", font=("Segoe UI", 10, "bold"), padx=12)
        self.btn_connect.pack(side="left", padx=8)

        self.status_lbl = tk.Label(row1, text="● Not Connected", bg=SURFACE, fg=ERROR, font=("Segoe UI", 10, "bold"))
        self.status_lbl.pack(side="left")

        # שורה שנייה: בחירת שיטת הצפנה (Key Exchange)
        row2 = tk.Frame(frame, bg=SURFACE)
        row2.pack(fill="x", padx=8, pady=(0, 8))

        tk.Label(row2, text="Method:", bg=SURFACE, fg=TEXT, font=("Segoe UI", 10)).pack(side="left")

        # כפתורי רדיו ל-DPH ו-RSA
        tk.Radiobutton(row2, text="DPH", variable=self.crypto_var, value="DPH",
                       bg=SURFACE, fg=TEXT, selectcolor=BG, activebackground=SURFACE).pack(side="left", padx=10)
        tk.Radiobutton(row2, text="RSA", variable=self.crypto_var, value="RSA",
                       bg=SURFACE, fg=TEXT, selectcolor=BG, activebackground=SURFACE,
                       state="disabled").pack(side="left")  # RSA מושבת כרגע לפי הדרישות

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

        # שדות קלט למשתמש וסיסמה
        f1, self.login_user = labeled_entry(inner, "Username")
        f1.pack(fill="x", pady=4)

        f2, self.login_pass = labeled_entry(inner, "Password", show="●")
        f2.pack(fill="x", pady=4)

        # כפתור Login - מוגדר כ-disabled ומשתנה ל-self.btn_login
        self.btn_login = tk.Button(inner, text="Login  →",
                                   command=self._on_login,
                                   state="disabled",  # כבוי עד לסיום ה-DPH
                                   bg=ACCENT, fg="white", relief="flat",
                                   font=("Segoe UI", 11, "bold"),
                                   cursor="hand2", padx=20, pady=6)
        self.btn_login.pack(pady=14)

        # קישור לשכחתי סיסמה
        tk.Label(inner, text="Forgot password?", bg=SURFACE, fg=ACCENT,
                 font=("Segoe UI", 9, "underline"), cursor="hand2").pack()

    # ── Sign Up tab ───────────────────────────
    def _build_signup_tab(self):
        tab = tk.Frame(self.notebook, bg=SURFACE)
        self.notebook.add(tab, text="  📋 Sign Up  ")

        # Scrollable inner area
        canvas = tk.Canvas(tab, bg=SURFACE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        inner = tk.Frame(canvas, bg=SURFACE)
        win = canvas.create_window((0, 0), window=inner, anchor="n")

        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        wrapper = tk.Frame(inner, bg=SURFACE)
        wrapper.pack(padx=60, pady=20)

        tk.Label(wrapper, text="Create a New Account", bg=SURFACE, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(pady=(0, 12))

        fields = [
            ("Username",   "",  "su_user"),
            ("Password",   "●", "su_pass"),
            ("First Name", "",  "su_name"),
            ("Last Name",  "",  "su_last"),
            ("Email",      "",  "su_email"),
            ("Phone",      "",  "su_phone"),
        ]
        for label, show, attr in fields:
            f, entry = labeled_entry(wrapper, label, show)
            f.pack(fill="x", pady=3)
            setattr(self, attr, entry)

        tk.Button(wrapper, text="Register  →",
                  command=self._on_signup,
                  bg=SUCCESS, fg="#1e1e2e", relief="flat",
                  font=("Segoe UI", 11, "bold"),
                  cursor="hand2", padx=20, pady=6).pack(pady=14)

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

        tk.Button(inner, text="Reset Password  →",
                  command=self._on_forgot,
                  bg="#fab387", fg="#1e1e2e", relief="flat",
                  font=("Segoe UI", 11, "bold"),
                  cursor="hand2", padx=20, pady=6).pack(pady=14)

    # ── Activity log panel ────────────────────
    def _build_log_panel(self, parent):
        tk.Label(parent, text="📋 Activity Log",
                 bg=BG, fg=ACCENT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))

        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="both", expand=True)

        sb = tk.Scrollbar(frame)
        sb.pack(side="right", fill="y")

        self.log_box = tk.Listbox(
            frame,
            yscrollcommand=sb.set,
            bg="#12121e", fg=TEXT,
            selectbackground=ACCENT2,
            font=("Consolas", 9),
            relief="flat", bd=0,
            activestyle="none",
        )
        self.log_box.pack(fill="both", expand=True)
        sb.config(command=self.log_box.yview)

        # Seed a few placeholder log entries
        for msg in ["[--] Waiting for connection...", "[--] Activity will appear here"]:
            self.log_box.insert("end", msg)

        tk.Button(parent, text="Clear Log",
                  command=lambda: self.log_box.delete(0, "end"),
                  bg=MUTED, fg="white", relief="flat",
                  font=("Segoe UI", 9),
                  cursor="hand2").pack(fill="x", pady=(6, 0))

    # ─────────────────────────────────────────
    #  Button stubs – wire up your logic here
    # ─────────────────────────────────────────
    def _on_connect(self):
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        self.log_box.insert("end", f"[-->] Connecting to {host}:{port} ...")
        self.log_box.see("end")
        # After successful connect:
        sock = socket.socket()
        try:
            sock.connect((host, int(port)))
            self.cli_sock = sock
            self.status_lbl.config(text="● Connected", fg=SUCCESS)
            self.btn_connect.config(state="disabled", bg=MUTED)

            parameters = recv_by_size(sock).decode()
            parts = parameters.split(',')
            p = int(parts[0])
            g = int(parts[1])  # alpha

            y = random.randint(2, p - 2)
            b = pow(g, y, p)
            send_with_size(sock, str(b).encode())

            a = int(recv_by_size(sock).decode())

            k = pow(a, y, p)
            print(f"the key is: {k}")

            self.btn_login.config(state="normal")
            listener = threading.Thread(target=self._listen_to_server, daemon=True)
            listener.start()

        except Exception:
            print(traceback.format_exc())

    def _on_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get()
        self.log_box.insert("end", f"[-->] LOGIN request for: {username}")
        self.log_box.see("end")

        # Shai_M hi06
        msg = "LOG_IN" + "~"
        msg += username + "~"
        msg += password + "~"
        send_with_size(self.cli_sock, msg.encode())


    def _on_signup(self):
        # TOD: send SIGNUP command to server
        username = self.su_user.get().strip()
        self.log_box.insert("end", f"[-->] SIGNUP request for: {username}")
        self.log_box.see("end")

        msg = "SIGNUP" + "~"
        msg += username + "~"
        msg += self.su_pass.get() + "~"
        msg += self.su_name.get() + "~"
        msg += self.su_last.get() + "~"
        msg += self.su_email.get() + "~"
        msg += self.su_phone.get()
        send_with_size(self.cli_sock, msg.encode())

        self._open_otp_window(username, "sign")

    def _on_forgot(self):
        # TOD: send FORGOT_PASSWORD command to server
        username = self.fp_user.get().strip()
        self.log_box.insert("end", f"[-->] FORGOT_PASSWORD request for: {username}")
        self.log_box.see("end")

        msg = "FORGOT" + "~"
        msg += username + "~"
        msg += self.fp_email.get() + "~"
        msg += self.fp_pass.get()
        send_with_size(self.cli_sock, msg.encode())

        self._open_otp_window(username, "forg")


    def _listen_to_server(self):
        while True:
            try:
                data = recv_by_size(self.cli_sock).decode()
                self.log_box.insert("end", f"[<--] {data}")

            except Exception:
                print(traceback.format_exc())
                break

    def _open_otp_window(self, username, type):
        # יצירת חלון חדש מעל החלון הראשי
        otp_win = tk.Toplevel(self)
        otp_win.title("Email Verification")
        otp_win.geometry("300x200")
        otp_win.configure(bg=SURFACE)

        tk.Label(otp_win, text=f"Enter code sent to email:",
                 bg=SURFACE, fg=TEXT, font=("Segoe UI", 10)).pack(pady=10)

        otp_entry = tk.Entry(otp_win, bg="#1a1a2e", fg=TEXT, font=("Segoe UI", 12))
        otp_entry.pack(pady=5, padx=20)

        def submit_code():
            code = otp_entry.get().strip()
            # שליחת הקוד לשרת לאימות (נממש את הפרוטוקול בהמשך)
            if type == "sign":
                num = 1
            elif type == "forg":
                num = 2
            msg = f"VERIFY{num}~{username}~{code}"
            send_with_size(self.cli_sock, msg.encode())
            otp_win.destroy()

        tk.Button(otp_win, text="Verify", command=submit_code,
                  bg=ACCENT, fg="white", font=("Segoe UI", 10, "bold")).pack(pady=20)

# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.destroy)
    app.mainloop()
