"""
Script untuk kelas Konfigurasi
Script ini akan membaca file konfigurasi json dan melakukan inisiasi data dan exchange saat diperlukan
"""

import json

from binance import Client
from tvDatafeed import TvDatafeed

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class Konfigurasi:
    def __init__(self, file_konfig: str) -> None:
        self.file_konfig = file_konfig
        with open(self.file_konfig, "r") as file_json:
            self.data_konfigurasi = json.load(file_json)

    def inisiasi_data_konektor(self) -> TvDatafeed:
        # username dan password di file konfigurasi
        USERNAME = self.data_konfigurasi["DATAFEED"]["USERNAME"]
        PASSWORD = self.data_konfigurasi["DATAFEED"]["PASSWORD"]
        return TvDatafeed(USERNAME, PASSWORD)

    def inisiasi_exchange(self) -> Client:
        # kunci API dan rahasia API di file konfigurasi
        KUNCI_API = self.data_konfigurasi["EXCHANGE"]["BINANCE"]["KUNCI_API"]
        RAHASIA_API = self.data_konfigurasi["EXCHANGE"]["BINANCE"]["RAHASIA_API"]
        return Client(KUNCI_API, RAHASIA_API)
