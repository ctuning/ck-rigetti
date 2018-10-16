#!/usr/bin/env python3

#
# Copyright (c) 2018 cTuning foundation, River Lane Research, dividiti
# SPDX-Licence-Identifier: BSD-3-Clause
#
# Parts of this file originated from Rigetti's Grove library (grove/pyvqe/vqe.py)
# Copyright (c) 2016-2017 Rigetti Computing
# SPDX-Licence-Identifier: Apache-2.0
#

"""
This module runs Oscar and Daochen's version Variational-Quantum-Eigensolver on Hydrogen

Example running it partially using CK infrastructure (assuming the current directory is $HOME/CK/ck-rigetti/program/rigetti-vqe) :
    time ck virtual `ck search env:* --tags=forestopenfermion` `ck search env:* --tags=pyquil` `ck search env:* --tags=login,rigetti` `ck search env:* --tags=hackathon`  --shell_cmd="./rigetti_vqe_combined.py --shots=1000 --minimizer_method=my_minimizer --max_func_evaluations=10"
"""

import json
import time
import inspect

import numpy as np
#from scipy import linalg as la

import pyquil.api
from pyquil.quil import Program
from pyquil.paulis import PauliTerm, PauliSum
from pyquil.gates import *
#from forestopenfermion import pyquilpauli_to_qubitop
#from openfermion.transforms import jordan_wigner, get_fermion_operator, get_sparse_operator

from vqe_utils import cmdline_parse_and_report, NumpyEncoder

from vqe_hamiltonian import label_to_hamiltonian_coeff, classical_energy    # the file contents will be different depending on the plugin choice


def vqe_for_pyquil(q_device, ansatz, hamiltonian, start_params, minimizer_function, minimizer_options, sample_number, json_stream_file):

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

        if report != 'TestMode':
            report['iterations'].append( report_this_iteration )
            report['total_q_seconds'] += report_this_iteration['total_q_seconds_per_c_iteration']  # total_q_time += total
            report['total_q_shots'] += report_this_iteration['total_q_shots_per_c_iteration']

        report_this_iteration['total_seconds_per_c_iteration'] = time.time() - timestamp_before_ee

        print(report_this_iteration, "\n")
        json_stream_file.write( json.dumps(report_this_iteration, cls=NumpyEncoder)+"\n" )
        json_stream_file.flush()

        return energy


    report = { 'total_q_seconds': 0, 'total_q_shots':0, 'iterations' : [] }

    # Initial objective function value
    fun_initial = expectation_estimation(start_params, 'TestMode')
    print('Initial guess at start_params is: {:.4f}'.format(fun_initial))

    timestamp_before_optimizer = time.time()
    optimizer_output = minimizer_function(expectation_estimation, start_params, my_args=(report), my_options = minimizer_options)
    report['total_seconds'] = time.time() - timestamp_before_optimizer

    # Also generate and provide a validated function value at the optimal point
    fun_validated = expectation_estimation(optimizer_output['x'], 'TestMode')
    print('Validated value at solution is: {:.4f}'.format(fun_validated))
    optimizer_output['fun_validated'] = fun_validated

    # Exact calculation of the energy using matrix multiplication:
    progs, coefs    = hamiltonian.get_programs()
    expect_coeffs   = np.array(qvm.expectation(ansatz(optimizer_output['x']), operator_programs=progs))
    optimizer_output['fun_exact']=np.real_if_close(np.dot(coefs, expect_coeffs))

    print('Total Q seconds = %f' % report['total_q_seconds'])
    print('Total Q shots = %d' % report['total_q_shots'])
    print('Total seconds = %f' % report['total_seconds'])

    return (optimizer_output, report)


def pyquil_tiny_ansatz_2(ab):
    "in this trial, we also explicitly supply the UCC ansatz"

    return Program(
        X(0),
        X(1),
        RX(np.pi/2, 0),
        H(1),
        CNOT(0, 1),
        RZ( ab[0] )(1),
        CNOT(0, 1),
        RX(-np.pi/2)(0),
        H(1),
        H(0),
        RX(np.pi/2)(1),
        CNOT(0, 1),
        RZ( ab[1] )(1),
        CNOT(0, 1),
        H(0),
        RX(-np.pi/2, 1)
    )


def pyquil_tiny_ansatz_1(ab):

    return Program(
        X(0),
        X(1),
        RX(-np.pi/2, 0),
        RY(np.pi/2, 1),
        CNOT(0, 1),
        RZ(ab[0], 1),
        CNOT(0, 1),
        RX(np.pi/2, 0),
        RY(-np.pi/2, 1)
    )


if __name__ == '__main__':

    # Load the Hamiltonian into Pyquil-friendly format:
    pauli_list  = []
    for label in label_to_hamiltonian_coeff:
        zipped_list = [(label[j], j) for j in range(len(label))]
        pauli_list.append( label_to_hamiltonian_coeff[label] * PauliTerm.from_list( zipped_list ) )
    hamiltonian = PauliSum( pauli_list )


    (ansatz_function, num_ansatz_params) = (pyquil_tiny_ansatz_2, 2)
    #(ansatz_function, num_ansatz_params) = (pyquil_tiny_ansatz_1, 1)

    start_params, sample_number, q_device_name, minimizer_method, minimizer_options, minimizer_function = cmdline_parse_and_report(
        num_params                  = num_ansatz_params,
        q_device_name_default       = 'QVM',
        q_device_name_help          = "Real devices: '8Q-Agave' or '19Q-Acorn'. Either 'QVM' or '' for remote simulator",
        minimizer_options_default   = '{}',
        start_param_value_default   = 0.0
    )

    # ---------------------------------------- pyquil-specific init: ----------------------------------------

    qvm = pyquil.api.QVMConnection()
    if q_device_name == 'QVM':
        q_device    = qvm
    else:
        q_device    = pyquil.api.QPUConnection( q_device_name )


    ## Input molecule and basis set (this is the only user input necessary to perform VQE
    ## on the Rigetti quantum computer with a UCC ansatz)
    #
    #name, basis = 'hydrogen', 'sto-3g'
    #
    ## This input would be then converted to the correct Hamiltonian using the q_chem library
    ## developed at River Lane
    # import q_chem
    # _, _, hamiltonian, _, _ = q_chem.run_chem(name, basis)


    ## Transforming the Rigetti-style hamiltonian into numpy-friendly dense form
    ## to compute the energy classically:
    #
    #qubitOp                 = pyquilpauli_to_qubitop(hamiltonian)
    #sparse_hamiltonian_jw   = get_sparse_operator(qubitOp)
    #dense_hamiltonian_jw    = sparse_hamiltonian_jw.todense()
    #classical_energy        = np.amin(la.eigh(dense_hamiltonian_jw)[0])
    #print("Classical energy: {}".format(classical_energy))
    #
    ## Due to difficulty in reliably installing forestopenfermion + openfermion,
    ## the code above is temporarily commented out and substituted by a pre-computed constant value.

    json_stream_file = open('vqe_stream.json', 'a')

    # ---------------------------------------- run VQE: ----------------------------------------

    (vqe_output, report) = vqe_for_pyquil(q_device, ansatz_function, hamiltonian, start_params, minimizer_function, minimizer_options, sample_number, json_stream_file)

    # ---------------------------------------- store the results: ----------------------------------------

    json_stream_file.write( '# Experiment finished\n' )
    json_stream_file.close()

    minimizer_src   = inspect.getsource( minimizer_function )
    ansatz_src      = inspect.getsource( ansatz_function )
    ansatz_method   = ansatz_function.__name__

    vqe_input = {
        "q_device_name"     : q_device_name,
        "minimizer_method"  : minimizer_method,
        "minimizer_src"     : minimizer_src,
        "minimizer_options" : minimizer_options,
        "ansatz_method"     : ansatz_method,
        "ansatz_src"        : ansatz_src,
        "sample_number"     : sample_number,
        "classical_energy"  : classical_energy,
    }

    output_dict     = { "vqe_input" : vqe_input, "vqe_output" : vqe_output, "report" : report }
    formatted_json  = json.dumps(output_dict, cls=NumpyEncoder, sort_keys = True, indent = 4)

#    print(formatted_json)

    with open('rigetti_vqe_report.json', 'w') as json_file:
        json_file.write( formatted_json )
