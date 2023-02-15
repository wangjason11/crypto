__version__ = "4.0"

import hashlib
import websocket
import _thread
import time
import json
import random
import sys
import web3

# for debugging, enable this line and add pdb.set_trace() where you want a breakpoint:
# import pdb

from web3 import Web3, HTTPProvider
from operator import itemgetter
from collections import OrderedDict

# The functions below are used for our soliditySha256() function
from web3.utils.normalizers import abi_ens_resolver
from web3.utils.abi import map_abi_data
from eth_utils import add_0x_prefix, remove_0x_prefix
from web3.utils.encoding import hex_encode_abi_type

# EtherDelta contract address
# This rarely changes.
addressEtherDelta = '0x8d12A197cB00D4747a1fe03395095ce2A5CC6819'    # etherdelta_2's contract address
# Global API interfaces
web3 = Web3(HTTPProvider('https://mainnet.infura.io/Ky03pelFIxoZdAUsr82w'))

class EtherDeltaClientService:

    # Global lists of sells, buys and trades that are always sorted and updated whenever data comes in
    orders_sells = []
    orders_buys = []
    trades = []

    # Personal order and trade books
    my_orders_sells = []
    my_orders_buys = []
    my_trades = []

    ws = None