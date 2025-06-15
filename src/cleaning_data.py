import pandas as pd
from import_data import load_data

def clean_and_merge_transaksi(df_qris, df_manual):
    # Tambahkan kolom "Metode Pembayaran"
    df_qris["Metode Pembayaran"] = "QRIS"
    df_manual["Metode Pembayaran"] = "Manual"

    # Gabungkan kedua dataframe
    df_transaksi = pd.concat([df_qris, df_manual], ignore_index=True)
    
    # Ganti nama kolom "Tanggal" menjadi "tanggal_jam"
    df_transaksi.rename(columns={"Tanggal": "tanggal_jam"}, inplace=True)
    
    # Pastikan dalam bentuk string
    df_transaksi["tanggal_jam"] = df_transaksi["tanggal_jam"].astype(str)
    
    # Ganti nama bulan Indonesia dengan angka agar bisa diparse
    bulan_mapping = {
        "Januari": "01", "Februari": "02", "Maret": "03", "April": "04",
        "Mei": "05", "Juni": "06", "Juli": "07", "Agustus": "08",
        "September": "09", "Oktober": "10", "November": "11", "Desember": "12"
    }

    for nama_bulan, angka_bulan in bulan_mapping.items():
        df_transaksi["tanggal_jam"] = df_transaksi["tanggal_jam"].str.replace(nama_bulan, angka_bulan)

    # Konversi ke datetime
    df_transaksi["tanggal_jam"] = pd.to_datetime(df_transaksi["tanggal_jam"], format="%d %m %Y %H:%M")

    # Buat kolom tanggal (hanya tanggal tanpa jam)
    df_transaksi["tanggal"] = df_transaksi["tanggal_jam"].dt.date
    
    # Hapus kolom "No"
    df_transaksi.drop("No", axis=1, inplace=True)
    
    # Bersihkan Total Donasi
    df_transaksi["Total Donasi"] = (
        df_transaksi["Total Donasi"]
        .astype(str)
        .str.replace(r"\D", "", regex=True)
        .replace("", "0")
        .astype(int)
    )
    
    # Hapus baris yang total_donasi nya 0
    df_transaksi = df_transaksi[df_transaksi["Total Donasi"] != 0]
    
    # Ganti NaN dengan "Anonim"
    df_transaksi["Nama Donatur"] = df_transaksi["Nama Donatur"].fillna("Anonim")
    
    # Seragamkan semua variasi penulisan di kolom Nama Donatur
    df_transaksi["Nama Donatur"] = (
        df_transaksi["Nama Donatur"]
        .astype(str) # Pastikan semua dalam bentuk string
        .str.strip() # Hilangkan spasi di awal/akhir
        .str.title() # Ubah ke format judul
    )
    # Ganti "Hamba Allah" pada kolom Nama Donatur menjadi "Anonim"
    df_transaksi["Nama Donatur"] = df_transaksi["Nama Donatur"].str.replace(r"(?i)^hamba allah$", "Anonim", regex=True)

    # Drop kolom Nama Campaign yang berisi "-"
    df_transaksi = df_transaksi[df_transaksi["Nama Campaign"] != "-"]

    # Ganti status dan isi kosong
    df_transaksi["Status"] = df_transaksi["Status"].replace("Belum Di Konfirmasi", "Pending").str.strip().str.title()

    # Tambahan kolom untuk agregasi
    df_transaksi["tahun"] = df_transaksi["tanggal_jam"].dt.year
    df_transaksi["bulan"] = df_transaksi["tanggal_jam"].dt.month
    df_transaksi["minggu"] = df_transaksi["tanggal_jam"].dt.isocalendar().week
    df_transaksi["hari"] = df_transaksi["tanggal_jam"].dt.day_name()
    df_transaksi["jam"] = df_transaksi["tanggal_jam"].dt.hour

    # Rename agar seragam dengan app.py
    df_transaksi = df_transaksi.rename(columns={
        "Nama Campaign": "nama_campaign",
        "Nama Donatur": "nama_donatur",
        "Total Donasi": "total_donasi",
        "Metode Pembayaran": "metode_pembayaran",
        "Status": "status"  
    })

    return df_transaksi[[
        "tanggal_jam", "tanggal", "tahun", "bulan", "minggu", "hari", "jam",
        "nama_campaign", "nama_donatur", "total_donasi", "metode_pembayaran", "status"
    ]] 


# Panggil load_data() dari file import_data.py
df_qris, df_manual = load_data() 

# Lanjutkan proses cleaning
df_clean = clean_and_merge_transaksi(df_qris, df_manual)

# Simpan hasilnya
df_clean.to_excel("D:/KP/sobatberbagi.com_dashboard/data/data_bersih.xlsx", index=False)
