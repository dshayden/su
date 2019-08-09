# su
SLURM job utility library

# Installation
Requires Python 3.6+
```
git clone git@github.mit.edu:dshayden/su.git
cd su
pip install .
```

# Example Use
###### Using Helper Script from Shell
```
>> printf "ls -lah\npwd\nhostname" > jobs.txt
>> ls
jobs.txt
>> MakeSlurmJobFiles jobs.txt myjobs --n_concur 2 --time 00:01:00
>> ls
jobs.txt myjobs.sbatch myjobs.py myjobs.gzip
>> scp myjobs* username@mycluster:/path/on/nfs
>> ssh username@mycluster
>> cd /path/on/nfs
>> sbatch myjobs.sbatch
Submitted batch job 12345
```
###### Using from Python
```
>> python
>>> import su
>>> cmds = ['ls -lah', 'hostname', 'whoami']
>>> su.MakeJobFiles(cmds, 'myjobs', n_concur=2, time='00:01:00')
>>> exit()
>> scp myjobs* username@mycluster:/path/on/nfs
>> ssh username@mycluster
>> cd /path/on/nfs
>> sbatch myjobs.sbatch
Submitted batch job 12345
```

# Comments
* Additional documentation on nearly all keyword arguments can be found at [the SLURM website](https://slurm.schedmd.com/documentation.html)
* This library doesn't give access to --ntasks and --nodes because everything is treated as a [job array](https://slurm.schedmd.com/job_array.html). If you have 10 commands to run and you pass --n_concur 2 --per_task 3, then there will be ceil(10 / 3) = 4 jobs in the array, and all but one will execute 3 commands in sequence, and the final job will execute the remaining one command. Two jobs will be executed at a time.
