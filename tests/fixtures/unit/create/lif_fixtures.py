#!/usr/bin/env python
# encoding:utf8
'''
Creates fixtures for nnmt tests.

WARNING: Only use this script, if your code is trustworthy! The script runs
         the nnmt code to produce the fixtures that are then
         stored in h5 format. If you run this script and your code is not
         working correctly, a lot of tests will pass despite your code giving
         wrong results.

If you still want to run this script, go to /nnmt/tests/fixture/ and type:
python unit/create/lif_fixtures.py -f <module>

Usage: lif_fixtures.py [options] <module>

Options:
    -f, --force        force code to run
    -h, --help         show this information
'''

import docopt
import inspect
import sys
import os
import numpy as np
import nnmt.input_output as io

from nnmt.input_output import load_val_unit_dict
from nnmt.utils import (
    _strip_units,
    _to_si_units,
    )

import nnmt


def get_required_params(func, all_params):
    """Checks arguments of func and returns corresponding parameters."""
    required_keys = list(inspect.signature(func).parameters)
    required_params = {k: v for k, v in all_params.items()
                       if k in required_keys}
    return required_params


def extract_required_params(func, regime_params):
    extracted = [get_required_params(func, params)
                 for params in regime_params]
    return extracted


def create_and_save_fixtures(func, regime_params, regimes, file):
    results = {}
    regime_params = extract_required_params(func,
                                            regime_params)
    for regime, params in zip(regimes, regime_params):
        output = func(**params)
        results[regime] = {
            'params': params,
            'output': output
            }
    io.save_h5(file, results, overwrite_dataset=True)


def load_params_and_regimes(config_path):
    param_files = os.listdir(config_path)
    regimes = [file.replace('.yaml', '').replace('.h5', '')
               for file in param_files]
    regime_params = [load_val_unit_dict(config_path + file)
                     for file in param_files]
    for dict in regime_params:
        _to_si_units(dict)
        _strip_units(dict)
    return regime_params, regimes


if __name__ == '__main__':
    # always show help message if not invoked with -f option
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    args = docopt.docopt(__doc__)

    # only run code if users are sure they want to do it
    if '--force' in args.keys():

        fixture_path = 'unit/data/'

        module = args['<module>']

        if (module == 'firing_rates') or (module == 'all'):
            config_path = 'unit/config/firing_rates/'
            regime_params, regimes = load_params_and_regimes(config_path)
            create_and_save_fixtures(
                nnmt.lif.delta._firing_rates_for_given_input,
                regime_params, regimes,
                fixture_path + 'lif_delta_firing_rate.h5')
            create_and_save_fixtures(nnmt.lif.exp._firing_rate_taylor,
                                     regime_params, regimes,
                                     fixture_path
                                     + 'lif_exp_firing_rate_taylor.h5')
            create_and_save_fixtures(nnmt.lif.exp._firing_rate_shift,
                                     regime_params, regimes,
                                     fixture_path
                                     + 'lif_exp_firing_rate_shift.h5')
        elif (module == 'inputs') or (module == 'all'):
            config_path = 'unit/config/inputs/'
            regime_params, regimes = load_params_and_regimes(config_path)
            create_and_save_fixtures(nnmt.lif._general._mean_input,
                                     regime_params, regimes,
                                     fixture_path + 'lif_mean_input.h5')
            create_and_save_fixtures(nnmt.lif._general._std_input,
                                     regime_params, regimes,
                                     fixture_path + 'lif_std_input.h5')
        elif (module == 'transfer_functions') or (module == 'all'):
            config_path = 'unit/config/transfer_functions/'
            regime_params, regimes = load_params_and_regimes(config_path)
            create_and_save_fixtures(nnmt.lif.exp._transfer_function_shift,
                                     regime_params, regimes,
                                     fixture_path
                                     + 'lif_exp_transfer_function_shift.h5')
            create_and_save_fixtures(nnmt.lif.exp._transfer_function_taylor,
                                     regime_params, regimes,
                                     fixture_path
                                     + 'lif_exp_transfer_function_taylor.h5')
            create_and_save_fixtures(
                nnmt.lif.exp._derivative_of_firing_rates_wrt_input_rate,
                regime_params, regimes,
                fixture_path
                + 'lif_exp_derivative_of_firing_rates_wrt_input_rate.h5')
            create_and_save_fixtures(
                nnmt.lif.exp._derivative_of_firing_rates_wrt_mean_input,
                regime_params, regimes,
                fixture_path
                + 'lif_exp_derivative_of_firing_rates_wrt_mean_input.h5')
        elif (module == 'sensitivity_measure') or (module == 'all'):
            config_path = 'unit/config/sensitivity_measure/'
            regime_params, regimes = load_params_and_regimes(config_path)
            create_and_save_fixtures(nnmt.lif.exp._effective_connectivity,
                                     regime_params, regimes,
                                     fixture_path
                                     + 'lif_exp_effective_connectivity.h5')
            create_and_save_fixtures(nnmt.lif.exp._sensitivity_measure,
                                     regime_params, regimes,
                                     fixture_path
                                     + 'lif_exp_sensitivity_measure.h5')
            create_and_save_fixtures(nnmt.lif.exp._sensitivity_measure_all_eigenmodes,
                                     regime_params, regimes,
                                     fixture_path
                                     + 'lif_exp_sensitivity_measure_all_eigenmodes.h5')
            create_and_save_fixtures(nnmt.lif.exp._power_spectra,
                                     regime_params, regimes,
                                     fixture_path
                                     + 'lif_exp_power_spectra.h5')
            create_and_save_fixtures(nnmt.lif.exp._propagator,
                                     regime_params, regimes,
                                     fixture_path
                                     + 'lif_exp_propagator.h5')
        elif (module == '_match_eigenvalues_across_frequencies') or (
            module == 'all'):
            # loading complex values from a .yaml does not work with
            # yaml.safe_load(), here we bypass this via .h5

            # load effective connectivity from .yaml
            config_path = 'unit/config/sensitivity_measure/'
            regime_params, regimes = load_params_and_regimes(config_path)
            # save complex eigenvalues as source for the fixtures
            intermediate_config_path = (
                'unit/config/_match_eigenvalues_across_frequencies/')
            # calculate complex eigenvalues and save to .h5
            for regime, params in zip(regimes, regime_params):
                effective_connectivity = params['effective_connectivity']
                quantity_dict = {'margin' : params['margin'],
                                 'eigenvalues' : np.linalg.eig(
                                     effective_connectivity)[0]}

                nnmt.input_output.save_quantity_dict_to_h5(
                    os.path.join(intermediate_config_path,
                                 f'{regime}.h5'),
                    quantity_dict)
            # create the fixtures
            regime_params, regimes = load_params_and_regimes(
                intermediate_config_path)
            create_and_save_fixtures(
                nnmt.lif.exp._match_eigenvalues_across_frequencies,
                regime_params, regimes,
                fixture_path
                + 'lif_exp_match_eigenvalues_across_frequencies.h5')
        elif (module == 'external_rates') or (module == 'all'):
            config_path = 'unit/config/external_rates/'
            regime_params, regimes = load_params_and_regimes(config_path)
            create_and_save_fixtures(
                nnmt.lif.exp._external_rates_for_fixed_input,
                regime_params, regimes,
                fixture_path
                + 'lif_exp_external_rates_for_fixed_input.h5')
        else:
            print('No such module')
