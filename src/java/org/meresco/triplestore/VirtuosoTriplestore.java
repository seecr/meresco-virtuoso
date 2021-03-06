/* begin license *
 *
 * The Meresco Virtuoso package is an Virtuoso Triplestore based on meresco-triplestore
 *
 * Copyright (C) 2014-2015 Seecr (Seek You Too B.V.) http://seecr.nl
 *
 * This file is part of "Meresco Virtuoso"
 *
 * "Meresco Virtuoso" is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * "Meresco Virtuoso" is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with "Meresco Virtuoso"; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * end license */

package org.meresco.triplestore;

import org.openrdf.query.MalformedQueryException;
import org.openrdf.query.QueryLanguage;
import org.openrdf.query.resultio.TupleQueryResultFormat;
import org.openrdf.query.parser.QueryParserUtil;

import java.io.File;
import virtuoso.sesame2.driver.VirtuosoRepository;

class VirtuosoTriplestore extends SesameTriplestore {

    public VirtuosoTriplestore(File directory, String hostname, Integer port, String username, String password) {
        super(directory);
        this.repository = new VirtuosoRepository("jdbc:virtuoso://" + hostname + ":" + port, username, password);
        startup();
    }

    public String executeTupleQuery(String sparQL, TupleQueryResultFormat resultFormat) throws MalformedQueryException {
        try {
            return super.executeTupleQuery(sparQL, resultFormat);
        } catch (RuntimeException e) {
            QueryParserUtil.parseTupleQuery(QueryLanguage.SPARQL, sparQL, null);
            throw e;
        }
    }
}
