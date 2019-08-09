import gzip, json, math

def MakeJobFiles(cmds, outputPrefix, **kwargs):
  # setup
  N = len(cmds)

  # how many jobs done concurrently
  n_concur = int(kwargs.get('n_concur', 1)) 

  # how many jobs for a single task i.e. chunking factor
  per_task = int(kwargs.get('per_task', 1))

  # max time for each chunk of jobs in job array'
  time = kwargs.get('time', None)

  # string qos to run under, default for cluster if not specified'
  qos = kwargs.get('qos', None)

  # number of CPU cores for each chunk of jobs in job array
  cpus_per_task = kwargs.get('cpus_per_task', 1)

  # RAM per allocated cpu
  mem_per_cpu = kwargs.get('mem_per_cpu', '1gb')

  # generic resources, e.g. GPU
  gres = kwargs.get('gres', None)

  # print header for each job in stdout
  output_job_header = kwargs.get('output_job_header', True)

  # capture stdout and stderr to out_<job_id>_<run_id>.out
  output = kwargs.get('output', 'out_%A_%5a.out')

  # run on a specified partition
  partition = kwargs.get('partition', None)
  
  # load modules as part of job, only for clusters with support for
  # http://modules.sourceforge.net/
  modules = kwargs.get('modules', None) 


  n_array = int(math.ceil(N / per_task)) # number of unique tasks

  # Make python calling program, make sure it plays nice with python2 and
  # python3 for using on broadest set of clusters
  fPy = open(f'{outputPrefix}.py', 'w')
  print('from __future__ import print_function', file=fPy)
  print('import argparse as ap, shlex, subprocess as sp', file=fPy)
  print('import json, gzip', file=fPy)
  print('', file=fPy)
  print(f"with gzip.GzipFile('{outputPrefix}.gzip','r') as fin: cmds = json.loads(fin.read().decode('utf-8'))", file=fPy)
  print('', file=fPy)
  print('def main(args):', file=fPy)
  print("  assert len(cmds) > args.run_id, 'Bad run id %d' % args.run_id", file=fPy)
  print('  cmd = shlex.split(cmds[args.run_id])', file=fPy)
  print('  return sp.call(cmd)', file=fPy)
  print('', file=fPy)
  print("if __name__ == '__main__':", file=fPy)
  print("  parser = ap.ArgumentParser()", file=fPy)
  print("  parser.add_argument('run_id', type=int, help='command index to run')", file=fPy)
  print("  parser.set_defaults(func=main)", file=fPy)
  print("  args = parser.parse_args()", file=fPy)
  print("  args.func(args)", file=fPy)
  fPy.close()

  # Make slurm sbatch script, can use python3 conveniences here e.g. f-strings
  fS = open(f'{outputPrefix}.sbatch', 'w')  
  print('#!/bin/bash', file=fS)
  print(f'#SBATCH --cpus-per-task={cpus_per_task}', file=fS)
  print(f'#SBATCH --mem-per-cpu={mem_per_cpu}', file=fS)
  if time is not None: print(f'#SBATCH --time={time}', file=fS)
  print(f'#SBATCH --output={output}', file=fS)
  if qos is not None: print(f'#SBATCH --qos={qos}', file=fS)
  if partition is not None: print(f'#SBATCH --partition {partition}', file=fS)
  print(f'#SBATCH --array=1-{n_array}%{n_concur}', file=fS)
  if gres is not None: print(f'#SBATCH --gres={gres}', file=fS)
  print('', file=fS)
  if modules is not None:
    for module in modules: print(f'module load {module}', file=fS)
  print('', file=fS)
  print(f'PER_TASK={per_task}', file=fS)
  print('START_NUM=$(( ($SLURM_ARRAY_TASK_ID - 1) * $PER_TASK + 1 ))', file=fS)
  print('END_NUM_POSSIBLE=$(( $SLURM_ARRAY_TASK_ID * $PER_TASK ))', file=fS)
  print(f'END_NUM=$(( END_NUM_POSSIBLE <= {N} ? END_NUM_POSSIBLE : {N} ))', file=fS)
  print('', file=fS)
  print('for (( run=$START_NUM; run<=END_NUM; run++ )); do', file=fS)
  if output_job_header:
    print(f"  echo {'='*80}", file=fS)
    print('  echo SLURM task $SLURM_ARRAY_TASK_ID, run $run', file=fS)
    print(f"  echo {'='*80}", file=fS)
  print(f'  python {outputPrefix}.py $(( ($run - 1) ))', file=fS)
  print('done', file=fS)
  fS.close()

  # make json file of jobs
  with gzip.GzipFile(f'{outputPrefix}.gzip', 'w') as fid:
    fid.write(json.dumps(cmds).encode('utf-8'))
  
if __name__ == '__main__':
  cmds = ['ls -lah', 'pwd', 'date', 'whoami', 'hostname', 'singularity --help']
  su(cmds, 'jobs', per_task=2, n_concur=2)
