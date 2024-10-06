

import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
    QTabWidget, QScrollArea, QFrame, QInputDialog, QSplitter, QSizePolicy, QLineEdit,
    QTextEdit, QListWidget
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QDateTime, QObject, pyqtSignal
from PyQt5.QtGui import QMovie, QFont
import pyqtgraph as pg
import qdarkstyle


class SeizureDetector(QObject):
    seizure_detected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.detect_seizure)
        self.timer.start(1000)  # Check every second

    def detect_seizure(self):
        import random
        # Randomly simulate seizure detection
        if random.randint(0, 100) < 5:  # 5% chance every second
            self.seizure_detected.emit()
            self.timer.stop()  # Stop detecting after seizure is detected


class SeizureProtocolManager(QObject):
    dose_to_administer = pyqtSignal(float)  # Signal with dose in mg
    protocol_started = pyqtSignal(str)  # Signal with protocol name
    protocol_completed = pyqtSignal(str)
    new_schedule = pyqtSignal(list)  # Signal with list of timestamps and doses

    def __init__(self):
        super().__init__()
        self.protocols = {}  # Store all protocols
        self.current_protocol = None
        self.current_protocol_timer = None
        self.step_index = 0

    def add_protocol(self, protocol_id, name, seizure_duration_threshold, steps, total_duration):
        """Add a new protocol to the system."""
        self.protocols[protocol_id] = {
            "id": protocol_id,
            "name": name,
            "seizure_duration_threshold": seizure_duration_threshold,  # in minutes
            "steps": steps,  # list of dicts with 'duration' in minutes and 'dose_mg'
            "total_duration": total_duration  # in minutes
        }
        print(f"Added {name} (Protocol {protocol_id}) to the system.")

    def start_protocol(self, protocol_id):
        """Start the protocol when a seizure is detected."""
        if protocol_id not in self.protocols:
            print(f"Protocol {protocol_id} not found.")
            return

        self.current_protocol = self.protocols[protocol_id]
        self.protocol_started.emit(self.current_protocol['name'])
        print(f"Running {self.current_protocol['name']}...")

        # Create a schedule of timestamps and doses
        self.schedule = []
        current_time = QDateTime.currentDateTime()
        for step in self.current_protocol['steps']:
            duration = step['duration']  # in minutes
            dose_mg = step['dose_mg']
            timestamp = current_time.addSecs(duration * 60)
            self.schedule.append({'time': timestamp, 'dose_mg': dose_mg})
            current_time = timestamp

        # Emit the schedule
        self.new_schedule.emit(self.schedule)

        # Start administering doses
        self.step_index = 0
        self.administer_next_dose()

    def administer_next_dose(self):
        if self.step_index >= len(self.current_protocol['steps']):
            # Protocol completed
            self.protocol_completed.emit(self.current_protocol['name'])
            self.current_protocol = None
            return

        step = self.current_protocol['steps'][self.step_index]
        dose_mg = step['dose_mg']
        self.dose_to_administer.emit(dose_mg)
        print(f"Administering {dose_mg} mg of medication.")

        # Schedule next dose
        duration = step['duration']  # in minutes
        self.current_protocol_timer = QTimer()
        self.current_protocol_timer.setSingleShot(True)
        self.current_protocol_timer.timeout.connect(self.administer_next_dose)
        self.current_protocol_timer.start(duration * 60 * 1000)  # Convert to milliseconds

        self.step_index += 1


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Medical Device UI")
        self.setGeometry(100, 100, 800, 600)

        # Serial Port and Connection setup
        self.serial_port = None
        self.data_buffer = []  # Buffer to store data from the serial port

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Top bar
        top_bar = self.create_top_bar()
        layout.addLayout(top_bar)

        # EEG Panel and Drug Dosage Panel (Split 3/4 for EEG and 1/4 for Drug Dosage)
        eeg_and_dosage_panel = self.create_eeg_and_dosage_panel()
        layout.addWidget(eeg_and_dosage_panel)

        # Tabs section
        tabs_panel = self.create_tabs_panel()
        layout.addWidget(tabs_panel)

        central_widget.setLayout(layout)

        # Timer for updating the EEG graph from serial data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_eeg_plot)

        # Instantiate SeizureDetector and SeizureProtocolManager
        self.seizure_detector = SeizureDetector()
        self.protocol_manager = SeizureProtocolManager()

        # Connect signals
        self.seizure_detector.seizure_detected.connect(self.on_seizure_detected)
        self.protocol_manager.dose_to_administer.connect(self.on_dose_to_administer)
        self.protocol_manager.new_schedule.connect(self.update_dosage_schedule)
        self.protocol_manager.protocol_started.connect(self.on_protocol_started)
        self.protocol_manager.protocol_completed.connect(self.on_protocol_completed)

        # Add default protocol
        self.protocol_manager.add_protocol(
            protocol_id=1,
            name="Default Protocol",
            seizure_duration_threshold=2,  # Seizure must last for 2 minutes
            steps=[
                {"duration": 1, "dose_mg": 5},  # First 1 minute: 5 mg
                {"duration": 1, "dose_mg": 2.5},  # Next 1 minute: 2.5 mg
                {"duration": 1, "dose_mg": 1},  # Next 1 minute: 1 mg
                {"duration": 1, "dose_mg": 0.5}  # Final 1 minute: 0.5 mg
            ],
            total_duration=4  # Total duration of the protocol: 4 minutes
        )

    def create_top_bar(self):
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setAlignment(Qt.AlignLeft)  # Align buttons to the left

        # Adding buttons for top bar
        buttons = ["Home", "Patient Data", "Seizure Stats", "Logs", "Settings"]
        for btn in buttons:
            button = QPushButton(btn)
            button.setFixedSize(100, 30)  # Set fixed size for buttons
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    font-size: 14px;
                    border: none;
                    padding: 5px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)
            top_bar_layout.addWidget(button)

        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        top_bar_layout.addWidget(spacer)

        # Add seizure detected label
        self.seizure_detected_label = QLabel("Seizure Detected!")
        self.seizure_detected_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")
        self.seizure_detected_label.setVisible(False)
        top_bar_layout.addWidget(self.seizure_detected_label)

        return top_bar_layout

    def create_eeg_and_dosage_panel(self):
        # Create a splitter to manage the 3/4 (EEG) and 1/4 (Drug Dosage) split
        splitter = QSplitter(Qt.Horizontal)

        # EEG Panel (left side, 3/4)
        eeg_widget = QWidget()
        eeg_layout = QVBoxLayout()

        # EEG Control buttons (right-aligned)
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # Push buttons to the right
        start_eeg_button = QPushButton("Start EEG")
        stop_eeg_button = QPushButton("Stop EEG")

        # Style buttons
        start_eeg_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #3498db;
            }
            QPushButton:hover {
                background-color: #2980b9;
                color: white;
            }
        """)
        stop_eeg_button.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #7f8c8d;
            }
            QPushButton:hover {
                background-color: #95a5a6;
                color: white;
            }
        """)

        start_eeg_button.clicked.connect(self.start_eeg)
        stop_eeg_button.clicked.connect(self.stop_eeg)

        button_layout.addWidget(start_eeg_button)
        button_layout.addWidget(stop_eeg_button)

        # EEG Graph (using pyqtgraph)
        self.eeg_plot_widget = pg.PlotWidget()
        self.eeg_plot_widget.setBackground('k')
        self.eeg_plot_widget.showGrid(x=True, y=True)
        self.eeg_plot = self.eeg_plot_widget.plot(pen=pg.mkPen(color=(0, 255, 0), width=2))

        eeg_layout.addLayout(button_layout)
        eeg_layout.addWidget(self.eeg_plot_widget)

        eeg_widget.setLayout(eeg_layout)
        splitter.addWidget(eeg_widget)

        # Drug Dosage Panel (right side, 1/4)
        dosage_widget = QWidget()
        dosage_layout = QVBoxLayout()

        # Scroll area for timestamps
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)

        drug_delivery_label = QLabel("Drug Dosage Information")
        drug_delivery_label.setAlignment(Qt.AlignLeft)
        drug_delivery_label.setFont(QFont('Arial', 16))
        drug_delivery_label.setStyleSheet("color: white;")

        # Dispensing animation label
        self.dispensing_label = QLabel("Dispensing...")
        self.dispensing_label.setFont(QFont('Arial', 18))
        self.dispensing_label.setAlignment(Qt.AlignCenter)
        self.dispensing_label.setStyleSheet("color: #00ff00;")
        self.dispensing_label.setVisible(False)  # Initially hidden

        # Current dosage in big letters
        current_dosage_label = QLabel("Current Dosage")
        current_dosage_label.setAlignment(Qt.AlignLeft)
        current_dosage_label.setFont(QFont('Arial', 14))
        current_dosage_label.setStyleSheet("color: white;")

        self.dosage_display = QLabel("0 mg")
        self.dosage_display.setFont(QFont('Arial', 30))
        self.dosage_display.setAlignment(Qt.AlignLeft)
        self.dosage_display.setStyleSheet("color: #3498db;")  # Updated color

        # Create a small animation for dispensing
        self.dispensing_animation_label = QLabel()
        self.dispensing_animation_label.setAlignment(Qt.AlignLeft)
        self.dispensing_animation_label.setFixedSize(30, 30)  # Set fixed size for the animation
        self.dispensing_animation = QMovie("dispensing.gif")  # Add your dispensing GIF here
        self.dispensing_animation_label.setMovie(self.dispensing_animation)

        dosage_layout.addWidget(drug_delivery_label)
        dosage_layout.addWidget(current_dosage_label)  # Add current dosage label
        dosage_layout.addWidget(self.dosage_display)

        # Add dispensing animation next to dosage
        dosage_layout.addWidget(self.dispensing_animation_label)  # Add dispensing animation
        dosage_layout.addWidget(self.scroll_area)  # Adding the scrollable area
        dosage_layout.addWidget(self.dispensing_label)  # Dispensing label at the bottom

        dosage_widget.setLayout(dosage_layout)
        splitter.addWidget(dosage_widget)

        splitter.setSizes([3 * self.width() // 4, self.width() // 4])  # Adjust size ratio (3/4 and 1/4)
        return splitter

    def create_tabs_panel(self):
        tabs = QTabWidget()

        # Tab for Settings
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        settings_layout.addWidget(QLabel("This is the Settings tab"))
        settings_tab.setLayout(settings_layout)
        tabs.addTab(settings_tab, "Settings")

        # Tab for Logs
        logs_tab = QWidget()
        logs_layout = QVBoxLayout()
        logs_layout.addWidget(QLabel("This is the Logs tab"))
        logs_tab.setLayout(logs_layout)
        tabs.addTab(logs_tab, "Logs")

        # Tab for Patient Data
        patient_data_tab = QWidget()
        patient_data_layout = QVBoxLayout()
        patient_data_layout.addWidget(QLabel("This is the Patient Data tab"))
        patient_data_tab.setLayout(patient_data_layout)
        tabs.addTab(patient_data_tab, "Patient Data")

        # Tab for Protocols
        protocols_tab = QWidget()
        protocols_layout = QVBoxLayout()

        # Form to add a new protocol
        protocol_form_layout = QVBoxLayout()
        protocol_form_layout.addWidget(QLabel("Add New Protocol"))

        self.protocol_name_input = QLineEdit()
        self.protocol_name_input.setPlaceholderText("Protocol Name")
        protocol_form_layout.addWidget(self.protocol_name_input)

        self.protocol_id_input = QLineEdit()
        self.protocol_id_input.setPlaceholderText("Protocol ID")
        protocol_form_layout.addWidget(self.protocol_id_input)

        self.protocol_seizure_duration_input = QLineEdit()
        self.protocol_seizure_duration_input.setPlaceholderText("Seizure Duration Threshold (minutes)")
        protocol_form_layout.addWidget(self.protocol_seizure_duration_input)

        self.protocol_total_duration_input = QLineEdit()
        self.protocol_total_duration_input.setPlaceholderText("Total Duration (minutes)")
        protocol_form_layout.addWidget(self.protocol_total_duration_input)

        # Steps input
        self.protocol_steps_input = QTextEdit()
        self.protocol_steps_input.setPlaceholderText("Steps (JSON format)")
        protocol_form_layout.addWidget(self.protocol_steps_input)

        add_protocol_button = QPushButton("Add Protocol")
        add_protocol_button.clicked.connect(self.add_protocol_from_ui)
        protocol_form_layout.addWidget(add_protocol_button)

        protocols_layout.addLayout(protocol_form_layout)

        # List of existing protocols
        self.protocol_list_widget = QListWidget()
        protocols_layout.addWidget(QLabel("Existing Protocols"))
        protocols_layout.addWidget(self.protocol_list_widget)

        # Set layout
        protocols_tab.setLayout(protocols_layout)
        tabs.addTab(protocols_tab, "Protocols")

        return tabs

    def add_protocol_from_ui(self):
        protocol_id = int(self.protocol_id_input.text())
        name = self.protocol_name_input.text()
        seizure_duration_threshold = float(self.protocol_seizure_duration_input.text())
        total_duration = float(self.protocol_total_duration_input.text())
        steps_text = self.protocol_steps_input.toPlainText()
        import json
        try:
            steps = json.loads(steps_text)
            # steps should be a list of dicts with 'duration' and 'dose_mg'
            self.protocol_manager.add_protocol(protocol_id, name, seizure_duration_threshold, steps, total_duration)
            # Update protocol list
            self.protocol_list_widget.addItem(f"{protocol_id}: {name}")
            # Clear inputs
            self.protocol_name_input.clear()
            self.protocol_id_input.clear()
            self.protocol_seizure_duration_input.clear()
            self.protocol_total_duration_input.clear()
            self.protocol_steps_input.clear()
        except json.JSONDecodeError as e:
            print("Invalid steps format. Please enter valid JSON.")
            # Show a message box or error message (not implemented here)

    def start_eeg(self):
        self.timer.start(100)  # Update every 100 ms
        print("EEG started")

    def stop_eeg(self):
        self.timer.stop()  # Stop updating
        print("EEG stopped")

    def update_eeg_plot(self):
        # Simulating data acquisition from the serial port
        import random
        self.data_buffer.append(random.uniform(-1, 1))  # Simulate EEG data

        # Update the EEG plot (up to the last 100 points)
        self.eeg_plot.setData(self.data_buffer[-100:])

    def on_seizure_detected(self):
        print("Seizure detected!")
        self.seizure_detected_label.setVisible(True)  # Show the seizure detected indicator
        # Start the protocol (for now, we can hardcode protocol_id=1)
        self.protocol_manager.start_protocol(1)

    def on_dose_to_administer(self, dose_mg):
        # Update the current dosage display
        self.dosage_display.setText(f"{dose_mg} mg")
        # Start dispensing animation
        self.dispensing_animation.start()
        # Show dispensing label
        self.dispensing_label.setVisible(True)
        # Stop the animation after some time
        QTimer.singleShot(2000, self.dispensing_animation.stop)
        QTimer.singleShot(2000, lambda: self.dispensing_label.setVisible(False))

    def update_dosage_schedule(self, schedule):
        # Clear the scroll area and update with new schedule
        for i in reversed(range(self.scroll_layout.count())):
            widget_to_remove = self.scroll_layout.itemAt(i).widget()
            self.scroll_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

        for entry in schedule:
            time_str = entry['time'].toString("hh:mm:ss")
            dose_str = f"{entry['dose_mg']} mg"
            ts = f"{time_str} - Dosage: {dose_str}"
            # Create rectangle notification-style for each timestamp
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setStyleSheet("background-color: #2c3e50; padding: 5px; border-radius: 10px;")  # Reduced padding

            layout_in_frame = QVBoxLayout()
            time_label = QLabel(time_str)
            time_label.setFont(QFont('Arial', 10, QFont.Bold))  # Bold font for time
            time_label.setStyleSheet("color: white;")
            timestamp_label = QLabel(f"Dosage: {dose_str}")
            timestamp_label.setFont(QFont('Arial', 9))  # Smaller font for dosage info
            timestamp_label.setStyleSheet("color: white;")
            layout_in_frame.addWidget(time_label)  # Time at the top
            layout_in_frame.addWidget(timestamp_label)  # Dosage information

            frame.setLayout(layout_in_frame)

            self.scroll_layout.addWidget(frame)

    def on_protocol_started(self, protocol_name):
        print(f"Protocol {protocol_name} started.")

    def on_protocol_completed(self, protocol_name):
        print(f"Protocol {protocol_name} completed.")
        # Hide the seizure detected label
        self.seizure_detected_label.setVisible(False)

    def closeEvent(self, event):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()  # Close the serial port on exit
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))  # Apply dark style
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
