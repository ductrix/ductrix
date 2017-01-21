import os 
import argparse
import getpass
import configparser
config = configparser.ConfigParser()


def runplay(playbook_nm, host, tags, args):
    from broker import Runner
    # You may want this to run as user root instead
    # or make this an environmental variable, or
    # a CLI prompt. Whatever you want!
    runner = Runner(
        hostnames=host,
        playbook=playbook_nm,
        tags = tags,
        run_data=args,
	hostfile = config.get('settings','hostfile'),
        verbosity=2,
        #private_key='/home/user/.ssh/id_whatever',
        #become_pass=become_user_password, 
        #become_pass=become_user_password, 
    )

    stats, success  = runner.run()

    if not success: 
    	raise ValueError('Job Failed: {0}'.format(stats))
    else:
	return str(stats)


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def deploy_server( args, tags=None):
    '''
    args for vmware = ( network_parms="comma,seperated,string", 
        name = "name of the vm",
        ssh_user = 'user to use for ssh,default root',
        datastore = 'target datastore for the vm'

    args for aws = ( network_parms=" comma, seperated, string", 
        'name'  = "name of the vm",
        'access_key' =  "access key for the aws',
        'secret_ key' = "secreat key for the aws',
    '''
    if isinstance(args, dict):
        args = dotdict(args) 

    if args.pooltype == 'vmware':
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        from ansible_vault import Vault
        vault = Vault(args.vault_pass)
        data = vault.load(args.vault_content)

        # This is passed to the newlybuilt.sh which splits based on ','
        # then appends all the line to the network-scripts file for ethernet
        network_parms = args.network_parms

        # This will figure out which users public key to send to the newly server
        if args.ssh_user:
            ssh_user = args.ssh_user
        else:
            ssh_user = 'root'

        # This key will be added to the .authorized_keys file on the server
        with open('/{0}/.ssh/id_rsa.pub'.format(ssh_user), 'r') as keyfile:
            pubkey = keyfile.read()

        deploy_parms = {
                'name': args.servername, 
                'vmdk_file': config.get(args.osimage, 'vmdk'),
                'ovf_file': config.get(args.osimage, 'ovf'),
                'cluster': args.cluster,
                'pooltarget': args.pooltarget,
                'poolname': args.poolname,
                'datacenter': args.datacenter,
                'cpucount': args.cpucount,
                'memsize': args.memsize,
                'pooluser': args.pooluser,
                'poolpass': data['poolpass'],
                'datastore': args.datastorenm,
                # This is the Default user and password for the OVF image
                'vmuser': 'root',
                'vmpasswd': 'Ductrix1', 
                # startup script on the OVF image
                'program_to_run': '/etc/dbcboot/newlybuilt.sh', 
                'cmd_to_run': '{0} /{1}/.ssh/authorized_keys \"{2}\"'.format(network_parms, ssh_user, pubkey)
        }

        # Playbook for OVF deploy
    playbook_nm = config.get('books', args.pooltype )

    return runplay (playbook_nm = playbook_nm, host=args.servername, args = deploy_parms, tags=tags)

def setup_roles( args, tags=None):
   '''Used to assign and execute a role on a server'''
    vpass = args.get('vault_pass',None)
    vault_content = args.get('vault_content',None)
    if vpass:
        from ansible_vault import Vault
        vault = Vault(vpass)
        data = vault.load(vault_content)

    return runplay (config.get('books', 'setup'), args['servername'],  args=args, tags=tags)

