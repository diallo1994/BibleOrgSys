#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# USFMMarkers.py
#
# Module handling USFMMarkers
#   Last modified: 2011-06-02 (also update versionString below)
#
# Copyright (C) 2011 Robert Hunt
# Author: Robert Hunt <robert316@users.sourceforge.net>
# License: See gpl-3.0.txt
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Module handling USFMMarkers.
"""

progName = "USFM Markers handler"
versionString = "0.53"


import logging, os.path
from gettext import gettext as _
from collections import OrderedDict

from singleton import singleton
import Globals


# Define commonly used sets of footnote and xref markers
footnoteSets = (
    ['fr', 'fr*'],
    ['fr', 'ft'], ['fr', 'ft', 'ft*'],
    ['fr', 'fq'], ['fr', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq'], ['fr', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft'], ['fr', 'fq', 'ft', 'ft*'], \
    ['fr', 'ft', 'fv'], ['fr', 'ft', 'fv', 'fv*'], \
    ['fr', 'fk', 'ft'], ['fr', 'fk', 'ft', 'ft*'], \
    ['fr', 'ft', 'fq', 'ft'], ['fr', 'ft', 'fq', 'ft', 'ft*'], \
    ['fr', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'fv'], ['fr', 'ft', 'fq', 'fv', 'fv*'], \
    ['fr', 'ft', 'ft', 'fq'], ['fr', 'ft', 'ft', 'fq', 'fq*'], \
    ['fr', 'fk', 'ft', 'fq'], ['fr', 'fk', 'ft', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'ft', 'fq'], ['fr', 'ft', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'ft'], ['fr', 'fq', 'ft', 'fq', 'ft', 'ft*'], \
    ['fr', 'fq', 'ft', 'fq', 'fv'], ['fr', 'fq', 'ft', 'fq', 'fv', 'fv*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq'], ['fr', 'fq', 'ft', 'fq', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'fv', 'fq'], ['fr', 'ft', 'fq', 'fv', 'fq', 'fq*'], \
    ['fr', 'fk', 'ft', 'fq', 'ft'], ['fr', 'fk', 'ft', 'fq', 'ft', 'ft*'], \
    ['fr', 'ft', 'fq', 'ft', 'ft'], ['fr', 'ft', 'fq', 'ft', 'ft', 'ft*'], \
    ['fr', 'ft', 'fv', 'fv*', 'fq'], ['fr', 'ft', 'fv', 'fv*', 'fq', 'fq*'], \
    ['fr', 'ft', 'fv', 'fv*', 'fv'], ['fr', 'ft', 'fv', 'fv*', 'fv', 'fv*'], \
    ['fr', 'ft', 'fq', 'ft', 'fq', 'ft'], ['fr', 'ft', 'fq', 'ft', 'fq', 'ft', 'ft*'], \
    ['fr', 'fq', 'ft', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq', 'ft'], ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'ft*'], \
    ['fr', 'fq', 'ft', 'fq', 'fv', 'fq'], ['fr', 'fq', 'ft', 'fq', 'fv', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'fv', 'fv*', 'fq'], ['fr', 'ft', 'fq', 'fv', 'fv*', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'fv', 'fv*', 'fv'], ['fr', 'ft', 'fq', 'fv', 'fv*', 'fv', 'fv*'], \
    ['fr', 'ft', 'fq', 'ft', 'fv', 'fv', 'fq'], ['fr', 'ft', 'fq', 'ft', 'fv', 'fv', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft'], ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'ft*'], \
    ['fr', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq'], ['fr', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'fv'], ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'fv', 'fv*'], \
    ['fr', 'ft', 'fq', 'fv', 'fq', 'fv', 'fq'], ['fr', 'ft', 'fq', 'fv', 'fq', 'fv', 'fq', 'fq*'], \
    ['fr', 'fk', 'ft', 'fq', 'ft', 'fq', 'ft'], ['fr', 'fk', 'ft', 'fq', 'ft', 'fq', 'ft', 'ft*'], \
    ['fr', 'fq', 'ft', 'fq', 'fv', 'fv*', 'fv'], ['fr', 'fq', 'ft', 'fq', 'fv', 'fv*', 'fv', 'fv*'], \
    ['fr', 'ft', 'fq', 'ft', 'fv', 'fv*', 'fq'], ['fr', 'ft', 'fq', 'ft', 'fv', 'fv*', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'fv', 'fv*', 'ft'], ['fr', 'fq', 'ft', 'fq', 'fv', 'fv*', 'ft', 'ft*'], \
    ['fr', 'ft', 'fq', 'fq', 'fv', 'fv*', 'ft'], ['fr', 'ft', 'fq', 'fq', 'fv', 'fv*', 'ft', 'ft*'], \
    ['fr', 'ft', 'fq', 'fq', 'fv', 'fv*', 'fq'], ['fr', 'ft', 'fq', 'fq', 'fv', 'fv*', 'fq', 'fq*'], \
    ['fr', 'fq', 'fv', 'fv*', 'ft', 'fq', 'fv'], ['fr', 'fq', 'fv', 'fv*', 'ft', 'fq', 'fv', 'fv*'], \
    ['fr', 'ft', 'fk', 'ft', 'fk', 'ft', 'fk', 'ft'], ['fr', 'ft', 'fk', 'ft', 'fk', 'ft', 'fk', 'ft', 'ft*'], \
    ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq', 'ft'], ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq', 'ft', 'ft*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'ft'], ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'ft', 'ft*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fv'], ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fv', 'fv*'], \
    ['fr', 'ft', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq'], ['fr', 'ft', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft'], ['fr', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'ft*'], \
    ['fr', 'fq', 'fv', 'fq', 'ft', 'fq', 'fv', 'fq'], ['fr', 'fq', 'fv', 'fq', 'ft', 'fq', 'fv', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'ft', 'fv', 'fv*', 'fq', 'ft'], ['fr', 'ft', 'fq', 'ft', 'fv', 'fv*', 'fq', 'ft', 'ft*'], \
    ['fr', 'fq', 'ft', 'fq', 'fv', 'fv*', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'fv', 'fv*', 'ft', 'fq', 'fq*'], \
    ['fr', 'ft', 'fv', 'fq', 'ft', 'fv', 'fq', 'fv', 'fq'], ['fr', 'ft', 'fv', 'fq', 'ft', 'fv', 'fq', 'fv', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft'], ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'ft*'], \
    ['fr', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq'], ['fr', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'ft', 'fv', 'fv*', 'fq', 'ft', 'fv', 'fv*', 'fq'], ['fr', 'ft', 'fv', 'fv*', 'fq', 'ft', 'fv', 'fv*', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq', 'ft'], ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq', 'ft', 'ft*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft'], ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'ft*'], \
    ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft'], ['fr', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'ft*'], \
    ['fr', 'ft', 'fq', 'fv', 'fv*', 'ft', 'fq', 'fv', 'fv*', 'fv'], ['fr', 'ft', 'fq', 'fv', 'fv*', 'ft', 'fq', 'fv', 'fv*', 'fv', 'fv*'], \
    ['fr', 'ft', 'fq', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv'], ['fr', 'ft', 'fq', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'ft', 'fv', 'fv*', 'fq', 'ft', 'fv', 'fv*', 'fq'], ['fr', 'ft', 'fq', 'ft', 'fv', 'fv*', 'fq', 'ft', 'fv', 'fv*', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq'], ['fr', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'fv', 'fv*', 'fv', 'fv*', 'ft', 'fq', 'fv', 'fv*', 'fv'], ['fr', 'fq', 'ft', 'fq', 'fv', 'fv*', 'fv', 'fv*', 'ft', 'fq', 'fv', 'fv*', 'fv', 'fv*'], \
    ['fr', 'ft', 'fv', 'fv*', 'fq', 'ft', 'fv', 'fv*', 'fq', 'ft', 'fv', 'fv*', 'fq'], ['fr', 'ft', 'fv', 'fv*', 'fq', 'ft', 'fv', 'fv*', 'fq', 'ft', 'fv', 'fv*', 'fq', 'fq*'], \
    ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq'], ['fr', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq', 'ft', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq'], ['fr', 'ft', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq', 'fv', 'fq', 'fq*'], \
    ['fr', 'ft', 'fq', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv'], ['fr', 'ft', 'fq', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*', 'fv', 'fv*'],
    )
xrefSets = (
    ['xo', 'xdc'], ['xo', 'xdc', 'xdc*'], \
    ['xo', 'xt'],['xo', 'xt', 'xt*'], \
    ['xo', 'xt', 'xk'], \
    ['xo', 'xt', 'xdc'], ['xo', 'xt', 'xdc*'], \
    ['xo', 'xdc', 'xt'], ['xo', 'xdc', 'xt', 'xt*'], \
    ['xo', 'xt', 'xo', 'xt'], ['xo', 'xt', 'xo', 'xt', 'xt*'], \
    ['xo', 'xt', 'xk', 'xt'], ['xo', 'xt', 'xk', 'xt', 'xt*'], \
    ['xo', 'xt', 'xdc', 'xt'], ['xo', 'xt', 'xdc', 'xt', 'xt*'], \
    ['xo', 'xt', 'xt', 'xo', 'xt'], ['xo', 'xt', 'xt', 'xo', 'xt', 'xt*'], \
    ['xo', 'xt', 'xo', 'xt', 'xdc'], ['xo', 'xt', 'xo', 'xt', 'xdc', 'xdc*'], \
    ['xo', 'xt', 'xo', 'xt', 'xo', 'xt'], ['xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xt*'], \
    ['xo', 'xdc', 'xt', 'xt', 'xo', 'xt'], ['xo', 'xdc', 'xt', 'xt', 'xo', 'xt', 'xt*'], \
    ['xo', 'xt', 'xdc', 'xt', 'xo', 'xt'], ['xo', 'xt', 'xdc', 'xt', 'xo', 'xt', 'xt*'], \
    ['xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt'], ['xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xt*'], \
    ['xo', 'xt', 'xdc', 'xt', 'xo', 'xt', 'xo', 'xt'], ['xo', 'xt', 'xdc', 'xt', 'xo', 'xt', 'xo', 'xt', 'xt*'], \
    ['xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt'], ['xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xt*'], \
    ['xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt'], ['xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xo', 'xt', 'xt*'],
    )
for thisSet in footnoteSets: assert( footnoteSets.count(thisSet) == 1 ) # Check there's no duplicates above
for thisSet in xrefSets: assert( xrefSets.count(thisSet) == 1 )


@singleton # Can only ever have one instance
class USFMMarkers:
    """
    Class for handling USFMMarkers.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.

    Note: marker is used in this class to represent the three-character marker.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor: 
        """
        self.__DataDict = None # We'll import into this in loadData
    # end of __init__

    def loadData( self, XMLFilepath=None ):
        """ Loads the XML data file and imports it to dictionary format (if not done already). """
        if not self.__DataDict: # We need to load them once -- don't do this unnecessarily
            # See if we can load from the pickle file (faster than loading from the XML)
            standardXMLFilepath = os.path.join( "DataFiles", "USFMMarkers.xml" )
            standardPickleFilepath = os.path.join( "DataFiles", "DerivedFiles", "USFMMarkers_Tables.pickle" )
            if XMLFilepath is None \
            and os.access( standardPickleFilepath, os.R_OK ) \
            and os.stat(standardPickleFilepath)[8] > os.stat(standardXMLFilepath)[8] \
            and os.stat(standardPickleFilepath)[9] > os.stat(standardXMLFilepath)[9]: # There's a newer pickle file
                import pickle
                if Globals.verbosityLevel > 2: print( "Loading pickle file {}...".format( standardPickleFilepath ) )
                with open( standardPickleFilepath, 'rb') as pickleFile:
                    self.__DataDict = pickle.load( pickleFile ) # The protocol version used is detected automatically, so we do not have to specify it
            else: # We have to load the XML (much slower)
                from USFMMarkersConverter import USFMMarkersConverter
                if XMLFilepath is not None: logging.warning( _("USFM markers are already loaded -- your given filepath of '{}' was ignored").format(XMLFilepath) )
                umc = USFMMarkersConverter()
                umc.loadAndValidate( XMLFilepath ) # Load the XML (if not done already)
                self.__DataDict = umc.importDataToPython() # Get the various dictionaries organised for quick lookup
        return self
    # end of loadData

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        indent = 2
        result = "USFM Markers object"
        result += ('\n' if result else '') + ' '*indent + _("Number of entries = {}").format( len(self.__DataDict["rawMarkerDict"]) )
        if Globals.verbosityLevel > 2:
            indent = 4
            result += ('\n' if result else '') + ' '*indent + _("Number of raw new line markers = {}").format( len(self.__DataDict["newlineMarkersList"]) )
            result += ('\n' if result else '') + ' '*indent + _("Number of internal markers = {}").format( len(self.__DataDict["internalMarkersList"]) )
        return result
    # end of __str__

    def __len__( self ):
        """ Return the number of available markers. """
        return len(self.__DataDict["combinedMarkerDict"])

    def __contains__( self, marker ):
        """ Returns True or False. """
        return marker in self.__DataDict["combinedMarkerDict"]

    def isValidMarker( self, marker ):
        """ Returns True or False. """
        return marker in self.__DataDict["combinedMarkerDict"]

    def isNewlineMarker( self, marker ):
        """ Return True or False. """
        if marker not in self.__DataDict["combinedMarkerDict"]: return False
        return self.toRawMarker(marker) in self.__DataDict["combinedNewlineMarkersList"]

    def isInternalMarker( self, marker ):
        """ Return True or False. """
        if marker not in self.__DataDict["combinedMarkerDict"]: return False
        return self.toRawMarker(marker) in self.__DataDict["internalMarkersList"]

    def isDeprecatedMarker( self, marker ):
        """ Return True or False. """
        return marker in self.__DataDict["deprecatedMarkersList"]

    def isCompulsoryMarker( self, marker ):
        """ Return True or False. """
        if marker not in self.__DataDict["combinedMarkerDict"]: return False
        return self.__DataDict["rawMarkerDict"][self.toRawMarker(marker)]["compulsoryFlag"]

    def isNumberableMarker( self, marker ):
        """ Return True or False. """
        if marker not in self.__DataDict["combinedMarkerDict"]: return False
        return self.__DataDict["rawMarkerDict"][self.toRawMarker(marker)]["numberableFlag"]

    def isNestingMarker( self, marker ):
        """ Return True or False. """
        if marker not in self.__DataDict["combinedMarkerDict"]: return False
        return self.__DataDict["rawMarkerDict"][self.toRawMarker(marker)]["nestsFlag"]

    def isPrinted( self, marker ):
        """ Return True or False. """
        if marker not in self.__DataDict["combinedMarkerDict"]: return False
        return self.__DataDict["rawMarkerDict"][self.toRawMarker(marker)]["printedFlag"]

    def markerShouldBeClosed( self, marker ):
        """ Return "N", "S", "A" for "never", "sometimes", "always".
            Returns False for an invalid marker. """
        if marker not in self.__DataDict["combinedMarkerDict"]: return False
        closed = self.__DataDict["rawMarkerDict"][self.toRawMarker(marker)]["closed"]
        #if closed is None: return "N"
        if closed == "No": return "N"
        if closed == "Always": return "A"
        if closed == "Optional": return "S"
        print( 'msbc {}'.format( closed ))
        raise KeyError # Should be something better here
    # end of markerShouldBeClosed

    def markerShouldHaveContent( self, marker ):
        """ Return "N", "S", "A" for "never", "sometimes", "always".
            Returns False for an invalid marker. """
        if marker not in self.__DataDict["combinedMarkerDict"]: return False
        hasContent = self.__DataDict["rawMarkerDict"][self.toRawMarker(marker)]["hasContent"]
        #if hasContent is None: return "N"
        if hasContent == "Never": return "N"
        if hasContent == "Always": return "A"
        if hasContent == "Sometimes": return "S"
        print( 'mshc {}'.format( hasContent ))
        raise KeyError # Should be something better here
    # end of markerShouldHaveContent

    def toRawMarker( self, marker ):
        """ Returns a marker without numerical suffixes, i.e., s1->s, q1->q, etc. """
        return self.__DataDict["combinedMarkerDict"][marker]

    def toStandardMarker( self, marker ):
        """ Returns a standard marker, i.e., s->s1, q->q1, etc. """
        if marker in self.__DataDict["conversionDict"]: return self.__DataDict["conversionDict"][marker]
        #else
        if marker in self.__DataDict["combinedMarkerDict"]: return marker
        #else must be something wrong
        raise KeyError
    # end of toStandardMarker

    def markerOccursIn( self, marker ):
        """ Return a short string, e.g. "Introduction", "Text". """
        return self.__DataDict["rawMarkerDict"][self.toRawMarker(marker)]["occursIn"]

    def getMarkerEnglishName( self, marker ):
        """ Returns the English name for a marker.
                Use getOccursInList() to get a list of all possibilities. """
        return self.__DataDict["rawMarkerDict"][self.toRawMarker(marker)]["nameEnglish"]

    def getMarkerDescription( self, marker ):
        """ Returns the description for a marker (or None). """
        return self.__DataDict["rawMarkerDict"][self.toRawMarker(marker)]["description"]

    def getOccursInList( self ):
        """ Returns a list of strings which markerOccursIn can return. """
        oiList = []
        for marker in self.__DataDict["rawMarkerDict"]:
            occursIn = self.__DataDict["rawMarkerDict"][marker]['occursIn']
            if occursIn not in oiList: oiList.append( occursIn )
        return oiList
    # end of getOccursInList

    def getNewlineMarkersList( self, option='Combined' ):
        """ Returns a list of all new line markers. """
        assert( option in ('Raw','Numbered','Combined') )
        if option=='Combined': return self.__DataDict["combinedNewlineMarkersList"]
        elif option=='Raw': return self.__DataDict["numberedNewlineMarkersList"]
        elif option=='Numbered': return self.__DataDict["newlineMarkersList"]
    # end of getNewlineMarkersList

    def getInternalMarkersList( self ):
        """ Returns a list of all internal markers.
            This includes character, footnote and xref markers. """
        return self.__DataDict["internalMarkersList"]

    def getCharacterMarkersList( self, includeBackslash=False, includeEndMarkers=False ):
        """ Returns a list of all character markers.
            This excludes footnote and xref markers. """
        result = []
        for marker in self.__DataDict["internalMarkersList"]:
            if marker!='f' and marker!='x' and self.markerOccursIn(marker)=="Text":
                adjMarker = '\\'+marker if includeBackslash else marker
                result.append( adjMarker )
                if includeEndMarkers:
                    assert( self.markerShouldBeClosed( marker ) == 'A' )
                    result.append( adjMarker + '*' )
        return result

    def getTypicalNoteSets( self, select='All' ):
        """ Returns a container of typical footnote and xref sets. """
        if select=='fn': return footnoteSets
        elif select=='xr': return xrefSets
        elif select=='All': return footnoteSets + xrefSets
    # end of getTypicalNoteSets

    def getMarkerListFromText( self, text ):
        """Given a text, return a list of the markers (along with their positions).
            Returns a list of three-tuple containing (marker, nextSignificantChar, indexOfBackslashCharacter).
                nextSignificantChar is ' ', '*' (for closing marker) or '' (for end of line)."""
        result = []
        textLength = len( text )
        ix = text.find( '\\' )
        while( ix != -1 ): # Find backslashes
            marker = ''
            iy = ix + 1
            if iy<textLength:
                c1 = text[iy]
                if c1==' ': logging.error( _("USFMMarkers.getMarkerListFromText found invalid '\\' in '{}'").format( text ) )
                elif c1=='*': logging.error( _("USFMMarkers.getMarkerListFromText found invalid '\\*' in '{}'").format( text ) )
                else: # it's probably ok
                    marker += c1
                    iy += 1
                    while ( iy < textLength ):
                        c = text[iy]
                        if c==' ': result.append( (marker,' ',ix,) ); break
                        elif c=='*': result.append( (marker,'*',ix,) ); break
                        else: # it's probably ok
                            marker += c
                        iy += 1
                    else: result.append( (marker,'',ix,) )
            else: # it was a backslash at the end of the line
                result.append( ('\\','',ix,) )
                logging.error( _("USFMMarkers.getMarkerListFromText found invalid '\\' at end of '{}'").format( text ) )
            ix = text.find( '\\', ix+1 )
        #if result: print( result )
        return result
    # end of getMarkerListFromText
# end of USFMMarkers class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v{}".format( versionString ) )
    #parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h/.c formats suitable for directly including into other programs, as well as .json.")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 1: print( "{} V{}".format( progName, versionString ) )

    # Demo the USFMMarkers object
    um = USFMMarkers().loadData() # Doesn't reload the XML unnecessarily :)
    print( um ) # Just print a summary
    print( "Markers can occurs in", um.getOccursInList() )
    pm = um.getNewlineMarkersList()
    print( "New line markers are", len(pm), pm )
    cm = um.getInternalMarkersList()
    print( "Internal (character) markers are", len(cm), cm )
    for m in ('ab', 'h', 'toc1', 'toc4', 'q', 'q1', 'q2', 'q3', 'q4', 'p', 'P', 'f', 'f*' ):
        print( _("{} is {}a valid marker").format( m, "" if um.isValidMarker(m) else _("not")+' ' ) )
        if um.isValidMarker(m):
            print( '  ' + "{}: {}".format( um.getMarkerEnglishName(m), um.getMarkerDescription(m) ) )
            if Globals.verbosityLevel > 2:
                print( '  ' + _("Compulsory:{}, Numberable:{}, Occurs in: {}").format( um.isCompulsoryMarker(m), um.isNumberableMarker(m), um.markerOccursIn(m) ) )
                print( '  ' + _("{} is {}a new line marker").format( m, "" if um.isNewlineMarker(m) else _("not")+' ' ) )
                print( '  ' + _("{} is {}an internal (character) marker").format( m, "" if um.isInternalMarker(m) else _("not")+' ' ) )
# end of main

if __name__ == '__main__':
    main()
# end of USFMMarkers.py