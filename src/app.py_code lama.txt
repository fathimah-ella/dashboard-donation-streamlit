import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
from cleaning_data import clean_and_merge_transaksi
import numpy as np

st.set_page_config(page_title="📊 Dashboard Donasi", layout="wide")
st.title("📊 Dashboard Transaksi Donasi Campaign SobatBerbagi.com")
st.subheader("16 Desember 2023 - 26 Mei 2025")

# Fungsi untuk mengkonversi nama hari dan bulan ke Bahasa Indonesia
def convert_to_indonesian(df):
    """Mengkonversi nama hari dan bulan ke Bahasa Indonesia"""
    
    # Mapping hari ke Bahasa Indonesia
    day_mapping = {
        'Monday': 'Senin',
        'Tuesday': 'Selasa', 
        'Wednesday': 'Rabu',
        'Thursday': 'Kamis',
        'Friday': 'Jumat',
        'Saturday': 'Sabtu',
        'Sunday': 'Minggu'
    }
    
    # Mapping bulan ke Bahasa Indonesia
    month_mapping = {
        'January': 'Januari',
        'February': 'Februari',
        'March': 'Maret',
        'April': 'April',
        'May': 'Mei',
        'June': 'Juni',
        'July': 'Juli',
        'August': 'Agustus',
        'September': 'September',
        'October': 'Oktober',
        'November': 'November',
        'December': 'Desember'
    }
    
    # Konversi nama hari jika kolom 'hari' ada
    if 'hari' in df.columns:
        df['hari'] = df['tanggal_jam'].dt.day_name().map(day_mapping)
    
    # Konversi nama bulan jika kolom 'bulan' ada
    if 'bulan' in df.columns:
        df['bulan'] = df['tanggal_jam'].dt.month_name().map(month_mapping)
    
    return df

def get_indonesian_day_order():
    """Mengembalikan urutan hari dalam Bahasa Indonesia"""
    return ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']

def get_indonesian_month_order():
    """Mengembalikan urutan bulan dalam Bahasa Indonesia"""
    return ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

@st.cache_data
def load_data():
    df_qris = pd.read_excel("data/transaksi_qris.xlsx", skiprows=1)
    df_manual = pd.read_excel("data/transaksi_manual.xlsx", skiprows=1)
    df = clean_and_merge_transaksi(df_qris, df_manual)
    
    # Tambahkan kolom hari dan bulan dalam Bahasa Indonesia
    df = convert_to_indonesian(df)
    
    return df

df = load_data()

# --- Sidebar Filter ---
st.sidebar.header("🔍 Filter Data")
min_date, max_date = df["tanggal_jam"].min().date(), df["tanggal_jam"].max().date()
start_date = st.sidebar.date_input("Mulai Tanggal", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.sidebar.date_input("Sampai Tanggal", min_value=min_date, max_value=max_date, value=max_date)
if start_date > end_date: st.sidebar.error("❌ Tanggal tidak valid."); st.stop()

metode = st.sidebar.multiselect("Metode Pembayaran", df["metode_pembayaran"].unique(), df["metode_pembayaran"].unique())
status = st.sidebar.multiselect("Status Transaksi", df["status"].unique(), df["status"].unique())

# --- Apply Filters ---
df_filtered = df[
    (df["tanggal_jam"].dt.date >= start_date) &
    (df["tanggal_jam"].dt.date <= end_date)
]
if metode:
    df_filtered = df_filtered[df_filtered["metode_pembayaran"].isin(metode)]
if status:
    df_filtered = df_filtered[df_filtered["status"].isin(status)]

def format_rupiah(val):
    return f"Rp {val:,.0f}".replace(",", ".")

def export_csv(data):
    return data.to_csv(index=False).encode("utf-8")

# --- Tabs ---
tabs = st.tabs([
    "📌 Ringkasan Utama", "👥 Donatur", "📊 Transaksi Keseluruhan",
    "📅 Transaksi Harian", "📆 Transaksi Bulanan", "📈 Tren Campaign", "🔮 Prediksi"
])

# === 📌 Ringkasan Utama ===
with tabs[0]:
    st.subheader("📌 Ringkasan Utama")
    total = int(df_filtered["total_donasi"].sum())
    trx = len(df_filtered)
    unik = df_filtered["nama_donatur"].nunique()
    campaign = df_filtered["nama_campaign"].nunique()
    
    st.metric("**💰 Total Donasi**", format_rupiah(total))
    
    c1, c2, c3 = st.columns(3)
    c1.metric("**🧾 Jumlah Transaksi**", trx)
    c2.metric("**👥 Donatur Unik**", unik)
    c3.metric("**📁 Jumlah Campaign**", campaign)
    
    st.subheader("📊 Status Transaksi per Metode Pembayaran")

    # Hitung jumlah transaksi berdasarkan status dan metode
    status_metode = (
        df_filtered.groupby(["metode_pembayaran", "status"])
        .size()
        .reset_index(name="jumlah")
    )

    # Buat stacked bar chart
    fig_status = px.bar(
        status_metode,
        x="metode_pembayaran",
        y="jumlah",
        color="status",
        title="Perbandingan Status Transaksi per Metode Pembayaran",
        barmode="stack",
        text_auto=True
    )
    st.plotly_chart(fig_status, use_container_width=True)

    # Keterangan naratif umum
    st.markdown("📌 Grafik di atas menunjukkan jumlah transaksi yang *Berhasil* dan *Pending* untuk setiap metode pembayaran.")
    st.markdown("🔍 Gunakan grafik ini untuk mengevaluasi efektivitas dan keandalan tiap metode pembayaran.")

    # Narasi otomatis berdasarkan data
    berhasil = status_metode[status_metode["status"] == "Berhasil"]
    pending = status_metode[status_metode["status"] == "Pending"]

    if not berhasil.empty:
        top_berhasil = berhasil.sort_values("jumlah", ascending=False).iloc[0]
        st.success(f"✅ Metode dengan transaksi **Berhasil** terbanyak adalah **{top_berhasil['metode_pembayaran']}** dengan **{top_berhasil['jumlah']} transaksi**. Ini menunjukkan metode ini paling andal dan disukai donatur.")

    if not pending.empty:
        top_pending = pending.sort_values("jumlah", ascending=False).iloc[0]
        st.warning(f"⚠ Metode dengan transaksi **Pending** terbanyak adalah **{top_pending['metode_pembayaran']}** dengan **{top_pending['jumlah']} transaksi**. Perlu dilakukan evaluasi untuk meningkatkan keandalan metode ini.")
    
    # Rekomendasi tambahan
    st.markdown("""
    💡 *Rekomendasi Strategis:*
    - Fokuskan promosi pada metode yang paling banyak berhasil.
    - Cek alur teknis atau sistem pembayaran pada metode yang sering pending.
    - Lakukan edukasi kepada donatur agar memilih metode yang paling stabil.
    """)

    #==========================================================================================
    st.subheader("💳 Frekuensi Penggunaan Metode Pembayaran")
    
    # Hitung jumlah transaksi per metode pembayaran
    metode_freq = df_filtered["metode_pembayaran"].value_counts().reset_index()
    metode_freq.columns = ["Metode Pembayaran", "Jumlah Transaksi"]

    # Bar chart horizontal
    fig = px.bar(
        metode_freq.sort_values("Jumlah Transaksi"),
        x="Jumlah Transaksi",
        y="Metode Pembayaran",
        orientation="h",
        text="Jumlah Transaksi",
        color="Metode Pembayaran",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tampilkan jumlah transaksi per metode
    for i, row in metode_freq.iterrows():
        st.write(f"👉 {row['Metode Pembayaran']}: {row['Jumlah Transaksi']} transaksi")

    # Narasi otomatis berdasarkan metode paling sering
    top_method = metode_freq.iloc[0]
    metode = top_method["Metode Pembayaran"]
    jumlah = top_method["Jumlah Transaksi"]
    st.success(f"📊 Metode yang paling sering digunakan adalah **{metode}** dengan **{jumlah} transaksi**.")

    # Keterangan tambahan otomatis
    if "qris" in metode.lower():
        st.info("💡 **QRIS** menjadi metode utama yang paling sering digunakan. Ini menunjukkan bahwa donatur cenderung memilih metode pembayaran yang cepat, instan, dan berbasis digital.")
    elif "manual" in metode.lower():
        st.info("💡 **Metode Manual** paling banyak digunakan. Ini bisa menandakan bahwa masih banyak donatur yang memerlukan bantuan admin atau belum terbiasa dengan metode digital.")
    else:
        st.info("💡 Metode ini paling banyak digunakan. Pertimbangkan untuk mengoptimalkan proses donasi pada metode ini untuk kenyamanan pengguna.")
        
        
    # ==============================================================================
    st.subheader("👥 Preferensi Metode Pembayaran per Donatur")
    # Hitung frekuensi setiap donatur terhadap metode pembayaran
    preferensi = (
        df_filtered.groupby(["nama_donatur", "metode_pembayaran"])
        .size()
        .reset_index(name="jumlah")
    )
    # Ambil metode yang paling sering dipakai oleh masing-masing donatur
    preferensi_top = (
        preferensi.sort_values("jumlah", ascending=False)
        .drop_duplicates("nama_donatur")
    )
    # Hitung berapa banyak donatur yang prefer QRIS / Manual
    preferensi_count = preferensi_top["metode_pembayaran"].value_counts().reset_index()
    preferensi_count.columns = ["Metode Pembayaran", "Jumlah Donatur"]
    
    # Tampilkan hasil
    fig = px.bar(preferensi_count, x="Metode Pembayaran", y="Jumlah Donatur", color="Metode Pembayaran",
                title="Preferensi Utama Donatur terhadap Metode Pembayaran")
    st.plotly_chart(fig, use_container_width=True)
    
    # Tampilkan jumlah preferensi tiap metode
    for i, row in preferensi_count.iterrows():
        st.write(f"👤 {row['Metode Pembayaran']}: {row['Jumlah Donatur']} donatur memilih metode ini paling sering")
        
    # Kesimpulan preferensi
    top_pref = preferensi_count.iloc[0]
    st.info(f"🧠 Sebagian besar donatur lebih suka menggunakan **{top_pref['Metode Pembayaran']}** dalam donasi mereka. Hal ini menunjukkan kecenderungan preferensi pengguna terhadap metode ini.")

# ==============================================================================
    st.subheader("⚖️ Perbandingan Total Donasi QRIS vs Manual")

    # Hitung total donasi per metode pembayaran (hanya QRIS & Manual)
    donasi_per_metode = (
        df_filtered[df_filtered["metode_pembayaran"].str.lower().isin(["qris", "manual"])]
        .groupby("metode_pembayaran")["total_donasi"]
        .sum()
        .reset_index()
    )
    donasi_per_metode.columns = ["Metode Pembayaran", "Total Donasi"]

    # Pie Chart
    fig_donasi_pie = px.pie(
        donasi_per_metode,
        names="Metode Pembayaran",
        values="Total Donasi",
        title="Proporsi Total Donasi QRIS vs Manual",
        hole=0.4,  # Donut chart
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_donasi_pie, use_container_width=True)

    # Narasi otomatis
    if not donasi_per_metode.empty:
        top_donasi = donasi_per_metode.sort_values("Total Donasi", ascending=False).iloc[0]
        st.info(f"💡 Metode dengan total donasi terbesar adalah **{top_donasi['Metode Pembayaran']}** sebesar **{format_rupiah(top_donasi['Total Donasi'])}**.")

# ==============================================================================
    st.download_button("📥 Export Laporan", export_csv(df_filtered), "transaksi_harian.csv", "text/csv")
    st.subheader("📄 Tabel Data Transaksi")
    st.dataframe(df_filtered)
    

# === 👥 Donatur ===
with tabs[1]:
    st.subheader("🏆 Top Donatur")
    top_donatur = df_filtered.groupby("nama_donatur")["total_donasi"].sum().reset_index().sort_values("total_donasi", ascending=False).head(10)
    st.dataframe(top_donatur)
    if not top_donatur.empty:
        top = top_donatur.iloc[0]
        st.success(f"👤 Donatur terbesar: **{top['nama_donatur']}** dengan total donasi sebesar **{format_rupiah(top['total_donasi'])}**")

# === 📊 Transaksi Keseluruhan ===
with tabs[2]:
    st.subheader("💰 Total Donasi Keseluruhan")
    total_harian = df_filtered.groupby("tanggal_jam")["total_donasi"].sum().reset_index()
    fig = px.line(total_harian, x="tanggal_jam", y="total_donasi", title="Tren Donasi Harian")
    st.plotly_chart(fig, use_container_width=True)
    
    max_trx = total_harian.loc[total_harian["total_donasi"].idxmax()]
    min_trx = total_harian.loc[total_harian["total_donasi"].idxmin()]
    st.success(f"🔼 Donasi tertinggi terjadi pada **{max_trx['tanggal_jam'].date()}** sebesar **{format_rupiah(max_trx['total_donasi'])}**")
    st.error(f"🔽 Donasi terendah terjadi pada **{min_trx['tanggal_jam'].date()}** sebesar **{format_rupiah(min_trx['total_donasi'])}**")

    st.markdown("""
    🧠 *Rekomendasi:*
    - Tingkatkan promosi dan perluas jangkauan campaign ke channel online & sosial media.
    - Fokuskan edukasi penggunaan metode ini untuk memudahkan donatur baru.
    - Evaluasi strategi promosi dan waktu publikasi campaign.
    - Pertimbangkan membuat event atau pengingat berkala kepada donatur.
    """)

    st.subheader("💳 Tren Metode Pembayaran dari Waktu ke Waktu")
    by_method = df_filtered.groupby(["tanggal_jam", "metode_pembayaran"])["total_donasi"].sum().reset_index()
    fig2 = px.line(by_method, x="tanggal_jam", y="total_donasi", color="metode_pembayaran", title="Metode Pembayaran dari Waktu ke Waktu")
    st.plotly_chart(fig2, use_container_width=True)

    populer = df_filtered["metode_pembayaran"].value_counts().idxmax()
    st.info(f"Metode pembayaran yang paling konsisten digunakan adalah **{populer}**")


# === 📅 Transaksi Harian ===
with tabs[3]:
    st.subheader("💰 Total Donasi per Hari")
    
    # Buat data harian dengan urutan yang benar
    harian = df_filtered.groupby("hari")["total_donasi"].sum().reset_index()
    
    # Urutkan berdasarkan urutan hari dalam seminggu
    day_order = get_indonesian_day_order()
    harian['hari'] = pd.Categorical(harian['hari'], categories=day_order, ordered=True)
    harian = harian.sort_values('hari')
    
    fig = px.bar(harian, x="hari", y="total_donasi", title="Total Donasi per Hari")
    st.plotly_chart(fig, use_container_width=True)

    max_h = harian.loc[harian["total_donasi"].idxmax()]
    min_h = harian.loc[harian["total_donasi"].idxmin()]
    avg = harian["total_donasi"].mean()
    st.success(f"🔼 Hari tertinggi: **{max_h['hari']}** sebesar **{format_rupiah(max_h['total_donasi'])}**")
    st.warning(f"🔽 Hari terendah: **{min_h['hari']}** sebesar **{format_rupiah(min_h['total_donasi'])}**")
    st.info(f"📊 Rata-rata donasi per hari: **{format_rupiah(avg)}**")

    st.markdown("""
    💡 *Rekomendasi:*
    - Tingkatkan promosi di hari dengan traffic rendah.
    - Uji waktu posting konten campaign.
    - Kombinasikan promosi dengan momen hari besar atau akhir pekan.
    """)


# === 📆 Transaksi Bulanan ===
with tabs[4]:
    st.subheader("💰 Total Donasi per Bulan")
    
    # Buat data bulanan dengan urutan yang benar
    bulanan = df_filtered.groupby("bulan")["total_donasi"].sum().reset_index()
    
    # Urutkan berdasarkan urutan bulan dalam tahun
    month_order = get_indonesian_month_order()
    bulanan['bulan'] = pd.Categorical(bulanan['bulan'], categories=month_order, ordered=True)
    bulanan = bulanan.sort_values('bulan')
    
    fig = px.bar(bulanan, x="bulan", y="total_donasi", title="Total Donasi per Bulan")
    fig.update_xaxes(tickangle=45)  # Rotasi label bulan agar lebih mudah dibaca
    st.plotly_chart(fig, use_container_width=True)

    max_b = bulanan.loc[bulanan["total_donasi"].idxmax()]
    min_b = bulanan.loc[bulanan["total_donasi"].idxmin()]
    avg_b = bulanan["total_donasi"].mean()
    st.success(f"🔼 Bulan tertinggi: **{max_b['bulan']}** sebesar **{format_rupiah(max_b['total_donasi'])}**")
    st.warning(f"🔽 Bulan terendah: **{min_b['bulan']}** sebesar **{format_rupiah(min_b['total_donasi'])}**")
    st.info(f"📊 Rata-rata donasi per bulan: **{format_rupiah(avg_b)}**")

    st.markdown("""
    📌 *Rekomendasi:*
    - Jadwalkan promosi intensif pada bulan dengan tren tinggi.
    - Evaluasi strategi di bulan dengan tren rendah.
    - Pertimbangkan campaign tematik bulanan.
    """)


# === 📈 Tren Campaign ===
with tabs[5]:
    st.subheader("📈 Donasi per Campaign")
    campaign = df_filtered.groupby("nama_campaign")["total_donasi"].sum().reset_index().sort_values("total_donasi", ascending=False)
    top_campaign = campaign.sort_values("total_donasi", ascending=True)
    fig = px.bar(
        top_campaign,
        x="total_donasi",
        y="nama_campaign",
        orientation="h",
        title="Donasi per Campaign",
        labels={"total_donasi": "Total Donasi", "nama_campaign": "Nama Campaign"},
        height=800
    )
    st.plotly_chart(fig, use_container_width=True)

    if not campaign.empty:
        top = campaign.iloc[0]
        bottom = campaign.iloc[-1]
        st.success(f"🏆 Campaign tertinggi: **{top['nama_campaign']}**  **{format_rupiah(top['total_donasi'])}**")
        st.error(f"📉 Campaign terendah: **{bottom['nama_campaign']}**  **{format_rupiah(bottom['total_donasi'])}**")
        st.info(f"📊 Rata-rata donasi per campaign: **{format_rupiah(campaign['total_donasi'].mean())}**")

    st.subheader("🧐 Evaluasi Campaign")
    avg_donasi = campaign["total_donasi"].mean()
    below_avg = campaign[campaign["total_donasi"] < avg_donasi]
    if not below_avg.empty:
        st.warning("⚠ Campaign berikut memiliki performa di bawah rata-rata dan perlu evaluasi:")
        st.dataframe(below_avg)
        st.markdown("""
        📌 *Rekomendasi:*
        - Revisi strategi promosi campaign.
        - Tampilkan testimoni penerima manfaat.
        - Gunakan visual yang menarik dan storytelling.
        """)


# === 🔮 Prediksi ===
with tabs[6]:
    st.subheader("🔮 Prediksi Donasi Bulan Depan (dengan Prophet)")

    if df_filtered.empty:
        st.warning("Data tidak tersedia untuk dilakukan prediksi.")
    else:
        # Siapkan data untuk Prophet
        pred_data = df_filtered.groupby("tanggal_jam")["total_donasi"].sum().reset_index()
        pred_data = pred_data.rename(columns={"tanggal_jam": "ds", "total_donasi": "y"})
        
        # Quick data cleaning
        pred_data = pred_data.sort_values('ds').reset_index(drop=True)
        Q1, Q3 = pred_data['y'].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        pred_data['y'] = np.clip(pred_data['y'], Q1 - 1.5*IQR, Q3 + 1.5*IQR)
        
        # Tentukan cap
        max_cap = pred_data["y"].max() * 1.2
        pred_data["cap"] = max_cap
        
        # Model untuk prediksi final (full data)
        model = Prophet(
            growth="logistic",
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0
        )
        model.fit(pred_data)
        
        # Buat prediksi
        future = model.make_future_dataframe(periods=30)
        future["cap"] = max_cap
        forecast = model.predict(future)
        
        # Rename kolom hasil prediksi
        forecast_renamed = forecast.rename(columns={
            "ds": "tanggal_jam",
            "yhat": "total_donasi"
        })
        forecast_renamed["total_donasi"] = forecast_renamed["total_donasi"].clip(lower=0)
        
        # Visualisasi prediksi
        fig = px.line(
            forecast_renamed,
            x="tanggal_jam",
            y="total_donasi",
            title="📈 Prediksi Donasi Harian (30 Hari ke Depan)"
        )
        fig.add_hline(y=0, line_dash="dot", line_color="red")
        st.plotly_chart(fig)
        
        # Estimasi dengan range
        future_pred = forecast_renamed["total_donasi"].iloc[-30:]
        est_total = future_pred.sum()
        est_lower = forecast["yhat_lower"].iloc[-30:].sum()
        est_upper = forecast["yhat_upper"].iloc[-30:].sum()
        
        st.success(f"📅 Estimasi total donasi 30 hari: **{format_rupiah(est_total)}**")
        st.info(f"📊 Range: **{format_rupiah(max(0, est_lower))}** - **{format_rupiah(est_upper)}**")
        
        # Analisis musiman
        forecast_renamed["bulan_num"] = forecast_renamed["tanggal_jam"].dt.month
        per_month = forecast_renamed.groupby("bulan_num")["total_donasi"].mean()
        
        month_names = {1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April', 5: 'Mei', 6: 'Juni',
                    7: 'Juli', 8: 'Agustus', 9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'}
        
        if len(per_month) > 1:
            max_month = month_names[per_month.idxmax()]
            min_month = month_names[per_month.idxmin()]
            st.info(f"📈 Lonjakan kemungkinan terjadi di bulan **{max_month}**")
            st.error(f"📉 Penurunan kemungkinan terjadi di bulan **{min_month}**")
        
            st.caption("🔍 Prediksi ini mempertimbangkan tren historis. Evaluasi dengan kalender event internal seperti Ramadhan atau Idul Fitri untuk akurasi strategi.")
