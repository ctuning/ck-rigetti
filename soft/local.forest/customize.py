#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#

import os

##############################################################################

def version_cmd(i):

    full_path               = i['full_path']                            # the full_path that ends with "qvm"
    bin_path                = os.path.dirname( full_path )
    ver_detection_cmd       = "{0} --version | cut -f 1 -d ' ' >$#filename#$".format(full_path)

    return {'return':0, 'cmd': ver_detection_cmd}


def parse_version(i):

    return {'return':0, 'version': i.get('output',[''])[0] }

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


    # Get variables
    ck=i['ck_kernel']

    iv=i.get('interactive','')

    cus=i.get('customize',{})

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    winh=hosd.get('windows_base','')

    full_path               = cus.get('full_path','')
    bin_path                = os.path.dirname(full_path)

    env                     = i['env']
    env_prefix              = cus['env_prefix']
    env[env_prefix]         = bin_path
    env[env_prefix+'_BIN']  = bin_path
    env['PATH']             = bin_path + ( ';%PATH%' if winh=='yes' else ':${PATH}')

    return {'return':0, 'bat':''}
