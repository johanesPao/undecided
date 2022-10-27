"""
Script untuk kelas Fungsi
Script ini akan melakukan perintah fungsi dasar di luar perdagangan spesifik
"""

import datetime
import time

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class Fungsi:
    def __init__(self):
        pass

    def kalibrasi_waktu(self):
        waktu_saat_ini = datetime.datetime.now()
        waktu_saat_ini_unix = time.mktime(waktu_saat_ini.timetuple())

        interval = "1 menit".split(" ")

        match interval[1]:
            case "menit":
                faktor_detik = 60
            case "jam":
                faktor_detik = 60 ^ 2
            case "hari":
                faktor_detik = 60 ^ 2 * 24
            case "minggu":
                faktor_detik = 60 ^ 2 * 24 * 7
            case "bulan":
                # kita harus menentukan jumlah hari dalam bulan berjalan setiap kali fungsi
                # kalibrasi waktu dijalankan
                faktor_detik = 60 ^ 2 * 24 * 7

        interval_detik = int(interval[0]) * faktor_detik
        hitung_mundur = faktor_detik - (waktu_saat_ini_unix % interval_detik)
        time.sleep(hitung_mundur)
