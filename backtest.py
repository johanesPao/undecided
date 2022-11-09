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
ASET_DATA = "MATICUSDTPERP"
ASET = "MATICUSDT"
EXCHANGE = "BINANCE"

k_cepat = 24
k_lambat = 20
d_lambat = 8

# Inisiasi kelas strategi
strategi_backtest = Strategi(
    ASET_DATA,
    ASET,
    EXCHANGE,
    backtest=True,
    jumlah_periode_backtest=720 + k_cepat + k_lambat + d_lambat,
    saldo_backtest=20,
    leverage_backtest=15,
)

# Eksekusi strategi dalam fungsi backtest kelas Strategi
hasil_strategi = strategi_backtest.jpao_niten_ichi_ryu_28_16_8(
    interval=["1 menit", "1 menit"],
    k_cepat=k_cepat,
    k_lambat=k_lambat,
    d_lambat=d_lambat,
)

# hasil_strategi = strategi_backtest.jpao_ride_the_wave(
#     interval=["1 menit"], periode_ma=100, k_cepat=15, k_lambat=8, d_lambat=3
# )
