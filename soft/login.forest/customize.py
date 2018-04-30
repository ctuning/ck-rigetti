#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#

import os

##############################################################################

def version_cmd(i):

    # The concept of version is not generally applicable to credentials

    return {'return':0, 'cmd':'', 'version':'N/A'}

##############################################################################

def dirs(i):
    dirs    = i.get('dirs', [])

    # The concept of directories is not applicable to credentials

    return {'return':0, 'dirs':[]}

##############################################################################

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
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              bat          - prepared string for bat file
            }

    """

    ck              = i['ck_kernel']

    forest_api_key  = os.environ.get('PYQUIL_FOREST_API_KEY','')
    user_id         = os.environ.get('PYQUIL_USER_ID','')

    interactive     = i.get('interactive','')

    env             = i['env']                      # target structure to deposit the future environment variables

    if interactive and not (forest_api_key and user_id):
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
        env['QVM_API_KEY']  = forest_api_key
        env['QVM_USER_ID']  = user_id
    else:
        return {'return':1, 'error':'Environment variables PYQUIL_FOREST_API_KEY and PYQUIL_USER_ID should be set!'}

    return {'return':0, 'bat':''}

