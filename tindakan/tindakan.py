"""
Script untuk kelas Order
Script ini akan melakukan eksekusi order buka_long, buka_short, tutup_long atau tutup_short
"""

import math

from akun.akun import InfoAkun
from api_rahasia.konfigurasi import Konfigurasi
from baca_konfig import Inisiasi
from fungsi.fungsi import Fungsi

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"

inisiasi_konektor = Inisiasi()
exchange = inisiasi_konektor.exchange()


class Order:
    def __init__(self, aset: str) -> None:
        self.inisiasi_konektor = Inisiasi()
        self.exchange = self.inisiasi_konektor.exchange()
        self.info_akun = InfoAkun(self.exchange)
        self.aset = aset
        self.pengguna_email = Konfigurasi().Email["USERNAME"]
        self.kunci_email = Konfigurasi().Email["KUNCI"]
        self.email_tujuan = "kripto.jpao@gmail.com"
        self.fungsi = Fungsi()

    def buka_long(
        self, kuantitas: float, leverage: int = 10, tipe_order: str = "MARKET"
    ) -> None:
        try:
            self.exchange.futures_change_leverage(symbol=self.aset, leverage=leverage)
            self.exchange.futures_create_order(
                symbol=self.aset,
                type=tipe_order,
                side="BUY",
                positionSide="LONG",
                quantity=math.floor(kuantitas),
            )

            *_, df_saldo_futures = self.info_akun.akun_futures()
            df_long = df_saldo_futures[df_saldo_futures["positionSide"] == "LONG"]
            harga_masuk_long = df_long.iloc[0]["entryPrice"]
            saldo_long = df_long.iloc[0]["isolatedWallet"]

            kalimat = f"Posisi LONG senilai {saldo_long} USDT / {math.floor(kuantitas)} {self.aset} berhasil dibuka untuk {self.aset} pada harga {harga_masuk_long}"
        except Exception as e:
            print(e)
            kalimat = f"Posisi LONG tidak berhasil dibuka untuk {self.aset}:\n{e}"

        print(kalimat)

        try:
            self.fungsi.kirim_email(
                self.pengguna_email,
                self.email_tujuan,
                "STATUS TRIGGER BUKA LONG",
                kalimat,
                self.kunci_email,
            )
        except Exception as e:
            print(e)
            print("Terjadi kesalahan dalam mengirimkan notifikasi email")

    def buka_short(
        self, kuantitas: float, leverage: int = 10, tipe_order: str = "MARKET"
    ) -> None:
        try:
            self.exchange.futures_change_leverage(symbol=self.aset, leverage=leverage)
            self.exchange.futures_create_order(
                symbol=self.aset,
                type=tipe_order,
                side="SELL",
                positionSide="SHORT",
                quantity=math.floor(kuantitas),
            )
            *_, df_saldo_futures = self.info_akun.akun_futures()
            df_short = df_saldo_futures[df_saldo_futures["positionSide"] == "SHORT"]
            harga_masuk_short = df_short.iloc[0]["entryPrice"]
            saldo_short = df_short.iloc[0]["isolatedWallet"]

            kalimat = f"Posisi SHORT senilai {saldo_short} USDT / {math.floor(kuantitas)} {self.aset} berhasil dibuka untuk {self.aset} pada harga {harga_masuk_short}"
        except Exception as e:
            print(e)
            kalimat = f"Posisi SHORT tidak berhasil dibuka untuk {self.aset}:\n{e}"

        print(kalimat)

        try:
            self.fungsi.kirim_email(
                self.pengguna_email,
                self.email_tujuan,
                "STATUS TRIGGER BUKA SHORT",
                kalimat,
                self.kunci_email,
            )
        except Exception as e:
            print(e)
            print("Terjadi kesalahan dalam mengirimkan notifikasi email")

    def tutup_long(
        self, kuantitas: float, leverage: int = 10, tipe_order: str = "MARKET"
    ) -> None:
        try:
            *_, df_saldo_futures = self.info_akun.akun_futures()
            df_long = df_saldo_futures[df_saldo_futures["positionSide"] == "LONG"]
            saldo_long = df_long.iloc[0]["isolatedWallet"]

            self.exchange.futures_change_leverage(symbol=self.aset, leverage=leverage)
            self.exchange.futures_create_order(
                symbol=self.aset,
                type=tipe_order,
                side="SELL",
                positionSide="LONG",
                quantity=math.ceil(kuantitas),
            )

            kalimat = f"Posisi LONG senilai {saldo_long} USDT / {math.floor(kuantitas)} {self.aset} berhasil ditutup untuk {self.aset}"
        except Exception as e:
            print(e)
            kalimat = f"Posisi LONG tidak berhasil ditutup untuk {self.aset}:\n{e}"

        print(kalimat)

        try:
            self.fungsi.kirim_email(
                self.pengguna_email,
                self.email_tujuan,
                "STATUS TRIGGER TUTUP LONG",
                kalimat,
                self.kunci_email,
            )
        except Exception as e:
            print(e)
            print("Terjadi kesalahan dalam mengirimkan notifikasi email")

    def tutup_short(
        self, kuantitas: float, leverage: int = 10, tipe_order: str = "MARKET"
    ) -> None:
        try:
            *_, df_saldo_futures = self.info_akun.akun_futures()
            df_short = df_saldo_futures[df_saldo_futures["positionSide"] == "SHORT"]
            saldo_short = df_short.iloc[0]["isolatedWallet"]

            self.exchange.futures_change_leverage(symbol=self.aset, leverage=leverage)
            self.exchange.futures_create_order(
                symbol=self.aset,
                type=tipe_order,
                side="BUY",
                positionSide="SHORT",
                quantity=math.ceil(kuantitas),
            )

            kalimat = f"Posisi SHORT senilai {saldo_short} USDT / {math.floor(kuantitas)} {self.aset} berhasil ditutup untuk {self.aset}"
        except Exception as e:
            print(e)
            kalimat = f"Posisi SHORT tidak berhasil ditutup untuk {self.aset}:\n{e}"

        print(kalimat)

        try:
            self.fungsi.kirim_email(
                self.pengguna_email,
                self.email_tujuan,
                "STATUS TRIGGER TUTUP SHORT",
                kalimat,
                self.kunci_email,
            )
        except Exception as e:
            print(e)
            print("Terjadi kesalahan dalam mengirimkan notifikasi email")
