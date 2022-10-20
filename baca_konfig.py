"""
Script untuk kelas Konfigurasi
Script ini akan membaca file konfigurasi json dan melakukan inisiasi data dan exchange saat diperlukan
"""

from binance import Client
from tvDatafeed import TvDatafeed

from api_rahasia.konfigurasi import Konfigurasi

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class Inisiasi:
    def __init__(self) -> None:
        self.konfigurasi = Konfigurasi()

    def data(self) -> TvDatafeed:
        # username dan password di file konfigurasi
        USERNAME = self.konfigurasi.DataFeed["USERNAME"]
        PASSWORD = self.konfigurasi.DataFeed["PASSWORD"]
        return TvDatafeed(USERNAME, PASSWORD)

    def exchange(self) -> Client:
        # kunci API dan rahasia API di file konfigurasi
        KUNCI_API = self.konfigurasi.Exchange["BINANCE"]["KUNCI_API"]
        RAHASIA_API = self.konfigurasi.Exchange["BINANCE"]["RAHASIA_API"]
        return Client(KUNCI_API, RAHASIA_API)
