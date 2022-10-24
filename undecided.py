"""
Script untuk Program Utama
Script ini berfungsi untuk menjalankan program utama dan mengintegrasikan berbagai komponen
"""

import time

from akun.akun import InfoAkun
from baca_konfig import Inisiasi
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
TGL_AWAL = "19 September 2022"
MODE_BACKTEST = True
# VARIABEL ASET
ASET = "MATICUSDTPERP"
EXCHANGE = "BINANCE"

inisiasi_konektor = Inisiasi()
konektor_exchange = inisiasi_konektor.exchange()

info_akun = InfoAkun(konektor_exchange)
ui = UI()

ui.garis_horizontal(komponen="=")
print(f"{ui.judul()} v{__version__}")
ui.garis_horizontal(komponen="=")

strategi = Strategi(ASET, EXCHANGE)

while True:
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
            ui.label_nilai(label_data_akun_spot[nomor_data], data_akun_spot[nomor_data])

        # print dataframe aset spot
        ui.spasi()
        ui.subjudul("posisi aset spot:")
        ui.print_dataframe_murni(df_saldo_aset_spot)
        ui.garis_horizontal()

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

        # print subjudul futures
        ui.subjudul("data akun futures:")

        # print iterasi list data_akun_futures
        for nomor_data in range(len(data_akun_futures)):
            ui.label_nilai(
                label_data_akun_futures[nomor_data],
                data_akun_futures[nomor_data],
                nomor_data == 4,
            )

        # print dataframe aset futures
        ui.spasi()
        ui.subjudul("posisi aset futures:")
        ui.print_dataframe_murni(df_saldo_aset_futures)
        ui.garis_horizontal()

    # Eksekusi strategi
    strategi.jpao_hold_trade_sto_1553()

    print("Hibernasi selama 5 detik...")
    ui.keluar()
    ui.garis_horizontal(komponen="=")

    time.sleep(5.0)
