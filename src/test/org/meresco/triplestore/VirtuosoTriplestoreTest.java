/* begin license *
 *
 * The Meresco Owlim package consists out of a HTTP server written in Java that
 * provides access to an Owlim Triple store, as well as python bindings to
 * communicate as a client with the server.
 *
 * Copyright (C) 2014 Seecr (Seek You Too B.V.) http://seecr.nl
 *
 * This file is part of "Meresco Owlim"
 *
 * "Meresco Owlim" is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * "Meresco Owlim" is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with "Meresco Owlim"; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * end license */

package org.meresco.triplestore;

import java.io.File;
import java.util.List;

import org.junit.Test;
import org.junit.Before;
import org.junit.After;
import static org.junit.Assert.*;

import static org.meresco.triplestore.Utils.createTempDirectory;
import static org.meresco.triplestore.Utils.deleteDirectory;

import org.openrdf.repository.RepositoryResult;
import org.openrdf.model.Statement;
import org.openrdf.model.impl.URIImpl;
import org.openrdf.model.impl.LiteralImpl;
import org.openrdf.query.resultio.TupleQueryResultFormat;

public class VirtuosoTriplestoreTest {
    Triplestore ts;
    File tempdir;

    @Before
    public void setUp() throws Exception {
        tempdir = createTempDirectory();
        ts = new VirtuosoTriplestore(tempdir, "localhost", 1111, "dba", "dba");
    }

    @After
    public void tearDown() throws Exception {
        deleteDirectory(tempdir);
    }

    @Test
    public void testAddRemoveTriple() throws Exception {
        long startingPoint = ts.size();
        ts.addTriple("uri:subj|uri:pred|uri:obj");
        assertEquals(startingPoint + 1, ts.size());
        ts.removeTriple("uri:subj|uri:pred|uri:obj");
        assertEquals(startingPoint, ts.size());
    }

    @Test
    public void testDelete() throws Exception {
        ts.add("uri:id0", rdf);
        long startingPoint = ts.size();
        ts.delete("uri:id0");
        assertEquals(startingPoint - 2, ts.size());
    }

    @Test
    public void testSparql() throws Exception {
        String answer = null;

        ts.add("uri:id0", rdf);
        try {
            answer = ts.executeQuery("SELECT ?x ?y ?z WHERE {?x ?y ?z}", TupleQueryResultFormat.JSON);
            assertTrue(answer.indexOf("\"value\" : \"A.M. Özman Yürekli\"") > -1);
            assertTrue(answer.endsWith("\n}"));
        } finally {
            ts.delete("uri:id0");
        }
    }

    @Test
    public void testSparqlWithNonMatchingOptional() throws Exception {
        String answer = null;

        ts.add("uri:id0", rdf);
        try {
            answer = ts.executeQuery("SELECT ?x ?y ?z ?b WHERE {?x ?y ?z . OPTIONAL { ?y ?a ?b }}", TupleQueryResultFormat.JSON);
            assertTrue(answer.indexOf("\"value\" : \"A.M. Özman Yürekli\"") > -1);
            assertTrue(answer.endsWith("\n}"));
        } finally {
            ts.delete("uri:id0");
        }
    }

    @Test
    public void testSparqlResultInXml() throws Exception {
        String answer = null;

        ts.add("uri:id0", rdf);
        try {
            answer = ts.executeQuery("SELECT ?x ?y ?z WHERE {?x ?y ?z}", TupleQueryResultFormat.SPARQL);
            assertTrue(answer.startsWith("<?xml"));
            assertTrue(answer.indexOf("<literal>A.M. Özman Yürekli</literal>") > -1);
            assertTrue(answer.endsWith("</sparql>\n"));
        } finally {
            ts.delete("uri:id0");
        }
    }

    static final String rdf = "<?xml version='1.0'?>" +
        "<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'" +
        "             xmlns:exterms='http://www.example.org/terms/'>" +
        "  <rdf:Description rdf:about='http://www.example.org/index.html'>" +
        "      <exterms:creation-date>August 16, 1999</exterms:creation-date>" +
        "      <rdf:value>A.M. Özman Yürekli</rdf:value>" +
        "  </rdf:Description>" +
        "</rdf:RDF>";
}