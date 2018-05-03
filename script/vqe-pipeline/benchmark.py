#! /usr/bin/python
import ck.kernel as ck
import copy
import re
import argparse


# Program and command.
program='vqe-demo'
cmd_key='vqe-helium-example'

# Platform tags.
methods=["Nelder-Mead"]
iterations={
  'start':60,
  'stop': 80,
  'step':20
}
sample_sizes=[100, 1000]

# Number of statistical repetitions.
num_repetitions=3


def do(i, arg):
    # Detect basic platform info.
    ii={'action':'detect',
        'module_uoa':'platform',
        'out':'out'}
    r=ck.access(ii)
    if r['return']>0: return r

    # Host and target OS params.
    hos=r['host_os_uoa']
    hosd=r['host_os_dict']

    tos=r['os_uoa']
    tosd=r['os_dict']
    tdid=r['device_id']


    # Load meta and desc of program:vqe-demo to check deps.
    ii={'action':'load',
        'module_uoa':'program',
        'data_uoa':program}
    rx=ck.access(ii)
    if rx['return']>0: return rx
    mm=rx['dict']

    # Get compile-time and run-time deps.
    cdeps=mm.get('compile_deps',{})
    rdeps=mm.get('run_deps',{})

    # Merge rdeps with cdeps for setting up the pipeline (which uses
    # common deps), but tag them as "for_run_time".
    for k in rdeps:
        cdeps[k]=rdeps[k]
        cdeps[k]['for_run_time']='yes'

    depl=copy.deepcopy(cdeps['lib-pyquil'])
    if (arg.tos is not None) and (arg.did is not None):
        tos=arg.tos
        tdid=arg.did

    ii={'action':'resolve',
        'module_uoa':'env',
        'host_os':hos,
        'target_os':tos,
        'device_id':tdid,
        'out':'con',
        'deps':{'lib-pyquil':copy.deepcopy(depl)}
    }
    r=ck.access(ii)
    if r['return']>0: return r

    udepl=r['deps']['lib-pyquil'].get('choices',[]) # All UOAs of env for Caffe libs.
    if len(udepl)==0:
        return {'return':1, 'error':'Rigetti pyQuil is not installed'}

    # Prepare pipeline.
    cdeps['lib-pyquil']['uoa']=udepl[0]

    ii={'action':'pipeline',
        'prepare':'yes',
        'dependencies':cdeps,

        'module_uoa':'program',
        'data_uoa':program,
        'cmd_key':cmd_key,

        'target_os':tos,
        'device_id':tdid,

        'env':{
          'CK_SOME_VARIABLE_HERE':1,
          'CK_ANOTHER_VARIABLE':4
        },

        'no_state_check':'yes',
        'no_compiler_description':'yes',
        'skip_calibration':'yes',

        'cpu_freq':'max',
        'gpu_freq':'max',

        'flags':'-O3',
        'speed':'no',
        'energy':'no',

        'skip_print_timers':'yes',
        'out':'con'
    }

    r=ck.access(ii)
    if r['return']>0: return r

    fail=r.get('fail','')
    if fail=='yes':
        return {'return':10, 'error':'pipeline failed ('+r.get('fail_reason','')+')'}

    ready=r.get('ready','')
    if ready!='yes':
        return {'return':11, 'error':'pipeline not ready'}

    state=r['state']
    tmp_dir=state['tmp_dir']

    # Clean pipeline.
    if 'ready' in r: del(r['ready'])
    if 'fail' in r: del(r['fail'])
    if 'return' in r: del(r['return'])

    pipeline=copy.deepcopy(r)

    for lib_uoa in udepl:
        # Load pyQuil lib.
        ii={'action':'load',
            'module_uoa':'env',
            'data_uoa':lib_uoa}
        r=ck.access(ii)
        if r['return']>0: return r
        lib_name=r['data_name']
        lib_tags='rigetti-pyquil' 
        skip_compile='no'

        record_repo='local'
        record_uoa=lib_tags

            # Prepare pipeline.
        ck.out('---------------------------------------------------------------------------------------')
        ck.out('%s - %s' % (lib_name, lib_uoa))
        ck.out('Experiment - %s:%s' % (record_repo, record_uoa))

        # Prepare autotuning input.
        cpipeline=copy.deepcopy(pipeline)

        # Reset deps and change UOA.
        new_deps={'lib-pyquil':copy.deepcopy(depl)}

        new_deps['lib-pyquil']['uoa']=lib_uoa

        jj={'action':'resolve',
            'module_uoa':'env',
            'host_os':hos,
            'target_os':tos,
            'device_id':tdid,
            'deps':new_deps}
        r=ck.access(jj)
        if r['return']>0: return r
        cpipeline['dependencies'].update(new_deps)
        cpipeline['no_clean']=skip_compile
        cpipeline['no_compile']=skip_compile

        cpipeline['cmd_key']=cmd_key
        ii={'action':'autotune',

            'module_uoa':'pipeline',
            'data_uoa':'program',

            'choices_order':[
                [
                    '##choices#env#VQE_MINIMIZER_METHOD'
                ],
                [
                    '##choices#env#VQE_MAX_ITERATIONS'
                ],
                [
                    '##choices#env#VQE_SAMPLE_SIZE'
                ]
            ],
            'choices_selection':[
                {'type':'loop', 'choice':methods},
                {'type':'loop', 'start':iterations['start'], 'stop':iterations['stop'], 'step':iterations['step'] },
                {'type':'loop', 'choice':sample_sizes}
            ],

            'features_keys_to_process':['##choices#*'],

            'iterations':-1,
            'repetitions':num_repetitions,

            'record':'yes',
            'record_failed':'yes',
            'record_params':{
                'search_point_by_features':'yes'
            },
            'record_repo':record_repo,
            'record_uoa':record_uoa,

            'tags':[ 'explore-method-iteration-sample', cmd_key, lib_tags],

            'pipeline':cpipeline,
            'out':'con'}

        r=ck.access(ii)
        if r['return']>0: return r

        fail=r.get('fail','')
        if fail=='yes':
            return {'return':10, 'error':'pipeline failed ('+r.get('fail_reason','')+')'}
            skip_compile='yes'
    return {'return':0}

parser = argparse.ArgumentParser(description='Pipeline')
parser.add_argument("--target_os", action="store", dest="tos")
parser.add_argument("--device_id", action="store", dest="did")
myarg=parser.parse_args()


r=do({}, myarg)
if r['return']>0: ck.err(r)
