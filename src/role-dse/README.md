ansible-dse
---------

These Ansible playbooks will build a DataStax Enterprise cluster.

You can pre-build a Rackspace Cloud environment or run the playbooks against an existing environment.

It support multiple regions and multiple virtual datacenters per Region (to separate workloads).

---

## [Installation] (id:installation)

See [INSTALL.md](../master/INSTALL.md) for installation and build instructions.


## [Requirements] (id:requirements)

- Ansible >= 2.0

- Expects CentOS 7 or Ubuntu 14 hosts

- Building the Rackspace Cloud environment requires the `pyrax` Python module: https://github.com/rackspace/pyrax


## [Features] (id:features)

- It supports static inventory if the environment is pre-built (`inventory/static` file).

- Mixed cloud and static environments (hybrid) can be deployed as long as the networking permits it.

- The data drive can be customized and can be put on top of Rackspace Cloud Block Storage.

- Multiple workloads can be defined per each virtual datacenter.

- OpsCenter can run on a separate node or alongside Cassandra and authentication is enabled by default.

- It uses the `GossipingPropertyFileSnitch` Snitch with `prefer_local`.

- With static inventory, nodes can be placed in different racks for a rack-aware topology.


## [Configuration] (id:configuration)
  
A single configuration file, `playbooks/groupvars/all` is used to set global variables and the topology.

- replace user and pass with your datastax credentials (used when signing up at `https://academy.datastax.com/user/login`):
```
     dserepouser: 'user'
     dserepopass: 'pass'
```

- set the cluster name
 
- set the virtual datacenter where OpsCenter runs. It can be on a separate datacenter or one shared with DSE nodes.

  If opscenter is installed in a virtual datacenter shared with DSE, it will be installed on the first node.

- replace the `listen_interface`, `broadcast_interface` and `rpc_interface` with the correct network device names from the hosts:
```
     listen_interface: 'eth1'
     broadcast_interface: 'eth0'
     rpc_interface: 'eth1'
```

- for multi-region deployments, `broadcast_interface` must be set to a reachable interface from the other regions.

- set the workloads for each virtual datacenter.

- set cloud options if Cloud Servers need to be built.

    
## [Inventory] (id:configuration)

- The cloud environment requires the standard pyrax credentials file that looks like this:
  ````
  [rackspace_cloud]
  username = my_username
  api_key = 01234567890abcdef
  ````
  
  This file will be referenced in the `RAX_CREDS_FILE` environment variable (or `RAX_LON_CREDS_FILE` for the LON region).

  By default, the file is expected to be: `~/.raxpub` and if you use LON region, `~/.raxpub-uk` must also be set.


- When provisioning DSE on existing infrastructure edit `inventory/static` to include all hosts you expect to install DSE on and assign the hosts to the groups configured in the topology.


## [Scripts] (id:scripts)

To provision a cloud environment, run the `provision_cloud.sh` script:

````
bash provision_cloud.sh
````

Then run the bootstrap and dse scripts (in this order):
````
bash bootstrap.sh
bash dse.sh
````

## [OpsCenter] (id:opscenter)

OpsCenter runs on the first dse-node or on its own separate node and can be accessed on port 8888.

The provided Ansible playbook will only open the firewall if you've added your workstation IP to `allowed_external_ips` variable in the `playbooks/group_vars/all` file. 

Alternatively, you can access OpsCenter by either opening the firewall manually or by opening an SSH tunnel and pointing a browser to `http://localhost:8888`.

```
ssh root@{{ opscenter-node }} -L 8888:localhost:8888
```

A socks proxy could also be opened but the browser must be configured to use localhost port 12345 as a socks proxy.

```
ssh -D 12345 root@{{ opscenter-node }}
```

You'll then be able to navigate to `http://opscenter-node:8888` in your configured browser and access all subsidiary links.
