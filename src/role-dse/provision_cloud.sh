#!/bin/bash

RAX_CREDS_FILE=${RAX_CREDS_FILE:-"${HOME}/.raxpub"}
RAX_LON_CREDS_FILE=${RAX_LON_CREDS_FILE:-"${HOME}/.raxpub-uk"}

if [ -n "${RAX_CREDS_FILE}" ] && [ -f "${RAX_CREDS_FILE}" ]
then
  echo "Rackspace Cloud (non-LON) will be used."
  EXTRA_VARS="${EXTRA_VARS} credentials_file=$RAX_CREDS_FILE"
else
  echo "Rackspace Cloud (non-LON) will not be used."
fi

if [ -n "${RAX_LON_CREDS_FILE}" ] && [ -f "${RAX_LON_CREDS_FILE}" ]
then
  echo "Rackspace Cloud (LON) will be used."
  EXTRA_VARS="${EXTRA_VARS} credentials_file_lon=$RAX_LON_CREDS_FILE"
else
  echo "Rackspace Cloud (LON) will not be used."
fi

ansible-playbook -i inventory/localhost -e "$EXTRA_VARS" playbooks/provision_cloud.yml
