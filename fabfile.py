import dotenv
dotenv.read_dotenv()

import os

from fabric.api import *

from jupiter.aws import Ec2

env.user = os.environ.get('FABRIC_USER')
env.key_filename = os.environ.get('FABRIC_KEY_FILENAME')

def staging():
    ec2 = Ec2()
    env.hosts = ec2.instances_dns_names()
    print env

def local_uname():
    local('uname -a')

def remote_uname():
    run('uname -a')
