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

export LANG=en_US.UTF-8
export PYTHONPATH=.:$PYTHONPATH
pycmd="python2.6"
if [ -e /usr/bin/python2.7 ]; then
    pycmd="python2.7"
fi
option=$1
if [ "${option:0:10}" == "--python2." ]; then
    shift
    pycmd="${option:2}"
fi
echo Using Python version: $pycmd
echo "================ $pycmd _integrationtest.py $@ ================"
$pycmd _integrationtest.py "$@"
