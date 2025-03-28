"""
Script untuk Program Utama
Script ini berfungsi untuk menjalankan program utama dan mengintegrasikan berbagai komponen
"""

import time

from akun.akun import InfoAkun
from api_rahasia.konfigurasi import Konfigurasi
from baca_konfig import Inisiasi
from fungsi.fungsi import Fungsi
from strategi.strategi import Strategi
from ui.ui_sederhana import UI

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"

# KONSTANTA
MODE_BACKTEST = False
PERIODE_BACKTEST = 1000
# Interval waktu yang digunakan untuk melakukan evaluasi tindakan
# Interval ini berbeda dengan interval waktu yang dipergunakan dalam
# dalam menarik data chart
INTERVAL_EVALUASI = ["0.1 menit"]
# Interval waktu chart yang dikembalikan oleh tradingview
INTERVAL_CHART = ["4 jam"]
# VARIABEL ASET
ASET_DATA = "1000SHIB/USDT"
ASET = "1000SHIBUSDT"
EXCHANGE = "BINANCE"
DATA_EXCHANGE = "binanceusdm"
LEVERAGE = 10
INISIATOR_WAKTU = True
JUMLAH_ERROR = 0
JUMLAH_TRADE_USDT = 1
inisiasi_konektor = Inisiasi()
konektor_exchange = inisiasi_konektor.exchange()
info_akun = InfoAkun(konektor_exchange)

pengguna_email = Konfigurasi().Email["USERNAME"]
kunci_email = Konfigurasi().Email["KUNCI"]
email_tujuan = "kripto.jpao@gmail.com"

ui = UI()
fungsi = Fungsi()

ui.garis_horizontal(komponen="=")
print(f"{ui.judul()} v{__version__}")
ui.garis_horizontal(komponen="=")

# Jika INTERVAL_EVALUASI lebih kecil dari INTERVAL_CHART terkecil maka
# MODE_HARGA_PENUTUPAN akan diset menjadi False dam sebaliknya adalah True
# Sebenarnya INTERVAL_EVALUASI tidak akan berguna jika strategi menggunakan
# kumpulan INTERVAL_CHART yang nilai terkecilnya lebih kecil dari INTERVAL_EVALUASI
split_int_eva = INTERVAL_EVALUASI[0].split(" ")
int_eva_konv = float(split_int_eva[0]) * fungsi.konverter_detik(split_int_eva[1])
list_int_chart = []
for waktu in INTERVAL_CHART:
    split_waktu = waktu.split(" ")
    int_chart = float(split_waktu[0]) * fungsi.konverter_detik(split_waktu[1])
    list_int_chart.append(int_chart)
# Mode ini menentukan penggunaan harga penutupan terakhir atau harga terakhir
MODE_HARGA_PENUTUPAN = False if int_eva_konv <= min(list_int_chart) else True
INDEX_INTERVAL_CHART_TERKECIL = list_int_chart.index(min(list_int_chart))

# Initiate objek Strategi di awal
strategi = Strategi(
    ASET_DATA,
    ASET,
    EXCHANGE,
    DATA_EXCHANGE,
    leverage=LEVERAGE,
    inter_eval=INTERVAL_EVALUASI,
    inter_chart=INTERVAL_CHART,
    mode_harga_penutupan=MODE_HARGA_PENUTUPAN,
    backtest=MODE_BACKTEST,
    jumlah_periode_backtest=PERIODE_BACKTEST,
    jumlah_trade_usdt=JUMLAH_TRADE_USDT
)

while True:
    try:
        # DATA AKAN DITAMPILKAN MENGGUNAKAN HANDLER UI
        # data akun spot
        (
            maker_commission,
            taker_commission,
            buyer_commission,
            seller_commission,
            df_saldo_aset_spot,
        ) = info_akun.akun_spot()

        # data akun futures
        (
            fee_tier,
            total_saldo,
            saldo_tersedia,
            saldo_terpakai,
            laba_rugi_terbuka,
            saldo_plus_profit,
            df_saldo_aset_futures,
        ) = info_akun.akun_futures()

        # Tampilkan data spot jika terdapat saldo atau posisi pada spot
        if len(df_saldo_aset_spot) > 0:
            # urut ulang data akun spot dalam list
            data_akun_spot = [
                maker_commission,
                taker_commission,
                buyer_commission,
                seller_commission,
            ]
            # assign label data akun spot
            label_data_akun_spot = [
                "Komisi Maker",
                "Komisi Taker",
                "Komisi Pembeli",
                "Komisi Penjual",
            ]

            # print subjudul spot
            ui.subjudul("data akun spot:")

            # print iterasi list data_akun_spot
            for nomor_data in range(len(data_akun_spot)):
                ui.label_nilai(
                    label_data_akun_spot[nomor_data], data_akun_spot[nomor_data]
                )

            # print dataframe aset spot
            ui.spasi()
            ui.subjudul("posisi aset spot:")
            ui.print_dataframe_murni(df_saldo_aset_spot)
            ui.garis_horizontal()

        # Tampilkan data futures jika terdapat saldo atau posisi pada futures
        # urut ulang data akun futures dalam list
        data_akun_futures = [
            fee_tier,
            round(saldo_tersedia, 2),
            round(saldo_terpakai, 2),
            round(total_saldo, 2),
            round(laba_rugi_terbuka, 2),
            round(saldo_plus_profit, 2),
        ]
        # assign label data akun futures
        label_data_akun_futures = [
            "Fee Tier",
            "Saldo Tersedia",
            "Saldo Terpakai",
            "Saldo Total",
            "Laba/Rugi Posisi",
            "Saldo + Laba/Rugi",
        ]
        # print subjudul futures
        ui.subjudul("data akun futures:")

        # print iterasi list data_akun_futures
        for nomor_data in range(len(data_akun_futures)):
            ui.label_nilai(
                label_data_akun_futures[nomor_data],
                data_akun_futures[nomor_data],
                nomor_data == 4,
            )

        if len(df_saldo_aset_futures) > 0:
            # print dataframe aset futures
            ui.spasi()
            ui.subjudul("posisi aset futures:")
            ui.print_dataframe_murni(df_saldo_aset_futures)

        ui.garis_horizontal()

        # Kalibrasi waktu sebelum eksekusi jika loop awal program
        # INTERVAL diubah menjadi INTERVAL_EVALUASI untuk memungkinkan
        # evaluasi tindakan yang berbeda dengan data yang dikembalikan oleh
        # INTERVAL_CHART
        if INISIATOR_WAKTU:
            hitung_mundur = (
                fungsi.kalibrasi_waktu(INTERVAL_CHART[INDEX_INTERVAL_CHART_TERKECIL])
                if MODE_HARGA_PENUTUPAN
                else fungsi.kalibrasi_waktu(INTERVAL_EVALUASI[0])
            )
            if hitung_mundur is not None and hitung_mundur > 2:
                ui.keluar()
                ui.hitung_mundur(hitung_mundur, True)

        # Hentikan inisiator_waktu
        INISIATOR_WAKTU = False

        # update parameter dan data strategi
        strategi.update_portfolio()

        # Eksekusi strategi
        # strategi.jpao_niten_ichi_ryu_28_16_8(interval=INTERVAL_CHART, k_cepat=24, k_lambat=16, d_lambat=8)  # type: ignore
        # strategi.jpao_ride_the_ema(interval=INTERVAL_CHART, periode_ema=37, smoothing=2, dual_ema=True, periode_ema_cepat=5)  # type: ignore
        # strategi.jpao_smooth_ma_velocity(interval=INTERVAL_CHART, periode_ma=3, smoothing=2)  # type: ignore
        # strategi.jpao_ride_the_wave(interval=INTERVAL_CHART, periode_ma_cepat=4, periode_ma_lambat=49)  # type: ignore
        # strategi.jpao_double_smoothed_heiken_ashi(smoothed_ha=True, tipe_ma_smoothing=["ema"], smoothing_1=1, smoothing_2=1)  # type: ignore
        strategi.jpao_naive_strat(threshold_pct=0.0025)
        # strategi.jpao_closing_in_ma(periode_ma=1, smoothing_period=5)

        # Reset jumlah error beruntun
        JUMLAH_ERROR = 0

        # Kalibrasi waktu untuk eksekusi selanjutnya
        hitung_mundur = (
            fungsi.kalibrasi_waktu(INTERVAL_CHART[INDEX_INTERVAL_CHART_TERKECIL])
            if MODE_HARGA_PENUTUPAN
            else fungsi.kalibrasi_waktu(INTERVAL_EVALUASI[0])
        )
        if hitung_mundur is not None and hitung_mundur > 2:
            ui.garis_horizontal(komponen="=")
            ui.keluar()
            ui.hitung_mundur(hitung_mundur)
    # Cegah program crash dan retry dalam 1 detik
    except Exception as e:
        print(e)
        print(f"Terjadi kesalahan, mengulang proses....")
        JUMLAH_ERROR += 1
        if JUMLAH_ERROR % 10 == 0:
            print("Terjadi 10 kesalahan berturut - turut...")
            # fungsi.kirim_bot_telegram(
            #     judul=f"KESALAHAN PADA {ui.judul()}",
            #     isi_pesan=f"Terjadi kesalahan beruntun yang menyebabkan script tidak dapat melanjutkan pekerjaannya, mohon cek script pada master-server:\n{e}",
            # )
        time.sleep(1)
