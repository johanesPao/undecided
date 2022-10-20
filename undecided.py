"""
Script untuk Program Utama
Script ini berfungsi untuk menjalankan program utama dan mengintegrasikan berbagai komponen
"""

import time

from numpy import take

from akun.akun import InfoAkun
from analisa.analisa_teknikal import AnalisaTeknikal
from baca_konfig import Konfigurasi
from model.model import Model
from strategi.strategi import Strategi
from ui.ui_sederhana import UI

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"

# PATH UNTUK FILE KONFIGURASI
PATH_KONFIGURASI = "./api_rahasia/api_konfig.json"
# KONSTANTA
JENIS_PASAR = "FUTURES"
TGL_AWAL = "19 September 2022"
MODE_BACKTEST = True
# VARIABEL ASET
ASET = "MATICUSDT"

Konfigurasi = Konfigurasi(PATH_KONFIGURASI)
Exchange = Konfigurasi.inisiasi_exchange()
Data = Konfigurasi.inisiasi_data_konektor()

InfoAkun = InfoAkun(Exchange)
UI = UI()
AnalisaTeknikal = AnalisaTeknikal()

UI.garis_horizontal(komponen="=")
print(f"{UI.judul()} v{__version__}")
UI.garis_horizontal(komponen="=")

data = Model(Exchange)

strategi = Strategi()

while True:
    # DATA AKAN DITAMPILKAN MENGGUNAKAN HANDLER UI
    # data akun spot
    (
        maker_commission,
        taker_commission,
        buyer_commission,
        seller_commission,
        df_saldo_aset_spot,
    ) = InfoAkun.akun_spot()

    # data akun futures
    (
        fee_tier,
        total_saldo,
        saldo_tersedia,
        saldo_terpakai,
        laba_rugi_terbuka,
        saldo_plus_profit,
        df_saldo_aset_futures,
    ) = InfoAkun.akun_futures()

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
        UI.subjudul("data akun spot:")

        # print iterasi list data_akun_spot
        for x in range(len(data_akun_spot)):
            UI.label_nilai(label_data_akun_spot[x], data_akun_spot[x])

        # print dataframe aset spot
        UI.spasi()
        UI.subjudul("posisi aset spot:")
        UI.print_dataframe_murni(df_saldo_aset_spot)
        UI.garis_horizontal()

    # Tampilkan data futures jika terdapat saldo atau posisi pada futures
    if len(df_saldo_aset_futures) > 0:
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

        # print subjudul spot
        UI.subjudul("data akun futures:")

        # print iterasi list data_akun_futures
        for x in range(len(data_akun_futures)):
            UI.label_nilai(
                label_data_akun_futures[x],
                data_akun_futures[x],
                True if x == 4 else False,
            )

        # print dataframe aset futures
        UI.spasi()
        UI.subjudul("posisi aset futures:")
        UI.print_dataframe_murni(df_saldo_aset_futures)
        UI.garis_horizontal()

    # Mengambil data aset
    data_aset = data.ambil_data_historis(
        ASET, Exchange.KLINE_INTERVAL_4HOUR, JENIS_PASAR, TGL_AWAL
    )
    df_ta = AnalisaTeknikal.stokastik(data_aset, 15, 5, 3, MODE_BACKTEST)

    # print hasil analisa teknikal
    print(df_ta)
    print("Hibernasi selama 60 detik...")
    UI.keluar()
    UI.garis_horizontal(komponen="=")

    time.sleep(60.0)
