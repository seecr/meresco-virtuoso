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

from simplejson import loads
from urllib import urlencode
from urllib2 import urlopen, Request
from time import time
from threading import Thread

from weightless.core import compose

from seecr.test.utils import getRequest, postRequest
from seecr.test.integrationtestcase import IntegrationTestCase

from meresco.triplestore import HttpClient, MalformedQueryException, InvalidRdfXmlException
from os.path import join


class VirtuosoTest(IntegrationTestCase):
    def testOne(self):
        result = urlopen("http://localhost:%s/query?%s" % (self.virtuosoPort, urlencode(dict(query='SELECT ?x WHERE {}')))).read()
        self.assertTrue('"vars" : [ "x" ]' in result, result)

    def testAddTripleThatsNotATriple(self):
        client = HttpClient(host='localhost', port=self.virtuosoPort, synchronous=True)
        try:
            list(compose(client.addTriple('uri:subject', 'uri:predicate', '')))
            self.fail("should not get here")
        except ValueError, e:
            self.assertEquals('java.lang.IllegalArgumentException: Not a triple: "uri:subject|uri:predicate|"', str(e))

    def testAddInvalidRdf(self):
        client = HttpClient(host='localhost', port=self.virtuosoPort, synchronous=True)
        try:
            list(compose(client.add('uri:identifier', '<invalidRdf/>')))
            self.fail("should not get here")
        except InvalidRdfXmlException, e:
            self.assertTrue('org.openrdf.rio.RDFParseException: Not a valid (absolute) URI: #invalidRdf [line 1, column 14]' in str(e), str(e))

    def testAddInvalidIdentifier(self):
        client = HttpClient(host='localhost', port=self.virtuosoPort, synchronous=True)
        try:
            list(compose(client.add('identifier', '<ignore/>')))
            self.fail("should not get here")
        except ValueError, e:
            self.assertEquals('java.lang.IllegalArgumentException: Not a valid (absolute) URI: identifier', str(e))

    def testInvalidSparql(self):
        client = HttpClient(host='localhost', port=self.virtuosoPort, synchronous=True)
        try:
            list(compose(client.executeQuery("""select ?x""")))
        except MalformedQueryException, e:
            self.assertTrue(str(e).startswith('org.openrdf.query.MalformedQueryException: Encountered "<EOF>"'), str(e))

    def testDeleteRecord(self):
        postRequest(self.virtuosoPort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:testDelete</rdf:type>
        </rdf:Description>
    </rdf:RDF>""", parse=False)
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(1, len(json['results']['bindings']))

        postRequest(self.virtuosoPort, "/update?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:testDeleteUpdated</rdf:type>
        </rdf:Description>
    </rdf:RDF>""", parse=False)
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(0, len(json['results']['bindings']))
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDeleteUpdated"}')
        self.assertEquals(1, len(json['results']['bindings']))

        postRequest(self.virtuosoPort, "/delete?identifier=uri:record", "", parse=False)
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(0, len(json['results']['bindings']))
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDeleteUpdated"}')
        self.assertEquals(0, len(json['results']['bindings']))

        postRequest(self.virtuosoPort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:testDelete</rdf:type>
        </rdf:Description>
    </rdf:RDF>""", parse=False)
        json = self.query('SELECT ?x WHERE {?x ?y "uri:testDelete"}')
        self.assertEquals(1, len(json['results']['bindings']))

    def testAddAndRemoveTriple(self):
        json = self.query('SELECT ?obj WHERE { <uri:subject> <uri:predicate> ?obj }')
        self.assertEquals(0, len(json['results']['bindings']))

        header, body = postRequest(self.virtuosoPort, "/addTriple", "uri:subject|uri:predicate|uri:object", parse=False)
        self.assertTrue("200" in header, header)

        json = self.query('SELECT ?obj WHERE { <uri:subject> <uri:predicate> ?obj }')
        self.assertEquals(1, len(json['results']['bindings']))

        header, body = postRequest(self.virtuosoPort, "/removeTriple", "uri:subject|uri:predicate|uri:object", parse=False)
        self.assertTrue("200" in header, header)
        json = self.query('SELECT ?obj WHERE { <uri:subject> <uri:predicate> ?obj }')
        self.assertEquals(0, len(json['results']['bindings']))

    def testAddPerformance(self):
        totalTime = 0
        try:
            for i in range(10):
                postRequest(self.virtuosoPort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <rdf:Description>
                <rdf:type>uri:testFirst%s</rdf:type>
            </rdf:Description>
        </rdf:RDF>""" % i, parse=False)
            number = 1000
            for i in range(number):
                start = time()
                postRequest(self.virtuosoPort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <rdf:Description>
                <rdf:type>uri:testSecond%s</rdf:type>
            </rdf:Description>
        </rdf:RDF>""" % i, parse=False)
                totalTime += time() - start

            self.assertTiming(0.001, totalTime / number, 0.010)
        finally:
            postRequest(self.virtuosoPort, "/delete?identifier=uri:record", "")

    def testAddPerformanceInCaseOfThreads(self):
        number = 25
        threads = []
        responses = []
        try:
            for i in range(number):
                def doAdd(i=i):
                    header, body = postRequest(self.virtuosoPort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <rdf:Description>
                <rdf:type>uri:testSecond%s</rdf:type>
            </rdf:Description>
        </rdf:RDF>""" % i, parse=False)
                    responses.append((header, body))
                threads.append(Thread(target=doAdd))

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            for header, body in responses:
                self.assertTrue('200 OK' in header, header + '\r\n\r\n' + body)
        finally:
            postRequest(self.virtuosoPort, "/delete?identifier=uri:record", "")

    def testAcceptHeaders(self):
        postRequest(self.virtuosoPort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description>
            <rdf:type>uri:test:acceptHeaders</rdf:type>
        </rdf:Description>
    </rdf:RDF>""", parse=False)

        request = Request('http://localhost:%s/query?%s' % (self.virtuosoPort, urlencode({'query': 'SELECT ?x WHERE {?x ?y "uri:test:acceptHeaders"}'})), headers={"Accept" : "application/xml"})
        contents = urlopen(request).read()
        self.assertTrue("<binding name='x'>" in contents, contents)

        headers, body = getRequest(self.virtuosoPort, "/query", arguments={'query': 'SELECT ?x WHERE {?x ?y "uri:test:acceptHeaders"}'}, additionalHeaders={"Accept" : "image/jpg"}, parse=False)

        self.assertEquals(["HTTP/1.1 406 Not Acceptable", "Content-type: text/plain"], headers.split('\r\n')[:2])
        self.assertEqualsWS("""Supported formats:
- SPARQL/XML (mimeTypes=application/sparql-results+xml, application/xml; ext=srx, xml)
- BINARY (mimeTypes=application/x-binary-rdf-results-table; ext=brt)
- SPARQL/JSON (mimeTypes=application/sparql-results+json, application/json; ext=srj, json)
- SPARQL/CSV (mimeTypes=text/csv; ext=csv)
- SPARQL/TSV (mimeTypes=text/tab-separated-values; ext=tsv)""", body)

    def testMimeTypeArgument(self):
        postRequest(self.virtuosoPort, "/add?identifier=uri:record", """<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description rdf:about="uri:test:mimeType">
            <rdf:value>Value</rdf:value>
        </rdf:Description>
    </rdf:RDF>""", parse=False)

        request = Request('http://localhost:%s/query?%s' % (self.virtuosoPort, urlencode({'query': 'SELECT ?x WHERE {?x ?y "Value"}', 'mimeType': 'application/sparql-results+xml'})))
        contents = urlopen(request).read()
        self.assertEqualsWS("""<?xml version='1.0' encoding='UTF-8'?>
<sparql xmlns='http://www.w3.org/2005/sparql-results#'>
    <head>
        <variable name='x'/>
    </head>
    <results>
        <result>
            <binding name='x'>
                <uri>uri:test:mimeType</uri>
            </binding>
        </result>
    </results>
</sparql>""", contents)

    def testBatchUpload(self):
        with open(join(self.bulkLoadDir, "test.rdf"), 'w') as f:
            f.write("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description>
        <rdf:type>uri:testBatchUpload</rdf:type>
    </rdf:Description>
</rdf:RDF>""")
        self.runBatchUpload(graph="uri:example.org")
        json = self.query('SELECT ?s WHERE { ?s ?p "uri:testBatchUpload" }')
        self.assertEquals(1, len(json['results']['bindings']))

        with open(join(self.bulkLoadDir, "test2.rdf"), 'w') as f:
            f.write("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description>
        <rdf:type>uri:testBatchUpload2</rdf:type>
    </rdf:Description>
</rdf:RDF>""")
        self.runBatchUpload(graph="uri:example.org")
        json = self.query('SELECT ?s WHERE { ?s ?p "uri:testBatchUpload" }')
        self.assertEquals(1, len(json['results']['bindings']))
        json = self.query('SELECT ?s WHERE { ?s ?p "uri:testBatchUpload2" }')
        self.assertEquals(1, len(json['results']['bindings']))


    def query(self, query):
        return loads(urlopen('http://localhost:%s/query?%s' % (self.virtuosoPort,
            urlencode(dict(query=query)))).read())

