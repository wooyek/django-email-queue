#!/usr/bin/env bash

#
# This script presumes that you have PostgreSQL setup and running
# If you need GIS support please you'll need a one time server setup
# Please take a look at https://github.com/wooyek/docker-geodjango/blob/master/docker-entrypoint.sh
#

echo "------> Creating user ${DATABASE_USER}"
sudo -u postgres -E sh -c 'createuser ${DATABASE_USER}'
sudo -u postgres -E psql -c "ALTER USER \"${DATABASE_USER}\" PASSWORD '${DATABASE_PASSWORD}';"

echo "------> Creating databases ${DATABASE_NAME} and ${DATABASE_TEST_NAME}"
sudo -u postgres -E sh -c 'createdb ${DATABASE_NAME}'
sudo -u postgres -E sh -c 'createdb ${DATABASE_TEST_NAME}'


