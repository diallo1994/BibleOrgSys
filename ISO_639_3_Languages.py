#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ISO_639_3_Languages.py
#
# Module handling ISO_639_3.xml to produce C and Python data tables
#   Last modified: 2011-02-03 (also update versionString below)
#
# Copyright (C) 2010-2011 Robert Hunt
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
Module handling ISO_639_3_Languages.xml and to export to JSON, C and Python data tables.
"""

progName = "ISO 639_3_Languages handler"
versionString = "0.81"

import logging, os.path
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree

from singleton import singleton
import Globals


@singleton # Can only ever have one instance
class _ISO_639_3_LanguagesConverter:
    """
    Class for handling and converting ISO 639-3 language codes.
    """

    def __init__( self ):
        """
        Constructor: expects the filepath of the source XML file.
        Loads (and crudely validates the XML file) into an element tree.
        """
        self._filenameBase = "iso_639_3"

        # These fields are used for parsing the XML
        self._treeTag = "iso_639_3_entries"
        self._mainElementTag = "iso_639_3_entry"

        # These fields are used for automatically checking/validating the XML
        self._compulsoryAttributes = ( "id", "name", "type", "scope", )
        self._optionalAttributes = ( "part1_code", "part2_code", )
        self._uniqueAttributes = ( "id", "name", "part1_code", "part2_code", )
        self._compulsoryElements = ()
        self._optionalElements = ()
        self._uniqueElements = self._compulsoryElements + self._optionalElements

        self.title = "ISO 639-3 language codes"

        # These are fields that we will fill later
        self._XMLtree, self.__DataDicts = None, None
    # end of __init__

    def loadAndValidate( self, XMLFilepath=None ):
        """
        Loads (and crudely validates the XML file) into an element tree.
            Allows the filepath of the source XML file to be specified, otherwise uses the default.
        """
        if self._XMLtree is None: # We mustn't have already have loaded the data
            if XMLFilepath is None:
                XMLFilepath = os.path.join( "DataFiles", self._filenameBase + ".xml" )

            self._load( XMLFilepath )
            if Globals.strictCheckingFlag:
                self._validate()
        else: # The data must have been already loaded
            if XMLFilepath is not None and XMLFilepath!=self.__XMLFilepath: logging.error( _("ISO 639-3 language codes are already loaded -- your different filepath of '{}' was ignored").format( XMLFilepath ) )
        return self
    # end of loadAndValidate

    def _load( self, XMLFilepath ):
        """
        Load the source XML file and remove the header from the tree.
        Also, extracts some useful Attributes from the header element.
        """
        assert( XMLFilepath )
        self.__XMLFilepath = XMLFilepath
        assert( self._XMLtree is None or len(self._XMLtree)==0 ) # Make sure we're not doing this twice

        if Globals.verbosityLevel > 2: print( "Loading ISO 639-3 languages XML file from '{}'...".format( XMLFilepath ) )
        self._XMLtree = ElementTree().parse( XMLFilepath )
        assert( self._XMLtree ) # Fail here if we didn't load anything at all

        if self._XMLtree.tag  != self._treeTag:
            logging.error( "Expected to load '{}' but got '{}'".format( self._treeTag, self._XMLtree.tag ) )
    # end of _load

    def _validate( self ):
        """
        Check/validate the loaded data.
        """
        assert( self._XMLtree )

        uniqueDict = {}
        #for elementName in self._uniqueElements: uniqueDict["Element_"+elementName] = []
        for attributeName in self._uniqueAttributes: uniqueDict["Attribute_"+attributeName] = []

        for j,element in enumerate(self._XMLtree):
            if element.tag == self._mainElementTag:
                # Check compulsory attributes on this main element
                for attributeName in self._compulsoryAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( "Compulsory '{}' attribute is missing from {} element in record {}".format( attributeName, element.tag, j ) )
                    if not attributeValue:
                        logging.warning( "Compulsory '{}' attribute is blank on {} element in record {}".format( attributeName, element.tag, j ) )

                # Check optional attributes on this main element
                for attributeName in self._optionalAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( "Optional '{}' attribute is blank on {} element in record {}".format( attributeName, element.tag, j ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in self._compulsoryAttributes and attributeName not in self._optionalAttributes:
                        logging.warning( "Additional '{}' attribute ('{}') found on {} element in record {}".format( attributeName, attributeValue, element.tag, j ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in self._uniqueAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict["Attribute_"+attributeName]:
                            logging.error( "Found '{}' data repeated in '{}' field on {} element in record {}".format( attributeValue, attributeName, element.tag, j ) )
                        uniqueDict["Attribute_"+attributeName].append( attributeValue )
            else:
                logging.warning( "Unexpected element: {} in record {}".format( element.tag, j ) )
    # end of _validate

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "_ISO_639_3_Languages_Converter object"
        if self.title: result += ('\n' if result else '') + self.title
        result += ('\n' if result else '') + "  Num entries = " + str(len(self._XMLtree))
        return result
    # end of __str__

    def __len__( self ):
        """ Returns the number of languages loaded. """
        return len( self._XMLtree )
    # end of __len__

    def importDataToPython( self ):
        """
        Loads (and pivots) the data into suitable Python containers to use in a Python program.
        (Of course, you can just use the elementTree in self._XMLtree if you prefer.)
        """
        assert( self._XMLtree )
        if self.__DataDicts: # We've already done an import/restructuring -- no need to repeat it
            return self.__DataDicts

        # We'll create a number of dictionaries with different Attributes as the key
        myIDDict, myNameDict = OrderedDict(), OrderedDict()
        for element in self._XMLtree:
            # Get the required information out of the tree for this element
            # Start with the compulsory attributes
            ID = element.get("id")
            Name = element.get("name")
            Scope = element.get("scope")
            Type = element.get("type")
            # The optional attributes are set to None if they don't exist
            Part1Code = element.get("part1_code")
            Part2Code = element.get("part2_code")

            # Now put it into my dictionaries for easy access
            # This part should be customized or added to for however you need to process the data
            #   Add .upper() if you require the abbreviations to be uppercase (or .lower() for lower case)
            if "id" in self._compulsoryAttributes or ID:
                if "id" in self._uniqueElements: assert( ID not in myIDDict ) # Shouldn't be any duplicates
                myIDDict[ID] = ( Name, Scope, Type, Part1Code, Part2Code, )
            if "name" in self._compulsoryAttributes or Name:
                if "name" in self._uniqueElements: assert( Name not in myNameDict ) # Shouldn't be any duplicates
                myNameDict[Name.upper()] = ID # Save it as UPPERCASE
            self.__DataDicts = myIDDict, myNameDict
        return self.__DataDicts
    # end of importDataToPython

    def exportDataToPython( self, filepath=None ):
        """
        Writes the information tables to a .py file that can be cut and pasted into a Python program.
        """
        def exportPythonDict( theFile, theDict, dictName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            theFile.write( "{} = {{\n  # Key is {}\n  # Fields are: {}\n".format( dictName, keyComment, fieldsComment ) )
            for dictKey in sorted(theDict.keys()):
                theFile.write( "  {}: {},\n".format( repr(dictKey), repr(theDict[dictKey]) ) )
            theFile.write( "}}\n# end of {}\n\n".format( dictName ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self._XMLtree )
        self.importDataToPython()
        assert( self.__DataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self._filenameBase + "_Languages_Tables.py" )
        if Globals.verbosityLevel > 1: print( "Exporting to {}...".format( filepath ) )

        IDDict, NameDict = self.__DataDicts
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# {}\n#\n".format( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by ISO_639_3_Languages_Converter.py V{} on {}\n#\n".format( versionString, datetime.now() ) )
            if self.title: myFile.write( "# {}\n".format( self.title ) )
            myFile.write( "#   {} {} loaded from the original XML file.\n#\n\n".format( len(self._XMLtree), self._treeTag ) )
            exportPythonDict( myFile, IDDict, "ISO639_3_Languages_IDDict", "id", "Name, Type, Scope, Part1Code, Part2Code" )
            exportPythonDict( myFile, NameDict, "ISO639_3_Languages_NameDict", "name", "ID" )
            myFile.write( "# end of {}".format( os.path.basename(filepath) ) )
    # end of exportDataToPython

    def exportDataToJSON( self, filepath=None ):
        """
        Writes the information tables to a .json file that can be easily loaded into a Java program.

        See http://en.wikipedia.org/wiki/JSON.
        """
        from datetime import datetime
        import json

        assert( self._XMLtree )
        self.importDataToPython()
        assert( self.__DataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self._filenameBase + "_Languages_Tables.json" )
        if Globals.verbosityLevel > 1: print( "Exporting to {}...".format( filepath ) )
        with open( filepath, 'wt' ) as myFile:
            json.dump( self.__DataDicts, myFile, indent=2 )
    # end of exportDataToJSON

    def exportDataToC( self, filepath=None ):
        """
        Writes the information tables to a .h and .c files that can be included in c and c++ programs.

        NOTE: The (optional) filepath should not have the file extension specified -- this is added automatically.
        """
        def exportPythonDict( hFile, cFile, theDict, dictName, sortedBy, structure ):
            """ Exports theDict to the .h and .c files. """
            def convertEntry( entry ):
                """ Convert special characters in an entry... """
                result = ""
                if isinstance( entry, tuple ):
                    for j, field in enumerate(entry):
                        if result: result += ", " # Separate the fields
                        if field is None: result += '""'
                        elif isinstance( field, str):
                            if j>0 and len(field)==1: result += "'" + field + "'" # Catch the character fields
                            else: result += '"' + str(field).replace('"','\\"') + '"' # String fields
                        else: logging.error( "Cannot convert unknown field type '{}' in entry '{}'".format( field, entry ) )
                elif isinstance( entry, str):
                    result += '"' + str(entry).replace('"','\\"') + '"' # String fields
                else:
                    logging.error( "Can't handle this type of entry yet: {}".format( repr(entry) ) )
                return result
            # end of convertEntry

            for dictKey in theDict.keys(): # Have to iterate this :(
                fieldsCount = len( theDict[dictKey] ) + 1 # Add one since we include the key in the count
                break # We only check the first (random) entry we get

            #hFile.write( "typedef struct {}EntryStruct { {} } {}Entry;\n\n".format( dictName, structure, dictName ) )
            hFile.write( "typedef struct {}EntryStruct {{\n".format( dictName ) )
            for declaration in structure.split(';'):
                adjDeclaration = declaration.strip()
                if adjDeclaration: hFile.write( "    {};\n".format( adjDeclaration ) )
            hFile.write( "}} {}Entry;\n\n".format( dictName ) )

            cFile.write( "const static {}Entry\n {}[{}] = {{\n  // Fields ({}) are {}\n  // Sorted by {}\n".format( dictName, dictName, len(theDict), fieldsCount, structure, sortedBy ) )
            for dictKey in sorted(theDict.keys()):
                if isinstance( dictKey, str ):
                    cFile.write( "  {{\"{}\", {}}},\n".format( dictKey, convertEntry(theDict[dictKey]) ) )
                elif isinstance( dictKey, int ):
                    cFile.write( "  {{{}, {}}},\n".format( dictKey, convertEntry(theDict[dictKey]) ) )
                else:
                    logging.error( "Can't handle this type of key data yet: {}".format( dictKey ) )
            cFile.write( "}}; // {} ({} entries)\n\n".format( dictName, len(theDict) ) )
        # end of exportPythonDict


        from datetime import datetime

        assert( self._XMLtree )
        self.importDataToPython()
        assert( self.__DataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self._filenameBase + "_Languages_Tables" )
        hFilepath = filepath + '.h'
        cFilepath = filepath + '.c'
        if Globals.verbosityLevel > 1: print( "Exporting to {}...".format( cFilepath ) ) # Don't bother telling them about the .h file
        ifdefName = self._filenameBase.upper() + "_Tables_h"

        IDDict, NameDict = self.__DataDicts
        with open( hFilepath, 'wt' ) as myHFile, open( cFilepath, 'wt' ) as myCFile:
            myHFile.write( "// {}\n//\n".format( hFilepath ) )
            myCFile.write( "// {}\n//\n".format( cFilepath ) )
            lines = "// This UTF-8 file was automatically generated by ISO_639_3_Languages.py V{} on {}\n//\n".format( versionString, datetime.now() )
            myHFile.write( lines ); myCFile.write( lines )
            myCFile.write( "//   {} {} loaded from the original XML file.\n//\n\n".format( len(self._XMLtree), self._treeTag ) )
            myHFile.write( "\n#ifndef {}\n#define {}\n\n".format( ifdefName, ifdefName ) )
            myCFile.write( '#include "{}"\n\n'.format( os.path.basename(hFilepath) ) )

            CHAR = "const unsigned char"
            BYTE = "const int"
            exportPythonDict( myHFile, myCFile, IDDict, "IDDict", "3-character lower-case ID field", "{}[3+1] ID; {}* Name; {} Type; {} Scope; {}[2+1] Part1Code; {}[3+1] Part2Code;".format(CHAR,CHAR,CHAR,CHAR,CHAR,CHAR) )
            exportPythonDict( myHFile, myCFile, NameDict, "NameDict", "language name (alphabetical)", "{}* Name; {}[3+1] ID;".format(CHAR,CHAR)  )

            myHFile.write( "#endif // {}\n\n".format( ifdefName ) )
            myHFile.write( "// end of {}".format( os.path.basename(hFilepath) ) )
            myCFile.write( "// end of {}".format( os.path.basename(cFilepath) ) )
    # end of exportDataToC
# end of _ISO_639_3_LanguagesConverter class


@singleton # Can only ever have one instance
class ISO_639_3_Languages:
    """
    Class for handling ISO_639_3_Languages.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.

    Note: BBB is used in this class to represent the three-character referenceAbbreviation.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor: 
        """
        self.lgC = _ISO_639_3_LanguagesConverter()
        self.__IDDict = self.__NameDict = None # We'll import into this in loadData
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "ISO_639_3_Languages object"
        assert( len(self.__IDDict) == len(self.__NameDict) )
        result += ('\n' if result else '') + "  Num entries = {}".format( len(self.__IDDict) )
        return result
    # end of __str__

    def loadData( self, XMLFilepath=None ):
        """ Loads the XML data file and imports it to dictionary format (if not done already). """
        if not self.__IDDict and not self.__NameDict: # Don't do this unnecessarily
            self.lgC.loadAndValidate( XMLFilepath ) # Load the XML (if not done already)
            self.__IDDict, self.__NameDict = self.lgC.importDataToPython() # Get the various dictionaries organised for quick lookup
            del self.lgC # Now the converter class (that handles the XML) is no longer needed
        return self
    # end of loadData

    def __len__( self ):
        """ Returns the number of languages loaded. """
        assert( len(self.__IDDict) == len(self.__NameDict) )
        return len(self.__IDDict)

    def isValidLanguageCode( self, ccc ):
        """ Returns True or False. """
        return ccc in self.__IDDict

    def getLanguageName( self, ccc ):
        """ Return the language name for the given language code. """
        return self.__IDDict[ccc][0] # The first field is the name

    def getScope( self, ccc ):
        """ Return the scope ('I','M' or 'S') for the given language code.
                I = individual language
                M = macrolanguage
                S = special code """
        return self.__IDDict[ccc][1] # The second field is the scope

    def getType( self, ccc ):
        """ Return the type ('A','C','E','H','L' or 'S') for the given language code.
                A = ancient (extinct since ancient times)
                C = constructed
                E = extinct (in recent times)
                H = historical (distinct from its modern form)
                L = living
                S = special code """
        return self.__IDDict[ccc][2] # The third field is the type

    def getPart1Code( self, ccc ):
        """ Return the optional 2-character ISO 639-1 code for the given language code (or None). """
        return self.__IDDict[ccc][3] # The fourth field is the (optional) part1code

    def getPart2Code( self, ccc ):
        """ Return the optional 3-character ISO 639-2B code for the given language code (or None). """
        return self.__IDDict[ccc][4] # The fifth field is the (optional) part2code

    def getLanguageCode( self, name ):
        """ Return the 3-character code for the given language name (or None if one can't be found). """
        UCName = name.upper() # Convert to UPPERCASE for searching
        if UCName in self.__NameDict: return self.__NameDict[UCName]

    def getNameMatches( self, namePortion ):
        """ Return a list of matching names for the given part of a name. """
        UCNamePortion = namePortion.upper()
        results = []
        for UCName in self.__NameDict:
            if UCNamePortion in UCName:
                ccc = self.__NameDict[UCName]
                results.append( self.__IDDict[ccc][0] ) # Get the mixed case language name
        return results
# end of ISO_639_3_Languages class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v{}".format( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 1: print( "{} V{}".format( progName, versionString ) )

    if Globals.commandLineOptions.export:
        lgC = _ISO_639_3_Languages_Converter().loadAndValidate() # Load the XML
        lgC.exportDataToPython() # Produce the .py tables
        lgC.exportDataToJSON() # Produce a json output file
        lgC.exportDataToC() # Produce the .h and .c tables

    else: # Must be demo mode
        # Demo the converter object
        lgC = _ISO_639_3_LanguagesConverter().loadAndValidate() # Load the XML
        print( lgC ) # Just print a summary

        # Demo the languages object
        lg = ISO_639_3_Languages().loadData() # Doesn't reload the XML unnecessarily :)
        print( lg ) # Just print a summary
        for testCode in ('qwq','mbt','MBT','abk',):
            print( "  Testing {}...".format( testCode ) )
            if not lg.isValidLanguageCode( testCode ):
                print( "    {} not found".format( testCode ) )
            else:
                print( "    {} -> {}".format( testCode, lg.getLanguageName( testCode ) ) )
                print( "    Scope is {}, Type is {}".format( lg.getScope(testCode), lg.getType(testCode) ) )
                part1Code, part2Code = lg.getPart1Code(testCode), lg.getPart2Code(testCode)
                if part1Code is not None: print( "    Part1 code is {}".format(part1Code) )
                if part2Code is not None: print( "    Part2 code is {}".format(part2Code) )
        for testName in ('English','German','Deutsch','French','Ayta, Abellen','Manobo, Matigsalug','Manobo','SomeName',):
            print( "  Testing {}...".format( testName ) )
            code = lg.getLanguageCode( testName )
            if code is None:
                print( "    {} not found".format( testName ) )
            else:
                print( "    {} -> {}".format( testName, code ) )
        for testNamePortion in ('English','German','Deutsch','French','Ayta, Abellen','Manobo, Matigsalug','Manobo','SomeName',):
            print( "  Testing {}...".format( testNamePortion ) )
            matches = lg.getNameMatches( testNamePortion )
            for match in matches:
                print( "    Found {} = {}".format( lg.getLanguageCode(match), match ) )
            else: print( "    {} not found".format( testNamePortion ) )
# end of main

if __name__ == '__main__':
    main()
# end of ISO_639_3_Languages.py
