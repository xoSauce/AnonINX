from __future__ import with_statement
from contextlib import contextmanager as _contextmanager
from fabric.api import *
from fabric.contrib.console import confirm
import time

env.use_ssh_config = True
env.env_directory = 'ENV'
env.user ='ec2-user'
env.code_dir = '/home/%s/itPIR' % env.user
env.repo = 'https://github.com/xoSauce/Lower-Cost-epsilon-Private-Information-Retrieval.git'
env.timestamp = "release_%s" % int(time.time() * 1000)
env.activate = "source %s/releases/%s/%s/bin/activate" % (env.code_dir, env.timestamp, env.env_directory)
#timestamp="release_%s" % int(time.time() * 1000)
def all_hosts():
    env.hosts = [
        'key-broker'
        , 'mix-node1'
        , 'mix-node2'
        , 'mix-node3'
        , 'mix-node4'
        , 'mix-node5'
    ]

def mix_hosts():
    env.hosts = [
        'mix-node1'
        , 'mix-node2'
        , 'mix-node3'
        , 'mix-node4'
        , 'mix-node5'
    ]

def keybroker_host():
    env.hosts = ['key-broker']


def deploy():
    define_permissions()
    system_dependencies()
    fetch_repo()
    update_permissions()
    create_venv()
    run_pip()


def system_dependencies():
    sudo('yum install -y openssl-devel')
    sudo("yum groupinstall -y 'Development Tools'")
    sudo('yum install -y libffi-devel')
    sudo("yum install -y python35")
    sudo("yum install -y python35-virtualenv.noarch")
    sudo("yum install -y git")

def fetch_repo():
    with settings(warn_only=True):
        run("mkdir %s" % env.code_dir)
    with cd(env.code_dir):
        with settings(warn_only=True):
            run("mkdir releases")
    with cd("%s/releases" % env.code_dir):
        run("git clone %s %s" % (env.repo, env.timestamp))

def create_venv():
    with cd("%s/releases/%s" % (env.code_dir, env.timestamp)):
        run("virtualenv-3.5 %s" % env.env_directory)

@_contextmanager
def virtualenv():
    with cd(env.code_dir):
        with prefix(env.activate):
            yield

def run_pip():
    with virtualenv():
        with cd("%s/releases/%s/" % (env.code_dir, env.timestamp)):
            run('pip3.5 install -r requirements.txt --ignore-installed')
            run('pip freeze')

def define_permissions():
    with settings(warn_only=True):
        sudo("groupadd itPIR")
        sudo("usermod -a -G itPIR %s" % env.user)

def update_permissions():
    with cd("%s/releases/%s" % (env.code_dir, env.timestamp)):
        sudo("chgrp -R itPIR .")
        sudo("chmod -R ug+rwx .")
