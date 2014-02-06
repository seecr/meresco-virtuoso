#!/bin/bash
## begin license ##
#
# The Meresco Virtuoso package is an Virtuoso Triplestore based on meresco-triplestore
#
# Copyright (C) 2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Meresco Virtuoso"
#
# "Meresco Virtuoso" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Virtuoso" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Virtuoso"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

source /usr/share/seecr-tools/functions.d/default
source /usr/share/seecr-tools/functions.d/svc
source /usr/share/seecr-tools/functions.d/user

mydir=$(cd $(dirname $0); pwd)
bindir=$(dirname $mydir)/bin
javadir=$(find /usr/lib/jvm/ -name 'java' | grep -E 'java-(1\.)?6' | grep jre | head -n1 | xargs dirname)
USERNAME=$(stat -c %U $0)
GROUPNAME=$(user_groupname $USERNAME)

triplestorePort=9010
stateDirBase=/data/meresco-virtuoso-state
SERVICEDIR=/data/meresco-virtuoso-services
test -d $stateDirBase || mkdir -p $stateDirBase
chown $USERNAME:$GROUPNAME $stateDirBase

runscript="
ulimit -n 100000
export JAVA_BIN=$javadir
cd $bindir
exec /usr/bin/setuidgid $USERNAME ./start-virtuoso \\
    --port=$triplestorePort \\
    --stateDir=${stateDirBase}/virtuoso \\
    --hostname=localhost \\
    --odbcPort=1111 \\
    --username=dba \\
    --password=dba 2>&1
"
SERVICE_NAME=virtuoso
svc_assert_service_down /etc/service/$SERVICE_NAME
svc_create_service $USERNAME $GROUPNAME $SERVICEDIR "" $SERVICE_NAME "${runscript}"
svc_prepare_service $SERVICEDIR $SERVICE_NAME


runscript="
ulimit -n 100000
cd $bindir
exec /usr/bin/setuidgid $USERNAME ./start-virtuoso-server \\
        ${stateDirBase}/virtuoso-server 2>&1
"
SERVICE_NAME=virtuoso-server
svc_assert_service_down /etc/service/$SERVICE_NAME
svc_create_service $USERNAME $GROUPNAME $SERVICEDIR "" $SERVICE_NAME "${runscript}"
svc_prepare_service $SERVICEDIR $SERVICE_NAME