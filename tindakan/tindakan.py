"""
Script untuk kelas Order
Script ini akan melakukan eksekusi order buka_long, buka_short, tutup_long atau tutup_short
"""

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
    """
    Kelas Order digunakan untuk mengeksekusi transaksi beli dan jual pada exchange

    Atribut
    -------
    inisiasi_konektor (Inisiasi):
        kelas Inisiasi yang akan digunakan untuk menginisiasi koneksi dengan exchange Client
    exchange (Client):
        objek Client yang akan digunakan dalam melakukan transaksi ke exchange
    info_akun (InfoAkun):
        kelas InfoAkun yang akan digunakan dalam melakukan penarikan data mengenai akun pengguna di exchange
    aset (str):
        str aset yang digunakan dalam melakukan transaksi
    pengguna_email (str):
        str pengguna email yang digunakan untuk mengirimkan notifikasi email
    kunci_email (str):
        str kunci email yang digunakan untuk autentikasi dengan smtp server
    email_tujuan (str):
        str email tujuan yang akan menerima notifikasi email
    fungsi (Fungsi):
        kelas Fungsi yang akan digunakan dalam melakukan fungsi-fungsi dasar seperti mengirimkan email

    Metode
    ------
    buka_long(kuantitas: float, leverage: int, tipe_order: str) -> None:
        Metode ini akan melakukan eksekusi order untuk membuka posisi long dengan kuantitas, leverage dan tipe order ke API exchange
    buka_short(kuantitas: float, leverage: int, tipe_order: str) -> None:
        Metode ini akan melakukan eksekusi order untuk membuka posisi short dengan kuantitas, leverage dan tipe order ke API exchange
    tutup_long(kuantitas: float, leverage: int, tipe_order: str) -> None:
        Metode ini akan melakukan eksekusi order untuk menutup posisi long dengan kuantitas, leverage dan tipe order ke API exchange
    tutup_short(kuantitas: float, leverage: int, tipe_order: str) -> None:
        Metode ini akan melakukan eksekusi order untuk menutup posisi short dengan kuantitas, leverage dan tipe order ke API exchange
    """

    def __init__(self, aset: str) -> None:
        """
        Metode inisiasi dari kelas Order

        Argumen
        -------
        aset (str):
            str aset yang digunakan dalam melakukan transaksi

        Return
        ------
        (None):
            Metode ini tidak mengembalikan nilai apapun selain melakukan inisiasi variabel
        """
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
    ) -> int | None:
        """
        Metode ini akan membuka posisi long di akun exchange

        Argumen
        -------
        kuantitas (float):
            float kuantitas aset yang akan dibeli (setelah dikalikan dengan leverage)
        leverage (int):
            int leverage yang digunakan dalam membuka posisi
        tipe_order (str):
            str tipe order yang dapat diterima oleh API Binance (LIMIT, MARKET, STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT, LIMIT_MAKER)

        Return
        ------
        (None):
            Metode ini tidak mengembalikan nilai apapun selain melakukan eksekusi order untuk membuka posisi long di akun dan mengirimkan notifikasi email
        """
        try:
            self.exchange.futures_change_leverage(symbol=self.aset, leverage=leverage)
            self.exchange.futures_create_order(
                symbol=self.aset,
                type=tipe_order,
                side="BUY",
                positionSide="LONG",
                quantity=round(kuantitas),
            )

            *_, df_saldo_futures = self.info_akun.akun_futures()
            df_long = df_saldo_futures[df_saldo_futures["positionSide"] == "LONG"]
            harga_masuk_long = df_long.iloc[0]["entryPrice"]
            saldo_long = df_long.iloc[0]["isolatedWallet"]

            kalimat = f"\nPosisi LONG senilai {saldo_long} USDT / {round(kuantitas)} {self.aset} berhasil dibuka untuk {self.aset} pada harga {harga_masuk_long}"
            try:
                self.fungsi.kirim_bot_telegram(
                    judul="STATUS TRIGGER BUKA LONG", isi_pesan=kalimat
                )
            except Exception as e:
                print(e)
                print("\nTerjadi kesalahan dalam mengirimkan notifikasi telegram")
            print(kalimat)
            return round(kuantitas)
        except Exception as e:
            kalimat = f"Posisi LONG tidak berhasil dibuka untuk {self.aset}:\n{e}"
            self.fungsi.kirim_bot_telegram(judul="LONG GAGAL DIBUKA", isi_pesan=kalimat)

    def buka_short(
        self, kuantitas: float, leverage: int = 10, tipe_order: str = "MARKET"
    ) -> int | None:
        """
        Metode ini akan membuka posisi short di akun exchange

        Argumen
        -------
        kuantitas (float):
            float kuantitas aset yang akan dijual (setelah dikalikan dengan leverage)
        leverage (int):
            int leverage yang digunakan dalam membuka posisi
        tipe_order (str):
            str tipe order yang dapat diterima oleh API Binance (LIMIT, MARKET, STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT, LIMIT_MAKER)

        Return
        ------
        (None):
            Metode ini tidak mengembalikan nilai apapun selain melakukan eksekusi order untuk membuka posisi short di akun dan mengirimkan notifikasi email
        """
        try:
            self.exchange.futures_change_leverage(symbol=self.aset, leverage=leverage)
            self.exchange.futures_create_order(
                symbol=self.aset,
                type=tipe_order,
                side="SELL",
                positionSide="SHORT",
                quantity=round(kuantitas),
            )
            *_, df_saldo_futures = self.info_akun.akun_futures()
            df_short = df_saldo_futures[df_saldo_futures["positionSide"] == "SHORT"]
            harga_masuk_short = df_short.iloc[0]["entryPrice"]
            saldo_short = df_short.iloc[0]["isolatedWallet"]

            kalimat = f"\nPosisi SHORT senilai {saldo_short} USDT / {round(kuantitas)} {self.aset} berhasil dibuka untuk {self.aset} pada harga {harga_masuk_short}"
            try:
                self.fungsi.kirim_bot_telegram(
                    judul="STATUS TRIGGER BUKA SHORT", isi_pesan=kalimat
                )
            except Exception as e:
                print(e)
                print("\nTerjadi kesalahan dalam mengirimkan notifikasi telegram")
            print(kalimat)
            return round(kuantitas)
        except Exception as e:
            kalimat = f"Posisi SHORT tidak berhasil dibuka untuk {self.aset}:\n{e}"
            self.fungsi.kirim_bot_telegram(
                judul="SHORT GAGAL DIBUKA", isi_pesan=kalimat
            )

    def tutup_long(
        self, kuantitas: float, leverage: int = 10, tipe_order: str = "MARKET"
    ) -> None:
        """
        Metode ini akan menutup posisi long di akun exchange

        Argumen
        -------
        kuantitas (float):
            float kuantitas aset yang akan dijual (setelah dikalikan dengan leverage)
        leverage (int):
            int leverage yang digunakan dalam menutu posisi
        tipe_order (str):
            str tipe order yang dapat diterima oleh API Binance (LIMIT, MARKET, STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT, LIMIT_MAKER)

        Return
        ------
        (None):
            Metode ini tidak mengembalikan nilai apapun selain melakukan eksekusi order untuk menutup posisi long di akun dan mengirimkan notifikasi email
        """
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
                quantity=round(kuantitas),
            )

            kalimat = f"\nPosisi LONG senilai {saldo_long} USDT / {round(kuantitas)} {self.aset} berhasil ditutup untuk {self.aset}"
            try:
                self.fungsi.kirim_bot_telegram(
                    judul="STATUS TRIGGER TUTUP LONG", isi_pesan=kalimat
                )
            except Exception as e:
                print(e)
                print("\nTerjadi kesalahan dalam mengirimkan notifikasi telegram")
            print(kalimat)
            return round(kuantitas)
        except Exception as e:
            kalimat = f"Posisi LONG tidak berhasil ditutup untuk {self.aset}:\n{e}"
            self.fungsi.kirim_bot_telegram(
                judul="LONG GAGAL DITUTUP", isi_pesan=kalimat
            )

    def tutup_short(
        self, kuantitas: float, leverage: int = 10, tipe_order: str = "MARKET"
    ) -> None:
        """
        Metode ini akan menutup posisi short di akun exchange

        Argumen
        -------
        kuantitas (float):
            float kuantitas aset yang akan dibeli (setelah dikalikan dengan leverage)
        leverage (int):
            int leverage yang digunakan dalam menutup posisi
        tipe_order (str):
            str tipe order yang dapat diterima oleh API Binance (LIMIT, MARKET, STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT, LIMIT_MAKER)

        Return
        ------
        (None):
            Metode ini tidak mengembalikan nilai apapun selain melakukan eksekusi order untuk menutup posisi short di akun dan mengirimkan notifikasi email
        """
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
                quantity=round(kuantitas),
            )

            kalimat = f"\nPosisi SHORT senilai {saldo_short} USDT / {round(kuantitas)} {self.aset} berhasil ditutup untuk {self.aset}"
            try:
                self.fungsi.kirim_bot_telegram(
                    judul="STATUS TRIGGER TUTUP SHORT", isi_pesan=kalimat
                )
            except Exception as e:
                print(e)
                print("\nTerjadi kesalahan dalam mengirimkan notifikasi telegram")
            print(kalimat)
            return round(kuantitas)
        except Exception as e:
            kalimat = f"Posisi SHORT tidak berhasil ditutup untuk {self.aset}:\n{e}"
            self.fungsi.kirim_bot_telegram(
                judul="SHORT GAGAL DITUTUP", isi_pesan=kalimat
            )
