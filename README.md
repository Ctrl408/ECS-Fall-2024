\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{geometry}
\usepackage{longtable}
\usepackage{amsmath}
\geometry{margin=1in}

\lstset{
    language=Python,
    basicstyle=\ttfamily\small,
    keywordstyle=\color{blue},
    commentstyle=\color{green!50!black},
    stringstyle=\color{red},
    breaklines=true,
    showstringspaces=false,
    numberstyle=\tiny\color{gray},
    numbers=left,
    stepnumber=1,
    frame=single,
    tabsize=4,
    captionpos=b,
}

\title{Medical Device UI Documentation}
\author{Your Name}
\date{\today}

\begin{document}

\maketitle

\tableofcontents

\section{Introduction}

This document provides detailed documentation for the Medical Device UI application developed using PyQt5. The application is designed to manage patient data, monitor EEG signals, detect seizures, administer medications according to protocols, and more.

\section{Features}

\begin{itemize}
    \item \textbf{Patient Data Management}: Input and save patient information such as name, age, and ID. View detailed patient data in a popup window, including EEG data, medications administered, logs, etc.
    \item \textbf{EEG Monitoring}: Start and stop EEG data acquisition with simulated data. View real-time EEG plots.
    \item \textbf{Seizure Detection}: Simulated seizure detection with an "Active Seizure" indicator widget.
    \item \textbf{Medication Protocols}: Manage medication protocols for seizures. Add new protocols manually or by inputting JSON content directly. Start protocols manually or automatically upon seizure detection.
    \item \textbf{Medication Administration}: Dispense medications manually or automatically according to the protocols. View dosage schedules and logs.
    \item \textbf{Recording and Logging}: Record EEG data and events such as seizures and medication administrations.
    \item \textbf{Settings}: Adjust application settings such as enabling auto mode and setting the seizure detection interval.
    \item \textbf{AI Model Updates}: Simulate updating an AI model with new data.
\end{itemize}

\section{Installation}

\subsection{Prerequisites}

Ensure you have Python 3.6 or newer installed.

\subsection{Clone the Repository}

\begin{verbatim}
git clone https://github.com/yourusername/medical-device-ui.git
cd medical-device-ui
\end{verbatim}

\subsection{Create a Virtual Environment (Optional)}

\begin{verbatim}
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\end{verbatim}

\subsection{Install Dependencies}

\begin{verbatim}
pip install -r requirements.txt
\end{verbatim}

The \texttt{requirements.txt} should contain:

\begin{verbatim}
PyQt5
pyqtgraph
qdarkstyle
\end{verbatim}

\section{Usage}

Run the application with:

\begin{verbatim}
python main.py
\end{verbatim}

\section{Application Overview}

\subsection{Top Bar}

\begin{itemize}
    \item \textbf{Navigation Buttons}: Home, Patient Data, Seizure Stats, Logs, Settings.
    \item \textbf{Auto Mode Toggle}: Enable or disable automatic seizure detection.
    \item \textbf{Active Seizure Indicator}: Displays "Active Seizure" when a seizure is detected.
\end{itemize}

\subsection{EEG Panel}

\begin{itemize}
    \item \textbf{Controls}: Start EEG, Stop EEG, Save EEG Data, Record.
    \item \textbf{EEG Plot}: Displays real-time EEG data.
\end{itemize}

\subsection{Drug Dosage Panel}

\begin{itemize}
    \item \textbf{Manual Dispense Button}: Dispense medication manually.
    \item \textbf{Dosage Schedule}: View upcoming medication doses.
\end{itemize}

\subsection{Tabs}

\begin{itemize}
    \item \textbf{Patient Data}: Input and save patient information.
    \item \textbf{Seizure Stats}: Manually mark the start and end of seizure episodes.
    \item \textbf{Protocols}: Manage medication protocols.
        \begin{itemize}
            \item \textbf{Add Protocol}: Create new protocols by specifying ID, name, seizure duration threshold, and steps.
            \item \textbf{Load Protocol from JSON}: Input JSON content directly to load protocols.
            \item \textbf{Start Selected Protocol}: Start a protocol manually.
        \end{itemize}
    \item \textbf{Logs}: View medication administration logs.
    \item \textbf{AI Model}: Simulate updating the AI model with new data.
    \item \textbf{Settings}: Adjust application settings.
\end{itemize}

\section{Code Explanation}

The application consists of several classes, each handling specific functionalities.

\subsection{Main Components}

\begin{itemize}
    \item \texttt{SeizureDetector}: Simulates seizure detection.
    \item \texttt{SeizureProtocolManager}: Manages medication protocols.
    \item \texttt{AddProtocolDialog}: Dialog to add new protocols.
    \item \texttt{AddStepDialog}: Dialog to add steps to a protocol.
    \item \texttt{JsonInputDialog}: Dialog to input JSON content for protocols.
    \item \texttt{PatientDataPopup}: Displays patient data in a popup window.
    \item \texttt{MainWindow}: The main application window.
\end{itemize}

\subsection{Class Descriptions}

\subsubsection{SeizureDetector}

Simulates seizure detection using a QTimer. It emits a signal \texttt{seizure\_detected} when a seizure is detected.

\begin{lstlisting}
class SeizureDetector(QObject):
    seizure_detected = pyqtSignal()
    ...
\end{lstlisting}

\subsubsection{SeizureProtocolManager}

Manages medication protocols. It can add protocols, start them, and administer doses according to the protocol steps.

\begin{lstlisting}
class SeizureProtocolManager(QObject):
    dose_to_administer = pyqtSignal(float, str)
    protocol_started = pyqtSignal(str)
    protocol_completed = pyqtSignal(str)
    ...
\end{lstlisting}

\subsubsection{AddProtocolDialog}

A dialog window that allows users to add new medication protocols manually.

\begin{lstlisting}
class AddProtocolDialog(QDialog):
    def __init__(self, medications):
        ...
\end{lstlisting}

\subsubsection{AddStepDialog}

A dialog window to add steps to a medication protocol.

\begin{lstlisting}
class AddStepDialog(QDialog):
    def __init__(self, medications):
        ...
\end{lstlisting}

\subsubsection{JsonInputDialog}

A dialog window that allows users to input JSON content directly for loading protocols.

\begin{lstlisting}
class JsonInputDialog(QDialog):
    def __init__(self):
        ...
\end{lstlisting}

\subsubsection{PatientDataPopup}

Displays detailed patient data in a popup window when the "Patient Data" tab is clicked.

\begin{lstlisting}
class PatientDataPopup(QDialog):
    def __init__(self, parent=None, patient_data=None):
        ...
\end{lstlisting}

\subsubsection{MainWindow}

The main window of the application. It sets up the UI components and handles interactions.

\begin{lstlisting}
class MainWindow(QMainWindow):
    def __init__(self):
        ...
\end{lstlisting}

\section{Full Source Code}

\begin{lstlisting}[language=Python]
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

# ... (Include the rest of the classes and code as provided in the previous assistant's response)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))  # Apply dark style
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
\end{lstlisting}

\section{Dependencies}

\begin{itemize}
    \item Python 3.6+
    \item PyQt5
    \item pyqtgraph
    \item qdarkstyle
\end{itemize}

Install dependencies using:

\begin{verbatim}
pip install PyQt5 pyqtgraph qdarkstyle
\end{verbatim}

\section{Inputting JSON Protocols}

When adding protocols via JSON:

\begin{enumerate}
    \item Navigate to the \textbf{Protocols} tab.
    \item Click on \textbf{"Load Protocol from JSON"}.
    \item A popup window will appear where you can type or paste the JSON content directly.
    \item After entering the JSON content, click \textbf{"OK"} to validate and load the protocol(s).
    \item If the JSON is valid and contains all required keys, the protocol will be added to the list.
\end{enumerate}

\subsection{Example JSON Content}

\begin{verbatim}
{
    "id": 2,
    "name": "Emergency Protocol",
    "seizure_duration_threshold": 1.5,
    "steps": [
        {"duration": 0.5, "dose_mg": 10, "medication": "Diazepam (Valium)"},
        {"duration": 1, "dose_mg": 5, "medication": "Lorazepam (Ativan)"}
    ]
}
\end{verbatim}

\subsection{Required Keys}

\begin{itemize}
    \item \texttt{id}: Unique identifier for the protocol.
    \item \texttt{name}: Name of the protocol.
    \item \texttt{seizure\_duration\_threshold}: Duration threshold to trigger the protocol (in minutes).
    \item \texttt{steps}: A list of steps, each containing:
        \begin{itemize}
            \item \texttt{duration}: Duration of the step (in minutes).
            \item \texttt{dose\_mg}: Dose to administer (in mg).
            \item \texttt{medication}: Name of the medication.
        \end{itemize}
\end{itemize}

\section{Contributing}

Contributions are welcome! Please fork the repository and submit a pull request.

\begin{enumerate}
    \item \textbf{Fork the repository}.
    \item \textbf{Create a new branch}:

    \begin{verbatim}
    git checkout -b feature/YourFeature
    \end{verbatim}

    \item \textbf{Commit your changes}:

    \begin{verbatim}
    git commit -am 'Add your feature'
    \end{verbatim}

    \item \textbf{Push to the branch}:

    \begin{verbatim}
    git push origin feature/YourFeature
    \end{verbatim}

    \item \textbf{Open a pull request}.
\end{enumerate}

\section{License}

This project is licensed under the MIT License.

\end{document}
