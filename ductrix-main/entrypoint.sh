#!/bin/bash

ssh-agent bash -c 'ssh-add /root/.ssh/repo_key; cd /var/ductrix;  git pull'
cp /var/ductrix/src/ansible.cfg /etc/ansible/ansible.cfg
supervisord --config /var/ductrix/web/supervisord.conf

if [ "$1" == "-d" ]; then
	echo "Running app in debug mode!"
	python /var/ductrix/web/app.py
else
	echo "Running app in production mode!"
	nginx && uwsgi --ini /app.ini
fi
