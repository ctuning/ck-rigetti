#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#

import os

##############################################################################

def version_cmd(i):

    path_with_init_py       = i['full_path']                            # the full_path that ends with PACKAGE_NAME/__init__.py
    path_without_init_py    = os.path.dirname( path_with_init_py )
    package_name            = os.path.basename( path_without_init_py )
    super_path              = os.path.dirname( path_without_init_py )
    ver_detection_cmd       = "PYTHONPATH={0} python3 -c 'import {1} ; print({1}.__version__)' >$#filename#$".format(super_path, package_name)

    return {'return':0, 'cmd': ver_detection_cmd}


def parse_version(i):

    return {'return':0, 'version': i.get('output',[''])[0] }

##############################################################################

def dirs(i):
    hosd    = i['host_os_dict']
    macos   = hosd.get('macos','')
    dirs    = i.get('dirs', [])

    if macos:
        python_site_packages_dir = os.path.expanduser("~") + "/Library/Python"
        if os.path.isdir( python_site_packages_dir ):
            dirs.append( python_site_packages_dir )

    return {'return':0, 'dirs':dirs}

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
    path_lib                = os.path.dirname(full_path)
    path_install            = os.path.dirname(path_lib)
    path_pre_install        = os.path.dirname(path_install)

    env                     = i['env']
    env_prefix              = cus['env_prefix']
    env[env_prefix]         = path_install
    env[env_prefix+'_LIB']  = path_lib
    env[env_prefix+'_EXAMPLES'] = os.path.join(path_pre_install,'src','examples')

    env['PYTHONPATH']       = path_install + ( ';%PYTHONPATH%' if winh=='yes' else ':${PYTHONPATH}')

    return {'return':0, 'bat':''}
