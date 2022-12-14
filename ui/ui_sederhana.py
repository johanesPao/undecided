"""
Script untuk kelas UI
Script untuk menampilkan informasi dasar exchange dan garis_horizontal pada terminal
"""

import math
import os
import sys
import time

import pandas as pd
from colorama import Fore, Style, init

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"

init()


class UI:
    def __init__(self) -> None:
        self.ukuran_terminal = os.get_terminal_size().columns

    def judul(self) -> str:
        return "UNDECIDED"

    def subjudul(self, label_subjudul: str) -> None:
        print(f"{Fore.GREEN}{label_subjudul.upper()}{Style.RESET_ALL}")

    def garis_horizontal(self, komponen: str = "-") -> None:
        self.komponen = komponen
        print(self.komponen * self.ukuran_terminal)

    def spasi(self) -> None:
        print("")

    def label_nilai(
        self,
        label: str = "Label",
        nilai: int | float = 0,
        penting: bool = False,
        spasi_label: int = 18,
        spasi_nilai: int = 17,
    ) -> None:
        wrapper_nilai = (
            f"{Fore.GREEN if nilai >= 0 else Fore.RED}{nilai}"
            if penting
            else f"{Fore.CYAN}{nilai}"
        )

        print(
            f"{label:{spasi_label}}:{wrapper_nilai.rjust(spasi_nilai, ' ')}{Style.RESET_ALL}"
        )

    def print_dataframe_murni(self, df: pd.DataFrame) -> None:
        print(df)

    def hitung_mundur(self, hitung_mundur: float, run_pertama: bool = False) -> None:
        for waktu in range(int(hitung_mundur), 0, -1):
            hari = int(math.floor(waktu / (60**2 * 24)))
            jam = int(math.floor((waktu - (hari * 60**2 * 24)) / 60**2))
            menit = int(
                math.floor((waktu - ((hari * 60**2 * 24) + (jam * 60**2))) / 60)
            )
            detik = int(waktu % 60)
            sys.stdout.write("\r")
            if run_pertama:
                sys.stdout.write(
                    "Program akan menunggu selama {:2d} hari {:2d} jam {:2d} menit {:2d} detik sebelum melakukan eksekusi strategi...".format(
                        hari, jam, menit, detik
                    )
                )
            else:
                sys.stdout.write(
                    "Hibernasi selama {:2d} hari {:2d} jam {:2d} menit {:2d} detik...".format(
                        hari, jam, menit, detik
                    )
                )
            sys.stdout.flush()
            time.sleep(1)
        # Tambahan detik untuk mencegah script running lebih cepat dari closing interval
        time.sleep(1)
        kalimat_selesai_hitung_mundur = "Melakukan eksekusi strategi!"
        sys.stdout.write(
            f"\r{kalimat_selesai_hitung_mundur}"
            + (" " * (self.ukuran_terminal - len(kalimat_selesai_hitung_mundur)))
            + "\n"
        )

    def keluar(self) -> None:
        print(f"{Fore.RED}Tekan Ctrl+C 2x untuk menghentikan program.{Style.RESET_ALL}")
