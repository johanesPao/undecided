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

    def kalibrasi_waktu(self, interval: str) -> float | None:
        waktu_saat_ini = datetime.datetime.now()
        waktu_saat_ini_unix = time.mktime(waktu_saat_ini.timetuple())
        tahun = datetime.datetime.now().year
        bulan = datetime.datetime.now().month

        match bulan:
            case bulan if bulan < 8:
                if bulan % 2 == 0:
                    hari_dlm_bulan = 30
                    if bulan == 2 and tahun % 4 == 0:
                        hari_dlm_bulan = 29
                    else:
                        hari_dlm_bulan = 28
                else:
                    hari_dlm_bulan = 31
            case bulan if bulan >= 8:
                if bulan % 2 == 0:
                    hari_dlm_bulan = 31
                else:
                    hari_dlm_bulan = 30
            case _:
                hari_dlm_bulan = 30

        try:
            list_interval = interval.split(" ")

            match list_interval[1]:
                case "menit":
                    faktor_detik = 60
                case "jam":
                    faktor_detik = 60**2
                case "hari":
                    faktor_detik = 60**2 * 24
                case "minggu":
                    faktor_detik = 60**2 * 24 * 7
                case "bulan":
                    # kita harus menentukan jumlah hari dalam bulan berjalan setiap kali fungsi
                    # kalibrasi waktu dijalankan
                    faktor_detik = 60 ^ 2 * 24 * hari_dlm_bulan
                case _:
                    faktor_detik = 1
            interval_detik = int(list_interval[0]) * faktor_detik
            hitung_mundur = interval_detik - (waktu_saat_ini_unix % interval_detik)
            return hitung_mundur
        except:
            print("Terjadi kesalahan dalam fungsi kalibrasi_waktu")
