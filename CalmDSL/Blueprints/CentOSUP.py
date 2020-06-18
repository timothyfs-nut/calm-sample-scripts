from calm.dsl.builtins import SimpleDeployment, SimpleBlueprint
from calm.dsl.builtins import read_local_file, basic_cred
from calm.dsl.builtins import AhvVmResources, AhvVmDisk, AhvVmNic, AhvVmGC, AhvVm
from calm.dsl.builtins import action, CalmTask, CalmVariable

# Simple Single VM Blueprint with taks for OS opdate
# Change values based on your calm environment
IMAGE_NAME = 'CENTOS_76'
NETWORK_NAME = 'dnd-demo'

# Password file located under './.local'
CENTOS_PASSWD = read_local_file('centos')
CENTOS_CRED = basic_cred('centos', CENTOS_PASSWD, name='CENTOS_CRED', default=True)

# Simple CentOS Guest Customizations Coud Init
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


class CentOS(SimpleDeployment):
    provider_spec = CentosVm
    os_type = 'Linux'
@action
def __install__(self):
        CalmTask.Exec.ssh(name='Update CentOS', script='sudo yum -y --quiet update')

class CentOSBlueprint(SimpleBlueprint):
    credentials = [CENTOS_CRED]
    deployments = [CentOS]


def main():
    print(CentOSBlueprint.json_dumps(pprint=True))

if __name__ == '__main__':
    main()