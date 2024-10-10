import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
    QTabWidget, QScrollArea, QFrame, QInputDialog, QSplitter, QSizePolicy, QLineEdit,
    QTextEdit, QListWidget, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox, QDialogButtonBox,
    QFileDialog, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QObject, pyqtSignal
from PyQt5.QtGui import QFont
import pyqtgraph as pg
import qdarkstyle
import json
import os
import threading
import datetime

class SeizureDetector(QObject):
    seizure_detected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.detect_seizure)
        # Start detection only when auto mode is enabled

    def start_detection(self):
        self.timer.start(1000)  # Check every second
        print("Seizure detection started.")

    def stop_detection(self):
        self.timer.stop()
        print("Seizure detection stopped.")

    def detect_seizure(self):
        import random
        # Randomly simulate seizure detection
        if random.randint(0, 100) < 5:  # 5% chance every second
            self.seizure_detected.emit()
            # Do not stop the timer to allow continuous detection

class SeizureProtocolManager(QObject):
    dose_to_administer = pyqtSignal(float, str)  # Signal with dose in mg and medication name
    protocol_started = pyqtSignal(str)  # Signal with protocol name
    protocol_completed = pyqtSignal(str)
    new_schedule = pyqtSignal(list)  # Signal with list of timestamps and doses
    protocol_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.protocols = {}  # Store all protocols
        self.current_protocol = None
        self.current_protocol_timer = None
        self.step_index = 0
        self.schedule = []

    def add_protocol(self, protocol_id, name, seizure_duration_threshold, steps, total_duration):
        """Add a new protocol to the system."""
        self.protocols[protocol_id] = {
            "id": protocol_id,
            "name": name,
            "seizure_duration_threshold": seizure_duration_threshold,  # in minutes
            "steps": steps,  # list of dicts with 'duration' in minutes, 'dose_mg', 'medication'
            "total_duration": total_duration  # in minutes
        }
        print(f"Added {name} (Protocol {protocol_id}) to the system.")
        self.protocol_updated.emit()

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
            medication = step.get('medication', 'Unknown')
            timestamp = current_time.addSecs(duration * 60)
            self.schedule.append({'time': timestamp, 'dose_mg': dose_mg, 'medication': medication})
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
        medication = step.get('medication', 'Unknown')
        self.dose_to_administer.emit(dose_mg, medication)
        print(f"Administering {dose_mg} mg of {medication} at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.")

        # Schedule next dose
        duration = step['duration']  # in minutes
        self.current_protocol_timer = QTimer()
        self.current_protocol_timer.setSingleShot(True)
        self.current_protocol_timer.timeout.connect(self.administer_next_dose)
        self.current_protocol_timer.start(duration * 60 * 1000)  # Convert to milliseconds

        self.step_index += 1

class AddProtocolDialog(QDialog):
    def __init__(self, medications):
        super().__init__()
        self.setWindowTitle("Add Protocol")
        self.medications = medications
        self.steps = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.protocol_id_input = QSpinBox()
        self.protocol_id_input.setMinimum(1)
        form_layout.addRow("Protocol ID:", self.protocol_id_input)

        self.protocol_name_input = QLineEdit()
        form_layout.addRow("Protocol Name:", self.protocol_name_input)

        self.seizure_duration_input = QDoubleSpinBox()
        self.seizure_duration_input.setDecimals(2)
        self.seizure_duration_input.setMinimum(0.1)
        self.seizure_duration_input.setMaximum(999.99)
        form_layout.addRow("Seizure Duration Threshold (minutes):", self.seizure_duration_input)

        layout.addLayout(form_layout)

        # Steps table
        self.steps_list_widget = QListWidget()
        layout.addWidget(QLabel("Protocol Steps:"))
        layout.addWidget(self.steps_list_widget)

        # Buttons to add and remove steps
        steps_buttons_layout = QHBoxLayout()
        add_step_button = QPushButton("Add Step")
        add_step_button.clicked.connect(self.add_step_dialog)
        remove_step_button = QPushButton("Remove Selected Step")
        remove_step_button.clicked.connect(self.remove_selected_step)
        steps_buttons_layout.addWidget(add_step_button)
        steps_buttons_layout.addWidget(remove_step_button)
        layout.addLayout(steps_buttons_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def add_step_dialog(self):
        dialog = AddStepDialog(self.medications)
        if dialog.exec_() == QDialog.Accepted:
            step = {
                'duration': dialog.duration_input.value(),
                'dose_mg': dialog.dose_input.value(),
                'medication': dialog.medication_input.currentText()
            }
            self.steps.append(step)
            self.steps_list_widget.addItem(f"Duration: {step['duration']} min, Dose: {step['dose_mg']} mg, Medication: {step['medication']}")

    def remove_selected_step(self):
        selected_items = self.steps_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Remove Step", "Please select a step to remove.")
            return
        index = self.steps_list_widget.row(selected_items[0])
        self.steps_list_widget.takeItem(index)
        del self.steps[index]

    def get_protocol_data(self):
        protocol_id = self.protocol_id_input.value()
        name = self.protocol_name_input.text()
        seizure_duration_threshold = self.seizure_duration_input.value()
        steps = self.steps
        total_duration = sum(step['duration'] for step in steps)
        return protocol_id, name, seizure_duration_threshold, steps, total_duration

class AddStepDialog(QDialog):
    def __init__(self, medications):
        super().__init__()
        self.setWindowTitle("Add Protocol Step")
        self.medications = medications
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.duration_input = QDoubleSpinBox()
        self.duration_input.setDecimals(2)
        self.duration_input.setMinimum(0.1)
        self.duration_input.setMaximum(999.99)
        layout.addRow("Duration (minutes):", self.duration_input)

        self.dose_input = QDoubleSpinBox()
        self.dose_input.setDecimals(2)
        self.dose_input.setMinimum(0.01)
        self.dose_input.setMaximum(9999.99)
        layout.addRow("Dose (mg):", self.dose_input)

        self.medication_input = QComboBox()
        self.populate_medication_list()
        layout.addRow("Medication:", self.medication_input)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def populate_medication_list(self):
        # Flatten the medications dictionary into a list of medications
        for category, meds in self.medications.items():
            self.medication_input.addItem(f"-- {category} --")
            for med in meds:
                self.medication_input.addItem(med)

class JsonInputDialog(QDialog):
    """Custom dialog to input JSON content."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Input JSON Content")
        self.resize(600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Paste or type JSON content here...")
        layout.addWidget(self.text_edit)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_json)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def validate_json(self):
        content = self.text_edit.toPlainText()
        try:
            self.json_data = json.loads(content)
            self.accept()
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"Error parsing JSON:\n{e}")

    def get_json_data(self):
        return self.json_data

class PatientDataPopup(QDialog):
    def __init__(self, parent=None, patient_data=None):
        super().__init__(parent)
        self.setWindowTitle("Patient Data")
        self.setGeometry(200, 200, 600, 400)
        self.patient_data = patient_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Display patient info
        patient_info_group = QGroupBox("Patient Information")
        patient_info_layout = QFormLayout()
        patient_info_layout.addRow("Name:", QLabel(self.patient_data.get('name', 'N/A')))
        patient_info_layout.addRow("Age:", QLabel(self.patient_data.get('age', 'N/A')))
        patient_info_layout.addRow("ID:", QLabel(self.patient_data.get('id', 'N/A')))
        patient_info_group.setLayout(patient_info_layout)
        layout.addWidget(patient_info_group)

        # Display EEG data
        eeg_group = QGroupBox("EEG Data")
        eeg_layout = QVBoxLayout()
        eeg_text_edit = QTextEdit()
        eeg_text_edit.setReadOnly(True)
        eeg_text = "\n".join([f"{data['timestamp']}: {data['value']}" for data in self.patient_data.get('eeg_data', [])])
        eeg_text_edit.setPlainText(eeg_text)
        eeg_layout.addWidget(eeg_text_edit)
        eeg_group.setLayout(eeg_layout)
        layout.addWidget(eeg_group)

        # Display medications used
        meds_group = QGroupBox("Medications Administered")
        meds_layout = QVBoxLayout()
        meds_text_edit = QTextEdit()
        meds_text_edit.setReadOnly(True)
        meds_text = "\n".join([f"{log}" for log in self.patient_data.get('med_logs', [])])
        meds_text_edit.setPlainText(meds_text)
        meds_layout.addWidget(meds_text_edit)
        meds_group.setLayout(meds_layout)
        layout.addWidget(meds_group)

        # Display logs
        logs_group = QGroupBox("Logs")
        logs_layout = QVBoxLayout()
        logs_text_edit = QTextEdit()
        logs_text_edit.setReadOnly(True)
        logs_text = self.patient_data.get('logs', '')
        logs_text_edit.setPlainText(logs_text)
        logs_layout.addWidget(logs_text_edit)
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)

        # Set layout
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Medical Device UI")
        self.setGeometry(100, 100, 1200, 800)

        # Serial Port and Connection setup
        self.serial_port = None
        self.data_buffer = []  # Buffer to store data from the serial port
        self.eeg_data = []  # Store EEG data with timestamps

        # Recording and Auto Mode Flags
        self.is_recording = False
        self.auto_mode = False
        self.seizure_active = False  # To track if a seizure is currently active

        # Instantiate SeizureDetector and SeizureProtocolManager
        self.seizure_detector = SeizureDetector()
        self.protocol_manager = SeizureProtocolManager()

        # Connect signals
        self.seizure_detector.seizure_detected.connect(self.on_seizure_detected)
        self.protocol_manager.dose_to_administer.connect(self.on_dose_to_administer)
        self.protocol_manager.new_schedule.connect(self.update_dosage_schedule)
        self.protocol_manager.protocol_started.connect(self.on_protocol_started)
        self.protocol_manager.protocol_completed.connect(self.on_protocol_completed)
        self.protocol_manager.protocol_updated.connect(self.update_protocol_list)

        # Medications Data
        self.medications = {
            'EEG': [
                'Levetiracetam (Keppra)',
                'Phenytoin (Dilantin)',
                'Valproate (Depakote)',
                'Lacosamide (Vimpat)',
                'Lorazepam (Ativan)',
                'Diazepam (Valium)',
                'Propofol'
            ],
            'ECG/EKG': [
                'Amiodarone',
                'Lidocaine',
                'Sotalol',
                'Heparin',
                'Warfarin',
                'Metoprolol'
            ],
            'EMG': [
                'Baclofen',
                'Dantrolene',
                'Pyridostigmine (Mestinon)'
            ]
        }

        # Add default protocol
        self.protocol_manager.add_protocol(
            protocol_id=1,
            name="Default Protocol",
            seizure_duration_threshold=2,  # Seizure must last for 2 minutes
            steps=[
                {"duration": 1, "dose_mg": 5, "medication": "Levetiracetam (Keppra)"},    # First 1 minute
                {"duration": 1, "dose_mg": 2.5, "medication": "Phenytoin (Dilantin)"},  # Next 1 minute
                {"duration": 1, "dose_mg": 1, "medication": "Valproate (Depakote)"},    # Next 1 minute
                {"duration": 1, "dose_mg": 0.5, "medication": "Lacosamide (Vimpat)"}   # Final 1 minute
            ],
            total_duration=4  # Total duration of the protocol: 4 minutes
        )

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
        self.tabs = tabs_panel  # Save the tabs widget
        self.tabs.currentChanged.connect(self.on_tab_changed)

        central_widget.setLayout(layout)

        # Timer for updating the EEG graph from serial data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_eeg_plot)

        # Initialize medication logs
        self.medication_logs = []

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
            # Connect buttons to respective functions
            if btn == "Home":
                button.clicked.connect(self.go_home)
            elif btn == "Patient Data":
                button.clicked.connect(lambda: self.tabs.setCurrentIndex(self.tabs.indexOf(self.patient_data_tab)))
            elif btn == "Seizure Stats":
                button.clicked.connect(lambda: self.tabs.setCurrentIndex(self.tabs.indexOf(self.seizure_stats_tab)))
            elif btn == "Logs":
                button.clicked.connect(lambda: self.tabs.setCurrentIndex(self.tabs.indexOf(self.logs_tab)))
            elif btn == "Settings":
                button.clicked.connect(lambda: self.tabs.setCurrentIndex(self.tabs.indexOf(self.settings_tab)))
            top_bar_layout.addWidget(button)

        # Add "Auto" button
        self.auto_button = QPushButton("Auto")
        self.auto_button.setCheckable(True)
        self.auto_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-size: 14px;
                border: none;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:checked {
                background-color: #2ecc71;
            }
        """)
        self.auto_button.clicked.connect(self.toggle_auto_mode)
        top_bar_layout.addWidget(self.auto_button)

        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        top_bar_layout.addWidget(spacer)

        # Add seizure detected label
        self.seizure_detected_label = QLabel("Active Seizure")
        self.seizure_detected_label.setStyleSheet("""
            QLabel {
                background-color: #e67e22;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
            }
        """)
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
        save_eeg_button = QPushButton("Save EEG Data")
        record_button = QPushButton("Record")  # Added Record button

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
        save_eeg_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #2ecc71;
            }
            QPushButton:hover {
                background-color: #27ae60;
                color: white;
            }
        """)
        record_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #e74c3c;
            }
            QPushButton:checked {
                background-color: #c0392b;
            }
        """)

        start_eeg_button.clicked.connect(self.start_eeg)
        stop_eeg_button.clicked.connect(self.stop_eeg)
        save_eeg_button.clicked.connect(self.save_eeg_data)
        record_button.setCheckable(True)
        record_button.clicked.connect(self.toggle_recording)
        self.record_button = record_button  # Keep a reference to change text

        button_layout.addWidget(start_eeg_button)
        button_layout.addWidget(stop_eeg_button)
        button_layout.addWidget(save_eeg_button)
        button_layout.addWidget(record_button)

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

        # Dispense button
        dispense_button = QPushButton("Dispense Medication Manually")
        dispense_button.clicked.connect(self.manual_dispense_medication)
        dispense_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #e67e22;
            }
            QPushButton:hover {
                background-color: #d35400;
                color: white;
            }
        """)

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

        dosage_layout.addWidget(drug_delivery_label)
        dosage_layout.addWidget(dispense_button)
        dosage_layout.addWidget(self.scroll_area)

        dosage_widget.setLayout(dosage_layout)
        splitter.addWidget(dosage_widget)

        splitter.setSizes([3 * self.width() // 4, self.width() // 4])  # Adjust size ratio (3/4 and 1/4)
        return splitter

    def create_tabs_panel(self):
        tabs = QTabWidget()

        # Tab for Patient Data
        patient_data_tab = QWidget()
        patient_data_layout = QVBoxLayout()

        # Patient data form
        patient_form_layout = QVBoxLayout()
        self.patient_name_input = QLineEdit()
        self.patient_age_input = QLineEdit()
        self.patient_id_input = QLineEdit()
        patient_form_layout.addWidget(QLabel("Patient Name:"))
        patient_form_layout.addWidget(self.patient_name_input)
        patient_form_layout.addWidget(QLabel("Patient Age:"))
        patient_form_layout.addWidget(self.patient_age_input)
        patient_form_layout.addWidget(QLabel("Patient ID:"))
        patient_form_layout.addWidget(self.patient_id_input)

        save_patient_data_button = QPushButton("Save Patient Data")
        save_patient_data_button.clicked.connect(self.save_patient_data)
        patient_data_layout.addLayout(patient_form_layout)
        patient_data_layout.addWidget(save_patient_data_button)
        patient_data_tab.setLayout(patient_data_layout)
        tabs.addTab(patient_data_tab, "Patient Data")
        self.patient_data_tab = patient_data_tab  # Store reference

        # Tab for Seizure Stats
        seizure_stats_tab = QWidget()
        seizure_stats_layout = QVBoxLayout()

        # Mark Seizure Episode Button
        mark_seizure_button = QPushButton("Mark Seizure Episode")
        mark_seizure_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #e74c3c;
            }
            QPushButton:hover {
                background-color: #c0392b;
                color: white;
            }
        """)
        mark_seizure_button.clicked.connect(self.manually_mark_seizure)

        # Stop Seizure Episode Button
        stop_seizure_button = QPushButton("Stop Seizure Episode")
        stop_seizure_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #2ecc71;
            }
            QPushButton:hover {
                background-color: #27ae60;
                color: white;
            }
        """)
        stop_seizure_button.clicked.connect(self.manually_stop_seizure)

        # Add buttons to layout
        seizure_stats_layout.addWidget(mark_seizure_button)
        seizure_stats_layout.addWidget(stop_seizure_button)

        seizure_stats_tab.setLayout(seizure_stats_layout)
        tabs.addTab(seizure_stats_tab, "Seizure Stats")
        self.seizure_stats_tab = seizure_stats_tab  # Store reference

        # Tab for Protocols
        protocols_tab = QWidget()
        protocols_layout = QVBoxLayout()

        # Protocol list
        self.protocol_list_widget = QListWidget()
        self.update_protocol_list()
        protocols_layout.addWidget(QLabel("Available Protocols:"))
        protocols_layout.addWidget(self.protocol_list_widget)

        # Buttons to add and start protocols
        protocol_buttons_layout = QHBoxLayout()
        add_protocol_button = QPushButton("Add Protocol")
        add_protocol_button.clicked.connect(self.add_protocol_dialog)
        load_protocol_button = QPushButton("Load Protocol from JSON")  # Modified Button
        load_protocol_button.clicked.connect(self.load_protocol_from_json)
        start_protocol_button = QPushButton("Start Selected Protocol")
        start_protocol_button.clicked.connect(self.start_selected_protocol)
        protocol_buttons_layout.addWidget(add_protocol_button)
        protocol_buttons_layout.addWidget(load_protocol_button)  # Add new button to layout
        protocol_buttons_layout.addWidget(start_protocol_button)
        protocols_layout.addLayout(protocol_buttons_layout)

        protocols_tab.setLayout(protocols_layout)
        tabs.addTab(protocols_tab, "Protocols")
        self.protocols_tab = protocols_tab  # Store reference

        # Tab for Logs
        logs_tab = QWidget()
        logs_layout = QVBoxLayout()
        logs_layout.addWidget(QLabel("Medication Administration Log:"))
        self.logs_text_edit = QTextEdit()
        self.logs_text_edit.setReadOnly(True)
        logs_layout.addWidget(self.logs_text_edit)
        logs_tab.setLayout(logs_layout)
        tabs.addTab(logs_tab, "Logs")
        self.logs_tab = logs_tab  # Store reference

        # Tab for AI Model Updates
        ai_tab = QWidget()
        ai_layout = QVBoxLayout()
        update_model_button = QPushButton("Update AI Model with New Data")
        update_model_button.clicked.connect(self.update_ai_model)
        ai_layout.addWidget(QLabel("This tab is for AI model management."))
        ai_layout.addWidget(update_model_button)
        ai_tab.setLayout(ai_layout)
        tabs.addTab(ai_tab, "AI Model")
        self.ai_tab = ai_tab  # Store reference

        # Tab for Settings
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()

        # Example settings
        auto_mode_checkbox = QCheckBox("Enable Auto Mode")
        auto_mode_checkbox.setChecked(self.auto_mode)
        auto_mode_checkbox.stateChanged.connect(self.toggle_auto_mode_from_settings)

        seizure_detection_interval_input = QSpinBox()
        seizure_detection_interval_input.setRange(1, 60)
        seizure_detection_interval_input.setValue(1)
        seizure_detection_interval_input.setSuffix(" sec")
        seizure_detection_interval_input.valueChanged.connect(self.set_seizure_detection_interval)

        settings_layout.addWidget(auto_mode_checkbox)
        settings_layout.addWidget(QLabel("Seizure Detection Interval:"))
        settings_layout.addWidget(seizure_detection_interval_input)

        settings_tab.setLayout(settings_layout)
        tabs.addTab(settings_tab, "Settings")
        self.settings_tab = settings_tab  # Store reference

        return tabs

    def start_eeg(self):
        self.timer.start(100)  # Update every 100 ms
        print("EEG started")
        # Record the start time
        self.eeg_start_time = datetime.datetime.now()
        self.eeg_data = []  # Clear previous EEG data

    def stop_eeg(self):
        self.timer.stop()  # Stop updating
        print("EEG stopped")
        # Record the stop time
        self.eeg_stop_time = datetime.datetime.now()

    def save_eeg_data(self):
        # Logic to save EEG data
        if not self.eeg_data:
            QMessageBox.warning(self, "Save EEG Data", "No EEG data to save.")
            return
        filename = f"EEG_Data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.eeg_data, f)
        print(f"EEG data saved to {filename}")
        QMessageBox.information(self, "Save EEG Data", f"EEG data has been saved to {filename}.")

    def save_patient_data(self):
        # Logic to save patient data
        patient_data = {
            'name': self.patient_name_input.text(),
            'age': self.patient_age_input.text(),
            'id': self.patient_id_input.text()
        }
        if not all(patient_data.values()):
            QMessageBox.warning(self, "Save Patient Data", "Please fill in all patient details.")
            return
        filename = f"Patient_Data_{patient_data['id']}.json"
        with open(filename, 'w') as f:
            json.dump(patient_data, f)
        print(f"Patient data saved to {filename}")
        QMessageBox.information(self, "Save Patient Data", f"Patient data has been saved to {filename}.")

    def manually_mark_seizure(self):
        # Logic to manually mark a seizure episode start
        if self.seizure_active:
            QMessageBox.warning(self, "Seizure Episode", "A seizure is already marked as active.")
            return
        self.seizure_active = True
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        event = {
            'timestamp': timestamp,
            'event': 'Seizure Start'
        }
        if self.is_recording:
            with open('seizure_events.json', 'a') as f:
                f.write(json.dumps(event) + '\n')
        print(f"Seizure episode started at {timestamp}")
        # Optional: Update UI to reflect seizure is active

    def manually_stop_seizure(self):
        # Logic to manually mark a seizure episode end
        if not self.seizure_active:
            QMessageBox.warning(self, "Seizure Episode", "No active seizure to stop.")
            return
        self.seizure_active = False
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        event = {
            'timestamp': timestamp,
            'event': 'Seizure Stop'
        }
        if self.is_recording:
            with open('seizure_events.json', 'a') as f:
                f.write(json.dumps(event) + '\n')
        print(f"Seizure episode stopped at {timestamp}")
        # Optional: Update UI to reflect seizure has ended

    def update_ai_model(self):
        # Logic to send data to backend AI model for training
        # This can be implemented as a separate thread to avoid freezing the UI
        threading.Thread(target=self.train_ai_model).start()

    def train_ai_model(self):
        print("AI model training started with new data...")
        # Simulate training process
        import time
        time.sleep(5)  # Simulate time-consuming training
        print("AI model updated with new data")
        QMessageBox.information(self, "AI Model Update", "AI model has been updated with new data.")

    def update_eeg_plot(self):
        # Simulating data acquisition from the serial port
        import random
        value = random.uniform(-1, 1)  # Simulate EEG data
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.data_buffer.append(value)
        if self.is_recording:
            self.eeg_data.append({'timestamp': timestamp, 'value': value})

        # Update the EEG plot (up to the last 100 points)
        self.eeg_plot.setData(self.data_buffer[-100:])

    def on_seizure_detected(self):
        if not self.auto_mode:
            print("Seizure detected, but auto mode is off. No action taken.")
            return
        print("Seizure detected!")
        self.seizure_detected_label.setVisible(True)  # Show the seizure detected indicator
        # Start the protocol (for now, we can hardcode protocol_id=1)
        self.protocol_manager.start_protocol(1)
        # Record the seizure event if recording
        if self.is_recording:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            event = {
                'timestamp': timestamp,
                'event': 'Seizure Detected'
            }
            with open('seizure_events.json', 'a') as f:
                f.write(json.dumps(event) + '\n')

    def on_dose_to_administer(self, dose_mg, medication):
        # No notification displayed
        # Update logs
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp}: Administered {dose_mg} mg of {medication}."
        self.logs_text_edit.append(log_entry)
        self.medication_logs.append(log_entry)  # Add this line
        # Record the medication event if recording
        if self.is_recording:
            event = {
                'timestamp': timestamp,
                'dose_mg': dose_mg,
                'medication': medication,
                'protocol': self.protocol_manager.current_protocol['name'] if self.protocol_manager.current_protocol else 'Manual'
            }
            with open('medication_log.json', 'a') as f:
                f.write(json.dumps(event) + '\n')
            print(f"Recorded medication event: {event}")

    def update_dosage_schedule(self, schedule):
        # Clear the scroll area and update with new schedule
        for i in reversed(range(self.scroll_layout.count())):
            widget_to_remove = self.scroll_layout.itemAt(i).widget()
            self.scroll_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

        for entry in schedule:
            time_str = entry['time'].toString("hh:mm:ss")
            dose_str = f"{entry['dose_mg']} mg"
            medication = entry.get('medication', 'Unknown')
            # Create rectangle notification-style for each timestamp
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setStyleSheet("background-color: #2c3e50; padding: 5px; border-radius: 10px;")

            layout_in_frame = QVBoxLayout()
            time_label = QLabel(time_str)
            time_label.setFont(QFont('Arial', 10, QFont.Bold))
            time_label.setStyleSheet("color: white;")
            dose_label = QLabel(f"Dose: {dose_str}")
            dose_label.setFont(QFont('Arial', 9))
            dose_label.setStyleSheet("color: white;")
            med_label = QLabel(f"Medication: {medication}")
            med_label.setFont(QFont('Arial', 9))
            med_label.setStyleSheet("color: white;")
            layout_in_frame.addWidget(time_label)
            layout_in_frame.addWidget(dose_label)
            layout_in_frame.addWidget(med_label)

            frame.setLayout(layout_in_frame)

            self.scroll_layout.addWidget(frame)

    def on_protocol_started(self, protocol_name):
        print(f"Protocol {protocol_name} started.")
        # Record the protocol start time
        self.protocol_start_time = datetime.datetime.now()
        # Update logs
        timestamp = self.protocol_start_time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp}: Protocol '{protocol_name}' started."
        self.logs_text_edit.append(log_entry)

    def on_protocol_completed(self, protocol_name):
        print(f"Protocol {protocol_name} completed.")
        # Hide the seizure detected label
        self.seizure_detected_label.setVisible(False)
        # Record the protocol completion
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp}: Protocol '{protocol_name}' completed."
        self.logs_text_edit.append(log_entry)

    def update_protocol_list(self):
        self.protocol_list_widget.clear()
        for protocol_id, protocol in self.protocol_manager.protocols.items():
            self.protocol_list_widget.addItem(f"ID: {protocol_id}, Name: {protocol['name']}")

    def add_protocol_dialog(self):
        # Open the custom AddProtocolDialog
        dialog = AddProtocolDialog(self.medications)
        if dialog.exec_() == QDialog.Accepted:
            protocol_id, name, seizure_duration_threshold, steps, total_duration = dialog.get_protocol_data()
            self.protocol_manager.add_protocol(
                protocol_id=protocol_id,
                name=name,
                seizure_duration_threshold=seizure_duration_threshold,
                steps=steps,
                total_duration=total_duration
            )
            QMessageBox.information(self, "Add Protocol", f"Protocol '{name}' added successfully.")

    def load_protocol_from_json(self):
        # Open a dialog to input JSON content
        dialog = JsonInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_json_data()
            # Validate and add protocol(s)
            if isinstance(data, dict):
                # Single protocol
                self.validate_and_add_protocol(data)
            elif isinstance(data, list):
                # Multiple protocols
                for protocol_data in data:
                    self.validate_and_add_protocol(protocol_data)
            else:
                QMessageBox.warning(self, "Load Protocol", "Invalid JSON format.")

    def validate_and_add_protocol(self, data):
        # Expected keys: id, name, seizure_duration_threshold, steps
        required_keys = {'id', 'name', 'seizure_duration_threshold', 'steps'}
        if not required_keys.issubset(data.keys()):
            QMessageBox.warning(self, "Load Protocol", f"Protocol data is missing required keys: {required_keys - set(data.keys())}")
            return
        protocol_id = data['id']
        name = data['name']
        seizure_duration_threshold = data['seizure_duration_threshold']
        steps = data['steps']
        # Validate steps
        if not isinstance(steps, list) or not steps:
            QMessageBox.warning(self, "Load Protocol", "Protocol steps are invalid or empty.")
            return
        total_duration = sum(step.get('duration', 0) for step in steps)
        self.protocol_manager.add_protocol(
            protocol_id=protocol_id,
            name=name,
            seizure_duration_threshold=seizure_duration_threshold,
            steps=steps,
            total_duration=total_duration
        )
        QMessageBox.information(self, "Load Protocol", f"Protocol '{name}' loaded successfully.")

    def start_selected_protocol(self):
        selected_items = self.protocol_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Start Protocol", "Please select a protocol to start.")
            return
        selected_text = selected_items[0].text()
        protocol_id = int(selected_text.split(',')[0].split(':')[1].strip())
        self.protocol_manager.start_protocol(protocol_id)

    def manual_dispense_medication(self):
        # Open a dialog to select medication and dose
        dialog = AddStepDialog(self.medications)
        dialog.setWindowTitle("Dispense Medication Manually")
        if dialog.exec_() == QDialog.Accepted:
            dose_mg = dialog.dose_input.value()
            medication = dialog.medication_input.currentText()
            # Update logs
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{timestamp}: Manually dispensed {dose_mg} mg of {medication}."
            self.logs_text_edit.append(log_entry)
            self.medication_logs.append(log_entry)  # Add this line
            # Record the medication event if recording
            if self.is_recording:
                event = {
                    'timestamp': timestamp,
                    'dose_mg': dose_mg,
                    'medication': medication,
                    'protocol': 'Manual'
                }
                with open('medication_log.json', 'a') as f:
                    f.write(json.dumps(event) + '\n')
                print(f"Recorded medication event: {event}")
            # No notification displayed

    def toggle_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.record_button.setText("Stop Recording")
            print("Recording started.")
        else:
            self.is_recording = False
            self.record_button.setText("Record")
            print("Recording stopped.")

    def toggle_auto_mode(self):
        self.auto_mode = self.auto_button.isChecked()
        if self.auto_mode:
            self.seizure_detector.start_detection()
            print("Auto mode enabled.")
        else:
            self.seizure_detector.stop_detection()
            print("Auto mode disabled.")
            # Hide seizure detected label if visible
            self.seizure_detected_label.setVisible(False)

    def toggle_auto_mode_from_settings(self, state):
        self.auto_mode = (state == Qt.Checked)
        self.auto_button.setChecked(self.auto_mode)
        self.toggle_auto_mode()

    def set_seizure_detection_interval(self, value):
        # Update the seizure detection interval
        self.seizure_detector.timer.setInterval(value * 1000)
        print(f"Seizure detection interval set to {value} seconds.")

    def on_tab_changed(self, index):
        tab_text = self.tabs.tabText(index)
        if tab_text == "Patient Data":
            self.show_patient_data_popup()

    def show_patient_data_popup(self):
        # Collect patient data
        patient_data = {
            'name': self.patient_name_input.text(),
            'age': self.patient_age_input.text(),
            'id': self.patient_id_input.text(),
            'eeg_data': self.eeg_data,
            'med_logs': self.medication_logs,
            'logs': self.logs_text_edit.toPlainText(),
        }
        self.patient_data_popup = PatientDataPopup(self, patient_data)
        self.patient_data_popup.exec_()

    def go_home(self):
        # For now, do nothing or implement as needed
        pass

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
