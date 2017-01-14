#!/bin/bash

RAX_CREDS_FILE=${RAX_CREDS_FILE:-"${HOME}/.raxpub"}
RAX_LON_CREDS_FILE=${RAX_LON_CREDS_FILE:-"${HOME}/.raxpub-uk"}
RAX_REGION=ALL
VARS="${VARS} ANSIBLE_SCP_IF_SSH=y ANSIBLE_HOST_KEY_CHECKING=False"

if [ -n "${RAX_CREDS_FILE}" ] && [ -f "${RAX_CREDS_FILE}" ]
then
  echo "Rackspace Cloud (non-LON) will be used."
  VARS="${VARS} RAX_CREDS_FILE=${RAX_CREDS_FILE}"
  \mv inventory/rax.py.bak inventory/rax.py 2> /dev/null
else
  echo "Rackspace Cloud (non-LON) will not be used."
  \mv inventory/rax.py inventory/rax.py.bak 2> /dev/null
fi

if [ -n "${RAX_LON_CREDS_FILE}" ] && [ -f "${RAX_LON_CREDS_FILE}" ]
then
  echo "Rackspace Cloud (LON) will be used."
  VARS="${VARS} RAX_LON_CREDS_FILE=${RAX_LON_CREDS_FILE}"
  \mv inventory/rax-lon.py.bak inventory/rax-lon.py 2> /dev/null
else
  echo "Rackspace Cloud (LON) will not be used."
  \mv inventory/rax-lon.py inventory/rax-lon.py.bak 2> /dev/null
fi

export $VARS
ansible-playbook -f 20 -i inventory/ playbooks/bootstrap.yml
