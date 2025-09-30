from fabric import task


@task
def qlaunch(c):
    """Launch FireWorks jobs on Quest"""
    c.run(
        "source /projects/p32234/projects/aerith/eis_mellon/.venv/bin/activate && module load openssl && cd /projects/p32234/projects/aerith/eis_mellon && qlaunch -q /projects/p32234/projects/aerith/eis_mellon/queuing/slurm_qadapter.yaml rapidfire  "
    )


@task
def qlaunch_single(c):
    """Launch a single FireWorks job on Quest"""
    c.run(
        "source /projects/p32234/projects/aerith/eis_mellon/.venv/bin/activate && module load openssl && cd /projects/p32234/projects/aerith/eis_mellon && qlaunch singleshot"
    )
