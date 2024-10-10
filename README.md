Medical Device UI
A PyQt5 application for managing patient data, EEG monitoring, seizure detection, medication protocols, and more.

Table of Contents
Features
Installation
Usage
Application Overview
Top Bar
EEG Panel
Drug Dosage Panel
Tabs
Dependencies
Inputting JSON Protocols
Contributing
License
Features
Patient Data Management: Input and save patient information such as name, age, and ID. View detailed patient data in a popup window, including EEG data, medications administered, logs, etc.
EEG Monitoring: Start and stop EEG data acquisition with simulated data. View real-time EEG plots.
Seizure Detection: Simulated seizure detection with an "Active Seizure" indicator widget.
Medication Protocols: Manage medication protocols for seizures. Add new protocols manually or by inputting JSON content directly. Start protocols manually or automatically upon seizure detection.
Medication Administration: Dispense medications manually or automatically according to protocols. View dosage schedules and logs.
Recording and Logging: Record EEG data and events such as seizures and medication administrations.
Settings: Adjust application settings such as enabling auto mode and setting the seizure detection interval.
AI Model Updates: Simulate updating an AI model with new data.
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/medical-device-ui.git
cd medical-device-ui
Install Python 3.6+: Ensure you have Python 3.6 or newer installed.

Create a virtual environment (optional but recommended):

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Note: The requirements.txt should contain:

Copy code
PyQt5
pyqtgraph
qdarkstyle
Usage
Run the application with:

bash
Copy code
python main.py
Application Overview
Top Bar
Navigation Buttons: Home, Patient Data, Seizure Stats, Logs, Settings.
Auto Mode Toggle: Enable or disable automatic seizure detection.
Active Seizure Indicator: Displays "Active Seizure" when a seizure is detected.
EEG Panel
Controls: Start EEG, Stop EEG, Save EEG Data, Record.
EEG Plot: Displays real-time EEG data.
Drug Dosage Panel
Manual Dispense Button: Dispense medication manually.
Dosage Schedule: View upcoming medication doses.
Tabs
Patient Data: Input and save patient information.
Seizure Stats: Manually mark the start and end of seizure episodes.
Protocols: Manage medication protocols.
Add Protocol: Create new protocols by specifying ID, name, seizure duration threshold, and steps.
Load Protocol from JSON: Input JSON content directly to load protocols.
Start Selected Protocol: Start a protocol manually.
Logs: View medication administration logs.
AI Model: Simulate updating the AI model with new data.
Settings: Adjust application settings.
Dependencies
Python 3.6+
PyQt5
pyqtgraph
qdarkstyle
Install dependencies using:

bash
Copy code
pip install PyQt5 pyqtgraph qdarkstyle
Inputting JSON Protocols
When adding protocols via JSON:

Navigate to the Protocols tab.
Click on "Load Protocol from JSON".
A popup window will appear where you can type or paste the JSON content directly.
After entering the JSON content, click "OK" to validate and load the protocol(s).
If the JSON is valid and contains all required keys, the protocol will be added to the list.
Example JSON Content:

json
Copy code
{
    "id": 2,
    "name": "Emergency Protocol",
    "seizure_duration_threshold": 1.5,
    "steps": [
        {"duration": 0.5, "dose_mg": 10, "medication": "Diazepam (Valium)"},
        {"duration": 1, "dose_mg": 5, "medication": "Lorazepam (Ativan)"}
    ]
}
Required Keys:

id: Unique identifier for the protocol.
name: Name of the protocol.
seizure_duration_threshold: Duration threshold to trigger the protocol (in minutes).
steps: A list of steps, each containing:
duration: Duration of the step (in minutes).
dose_mg: Dose to administer (in mg).
medication: Name of the medication.
Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

Fork the repository.

Create a new branch:

bash
Copy code
git checkout -b feature/YourFeature
Commit your changes:

bash
Copy code
git commit -am 'Add your feature'
Push to the branch:

bash
Copy code
git push origin feature/YourFeature
Open a pull request.

License
This project is licensed under the MIT License.
