import sys
import bcrypt
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QStackedWidget
)

# ---------------------- Database Setup ----------------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ---------------------- Home Page ----------------------
class HomePage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.label_welcome = QLabel("Selamat datang, [username]")
        self.label_welcome.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")

        self.logout_btn = QPushButton("Keluar")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        self.logout_btn.clicked.connect(self.logout)

        self.layout.addWidget(self.label_welcome)
        self.layout.addWidget(self.logout_btn)
        self.setLayout(self.layout)

    def set_username(self, username):
        self.label_welcome.setText(f"Selamat datang, {username}!")

    def logout(self):
        self.stacked_widget.setCurrentIndex(0)

# ---------------------- Login Page ----------------------
class LoginPage(QWidget):
    def __init__(self, stacked_widget, home_page):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.home_page = home_page
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Silahkan Login")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setStyleSheet("padding: 8px; font-size: 14px;")

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.password.setStyleSheet("padding: 8px; font-size: 14px;")

        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                padding: 8px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)

        register_btn = QPushButton("Belum punya akun? Registrasi")
        register_btn.setStyleSheet("font-size: 12px; color: #333;")

        login_btn.clicked.connect(self.login)
        register_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(label)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)
        self.setLayout(layout)

    def login(self):
        uname = self.username.text()
        pw = self.password.text()

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE username=?", (uname,))
        result = c.fetchone()
        conn.close()

        if result and bcrypt.checkpw(pw.encode(), result[0]):
            self.home_page.set_username(uname)
            self.stacked_widget.setCurrentIndex(2)
        else:
            QMessageBox.critical(self, "Login Gagal", "Username atau password salah")

# ---------------------- Register Page ----------------------
class RegisterPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel("Buat Akun Baru")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username Baru")
        self.username.setStyleSheet("padding: 8px; font-size: 14px;")

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password Baru")
        self.password.setStyleSheet("padding: 8px; font-size: 14px;")

        register_btn = QPushButton("Daftar")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        back_btn = QPushButton("Kembali ke Login")
        back_btn.setStyleSheet("font-size: 12px; color: #333;")

        register_btn.clicked.connect(self.register)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        layout.addWidget(label)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(register_btn)
        layout.addWidget(back_btn)
        self.setLayout(layout)

    def register(self):
        uname = self.username.text()
        pw = self.password.text()

        if uname == "" or pw == "":
            QMessageBox.warning(self, "Input Kosong", "Isi semua data!")
            return

        hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

        try:
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (uname, hashed))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Registrasi", "Registrasi berhasil!")
            self.stacked_widget.setCurrentIndex(0)
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "Gagal", "Username sudah digunakan")

# ---------------------- Main App ----------------------
def main():
    init_db()
    app = QApplication(sys.argv)

    # Global background & input style
    app.setStyleSheet("""
        QWidget {
            background-color: #f2f2f2;
        }
        QLineEdit {
            border: 1px solid #ccc;
            border-radius: 4px;
        }
    """)

    stacked = QStackedWidget()

    # Pages
    home_page = HomePage(stacked)
    login_page = LoginPage(stacked, home_page)
    register_page = RegisterPage(stacked)

    # Stack order
    stacked.addWidget(login_page)    # index 0
    stacked.addWidget(register_page) # index 1
    stacked.addWidget(home_page)     # index 2

    stacked.setWindowTitle("CRYPTO")
    stacked.setFixedSize(320, 250)
    stacked.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
