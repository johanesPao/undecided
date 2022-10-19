"""
Script untuk kelas Akun
Script untuk menghubungkan program dengan akun pada API endpoint server
"""

import json

from binance import Client

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class Exchange:
    def __init__(self) -> None:
        pass

    # definisi untuk koneksi ke akun exchange ditulis di bagian bawah ini
    # BINANCE
    def binance(self, path_file_konfig_json: str):
        self.path_konfig = path_file_konfig_json
        with open(self.path_konfig, "r") as file_json:
            data_api = json.load(file_json)
            KUNCI_API = data_api["EXCHANGE"]["BINANCE"]["KUNCI_API"]
            RAHASIA_API = data_api["EXCHANGE"]["BINANCE"]["RAHASIA_API"]
            return Client(KUNCI_API, RAHASIA_API)
