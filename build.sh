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

VERSION=$1

javac -version 2>&1 | grep 1.6 > /dev/null || echo "javac should be java 6"; exit 1

MERESCO_TRIPLESTORE_JARS=$(test -d /usr/share/java/meresco-triplestore && find /usr/share/java/meresco-triplestore -type f -name "*.jar")
MERESCO_TRIPLESTORE_JARS=$(find -L deps.d/* -type f -name "*.jar") # DO_NOT_DISTRIBUTE
JARS=$(find jars -type f -name "*.jar")

BUILDDIR=./build
TARGET=meresco-virtuoso.jar
if [ "${VERSION}" != "" ]; then
    TARGET=meresco-virtuoso-${VERSION}.jar
fi

test -d $BUILDDIR && rm -r $BUILDDIR
mkdir $BUILDDIR

CP="$(echo $JARS | tr ' ' ':'):$(echo $MERESCO_TRIPLESTORE_JARS | tr ' ' ':')"

javaFiles=$(find src/java -name "*.java")
javac -d $BUILDDIR -cp $CP $javaFiles
if [ "$?" != "0" ]; then
    echo "Build failed"
    exit 1
fi

jar -cf $TARGET -C $BUILDDIR org

