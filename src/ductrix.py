#!/usr/bin/python
import os 
import argparse
import getpass


def get_args():
    parser = argparse.ArgumentParser( description='Arguments for talking to vCenter') 
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_create = subparsers.add_parser('create', help='create database or dbserver')

    subparsers_create= parser_create.add_subparsers(help='create help')
    parser_dbserver = subparsers_create.add_parser('dbserver', help='create a database ')

    subparsers_dbserver = parser_dbserver.add_subparsers(help='create dbserver help')

    parser_dbserver_vm = subparsers_dbserver.add_parser('vmware', help='create a database ')
    parser_dbserver_vm.add_argument('-r', '--server_role', required=True, default=None, 
        action='store', help='server role seperated by comma [mysql, postgres, oracle]')
    parser_dbserver_vm.add_argument('-s', '--ssh_user', required=False, action='store', default='root', help='ssh user to use') 
    parser_dbserver_vm.add_argument('-n', '--servername', required=True, action='store', help='Name of the New VM') 
    parser_dbserver_vm.add_argument('-d', '--datastorenm', required=False, action='store', help='datatstore to use vm')
    parser_dbserver_vm.add_argument('-v', '--pooluser', required=False, action='store', help='vcenter username')
    parser_dbserver_vm.add_argument('-i', '--network_parms', required=False, action='store', help='Name of the New VM') 

    parser_dbserver_aws = subparsers_dbserver.add_parser('aws', help='create a database ')
    parser_dbserver_aws.add_argument('-a', '--accesskey', required=False, action='store', help='datatstore to use vm')
    parser_dbserver_aws.add_argument('-n', '--servername', required=True, action='store', help='Name of the New VM') 
    parser_dbserver_aws.add_argument('-r', '--serverrole', required=True, default=None, action='store', help='datatstore to use vm')

    parser_database = subparsers_create.add_parser('database', help='create a database server')
    #parser_database.add_argument('-n', '--servername', required=True, action='store', help='Name of the New VM') 
    parser_database.add_argument('-d', '--dbname', required=True, default=None, action='store', help='Name of the New VM') 
    parser_database.add_argument('-t', '--dbtype', required=True, action='store', help='Type of database ' , choices=['mysql','postgres','oracle'] )  
    parser_database.add_argument('-n', '--servername', required=False, action='store', help='Use a paticular server for the database ') 


    # VMware  specefic

    # Aws specefic
    args = parser.parse_args()
    return args

    #if args.server_type == 'aws':
    #    args.accesskey = getpass.getpass( prompt='Enter secret key: ')
    #elif args.pooluser:
    #    args.vcpass = getpass.getpass( prompt='Enter password: ')


def runplay(playbook_nm, host, tags, args):
    ##if isinstance(args, dict):
    #    args = dotdict(args) 



    from broker import Runner
    # You may want this to run as user root instead
    # or make this an environmental variable, or
    # a CLI prompt. Whatever you want!
    #become_user_password = 'root'
    runner = Runner(
        hostnames=host,
        playbook=playbook_nm,
        tags = tags,
        run_data=args,
        verbosity=2,
        #private_key='/home/user/.ssh/id_whatever',
        #become_pass=become_user_password, 
        #become_pass=become_user_password, 
    )

    stats = runner.run()


#def downloadChunks(url, filepath):
#    # Thanks to https://gist.github.com/gourneau/1430932#file-downloadchunks-py-L29
#    import urllib2
#    import math
#    
#    """Helper to download large files
#        the only arg is a url
#       this file will go to a temp directory
#       the file will also be downloaded
#       in chunks and print out how much remains
#    """
#
#
#    #move the file to a more uniq path
#    os.umask(0002)
#    try:
#        file = filepath
#        req = urllib2.urlopen(url)
#        total_size = int(req.info().getheader('Content-Length').strip())
#        downloaded = 0
#        CHUNK = 256 * 10240
#        with open(file, 'wb') as fp:
#            while True:
#                chunk = req.read(CHUNK)
#                downloaded += len(chunk)
#                print math.floor( (downloaded / total_size) * 100 )
#                if not chunk: break
#                fp.write(chunk)
#    except urllib2.HTTPError, e:
#        print "htTP Error:",e.code , url
#        return false
#    except urllib2.URLError, e:
#        print "urL Error:",e.reason , url
#        return false
#
#    return file

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

    if args.pooluser:
        
        # image location
        vmdk_file = '/var/ductrix/images/CENTOS72_IMAGE-disk1.vmdk'
        ovf_file = '/var/ductrix/images/CENTOS72_IMAGE.ovf'
        mf_file = '/var/ductrix/images/CENTOS72_IMAGE.mf'
        
        # hosted files 
        #hvmdk_file = "https://drive.google.com/file/d/0BzGos2y0Otu-cmxFaEhnUXlPWXc/view?usp=sharing"
        #hovf_file =  "https://drive.google.com/file/d/0BzGos2y0Otu-ZllaMm1vLUNzRU0/view?usp=sharing"
        #hmf_file = "https://drive.google.com/file/d/0BzGos2y0Otu-ajl0MzdZZGFoeDg/view?usp=sharing"

        dir_path = os.path.dirname(os.path.realpath(__file__))
        from ansible_vault import Vault
        vault = Vault(args.vault_pass)
        data = vault.load(args.vault_content)
        #data = vault.load(open('{0}/pools/{1}.yml'.format(dir_path, args.poolname)).read())
            
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
        #with open('/var/hfiles/id_rsa.pub'.format(ssh_user), 'r') as keyfile:
            pubkey = keyfile.read()

        deploy_parms = {
                'name': args.servername, 
                'vmdk_file': vmdk_file,
                'ovf_file': ovf_file,
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
        playbook_nm = 'vsphere_ovf.yml'

    elif args.access_key:
        deploy_parms = vars(args)
        playbook_nm = 'aws.yml'
        
    runplay (playbook_nm = playbook_nm, host=args.servername, args = deploy_parms, tags=tags)

def setup_roles( args, tags=None):
#    if isinstance(args, dict):
#        args = dotdict(args) 

    vpass = args.get('vault_pass',None)
    vault_content = args.get('vault_content',None)
    if vpass:
        from ansible_vault import Vault
        vault = Vault(vpass)
        data = vault.load(vault_content)
        #dir_path = os.path.dirname(os.path.realpath(__file__))
        #data = vault.load(open('{0}/pools/{1}.yml'.format(dir_path, args['poolname'])).read())
        #args['poolpass'] = data['poolpass']

   # if args.dbname:
   #     run_data = { 'servername': args.servername , 'dbname': args.dbname, 'db }
   # else:
   #     run_data = { 'servername': args.servername }

    #runplay ('setupserver.yml', args.servername,  args= run_data, tags=tags)
    runplay ('setupserver.yml', args['servername'],  args=args, tags=tags)
    #runplay ('/var/hfiles/setupserver.yml', args['servername'],  args=args, tags=tags)

#def create_vaultfile( fileloc, passwd, content):
#    try:
#        from ansible_vault import Vault
#        vault = Vault(passwd)
#        vault.dump(content, open(fileloc, 'w'))
#        return 
#    except Exception as inst: 
#        raise Exception("Error occured while creating vault file {0} ".format(str(inst)))
#
#def create_vcpassfile(passwd, vcpass, poolname):
#    x = {'poolpass' : str(vcpass)}
#    dir_path = os.path.dirname(os.path.realpath(__file__))
#    create_vaultfile('{0}/pools/{1}.yml'.format(dir_path, poolname), passwd, x)

if __name__ == "__main__":

    args = get_args()

    if not hasattr(args,'dbname'):
        deploy_server(args) 

    if hasattr(args,'dbtype'):
        roles = [ 'create-{0}'.format(args.dbtype) ]
    else:
        roles = []
        for r in args.server_role.split(','):
            roles.append('install-{0}'.format(r))

    if not hasattr(args,'dbname'):
        run_data = { 'name': args.servername }
        roles.append('default')
    else:
        run_data = { 'name': 'centovf10' , 'dbname': args.dbname }

    #runplay ('setupserver.yml', run_data['name'], roles, run_data)


    runplay ('setupserver.yml', args.servername,  args= run_data, tags=tags)
    #tags = [ 'default' ,'install-mysql', 'install-postgres']


