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

    cus=i.get('customize',{})

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    winh=hosd.get('windows_base','')

    env = i['env'] 

    full_path               = cus.get('full_path','')

    r=ck.load_json_file({'json_file':full_path})
    if r['return']>0: return r

    d=r['dict']

    env['QVM_API_KEY']  = d['QVM_API_KEY']
    env['QVM_USER_ID']  = d['QVM_USER_ID']

    # For now write dummy JSON (it was used to pass info) - later can remove passwords and add other important info
    d={}
    r=ck.save_json_to_file({'json_file':full_path, 'dict':d})
    if r['return']>0: return r
    
    return {'return':0, 'bat':''}

