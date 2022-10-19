"""
Script untuk kelas UI
Script untuk menampilkan informasi dasar akun dan garis_horizontal pada terminal
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
    def __init__(self, akun) -> None:
        self.akun = akun
        self.ukuran_terminal = os.get_terminal_size().columns

    def garis_horizontal(self, komponen: str = "-") -> None:
        self.komponen = komponen
        print(self.komponen * self.ukuran_terminal)

    def data_akun_futures(self) -> None:
        data_futures = self.akun.futures_account()

        bisa_trade = data_futures["canTrade"]
        bisa_deposit = data_futures["canDeposit"]
        bisa_tarik = data_futures["canWithdraw"]
        total_saldo = float(data_futures["totalWalletBalance"])
        saldo_tersedia = float(data_futures["availableBalance"])
        saldo_terpakai = total_saldo - saldo_tersedia
        laba_rugi_terbuka = float(data_futures["totalUnrealizedProfit"])
        saldo_plus_profit = float(data_futures["totalMarginBalance"])
        data_posisi_df = pd.DataFrame(data_futures["positions"])
        data_posisi_df = data_posisi_df.loc[
            pd.to_numeric(data_posisi_df["initialMargin"]) > 0
        ]
        data_posisi_df = data_posisi_df[
            [
                "symbol",
                "positionSide",
                "isolatedWallet",
                "entryPrice",
                "unrealizedProfit",
            ]
        ]

        print(f"{Fore.GREEN}MODE:{Style.RESET_ALL}")
        print(
            f"Perdagangan: {Fore.CYAN if bisa_trade else Fore.RED}{bisa_trade}{Style.RESET_ALL}"
        )
        print(
            f"Deposit Dana: {Fore.CYAN if bisa_deposit else Fore.RED}{bisa_deposit}{Style.RESET_ALL}"
        )
        print(
            f"Tarik Dana: {Fore.CYAN if bisa_tarik else Fore.RED}{bisa_tarik}{Style.RESET_ALL}"
        )
        print(f"\n{Fore.GREEN}SALDO & PROFITABILITAS:{Style.RESET_ALL}")
        print(
            f"Saldo Tersedia: {Fore.RED if saldo_tersedia < 0 else Fore.CYAN}{round(saldo_tersedia, 2)} USDT {Style.RESET_ALL}"
        )
        print(
            f"Saldo Terpakai: {Fore.RED if saldo_terpakai < 0 else Fore.CYAN}{round(saldo_terpakai, 2)} USDT {Style.RESET_ALL}"
        )
        print(
            f"Laba Rugi Terbuka: {Fore.RED if laba_rugi_terbuka < 0 else Fore.GREEN}{round(laba_rugi_terbuka, 2)} USDT {Style.RESET_ALL}"
        )
        print(
            f"Saldo & Laba/Rugi: {Fore.RED if saldo_plus_profit < 0 else Fore.CYAN}{round(saldo_plus_profit, 2)} USDT {Style.RESET_ALL}"
        )
        print(f"\n{Fore.GREEN}POSISI BERJALAN:{Style.RESET_ALL}")
        print(data_posisi_df)
        self.garis_horizontal()

    def keluar(self) -> None:
        print(f"{Fore.RED}Tekan Ctrl+C untuk menghentikan program.{Style.RESET_ALL}")
