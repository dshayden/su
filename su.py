from math import ceil

def su(cmds, out_sbatch, out_python, **kwargs):
  # setup
  N = len(cmds)
  per_task = int(kwargs.get('per_task', 1))  # how many jobs for a single task i.e. chunking factor
  n_concur = int(kwargs.get('n_concur', 1)) # how many jobs done concurrently
  output_task_guards = kwargs.get('output_task_guards', True) # Delineate output of each task
  qos = kwargs.get('qos', None) # qos to run under
  mem_per_cpu = kwargs.get('mem_per_cpu', '1gb') # RAM per allocated cpu
  time = kwargs.get('time', '00:01:00') # 1 minute for each array task
  output = kwargs.get('output', 'out_%A_%5a.out') # out_<job_id>_<run_id>.out
  nodes = kwargs.get('nodes', 1)
  ntasks = kwargs.get('ntasks', 1)
  cpus_per_task = kwargs.get('cpus_per_task', 1)
  gres = kwargs.get('gres', None) # special resources, e.g. GPU

  n_array = int(ceil(N / per_task)) # number of unique tasks

  # make python calling program, make sure it plays nice with python2 and python3
  # i.e. no format strings!
  fPy = open(out_python, 'w')
  print('import argparse as ap, shlex, subprocess as sp', file=fPy)
  print('', file=fPy)
  print('cmds = [', file=fPy)
  for cmd in cmds: print(f"  '{cmd}',", file=fPy)
  print(']', file=fPy)
  print('', file=fPy)
  print('def main(args):', file=fPy)
  print("  assert len(cmds) > args.run_id, 'Bad run id %d' % args.run_id", file=fPy)
  print('  cmd = shlex.split(cmds[args.run_id])', file=fPy)
  print('  return sp.call(cmd, shell=True)', file=fPy)
  print('', file=fPy)
  print("if __name__ == '__main__':", file=fPy)
  print("  parser = ap.ArgumentParser()", file=fPy)
  print("  parser.add_argument('run_id', type=int, help='command index to run')", file=fPy)
  print("  parser.set_defaults(func=main)", file=fPy)
  print("  args = parser.parse_args()", file=fPy)
  print("  args.func(args)", file=fPy)
  fPy.close()

  # make slurm sbatch script, can use python3 conveniences here
  fS = open(out_sbatch, 'w')  
  print('#!/bin/bash', file=fS)
  print(f'#SBATCH --nodes={nodes}', file=fS)
  print(f'#SBATCH --ntasks={ntasks}', file=fS)
  print(f'#SBATCH --cpus-per-task={cpus_per_task}', file=fS)
  print(f'#SBATCH --mem-per-cpu={mem_per_cpu}', file=fS)
  print(f'#SBATCH --time={time}', file=fS)
  print(f'#SBATCH --output={output}', file=fS)
  if qos is not None: print(f'#SBATCH --qos={qos}', file=fS)
  print(f'#SBATCH --array=1-{n_array}%{n_concur}', file=fS)
  if gres is not None: print(f'#SBATCH --gres={gres}', file=fS)
  print('', file=fS)
  print(f'PER_TASK={per_task}', file=fS)
  print('START_NUM=$(( ($SLURM_ARRAY_TASK_ID - 1) * $PER_TASK + 1 ))', file=fS)
  print('END_NUM_POSSIBLE=$(( $SLURM_ARRAY_TASK_ID * $PER_TASK ))', file=fS)
  print(f'END_NUM=$(( END_NUM_POSSIBLE <= {N} ? END_NUM_POSSIBLE : {N} ))', file=fS)
  print('', file=fS)
  print('for (( run=$START_NUM; run<=END_NUM; run++ )); do', file=fS)
  if output_task_guards:
    print(f"  echo {'='*80}", file=fS)
    print('  echo SLURM task $SLURM_ARRAY_TASK_ID, run $run', file=fS)
    print(f"  echo {'='*80}", file=fS)
  print(f'  python {out_python} $(( ($run - 1) ))', file=fS)
  print('done', file=fS)
  fS.close()
  
if __name__ == '__main__':
  cmds = ['ls -lah', 'pwd', 'date', 'whoami', 'hostname']
  su(cmds, 'jobs.sbatch', 'jobber.py', per_task=2, n_concur=2, qos='desimonelab', gres='gpu')
