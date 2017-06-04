FROM alpine
MAINTAINER Kevin Patel <kevin@ductrix.com>

RUN mkdir /etc/ansible/
RUN echo '[servers]' > /etc/ansible/hosts
RUN apk update 
RUN apk add --no-cache bash git openssh supervisor curl nginx uwsgi uwsgi-python py-pip
RUN pip install --upgrade pip
RUN pip install flask

# Directory for ansible

# Make ssh dir

# since root is empty anyways
RUN chmod 777 /root/
RUN mkdir /root/.ssh/
RUN ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa -q -N ""


# Copy over private key, and set permissions
ADD repo_key /root/.ssh/repo_key
RUN chmod 600 /root/.ssh/repo_key


# Create known_hosts RUN touch /root/.ssh/known_hosts 
# Add bitbuckets key
RUN ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts


# Install psycopg2 and other packages 
RUN apk add --virtual build-deps gcc python-dev musl-dev libffi-dev libxml2 libxml2-dev libxslt-dev \ 
  && apk add postgresql-dev \
  && pip install psycopg2 \
  && pip install sqlalchemy \
  && pip install uuid \
  && pip install ConfigParser \
  && pip install Crypto \
  && pip install datetime \
  && pip install rq \
  && pip install redis \
  && pip install ansible\
  && pip install ansible-vault\
  && pip install pyvmomi\
  && pip install pysphere\
  && pip install tools\
  && apk del build-deps


# application folder
ENV APP_DIR /app

# app dir
#RUN mkdir ${APP_DIR} \
#	&& chown -R nginx:nginx ${APP_DIR} \
#	&& chmod 755 /run/ -R 
#	&& chmod 755 /root/ -R
VOLUME [${APP_DIR}]
WORKDIR ${APP_DIR}

# expose web server port
# only http, for ssl use reverse proxy
EXPOSE 443

# copy config files into filesystem
COPY nginx.conf /etc/nginx/nginx.conf
COPY app.ini /app.ini
COPY entrypoint.sh /entrypoint.sh

# Clone the conf files into the docker container
RUN ssh-agent bash -c 'ssh-add /root/.ssh/repo_key; git clone git@bitbucket.org:ketul917/ductrix-src.git /var/ductrix/'
RUN ssh-agent bash -c 'ssh-add /root/.ssh/repo_key; git clone git@bitbucket.org:ketul917/ductrix-images.git /var/ductrix-images'
RUN cp /var/ductrix/src/ansible.cfg /etc/ansible/

# exectute start up script
ENTRYPOINT ["/entrypoint.sh"]
