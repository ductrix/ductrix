from flask import Flask, session, redirect, url_for, render_template, request, jsonify, Response
from urlparse import urlparse
from ConfigParser import SafeConfigParser
import os, sys
from datetime import timedelta
import model
import uuid
import string
import random
from rq import Queue
from rq.job import Job
from worker import conn

config = SafeConfigParser()
app = Flask(__name__)
app.config.from_pyfile("config.py")
app.debug = True
ductrix_root = app.config['DUCTRIX_ROOT']
grafana_port = app.config['GRAFANA_PORT']

db = model.dbaccess(db_con_string=app.config['SQLALCHEMY_DATABASE_URI'], userschema=app.config['SQLALCHEMY_DATABASE_SCHEMA'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key=os.urandom(24)
#keyfile = "{0}/key".format(os.path.dirname(os.path.realpath(__file__)))
#with open (keyfile, "r") as myfile:
#    app.secret_key=myfile.read()
app.permanent_session_lifetime = timedelta(minutes=10)

q = Queue(connection=conn)


def get_servermap():
    dbsession = db.get_session()

    servermap = {}
    servertable = db.get_servertbl()
    servertableres = dbsession.query(servertable).all()

    for serveritem in servertableres: 
        servermap[serveritem.serverid ] = serveritem.servername

    dbsession.close()
    return servermap
    

def get_databasemap():
    # get all the databases
    dbmap = {}
    dbtable = db.get_dbtbl()
    dbtableres = dbsession.query(dbtable).all()

    for db_res in dbtableres:
        dbmap[db_res.dbid] = db_res.dbname
    dbsession.close()
    return dbmap

def get_poolrmap():

    poolmap= {}
    pooltable = db.get_pooltbl()
    pooltableres = dbsession.query(pooltable).all()

    for item in pooltableres: 
        poolmap[item.poolid] = item.poolname

    dbsession.close()
    return poolmap

def passgen(size=64, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route('/getvcdata', methods=['POST'])
def get_vcdata():
    vcuser= request.form['vcuser']
    vcpass = request.form['vcpass']
    vcname = request.form['vcname']
    clustername = request.form.get('clustername', None)
    try: 
        import getvclusters
        vcdata = getvclusters.getlist()
        vcdata.storeuser(vcuser)
        vcdata.storepass(vcpass)
        vcdata.storevcenter(vcname)
        if not clustername or clustername == '': 
            clusters = vcdata.getclusterlist() 
            return jsonify(clusters)
        else:
            clusters = vcdata.getclusterlist() 
            networks = vcdata.getnetworklist(clustername) 
            datastores = vcdata.getdatastorelist(clustername) 
            datacenter = vcdata.getdatacenter(clustername) 
            return jsonify({'networks': networks, 'datastores': datastores, 'datacenter': datacenter})
    except Exception as inst: 
        return '''
        <div class="alert alert-danger">
          <span class="pficon pficon-error-circle-o"></span>
          <strong>Erro occured while connecting to {0} </strong> Error: {1} </a>.
        </div> '''.format(vcname, str(inst))

@app.route('/')
def index():
    return render_template('index.html', dashboard='https://{0}:{1}/dashboard/db/server-information?from=now-30m&to=now-1m'.format(urlparse(request.url_root).hostname, grafana_port))


@app.route('/databases/<id>/')
def database_info(id):
    dbsession = db.get_session()

    dbtable = db.get_dbtbl()
    databaseres = dbsession.query(dbtable).filter(dbtable.dbid == id)

    for result in databaseres:
        serverid = result.serverid
        databasenm = result.dbname
        dbtype = result.dbtype
    if not dbtype:
        dbtype = "mysql"
    
    dbsession.close()
    return render_template('databaseinfo.html', dbconn='https://{0}:{3}/dashboard/db/{1}-dashboards?var-database={2}'.format(urlparse(request.url_root).hostname, dbtype, databasenm, grafana_port))


@app.route('/servers/<id>/')
def server_info(id):
    # get all servers 
    dbsession = db.get_session()
    servertable = db.get_servertbl()
    pooltable = db.get_pooltbl()
    serverres = dbsession.query(servertable).filter(servertable.serverid  == id)
    for result in serverres:
        servername = result.servername
        poolid = result.poolid

    poolres = dbsession.query(pooltable).filter(pooltable.poolid == poolid)
    for result2 in poolres:
        poolname = result2.poolname

    dbsession.close()
    return render_template('serverinfo.html', serverconn='https://{0}:{3}/dashboard/db/server-data?var-pool={1}&var-server={2}'.format(urlparse(request.url_root).hostname, poolname, servername, grafana_port))
    #serverconn = "httpss://{0}:9090/@{1}".format("192.168.1.107", servername)
    #return render_template('serverinfo.html', serverconn=serverconn)
    
@app.route('/pools/<id>/')
def pool_info(id):
    # get all servers 
    dbsession = db.get_session()
    pooltable = db.get_pooltbl()
    poolres = dbsession.query(pooltable).filter(pooltable.poolid == id)
    for result in poolres:
        poolname = result.poolname
    
    dbsession.close()
    return render_template('poolinfo.html', poolconn='https://{0}:{2}/dashboard/db/server-information?var-pool={1}&var-server=All'.format(urlparse(request.url_root).hostname, poolname, grafana_port))

@app.route('/databases')
def databases():
    message = None
    if request.args:
        message = request.args['message']

    dbsession = db.get_session()

    # get all the pools 
    pools = []
    pooltable = db.get_pooltbl()
    pooltableres = dbsession.query(pooltable).all()

    # get all the databases
    databases = []
    dbmap = {}
    dbtable = db.get_dbtbl()
    dbtableres = dbsession.query(dbtable).all()

    # get all servers 
    servermap = {}
    servertable = db.get_servertbl()
    servertableres = dbsession.query(servertable).all()

    dbsession.close()

    for item in pooltableres: 
        pools.append(item.poolname)

    for serveritem in servertableres: 
        servermap[serveritem.serverid ] = serveritem.servername

    #for db_res in dbtableres:
    #    databases.append("<tr>")
    #    databases.append("<td>{0}</td>".format(db_res.dbid))
    #    databases.append("<td>{0}</td>".format(db_res.dbname))
    #    databases.append("<td>{0}</td>".format(servermap[db_res.serverid]))
    #    databases.append("</tr>")
    for db_res in dbtableres:
        #dbmap[db_res.dbid] = {'dbid' : db_res.dbid, 'dbname' : db_res.dbname, 'serverid': db_res.serverid, 'servername': servermap[db_res.serverid]}
        databases.append({'dbid' : db_res.dbid, 'dbname' : db_res.dbname, 'serverid': db_res.serverid, 'servername': servermap[db_res.serverid]})
    if len(servermap.values()) <= 0 or len(pools) <=0:
        return render_template('databases.html')

    return render_template('databases.html', pool_list=pools, 
        servers_list=servermap.values(), databases_list=databases,  message=message)

@app.route('/tasks')
def tasks():
    import tasks
    alltasks = tasks.get_all_jobs(queue = q, redis_conn=conn)
    return render_template('tasks.html', task_list=alltasks)

@app.route('/servers', methods=['GET'])
def servers():
    message = None
    if request.args:
        message = request.args['message']
    # get all the pools 
    dbsession = db.get_session()

    pools = []
    pooltable = db.get_pooltbl()
    pooltableres = dbsession.query(pooltable).all()

    # get all servers 
    servers = []
    servertable = db.get_servertbl()
    servertableres = dbsession.query(servertable).all()

    dbsession.close()
    poolmap = {}

    for item in pooltableres: 
        poolmap[item.poolid] = item.poolname

    for item in pooltableres: 
        pools.append(item.poolname)

    for serveritem in servertableres: 
        servers.append({'serverid': serveritem.serverid, 'servername':serveritem.servername, \
            'poolid': serveritem.poolid, 'poolname':poolmap[serveritem.poolid]})

    if len(servers) <= 0 and len(poolmap.values()) <=0:
        return render_template('servers.html', message=message)
    elif len(servers) <= 0:
        return render_template('servers.html', pool_list=poolmap.values(), message=message)

    return render_template('servers.html', pool_list=poolmap.values(), servers_list=servers, message=message)

    if len(pools) <= 0:
        return render_template('servers.html')
    return render_template('servers.html', pool_list=pools)

def server_create(servername, poolid, args, tags): 
    try:
        sys.path.append(ductrix_root)

        import ductrix
        # Run the Server create Job
        res = ductrix.deploy_server(args)

        # Get the output of the commands 
        print res

        # Run the Job to add roles to the server
        setupserv = ductrix.setup_roles(args, tags)

        # Get the output of the commands 
        print setupserv

        # Add new server to the database
        dbsession = db.get_session()
        servertable = db.get_servertbl()

        # By Default no roles 
        roledict = { 'mysql_role': False,
            'postgres_role':  False,
            'oracle_role': False,
            }

        # Tags contains the roles like 'mysql_role' that user checked in the form
        # hence check the roles that are declared and assign them to True for our database entry 
        for role in tags:
            if role in roledict.keys():
                roledict[role] = True
                
        dbsession.add(servertable( servername=servername, 
            poolid=poolid, 
            mysql_role = roledict['mysql_role'],
            postgres_role = roledict['postgres_role'],
            oracle_role = roledict['oracle_role'],
            serverid=str(uuid.uuid4()) ))
        dbsession.commit()
        dbsession.close()
        success_msg = """
                <div class="toast-pf alert alert-success alert-dismissable">
                  <span class="pficon pficon-ok"></span>
                  Server {0} has been created successfully.
                </div> """.format(servername)
        return success_msg
    except Exception as inst: 
        failed_msg = """
                <div class="toast-pf alert alert-danger alert-dimissable">
                  <span class="pficon pficon-error-circle-o"></span>
                  Sorry ! There was an error while creating {0} server. {1}
                </div> """.format(servername, inst)
        #return redirect(url_for('servers', message=failed_msg))
        return failed_msg

def database_create(args, tags): 
    try:
        sys.path.append(ductrix_root)
        import ductrix

        databasetable = db.get_dbtbl()
        servertable = db.get_servertbl()
        setupserv = ductrix.setup_roles(args, tags)

        dbsession = db.get_session()

        # This comes from database create web form ex. create-mysql, create-postgres, create-oracle
        # Resulting value is mysql,postgres,oracle
        databasetype = tags[0].split('-')[-1]
                
        serverresults = dbsession.query(servertable).filter(servertable.servername == args['servername']).all()

        for result in serverresults :
            serverid = result.serverid

        dbsession.add(databasetable( dbname=args['dbname'], serverid=serverid, dbid=str(uuid.uuid4()), dbtype = databasetype))
        dbsession.commit()
        dbsession.close()

        success_msg = """
                <div class="toast-pf alert alert-success alert-dismissable">
                  <span class="pficon pficon-ok"></span>
                  Database {0} has been created successfully.
                </div> """.format(args['dbname'])
        return success_msg

    except Exception as inst: 
        failed_msg = """
                <div class="toast-pf alert alert-danger alert-dimissable">
                  <span class="pficon pficon-error-circle-o"></span>
                  Sorry ! There was an error while creating {0} Database. {1}
                </div> """.format(args['dbname'] , inst)
        #return redirect(url_for('servers', message=failed_msg))
        return failed_msg

@app.route('/createdatabase', methods=['POST'])
def create_database():
    databasetype = request.form['database_type']
    databasename = request.form['database_name']
    poolname = request.form['pool_name']
    servername = request.form['server_name']
    memsize = request.form['mem_size']
    dbuser = request.form['username']
    dbpasswd = request.form['password']
    tags = [ databasetype ] 

    args = {}
    args['dbname'] = databasename
    args['servername'] = servername
    args['dbuser'] = dbuser
    args['memsize'] = memsize
    args['dbpasswd'] = dbpasswd
    args['poolname'] = poolname
    if databasetype == 'oracle':
        args['disk_type'] = 'thin'
        args['disk_size'] = '20'

    dbsession = db.get_session()
    pooltable = db.get_pooltbl()
    privatepool = db.get_privatepooltbl()
    poolresult = dbsession.query(pooltable).filter(pooltable.poolname == poolname).all()
    poolid = None 
    for result in poolresult:
        poolid = result.poolid
        privatepoolresult = dbsession.query(privatepool).filter(privatepool.poolid == result.poolid).all()

    for result in privatepoolresult:
        args['pooluser'] = result.username
        args['pooltarget'] = result.targetserver
        #args['cluster'] = result.clusternm
        #args['network'] = result.networknm
        #args['datastore'] = result.storagenm
        args['datacenter'] = result.datacenternm
        passwd = result.password
        content = result.content
        
    # Decryption
    import base64
    ## Encryption
    args['vault_pass'] = base64.b64decode(passwd)
    args['vault_content'] = base64.b64decode(content)

    job = q.enqueue_call(func=database_create, args=(args, tags), result_ttl=5000, timeout=10000)
    jid = job.get_id()

    job_msg = """
              <button type="button" class="close" data-dismiss="alert" aria-hidden="true">
                <span class="pficon pficon-close"></span>
              </button>
              <span class="pficon pficon-ok"></span>
              Task to create {0} database has been submited ,taskid <a href={1}>{2}</a>
            """.format(databasename, url_for('tasks'), jid)
    return redirect(url_for('databases', message=job_msg))

@app.route('/createpool', methods=['POST'])
def create_pool():
    pooltype = request.form['pooltype']
    poolname = request.form['poolname'].upper()
    if pooltype == 'vmware':
        vcname = request.form['vcname']
        vcuser = request.form['vcuser']
        vcpass = request.form['vcpass']
        clustername = request.form['clustername']
        networkname = request.form.get('networkname', None)
        datastorename = request.form.get('datastorename', None)
        datacentername = request.form.get('datacentername', None)

        dbsession = db.get_session()
        dbsession = db.get_session()
        pooltable = db.get_pooltbl()
        privatepool = db.get_privatepooltbl()
        poolid = str(uuid.uuid4()) 
        passwd = passgen()
        #from Crypto.Cipher import AES
        import base64
        ## Encryption
        #encryption_suite = AES.new('BM^@Y5BENeX2qpw$rRRkfR1LQ5$jQtMf', AES.MODE_CBC, 'This is an IV456')
        #passwd = encryption_suite.encrypt(passwd)
        hashpass = base64.b64encode(passwd)

	from ansible_vault import Vault
	vault = Vault(passwd)
	vault_content = vault.dump({'poolpass' : str(vcpass)})
        hashcontent = base64.b64encode(vault_content)

        try:
            sys.path.append(ductrix_root)
            #import ductrix
            #ductrix.create_vcpassfile(passwd, "{0}".format(vcpass), poolname)
            dbsession.add(pooltable( poolname=poolname, pooltype=pooltype, poolid=poolid))
            dbsession.add(privatepool(username=vcuser,password=hashpass, content=hashcontent, targetserver=vcname, 
		clusternm=clustername, poolid=poolid, networknm=networkname, storagenm=datastorename, datacenternm=datacentername))
            dbsession.commit()
            dbsession.close()

            successmsg = "{0} Pool has been created sucessfully".format(poolname)
            job_msg = gen_message("success", successmsg)

        except Exception as inst: 
            error = inst
            errormsg = "Error occured while connecting to {0} : {1} ".format(poolname, error)
            job_msg = gen_message("danger", errormsg)
        return redirect(url_for('pools', message=job_msg))

def gen_message(msgtype, message):

    return '''<div class="toast-pf toast-pf-max-width toast-pf-top-right alert alert-{0} alert-dimissable">
          <button type="button" class="close" data-dismiss="alert" aria-hidden="true">
            <span class="pficon pficon-close"></span> </button>
          <span class="pficon pficon-ok"></span>
          {1}
          </div>'''.format(msgtype, message)
            
@app.route('/createserver', methods=['POST'])
def create_servers():
    poolname = request.form['pool_name']
    servername = request.form['server_name'].upper()
    memsize = request.form['mem_size']
    cpucount = request.form['cpu_count']
    mysql = request.form.get('mysql_role', None)
    postgres = request.form.get('postgres_role', None)
    oracle = request.form.get('oracle_role', None)
    dhcp = request.form.get('dhcp', None)
    static = request.form.get('static', None)

    tags = [ 'default']
    roles = [ mysql, postgres, oracle]
    for role in roles:
        if role:
            tags.append(str(role))
        
    args = {}
    args['servername'] = servername
    args['poolname'] = poolname
    args['cpucount'] = cpucount
    args['memsize'] = int(memsize) * 1024
    if oracle:
        args['disk_type'] = 'thin'
        args['disk_size'] = '20'

    if dhcp:
        args['network_parms'] = "BOOTPROTO\=dhcp"
    if static:
        ipaddr = request.form.get('ipaddr')
        subnet = request.form.get('subnet')
        gateway = request.form.get('gateway')
        dns1 = request.form.get('dns1', gateway)
        args['network_parms'] = "BOOTPROTO\=static,IPADDR\={0},NETMASK\={1},GATEWAY\={2},DNS1\={3}".format(ipaddr, subnet, gateway, dns1)

    args['ssh_user'] = "root"

    pooltable = db.get_pooltbl()
    privatepool = db.get_privatepooltbl()
    publicpool = db.get_publicpooltbl()

    dbsession = db.get_session()
    poolresult = dbsession.query(pooltable).filter(pooltable.poolname == poolname).all()
    poolid = None 
    for result in poolresult:
        if result.pooltype == 'vmware':
            poolid = result.poolid
            privatepoolresult = dbsession.query(privatepool).filter(privatepool.poolid == result.poolid).all()

    for result in privatepoolresult:
        args['pooluser'] = result.username
        args['pooltarget'] = result.targetserver
        args['cluster'] = result.clusternm
        args['network'] = result.networknm
        args['datastore'] = result.storagenm
        args['datacenter'] = result.datacenternm
        #args['vault_pass'] = result.password
        passwd = result.password
        content = result.content

    # Decryption
    import base64
    ## Encryption
    args['vault_pass'] = base64.b64decode(passwd)
    args['vault_content'] = base64.b64decode(content)

    job = q.enqueue_call(func=server_create, args=(servername, poolid, args, tags), result_ttl=5000, timeout=10000)
    jid = job.get_id()

    job_msg = """
            <div class="toast-pf alert alert-success alert-dismissable">
              <button type="button" class="close" data-dismiss="alert" aria-hidden="true">
                <span class="pficon pficon-close"></span>
              </button>
              <span class="pficon pficon-ok"></span>
              Task to create {0} server submited successfully with taskid <a href={1}>{2}</a>
            </div> """.format(servername, url_for('tasks'), jid)
    dbsession.close()
    return redirect(url_for('servers', message=job_msg))

@app.route('/pools')
def pools():
    message = None
    if request.args:
        message = request.args['message']
    pools = []
    pooltable = db.get_pooltbl()
    privatepool = db.get_privatepooltbl()
    publicpool = db.get_publicpooltbl()

    # get all the pools 
    dbsession = db.get_session()
    pooltableres = dbsession.query(pooltable).all()

    for item in pooltableres: 
        pools.append("<tr>")
        pools.append("<td>{0}</td>".format(item.poolid))
        pools.append("<td>{0}</td>".format(item.poolname))
        pools.append("<td>{0}</td>".format(item.pooltype))
        pools.append("</tr>")

    dbsession.close()

    # get the id that was generated from SEQ in the database 

    if len(pools) <= 0:
        return render_template('pools.html', message=message)
    return render_template('pools.html', pools_list=pools, message=message)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=443, debug = 'True')
