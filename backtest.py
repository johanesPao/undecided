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
k_cepat = 300
k_lambat = 300
d_lambat = 30

# RTW
# periode_ma = 200
# k_cepat = 21
# k_lambat = 10
# d_lambat = 10

# RTE
# periode_ema = 36
# periode_ema_cepat = 5
# dual_ema = False
# smoothing = 14
# demastoch = False
# k_cepat = 50
# k_lambat = 400
# d_lambat = 100

# Inisiasi kelas strategi
strategi_backtest = Strategi(
    ASET_DATA,
    ASET,
    EXCHANGE,
    backtest=True,
    jumlah_periode_backtest=4320,
    saldo_backtest=33,
    leverage_backtest=1,
)

# Eksekusi strategi dalam fungsi backtest kelas Strategi
hasil_strategi = strategi_backtest.jpao_niten_ichi_ryu_28_16_8(
    interval=["1 jam", "1 jam"],
    k_cepat=k_cepat,
    k_lambat=k_lambat,
    d_lambat=d_lambat,
)

# hasil_strategi = strategi_backtest.jpao_ride_the_wave(
#     interval=["1 menit"],
#     periode_ma=periode_ma,
#     k_cepat=k_cepat,
#     k_lambat=k_lambat,
#     d_lambat=d_lambat,
#     mode_laju_stokastik=True,
# )

# hasil_strategi = strategi_backtest.jpao_ride_the_ema(
#     interval=["1 menit"],
#     periode_ema=periode_ema,
#     smoothing=smoothing,
#     dual_ema=dual_ema,
#     periode_ema_cepat=periode_ema_cepat,
#     demastoch=demastoch,
#     k_cepat=k_cepat,
#     k_lambat=k_lambat,
#     d_lambat=d_lambat,
# )
