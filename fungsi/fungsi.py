"""
Script untuk kelas Fungsi
Script ini akan melakukan perintah fungsi dasar di luar perdagangan spesifik
"""
import datetime
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import telegram_send
from pandas import DateOffset
from tvDatafeed import Interval

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class Fungsi:
    """
    Kelas Fungsi merupakan kelas yang berisi fungsi - fungsi dasar bagi program di luar fungsi perdagangan spesifik.

    Atribut
    -------
    (None)

    Metode
    ------
    konverter_detik(interval: str, hari_dlm_bulan: int) -> int:
        Metode yang dipergunakan untuk mengkonversi string menit, jam, hari, minggu dan bulan dalam nilai jumlah detik
    kalibrasi_waktu(interval: str) -> float | None:
        Metode yang dipergunakan untuk melakukan kalibrasi waktu dari program dengan timeframe interval waktu penutupan harga perdagangan
        kirim_email(dari: str, ke: str, judul: str, isi_pesan: str, kunci: str) -> None: Metode yang dipergunakan untuk mengirimkan email kepada pengguna jika terjadi kesalahan pada program secara beruntun atau saat terjadi transaksi
        konverter_offset(interval: str, offset_kosong: bool) -> DateOffset: Metode yang dipergunakan untuk melakukan offset datetime pada tabel pd.DataFrame terkait dengan strategi
        konverter_waktu(interval: str) -> Interval: Metode yang dipergunakan untuk mengkonversi string menjadi objek Interval yang dipergunakan oleh modul tvDatafeed
    """

    def __init__(self):
        """
        Metode inisiasi kelas Fungsi

        Argumen
        -------
        (None)

        Return
        ------
        (None)
        """
        pass

    def konverter_detik(self, interval: str, hari_dlm_bulan: int = 30) -> int:
        """
        Metode untuk mengkonversi string 'menit', 'jam', 'hari', 'minggu' dan 'bulan' dalam jumlah detik

        Argumen
        -------
        interval (str):
            string yang akan dikonversi menjadi detik int
        hari_dlm_bulan (int):
            jumlah hari dalam bulan (jika interval='bulan') untuk dikonversi menjadi detik

        Return
        ------
        (int):
            jumlah detik dari interval yang diberikan
        """
        # Memastikan nilai str dari interval adalah menit, jam, hari, minggu atau bulan
        assert interval == "menit" or "jam" or "hari" or "minggu" or "bulan"

        match interval:
            case "menit":
                # (60) detik dalam 1 menit
                faktor_detik = 60
            case "jam":
                # (60 pangkat 2) detik dalam 1 jam
                faktor_detik = 60**2
            case "hari":
                # (60 pangkat 2 dikalikan dengan 24) detik dalam 1 hari
                faktor_detik = 60**2 * 24
            case "minggu":
                # (60 pangkat 2 dikalikan dengan 24 dan 7) detik dalam 1 minggu
                faktor_detik = 60**2 * 24 * 7
            case "bulan":
                # (60 pangkat 2 dikalikan dengan 24, 7 dan jumlah hari dalam bulan) detik dalam bulan berjalan
                faktor_detik = 60 ^ 2 * 24 * hari_dlm_bulan
            case _:
                # Kasus default
                faktor_detik = 1

        # Mengembalikan pengali detik
        return faktor_detik

    def kalibrasi_waktu(self, interval: str) -> float | None:
        """
        Metode ini akan melakukan kalibrasi waktu saat program berjalan supaya program dieksekusi pada timeframe yang sama dengan interval waktu yang diberikan untuk melakukan evaluasi strategi di awal timeframe yang baru.
        Metode ini mengembalikan nilai float yang merupakan hitung mundur (dalam detik) menuju penutupan harga pada interval waktu yang digunakan atau mengembalikan None dan melakukan print kesalahan jika interval waktu yang diberikan tidak sesuai atau terjadi kesalahan internal dalam metode ini.

        Argumen
        -------
        interval (str):
            Interval waktu pertama (list[0]) yang digunakan dalam evaluasi strategi.

        Return
        ------
        hitung_mundur (float):
            hitung mundur sampai evaluasi strategi dijalankan oleh program dalam detik.
        (None):
            Print kesalahan format argumen atau kesalahan internal metode ini.
        """
        # Waktu saat metode dijalankan
        waktu_saat_ini = datetime.datetime.now()
        # Waktu saat metode dijalankan dalam format unix (jumlah detik sejak 1 Januari 1970)
        waktu_saat_ini_unix = time.mktime(waktu_saat_ini.timetuple())
        # Tahun saat metode dijalankan
        tahun = datetime.datetime.now().year
        # Bulan saat metode dijalankan
        bulan = datetime.datetime.now().month

        match bulan:
            # Jika bulan kurang dari 8
            case bulan if bulan < 8:
                # Jika bulan genap, maka 30 hari
                if bulan % 2 == 0:
                    hari_dlm_bulan = 30
                    # Jika bulan genap dan merupakan bulan 2 dan tahun adalah kabisat, maka 29 hari
                    if bulan == 2 and tahun % 4 == 0:
                        hari_dlm_bulan = 29
                    else:
                        # Jika bulan 2 bukan pada tahun kabisat, maka 28 hari
                        hari_dlm_bulan = 28
                else:
                    # Jika bulan ganjil, maka 31 hari
                    hari_dlm_bulan = 31
            # Jika bulan lebih besar atau sama dengan 8
            case bulan if bulan >= 8:
                # Jika bulan genap maka 31 hari
                if bulan % 2 == 0:
                    hari_dlm_bulan = 31
                else:
                    # Jika bulan ganjil maka 30 hari
                    hari_dlm_bulan = 30
            # Kasus default
            case _:
                hari_dlm_bulan = 30
        # Konversi string menjadi detik
        try:
            # Split str berdasar spasi menjadi 2 komponen
            list_interval = interval.split(" ")
            # Konversi str menit, jam, hari, minggu dan bulan menjadi pengali dalam detik
            faktor_detik = self.konverter_detik(
                list_interval[1],
                hari_dlm_bulan=hari_dlm_bulan if list_interval[1] == "bulan" else 0,
            )
            # Jumlah detik interval
            interval_detik = int(list_interval[0]) * faktor_detik
            # Jumlah detik hitung mundur sampai eksekusi berikutnya adalah
            # jumlah detik dalam interval dikurangi dengan waktu_saat_ini
            # modulus jumlah detik dalam interval
            hitung_mundur = interval_detik - (waktu_saat_ini_unix % interval_detik)
            # Mengembalikan nilai detik hitung mundur sampai eksekusi berikutnya
            return hitung_mundur
        except Exception as e:
            # Print kesalahan metode kalibrasi waktu
            print(f"Terjadi kesalahan dalam fungsi kalibrasi_waktu:\n{e}")

    def kirim_email(
        self, dari: str, ke: str, judul: str, isi_pesan: str, kunci: str
    ) -> None:
        """
        Metode untuk mengirimkan email ke pengguna menggunakan server smtp gmail

        Argumen
        -------
        dari (str):
            alamat email yang menjadi pengirim email
        ke (str):
            alamat email yang menjadi tujuan email
        judul (str):
            judul dari email
        isi_pesan (str):
            isi pesan dari email
        kunci (str):
            kunci autentikasi email google (App Password) yang bisa digenerate dari akun pengirim email, lebih lanjut merujuk kepada https://support.google.com/mail/answer/185833?hl=en

        Return
        ------
        (None):
            email terkirim atau print kesalahan di console
        """
        pesan = MIMEMultipart("alternative")
        pesan["Subject"] = judul
        pesan["From"] = dari
        pesan["To"] = ke

        # Konversi isi pesan dalam HTML
        isi_pesan_ke_html = MIMEText(isi_pesan, "html")

        pesan.attach(isi_pesan_ke_html)
        try:
            email = smtplib.SMTP("smtp.gmail.com", 587)
            email.ehlo()
            email.starttls()
            email.login(dari, kunci)
            email.sendmail(dari, ke, pesan.as_string())
            email.quit()
        except Exception as e:
            print(f"Terjadi kesalahan dalam pengiriman email:\n{e}")

    def kirim_bot_telegram(self, judul: str, isi_pesan: str) -> None:
        telegram_send.send(messages=[f"{judul}\n\n{isi_pesan}"])

    def konverter_offset(
        self, interval: str, offset_kosong: bool = False
    ) -> DateOffset:
        """
        Metode ini akan dipergunakan untuk meng-offset data datetime pada timeframe besar di pd.DataFrame untuk tampil berdampingan dengan datetime timeframe kecil dalam 1 baris sebagai bahan evaluasi strategi.

        Argumen
        -------
        interval (str):
            str interval waktu timeframe
        offset_kosong (bool):
            offset_kosong dipergunakan (True) jika interval waktu pada timeframe kecil dan besar adalah sama sehingga sebenarnya tidak perlu dilakukan offset pada timeframe besar. Jika interval waktu pada timeframe kecil dan besar tidak sama maka perlu dilakukan offset pada tabel datetime timeframe besar, sehingga baris timeframe besar dapat berdampingan dengan baris timeframe kecil pada interval waktu yang benar

        Return
        ------
        (DateOffset):
            objek DateOffset pada pd.DataFrame untuk meng-offset timeframe besar dengan timeframe kecil
        """
        if offset_kosong:
            match interval:
                case "menit":
                    offset_waktu = DateOffset(minutes=0)
                case "jam":
                    offset_waktu = DateOffset(hours=0)
                case "hari":
                    offset_waktu = DateOffset(days=0)
                case "minggu":
                    offset_waktu = DateOffset(weeks=0)
                case "bulan":
                    offset_waktu = DateOffset(months=0)
                case _:
                    offset_waktu = DateOffset(minutes=0)
        else:
            match interval:
                case "3 menit":
                    offset_waktu = DateOffset(minutes=3)
                case "5 menit":
                    offset_waktu = DateOffset(minutes=5)
                case "15 menit":
                    offset_waktu = DateOffset(minutes=15)
                case "45 menit":
                    offset_waktu = DateOffset(minutes=45)
                case "1 jam":
                    offset_waktu = DateOffset(hours=1)
                case "2 jam":
                    offset_waktu = DateOffset(hours=2)
                case "3 jam":
                    offset_waktu = DateOffset(hours=3)
                case "4 jam":
                    offset_waktu = DateOffset(hours=4)
                case "1 hari":
                    offset_waktu = DateOffset(days=1)
                case "1 minggu":
                    offset_waktu = DateOffset(weeks=1)
                case "1 bulan":
                    offset_waktu = DateOffset(months=1)
                case _:
                    offset_waktu = DateOffset(minutes=1)

        # Mengembalikan objek DateOffset
        return offset_waktu

    def konverter_waktu(self, interval: str) -> Interval:
        """
        Metode untuk mengkonversi string interval waktu menjadi objek Interval yang diterima oleh modul tvDatafeed

        Argumen
        -------
        interval (str):
            str interval waktu yang akan dikonversi menjadi objek Interval tvDatafeed

        Return
        ------
        (Interval):
            Objek Interval pada modul tvDatafeed
        """
        # Memastikan interval adalah nilai str yang ditetapkan
        assert (
            interval == "1 menit"
            or "3 menit"
            or "5 menit"
            or "15 menit"
            or "30 menit"
            or "45 menit"
            or "1 jam"
            or "2 jam"
            or "3 jam"
            or "4 jam"
            or " 1 hari"
            or "1 minggu"
            or "1 bulan"
        )

        # Konversi str menjadi objek Interval tvDatafeed
        match interval:
            case "1 menit":
                konversi_interval = Interval.in_1_minute
            case "3 menit":
                konversi_interval = Interval.in_3_minute
            case "5 menit":
                konversi_interval = Interval.in_5_minute
            case "15 menit":
                konversi_interval = Interval.in_15_minute
            case "30 menit":
                konversi_interval = Interval.in_30_minute
            case "45 menit":
                konversi_interval = Interval.in_45_minute
            case "1 jam":
                konversi_interval = Interval.in_1_hour
            case "2 jam":
                konversi_interval = Interval.in_2_hour
            case "3 jam":
                konversi_interval = Interval.in_3_hour
            case "4 jam":
                konversi_interval = Interval.in_4_hour
            case "1 hari":
                konversi_interval = Interval.in_daily
            case "1 minggu":
                konversi_interval = Interval.in_weekly
            case "1 bulan":
                konversi_interval = Interval.in_monthly
            case _:
                konversi_interval = Interval.in_1_minute

        # Mengembalikan objek Interval tvDatafeed
        return konversi_interval
