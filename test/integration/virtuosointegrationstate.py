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

from os import system
from os.path import join, dirname, abspath

from seecr.test.integrationtestcase import IntegrationState
from seecr.test.portnumbergenerator import PortNumberGenerator


myDir = dirname(abspath(__file__))
serverBinDir = join(dirname(dirname(myDir)), 'bin')

class VirtuosoIntegrationState(IntegrationState):
    def __init__(self, stateName, tests=None, fastMode=False):
        IntegrationState.__init__(self, stateName=stateName, tests=tests, fastMode=fastMode)

        self.virtuosoDataDir = join(self.integrationTempdir, 'virtuoso-data')
        self.bulkLoadDir = join(self.integrationTempdir, 'bulk-load-data')
        self.virtuosoPort = PortNumberGenerator.next()
        self.odbcPort = PortNumberGenerator.next()
        self.httpPort = PortNumberGenerator.next()
        self.testdataDir = join(dirname(myDir), 'data')
        if not fastMode:
            system('rm -rf ' + self.integrationTempdir)
            system('mkdir --parents ' + self.virtuosoDataDir)

    def setUp(self):
        self.startVirtuosoServer()
        self.startVirtuoso()

    def binDir(self):
        return serverBinDir

    def startVirtuoso(self):
        self._startServer('virtuoso', self.binPath('start-virtuoso'), 'http://localhost:%s/query' % self.virtuosoPort, port=self.virtuosoPort, stateDir=self.virtuosoDataDir, hostname="localhost", odbcPort=self.odbcPort, username="dba", password="dba")

    def startVirtuosoServer(self):
        self._startServer('virtuoso-server', self.binPath('start-virtuoso-server'), 'http://localhost:%s/sparql' % self.httpPort, stateDir=self.virtuosoDataDir, bulkLoadDir=self.bulkLoadDir, odbcPort=self.odbcPort, httpPort=self.httpPort)

    def restartVirtuoso(self):
        self.stopVirtuoso()
        self.startVirtuoso()

    def stopVirtuoso(self):
        self._stopServer('virtuoso')

    def runBatchUpload(self, graph):
        self._runExecutable(self.binPath('virtuoso-batch-upload'), bulkLoadDir=self.bulkLoadDir, odbcPort=self.odbcPort, graph=graph)

