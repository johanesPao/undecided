"""
Script untuk kelas Order
Script ini akan melakukan eksekusi order buka_long, buka_short, tutup_long atau tutup_short
"""

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"


class Order:
    def buka_long(self) -> str:
        return "BUKA_LONG"

    def buka_short(self) -> str:
        return "BUKA_SHORT"

    def tutup_long(self) -> str:
        return "TUTUP_LONG"

    def tutup_short(self) -> str:
        return "TUTUP_SHORT"
