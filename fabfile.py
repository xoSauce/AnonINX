from __future__ import with_statement
from contextlib import contextmanager as _contextmanager
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.operations import put
from fabric.contrib.files import exists
import os
import time
import re

env.use_ssh_config = True
env.env_directory = 'ENV'
env.user ='ubuntu'
env.latest_dir = '/home/%s/itPIR/latest' % env.user
env.code_dir = '/home/%s/itPIR' % env.user
env.repo = 'https://github.com/xoSauce/Lower-Cost-epsilon-Private-Information-Retrieval.git'
env.timestamp = "release_%s" % int(time.time() * 1000)
env.activate = "source %s/releases/%s/%s/bin/activate" % (env.code_dir, env.timestamp, env.env_directory)
#timestamp="release_%s" % int(time.time() * 1000)
def all_hosts():
    env.hosts = [
        'key-brokerU'
        , 'mix-node1U'
        , 'mix-node2U'
        , 'mix-node3U'
        , 'mix-node4U'
        , 'mix-node5U'
        , 'db1'
        , 'db2'
        , 'db3'
        , 'db4'
    ]
def debug_hosts():
	env.hosts = [
     	'key-brokerU'
        , 'mix-node1U'
        , 'mix-node2U'
        , 'db1'
        , 'db2'
	]

def all_dbs():
	env.hosts = [
		'db1',
		'db2',
		'db3',
		'db4',
	]

def db_1_2():
    env.hosts = [
		'db1',
        'db2'
	]
def db_1():
	env.hosts = [
		'db1'
	]

def db_2():
    env.hosts = [
        'db2'
    ]

def mix_hosts():
    env.hosts = [
        'mix-node1U'
        , 'mix-node2U'
        , 'mix-node3U'
        , 'mix-node4U'
        , 'mix-node5U'
    ]

def mix_1():
    env.hosts = ['mix-node1U']
def mix_2():
    env.hosts = ['mix-node2U']

def mix_1_2():
    env.hosts = [
        'mix-node1U'
        , 'mix-node2U'
    ]

def mix_1_2_3():
    env.hosts = [
        'mix-node1U'
        , 'mix-node2U'
        , 'mix-node3U'
    ]
def keybroker_host():
    env.hosts = ['key-brokerU']

def start_keybroker():
    with virtualenv_latest():
        with cd(env.latest_dir):
            run('python3 m_keys_server.py')
@parallel
def start_db_listener(ip, port, db_path):
    if not exists(db_path):
        print("db_path: {} not found".format(db_path))
        return False
    port = int(port)
    pattern = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    if not pattern.match(ip):
        return False
    with virtualenv_latest():
        with cd(env.latest_dir):
            run_string = "python3 m_db_server.py {} {} -db {}".format(ip,port,db_path)
            run(run_string)
@parallel
def start_mix_listener(ip, port):
    try:
        port = int(port)
        pattern = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        if not pattern.match(ip):
            return False
        with virtualenv_latest():
            with cd(env.latest_dir):
                run("python3 m_mixnode_server.py %s %s" % (ip, port))
    except ValueError:
        return False

def clear_global_pip():
    sudo("sudo pip freeze | xargs sudo pip uninstall -y")

def remove_():
    with cd("~"):
        sudo("rm -rf itPIR")
@parallel
def deploy():
    define_permissions()
    system_dependencies_ubuntu()
    fetch_repo()
    update_permissions()
    create_venv()
    run_pip()
    copy_latest()

def deploy_db_file(path_db):
	run("mkdir -p %s" % "dbs")
	put(path_db, "dbs/")

def kill_python():
    sudo("pkill python");

def copy_latest():

    with settings(warn_only=True):
        with cd(env.code_dir):
            run("mkdir -p %s" % env.latest_dir)
            with cd(env.latest_dir):
                run("rm -rf *")
        with cd("%s/releases/" % (env.code_dir)):
            directory = run("ls -td -- */ | head -n 1")
            with cd(directory):
                run("cp -r * %s" % (env.latest_dir))

def system_dependencies_ubuntu():
    sudo('apt-get update')
    sudo('apt-get install -y libssl-dev')
    sudo("apt-get install -y python-pip python-dev python3-dev build-essential")
    sudo('apt-get install -y libffi-dev')
    sudo("apt-get install -y python3")
    sudo("apt-get install -y git")
    sudo("pip install virtualenv")

def system_dependencies():
    sudo('yum install -y openssl-devel')
    sudo("yum groupinstall -y 'Development Tools'")
    sudo('yum install -y libffi-devel')
    sudo("yum install -y python35")
    sudo("yum install -y git")
    sudo("pip install virtualenv")

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
        run("virtualenv -p python3 %s" % env.env_directory)

@_contextmanager
def virtualenv():
    with cd(env.code_dir):
        with prefix(env.activate):
            yield
@_contextmanager
def virtualenv_latest():
    with cd(env.latest_dir):
        with prefix("source ENV/bin/activate"):
            yield

def run_pip():
    with virtualenv():
        with cd("%s/releases/%s/" % (env.code_dir, env.timestamp)):
            run('pip install -r requirements.txt --no-cache-dir')
            run('pip freeze')

def define_permissions():
    with settings(warn_only=True):
        sudo("groupadd itPIR")
        sudo("usermod -a -G itPIR %s" % env.user)

def update_permissions():
    with cd("%s/releases/%s" % (env.code_dir, env.timestamp)):
        sudo("chgrp -R itPIR .")
        sudo("chmod -R ug+rwx .")
