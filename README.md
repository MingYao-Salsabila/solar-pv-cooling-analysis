Solar PV Temperature vs Output Analysis & Cooling Comparison ☀️💧

Author: [Your Name Here]

Tools Used: Python (Pandas, Matplotlib, Seaborn), Excel, Jupyter Notebook

📌 Project Overview

This project analyzes real-world experimental data to understand the relationship between solar photovoltaic (PV) operating temperature and power output. Specifically, it compares a standard 50W Polycrystalline solar panel against one equipped with a water cooling system.

This project proves the concept that reducing thermal losses via a water cooling system significantly increases the overall efficiency and power stability of solar PV systems in high-temperature environments.

📊 Key Findings

Temperature Impact: As panel temperature increases, the voltage drop reduces the overall power output of the standard panel.

Cooling Efficiency: The implementation of a water cooling system successfully lowered the panel temperature, resulting in higher and more stable power output, especially during peak sunlight hours.

📈 Visualizations

1. Temperature vs Power Output

(This chart demonstrates the negative correlation between high heat and power output).


(Note: Upload your generated temp_vs_power.png to GitHub for this image to show)

2. Standard vs Cooled Panel Performance

(This chart tracks the power generation of both panels over the course of the day).


(Note: Upload your generated cooling_comparison.png to GitHub for this image to show)

📂 Data Summary

The dataset (cleaned_solar_data.csv) was collected experimentally and includes:

Time/Weather: Hourly tracking under varying weather conditions (Sunny, Cloudy).

Temperatures: Operating surface temperature of both standard and cooled panels.

Electrical Metrics: Open-circuit voltage (Voc), Short-circuit current (Isc), and calculated Power Output (W).

Irradiance: Light intensity measured in Lux.

🚀 How to Run This Project

Clone this repository.

Install dependencies: pip install pandas matplotlib seaborn

Run the analysis script: python solar_analysis.py

💡 Next Steps in My Portfolio

[ ] Build a Solar Panel Performance Simulator (Interactive Calculator).

[ ] Develop an Indonesia Renewable Energy Mini-Report.
