"""
Script untuk Program Utama
Script ini berfungsi untuk menjalankan program utama dan mengintegrasikan berbagai komponen
"""

import time

from akun.akun import Akun
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

# PATH UNTUK FILE KONFIG AKUN
PATH_AKUN = "./api_rahasia/api_konfig.json"

Akun = Akun()
AkunBinance = Akun.binance(PATH_AKUN)
UI = UI(AkunBinance)

UI.garis_horizontal(komponen="=")
print(f"UNDECIDED v{__version__}")
UI.garis_horizontal(komponen="=")

data = Model(AkunBinance)

strategi = Strategi()

while True:
    # ambil data
    UI.data_akun_futures()
    print("Mengambil data...")
    data_matic_df = data.ambil_data_historis(
        "MATICUSDT", AkunBinance.KLINE_INTERVAL_1MINUTE, "18 October 2022"
    )
    print(data_matic_df.tail())
    print("Hibernasi selama 60 detik...")
    UI.keluar()
    UI.garis_horizontal(komponen="=")

    time.sleep(60.0)
