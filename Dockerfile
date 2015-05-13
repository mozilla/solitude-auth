# This is designed to be run from fig as part of a
# Marketplace development environment.

# NOTE: this is not provided for production usage.
FROM mozillamarketplace/centos-mysql-mkt:0.2

RUN yum install -y supervisor
RUN yum install -y bash-completion

RUN mkdir -p /pip/{cache,build}
ADD requirements /pip/requirements
WORKDIR /pip
# Download this securely from pyrepo first.
RUN pip install --no-deps --find-links https://pyrepo.addons.mozilla.org/ peep
RUN peep install \
    --build /pip/build \
    --download-cache /pip/cache \
    --no-deps \
    -r /pip/requirements/dev.txt \
    --find-links https://pyrepo.addons.mozilla.org/

# Ship the source in the container, its up to docker-compose to override it
# if it wants to.
COPY . /srv/auth

EXPOSE 2603

# Preserve bash history across image updates.
# This works best when you link your local source code
# as a volume.
ENV HISTFILE /srv/auth/docker/bash_history
# Configure bash history.
ENV HISTSIZE 50000
ENV HISTIGNORE ls:exit:"cd .."
# This prevents dupes but only in memory for the current session.
ENV HISTCONTROL erasedups
