FROM ubuntu:bionic as builder

#SHELL ["/bin/bash", "-c"]

RUN echo 'APT::Install-Recommends 0;' >> /etc/apt/apt.conf.d/01norecommends \
    && echo 'APT::Install-Suggests 0;' >> /etc/apt/apt.conf.d/01norecommends \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y bash mysql-client vim.tiny wget sudo net-tools ca-certificates unzip apt-transport-https \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-dev python3-pip libmysqlclient-dev libxml2-dev libxslt-dev libffi-dev gcc libssl-dev gettext \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs node-gyp npm ruby nginx \
    && pip3 install --upgrade pip \
    && npm install -g less@2.7.1 \
    && npm install -g yuglify@0.1.4 \
    && gem install sass -v 3.4.22

WORKDIR /app
ADD . .

RUN export PATH=$PATH:/usr/bin/ \
    && export PATH=$PATH:/usr/local/bin/

RUN pip3 install --upgrade setuptools \
    && pip3 install -r requirements.txt \
    && apt-get install -y libmysqlclient-dev

RUN cp ./nginx/default.site-example /etc/nginx/sites-available/default \
    && cp ./frontend/frontend/settings.py.example ./frontend/frontend/settings.py

RUN cd /var/lib/gems/2.5.0/gems/sass-3.4.22/lib/sass/ \
    && sed -i "s/when\ Fixnum/when\ Integer/" util.rb

#WORKDIR ./frontend
RUN chmod +x ./wait-for-it.sh

#ENTRYPOINT ["/bin/bash", "start.sh"]
