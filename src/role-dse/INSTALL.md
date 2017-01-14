ansible-dse installation guide
---------

* These Ansible playbooks can build a Cloud environment and install DataStax Enterprise on it. Follow this [link](#install-dse-on-rackspace-cloud).

* It can also install DSE on existing Linux devices, be it dedicated devices in a datacenter or VMs running on a hypervizor. Follow this [link](#install-dse-on-existing-devices).


---


# Install DSE on Rackspace Cloud

## Build setup

First step is to setup the build node / workstation.

This build node or workstation will run the Ansible code and build the DSE cluster (itself can be a DSE or OpsCenter node).

This node needs to be able to contact the cluster devices via SSH and the Rackspace APIs via HTTPS.

The following steps must be followed to install Ansible and the prerequisites on this build node / workstation, depending on its operating system:

### CentOS/RHEL 6

1. Install Ansible and git:

  ```
  sudo su -
  yum -y remove python-crypto
  yum install http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
  yum repolist; yum install gcc gcc-c++ python-pip python-devel sshpass git vim-enhanced -y
  pip install ansible pyrax importlib oslo.config==3.0.0
  ```

2. Generate SSH public/private key pair (press Enter for defaults):

  ```
  ssh-keygen -q -t rsa
  ```

### CentOS/RHEL 7

1. Install Ansible and git:

  ```
  sudo su -
  yum install https://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
  yum repolist; yum install gcc gcc-c++ python-pip python-devel sshpass git vim-enhanced -y
  pip install ansible pyrax
  ```

2. Generate SSH public/private key pair (press Enter for defaults):

  ```
  ssh-keygen -q -t rsa
  ```

### Ubuntu 14+ / Debian 8

1. Install Ansible and git:

  ```
  sudo su -
  apt-get update; apt-get -y install python-pip python-dev sshpass git vim
  pip install ansible pyrax
  ```

2. Generate SSH public/private key pair (press Enter for defaults):

  ```
  ssh-keygen -q -t rsa
  ```

## Setup the Rackspace credentials files

The cloud environment requires the standard [pyrax](https://github.com/rackspace/pyrax/blob/master/docs/getting_started.md#authenticating) credentials file that looks like this:
```
[rackspace_cloud]
username = my_username
api_key = 01234567890abcdef
```

Replace `my_username` with your Rackspace Cloud username and `01234567890abcdef` with your API key.

Save this file as `.raxpub` under the home folder of the user running the playbook.

If multi-regions including LON are to be used, then a separate credentials file, for LON only, must be created.

Save this file as `.raxpub-uk` under the home folder of the user running the playbook.


## Clone the repository

On the same build node / workstation, run the following:

```
cd; git clone https://github.com/rackerlabs/ansible-dse
```


## Set the global variables

Modify the file at `~/ansible-dse/playbooks/group_vars/all` to set the cluster configuration.

The following table will describe the most important variables:

| Variable                | Description                                                                |
| ----------------------- | -------------------------------------------------------------------------- |
| cluster_name            | The name of the DSE cluster.                                               |
| dserepouser dserepopass | DSE Repository credentials (from https://academy.datastax.com/user/login). |
| opscenter_dc            | The virtual datacenter where opscenter runs. It can be on a separate datacenter or one shared with DSE nodes. If opscenter is installed in a virtual datacenter shared with DSE, it will be installed on the first DSE node. |
| allowed_external_ips    | A list of IPs allowed to connect to cluster nodes.                         |
| ssh keyfile             | The SSH keyfile that will be placed on cluster nodes at build time.        |
| ssh keyname             | The name of the SSH key. Make sure you change this if another key was previously used with the same name. |


## Set the topology

In the same file, `~/ansible-dse/playbooks/group_vars/all`, set the topology.

Set at least one datacenter, depending on how your topology looks like.

For each virtual datacenter, set the variables:

| Variable            | Description                                                               |
| ------------------- | ------------------------------------------------------------------------- |
| dc_name             | The name of the datacenter.                                               |
| workloads           | Set the workloads for the datacenter. If mixed workloads are used for that particular datacenter, add them to the list. Possible workloads are: `cassandra`, `spark`, `hadoop` and `search`. |
| group               | The group name assigned to this datacenter. Nodes part of this group are defined in the inventory file, be it dynamic (cloud) or static. |                                                                        |
| data_disks_devices  | The device name of the data disk. If it's already partitioned by default, set this variable to `[]`.  |
| listen_interface    | Interface to listen on for Cassandra inter-nodes communication.           |
| broadcast_interface | Interface to broadcast on for inter-nodes communication. Same as `listen_interface` unless multi-regions are used.  |
| rpc_interface       | Interface to listen on for client connections.                            |

If OpsCenter is to be installed on a separate node, add another datacenter, with the name to match the `opscenter_dc` previously set.

If not, set `opscenter_dc` to the `dc_name` from one of the datacenters already defined and OpsCenter will be installed on the first DSE node.

Cloud options can be set for each virtual datacenter:

| Variable    | Description                                                                                     |
| ----------- | ----------------------------------------------------------------------------------------------- |
| region      | The cloud region where nodes will be built.                                                     |
| nodes_count | The desired number of nodes to be built.                                                        |
| image       | The OS image to be used. Can be `CentOS 7 (PVHVM)` or `Ubuntu 14.04 LTS (Trusty Tahr) (PVHVM)`. |
| flavor      | [Size flavor](https://developer.rackspace.com/docs/cloud-servers/v2/developer-guide/#list-flavos-with-nova) of the nodes. Minimum `general1-8` for DSE nodes. |

If Rackspace Block Storage is to be built for Cassandra data, set the following options:

| Variable           | Description                                                                         |
| ------------------ | ----------------------------------------------------------------------------------- |
| data_disks_devices | The device name of the disk(s), usually starting with `xvde` for Rackspace Servers. |
| build_cbs          | Set to `true` to build CBS.                                                         |
| disks_size         | The size of the disk(s) in GB.                                                      |
| disks_type         | The type of the disk(s), can be `SATA` or `SSD`.                                    |


- Example topology with a single DC (OpsCenter will be installed on the first node) and Cassandra + Spark workloads.

  It will build 3 x `general1-8` nodes running CentOS7 in the `IAD` datacenter.
  
  It will also build 1 x 100GB SSD Cloud Block Storage.

  ```
  opscenter_dc: 'IAD'

  topology:
    - dc_name: IAD
      options:
        workloads:
          - cassandra
          - spark
        tokens: 64
        group: 'dse-cs-iad'
        data_disks_devices: []
        cassandra_base_path: "/var/lib/cassandra"
        listen_interface: 'eth1'
        broadcast_interface: 'eth0'
        rpc_interface: 'eth1'
        cloud:
          region: 'IAD'
          nodes_count: 3
          image: 'CentOS 7 (PVHVM)'
          flavor: 'general1-8'
        cbs:
          build_cbs: true
          disks_size: 100
          disks_type: 'SSD'
  ```

- Example topology with a single Cassandra DC and OpsCenter on a separate node / separate DC:

  ```
  opscenter_dc: 'opscenter'

  topology:
    - dc_name: IAD
      options:
        workloads:
          - cassandra
        tokens: 64
        group: 'dse-c-iad'
        data_disks_devices: []
        cassandra_base_path: "/var/lib/cassandra"
        listen_interface: 'eth1'
        broadcast_interface: 'eth0'
        rpc_interface: 'eth1'
        cloud:
          region: 'IAD'
          nodes_count: 3
          image: 'CentOS 7 (PVHVM)'
          flavor: 'general1-8'
   
    - dc_name: opscenter
      options:
        group: 'opscenter-node'
        data_disks_devices: []
        cassandra_base_path: "/var/lib/cassandra"
        listen_interface: 'eth1'
        broadcast_interface: 'eth0'
        rpc_interface: 'eth1'
        cloud:
          region: 'IAD'
          nodes_count: 1
          image: 'CentOS 7 (PVHVM)'
          flavor: 'general1-2'
  ```

- Example topology with two Cassandra DCs (one in LON for database workloads only and one in IAD for analytics workloads).

  OpsCenter is on a separate node in LON.

  ```
  opscenter_dc: 'opscenter'

  topology:
    - dc_name: LON
      options:
        workloads:
          - cassandra
        tokens: 256
        group: 'dse-c-lon'
        data_disks_devices: []
        cassandra_base_path: "/var/lib/cassandra"
        listen_interface: 'eth1'
        broadcast_interface: 'eth0'
        rpc_interface: 'eth0'
        cloud:
          region: 'LON'
          nodes_count: 3
          image: 'CentOS 7 (PVHVM)'
          flavor: 'general1-8'

    - dc_name: IAD
      options:
        workloads:
          - spark
        tokens: 16
        group: 'dse-spark-iad'
        data_disks_devices: []
        cassandra_base_path: "/var/lib/cassandra"
        listen_interface: 'eth1'
        broadcast_interface: 'eth0'
        rpc_interface: 'eth0'
        cloud:
          region: 'IAD'
          nodes_count: 1
          image: 'CentOS 7 (PVHVM)'
          flavor: 'performance2-15'

    - dc_name: opscenter
      options:
        group: 'opscenter-node'
        data_disks_devices: []
        cassandra_base_path: "/var/lib/cassandra"
        listen_interface: 'eth1'
        broadcast_interface: 'eth0'
        rpc_interface: 'eth0'
        cloud:
          region: 'LON'
          nodes_count: 1
          image: 'CentOS 7 (PVHVM)'
          flavor: 'general1-2'
  ```


## Provision the Cloud environment

The first step is to run the script that will provision the Cloud environment:.

Set the environment variables `RAX_CREDS_FILE` and `RAX_LON_CREDS_FILE` to point to the Rackspace credentials file(s) [set previously](#setup-the-rackspace-credentials-files).

```
export RAX_CREDS_FILE="/root/.raxpub"
export RAX_LON_CREDS_FILE="/root/.raxpub-uk"

cd ~/ansible-dse/ && bash provision_cloud.sh
```


## Bootstrapping

Then run the bootstrapping script that will setup the prerequisites on the cluster nodes.

Set the environment variables `RAX_CREDS_FILE` and `RAX_LON_CREDS_FILE` to point to the Rackspace credentials file(s) [set previously](#setup-the-rackspace-credentials-files).

```
export RAX_CREDS_FILE="/root/.raxpub"
export RAX_LON_CREDS_FILE="/root/.raxpub-uk"

cd ~/ansible-dse/ && bash bootstrap.sh
```


## DSE Installation

Lastly, run the following to proceed with the DSE and cluster installation.

Set the environment variables `RAX_CREDS_FILE` and `RAX_LON_CREDS_FILE` to point to the Rackspace credentials file(s) [set previously](#setup-the-rackspace-credentials-files).

```
export RAX_CREDS_FILE="/root/.raxpub"
export RAX_LON_CREDS_FILE="/root/.raxpub-uk"

cd ~/ansible-dse/ && bash dse.sh
```


## Login to OpsCenter

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


---


# Install DSE on existing devices


## Build setup

First step is to setup the build node / workstation.

This build node or workstation will run the Ansible code and build the DSE cluster (itself can be a DSE or OpsCenter node).

This node needs to be able to contact the cluster devices via SSH.

All the SSH logins must be known / prepared in advance or alternative SSH public-key authentication can also be used.

The following steps must be followed to install Ansible and the prerequisites on this build node / workstation, depending on its operating system:

### CentOS/RHEL 6

Install Ansible and git:

```
sudo su -
yum install http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
yum repolist; yum install python-pip python-devel sshpass git vim-enhanced -y
pip install ansible
```

### CentOS/RHEL 7

Install Ansible and git:

```
sudo su -
yum install https://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
yum repolist; yum install python-pip python-devel sshpass git vim-enhanced -y
pip install ansible
```

### Ubuntu 14+ / Debian 8

Install Ansible and git:

```
sudo su -
apt-get update; apt-get -y install python-pip python-dev sshpass git vim
pip install ansible
```


## Clone the repository

On the same build node / workstation, run the following:

```
cd; git clone https://github.com/rackerlabs/ansible-dse
```


## Set the global variables

Modify the file at `~/ansible-dse/playbooks/group_vars/all` to set the cluster configuration.

The following table will describe the most important variables:

| Variable                | Description                                                                   |
| ----------------------- | ----------------------------------------------------------------------------- |
| cluster_name            | The name of the DSE cluster.                                                  |
| dserepouser dserepopass | DSE Repository credentials (from https://academy.datastax.com/user/login).    |
| opscenter_dc            | The virtual datacenter where opscenter runs. It can be on a separate datacenter or one shared with DSE nodes. If opscenter is installed in a virtual datacenter shared with DSE, it will be installed on the first DSE node. |


## Set the topology

In the same file, `~/ansible-dse/playbooks/group_vars/all`, set the topology.

Set at least one datacenter, depending on how your topology looks like.

For each virtual datacenter, set the variables:

| Variable            | Description                                                               |
| ------------------- | ------------------------------------------------------------------------- |
| dc_name             | The name of the datacenter.                                               |
| workloads           | Set the workloads for the datacenter. If mixed workloads are used for that particular datacenter, add them to the list. Possible workloads are: `cassandra`, `spark`, `hadoop` and `search`. |
| group               | The group name assigned to this datacenter. Nodes part of this group are defined in the inventory file, be it dynamic (cloud) or static. |                                                                        |
| data_disks_devices  | The device name of the data disk. If it's already partitioned by default, set this variable to `[]`.  |
| listen_interface    | Interface to listen on for Cassandra inter-nodes communication.           |
| broadcast_interface | Interface to broadcast on for inter-nodes communication. Same as `listen_interface` unless multi-regions are used.  |
| rpc_interface       | Interface to listen on for client connections.                            |

If OpsCenter is to be installed on a separate node, add another datacenter, with the name to match the `opscenter_dc` previously set.

If not, set `opscenter_dc` to the `dc_name` from one of the datacenters already defined and OpsCenter will be installed on the first DSE node.


- Example topology with a single DC (OpsCenter will be installed on the first node) and Cassandra + Spark workloads:

  ```
  opscenter_dc: 'LON5'

  topology:
    - dc_name: LON5
      options:
        workloads:
          - cassandra
          - spark
        tokens: 64
        group: 'dse-cs-lon5'
        data_disks_devices: ['sdb']
        cassandra_base_path: "/var/lib/cassandra"
        listen_interface: 'bond0'
        broadcast_interface: 'bond0'
        rpc_interface: 'bond0'
  ```

- Example topology with a single Cassandra DC and OpsCenter on a separate node:

  ```
  opscenter_dc: 'opscenter'
  
  topology:
    - dc_name: LON5
      options:
        workloads:
          - cassandra
        tokens: 64
        group: 'dse-c-lon5'
        data_disks_devices: ['sdb']
        cassandra_base_path: "/var/lib/cassandra"
        listen_interface: 'bond0'
        broadcast_interface: 'bond0'
        rpc_interface: 'bond0'
   
    - dc_name: opscenter
      options:
        group: 'opscenter-node'
        data_disks_devices: []
        cassandra_base_path: "/var/lib/cassandra"
        listen_interface: 'bond0'
        broadcast_interface: 'bond0'
        rpc_interface: 'bond0'
  ```


## Set the inventory

Modify the inventory file at `~/ansible-dse/inventory/static` to match the cluster layout and the topology.

In here, you'll use the same groups as defined previously in the topology and assign nodes to these groups.

- For each node, set the `ansible_host` to the IP address that is reachable from the build node / workstation.

- Then set `ansible_user=root` and `ansible_ssh_pass` if the node allows for root user logins. If these are not set, public-key authentication will be used.

- If root logins are not allowed then sudo can be used, set `ansible_user` to a user that can sudo.

- Nodes can be placed in different racks / cabinets, use `rack_name` to set the node's rack. 

- Example inventory with a single group/DC (OpsCenter will be installed on the first node - `dse01`) and two racks:

  ```
  [dse-cs-lon5]
  dse01 ansible_host=127.0.0.1 rack_name=RAC1 ansible_user=root ansible_ssh_pass=AsdQwe123
  dse02 ansible_host=127.0.0.2 rack_name=RAC1 ansible_user=root ansible_ssh_pass=AsdQwe123
  dse03 ansible_host=127.0.0.3 rack_name=RAC2 ansible_user=root ansible_ssh_pass=AsdQwe123
  ```

- Example inventory with a single Cassandra group/DC and OpsCenter on a separate group/node:

  ```
  [dse-c-lon5]
  dse01 ansible_host=127.0.0.1 rack_name=RAC1 ansible_user=root ansible_ssh_pass=AsdQwe123
  dse02 ansible_host=127.0.0.2 rack_name=RAC1 ansible_user=root ansible_ssh_pass=AsdQwe123
  dse03 ansible_host=127.0.0.3 rack_name=RAC1 ansible_user=root ansible_ssh_pass=AsdQwe123
   
  [opscenter-node]
  ops01 ansible_host=127.1.0.1 ansible_user=root ansible_ssh_pass=AsdQwe123
  ```


## Bootstrapping

The first step is to run the bootstrapping script that will setup the prerequisites on the cluster nodes.

```
cd ~/ansible-dse/ && bash bootstrap.sh
```


## DSE Installation

Then run the following to proceed with the DSE and cluster installation:

```
cd ~/ansible-dse/ && bash dse.sh
```


## Login to OpsCenter

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
