import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cleaning_data import clean_and_merge_transaksi
import numpy as np
from datetime import datetime, timedelta

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

def calculate_growth_rate(current, previous):
    """Menghitung persentase pertumbuhan"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

def get_performance_insight(value, benchmark, metric_name):
    """Memberikan insight berdasarkan performa relatif terhadap benchmark"""
    if value > benchmark * 1.2:
        return f"📈 {metric_name} menunjukkan performa SANGAT BAIK (20% di atas rata-rata)"
    elif value > benchmark:
        return f"✅ {metric_name} menunjukkan performa BAIK (di atas rata-rata)"
    elif value > benchmark * 0.8:
        return f"⚠️ {metric_name} menunjukkan performa CUKUP (mendekati rata-rata)"
    else:
        return f"🔴 {metric_name} menunjukkan performa PERLU PERBAIKAN (di bawah rata-rata)"

# --- Tabs ---
tabs = st.tabs([
    "📌 Ringkasan Utama", "👥 Donatur", "📊 Transaksi Keseluruhan",
    "📅 Transaksi Harian", "📆 Transaksi Bulanan", "📈 Tren Campaign"
])

# === 📌 Ringkasan Utama ===
with tabs[0]:
    st.subheader("📌 Ringkasan Utama")
    
    # Metrics utama
    total = int(df_filtered["total_donasi"].sum())
    trx = len(df_filtered)
    unik = df_filtered["nama_donatur"].nunique()
    campaign = df_filtered["nama_campaign"].nunique()
    
    # Hitung rata-rata donasi per transaksi
    avg_per_trx = total / trx if trx > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Donasi", format_rupiah(total))
    with col2:
        st.metric("🧾 Jumlah Transaksi", f"{trx:,}")
    with col3:
        st.metric("👥 Donatur Unik", f"{unik:,}")
    with col4:
        st.metric("📁 Campaign Aktif", f"{campaign:,}")
    
    # Tambahan metrics untuk insight lebih dalam
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("💵 Rata-rata per Transaksi", format_rupiah(avg_per_trx))
    with col6:
        loyalty_rate = (trx / unik) if unik > 0 else 0
        st.metric("🔄 Tingkat Loyalitas", f"{loyalty_rate:.1f}x")
    with col7:
        success_rate = len(df_filtered[df_filtered["status"] == "Berhasil"]) / trx * 100 if trx > 0 else 0
        st.metric("✅ Tingkat Keberhasilan", f"{success_rate:.1f}%")
    with col8:
        avg_per_campaign = total / campaign if campaign > 0 else 0
        st.metric("📊 Rata-rata per Campaign", format_rupiah(avg_per_campaign))

    # === GRAFIK 1: Status Transaksi per Metode Pembayaran ===
    st.subheader("📊 Analisis Status Transaksi per Metode Pembayaran")
    
    # Hitung jumlah transaksi berdasarkan status dan metode
    status_metode = (
        df_filtered.groupby(["metode_pembayaran", "status"])
        .size()
        .reset_index(name="jumlah")
    )

    # Buat stacked bar chart dengan styling yang lebih baik
    fig_status = px.bar(
        status_metode,
        x="metode_pembayaran",
        y="jumlah",
        color="status",
        title="Distribusi Status Transaksi Berdasarkan Metode Pembayaran",
        barmode="stack",
        text_auto=True,
        color_discrete_map={
            "Berhasil": "#2E8B57",  # SeaGreen
            "Pending": "#FF6347"    # Tomato
        }
    )
    fig_status.update_layout(
        xaxis_title="Metode Pembayaran",
        yaxis_title="Jumlah Transaksi",
        showlegend=True
    )
    st.plotly_chart(fig_status, use_container_width=True)

    # Analisis dan insight yang lebih mendalam
    st.markdown("#### 🔍 Insight Analisis Status Transaksi:")
    
    # Hitung tingkat keberhasilan per metode
    success_by_method = df_filtered.groupby("metode_pembayaran").apply(
        lambda x: (x["status"] == "Berhasil").sum() / len(x) * 100
    ).reset_index(name="success_rate")
    
    best_method = success_by_method.loc[success_by_method["success_rate"].idxmax()]
    worst_method = success_by_method.loc[success_by_method["success_rate"].idxmin()]
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"🏆 **Metode Terbaik**: {best_method['metode_pembayaran']} dengan tingkat keberhasilan {best_method['success_rate']:.1f}%")
    with col2:
        st.warning(f"⚠️ **Perlu Perbaikan**: {worst_method['metode_pembayaran']} dengan tingkat keberhasilan {worst_method['success_rate']:.1f}%")

    # Rekomendasi strategis yang spesifik
    st.markdown("#### 💡 Rekomendasi Strategis:")
    
    if best_method['success_rate'] > 90:
        st.info(f"✅ **Prioritaskan {best_method['metode_pembayaran']}**: Metode ini sangat reliable. Tingkatkan promosi dan edukasi penggunaan metode ini kepada donatur baru.")
    
    if worst_method['success_rate'] < 80:
        st.error(f"🔧 **Perbaiki Segera {worst_method['metode_pembayaran']}**: Tingkat kegagalan tinggi dapat menurunkan kepercayaan donatur. Lakukan audit teknis sistem pembayaran.")
    
    # Tindakan konkret berdasarkan data
    pending_total = df_filtered[df_filtered["status"] == "Pending"]["total_donasi"].sum()
    if pending_total > 0:
        st.warning(f"💰 **Potensi Kehilangan**: Rp {pending_total:,.0f} dalam status pending. Segera follow-up transaksi pending untuk mengoptimalkan revenue.")

    # === GRAFIK 2: Frekuensi Penggunaan Metode Pembayaran ===
    st.subheader("💳 Popularitas Metode Pembayaran")
    
    # Hitung frekuensi dan persentase
    metode_freq = df_filtered["metode_pembayaran"].value_counts().reset_index()
    metode_freq.columns = ["Metode Pembayaran", "Jumlah Transaksi"]
    metode_freq["Persentase"] = (metode_freq["Jumlah Transaksi"] / metode_freq["Jumlah Transaksi"].sum() * 100).round(1)

    # Dual chart: Bar + Pie
    col1, col2 = st.columns(2)
    
    with col1:
        fig_bar = px.bar(
            metode_freq.sort_values("Jumlah Transaksi", ascending=True),
            x="Jumlah Transaksi",
            y="Metode Pembayaran",
            orientation="h",
            text="Persentase",
            title="Frekuensi Penggunaan Metode Pembayaran",
            color="Jumlah Transaksi",
            color_continuous_scale="viridis"
        )
        fig_bar.update_traces(texttemplate='%{text}%', textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        fig_pie = px.pie(
            metode_freq,
            names="Metode Pembayaran",
            values="Jumlah Transaksi",
            title="Distribusi Market Share Metode Pembayaran",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Market dominance analysis
    dominant_method = metode_freq.iloc[0]
    market_share = dominant_method["Persentase"]
    
    st.markdown("#### 📈 Analisis Market Share:")
    
    if market_share > 60:
        st.success(f"🎯 **Monopoli Pasar**: {dominant_method['Metode Pembayaran']} mendominasi {market_share}% transaksi. Posisi sangat kuat!")
        st.info("💡 **Strategi**: Pertahankan kualitas layanan metode dominan sambil mengembangkan metode alternatif untuk diversifikasi risiko.")
    elif market_share > 40:
        st.info(f"📊 **Leader Pasar**: {dominant_method['Metode Pembayaran']} memimpin dengan {market_share}% market share.")
        st.warning("⚠️ **Strategi**: Perkuat posisi leadership dengan meningkatkan user experience dan reliability.")
    else:
        st.warning(f"⚖️ **Kompetisi Seimbang**: {dominant_method['Metode Pembayaran']} hanya {market_share}% market share.")
        st.info("🎯 **Strategi**: Fokus diferensiasi dan value proposition untuk memenangkan market share.")

    # === GRAFIK 3: Preferensi Donatur Individual ===
    st.subheader("👥 Pola Preferensi Donatur")
    
    # Analisis preferensi per donatur
    preferensi = (
        df_filtered.groupby(["nama_donatur", "metode_pembayaran"])
        .size()
        .reset_index(name="jumlah")
    )
    
    preferensi_top = (
        preferensi.sort_values("jumlah", ascending=False)
        .drop_duplicates("nama_donatur")
    )
    
    preferensi_count = preferensi_top["metode_pembayaran"].value_counts().reset_index()
    preferensi_count.columns = ["Metode Pembayaran", "Jumlah Donatur"]
    preferensi_count["Persentase Donatur"] = (preferensi_count["Jumlah Donatur"] / preferensi_count["Jumlah Donatur"].sum() * 100).round(1)
    
    fig_pref = px.bar(
        preferensi_count, 
        x="Metode Pembayaran", 
        y="Jumlah Donatur",
        text="Persentase Donatur",
        title="Preferensi Utama Donatur terhadap Metode Pembayaran",
        color="Jumlah Donatur",
        color_continuous_scale="plasma"
    )
    fig_pref.update_traces(texttemplate='%{text}%', textposition="outside")
    st.plotly_chart(fig_pref, use_container_width=True)
    
    # Analisis loyalitas donatur
    multi_method_users = preferensi.groupby("nama_donatur")["metode_pembayaran"].nunique()
    loyal_users = (multi_method_users == 1).sum()
    flexible_users = (multi_method_users > 1).sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Donatur Loyal (1 metode)", f"{loyal_users}")
    with col2:
        st.metric("🔄 Donatur Fleksibel (multi metode)", f"{flexible_users}")
    with col3:
        loyalty_rate = (loyal_users / (loyal_users + flexible_users) * 100) if (loyal_users + flexible_users) > 0 else 0
        st.metric("📊 Tingkat Loyalitas Metode", f"{loyalty_rate:.1f}%")

    # === GRAFIK 4: Perbandingan Value Donasi per Metode ===
    st.subheader("💰 Analisis Value Donasi per Metode")
    
    donasi_stats = df_filtered.groupby("metode_pembayaran").agg({
        "total_donasi": ["sum", "mean", "count"]
    }).round(2)
    donasi_stats.columns = ["Total Donasi", "Rata-rata Donasi", "Jumlah Transaksi"]
    donasi_stats = donasi_stats.reset_index()
    
    # Multi-metric comparison chart
    fig_comparison = go.Figure()
    
    # Bar untuk total donasi
    fig_comparison.add_trace(go.Bar(
        name="Total Donasi (Juta Rp)",
        x=donasi_stats["metode_pembayaran"],
        y=donasi_stats["Total Donasi"] / 1000000,  # Convert to millions
        yaxis="y",
        marker_color="lightblue"
    ))
    
    # Line untuk rata-rata donasi
    fig_comparison.add_trace(go.Scatter(
        name="Rata-rata per Transaksi (Ribu Rp)",
        x=donasi_stats["metode_pembayaran"],
        y=donasi_stats["Rata-rata Donasi"] / 1000,  # Convert to thousands
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="red", width=3),
        marker=dict(size=8)
    ))
    
    fig_comparison.update_layout(
        title="Perbandingan Total vs Rata-rata Donasi per Metode",
        xaxis_title="Metode Pembayaran",
        yaxis=dict(title="Total Donasi (Juta Rp)", side="left"),
        yaxis2=dict(title="Rata-rata per Transaksi (Ribu Rp)", side="right", overlaying="y"),
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Value-based insights
    highest_value_method = donasi_stats.loc[donasi_stats["Rata-rata Donasi"].idxmax()]
    highest_volume_method = donasi_stats.loc[donasi_stats["Total Donasi"].idxmax()]
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"💎 **Highest Value**: {highest_value_method['metode_pembayaran']} - Rata-rata {format_rupiah(highest_value_method['Rata-rata Donasi'])}")
        st.info("🎯 **Strategi**: Fokus pada metode ini untuk donatur premium atau campaign besar.")
    
    with col2:
        st.success(f"📊 **Highest Volume**: {highest_volume_method['metode_pembayaran']} - Total {format_rupiah(highest_volume_method['Total Donasi'])}")
        st.info("🎯 **Strategi**: Metode ini adalah revenue driver utama. Pastikan selalu optimal.")

    # === STRATEGIC RECOMMENDATIONS SECTION ===
    st.subheader("🎯 Rekomendasi Strategis Berbasis Data")
    
    # Calculate key performance indicators
    total_pending_value = df_filtered[df_filtered["status"] == "Pending"]["total_donasi"].sum()
    total_success_value = df_filtered[df_filtered["status"] == "Berhasil"]["total_donasi"].sum()
    pending_percentage = (total_pending_value / (total_pending_value + total_success_value) * 100) if (total_pending_value + total_success_value) > 0 else 0
    
    # Strategic recommendations based on data analysis
    recommendations = []
    
    if pending_percentage > 10:
        recommendations.append({
            "priority": "🔴 URGENT",
            "action": f"Optimasi Sistem Pembayaran - {pending_percentage:.1f}% transaksi pending",
            "impact": f"Potensi revenue recovery: {format_rupiah(total_pending_value)}",
            "timeline": "1-2 minggu"
        })
    
    if market_share > 70:
        recommendations.append({
            "priority": "🟡 MEDIUM",
            "action": "Diversifikasi Metode Pembayaran",
            "impact": "Mengurangi risiko ketergantungan pada satu metode",
            "timeline": "1-3 bulan"
        })
    
    if loyalty_rate < 2:
        recommendations.append({
            "priority": "🟠 HIGH",
            "action": "Program Retensi Donatur",
            "impact": "Meningkatkan lifetime value donatur",
            "timeline": "2-4 minggu"
        })
    
    # Display recommendations in organized format
    for i, rec in enumerate(recommendations, 1):
        with st.expander(f"{rec['priority']} - Rekomendasi {i}: {rec['action']}"):
            st.write(f"**Impact**: {rec['impact']}")
            st.write(f"**Timeline**: {rec['timeline']}")
            st.write("**Action Items**:")
            if "Sistem Pembayaran" in rec['action']:
                st.write("- Audit teknis gateway pembayaran")
                st.write("- Implementasi retry mechanism otomatis")
                st.write("- Setup monitoring real-time untuk transaksi pending")
            elif "Diversifikasi" in rec['action']:
                st.write("- Riset metode pembayaran alternatif")
                st.write("- A/B test metode baru dengan user sample kecil")
                st.write("- Edukasi donatur tentang pilihan metode")
            elif "Retensi" in rec['action']:
                st.write("- Implementasi email reminder otomatis")
                st.write("- Program loyalty points atau reward")
                st.write("- Personalisasi komunikasi berdasarkan preferensi donatur")

    # Download section
    st.subheader("📥 Export Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("📊 Export Summary", export_csv(df_filtered), "summary_donasi.csv", "text/csv")
    with col2:
        st.download_button("📈 Export Analytics", export_csv(donasi_stats), "analytics_metode.csv", "text/csv")
    with col3:
        st.download_button("👥 Export Donatur", export_csv(preferensi_count), "preferensi_donatur.csv", "text/csv")


# === 👥 DONATUR ANALYSIS ===
with tabs[1]:
    st.subheader("👥 Analisis Mendalam Profil Donatur")
    
    # Segmentasi donatur berdasarkan total donasi
    donatur_stats = df_filtered.groupby("nama_donatur").agg({
        "total_donasi": "sum",
        "nama_campaign": "count",
        "metode_pembayaran": lambda x: x.mode().iloc[0] if not x.empty else "Unknown"
    }).reset_index()
    donatur_stats.columns = ["Nama Donatur", "Total Donasi", "Jumlah Transaksi", "Metode Favorit"]
    donatur_stats = donatur_stats.sort_values("Total Donasi", ascending=False)
    
    # Segmentasi donatur
    q75 = donatur_stats["Total Donasi"].quantile(0.75)
    q50 = donatur_stats["Total Donasi"].quantile(0.50)
    q25 = donatur_stats["Total Donasi"].quantile(0.25)
    
    def categorize_donor(amount):
        if amount >= q75:
            return "🌟 Premium Donor"
        elif amount >= q50:
            return "💎 Gold Donor" 
        elif amount >= q25:
            return "🥈 Silver Donor"
        else:
            return "🥉 Bronze Donor"
    
    donatur_stats["Kategori"] = donatur_stats["Total Donasi"].apply(categorize_donor)
    
    # Dashboard donatur
    col1, col2, col3, col4 = st.columns(4)
    premium_count = len(donatur_stats[donatur_stats["Kategori"] == "🌟 Premium Donor"])
    gold_count = len(donatur_stats[donatur_stats["Kategori"] == "💎 Gold Donor"])
    silver_count = len(donatur_stats[donatur_stats["Kategori"] == "🥈 Silver Donor"])
    bronze_count = len(donatur_stats[donatur_stats["Kategori"] == "🥉 Bronze Donor"])
    
    with col1:
        st.metric("🌟 Premium Donors", premium_count)
    with col2:
        st.metric("💎 Gold Donors", gold_count)
    with col3:
        st.metric("🥈 Silver Donors", silver_count)
    with col4:
        st.metric("🥉 Bronze Donors", bronze_count)
    
    # Top 10 Donatur dengan insight
    st.subheader("🏆 Hall of Fame - Top 10 Donatur")
    top_10_donatur = donatur_stats.head(10)
    
    # Tambahkan kontribusi persentase
    total_all_donations = donatur_stats["Total Donasi"].sum()
    top_10_donatur["Kontribusi %"] = (top_10_donatur["Total Donasi"] / total_all_donations * 100).round(2)
    
    st.dataframe(
        top_10_donatur[["Nama Donatur", "Total Donasi", "Jumlah Transaksi", "Metode Favorit", "Kategori", "Kontribusi %"]].style.format({
            "Total Donasi": lambda x: format_rupiah(x),
            "Kontribusi %": "{:.2f}%"
        }),
        use_container_width=True
    )
    
    # Pareto Analysis (80/20 rule)
    donatur_stats_sorted = donatur_stats.sort_values("Total Donasi", ascending=False)
    donatur_stats_sorted["Cumulative %"] = (donatur_stats_sorted["Total Donasi"].cumsum() / total_all_donations * 100)
    
    # Find 80% contributors
    pareto_80_count = len(donatur_stats_sorted[donatur_stats_sorted["Cumulative %"] <= 80])
    pareto_80_percentage = (pareto_80_count / len(donatur_stats_sorted) * 100)
    
    st.markdown("#### 📊 Analisis Pareto (80/20 Rule)")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🎯 Core Contributors (80% donasi)", f"{pareto_80_count} donatur")
    with col2:
        st.metric("📈 Persentase Core Contributors", f"{pareto_80_percentage:.1f}%")
    
    if pareto_80_percentage <= 20:
        st.success("✅ **Excellent**: Distribusi mengikuti Pareto principle yang sehat!")
        st.info("💡 **Strategi**: Fokus pada retention program untuk core contributors.")
    else:
        st.warning("⚠️ **Alert**: Distribusi donasi terlalu merata, kurang ada major contributors.")
        st.info("💡 **Strategi**: Develop program untuk mengidentifikasi dan nurture potential major donors.")
    
    # Donor behavior analysis
    st.subheader("🔍 Analisis Perilaku Donatur")
    
    # Frequency vs Value analysis
    fig_scatter = px.scatter(
        donatur_stats,
        x="Jumlah Transaksi",
        y="Total Donasi",
        color="Kategori",
        size="Total Donasi",
        hover_data=["Nama Donatur", "Metode Favorit"],
        title="Pola Perilaku Donatur: Frekuensi vs Total Donasi",
        labels={
            "Jumlah Transaksi": "Frekuensi Donasi (kali)",
            "Total Donasi": "Total Kontribusi (Rp)"
        }
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Behavioral insights
    high_freq_low_value = donatur_stats[
        (donatur_stats["Jumlah Transaksi"] >= donatur_stats["Jumlah Transaksi"].quantile(0.75)) & 
        (donatur_stats["Total Donasi"] <= donatur_stats["Total Donasi"].quantile(0.5))
    ]
    
    low_freq_high_value = donatur_stats[
        (donatur_stats["Jumlah Transaksi"] <= donatur_stats["Jumlah Transaksi"].quantile(0.5)) & 
        (donatur_stats["Total Donasi"] >= donatur_stats["Total Donasi"].quantile(0.75))
    ]
    
    st.markdown("#### 🎯 Segmentasi Perilaku Donatur:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🔄 **Frequent Small Donors**: {len(high_freq_low_value)} donatur")
        st.write("Karakteristik: Sering berdonasi dengan nominal kecil")
        st.write("💡 **Strategi**: Program micro-donation, gamifikasi")
        
    with col2:
        st.success(f"💎 **Occasional Big Donors**: {len(low_freq_high_value)} donatur")
        st.write("Karakteristik: Jarang berdonasi tapi nominal besar")
        st.write("💡 **Strategi**: VIP treatment, exclusive updates")


# === 📊 TRANSAKSI KESELURUHAN ===
with tabs[2]:
    st.subheader("📊 Analisis Komprehensif Transaksi Keseluruhan")
    
    # Time series analysis dengan trend line
    df_filtered_sorted = df_filtered.sort_values("tanggal_jam")
    daily_totals = df_filtered_sorted.groupby(df_filtered_sorted["tanggal_jam"].dt.date).agg({
        "total_donasi": "sum",
        "nama_donatur": "count"
    }).reset_index()
    daily_totals.columns = ["Tanggal", "Total Donasi", "Jumlah Transaksi"]
    
    # Calculate moving averages
    daily_totals["MA_7"] = daily_totals["Total Donasi"].rolling(window=7, min_periods=1).mean()
    daily_totals["MA_30"] = daily_totals["Total Donasi"].rolling(window=30, min_periods=1).mean()
    
    # Advanced time series chart
    fig_trend = go.Figure()
    
    # Actual data
    fig_trend.add_trace(go.Scatter(
        x=daily_totals["Tanggal"],
        y=daily_totals["Total Donasi"],
        mode='lines+markers',
        name='Donasi Harian',
        line=dict(color='lightblue', width=1),
        marker=dict(size=4)
    ))
    
    # 7-day moving average
    fig_trend.add_trace(go.Scatter(
        x=daily_totals["Tanggal"],
        y=daily_totals["MA_7"],
        mode='lines',
        name='Trend 7 Hari',
        line=dict(color='orange', width=2)
    ))
    
    # 30-day moving average
    fig_trend.add_trace(go.Scatter(
        x=daily_totals["Tanggal"],
        y=daily_totals["MA_30"],
        mode='lines',
        name='Trend 30 Hari',
        line=dict(color='red', width=3)
    ))
    
    fig_trend.update_layout(
        title="Tren Donasi Harian dengan Moving Average",
        xaxis_title="Tanggal",
        yaxis_title="Total Donasi (Rp)",
        hovermode='x unified'
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Statistical analysis
    max_day = daily_totals.loc[daily_totals["Total Donasi"].idxmax()]
    min_day = daily_totals.loc[daily_totals["Total Donasi"].idxmin()]
    avg_daily = daily_totals["Total Donasi"].mean()
    std_daily = daily_totals["Total Donasi"].std()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📈 Hari Tertinggi", f"{max_day['Tanggal']}", f"{format_rupiah(max_day['Total Donasi'])}")
    with col2:
        st.metric("📉 Hari Terendah", f"{min_day['Tanggal']}", f"{format_rupiah(min_day['Total Donasi'])}")
    with col3:
        st.metric("📊 Rata-rata Harian", format_rupiah(avg_daily))
    with col4:
        volatility = (std_daily / avg_daily * 100) if avg_daily > 0 else 0
        st.metric("📊 Volatilitas", f"{volatility:.1f}%")
    
    # Trend analysis and insights
    st.markdown("#### 📈 Analisis Tren dan Pola:")
    
    # Calculate recent trend (last 30 days vs previous 30 days)
    if len(daily_totals) >= 60:
        recent_30 = daily_totals.tail(30)["Total Donasi"].mean()
        previous_30 = daily_totals.iloc[-60:-30]["Total Donasi"].mean()
        trend_change = ((recent_30 - previous_30) / previous_30 * 100) if previous_30 > 0 else 0
        
        if trend_change > 10:
            st.success(f"📈 **Tren Positif**: Donasi meningkat {trend_change:.1f}% dalam 30 hari terakhir!")
            st.info("💡 **Strategi**: Pertahankan momentum dengan intensifikasi campaign yang sedang berjalan.")
        elif trend_change < -10:
            st.warning(f"📉 **Tren Menurun**: Donasi turun {abs(trend_change):.1f}% dalam 30 hari terakhir.")
            st.info("💡 **Strategi**: Evaluasi campaign strategy, launch program reaktivasi donatur.")
        else:
            st.info(f"📊 **Tren Stabil**: Fluktuasi normal {trend_change:.1f}% dalam 30 hari terakhir.")
    
    # Volatility insights
    if volatility > 50:
        st.warning("⚠️ **Volatilitas Tinggi**: Donasi sangat fluktuatif. Perlu stabilisasi melalui campaign berkelanjutan.")
    elif volatility < 20:
        st.success("✅ **Stabilitas Baik**: Pola donasi relatif konsisten.")
    
    
# === 📅 TRANSAKSI HARIAN ===
with tabs[3]:
    st.subheader("📅 Analisis Mendalam Pola Transaksi Harian")
    
    # Buat data harian dengan insight yang lebih dalam
    harian = df_filtered.groupby("hari").agg({
        "total_donasi": ["sum", "mean", "count"],
        "nama_donatur": "nunique"
    }).round(2)
    harian.columns = ["Total Donasi", "Rata-rata per Transaksi", "Jumlah Transaksi", "Donatur Unik"]
    harian = harian.reset_index()
    
    # Urutkan berdasarkan urutan hari dalam seminggu
    day_order = get_indonesian_day_order()
    harian['hari'] = pd.Categorical(harian['hari'], categories=day_order, ordered=True)
    harian = harian.sort_values('hari')
    
    # Multi-metric daily analysis
    fig_daily = go.Figure()
    
    # Bar chart untuk total donasi
    fig_daily.add_trace(go.Bar(
        name="Total Donasi (Juta Rp)",
        x=harian["hari"],
        y=harian["Total Donasi"] / 1000000,
        yaxis="y",
        marker_color="lightblue",
        text=[f"{x/1000000:.1f}M" for x in harian["Total Donasi"]],
        textposition="outside"
    ))
    
    # Line chart untuk jumlah transaksi
    fig_daily.add_trace(go.Scatter(
        name="Jumlah Transaksi",
        x=harian["hari"],
        y=harian["Jumlah Transaksi"],
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="red", width=3),
        marker=dict(size=8)
    ))
    
    fig_daily.update_layout(
        title="Analisis Komprehensif Pola Donasi Harian",
        xaxis_title="Hari",
        yaxis=dict(title="Total Donasi (Juta Rp)", side="left"),
        yaxis2=dict(title="Jumlah Transaksi", side="right", overlaying="y"),
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig_daily, use_container_width=True)
    
    # Daily performance metrics
    max_day = harian.loc[harian["Total Donasi"].idxmax()]
    min_day = harian.loc[harian["Total Donasi"].idxmin()]
    avg_daily = harian["Total Donasi"].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏆 Hari Terbaik", max_day["hari"], format_rupiah(max_day["Total Donasi"]))
    with col2:
        st.metric("📉 Hari Terlemah", min_day["hari"], format_rupiah(min_day["Total Donasi"]))
    with col3:
        st.metric("📊 Rata-rata Harian", format_rupiah(avg_daily))
    with col4:
        best_avg_transaction = harian.loc[harian["Rata-rata per Transaksi"].idxmax()]
        st.metric("💎 Nilai Tertinggi per Transaksi", best_avg_transaction["hari"], format_rupiah(best_avg_transaction["Rata-rata per Transaksi"]))
    
    # Weekend vs Weekday analysis
    weekend_days = ["Sabtu", "Minggu"]
    weekday_data = harian[~harian["hari"].isin(weekend_days)]
    weekend_data = harian[harian["hari"].isin(weekend_days)]
    
    weekday_avg = weekday_data["Total Donasi"].mean()
    weekend_avg = weekend_data["Total Donasi"].mean()
    
    st.markdown("#### 📊 Analisis Weekday vs Weekend:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Rata-rata Weekday", format_rupiah(weekday_avg))
    with col2:
        st.metric("🎉 Rata-rata Weekend", format_rupiah(weekend_avg))
    with col3:
        weekend_performance = ((weekend_avg - weekday_avg) / weekday_avg * 100) if weekday_avg > 0 else 0
        st.metric("📈 Weekend vs Weekday", f"{weekend_performance:+.1f}%")
    
    # Strategic insights for daily patterns
    st.markdown("#### 💡 Insight dan Rekomendasi Strategis:")
    
    if weekend_performance > 20:
        st.success("🎉 **Weekend Premium**: Donasi weekend 20%+ lebih tinggi dari weekday!")
        st.info("📅 **Strategi**: Jadwalkan campaign utama di weekend. Gunakan weekday untuk nurturing dan engagement.")
    elif weekend_performance < -20:
        st.info("💼 **Weekday Focus**: Donasi weekday lebih tinggi dari weekend.")
        st.info("📅 **Strategi**: Fokus promosi intensif Senin-Jumat. Weekend untuk content storytelling.")
    else:
        st.info("⚖️ **Balanced Pattern**: Pola donasi relatif seimbang sepanjang minggu.")
    
    # Day-specific recommendations
    performance_ranking = harian.sort_values("Total Donasi", ascending=False)
    top_3_days = performance_ranking.head(3)["hari"].tolist()
    bottom_2_days = performance_ranking.tail(2)["hari"].tolist()
    
    st.success(f"🎯 **Prime Time Days**: {', '.join(top_3_days)} - Fokuskan campaign besar di hari-hari ini.")
    st.warning(f"⚠️ **Boost Needed**: {', '.join(bottom_2_days)} - Perlu strategi khusus untuk meningkatkan performa.")
    
    # Hour-of-day analysis if timestamp available
    if "tanggal_jam" in df_filtered.columns:
        st.subheader("🕐 Analisis Pola Jam Donasi")
        df_filtered["jam"] = df_filtered["tanggal_jam"].dt.hour
        hourly_pattern = df_filtered.groupby("jam").agg({
            "total_donasi": "sum",
            "nama_donatur": "count"
        }).reset_index()
        hourly_pattern.columns = ["Jam", "Total Donasi", "Jumlah Transaksi"]
        
        fig_hourly = px.line(
            hourly_pattern,
            x="Jam", 
            y="Total Donasi",
            title="Pola Donasi per Jam dalam Sehari",
            markers=True
        )
        fig_hourly.update_xaxes(tickmode='linear', tick0=0, dtick=2)
        st.plotly_chart(fig_hourly, use_container_width=True)
        
        # Peak hours analysis
        peak_hour = hourly_pattern.loc[hourly_pattern["Total Donasi"].idxmax()]
        quiet_hour = hourly_pattern.loc[hourly_pattern["Total Donasi"].idxmin()]
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"⏰ **Peak Hour**: {peak_hour['Jam']:02d}:00 - {format_rupiah(peak_hour['Total Donasi'])}")
        with col2:
            st.info(f"😴 **Quiet Hour**: {quiet_hour['Jam']:02d}:00 - {format_rupiah(quiet_hour['Total Donasi'])}")
        
        # Time-based recommendations
        if peak_hour["Jam"] >= 9 and peak_hour["Jam"] <= 17:
            st.info("💼 **Working Hours Peak**: Donatur aktif saat jam kerja. Optimalkan push notification saat jam makan siang.")
        elif peak_hour["Jam"] >= 19 and peak_hour["Jam"] <= 22:
            st.info("🌙 **Evening Peak**: Donatur aktif malam hari. Fokus social media campaign sore-malam.")
        else:
            st.info("🌅 **Off-Peak Pattern**: Pola unik donatur. Analisis lebih lanjut diperlukan.")


# === 📆 TRANSAKSI BULANAN ===
with tabs[4]:
    st.subheader("📆 Analisis Strategis Pola Transaksi Bulanan")
    
    # Enhanced monthly analysis
    bulanan = df_filtered.groupby("bulan").agg({
        "total_donasi": ["sum", "mean", "count"],
        "nama_donatur": "nunique",
        "nama_campaign": "nunique"
    }).round(2)
    bulanan.columns = ["Total Donasi", "Rata-rata per Transaksi", "Jumlah Transaksi", "Donatur Unik", "Campaign Aktif"]
    bulanan = bulanan.reset_index()
    
    # Calculate additional metrics
    bulanan["Donasi per Donatur"] = bulanan["Total Donasi"] / bulanan["Donatur Unik"]
    bulanan["Donasi per Campaign"] = bulanan["Total Donasi"] / bulanan["Campaign Aktif"]
    
    # Urutkan berdasarkan urutan bulan dalam tahun
    month_order = get_indonesian_month_order()
    bulanan['bulan'] = pd.Categorical(bulanan['bulan'], categories=month_order, ordered=True)
    bulanan = bulanan.sort_values('bulan')
    
    # Advanced monthly visualization
    fig_monthly = go.Figure()
    
    # Bar untuk total donasi
    fig_monthly.add_trace(go.Bar(
        name="Total Donasi (Juta Rp)",
        x=bulanan["bulan"],
        y=bulanan["Total Donasi"] / 1000000,
        yaxis="y",
        marker_color="lightcoral",
        text=[f"{x/1000000:.1f}M" for x in bulanan["Total Donasi"]],
        textposition="outside"
    ))
    
    # Line untuk donatur unik
    fig_monthly.add_trace(go.Scatter(
        name="Donatur Unik",
        x=bulanan["bulan"],
        y=bulanan["Donatur Unik"],
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="green", width=3),
        marker=dict(size=10)
    ))
    
    fig_monthly.update_layout(
        title="Analisis Komprehensif Performa Bulanan",
        xaxis_title="Bulan",
        yaxis=dict(title="Total Donasi (Juta Rp)", side="left"),
        yaxis2=dict(title="Donatur Unik", side="right", overlaying="y"),
        legend=dict(x=0.01, y=0.99)
    )
    fig_monthly.update_xaxes(tickangle=45)
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Monthly performance dashboard
    best_month = bulanan.loc[bulanan["Total Donasi"].idxmax()]
    worst_month = bulanan.loc[bulanan["Total Donasi"].idxmin()]
    most_active_donors = bulanan.loc[bulanan["Donatur Unik"].idxmax()]
    highest_per_donor = bulanan.loc[bulanan["Donasi per Donatur"].idxmax()]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🏆 Bulan Terbaik", best_month["bulan"], format_rupiah(best_month["Total Donasi"]))
        st.metric("👥 Donatur Paling Aktif", most_active_donors["bulan"], f"{most_active_donors['Donatur Unik']:,} orang")
    with col2:
        st.metric("📉 Perlu Perbaikan", worst_month["bulan"], format_rupiah(worst_month["Total Donasi"]))
        st.metric("💎 Nilai Tertinggi per Donatur", highest_per_donor["bulan"], format_rupiah(highest_per_donor["Donasi per Donatur"]))
    
    # Seasonal analysis
    st.markdown("#### 🌍 Analisis Pola Musiman:")
    
    # Define seasons (adjusted for Indonesia)
    def get_season(month):
        if month in ["Desember", "Januari", "Februari"]:
            return "🎄 Akhir Tahun"
        elif month in ["Maret", "April", "Mei"]:
            return "🌸 Awal Tahun"
        elif month in ["Juni", "Juli", "Agustus"]:
            return "☀️ Pertengahan Tahun"
        else:
            return "🍂 Menuju Akhir Tahun"
    
    bulanan["Musim"] = bulanan["bulan"].apply(get_season)
    seasonal_performance = bulanan.groupby("Musim")["Total Donasi"].sum().sort_values(ascending=False)
    
    col1, col2 = st.columns(2)
    with col1:
        fig_seasonal = px.pie(
            values=seasonal_performance.values,
            names=seasonal_performance.index,
            title="Distribusi Donasi per Musim",
            hole=0.4
        )
        st.plotly_chart(fig_seasonal, use_container_width=True)
    
    with col2:
        st.markdown("**Insight Pola Musiman:**")
        best_season = seasonal_performance.index[0]
        best_season_value = seasonal_performance.iloc[0]
        total_seasonal = seasonal_performance.sum()
        season_percentage = (best_season_value / total_seasonal * 100)
        
        st.success(f"🎯 **Peak Season**: {best_season}")
        st.info(f"📊 **Dominasi**: {season_percentage:.1f}% total donasi")
        
        if "Akhir Tahun" in best_season:
            st.write("💡 **Insight**: Donatur lebih murah hati menjelang akhir tahun")
            st.write("🎯 **Strategi**: Intensifikasi campaign November-Januari")
        elif "Awal Tahun" in best_season:
            st.write("💡 **Insight**: Semangat berbagi tinggi di awal tahun")
            st.write("🎯 **Strategi**: Manfaatkan momentum resolusi tahun baru")
    
    # Month-over-month growth analysis
    bulanan_sorted = bulanan.sort_values("bulan")
    bulanan_sorted["MoM Growth"] = bulanan_sorted["Total Donasi"].pct_change() * 100
    
    st.subheader("📈 Analisis Pertumbuhan Month-over-Month")
    
    fig_growth = px.bar(
        bulanan_sorted,
        x="bulan",
        y="MoM Growth",
        title="Pertumbuhan Donasi Month-over-Month (%)",
        color="MoM Growth",
        color_continuous_scale=["red", "yellow", "green"]
    )
    fig_growth.update_xaxes(tickangle=45)
    fig_growth.add_hline(y=0, line_dash="dash", line_color="black")
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # Growth insights
    positive_growth_months = bulanan_sorted[bulanan_sorted["MoM Growth"] > 0]
    negative_growth_months = bulanan_sorted[bulanan_sorted["MoM Growth"] < 0]
    
    if len(positive_growth_months) > len(negative_growth_months):
        st.success(f"📈 **Tren Positif**: {len(positive_growth_months)} bulan dengan pertumbuhan positif")
    else:
        st.warning(f"📉 **Perlu Perhatian**: {len(negative_growth_months)} bulan dengan penurunan")
        
    st.info(f"Rata-Rata Donasi Per bulan: **Rp {bulanan['Total Donasi'].mean():,.0f}**")
    
    # Strategic recommendations based on monthly patterns
    st.markdown("#### 🎯 Rekomendasi Strategis Bulanan:")
    
    # Identify months that need attention
    avg_monthly = bulanan["Total Donasi"].mean()
    underperforming_months = bulanan[bulanan["Total Donasi"] < avg_monthly * 0.8]
    
    if not underperforming_months.empty:
        with st.expander("⚠️ Bulan yang Perlu Boost"):
            st.markdown("Beberapa bulan performanya masih di bawah rata-rata. Berikut ini bulan-bulan tersebut beserta saran strategi untuk meningkatkan hasil donasinya:")

            for _, month_data in underperforming_months.iterrows():
                gap = avg_monthly - month_data["Total Donasi"]
                st.markdown(f"""
                ### 📅 **{month_data['bulan']}**
                - Selisih dari rata-rata: **{format_rupiah(gap)}**
                """)

                # Penjelasan strategi dengan bahasa lebih mudah dipahami
                if month_data["bulan"] in ["Juni", "Juli"]:
                    st.markdown("💡 **Saran Strategi**: Karena ini musim liburan sekolah, coba buat campaign yang menarik untuk keluarga dan anak-anak. Misalnya, bantu anak yatim, pendidikan, atau kegiatan liburan yang bermanfaat.")
                elif month_data["bulan"] in ["Januari", "Februari"]:
                    st.markdown("💡 **Saran Strategi**: Awal tahun biasanya orang masih pemulihan dari pengeluaran liburan. Coba gunakan cerita yang menyentuh hati agar orang tetap terdorong untuk berdonasi.")
                else:
                    st.markdown("💡 **Saran Strategi**: Coba evaluasi waktu dan pesan dari campaign. Mungkin perlu disesuaikan supaya lebih menarik perhatian di bulan tersebut.")


    
    # Best practices recommendations
    top_performing_months = bulanan.nlargest(3, "Total Donasi")
    with st.expander("🏆 Best Practices dari Bulan Terbaik"):
        st.markdown("Berikut adalah bulan dengan performa donasi terbaik, yang bisa dijadikan acuan strategi ke depan:")
        
        for _, month_data in top_performing_months.iterrows():
            st.markdown(f"""
            ✅ **{month_data['bulan']}**
            - Campaign Aktif: **{month_data['Campaign Aktif']}**
            - Donatur Unik: **{month_data['Donatur Unik']}**
            """)


# === 📈 TREN CAMPAIGN ===
# === 📈 ANALISIS MENDALAM PERFORMA CAMPAIGN ===
with tabs[5]:
    st.subheader("📈 Analisis Mendalam Performa Campaign")
    
    # Comprehensive campaign analysis
    campaign_stats = df_filtered.groupby("nama_campaign").agg({
        "total_donasi": ["sum", "mean", "count"],
        "nama_donatur": ["nunique", "count"],
        "tanggal_jam": ["min", "max"]
    }).round(2)
    
    campaign_stats.columns = [
        "Total Donasi", "Rata-rata per Transaksi", "Jumlah Transaksi",
        "Donatur Unik", "Total Kontribusi", "Tanggal Mulai", "Tanggal Selesai"
    ]
    campaign_stats = campaign_stats.reset_index()
    
    # Calculate campaign duration and efficiency metrics
    campaign_stats["Durasi (hari)"] = (campaign_stats["Tanggal Selesai"] - campaign_stats["Tanggal Mulai"]).dt.days + 1
    campaign_stats["Donasi per Hari"] = campaign_stats["Total Donasi"] / campaign_stats["Durasi (hari)"]
    campaign_stats["Conversion Rate"] = (campaign_stats["Donatur Unik"] / campaign_stats["Total Kontribusi"] * 100).round(2)
    campaign_stats["Repeat Rate"] = ((campaign_stats["Total Kontribusi"] - campaign_stats["Donatur Unik"]) / campaign_stats["Donatur Unik"] * 100).round(2)
    
    # Sort by total donation
    campaign_stats = campaign_stats.sort_values("Total Donasi", ascending=False)
    
    # Campaign performance dashboard
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Total Campaign", len(campaign_stats))
    with col2:
        avg_per_campaign = campaign_stats["Total Donasi"].mean()
        st.metric("💰 Rata-rata per Campaign", format_rupiah(avg_per_campaign))
    
    most_efficient = campaign_stats.loc[campaign_stats["Donasi per Hari"].idxmax()]
    st.metric(
        label="⚡ Paling Efisien",
        value=most_efficient["nama_campaign"],
        delta=f"{format_rupiah(most_efficient['Donasi per Hari'])}/hari"
    )

    longest_duration = campaign_stats.loc[campaign_stats["Durasi (hari)"].idxmax()]
    st.metric(
        label="⏱️ Durasi Terpanjang",
        value=longest_duration["nama_campaign"],
        delta=f"{longest_duration['Durasi (hari)']} hari"
    )
        
    # === GRAFIK 1: TOP 10 CAMPAIGN BERDASARKAN TOTAL DONASI ===
    st.markdown("### 📊 Ranking Campaign Berdasarkan Total Donasi")
    
    top_10_campaigns = campaign_stats.head(10)
    
    fig_campaign = px.bar(
        top_10_campaigns.sort_values("Total Donasi", ascending=True),
        x="Total Donasi",
        y="nama_campaign",
        orientation="h",
        title="Top 10 Campaign Berdasarkan Total Donasi",
        labels={"Total Donasi": "Total Donasi (Rp)", "nama_campaign": "Nama Campaign"},
        height=600,
        color="Total Donasi",
        color_continuous_scale="viridis"
    )
    fig_campaign.update_layout(
        xaxis_title="Total Donasi (Rp)",
        yaxis_title="Nama Campaign",
        font=dict(size=12)
    )
    st.plotly_chart(fig_campaign, use_container_width=True)
    
    # Penjelasan Grafik 1
    with st.expander("💡 Penjelasan & Insight"):
        st.markdown(f"""
        **Analisis Performa Campaign:**
        - **Campaign Teratas:** {top_10_campaigns.iloc[0]['nama_campaign']} dengan total donasi {format_rupiah(top_10_campaigns.iloc[0]['Total Donasi'])}
        - **Gap Performa:** Selisih antara campaign terbaik dan ke-10 adalah {format_rupiah(top_10_campaigns.iloc[0]['Total Donasi'] - top_10_campaigns.iloc[9]['Total Donasi'])}
        - **Distribusi:** {'Terdapat kesenjangan besar' if (top_10_campaigns.iloc[0]['Total Donasi'] / top_10_campaigns.iloc[9]['Total Donasi']) > 5 else 'Distribusi relatif merata'} antar campaign top 10
        
        **Rekomendasi Strategis:**
        - 🎯 **Replikasi Sukses:** Pelajari strategi campaign teratas untuk diterapkan pada campaign lain
        - 📈 **Optimasi Konten:** Campaign dengan performa rendah perlu revisi storytelling dan visual
        - 🔄 **Resource Allocation:** Alokasikan lebih banyak resource marketing pada campaign dengan potensi tinggi
        """)
    
    # === GRAFIK 2: EFISIENSI CAMPAIGN (DONASI PER HARI) ===
    st.markdown("### ⚡ Efisiensi Campaign (Donasi per Hari)")
    
    top_efficient = campaign_stats.nlargest(10, "Donasi per Hari")
    
    fig_efficiency = px.scatter(
        top_efficient,
        x="Durasi (hari)",
        y="Donasi per Hari",
        size="Total Donasi",
        color="Jumlah Transaksi",
        hover_name="nama_campaign",
        title="Efisiensi Campaign: Donasi per Hari vs Durasi",
        labels={
            "Durasi (hari)": "Durasi Campaign (Hari)",
            "Donasi per Hari": "Donasi per Hari (Rp)",
            "Total Donasi": "Total Donasi",
            "Jumlah Transaksi": "Jumlah Transaksi"
        },
        height=500
    )
    st.plotly_chart(fig_efficiency, use_container_width=True)
    
    # Penjelasan Grafik 2
    with st.expander("💡 Penjelasan & Insight"):
        most_efficient_campaign = campaign_stats.loc[campaign_stats["Donasi per Hari"].idxmax()]
        avg_efficiency = campaign_stats["Donasi per Hari"].mean()
        
        st.markdown(f"""
        **Analisis Efisiensi Campaign:**
        - **Campaign Paling Efisien:** {most_efficient_campaign['nama_campaign']} dengan {format_rupiah(most_efficient_campaign['Donasi per Hari'])}/hari
        - **Rata-rata Efisiensi:** {format_rupiah(avg_efficiency)}/hari
        - **Insight Durasi:** Campaign dengan durasi {'pendek cenderung lebih efisien' if campaign_stats['Donasi per Hari'].corr(campaign_stats['Durasi (hari)']) < -0.3 else 'tidak berkorelasi langsung dengan efisiensi'}
        
        **Rekomendasi Strategis:**
        - ⏰ **Durasi Optimal:** Fokus pada campaign dengan durasi 7-30 hari untuk efisiensi maksimal
        - 🚀 **Quick Wins:** Prioritaskan campaign dengan potensi hasil cepat
        - 📊 **Monitoring:** Evaluasi harian untuk campaign dengan target tinggi
        """)
    
    # === GRAFIK 3: ANALISIS ENGAGEMENT (REPEAT RATE VS CONVERSION RATE) ===
    st.markdown("### 🎯 Analisis Engagement Campaign")
    
    fig_engagement = px.scatter(
        campaign_stats,
        x="Conversion Rate",
        y="Repeat Rate",
        size="Donatur Unik",
        color="Total Donasi",
        hover_name="nama_campaign",
        title="Analisis Engagement: Conversion Rate vs Repeat Rate",
        labels={
            "Conversion Rate": "Conversion Rate (%)",
            "Repeat Rate": "Repeat Rate (%)",
            "Donatur Unik": "Jumlah Donatur Unik",
            "Total Donasi": "Total Donasi"
        },
        height=500,
        color_continuous_scale="plasma"
    )
    
    # Add quadrant lines
    avg_conversion = campaign_stats["Conversion Rate"].mean()
    avg_repeat = campaign_stats["Repeat Rate"].mean()
    
    fig_engagement.add_hline(y=avg_repeat, line_dash="dash", line_color="red", 
                        annotation_text=f"Avg Repeat Rate: {avg_repeat:.1f}%")
    fig_engagement.add_vline(x=avg_conversion, line_dash="dash", line_color="red", 
                        annotation_text=f"Avg Conversion: {avg_conversion:.1f}%")
    
    st.plotly_chart(fig_engagement, use_container_width=True)
    
    # Penjelasan Grafik 3
    with st.expander("💡 Penjelasan & Insight"):
        high_conversion = campaign_stats[campaign_stats["Conversion Rate"] > avg_conversion]
        high_repeat = campaign_stats[campaign_stats["Repeat Rate"] > avg_repeat]
        stars = campaign_stats[(campaign_stats["Conversion Rate"] > avg_conversion) & 
                            (campaign_stats["Repeat Rate"] > avg_repeat)]
        
        st.markdown(f"""
        **Segmentasi Campaign berdasarkan Engagement:**
        
        **🌟 STAR CAMPAIGNS ({len(stars)} campaign):**
        - Conversion Rate tinggi DAN Repeat Rate tinggi
        - Campaign dengan loyalitas dan akuisisi terbaik
        
        **📈 HIGH ACQUISITION ({len(high_conversion) - len(stars)} campaign):**
        - Conversion Rate tinggi, Repeat Rate rendah
        - Baik menarik donatur baru, perlu strategi retensi
        
        **🔄 HIGH RETENTION ({len(high_repeat) - len(stars)} campaign):**
        - Repeat Rate tinggi, Conversion Rate rendah
        - Donatur loyal tapi sulit akuisisi baru
        
        **Rekomendasi Strategis:**
        - ⭐ **Star Campaigns:** Jadikan template untuk campaign baru
        - 📊 **High Acquisition:** Implementasi program loyalitas dan follow-up
        - 🎯 **High Retention:** Tingkatkan awareness dan reach campaign
        """)
    
    # === GRAFIK 4: TREN WAKTU PERFORMA CAMPAIGN ===
    st.markdown("### 📅 Timeline Performa Campaign")
    
    # Create timeline data
    timeline_data = []
    for _, campaign in campaign_stats.iterrows():
        timeline_data.append({
            'Campaign': campaign['nama_campaign'],
            'Start': campaign['Tanggal Mulai'],
            'Finish': campaign['Tanggal Selesai'],
            'Total_Donasi': campaign['Total Donasi'],
            'Efficiency': campaign['Donasi per Hari']
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    
    fig_timeline = px.timeline(
        timeline_df.head(15),  # Top 15 campaigns
        x_start="Start",
        x_end="Finish",
        y="Campaign",
        color="Total_Donasi",
        title="Timeline Top 15 Campaign",
        height=600,
        color_continuous_scale="viridis"
    )
    
    fig_timeline.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Penjelasan Grafik 4
    with st.expander("💡 Penjelasan & Insight"):
        # Analyze timing patterns
        campaign_stats['Bulan_Mulai'] = pd.to_datetime(campaign_stats['Tanggal Mulai']).dt.month
        monthly_performance = campaign_stats.groupby('Bulan_Mulai')['Total Donasi'].mean()
        best_month = monthly_performance.idxmax()
        
        st.markdown(f"""
        **Analisis Timeline Campaign:**
        - **Bulan Terbaik untuk Launch:** Bulan ke-{best_month} dengan rata-rata donasi {format_rupiah(monthly_performance[best_month])}
        - **Pola Seasonality:** {'Teridentifikasi pola musiman' if monthly_performance.std() > monthly_performance.mean() * 0.2 else 'Tidak ada pola musiman yang signifikan'}
        - **Overlap Analysis:** {'Banyak campaign berjalan bersamaan' if len(timeline_df) > 10 else 'Campaign relatif tersebar waktu'}
        
        **Rekomendasi Strategis:**
        - 📅 **Timing Optimal:** Launch campaign baru pada bulan-bulan dengan performa historis terbaik
        - 🔄 **Overlap Management:** Hindari terlalu banyak campaign aktif bersamaan
        - 📈 **Seasonal Planning:** Sesuaikan jenis campaign dengan karakteristik musiman
        """)
    
    # === TABEL EVALUASI CAMPAIGN ===
    # Menampilkan judul bagian
    st.markdown("### 🚨 Campaign Bermasalah yang Perlu Perhatian")

    # Menentukan campaign yang dianggap bermasalah
    problematic = campaign_stats[
        (campaign_stats['Total Donasi'] < avg_per_campaign * 0.5) |
        (campaign_stats['Conversion Rate'] < 50) |
        (campaign_stats['Donasi per Hari'] < campaign_stats['Donasi per Hari'].quantile(0.25))
    ]

    if not problematic.empty:
        st.warning(f"⚠️ {len(problematic)} campaign memerlukan evaluasi mendalam:")

        # Siapkan tabel dengan kolom yang relevan
        table_data = problematic[[
            'nama_campaign', 
            'Total Donasi', 
            'Donasi per Hari', 
            'Conversion Rate'
        ]].copy()

        # Format kolom rupiah
        table_data['Total Donasi'] = table_data['Total Donasi'].apply(format_rupiah)
        table_data['Donasi per Hari'] = table_data['Donasi per Hari'].apply(format_rupiah)
        table_data['Conversion Rate'] = table_data['Conversion Rate'].astype(str) + '%'

        # Tampilkan hanya 5 teratas jika terlalu banyak
        st.dataframe(table_data.head(5), use_container_width=True)

    
    # === TABEL DETAIL PERFORMA CAMPAIGN ===
    st.markdown("### 📋 Detail Performa Seluruh Campaign")
    
    # Performance categorization
    campaign_stats['Kategori Performa'] = pd.cut(
        campaign_stats['Total Donasi'],
        bins=5,
        labels=['Sangat Rendah', 'Rendah', 'Sedang', 'Tinggi', 'Sangat Tinggi']
    )
    
    # Display comprehensive table
    display_columns = [
        'nama_campaign', 'Total Donasi', 'Jumlah Transaksi', 'Donatur Unik',
        'Rata-rata per Transaksi', 'Durasi (hari)', 'Donasi per Hari',
        'Conversion Rate', 'Repeat Rate', 'Kategori Performa'
    ]
    
    formatted_stats = campaign_stats[display_columns].copy()
    formatted_stats['Total Donasi'] = formatted_stats['Total Donasi'].apply(format_rupiah)
    formatted_stats['Rata-rata per Transaksi'] = formatted_stats['Rata-rata per Transaksi'].apply(format_rupiah)
    formatted_stats['Donasi per Hari'] = formatted_stats['Donasi per Hari'].apply(format_rupiah)
    
    st.dataframe(formatted_stats, use_container_width=True, height=400)
    
    # === INSIGHT DAN REKOMENDASI STRATEGIS KOMPREHENSIF ===
    st.markdown("## 🎯 Ringkasan Insight & Rekomendasi Strategis")

    # Hitung data performa
    total_campaigns = len(campaign_stats)
    high_performers = len(campaign_stats[campaign_stats['Total Donasi'] > avg_per_campaign])
    avg_duration = campaign_stats['Durasi (hari)'].mean()
    avg_donors_per_campaign = campaign_stats['Donatur Unik'].mean()

    # Insight Performa
    with st.expander("📊 Ringkasan Kinerja Campaign", expanded=True):
        st.markdown(f"""
        - 📈 **{high_performers} dari {total_campaigns} campaign** ({high_performers/total_campaigns*100:.1f}%) memiliki hasil di atas rata-rata  
        - ⏱️ **Rata-rata durasi campaign:** {avg_duration:.0f} hari  
        - 👥 **Rata-rata jumlah donatur per campaign:** {avg_donors_per_campaign:.0f} orang  
        - 💰 **Total donasi yang terkumpul:** {format_rupiah(campaign_stats['Total Donasi'].sum())}
        """)

    # Rekomendasi Strategis
    with st.expander("🚀 Rekomendasi Strategi yang Bisa Dilakukan", expanded=True):
        st.markdown("#### 📅 Jangka Pendek (1–3 bulan ke depan)")
        st.markdown("""
        - 🎯 **Fokus ke campaign yang paling sukses:** Alokasikan sekitar 60% dana promosi ke 5 campaign terbaik  
        - 📱 **Perbanyak promosi online:** Tingkatkan posting di media sosial terutama untuk campaign yang kurang berjalan  
        - 👥 **Jaga relasi dengan donatur lama:** Buat program agar mereka mau berdonasi lagi
        """)

        st.markdown("#### 📆 Jangka Menengah (3–6 bulan)")
        st.markdown("""
        - 🧪 **Coba-coba metode promosi (A/B Testing):** Bandingkan beberapa pendekatan di campaign yang kurang berhasil  
        - 🤝 **Bangun kerja sama baru:** Libatkan influencer atau komunitas untuk campaign berikutnya  
        - 🖼️ **Tingkatkan kualitas konten:** Perbaiki cerita dan visual agar lebih menarik
        """)

        st.markdown("#### 📈 Jangka Panjang (6 bulan ke atas)")
        st.markdown("""
        - 🔄 **Evaluasi campaign yang kurang efektif:** Pertimbangkan untuk menghentikan atau ubah cara promosinya  
        - 🎉 **Manfaatkan momen spesial:** Buat campaign khusus saat event besar seperti Ramadan, tahun baru, dll.  
        - 💡 **Eksperimen dengan format baru:** Coba gaya campaign unik berdasarkan data yang sudah terkumpul
        """)

    # Daftar Tindakan Prioritas
    with st.expander("✅ Daftar Tindakan yang Harus Diprioritaskan", expanded=True):
        st.markdown("#### 🔥 Segera Dikerjakan (Minggu ini)")
        urgent_actions = [
            "Evaluasi 5 campaign dengan performa terendah",
            "Pindahkan anggaran dari campaign yang tidak efektif",
            "Pasang sistem pelacakan data yang lebih detail"
        ]
        for action in urgent_actions:
            st.markdown(f"- [ ] {action}")

        st.markdown("#### ⚡ Penting (Dalam Bulan Ini)")
        important_actions = [
            "Jalankan program loyalitas donatur",
            "Perbarui konten campaign yang tidak menarik",
            "Siapkan sistem pengujian A/B sederhana"
        ]
        for action in important_actions:
            st.markdown(f"- [ ] {action}")

        st.markdown("#### 📈 Strategis (3 Bulan ke Depan)")
        strategic_actions = [
            "Buat template campaign berdasarkan yang paling sukses",
            "Bangun sistem kerja sama jangka panjang",
            "Optimalkan seluruh portofolio campaign secara berkala"
        ]
        for action in strategic_actions:
            st.markdown(f"- [ ] {action}")


    # Export data option
    st.markdown("---")
    if st.button("📥 Download Detail Analisis Campaign", key="download_campaign"):
        # Create comprehensive export data
        export_data = campaign_stats.copy()
        export_data['Total Donasi'] = export_data['Total Donasi'].apply(lambda x: f"{x:,.0f}")
        export_data['Rata-rata per Transaksi'] = export_data['Rata-rata per Transaksi'].apply(lambda x: f"{x:,.0f}")
        export_data['Donasi per Hari'] = export_data['Donasi per Hari'].apply(lambda x: f"{x:,.0f}")
        
        st.download_button(
            label="💾 Download CSV",
            data=export_data.to_csv(index=False),
            file_name=f"analisis_campaign_detail_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
