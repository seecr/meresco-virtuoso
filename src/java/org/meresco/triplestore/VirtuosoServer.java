/* begin license *
 *
 * The Meresco Virtuoso package is an Virtuoso Triplestore based on meresco-triplestore
 *
 * Copyright (C) 2014 Seecr (Seek You Too B.V.) http://seecr.nl
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

import java.io.File;
import java.nio.charset.Charset;

import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.PosixParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.MissingOptionException;

public class VirtuosoServer {
    public static void main(String[] args) throws Exception {
        Option option;

        Options options = new Options();

        option = new Option("p", "port", true, "Port number");
        option.setType(Integer.class);
        option.setRequired(true);
        options.addOption(option);

        option = new Option("d", "stateDir", true, "State directory for backup e.d.");
        option.setType(String.class);
        option.setRequired(true);
        options.addOption(option);

        option = new Option("hostname", "hostname", true, "Hostame of the virtuoso instance");
        option.setType(String.class);
        option.setRequired(true);
        options.addOption(option);

        option = new Option("virtuosoPort", "virtuosoPort", true, "Port number of the virtuoso instance");
        option.setType(Integer.class);
        option.setRequired(true);
        options.addOption(option);

        option = new Option("username", "username", true, "Username of virtuoso");
        option.setType(String.class);
        option.setRequired(true);
        options.addOption(option);

        option = new Option("password", "password", true, "Password of virtuoso");
        option.setType(String.class);
        option.setRequired(true);
        options.addOption(option);

        PosixParser parser = new PosixParser();
        CommandLine commandLine = null;
        try {
            commandLine = parser.parse(options, args);
        } catch (MissingOptionException e) {
            HelpFormatter helpFormatter = new HelpFormatter();
            helpFormatter.printHelp("start-virtuoso" , options);
            System.exit(1);
        }

        Integer port = new Integer(commandLine.getOptionValue("p"));
        String stateDir = commandLine.getOptionValue("d");
        String hostname = commandLine.getOptionValue("hostname");
        Integer virtuosoPort = new Integer(commandLine.getOptionValue("virtuosoPort"));
        String username = commandLine.getOptionValue("username");
        String password = commandLine.getOptionValue("password");
        Boolean disableTransactionLog = commandLine.hasOption("disableTransactionLog");

        if (Charset.defaultCharset() != Charset.forName("UTF-8")) {
        	System.err.println("file.encoding must be UTF-8.");
            System.exit(1);
        }

        Triplestore tripleStore = new VirtuosoTriplestore(new File(stateDir), hostname, virtuosoPort, username, password);
        HttpHandler handler = new HttpHandler(tripleStore);
        HttpServer httpServer = new HttpServer(port, 15);

        System.out.println("Triplestore started with " + String.valueOf(tripleStore.size()) + " statements");
        System.out.flush();

        httpServer.setHandler(handler);
        httpServer.start();
    }
}
