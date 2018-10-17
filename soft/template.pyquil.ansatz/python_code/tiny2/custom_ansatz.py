#!/usr/bin/env python3

import numpy as np
import pyquil.quil
import pyquil.gates as g


num_params = 2      # make sure you set this correctly to the number of parameters used by the ansatz


def tiny_ansatz_2(current_params):
    "Previously used for Helium VQE in Rigetti implementation"

    return pyquil.quil.Program(
        g.X(0),
        g.X(1),
        g.RX(np.pi/2, 0),
        g.H(1),
        g.CNOT(0, 1),
        g.RZ( current_params[0] )(1),
        g.CNOT(0, 1),
        g.RX(-np.pi/2)(0),
        g.H(1),
        g.H(0),
        g.RX(np.pi/2)(1),
        g.CNOT(0, 1),
        g.RZ( current_params[1] )(1),
        g.CNOT(0, 1),
        g.H(0),
        g.RX(-np.pi/2, 1)
    )
