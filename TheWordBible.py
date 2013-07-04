#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# TheWordBible.py
#   Last modified: 2013-07-04 by RJH (also update ProgVersion below)
#
# Module handling "TheWord" Bible module files
#
# Copyright (C) 2013 Robert Hunt
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
Module reading and loading TheWord Bible files.
These can be downloaded from: http://www.theword.net/index.php?downloads.modules

A TheWord Bible module file has one verse per line (KJV versification)
    OT (.ot file) has 23145 lines
    NT (.nt file) has 7957 lines
    Bible (.ont file) has 31102 lines.

Some basic HTML-style tags are recognised: <u></u>, <i></i>, <b></b>, <s></s>, <br>, <p>, <sup></sup>, <sub></sub>

Also, custom tags:
    <FI><Fi> for added words
    <CL> = new line (usually at the end of lines)
    <CM> = new paragraph (usually at the end of lines)

e.g.,
    In the beginning of God's preparing the heavens and the earth--
    the earth hath existed waste and void, and darkness <FI>is<Fi> on the face of the deep, and the Spirit of God fluttering on the face of the waters,<CM>
    and God saith, `Let light be;' and light is.
    And God seeth the light that <FI>it is<Fi> good, and God separateth between the light and the darkness,
    and God calleth to the light `Day,' and to the darkness He hath called `Night;' and there is an evening, and there is a morning--day one.<CM>
    And God saith, `Let an expanse be in the midst of the waters, and let it be separating between waters and waters.'
    And God maketh the expanse, and it separateth between the waters which <FI>are<Fi> under the expanse, and the waters which <FI>are<Fi> above the expanse: and it is so.
    And God calleth to the expanse `Heavens;' and there is an evening, and there is a morning--day second.<CM>
"""

ProgName = "TheWord Bible format handler"
ProgVersion = "0.02"
ProgNameVersion = "{} v{}".format( ProgName, ProgVersion )


import logging, os
from gettext import gettext as _
import multiprocessing

import Globals
from Bible import Bible, BibleBook
from BibleOrganizationalSystems import BibleOrganizationalSystem


filenameEndingsToAccept = ('.OT','.NT','.ONT','.OTX','.NTX','.ONTX',) # Must be UPPERCASE
#filenameEndingsToIgnore = ('.ZIP.GO', '.ZIP.DATA',) # Must be UPPERCASE
#extensionsToIgnore = ('ZIP', 'BAK', 'LOG', 'HTM','HTML', 'XML', 'OSIS', 'USX', 'STY', 'LDS', 'SSF', 'VRS',) # Must be UPPERCASE



def TheWordBibleFileCheck( givenFolderName, strictCheck=True, autoLoad=False ):
    """
    Given a folder, search for TheWord Bible files or folders in the folder and in the next level down.

    Returns False if an error is found.

    if autoLoad is false (default)
        returns None, or the number of Bibles found.

    if autoLoad is true and exactly one TheWord Bible is found,
        returns the loaded TheWordBible object.
    """
    if Globals.verbosityLevel > 2: print( "TheWordBibleFileCheck( {}, {}, {} )".format( givenFolderName, strictCheck, autoLoad ) )
    if Globals.debugFlag: assert( givenFolderName and isinstance( givenFolderName, str ) )
    if Globals.debugFlag: assert( autoLoad in (True,False,) )

    # Check that the given folder is readable
    if not os.access( givenFolderName, os.R_OK ):
        logging.critical( _("TheWordBibleFileCheck: Given '{}' folder is unreadable").format( givenFolderName ) )
        return False
    if not os.path.isdir( givenFolderName ):
        logging.critical( _("TheWordBibleFileCheck: Given '{}' path is not a folder").format( givenFolderName ) )
        return False

    # Find all the files and folders in this folder
    if Globals.verbosityLevel > 3: print( " TheWordBibleFileCheck: Looking for files in given {}".format( givenFolderName ) )
    foundFolders, foundFiles = [], []
    for something in os.listdir( givenFolderName ):
        somepath = os.path.join( givenFolderName, something )
        if os.path.isdir( somepath ): foundFolders.append( something )
        elif os.path.isfile( somepath ):
            somethingUpper = something.upper()
            somethingUpperProper, somethingUpperExt = os.path.splitext( somethingUpper )
            #ignore = False
            #for ending in filenameEndingsToIgnore:
                #if somethingUpper.endswith( ending): ignore=True; break
            #if ignore: continue
            #if not somethingUpperExt[1:] in extensionsToIgnore: # Compare without the first dot
            if somethingUpperExt in filenameEndingsToAccept:
                foundFiles.append( something )
    if '__MACOSX' in foundFolders:
        foundFolders.remove( '__MACOSX' )  # don't visit these directories

    # See if there's an TheWordBible project here in this given folder
    numFound = 0
    looksHopeful = False
    lastFilenameFound = None
    for thisFilename in sorted( foundFiles ):
        lastFilenameFound = thisFilename
        numFound += 1
    if numFound:
        if Globals.verbosityLevel > 2: print( "TheWordBibleFileCheck got", numFound, givenFolderName, lastFilenameFound )
        if numFound == 1 and autoLoad:
            twB = TheWordBible( givenFolderName, lastFilenameFound )
            twB.load() # Load and process the file
            return twB
        return numFound
    elif looksHopeful and Globals.verbosityLevel > 2: print( "    Looked hopeful but no actual files found" )

    # Look one level down
    numFound = 0
    foundProjects = []
    for thisFolderName in sorted( foundFolders ):
        tryFolderName = os.path.join( givenFolderName, thisFolderName+'/' )
        if not os.access( tryFolderName, os.R_OK ): # The subfolder is not readable
            logging.warning( _("TheWordBibleFileCheck: '{}' subfolder is unreadable").format( tryFolderName ) )
            continue
        if Globals.verbosityLevel > 3: print( "    TheWordBibleFileCheck: Looking for files in {}".format( tryFolderName ) )
        foundSubfolders, foundSubfiles = [], []
        for something in os.listdir( tryFolderName ):
            somepath = os.path.join( givenFolderName, thisFolderName, something )
            if os.path.isdir( somepath ): foundSubfolders.append( something )
            elif os.path.isfile( somepath ):
                somethingUpper = something.upper()
                somethingUpperProper, somethingUpperExt = os.path.splitext( somethingUpper )
                #ignore = False
                #for ending in filenameEndingsToIgnore:
                    #if somethingUpper.endswith( ending): ignore=True; break
                #if ignore: continue
                #if not somethingUpperExt[1:] in extensionsToIgnore: # Compare without the first dot
                if somethingUpperExt in filenameEndingsToAccept:
                    foundSubfiles.append( something )

        # See if there's an TW project here in this folder
        for thisFilename in sorted( foundSubfiles ):
            foundProjects.append( (tryFolderName, thisFilename,) )
            lastFilenameFound = thisFilename
            numFound += 1
    if numFound:
        if Globals.verbosityLevel > 2: print( "TheWordBibleFileCheck foundProjects", numFound, foundProjects )
        if numFound == 1 and autoLoad:
            if Globals.debugFlag: assert( len(foundProjects) == 1 )
            twB = TheWordBible( foundProjects[0][0], foundProjects[0][1] )
            twB.load() # Load and process the file
            return twB
        return numFound
# end of TheWordBibleFileCheck



class TheWordBible( Bible ):
    """
    Class for reading, validating, and converting TheWordBible files.
    """
    def __init__( self, sourceFolder, givenFilename, encoding='utf-8' ):
        """
        Constructor: just sets up the Bible object.
        """
         # Setup and initialise the base class first
        Bible.__init__( self )
        self.objectNameString = 'TheWord Bible object'
        self.objectTypeString = 'TheWord'

        # Now we can set our object variables
        self.sourceFolder, self.sourceFilename, self.encoding = sourceFolder, givenFilename, encoding
        self.sourceFilepath =  os.path.join( self.sourceFolder, self.sourceFilename )

        # Do a preliminary check on the readability of our file
        if not os.access( self.sourceFilepath, os.R_OK ):
            logging.critical( _("TheWordBible: File '{}' is unreadable").format( self.sourceFilepath ) )

        filenameBits = os.path.splitext( self.sourceFilename )
        self.name = filenameBits[0]
        self.fileExtension = filenameBits[1]

        if self.fileExtension.upper().endswith('X'):
            logging.warning( _("TheWordBible: File '{}' is encrypted").format( self.sourceFilepath ) )
    # end of TheWordBible.__init__


    def load( self ):
        """
        Load a single source file and load book elements.
        """
        if Globals.verbosityLevel > 2: print( _("Loading {}...").format( self.sourceFilepath ) )

        fileExtensionUpper = self.fileExtension.upper()
        assert( fileExtensionUpper in filenameEndingsToAccept )
        if fileExtensionUpper.endswith('X'):
            logging.error( _("TheWordBible: File '{}' is encrypted").format( self.sourceFilepath ) )
            return

        if fileExtensionUpper in ('.ONT','.ONTX',):
            testament, BBB = 'BOTH', 'GEN'
            booksExpected, textLineCountExpected = 66, 31102
        elif fileExtensionUpper in ('.OT','.OTX',):
            testament, BBB = 'OT', 'GEN'
            booksExpected, textLineCountExpected = 39, 23145
        elif fileExtensionUpper in ('.NT','.NTX',):
            testament, BBB = 'NT', 'MAT'
            booksExpected, textLineCountExpected = 27, 7957

        BOS = BibleOrganizationalSystem( "GENERIC-KJV-66-ENG" )

        # Create the first book
        thisBook = BibleBook( BBB )
        thisBook.objectNameString = "TheWord Bible Book object"
        thisBook.objectTypeString = "TheWord"

        verseList = BOS.getNumVersesList( BBB )
        numC, numV = len(verseList), verseList[0]
        C = V = 1

        lastLine, lineCount, bookCount = '', 0, 0
        continued = haveParagraph = False
        encodings = ['utf-8', 'ISO-8859-15', 'ISO-8859-1']
        encodings.remove( self.encoding ) # Remove the given encoding if included
        if self.encoding: encodings.insert( 0, self.encoding ) # Put the given encoding back in in the first position
        for encoding in encodings: # Start by trying the given encoding
            try:
                with open( self.sourceFilepath, 'rt', encoding=encoding ) as myFile: # Automatically closes the file when done
                    for line in myFile:
                        lineCount += 1
                        if lineCount==1 and self.encoding.lower()=='utf-8' and line[0]==chr(65279): #U+FEFF
                            logging.info( "      TheWordBible.load: Detected UTF-16 Byte Order Marker" )
                            line = line[1:] # Remove the UTF-8 Byte Order Marker
                        if line[-1]=='\n': line=line[:-1] # Removing trailing newline character
                        lastLine = line

                        if lineCount <= textLineCountExpected: # assume it's verse text
                            #print ( lineCount, BBB, C, V, 'TW file line is "' + line + '"' )
                            if not line: logging.warning( "TheWordBible.load: Found blank verse line at {} {} {}:{}".format( lineCount, BBB, C, V ) )

                            # Try to convert display formatting to semantic formatting as much as possible
                            # Adjust paragraph formatting
                            assert( not haveParagraph )
                            if line.endswith( '<CM>' ): # Means start a new paragraph after this line
                                line = line[:-4] # Remove the marker
                                haveParagraph = 'CM'
                            elif line.endswith( '<CI>' ): # Means start a new paragraph (without a space before it) after this line
                                line = line[:-4] # Remove the marker
                                haveParagraph = 'CI'
                            elif line.endswith( '<CL>' ): # Means start on a new line
                                line = line[:-4] # Remove the marker
                                haveParagraph = 'CL'

                            # Adjust line formatting
                            line = line.replace('<TS1>','\\mt1 ').replace('<Ts1>','\\NL*') # Start marker and then a newline at end
                            line = line.replace('<TS2>','\\mt2 ').replace('<Ts2>','\\NL*')
                            line = line.replace('<TS3>','\\mt3 ').replace('<Ts3>','\\NL*')

                            # Adjust character formatting with USFM equivalents
                            line = line.replace('<FI>','\\add ').replace('<Fi>','\\add*')
                            line = line.replace('<FO>','\\qt ').replace('<Fo>','\\qt*')
                            line = line.replace('<FR>','\\wj ').replace('<Fr>','\\wj*')
                            line = line.replace('<FU>','\\ul ').replace('<Fu>','\\ul*') # Not USFM
                            line = line.replace('<RF q=*>','\\f ').replace('<Rf>','\\f*')
                            line = line.replace('<RF>','\\f ').replace('<Rf>','\\f*')
                            line = line.replace('<RX>','\\x ').replace('<Rx>','\\x*')

                            # Simple HTML tags (with no semantic info)
                            line = line.replace('<b>','\\bd ').replace('</b>','\\bd*')
                            line = line.replace('<i>','\\it ').replace('</i>','\\it*')
                            line = line.replace('<u>','\\ul ').replace('</u>','\\ul*') # Not USFM

                            # Unhandled stuff -- not done properly yet...............................................
                            line = line.replace('<CI>','')
                            line = line.replace('<CM>','')
                            line = line.replace('<PF0>','')
                            line = line.replace('<PF1>','')
                            line = line.replace('<PF2>','')
                            line = line.replace('<PF3>','')
                            line = line.replace('<PI1>','')
                            line = line.replace('<PI2>','')
                            line = line.replace('<PI3>','')

                            # Check what's left at the end
                            if '<' in line or '>' in line:
                                logging.error( "TheWordBible.load: Doesn't handle formatted line yet: '{}'".format( line ) )

                            if '\\NL*' in line: # We need to break the original line into different USFM markers
                                #print( "Messing with segments: '{}'".format( line ) )
                                segments = line.split( '\\NL*' )
                                assert( len(segments) >= 2 )
                                for segment in segments:
                                    if segment[0] == '\\':
                                        bits = segment.split( None, 1 )
                                        assert( len(bits) == 2 )
                                        if bits[0] in ('\\mt1','\\mt2','\\mt3',):
                                            thisBook.appendLine( bits[0][1:], bits[1] )
                                        else: halt # programming error
                                    else:
                                        if V==1: thisBook.appendLine( 'c', str(C) )
                                        thisBook.appendLine( 'v', '{} {}'.format( V, segment ) )
                            else:
                                if V==1: thisBook.appendLine( 'c', str(C) )
                                thisBook.appendLine( 'v', '{} {}'.format( V, line ) )
                            V += 1
                            if V > numV:
                                C += 1
                                if C > numC: # Save this book now
                                    if Globals.verbosityLevel > 3: print( "Saving", BBB, bookCount+1 )
                                    self.saveBook( thisBook )
                                    bookCount += 1
                                    if bookCount >= booksExpected: continue
                                    BBB = BOS.getNextBookCode( BBB )
                                    # Create the next book
                                    thisBook = BibleBook( BBB )
                                    thisBook.objectNameString = "TheWord Bible Book object"
                                    thisBook.objectTypeString = "TheWord"

                                    verseList = BOS.getNumVersesList( BBB )
                                    numC, numV = len(verseList), verseList[0]
                                    C = V = 1
                                    #thisBook.appendLine( 'c', str(C) )
                                else: # next chapter only
                                    #thisBook.appendLine( 'c', str(C) )
                                    numV = verseList[C-1]
                                    V = 1

                            if haveParagraph:
                                thisBook.appendLine( 'p', '' )
                                haveParagraph = False

                        else: # Should be module info at end of file (after all of the verse lines)
                            #print ( lineCount, 'TW file line is "' + line + '"' )
                            if not line: continue # Just discard additional blank lines
                            if line[0] == '#': continue # Just discard comment lines
                            if not continued:
                                if '=' not in line:
                                    logging.error( "Missing equals sign from info line: {} '{}'".format( lineCount, line ) )
                                else: # Seems like a field=something type line
                                    bits = line.split( '=', 1 )
                                    assert( len(bits) == 2 )
                                    fieldName = bits[0]
                                    fieldContents = bits[1]
                                    if line.endswith( '\\' ): continued = True
                                    else: self.settingsDict[fieldName] = fieldContents
                            else: # continued
                                fieldContents += line
                                if not line.endswith( '\\' ):
                                    self.settingsDict[fieldName] = fieldContents
                                    continued = False
                        #if lineCount > 3:
                            #self.saveBook( thisBook )
                            #break

                if lineCount < textLineCountExpected:
                    logging.error( _("TheWord Bible module file seems too short: {}").format( self.sourceFilename ) )
                self.encoding = encoding
                break; # Get out of decoding loop because we were successful
            except UnicodeDecodeError:
                logging.critical( _("TheWord Bible module file fails with encoding: {} {}").format( self.sourceFilename, self.encoding ) )
        #print( self.settingsDict ); halt
        if 'description' in self.settingsDict and len(self.settingsDict['description'])<40: self.name = self.settingsDict['description']
        if 'short.title' in self.settingsDict: self.shortName = self.settingsDict['short.title']
    # end of TheWordBible.load
# end of TheWordBible class



def testTWB( TWBfolder, TWBfilename ):
    # Crudely demonstrate the TheWord Bible class
    import VerseReferences
    #testFolder = "../../../../../Data/Work/Bibles/TheWord modules/" # Must be the same as below

    #TUBfolder = os.path.join( TWBfolder, TWBfilename )
    if Globals.verbosityLevel > 1: print( _("Demonstrating the TheWord Bible class...") )
    if Globals.verbosityLevel > 0: print( "  Test folder is '{}' '{}'".format( TWBfolder, TWBfilename ) )
    tWb = TheWordBible( TWBfolder, TWBfilename )
    tWb.load() # Load and process the file
    if Globals.verbosityLevel > 1: print( tWb ) # Just print a summary
    if tWb:
        if Globals.strictCheckingFlag: tWb.check()
        for reference in ( ('OT','GEN','1','1'), ('OT','GEN','1','3'), ('OT','PSA','3','0'), ('OT','PSA','3','1'), \
                            ('OT','DAN','1','21'),
                            ('NT','MAT','3','5'), ('NT','JDE','1','4'), ('NT','REV','22','21'), \
                            ('DC','BAR','1','1'), ('DC','MA1','1','1'), ('DC','MA2','1','1',), ):
            (t, b, c, v) = reference
            if t=='OT' and len(tWb)==27: continue # Don't bother with OT references if it's only a NT
            if t=='NT' and len(tWb)==39: continue # Don't bother with NT references if it's only a OT
            if t=='DC' and len(tWb)<=66: continue # Don't bother with DC references if it's too small
            svk = VerseReferences.SimpleVerseKey( b, c, v )
            #print( svk, ob.getVerseDataList( reference ) )
            shortText, verseText = svk.getShortText(), tWb.getVerseText( svk )
            if Globals.verbosityLevel > 1: print( reference, shortText, verseText )

        # Now export the Bible and compare the round trip
        #tWb.toTheWord()
        doaResults = tWb.doAllExports()
        if Globals.strictCheckingFlag: # Now compare the original and the derived USX XML files
            outputFolder = "OutputFiles/BOS_TheWordReexport/"
            if Globals.verbosityLevel > 1: print( "\nComparing original and re-exported theWord files..." )
            result = Globals.fileCompare( TWBfilename, TWBfilename, TWBfolder, outputFolder )
            if Globals.debugFlag:
                if not result: halt
# end of testTWB


def demo():
    """
    Main program to handle command line parameters and then run what they want.
    """
    if Globals.verbosityLevel > 0: print( ProgNameVersion )


    #testFolder = "../../../../../Data/Work/Bibles/TheWord modules/"
    testFolder = "Tests/DataFilesForTests/TheWordTest/"


    if 0: # demo the file checking code -- first with the whole folder and then with only one folder
        result1 = TheWordBibleFileCheck( testFolder )
        if Globals.verbosityLevel > 1: print( "TestA1", result1 )
        result2 = TheWordBibleFileCheck( testFolder, autoLoad=True )
        if Globals.verbosityLevel > 1: print( "TestA2", result2 )


    if 1: # all discovered modules in the test folder
        testFolder = "../../../../../Data/Work/Bibles/TheWord modules/"
        foundFolders, foundFiles = [], []
        for something in os.listdir( testFolder ):
            somepath = os.path.join( testFolder, something )
            if os.path.isdir( somepath ): foundFolders.append( something )
            elif os.path.isfile( somepath ): foundFiles.append( something )

        if 0 and Globals.maxProcesses > 1: # Get our subprocesses ready and waiting for work
            if Globals.verbosityLevel > 1: print( "\nTrying all {} discovered modules...".format( len(foundFolders) ) )
            parameters = [filename for filename in sorted(foundFiles)]
            with multiprocessing.Pool( processes=Globals.maxProcesses ) as pool: # start worker processes
                results = pool.map( testTWB, parameters ) # have the pool do our loads
                assert( len(results) == len(parameters) ) # Results (all None) are actually irrelevant to us here
        else: # Just single threaded
            for j, someFile in enumerate( sorted( foundFiles ) ):
                if Globals.verbosityLevel > 1: print( "\n{}/ Trying {}".format( j+1, someFile ) )
                #myTestFolder = os.path.join( testFolder, someFolder+'/' )
                testTWB( testFolder, someFile )
                #break # only do the first one.........temp
# end of demo

if __name__ == '__main__':
    # Configure basic set-up
    parser = Globals.setup( ProgName, ProgVersion )
    Globals.addStandardOptionsAndProcess( parser )

    multiprocessing.freeze_support() # Multiprocessing support for frozen Windows executables

    demo()

    Globals.closedown( ProgName, ProgVersion )
# end of TheWordBible.py