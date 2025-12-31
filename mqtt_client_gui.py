"""
MQTT Client GUI - PyQt6 Version
ทำงานเหมือน mqtt_client.py แต่มี GUI แสดง output ใน text area
ใช้ QSettings สำหรับจัดเก็บการตั้งค่า
"""
import os
import sys
import time
from datetime import datetime
from datetime import datetime
from typing import Optional
import ssl

from dotenv import load_dotenv
from paho.mqtt import client as mqtt
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSettings, QLocale
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QLineEdit,
    QGroupBox,
    QStatusBar,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QMessageBox,
    QSpinBox,
)

import send_ipd
import send_icu
import send_or
from send_log import log_send, ensure_log_file

load_dotenv()

# Application info for QSettings
APP_NAME = "OnePlk MQTT Client"
ORG_NAME = "OnePlk"


class SettingsDialog(QDialog):
    """Dialog สำหรับตั้งค่า MQTT พร้อมปุ่มทดสอบการเชื่อมต่อ"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ MQTT Settings")
        self.setMinimumWidth(450)
        self.setStyleSheet(self.get_dialog_stylesheet())
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """สร้าง UI ของ dialog"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("⚙️ MQTT Configuration")
        title_label.setObjectName("dialog_title")
        layout.addWidget(title_label)
        
        # Form layout for settings
        form_group = QGroupBox("Connection Settings")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(12)
        
        # Broker
        self.broker_input = QLineEdit()
        self.broker_input.setPlaceholderText("e.g., localhost or broker.hivemq.com")
        form_layout.addRow("Broker:", self.broker_input)
        
        # Port
        self.port_input = QSpinBox()
        self.port_input.setLocale(QLocale(QLocale.Language.C))  # Use Arabic numerals
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(1883)
        form_layout.addRow("Port:", self.port_input)
        
        # Topic
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("e.g., oneplk/command")
        form_layout.addRow("Topic:", self.topic_input)
        
        # Client ID
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Leave empty for auto-generated")
        # Client ID
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Leave empty for auto-generated")
        form_layout.addRow("Client ID:", self.client_id_input)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Optional")
        form_layout.addRow("Username:", self.username_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Optional")
        form_layout.addRow("Password:", self.password_input)
        
        # Rate limit
        self.rate_limit_input = QSpinBox()
        self.rate_limit_input.setLocale(QLocale(QLocale.Language.C))  # Use Arabic numerals
        self.rate_limit_input.setRange(1, 60)
        self.rate_limit_input.setValue(5)
        self.rate_limit_input.setSuffix(" seconds")
        form_layout.addRow("Rate Limit:", self.rate_limit_input)
        
        layout.addWidget(form_group)
        
        # Test connection button
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("🔍 Test Connection")
        self.test_btn.setObjectName("test_btn")
        self.test_btn.clicked.connect(self.test_connection)
        test_layout.addWidget(self.test_btn)
        
        self.test_status_label = QLabel("")
        self.test_status_label.setObjectName("test_status")
        test_layout.addWidget(self.test_status_label, stretch=1)
        
        layout.addLayout(test_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_and_accept)
        button_box.rejected.connect(self.reject)
        
        # Style the buttons
        save_btn = button_box.button(QDialogButtonBox.StandardButton.Save)
        save_btn.setText("💾 Save")
        save_btn.setObjectName("save_btn")
        
        cancel_btn = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setText("❌ Cancel")
        
        layout.addWidget(button_box)
    
    def get_dialog_stylesheet(self) -> str:
        """Stylesheet สำหรับ dialog"""
        return """
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                color: #333333;
            }
            QLabel#dialog_title {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px 0;
            }
            QLabel#test_status {
                font-size: 11px;
                padding: 5px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
                padding-top: 25px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: #2c3e50;
            }
            QLineEdit, QSpinBox {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 8px;
                color: #333333;
                min-width: 200px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 1px solid #2c3e50;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 10px 20px;
                color: #333333;
                font-weight: bold;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
                border-color: #adadad;
            }
            QPushButton:pressed {
                background-color: #d4d4d4;
            }
            QPushButton#test_btn {
                background-color: #6c757d;
                color: #ffffff;
                border: none;
            }
            QPushButton#test_btn:hover {
                background-color: #5a6268;
            }
            QPushButton#save_btn {
                background-color: #00875a;
                color: #ffffff;
                border: none;
            }
            QPushButton#save_btn:hover {
                background-color: #00a86b;
            }
            QDialogButtonBox {
                margin-top: 10px;
            }
        """
    
    def load_settings(self):
        """โหลด settings จาก QSettings (fallback to env vars)"""
        hospcode = os.getenv("HOSPCODE", "00001")
        
        self.broker_input.setText(
            self.settings.value("mqtt/broker", os.getenv("MQTT_BROKER", "localhost"))
        )
        self.port_input.setValue(
            int(self.settings.value("mqtt/port", os.getenv("MQTT_PORT", "1883")))
        )
        self.topic_input.setText(
            self.settings.value("mqtt/topic", os.getenv("MQTT_TOPIC", "oneplk/command"))
        )
        self.client_id_input.setText(
            self.settings.value("mqtt/client_id", os.getenv("MQTT_CLIENT_ID", "") or hospcode)
        )
        # Robust loading for SettingsDialog
        username = self.settings.value("mqtt/username", "")
        if not username:
            username = os.getenv("MQTT_USERNAME", "")
            
        password = self.settings.value("mqtt/password", "")
        if not password:
            password = os.getenv("MQTT_PASSWORD", "")

        self.username_input.setText(username)
        self.password_input.setText(password)
        self.rate_limit_input.setValue(
            int(self.settings.value("mqtt/rate_limit", os.getenv("RATE_LIMIT_SECONDS", "5")))
        )
    
    def save_settings(self):
        """บันทึก settings ลง QSettings"""
        self.settings.setValue("mqtt/broker", self.broker_input.text())
        self.settings.setValue("mqtt/port", self.port_input.value())
        self.settings.setValue("mqtt/topic", self.topic_input.text())
        self.settings.setValue("mqtt/client_id", self.client_id_input.text())
        self.settings.setValue("mqtt/username", self.username_input.text())
        self.settings.setValue("mqtt/password", self.password_input.text())
        self.settings.setValue("mqtt/rate_limit", self.rate_limit_input.value())
        self.settings.sync()
    
    def save_and_accept(self):
        """บันทึกและปิด dialog"""
        # Validate
        if not self.broker_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Broker address is required!")
            return
        if not self.topic_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Topic is required!")
            return
        
        self.save_settings()
        self.accept()
    
    def test_connection(self):
        """ทดสอบการเชื่อมต่อ MQTT broker"""
        broker = self.broker_input.text().strip()
        port = self.port_input.value()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not broker:
            self.test_status_label.setText("❌ Please enter broker address")
            self.test_status_label.setStyleSheet("color: #ff6b6b;")
            return
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("⏳ Testing...")
        self.test_status_label.setText("Connecting...")
        self.test_status_label.setStyleSheet("color: #ffd93d;")
        QApplication.processEvents()
        
        try:
            # Create temporary client for testing
            test_client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id=f"test-{os.getpid()}"
            )
            
            if username and password:
                test_client.username_pw_set(username, password)

            if port == 8883:
                cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emqxsl-ca.crt")
                if os.path.exists(cert_path):
                    test_client.tls_set(ca_certs=cert_path)
                else:
                    test_client.tls_set(cert_reqs=ssl.CERT_NONE)
                    test_client.tls_insecure_set(True)
            
            connected = False
            error_msg = ""
            
            def on_connect(client, userdata, flags, reason_code, properties=None):
                nonlocal connected
                rc = getattr(reason_code, "value", reason_code)
                connected = (rc == 0)
            
            test_client.on_connect = on_connect
            
            # Try to connect with timeout
            test_client.connect(broker, port, 60)
            test_client.loop_start()
            
            # Wait for connection (max 5 seconds)
            start_time = time.time()
            while not connected and (time.time() - start_time) < 5:
                time.sleep(0.1)
            
            test_client.loop_stop()
            test_client.disconnect()
            
            if connected:
                self.test_status_label.setText(f"✅ Connected to {broker}:{port}")
                self.test_status_label.setStyleSheet("color: #69db7c;")
            else:
                self.test_status_label.setText(f"❌ Connection timeout")
                self.test_status_label.setStyleSheet("color: #ff6b6b;")
                
        except Exception as e:
            self.test_status_label.setText(f"❌ Error: {str(e)[:50]}")
            self.test_status_label.setStyleSheet("color: #ff6b6b;")
        
        finally:
            self.test_btn.setEnabled(True)
            self.test_btn.setText("🔍 Test Connection")
    
    def get_settings(self) -> dict:
        """Return current settings as dict"""
        return {
            "broker": self.broker_input.text().strip() or "localhost",
            "port": self.port_input.value(),
            "topic": self.topic_input.text().strip() or "oneplk/command",
            "client_id": self.client_id_input.text().strip() or f"oneplk-{os.getpid()}",
            "rate_limit": self.rate_limit_input.value(),
        }


class MQTTWorker(QThread):
    """Worker thread สำหรับ MQTT client เพื่อไม่ให้ block GUI"""
    
    message_received = pyqtSignal(str)  # Signal สำหรับส่งข้อความไปยัง GUI
    connection_status = pyqtSignal(bool, str)  # Signal สำหรับสถานะการเชื่อมต่อ
    
    def __init__(self, broker: str, port: int, topic: str, client_id: str, username: str = "", password: str = "", rate_limit: int = 5):
        super().__init__()
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = client_id
        self.username = username
        self.password = password
        self.running = True
        self.client: Optional[mqtt.Client] = None
        
        # Rate Limiting
        self.rate_limit_seconds = rate_limit
        self._last_command_time: dict[str, float] = {}
    
    def log(self, message: str):
        """ส่ง log message ไปยัง GUI"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.message_received.emit(f"[{timestamp}] {message}")
    
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        rc = getattr(reason_code, "value", reason_code)
        if rc == 0:
            self.log(f"✅ Connected to MQTT Broker: {self.broker}")
            self.connection_status.emit(True, f"Connected to {self.broker}:{self.port}")
            client.subscribe(self.topic)
            self.log(f"📡 Subscribed to topic: {self.topic}")
        else:
            self.log(f"❌ Failed to connect, return code {rc}")
            self.connection_status.emit(False, f"Connection failed (code: {rc})")
    
    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties=None):
        self.log("⚠️ Disconnected from MQTT Broker")
        self.connection_status.emit(False, "Disconnected")
    
    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8").strip().lower()
        self.log(f"📨 Received message: '{payload}' on topic: '{msg.topic}'")
        
        # Rate limiting
        now = time.time()
        if payload in self._last_command_time:
            elapsed = now - self._last_command_time[payload]
            if elapsed < self.rate_limit_seconds:
                self.log(f"⏳ Rate limited: '{payload}' (wait {self.rate_limit_seconds - elapsed:.1f}s)")
                return
        self._last_command_time[payload] = now
        
        command_dt = ""
        send_status = "fail"
        send_success_dt = ""
        error_reason = ""
        func_name = ""
        command = ""
        
        match payload:
            case "icu":
                command = "icu"
                func_name = "send_icu"
                self.log("🏥 Executing ICU send...")
                command_dt, send_status, send_success_dt, error_reason = send_icu.send()
            case "ipd":
                command = "ipd"
                func_name = "send_ipd"
                self.log("🏥 Executing IPD send...")
                command_dt, send_status, send_success_dt, error_reason = send_ipd.send()
            case "or":
                command = "or"
                func_name = "send_or"
                self.log("🏥 Executing OR send...")
                command_dt, send_status, send_success_dt, error_reason = send_or.send()
            case _:
                self.log(f"❓ Unknown command: '{payload}' (ignored)")
                return
        
        # Log result
        if send_status == "success":
            self.log(f"✅ {command.upper()} send completed successfully")
        else:
            self.log(f"❌ {command.upper()} send failed: {error_reason}")
        
        log_send(command, func_name, command_dt, send_status, send_success_dt, error_reason)
    
    def run(self):
        """Main thread loop สำหรับ MQTT client"""
        self.log(f"🚀 Starting MQTT Client...")
        self.log(f"📍 Broker: {self.broker}:{self.port}")
        self.log(f"📡 Topic: {self.topic}")
        self.log(f"🆔 Client ID: {self.client_id}")
        
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id
        )

        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id
        )

        if self.username and self.password:
            self.log(f"🔐 Authenticating as user: {self.username}")
            self.client.username_pw_set(self.username, self.password)
        else:
            self.log("⚠️ No authentication credentials provided")
        
        if self.port == 8883:
            cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emqxsl-ca.crt")
            if os.path.exists(cert_path):
                self.log(f"🔐 Using CA certificate: {cert_path}")
                self.client.tls_set(ca_certs=cert_path)
            else:
                self.log("⚠️ CA certificate not found. Using insecure SSL.")
                self.client.tls_set(cert_reqs=ssl.CERT_NONE)
                self.client.tls_insecure_set(True)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        
        # Loop with retry for robust connection
        while self.running:
            try:
                self.log(f"🔌 Connecting to {self.broker}:{self.port}...")
                self.client.connect(self.broker, self.port, 60)
                
                # loop_forever handles reconnection automatically
                # It returns only when disconnect() is called or connection fails critically
                self.client.loop_forever()
                
            except Exception as e:
                if self.running:
                    self.log(f"❌ Connection failed: {e}. Retrying in 5s...")
                    self.connection_status.emit(False, f"Connection failed: {e}")
                    time.sleep(5)
            
            # If loop_forever returns but we are still running, retry
            if self.running:
                # Small delay before retry if loop_forever returned unexpectedly
                time.sleep(1)
    
    def stop(self):
        """หยุด MQTT client"""
        self.running = False
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass


class MQTTClientGUI(QMainWindow):
    """Main GUI Window"""
    
    def __init__(self):
        super().__init__()
        self.mqtt_worker: Optional[MQTTWorker] = None
        self.settings = QSettings(ORG_NAME, APP_NAME)
        self.current_settings = {}
        self.init_ui()
        self.load_settings()
        
        # Auto-connect on startup
        self.connect_mqtt()
    
    def init_ui(self):
        """สร้าง UI components"""
        self.setWindowTitle("MQTT Client - OnePlk")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(self.get_stylesheet())
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with settings button
        header_layout = QHBoxLayout()
        
        header_label = QLabel("🔌 MQTT Client - OnePlk")
        header_label.setObjectName("header")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        # Settings info label
        self.settings_info_label = QLabel("")
        self.settings_info_label.setObjectName("settings_info")
        header_layout.addWidget(self.settings_info_label)
        
        # Settings button "..."
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setObjectName("settings_btn")
        self.settings_btn.setToolTip("Open Settings")
        self.settings_btn.setFixedSize(45, 45)
        self.settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(header_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("🔌 Connect")
        self.connect_btn.setObjectName("connect_btn")
        self.connect_btn.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.connect_btn)
        
        self.clear_btn = QPushButton("🗑️ Clear Log")
        self.clear_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Output text area with scroll
        output_group = QGroupBox("Output Log")
        output_layout = QVBoxLayout(output_group)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        self.output_text.setMinimumHeight(400)
        output_layout.addWidget(self.output_text)
        
        main_layout.addWidget(output_group, stretch=1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("Disconnected", False)
    
    def get_stylesheet(self) -> str:
        """Return application stylesheet"""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                color: #333333;
            }
            QLabel#header {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
            QLabel#settings_info {
                font-size: 11px;
                color: #666666;
                padding: 5px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 10px 20px;
                color: #333333;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
                border-color: #adadad;
            }
            QPushButton:pressed {
                background-color: #d4d4d4;
            }
            QPushButton#connect_btn {
                background-color: #00875a;
                color: #ffffff;
                border: none;
            }
            QPushButton#connect_btn:hover {
                background-color: #00a86b;
            }
            QPushButton#settings_btn {
                font-size: 18px;
                border-radius: 22px;
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
            }
            QPushButton#settings_btn:hover {
                background-color: #f0f0f0;
                border-color: #2c3e50;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 10px;
                color: #333333;
            }
            QStatusBar {
                background-color: #e0e0e0;
                color: #333333;
                border-top: 1px solid #dcdcdc;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """
    
    def load_settings(self):
        """โหลด settings จาก QSettings"""
        hospcode = os.getenv("HOSPCODE", "00001")
        
        username = self.settings.value("mqtt/username")
        if not username:
             username = os.getenv("MQTT_USERNAME", "")
        
        password = self.settings.value("mqtt/password")
        if not password:
             password = os.getenv("MQTT_PASSWORD", "")

        self.current_settings = {
            "broker": self.settings.value("mqtt/broker", os.getenv("MQTT_BROKER", "localhost")),
            "port": int(self.settings.value("mqtt/port", os.getenv("MQTT_PORT", "1883"))),
            "topic": self.settings.value("mqtt/topic", os.getenv("MQTT_TOPIC", "oneplk/command")),
            "client_id": self.settings.value("mqtt/client_id", os.getenv("MQTT_CLIENT_ID", "") or hospcode),
            "username": username,
            "password": password,
            "rate_limit": int(self.settings.value("mqtt/rate_limit", os.getenv("RATE_LIMIT_SECONDS", "5"))),
        }
        
        self.update_settings_info()
    
    def update_settings_info(self):
        """อัปเดต label แสดงข้อมูล settings ปัจจุบัน"""
        broker = self.current_settings.get("broker", "localhost")
        port = self.current_settings.get("port", 1883)
        self.settings_info_label.setText(f"📍 {broker}:{port}")
    
    def open_settings(self):
        """เปิด Settings Dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_settings = dialog.get_settings()
            self.update_settings_info()
            self.append_log("⚙️ Settings updated")
    
    def toggle_connection(self):
        """Toggle MQTT connection on/off"""
        if self.mqtt_worker and self.mqtt_worker.isRunning():
            self.disconnect_mqtt()
        else:
            self.connect_mqtt()
    
    def connect_mqtt(self):
        """เชื่อมต่อ MQTT broker"""
        broker = self.current_settings.get("broker", "localhost")
        port = self.current_settings.get("port", 1883)
        topic = self.current_settings.get("topic", "oneplk/command")
        client_id = self.current_settings.get("client_id") or f"oneplk-{os.getpid()}"
        
        # Robust fallback for connect
        username = self.current_settings.get("username", "")
        if not username:
             username = os.getenv("MQTT_USERNAME", "")
             
        password = self.current_settings.get("password", "")
        if not password:
             password = os.getenv("MQTT_PASSWORD", "")
        rate_limit = self.current_settings.get("rate_limit", 5)
        
        # Ensure log file exists
        ensure_log_file()
        
        # Create and start worker
        self.mqtt_worker = MQTTWorker(broker, port, topic, client_id, username, password, rate_limit)
        self.mqtt_worker.message_received.connect(self.append_log)
        self.mqtt_worker.connection_status.connect(self.update_status)
        self.mqtt_worker.start()
        
        # Update UI
        self.connect_btn.setText("🔴 Disconnect")
        self.connect_btn.setStyleSheet("background-color: #c44536;")
        self.settings_btn.setEnabled(False)
    
    def disconnect_mqtt(self):
        """ตัดการเชื่อมต่อ MQTT broker"""
        if self.mqtt_worker:
            self.mqtt_worker.stop()
            self.mqtt_worker.wait(2000)  # Wait up to 2 seconds
            self.mqtt_worker = None
        
        # Update UI
        self.connect_btn.setText("🔌 Connect")
        self.connect_btn.setStyleSheet("")
        self.settings_btn.setEnabled(True)
        self.update_status("Disconnected", False)
        self.append_log("🔌 Disconnected from MQTT broker")
    
    def append_log(self, message: str):
        """เพิ่มข้อความลงใน output log"""
        self.output_text.append(message)
        # Also print to console
        print(message)
        # Auto-scroll to bottom
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)
    
    def clear_log(self):
        """ล้าง output log"""
        self.output_text.clear()
    
    def update_status(self, message: str, connected: bool):
        """อัปเดต status bar"""
        if connected:
            self.status_bar.setStyleSheet("background-color: #00875a; color: white;")
            self.status_bar.showMessage(f"✅ {message}")
        else:
            self.status_bar.setStyleSheet("background-color: #c44536; color: white;")
            self.status_bar.showMessage(f"❌ {message}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.mqtt_worker and self.mqtt_worker.isRunning():
            self.mqtt_worker.stop()
            self.mqtt_worker.wait(2000)
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MQTTClientGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
