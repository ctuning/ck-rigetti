#!/usr/bin/env python3

"""
This module runs DaoChen's version Variational-Quantum-Eigensolver on Helium

Example running it partially using CK infrastructure:
    time ck virtual `ck search env:* --tags=pyquil` `ck search env:* --tags=login,rigetti` `ck search env:* --tags=hackathon`  --shell_cmd='vqe_helium_example.py --minimizer_method=my_cobyla --minimizer_options='{\"alpha\":34}'"
"""

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
                        
                    # Because Rigetti sometimes drops the connection after a few successful runs,
                    # we try to recover from unsuccessful runs and carry on
                    #
                    for attempt in range(1,8):
                        try:
                            timestamp_before_qvm = time.time()
                            result = q_device.run(meas_prog, qubits_to_measure, sample_number)
                            q_run_seconds = time.time() - timestamp_before_qvm
                            q_run_shots   = sample_number
                            break
                        except Exception as e:
                            print("Caught exception (%s), attempt number %d" % (str(e), attempt))

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


def cmdline_parse_and_report(num_params, q_device_name_default, q_device_name_help, minimizer_options_default='{}'):

    import argparse

    start_params_default = np.random.randn( num_params )  # Initial guess of ansatz

    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('--start_params', '--start-params',
                            default=start_params_default, type=float, nargs=num_params, help="Initial values of optimized parameters")

    arg_parser.add_argument('--sample_number', '--sample-number', '--shots',
                            default=100, type=int, help="Number of repetitions of each individual quantum run")

    arg_parser.add_argument('--q_device_name', '--q-device-name',
                            default=q_device_name_default, help=q_device_name_help)

    arg_parser.add_argument('--minimizer_method', '--minimizer-method',
                            default='my_nelder_mead', help="SciPy-based: 'my_nelder_mead', 'my_cobyla' or the custom 'my_minimizer'")

    arg_parser.add_argument('--max_func_evaluations', '--max-func-evaluations',
                            default=100, type=int, help="Minimizer's upper limit on the number of function evaluations")

    arg_parser.add_argument('--minimizer_options', '--minimizer-options',
                            default=minimizer_options_default, help="A dictionary in JSON format to be passed to the minimizer function")

    args = arg_parser.parse_args()

    start_params            = args.start_params
    sample_number           = args.sample_number
    q_device_name           = args.q_device_name
    minimizer_method        = args.minimizer_method
    max_func_evaluations    = args.max_func_evaluations
    minimizer_options       = json.loads( args.minimizer_options )

    # We only know how to limit the number of iterations for certain methods,
    # so will introduce this as a "patch" to their minimizer_options dictionary:
    #
    if max_func_evaluations:
        minimizer_options_update = {
            'my_nelder_mead':   {'maxfev':  max_func_evaluations},
            'my_cobyla':        {'maxiter': max_func_evaluations},
            }.get(minimizer_method, {})

        minimizer_options.update( minimizer_options_update )

    print("Using start_params = '%s'"           % str(start_params) )
    print("Using shots (sample_number) = %d"    % sample_number)
    print("Using q_device_name = '%s'"          % q_device_name)
    print("Using minimizer_method = '%s'"       % minimizer_method)
    print("Using max_func_evaluations = %d"     % max_func_evaluations)         # this parameter may influence the next one
    print("Using minimizer_options = '%s'"      % str(minimizer_options) )

    minimizer_function = getattr(optimizers, minimizer_method)   # minimizer_method is a string/name, minimizer_function is an imported callable

    return start_params, sample_number, q_device_name, minimizer_method, minimizer_options, minimizer_function


if __name__ == '__main__':
    start_params, sample_number, q_device_name, minimizer_method, minimizer_options, minimizer_function = cmdline_parse_and_report(
        num_params                  = 2,
        q_device_name_default       = 'QVM',
        q_device_name_help          = "Real devices: '8Q-Agave' or '19Q-Acorn'. Either 'QVM' or '' for remote simulator",
        minimizer_options_default   = '{}'
        )

    # ---------------------------------------- pyquil-specific init: ----------------------------------------

    if q_device_name == 'QVM':
        q_device    = pyquil.api.QVMConnection()
    else:
        q_device    = pyquil.api.QPUConnection( q_device_name )

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

    # ---------------------------------------- run VQE: ----------------------------------------

    (vqe_output, report) = daochens_vqe(q_device, helium_tiny_ansatz, hamiltonian, start_params, minimizer_function, minimizer_options, sample_number)

    # ---------------------------------------- store the results: ----------------------------------------

    vqe_input = {
        "q_device_name"     : q_device_name,
        "minimizer_method"  : minimizer_method,
        "minimizer_options" : minimizer_options,
        "sample_number"     : sample_number
        }

    minimizer_src   = inspect.getsource( minimizer_function )

    output_dict     = { "vqe_input" : vqe_input, "vqe_output" : vqe_output, "report" : report, "minimizer_src" : minimizer_src }
    formatted_json  = json.dumps(output_dict, cls=NumpyEncoder, sort_keys = True, indent = 4)

#    print(formatted_json)

    with open('vqe_report.json', 'w') as json_file:
        json_file.write( formatted_json )

