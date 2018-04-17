#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#

import os

##############################################################################

def version_cmd(i):                     # FIXME: an extremely fragile approach - lots of assumptions:

    full_path=i['full_path']            # the full_path is to pyquil/__init__.py

    with open(full_path) as init_fd:    # this file only contains one line:     __version__ = "a.b.c"
        contents = init_fd.read()

    ver = (contents.split('"'))[1]      # assuming the format stays the same, get the stuff from between double quotes

    return {'return':0, 'cmd':'', 'version':ver}

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

    install_env             = cus.get('install_env',{})
    forest_api_key          = install_env.get('PYQUIL_FOREST_API_KEY',  os.environ.get('PYQUIL_FOREST_API_KEY',''))
    user_id                 = install_env.get('PYQUIL_USER_ID',         os.environ.get('PYQUIL_USER_ID',''))

    if forest_api_key and user_id:
        env['QVM_API_KEY']  = forest_api_key
        env['QVM_USER_ID']  = user_id
    else:
        return {'return':1, 'error':'Environment variables PYQUIL_FOREST_API_KEY and PYQUIL_USER_ID should be set!'}

    return {'return':0, 'bat':''}
