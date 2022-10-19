"""
Script untuk Program Utama
Script ini berfungsi untuk menjalankan program utama dan mengintegrasikan berbagai komponen
"""

import time

from akun.akun import InfoAkun
from analisa.analisa_teknikal import AnalisaTeknikal
from exchange.exchange import Exchange
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
# KONSTANTA
JENIS_PASAR = "FUTURES"
TGL_AWAL = "19 September 2022"
MODE_BACKTEST = True
# VARIABEL ASET
ASET = "MATICUSDT"

Exchange = Exchange()
ExchangeBinance = Exchange.binance(PATH_AKUN)
InfoAkun = InfoAkun(ExchangeBinance)
UI = UI(ExchangeBinance)
AnalisaTeknikal = AnalisaTeknikal()

UI.garis_horizontal(komponen="=")
print(f"UNDECIDED v{__version__}")
UI.garis_horizontal(komponen="=")

data = Model(ExchangeBinance)

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

    # Tampilkan data futures jika terdapat saldo atau posisi pada futures
    UI.data_akun_futures()

    # Mengambil data aset
    data_aset = data.ambil_data_historis(
        ASET, ExchangeBinance.KLINE_INTERVAL_4HOUR, JENIS_PASAR, TGL_AWAL
    )
    df_ta = AnalisaTeknikal.stokastik(data_aset, 15, 5, 3, MODE_BACKTEST)

    # print hasil analisa teknikal
    print(df_ta)
    print("Hibernasi selama 60 detik...")
    UI.keluar()
    UI.garis_horizontal(komponen="=")

    time.sleep(60.0)
