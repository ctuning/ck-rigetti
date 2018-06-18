#!/usr/bin/env python3

"""
This module runs DaoChen's version Variational-Quantum-Eigensolver on Helium

Example running it partially using CK infrastructure (assuming the current directory is $HOME/CK/ck-rigetti/program/rigetti-vqe) :
	ck virtual `ck search env:* --tags=hackathon`  --shell_cmd="./hackathon_examine.py $HOME/CK/local/experiment/leo\@dividiti.com-qvm/ckp-43c3910e884fd086.0001.json"
"""

import argparse
import json
import numpy as np

from hackathon_utils import *


arg_parser  = argparse.ArgumentParser()
arg_parser.add_argument('filename',                                 help='JSON filename')
arg_parser.add_argument('--delta',      default=0.15,   type=float, help='accepted difference from the ideal solution')
arg_parser.add_argument('--prob',       default=0.90,   type=float, help='desired probability of success')
arg_parser.add_argument('--which_fun',  default='fun_validated',    help='which function value ("fun", "fun_validated" or "fun_exact")')
arg_parser.add_argument('--which_time', default='total_q_shots',    help='which time metric ("total_q_seconds" or "total_q_shots")')
arg_parser.add_argument('--show_more',  action='store_true',        help='whether to show more stats')

args        = arg_parser.parse_args()
filename    = args.filename
delta       = args.delta
prob        = args.prob
which_fun   = args.which_fun
which_time  = args.which_time
show_more	= args.show_more

with open( filename ) as f:
    data            = json.load(f)
    list_of_runs    = [char['run'] for char in data['characteristics_list']]

    benchmark_list_of_runs(list_of_runs, delta, prob, which_fun, which_time, show_more)
