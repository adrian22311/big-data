#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source "/vagrant/scripts/common.sh"

echo 'Adding NIFI properties files to configuration'

sudo sed -i "s#nifi.variable.registry.properties=.*#nifi.variable.registry.properties=${SCRIPT_DIR}/config/nifi_custom_properties.properties#g" ${NIFI_HOME}/conf/nifi.properties


echo 'Initializing apps (reseting nifi just in case it is already started with old config file)'

source "/vagrant/scripts/common.sh"

${NIFI_HOME}/bin/nifi.sh stop

echo 'sudo /vagrant/scripts/bootstrap.sh'
sudo /vagrant/scripts/bootstrap.sh 