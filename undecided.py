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
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"

# KONSTANTA
MODE_BACKTEST = False
PERIODE_BACKTEST = 1000
INTERVAL = ["1 menit"]
# VARIABEL ASET
ASET_DATA = "MATICUSDTPERP"
ASET = "MATICUSDT"
EXCHANGE = "BINANCE"
LEVERAGE = 10
INISIATOR_WAKTU = True
JUMLAH_ERROR = 0
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
        if INISIATOR_WAKTU:
            hitung_mundur = fungsi.kalibrasi_waktu(INTERVAL[0])
            if hitung_mundur is not None and hitung_mundur > 2:
                ui.keluar()
                ui.hitung_mundur(hitung_mundur, True)

        # Hentikan inisiator_waktu
        INISIATOR_WAKTU = False

        # Inisiasi strategi
        strategi = Strategi(
            ASET_DATA,
            ASET,
            EXCHANGE,
            leverage=LEVERAGE,
            backtest=MODE_BACKTEST,
            jumlah_periode_backtest=PERIODE_BACKTEST,
        )

        # Eksekusi strategi
        # strategi.jpao_niten_ichi_ryu_28_16_8(interval=INTERVAL, k_cepat=120, k_lambat=160, d_lambat=20)  # type: ignore
        strategi.jpao_ride_the_wave(interval=INTERVAL, periode_ma=200, k_cepat=120, k_lambat=140, d_lambat=20)  # type: ignore

        # Reset jumlah error b2eruntun
        JUMLAH_ERROR = 0

        # Kalibrasi waktu untuk eksekusi selanjutnya
        hitung_mundur = fungsi.kalibrasi_waktu(INTERVAL[0])
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
            fungsi.kirim_bot_telegram(
                judul=f"KESALAHAN PADA {ui.judul()}",
                isi_pesan=f"Terjadi kesalahan beruntun yang menyebabkan script tidak dapat melanjutkan pekerjaannya, mohon cek script pada master-server:\n{e}",
            )
        time.sleep(1)
