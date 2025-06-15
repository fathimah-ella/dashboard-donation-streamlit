import pandas as pd

def load_data():
    # Baca file Excel
    transaksi_qris = pd.read_excel("data/transaksi_qris.xlsx", skiprows=1)
    transaksi_manual = pd.read_excel("data/transaksi_manual.xlsx", skiprows=1)

    return transaksi_qris, transaksi_manual
