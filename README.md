# Seizure Detection and Medication Administration System

## Overview

This project is a graphical user interface (GUI) application designed to detect seizures and manage medication administration for patients. It utilizes PyQt5 for the GUI, PyQtGraph for real-time EEG plotting, and includes a simulated seizure detection mechanism. The application is capable of defining protocols for medication delivery based on detected seizures.

## Features

- **Seizure Detection**: Monitors for seizure events using a simulated random detection algorithm.
- **Medication Protocol Management**: Allows the addition and management of medication protocols with defined doses and timings.
- **Real-Time EEG Visualization**: Displays EEG data in real-time using PyQtGraph.
- **User-Friendly Interface**: Intuitive layout with clear indications of seizure events and medication administration.

## Technologies Used

- Python
- PyQt5
- PyQtGraph
- Serial Communication (for potential integration with medical devices)

## Installation

To set up the project on your local machine, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
Navigate to the project directory:

bash
Copy code
cd <project-directory>
Install the required packages: Make sure you have Python installed, then run:

bash
Copy code
pip install PyQt5 pyqtgraph qdarkstyle pyserial
Run the application:

bash
Copy code
python main.py
Usage
Launch the application.
Press the "Start EEG" button to begin monitoring for seizure activity.
When a seizure is detected, the application will display a notification and begin administering the predefined medication protocol.
The dosage and administration schedule will be displayed in the Drug Dosage panel.
Code Structure
main.py: Contains the main application logic and GUI components.
SeizureDetector: Class responsible for simulating seizure detection.
SeizureProtocolManager: Manages medication protocols and their administration.
MainWindow: The main GUI class that organizes the layout and user interaction.
Contributing
Contributions are welcome! If you would like to contribute to this project, please follow these steps:

Fork the repository.
Create a new branch for your feature:
bash
Copy code
git checkout -b feature/my-feature
Make your changes and commit them:
bash
Copy code
git commit -m "Add my feature"
Push to your branch:
bash
Copy code
git push origin feature/my-feature
Create a pull request.
License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgements
PyQt5 for the GUI framework
PyQtGraph for the EEG visualization
The community for inspiration and support
