from calm.dsl.builtins import SimpleDeployment, SimpleBlueprint
from calm.dsl.builtins import read_local_file, basic_cred
from calm.dsl.builtins import AhvVmResources, AhvVmDisk, AhvVmNic, AhvVmGC, AhvVm
from calm.dsl.builtins import action, CalmTask, CalmVariable


# Change values based on your calm environment
IMAGE_NAME = 'CENTOS_76'
NETWORK_NAME = 'dnd-demo'

# Password file located under './.local'
CENTOS_PASSWD = read_local_file('centos')
CENTOS_CRED = basic_cred('centos', CENTOS_PASSWD, name='CENTOS_CRED', default=True)


class CentosVmResources(AhvVmResources):

    memory = 4
    vCPUs = 2
    cores_per_vCPU = 1
    disks = [AhvVmDisk.Disk.Scsi.cloneFromImageService(IMAGE_NAME, bootable=True)]
    nics = [AhvVmNic.DirectNic.ingress(NETWORK_NAME)]
    guest_customization = AhvVmGC.CloudInit(
        config={
            'password': CENTOS_PASSWD,
            'ssh_pwauth': True,
            'chpasswd': { 'expire': False }
        }
    )


class CentosVm(AhvVm):
    resources = CentosVmResources

# 
class ApachePHP(SimpleDeployment):
    provider_spec = CentosVm
    os_type = 'Linux'
    min_replicas = '@@{COUNT}@@'

    @action
    def __install__(self):
        CalmTask.Exec.ssh(name='install_apache', filename='scripts/Apache_install.sh')

class HAProxy(SimpleDeployment):
    provider_spec = CentosVm
    os_type = 'Linux'

    @action
    def __install__(self):
        CalmTask.Exec.ssh(name='install_haproxy', filename='scripts/haproxy_install.sh')

class MySQL(SimpleDeployment):
    provider_spec = CentosVm
    os_type = 'Linux'

    @action
    def __install__(self):
        CalmTask.Exec.ssh(name='install_mysql', filename='scripts/mysql_install.sh')


class LAMPBlueprint(SimpleBlueprint):
    credentials = [CENTOS_CRED]
    deployments = [ApachePHP, HAProxy, MySQL]

    MYSQL_PASSWORD = CalmVariable.Simple.Secret('MYSQL_PASSWORD', label='MySQL root password',runtime=True)
    COUNT = CalmVariable.WithOptions.Predefined.string(['1', '2', '3'], default='1', name='COUNT',
                                                        label='Apache Count', runtime=True)

def main():
    print(LAMPBlueprint.json_dumps(pprint=True))

if __name__ == '__main__':
    main()