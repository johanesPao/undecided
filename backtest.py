"""
Script untuk simulasi backtest strategi trading
"""

from strategi.strategi import *

__author__ = "Johanes Indra Pradana Pao"
__copyright__ = "Copyright 2022, Undecided"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer = "Johanes Indra Pradana Pao"
__email__ = "johanes.pao@gmail.com"
__status__ = "Development"

# VARIABEL DAN KONSTANTA
ASET = "MATICUSDTPERP"
EXCHANGE = "BINANCE"
SALDO = 40
LEVERAGE = 10

# Inisiasi kelas strategi
strategi_backtest = Strategi(ASET, EXCHANGE, backtest=True, jumlah_periode_backtest=338)

# Eksekusi strategi dalam fungsi backtest kelas Strategi
hasil_strategi = strategi_backtest.jpao_niten_ichi_ryu_26_18_8(
    interval=["5 menit", "5 menit"], k_cepat=10, k_lambat=5, d_lambat=2
)
