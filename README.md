# 📊 Dashboard Donation with Streamlit

## Project Overview
This repository contains a web-based interactive dashboard for analyzing donation transactions, built using Streamlit. Developed as part of a real-world internship project at **Lazismu Banyumas**, the dashboard processes donation data collected from the SobatBerbagi.com platform, encompassing both QRIS and manual transfer methods. It provides key insights into donor behavior, transaction trends, campaign performance, and donation method preferences, ultimately supporting data-driven fundraising strategies.

## 🔧 Key Features
* Clean and merged donation dataset (QRIS & manual transfers).
* Real-time interactive dashboard using Streamlit.
* Visualizations of total donations, daily/monthly trends, top donors, and campaign performance.
* Exportable CSV reports for further analysis.
* Bahasa Indonesia support for dates and labels, enhancing user experience for local stakeholders.

## 🧰 Built With
* Python (Pandas, Plotly, Streamlit)
* Visual Studio Code
* Jupyter Notebook

## 📌 Use Case
Non-profit organizations, especially those in the Zakat/Donation sector, can leverage this dashboard to gain a deeper understanding of donation dynamics. This tool enables them to optimize campaign strategies, make informed future plans, and utilize forecasted data for more effective fundraising initiatives.

## How to Run the Dashboard
1.  **Clone the repository:**
    ```bash
    git clone [[dashboard-donation-streamlit](https://github.com/fathimah-ella/dashboard-donation-streamlit)]
    cd [[src](https://github.com/fathimah-ella/dashboard-donation-streamlit/tree/main/src)]
    ```
2.  **Install dependencies:**
    Ensure you have Python installed. Then, install the required libraries (it's recommended to use a virtual environment):
    ```bash
    pip install -r requirements.txt
    ```
    *(If you don't have a `requirements.txt` yet, you can create one by listing `pandas`, `plotly`, `streamlit`.)*
3.  **Prepare your data:**
    Place your donation transaction data (transaksi_manual.xlsx and transaksi_qris.xlsx) in the same directory as the Streamlit application file.
    *(You might want to specify the expected file name/format here).*
4.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
    *(Assuming your main Streamlit script is named `app.py`. Adjust if your file has a different name.)*
    The dashboard will open in your default web browser.

## Contact
[[Fathimah Ella Syarif](https://www.linkedin.com/in/fathimahellasyarif/)]
