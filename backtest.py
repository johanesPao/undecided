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

# NIR
# k_cepat = 120
# k_lambat = 160
# d_lambat = 20

# RTW
# periode_ma = 200
# k_cepat = 21
# k_lambat = 10
# d_lambat = 10

# RTE
periode_ema = 200
smoothing = 20

# Inisiasi kelas strategi
strategi_backtest = Strategi(
    ASET_DATA,
    ASET,
    EXCHANGE,
    backtest=True,
    jumlah_periode_backtest=288,
    saldo_backtest=29,
    leverage_backtest=20,
)

# Eksekusi strategi dalam fungsi backtest kelas Strategi
# hasil_strategi = strategi_backtest.jpao_niten_ichi_ryu_28_16_8(
#     interval=["1 menit", "1 menit"],
#     k_cepat=k_cepat,
#     k_lambat=k_lambat,
#     d_lambat=d_lambat,
# )

# hasil_strategi = strategi_backtest.jpao_ride_the_wave(
#     interval=["1 menit"],
#     periode_ma=periode_ma,
#     k_cepat=k_cepat,
#     k_lambat=k_lambat,
#     d_lambat=d_lambat,
#     mode_laju_stokastik=True,
# )

hasil_strategi = strategi_backtest.jpao_ride_the_ema(
    interval=["5 menit"], periode_ema=periode_ema, smoothing=smoothing
)
