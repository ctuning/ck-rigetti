#!/usr/bin/env python3

"""
This module runs DaoChen's version Variational-Quantum-Eigensolver on Helium
"""

import sys
import json
import time

import numpy as np

import pyquil.api
from pyquil.quil import Program
from pyquil.paulis import PauliTerm
from pyquil.gates import *

import inspect
from hackathon import optimizers as optimizers

# See https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
#
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return json.JSONEncoder.default(self, obj)

def daochens_vqe(q_device, ansatz, hamiltonian, start_params, minimizer_function, minimizer_options, sample_number):

    def expectation_estimation(ab, report):
        """
            instead of using Rigetti's VQE instance as is, we have taken it apart to help us improve it 
            TODO: change the expectation-estimation algorithm according to our paper arXiv:1802.00171
        """
        
        timestamp_before_ee = time.time()

        state_program = ansatz(ab)
        expectation = 0.0   

        report_this_iteration = {
            'total_q_seconds_per_c_iteration' : 0.0,
            'seconds_per_individual_q_run' : [],
            'total_q_shots_per_c_iteration' : 0,
            'shots_per_individual_q_run' : []
            }

        for j, term in enumerate(hamiltonian.terms):
            meas_basis_change = Program()
            qubits_to_measure = []
            if term.id() == "":
                meas_outcome = 1.0
            else:
                for index, gate in term: 
                    
                    # TODO: vary sample_number with term.coefficient to make VQE more efficient
                    ## sample_number = 1000;

                    qubits_to_measure.append(index)
                    if gate == 'X':
                        meas_basis_change.inst(RY(-np.pi/2, index))
                    elif gate == 'Y':
                        meas_basis_change.inst(RX(np.pi/2, index))
                    
                    meas_prog = state_program + meas_basis_change
                    for qindex in qubits_to_measure:
                        meas_prog.measure(qindex, qindex)
                        
                    # our own short program to get the expectation.
                    timestamp_before_qvm = time.time()
                    result = q_device.run(meas_prog, qubits_to_measure, sample_number)
                    q_run_seconds = time.time() - timestamp_before_qvm
                    q_run_shots   = sample_number

                    meas_outcome = np.sum([np.power(-1, np.sum(x)) for x in result])/sample_number

                    report_this_iteration['total_q_seconds_per_c_iteration'] += q_run_seconds # total_q_time_per_iteration
                    report_this_iteration['seconds_per_individual_q_run'].append( q_run_seconds ) # q_time_per_iteration
                    report_this_iteration['total_q_shots_per_c_iteration'] += q_run_shots
                    report_this_iteration['shots_per_individual_q_run'].append( q_run_shots )

            expectation += term.coefficient * meas_outcome

        energy = expectation.real
        report_this_iteration['energy'] = energy

        report['iterations'].append( report_this_iteration )
        report['total_q_seconds'] += report_this_iteration['total_q_seconds_per_c_iteration']  # total_q_time += total
        report['total_q_shots'] += report_this_iteration['total_q_shots_per_c_iteration']

        report_this_iteration['total_seconds_per_c_iteration'] = time.time() - timestamp_before_ee

        print(report_this_iteration, "\n")

        return energy

    report = { 'total_q_seconds': 0, 'total_q_shots':0, 'iterations' : [] }

    # we fix the maximum number of function evaluations to allow for benchmarking
    timestamp_before_optimizer = time.time()
    optimizer_output = minimizer_function(expectation_estimation, start_params, my_args=(report), my_options = minimizer_options)
    timestamp_after_optimizer = time.time()

    total_optimization_seconds = timestamp_after_optimizer - timestamp_before_optimizer

    report['total_seconds'] = total_optimization_seconds

    print('Total Q seconds = %f' % report['total_q_seconds'])
    print('Total Q shots = %d' % report['total_q_shots'])
    print('Total seconds = %f' % report['total_seconds'])

    return (optimizer_output, report)

    # the "correct answer" is: -2.8551604772427424 a.u.
    # this number now serves as an "application-based" benchmarking tool


def helium_tiny_ansatz(ab):
    "in this trial, we also explicitly supply the UCC ansatz"

    a = ab[0];
    b = ab[1];
    p = Program(
    X(0),
    X(1),
    RX(np.pi/2, 0),
    H(1),
    CNOT(0, 1),
    RZ(a)(1),
    CNOT(0, 1),
    RX(-np.pi/2)(0),
    H(1),
    H(0),
    RX(np.pi/2)(1),
    CNOT(0, 1),
    RZ(b)(1),
    CNOT(0, 1),
    H(0),
    RX(-np.pi/2, 1))

    return p

if __name__ == '__main__':
    if len(sys.argv)!=5:
        print("Usage: "+sys.argv[0]+" <q_device_name> <minimizer_method> <max_function_evaluations> <sample_number>")
        exit(1)

    q_device_name               = sys.argv[1]       # '8Q-Agave', '19Q-Acorn', etc . Empty string means run on QVM simulator.
    minimizer_method            = sys.argv[2]
    max_function_evaluations    = int( sys.argv[3] )
    sample_number               = int( sys.argv[4] )

    print("Trying q_device_name='"+q_device_name+"'")
    print("Using minimizer_method='"+minimizer_method+"'")
    print("Using max_function_evaluations="+str(max_function_evaluations))
    print("Using sample_number="+str(sample_number))

    # input molecule and basis set (this is the only user input necessary to perform VQE
    # on the Rigetti quantum computer with a UCC ansatz)
    name = 'helium'
    basis = 'sto-3g'

    # # this input would be then converted to the correct Hamiltonian using the q_chem library
    # # developed here at River Lane
    # import q_chem
    # _, _, hamiltonian, _, _ = q_chem.run_chem(name, basis)

    # in this trial, we instead explicitly supply the hamiltonian for "helium, sto-3g"
    hamiltonian = \
        -1.6678202144537553*PauliTerm('I',0) + \
        0.7019459893849936*PauliTerm('Z',0) + \
        0.263928235683768058*PauliTerm.from_list([("Z", 0), ("Z", 1)]) + \
        0.7019459893849936*PauliTerm('Z',1)
    ansatz = helium_tiny_ansatz
    start_params = [1, 1]

    if not q_device_name or q_device_name == 'QVM':
        q_device        = pyquil.api.QVMConnection()
        q_device_name   = 'QVM'                         # only setting it for printable output
    else:
        q_device        = pyquil.api.QPUConnection( q_device_name )

    minimizer_options = {
        'my_nelder_mead':   {'maxfev':  max_function_evaluations},
        'my_cobyla':        {'maxiter': max_function_evaluations},
        'my_minimizer':     {}
        }[minimizer_method]

    vqe_input = {
        "q_device_name"     : q_device_name,
        "minimizer_method"  : minimizer_method,
        "minimizer_options" : minimizer_options,
        "sample_number"     : sample_number
        }

    minimizer_function = getattr(optimizers, minimizer_method)   # minimizer_method is a string/name, minimizer_function is an imported callable

    (vqe_output, report) = daochens_vqe(q_device, ansatz, hamiltonian, start_params, minimizer_function, minimizer_options, sample_number)

    minimizer_src   = inspect.getsource( minimizer_function )

    output_dict     = { "vqe_input" : vqe_input, "vqe_output" : vqe_output, "report" : report, "minimizer_src" : minimizer_src }
    formatted_json  = json.dumps(output_dict, cls=NumpyEncoder, sort_keys = True, indent = 4)

#    print(formatted_json)

    with open('vqe_report.json', 'w') as json_file:
        json_file.write( formatted_json )

