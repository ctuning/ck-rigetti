#!/usr/bin/python

#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

import os
import sys
import json

##############################################################################
# customize installation

def setup(i):
    """
    Input:  {
              cfg              - meta of this soft entry
              self_cfg         - meta of module soft
              ck_kernel        - import CK kernel module (to reuse functions)

              host_os_uoa      - host OS UOA
              host_os_uid      - host OS UID
              host_os_dict     - host OS meta

              target_os_uoa    - target OS UOA
              target_os_uid    - target OS UID
              target_os_dict   - target OS meta

              target_device_id - target device ID (if via ADB)

              tags             - list of tags used to search this entry

              env              - updated environment vars from meta
              customize        - updated customize vars from meta

              deps             - resolved dependencies for this soft

              interactive      - if 'yes', can ask questions, otherwise quiet

              path             - path to entry (with scripts)
              install_path     - installation path
            }

    Output: {
              return        - return code =  0, if successful
                                          >  0, if error
              (error)       - error text if return > 0

              (install_env) - prepare environment to be used before the install script
            }

    """

    import os
    import shutil

    # Get variables
    o=i.get('out','')

    ck=i['ck_kernel']

    env=i['env']

    pi=i.get('install_path','')

    pix=os.path.join(pi, i['cfg']['end_full_path_universal'])

    cus=i['customize']
    ie=cus.get('install_env',{})
    nie={} # new env

    # Customization
    forest_api_key  = os.environ.get('PYQUIL_FOREST_API_KEY','')
    user_id         = os.environ.get('PYQUIL_USER_ID','')

    interactive     = i.get('interactive','')

    if interactive and not (forest_api_key and user_id):
        ck.out('')

        kernel_ret = ck.inp({'text': 'Please enter your Forest API key: '})
        if kernel_ret['return']:
            return kernel_ret
        else:
            forest_api_key = kernel_ret['string']

        kernel_ret = ck.inp({'text': 'Please enter your Forest User ID: '})
        if kernel_ret['return']:
            return kernel_ret
        else:
            user_id = kernel_ret['string']

    if forest_api_key and user_id:
        nie['QVM_API_KEY']  = forest_api_key
        nie['QVM_USER_ID']  = user_id
    else:
        return {'return':1, 'error':'Environment variables PYQUIL_FOREST_API_KEY and PYQUIL_USER_ID should be set!'}

    r=ck.save_json_to_file({'json_file':pix, 'dict':nie})
    if r['return']>0: return r

    return {'return':0}
