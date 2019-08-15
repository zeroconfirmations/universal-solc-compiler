####################################################################################################
#                                                                                                  #
# (c) 2018 Quantstamp, Inc. All rights reserved.  This content shall not be used, copied,          #
# modified, redistributed, or otherwise disseminated except to the extent expressly authorized by  #
# Quantstamp for credentialed users. This content and its use are governed by the Quantstamp       #
# Demonstration License Terms at <https://s3.amazonaws.com/qsp-protocol-license/LICENSE.txt>.                                                    #
#                                                                                                  #
####################################################################################################

FROM docker:dind
# for "Docker-in-Docker" support

# the following steps are based on https://hub.docker.com/r/frolvlad/alpine-python3/
RUN apk add --no-cache python3 && \
  python3 -m ensurepip && \
  rm -r /usr/lib/python*/ensurepip && \
  pip3 install --upgrade pip setuptools && \
  if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
  if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
  rm -r /root/.cache

RUN apk add --no-cache libtool
RUN apk add vim

# Install solc
## Create solc-versions directory
RUN mkdir /usr/local/bin/solc-versions

# Create a directory to host testing files
RUN mkdir ./app
WORKDIR ./app
COPY . .

RUN chmod +x run_tests
# Install pip requirements for usolc
RUN pip3 install -r requirements.txt

# usolc setup
# Running the solc download
RUN chmod +x ./usolc/solc_download
RUN ./usolc/solc_download

# Copying usolc scripts
RUN cp ./usolc/usolc.py /usr/local/bin/solc-versions/usolc.py
RUN cp -r ./usolc/exceptions /usr/local/bin/solc-versions/exceptions
RUN cp ./usolc/solc_version_list /usr/local/bin/solc-versions/solc_version_list
RUN cp ./usolc/solc /usr/local/bin/solc
RUN chmod +x /usr/local/bin/solc
