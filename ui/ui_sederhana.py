"""
Script untuk kelas UI
Script untuk menampilkan informasi dasar exchange dan garis_horizontal pada terminal
"""

import os

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
        self, label: str = "Label", nilai: int = 0, penting: bool = False
    ) -> None:
        wrapper_nilai = (
            f"{Fore.GREEN if nilai >= 0 else Fore.RED}{nilai}"
            if penting
            else f"{Fore.CYAN}{nilai}"
        )

        print(f"{label}: {wrapper_nilai}{Style.RESET_ALL}")

    def print_dataframe_murni(self, df: pd.DataFrame) -> None:
        print(df)

    def keluar(self) -> None:
        print(f"{Fore.RED}Tekan Ctrl+C untuk menghentikan program.{Style.RESET_ALL}")
