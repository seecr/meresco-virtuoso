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

set -o errexit

echo "Please verify you have installed:
  git patch autoconf automake libtool flex bison gperf gawk m4 make openssl-devel java-1.6.0-openjdk-devel"""
echo "Press enter to continue"
read

javac -version 2>&1 | grep 1.6 > /dev/null || echo "javac should be java 6"

# git clone git://git.code.sf.net/p/virtuoso/virtuoso-opensource
cd virtuoso-opensource
git checkout v7.0.0

./autogen.sh
CFLAGS="-O2 -m64"
export CFLAGS
./configure

cat <<EOF | patch -p0
--- binsrc/sesame2/virtuoso_driver/VirtuosoRepositoryConnection.java    2014-01-08 14:19:47.647022290 +0100
+++ binsrc/sesame2/virtuoso_driver/VirtuosoRepositoryConnection.java.new    2014-01-08 14:19:41.038916571 +0100
@@ -2723,6 +2723,7 @@
			}
			catch (Exception e)
			{
+				e.printStackTrace();
			    throw createException(e);
			}
		}
@@ -2836,7 +2836,9 @@
				String col = rsmd.getColumnName(i);
				Object val = v_rs.getObject(i);
				Value v = castValue(val);
-				((QueryBindingSet)v_row).setBinding(col, v);
+				if (v != null) {
+					((QueryBindingSet)v_row).setBinding(col, v);
+				}
			}
		}
	}
EOF

cd binsrc/sesame2
mkdir lib
wget http://www.slf4j.org/dist/slf4j-1.6.1.tar.gz
tar xzf slf4j-1.6.1.tar.gz
cp slf4j-1.6.1/slf4j-api-1.6.1.jar lib
cp slf4j-1.6.1/slf4j-simple-1.6.1.jar lib
rm -rf slf4j-1.6.1 slf4j-1.6.1.tar.gz
(cd lib; wget http://downloads.sourceforge.net/project/sesame/Sesame%202/2.7.3/openrdf-sesame-2.7.3-onejar.jar)

JAVAC=/usr/bin/javac
export JAVAC
JAR=/usr/bin/jar
export JAR
make virt_sesame2.jar

cd ../../..
cp virtuoso-opensource/binsrc/sesame2/virt_sesame2.jar ../jars
cp virtuoso-opensource/libsrc/JDBCDriverType4/virtjdbc4.jar ../jars
rm -rf virtuoso-opensource