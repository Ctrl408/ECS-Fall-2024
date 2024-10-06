# IoT-Enabled Device for Intelligent Drug Delivery

## Overview

 This paper presents the development of an IoT-enabled device designed to opti
mize the delivery of various medications for patients requiring continuous infusion
 therapy. 




## Installation

To set up the project on your local machine, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ctrl408/ECS-Fall-2024
   cd ECS-Fall-2024
   ```
2. **Install the required packages: Make sure you have Python installed, then run:**:
   ```bash
   pip install PyQt5 pyqtgraph qdarkstyle pyserial
   ```

3. **Install the required packages: Make sure you have Python installed, then run:**:
   ```bash
   pip install PyQt5 pyqtgraph qdarkstyle pyserial
   ```




# JSON File Usage for Dosage Management

## Overview

The application uses a JSON file to manage and store medication dosage protocols. This allows for easy customization and flexibility in administering medications based on specific seizure detection events.

## Dosage JSON Structure

The JSON file should be structured as follows:

```json
{
  "medications": [
    {
      "name": "MedicationA",
      "dosage": "500mg",
      "route": "oral",
      "schedule": [
        {
          "time": "08:00",
          "dose": "500mg"
        },
        {
          "time": "20:00",
          "dose": "500mg"
        }
      ]
    },
    {
      "name": "MedicationB",
      "dosage": "250mg",
      "route": "intravenous",
      "schedule": [
        {
          "time": "12:00",
          "dose": "250mg"
        }
      ]
    }
  ]
}

