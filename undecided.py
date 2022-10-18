import json
import time

import pandas as pd
from binance import Client, ThreadedDepthCacheManager, ThreadedWebsocketManager

from model.model import DataHistoris
from strategi.strategi import Strategi
from ui.ui_sederhana import UI

with open("./api_rahasia/api_konfig.json", "r") as file_json:
    data_api = json.load(file_json)
    KUNCI_API = data_api["EXCHANGE"]["BINANCE"]["KUNCI_API"]
    RAHASIA_API = data_api["EXCHANGE"]["BINANCE"]["RAHASIA_API"]

VERSI = "v1.0.0"
akun = Client(KUNCI_API, RAHASIA_API)
ui = UI(akun)

ui.garis_horizontal(komponen="=")
print(f"UNDECIDED {VERSI}")
print(f"API: {KUNCI_API}")
ui.garis_horizontal(komponen="=")

data = DataHistoris(akun)

strategi = Strategi()

while True:
    # ambil data
    ui.data_akun_futures()
    print("Mengambil data...")
    data_matic_df = data.ambil_data_historis(
        "MATICUSDT", akun.KLINE_INTERVAL_1MINUTE, "18 October 2022"
    )
    print(data_matic_df.tail())
    print("Hibernasi selama 60 detik...")
    ui.garis_horizontal(komponen="=")

    time.sleep(60.0)
