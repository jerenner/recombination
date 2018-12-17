from __future__ import print_function

import argparse
from time import sleep
import magic
from subprocess import call
import sys, os
from datetime import datetime
from os.path import dirname
from glob import glob

script_name = "/home/jrenner/recombination/recomb_calc.py"
ntrks = 1000

# ------------------------------------------------------------------------------
# recomb_prod.py

def get_parser(args=None):
    parser = argparse.ArgumentParser(description='Script to produce HDF5 files')
    parser.add_argument('-j','--jobs',
                        action='store',
                        help='jobs',
                        required='True')
    return parser


#get options
args = get_parser().parse_args()
opts = vars(args) # dict
#print(args)

njobs = int(args.jobs)

#----------- check and make dirs
def checkmakedir( path ):
    if os.path.isdir( path ):
        print('hey, directory already exists!:\n' + path)
    else:
        os.makedirs( path )
        print('creating directory...\n' + path)

JOBSDIR = '/home/jrenner/recombination/jobs'

checkmakedir(JOBSDIR)

#remove old jobs
jobs_files = glob(JOBSDIR + '/recomb_*.sh')
map(os.remove, jobs_files)

exec_template_file = '/home/jrenner/recombination/template/recomb.sh'
exec_template = open(exec_template_file).read()
exec_params = {'jobsdir' : JOBSDIR}

jobfilename = JOBSDIR + '/' + 'recomb_0.sh'
jobfile = open(jobfilename, 'w')
jobfile.write(exec_template.format(**exec_params))

count_jobs = 0
for j in range(njobs):
    if j > 0:
        jobfile.write('\n\necho date\ndate\n')
        jobfile.close()
        count_jobs += 1
        jobfilename = JOBSDIR + '/recomb_{}.sh'.format(count_jobs)
        jobfile = open(jobfilename, 'w')
        jobfile.write(exec_template.format(**exec_params))

    r1 = int((ntrks / njobs) * j)
    r2 = int((ntrks / njobs) * (j+1))
    if(j == njobs-1): r2 = ntrks

    cmd = 'python {0} {1} {2}\n'.format(script_name,r1,r2)
    jobfile.write(cmd)
jobfile.write('\n\necho date\ndate\n')
jobfile.close()

#send jobs
for i in range(0, count_jobs+1):
    cmd = 'qsub {}/recomb_{}.sh'.format(JOBSDIR, i)
    print(cmd)
    os.system(cmd)
    sleep(0.5)

sys.exit()
