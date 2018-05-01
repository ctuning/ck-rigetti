import json
import os
import re

#FIXME GET FILENAME 
def ck_postprocess(i):
    ck=i['ck_kernel']
    d={}
    env=i.get('env',{})    
    rt=i['run_time']
#    for ii in i.keys():
#        print ii
    d['program_name'] = i['meta']['data_name']
    rf1=rt['run_cmd_out1']
    r=ck.load_text_file({'text_file':rf1,'split_to_list':'yes'})
    if r['return']>0: return

#  PARSER GOES HERE
    for line in r['lst']:
        ls = line.split('\t')
# END 
    d['execution_time'] = 1.100


    if d.has_key('execution_time'):
        d['post_processed'] = 'yes'
    rr={}
    rr['return']=0
    if d.get('post_processed','')=='yes':
        r=ck.save_json_to_file({'json_file':'vqe_output.json', 'dict':d})
        if r['return']>0: return r
    else:
       rr['return']=1
       rr['error']='failed to find the time in output'

    return rr
# Do not add anything here!
   
