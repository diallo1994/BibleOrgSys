#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ESFMBibleBook.py
#
# Module handling the ESFM markers for Bible books
#
# Copyright (C) 2010-2018 Robert Hunt
# Author: Robert Hunt <Freely.Given.org@gmail.com>
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
Module for defining and manipulating ESFM Bible books.
"""

from gettext import gettext as _

LastModifiedDate = '2018-03-08' # by RJH
ShortProgName = "USFMBibleBook"
ProgName = "ESFM Bible book handler"
ProgVersion = '0.48'
ProgNameVersion = '{} v{}'.format( ShortProgName, ProgVersion )
ProgNameVersionDate = '{} {} {}'.format( ProgNameVersion, _("last modified"), LastModifiedDate )

debuggingThisModule = False


import os, logging

import BibleOrgSysGlobals, USFMMarkers
from ESFMFile import ESFMFile
from Bible import BibleBook


ESFM_SEMANTIC_TAGS = 'AGLOPQTS' # S is put last coz it must be the last tag if there are multiple tags
ESFM_STRONGS_TAGS = 'HG'


sortedNLMarkers = None

class ESFMBibleBook( BibleBook ):
    """
    Class to load and manipulate a single ESFM file / book.
    """

    def __init__( self, containerBibleObject, BBB ):
        """
        Create the ESFM Bible book object.
        """
        BibleBook.__init__( self, containerBibleObject, BBB ) # Initialise the base class
        self.objectNameString = 'ESFM Bible Book object'
        self.objectTypeString = 'ESFM'

        global sortedNLMarkers
        if sortedNLMarkers is None:
            sortedNLMarkers = sorted( BibleOrgSysGlobals.USFMMarkers.getNewlineMarkersList('Combined'), key=len, reverse=True )
    # end of __init__


    def load( self, filename, folder=None ):
        """
        Load the ESFM Bible book from a file.

        Tries to combine physical lines into logical lines,
            i.e., so that all lines begin with a ESFM paragraph marker.

        Uses the addLine function of the base class to save the lines.

        Note: the base class later on will try to break apart lines with a paragraph marker in the middle --
                we don't need to worry about that here.
        """
        if debuggingThisModule or BibleOrgSysGlobals.debugFlag:
            print( "ESFM.load( {}, {} )".format( filename, folder ) )


        def ESFMPreprocessing( BBB, C, V, marker, originalText ):
            """
            Converts ESFM tagging to pseudo-USFM codes for easier handling later on.

            Parameters:
                BBB, C, V parameters are just for use in error messages
                originalText is the text line from the file

            Returns:
                A string replacement to use instead of originalText

            Converts:
                XXX=PYYYY to \dic PXXX=YYY\dic*
                    e.g., "{the three lepers}=PMat6Lepers" to "the three lepers\dic Pthe_three_lepers=Mat6lepers\dic*"
                i.e, braces and equal signs are removed from the text
                    and the information is placed in a \dic field.

            Note: This DOESN'T remove the underline/underscore characters used to join translated words
                which were one word in the original, e.g., went_down
            """
            if (debuggingThisModule or BibleOrgSysGlobals.debugFlag) \
            and len(originalText)>5: # Don't display for "blank" lines (like '\v 10 ')
                print( "\n\nESFMPreprocessing( {} {}:{}, {}, {!r} )".format( BBB, C, V, marker, originalText ) )


            def saveWord( BBB, C, V, word ):
                """
                """
                if debuggingThisModule or BibleOrgSysGlobals.debugFlag:
                    print( "ESFM saveWord( {}, {}:{}, {!r} )".format( BBB, C, V, word ) )
                assert word and ' ' not in word
            # end of saveWord

            def saveSemanticTag( BBB, C, V, word, tag ):
                """
                Fills the semantic dictionary with keys:
                    'Tag errors': contains a list of 4-tuples (BBB,C,V,errorWord)
                    'Missing': contains a dictionary
                    'A' 'G' 'L' 'O' 'P' 'Q' entries each containing a dictionary
                        where the key is the name (e.g., 'Jonah')
                        and the entry is a list of 4-tuples (BBB,C,V,actualWord)

                Returns a character SFM field to be inserted into the line
                    (for better compatibility with the software chain).
                """
                #if C=='4' and V in ('11','12'):
                if debuggingThisModule or BibleOrgSysGlobals.debugFlag:
                    print( "ESFM saveSemanticTag( {} {}:{}, {!r}, {!r} )".format( BBB, C, V, word, tag ) )
                assert word and ' ' not in word
                assert tag and tag[0]=='=' and len(tag)>=2
                tagMarker, tagContent = tag[1], tag[2:]

                thisDict = self.containerBibleObject.semanticDict
                if tagMarker not in ESFM_SEMANTIC_TAGS:
                    loadErrors.append( _("{} {}:{} unknown ESFM {!r} tag content {!r}").format( self.BBB, C, V, tagMarker, tagContent ) )
                    logging.error( "ESFM tagging error in {} {}:{}: unknown {!r} tag in {!r}".format( BBB, C, V, tagMarker, tag ) )
                    self.addPriorityError( 15, C, V, _("Unknown ESFM semantic tag") )
                    if 'Tag errors' not in thisDict: thisDict['Tag errors'] = []
                    thisDict['Tag errors'].append( (BBB,C,V,tag[1:]) )
                if not tagContent: tagContent = word

                # Now look in the semantic database
                if tagMarker in thisDict \
                and tagContent in thisDict[tagMarker]:
                    thisDict[tagMarker][tagContent].append( (BBB,C,V,word) )
                    #print( "Now have {}:{}={}".format( tagMarker, tagContent, thisDict[tagMarker][tagContent] ) )
                else: # couldn't find it
                    loadErrors.append( _("{} {}:{} unknown ESFM {!r} tag content {!r}").format( self.BBB, C, V, tagMarker, tagContent ) )
                    logging.error( "ESFM tagging error in {} {}:{}: unknown {!r} tag content {!r}".format( BBB, C, V, tagMarker, tagContent ) )
                    self.addPriorityError( 15, C, V, _("Unknown ESFM semantic tag") )
                    if 'Missing' not in thisDict: thisDict['Missing'] = {}
                    if tagMarker not in thisDict['Missing']: thisDict['Missing'][tagMarker] = {}
                    if tagContent not in thisDict['Missing'][tagMarker]: thisDict['Missing'][tagMarker][tagContent] = []
                    thisDict['Missing'][tagMarker][tagContent].append( (BBB,C,V) if word==tagContent else (BBB,C,V,word) )

                if word==tagContent:
                    return "\\sem {} {}\\sem*".format( tagMarker, word )
                return "\\sem {} {}={}\\sem*".format( tagMarker, word, tagContent )
            # end of saveSemanticTag


            def saveStrongsTag( BBB, C, V, word, tag ):
                """
                Returns a character SFM field to be inserted into the line
                    (for better compatibility with the software chain).
                """
                #if C=='4' and V in ('11','12'):
                if debuggingThisModule or BibleOrgSysGlobals.debugFlag:
                    print( "ESFM saveStrongsTag( {}, {}:{}, {!r}, {!r} )".format( BBB, C, V, word, tag ) )
                assert word and ' ' not in word
                assert tag and tag[0]=='=' and tag[1]=='S' and len(tag)>=3
                tagMarker, tagContent = tag[2], tag[3:]

                thisDict = self.containerBibleObject.StrongsDict
                if tagMarker not in ESFM_STRONGS_TAGS:
                    loadErrors.append( _("{} {}:{} unknown ESFM {!r} tag content {!r}").format( self.BBB, C, V, tagMarker, tagContent ) )
                    logging.error( "ESFM tagging error in {} {}:{}: unknown {!r} tag in {!r}".format( BBB, C, V, tagMarker, tag ) )
                    self.addPriorityError( 10, C, V, _("Unknown ESFM Strong's tag") )
                    if 'Tag errors' not in thisDict: thisDict['Tag errors'] = []
                    thisDict['Tag errors'].append( (BBB,C,V,tag[1:]) )
                if not tagContent: tagContent = word

                # Now look in the Strongs database
                if tagMarker in thisDict \
                and tagContent in thisDict[tagMarker]:
                    thisEntry = thisDict[tagMarker][tagContent]
                    if isinstance( thisEntry, str ):
                        thisDict[tagMarker][tagContent] = [thisEntry] # Convert from a string to a list with the string as the first list item
                    thisDict[tagMarker][tagContent].append( (BBB,C,V,word) )
                    #print( " ", tagMarker, tagContent, thisEntry )
                    #print( "Now have {}:{}={}".format( tagMarker, tagContent, thisDict[tagMarker][tagContent] ) )
                else: # couldn't find it
                    loadErrors.append( _("{} {}:{} unknown ESFM {!r} tag content {!r}").format( self.BBB, C, V, tagMarker, tagContent ) )
                    logging.error( "ESFM tagging error in {} {}:{}: unknown {!r} tag content {!r}".format( BBB, C, V, tagMarker, tagContent ) )
                    self.addPriorityError( 10, C, V, _("Unknown ESFM Strong's tag") )
                    if 'Missing' not in thisDict: thisDict['Missing'] = {}
                    if tagMarker not in thisDict['Missing']: thisDict['Missing'][tagMarker] = {}
                    if tagContent not in thisDict['Missing'][tagMarker]: thisDict['Missing'][tagMarker][tagContent] = []
                    thisDict['Missing'][tagMarker][tagContent].append( (BBB,C,V) if word==tagContent else (BBB,C,V,word) )

                return "\\str {} {}={}\\str*".format( tagMarker, tagContent, word )
            # end of saveStrongsTag


            # Main code for ESFMPreprocessing
            # Analyse and collect all ESFM tags and special characters,
            #    and put the results into USFM type character fields
            bracedGroupFlag = underlineGroupFlag = startsWithUnderline = False
            word = underlineGroup = bracedGroupText = tagText = ''
            # The tag is the bit starting with =, e.g., '=PJonah'
            hangingUnderlineCount = 0 # Count of unclosed '…_ ' sequences
            lastChar = ''
            #textLen = len( originalText )
            resultText = ''
            firstWordFlag = True
            #print( 'ESFMPreprocessing {} {}:{}'.format( BBB, C, V ) )
            for j, originalChar in enumerate( originalText ):
                char = originalChar
                #nextChar = originalText[j+1] if j<textLen-1 else ''

                #if '{'  in originalText or '_' in originalText or '=' in originalText:
                #if C=='4' and V=='11':
                #print( "  ESFMPreprocessing {}={!r} lc={!r} uGF={} hUC={} uL={!r} bGF={} bG={!r} tg={!r} \n    oT={!r} \n    rT={!r}" \
                    #.format( j, originalChar, lastChar, underlineGroupFlag, hangingUnderlineCount, underlineGroup, bracedGroupFlag, bracedGroup, tag, originalText, resultText ) )

                # Handle hanging underlines, e.g., 'and_ ' or ' _then' or 'and_ they_ _were_ _not _ashamed'
                if char == ' ':
                    if lastChar == '_':
                        hangingUnderlineCount += 1
                        assert hangingUnderlineCount < 3
                        #assert resultText[-1] == ' '
                        #resultText = resultText[:-1] # Remove the space from the underline otherwise we'll get two spaces
                    if lastChar != '_' and (not underlineGroupFlag) and hangingUnderlineCount!=0:
                        #if underlineGroup: print( "underlineGroup was: {!r}".format( underlineGroup ) )
                        underlineGroup = ''
                #if lastChar == ' ':
                    #startsWithUnderline =  char == '_'
                    #if char == ' ': hangingUnderlineCount += 1
                elif char == '_':
                    if lastChar == ' ':
                        hangingUnderlineCount -= 1
                        if hangingUnderlineCount < 0:
                            loadErrors.append( _("{} {}:{} missing first part of ESFM underline group at position {}").format( self.BBB, C, V, j ) )
                            logging.error( "ESFM underlining error at {} in {} {}:{}".format( j, BBB, C, V ) )
                            self.addPriorityError( 10, C, V, _("Missing first part of ESFM underline group") )
                            hangingUnderlineCount = 0 # recover

                if bracedGroupFlag:
                    if char == '}': bracedGroupFlag = False
                    else: bracedGroupText += '_' if char==' ' else char

                # Handle formation of output string but with tagged text converted into internal SFM fields
                #     e.g., 'And_ Elohim=G=SH430 _said=SH559:'
                #   becomes 'And_ Elohim\sem G Elohim\sem*\str H 430=Elohim\str* _said\str H 559=said\str*:'
                if tagText:
                    if BibleOrgSysGlobals.strictCheckingFlag or BibleOrgSysGlobals.debugFlag: assert tagText[0] == '='
                    if char in ' _=' or char in BibleOrgSysGlobals.ALL_WORD_PUNCT_CHARS: # Note: A forward slash is permitted
                        if underlineGroupFlag:
                            underlineGroup += word
                            if char == '_': underlineGroup += char
                            else: underlineGroupFlag = False
                        if len(tagText) > 1:
                            if tagText[1]=='S':
                                resultText += saveStrongsTag( BBB, C, V, underlineGroup if underlineGroup else word, tagText )
                                underlineGroup = ''
                                underlineGroupFlag = hangingUnderlineFlag = False
                            elif bracedGroupText or word:
                                resultText += saveSemanticTag( BBB, C, V, bracedGroupText if bracedGroupText else word, tagText )
                            else: # WEB Luke 16:7 contains a footnote: \f + \ft 100 cors = about 2,110 liters or 600 bushels.\f*
                                logging.critical( "Something funny with special symbol {!r} at {} {}:{}".format( char, BBB, C, V ) )
                                if BibleOrgSysGlobals.debugFlag or debuggingThisModule: halt
                            if char == '_':
                                if not underlineGroupFlag: # it's just starting now
                                    underlineGroup += word + char
                                    underlineGroupFlag = True
                                char = ' ' # to go into resultText
                            elif char != '=': underlineGroupFlag = False
                            if char == '=': tagText = char # Started a new consecutive tag
                            else:
                                if word:
                                    saveWord( BBB, C, V, word )
                                    firstWordFlag = False
                                word = bracedGroupText = tagText = ''
                                if char!='}': resultText += char
                        else:
                            loadErrors.append( _("{} {}:{} unexpected short ESFM tag at {}={!r} in {!r}").format( self.BBB, C, V, j, originalChar, originalText ) )
                            logging.error( "ESFM tagging error in {} {}:{}: unexpected short tag at {}={!r} in {!r}".format( BBB, C, V, j, originalChar, originalText ) )
                            self.addPriorityError( 21, C, V, _("Unexpected ESFM short tag") )
                    else: # still in tag
                        tagText += char
                else: # not in tag
                    if char == '=':
                        assert not tagText
                        tagText = char
                    else: # still not in tag
                        if char == '{':
                            if (lastChar and lastChar!=' ') or tagText or bracedGroupFlag or bracedGroupText:
                                loadErrors.append( _("{} {}:{} unexpected ESFM opening brace at {}={!r} in {!r}").format( self.BBB, C, V, j, originalChar, originalText ) )
                                logging.error( "ESFM tagging error in {} {}:{}: unexpected opening brace at {}={!r} in {!r}".format( BBB, C, V, j, originalChar, originalText ) )
                                self.addPriorityError( 20, C, V, _("Unexpected ESFM opening brace") )
                            bracedGroupFlag = True
                            char = '' # nothing to go into resultText
                        elif char in ' _' or char in BibleOrgSysGlobals.DASH_CHARS:
                            if underlineGroupFlag:
                                underlineGroup += word
                                if char == '_':
                                    underlineGroup += char
                                    #char = ' ' # to go into resultText
                                else: underlineGroupFlag = False
                            elif char == ' ':
                                underlineGroupFlag = False
                                if startsWithUnderline:
                                    underlineGroup += word
                                    startsWithUnderline = False
                            elif char == '_':
                                if hangingUnderlineCount > 0:
                                    #char = '' # nothing to go into resultText
                                    #hangingUnderlineCount -= 1# underlineGroupFlag will be set instead below
                                    pass
                                else: # not hanging underline
                                    underlineGroup += word + char
                                    #char = ' ' # to go into resultText
                                underlineGroupFlag = True
                            if word:
                                if marker == 'v' and not firstWordFlag:
                                    saveWord( BBB, C, V, word )
                                firstWordFlag = False
                            word = ''
                        elif char!='}': word += char
                        if char!='}': resultText += char
                lastChar = originalChar

            #else: # TEMP: just remove all ESFM tags and special characters
                #inTag = False
                #for char in originalText:
                    #if inTag:
                        #if char in ' _' or char in BibleOrgSysGlobals.ALL_WORD_PUNCT_CHARS: # Note: A forward slash is permitted
                            #inTag = False
                            #resultText += char
                    #else: # not in tag
                        #if char == '=': inTag = True; continue
                        #resultText += char
                #resultText = resultText.replace('{','').replace('}','').replace('_(',' ').replace(')_',' ').replace('_',' ')

            if debuggingThisModule and resultText != originalText:
                print( "from: {!r}".format( originalText ) )
                print( " got: {!r}".format( resultText ) )
                #assert originalText.count('_') == resultText.count('_') Not necessarily true
            elif BibleOrgSysGlobals.strictCheckingFlag or (BibleOrgSysGlobals.debugFlag and debuggingThisModule) \
            and ('{'  in originalText or '}' in originalText or '=' in originalText):
                print( "original:", repr(originalText) )
                print( "returned:", repr(resultText) )

            return resultText
        # end of ESFMBibleBook.ESFMPreprocessing


        def doaddLine( originalMarker, originalText ):
            """
            Check for newLine markers within the line (if so, break the line)
                and save the information in our database.

            Also checks for matching underlines.

            Also convert ~ to a proper non-break space.
            """
            #if (debuggingThisModule or BibleOrgSysGlobals.verbosityLevel > 1) \
                #and (originalMarker not in ('c','v') or len(originalText)>5): # Don't display for "blank" lines (like '\v 10 ')
                #print( "ESFM doaddLine( {!r}, {!r} )".format( originalMarker, originalText ) )

            marker, text = originalMarker, originalText.replace( '~', ' ' )
            marker = BibleOrgSysGlobals.USFMMarkers.toStandardMarker( originalMarker )
            if marker != originalMarker:
                loadErrors.append( _("{} {}:{} ESFM doesn't allow unnumbered marker \\{}: {!r}").format( self.BBB, C, V, originalMarker, originalText ) )
                logging.error( _("ESFM doesn't allow the unnumbered marker after {} {}:{} in \\{}: {!r}").format( self.BBB, C, V, originalMarker, originalText ) )
                self.addPriorityError( 90, C, V, _("ESFM doesn't allow unnumbered markers") )

            if '\\' in text: # Check markers inside the lines
                markerList = BibleOrgSysGlobals.USFMMarkers.getMarkerListFromText( text )
                ix = 0
                for insideMarker, iMIndex, nextSignificantChar, fullMarker, characterContext, endIndex, markerField in markerList: # check paragraph markers
                    if insideMarker == '\\': # it's a free-standing backspace
                        loadErrors.append( _("{} {}:{} Improper free-standing backspace character within line in \\{}: {!r}").format( self.BBB, C, V, marker, text ) )
                        logging.error( _("Improper free-standing backspace character within line after {} {}:{} in \\{}: {!r}").format( self.BBB, C, V, marker, text ) ) # Only log the first error in the line
                        self.addPriorityError( 100, C, V, _("Improper free-standing backspace character inside a line") )
                    elif BibleOrgSysGlobals.USFMMarkers.isNewlineMarker(insideMarker): # Need to split the line for everything else to work properly
                        if ix==0:
                            loadErrors.append( _("{} {}:{} NewLine marker {!r} shouldn't appear within line in \\{}: {!r}").format( self.BBB, C, V, insideMarker, marker, text ) )
                            logging.error( _("NewLine marker {!r} shouldn't appear within line after {} {}:{} in \\{}: {!r}").format( insideMarker, self.BBB, C, V, marker, text ) ) # Only log the first error in the line
                            self.addPriorityError( 96, C, V, _("NewLine marker \\{} shouldn't be inside a line").format( insideMarker ) )
                        thisText = text[ix:iMIndex].rstrip()
                        self.addLine( marker, thisText )
                        ix = iMIndex + 1 + len(insideMarker) + len(nextSignificantChar) # Get the start of the next text -- the 1 is for the backslash
                        #print( "Did a split from {}:{!r} to {}:{!r} leaving {}:{!r}".format( originalMarker, originalText, marker, thisText, insideMarker, text[ix:] ) )
                        marker = BibleOrgSysGlobals.USFMMarkers.toStandardMarker( insideMarker ) # setup for the next line
                        if marker != insideMarker:
                            loadErrors.append( _("{} {}:{} ESFM doesn't allow unnumbered marker within line \\{}: {!r}").format( self.BBB, C, V, insideMarker, originalText ) )
                            logging.error( _("ESFM doesn't allow the unnumbered marker within line after {} {}:{} in \\{}: {!r}").format( self.BBB, C, V, insideMarker, originalText ) )
                            self.addPriorityError( 90, C, V, _("ESFM doesn't allow unnumbered markers") )

                if ix != 0: # We must have separated multiple lines
                    text = text[ix:] # Get the final bit of the line

            if '_' in text:
                # Should this code be somewhere more general, e.g., in InternalBibleBook.py ???
                leftCount, rightCount = text.count( '_ ' ), text.count( ' _' )
                if leftCount > rightCount:
                    loadErrors.append( _("{} {}:{} Too many '_ ' sequences in {} text: {}").format( self.BBB, C, V, marker, text ) )
                    logging.warning( _("Too many '_ ' sequences in {} line after {} {}:{} at beginning of line with text: {!r}").format( marker, self.BBB, C, V, text ) )
                elif leftCount < rightCount:
                    loadErrors.append( _("{} {}:{} Too many ' _' sequences in {} text: {}").format( self.BBB, C, V, marker, text ) )
                    logging.warning( _("Too many ' _' sequences in {} line after {} {}:{} at beginning of line with text: {!r}").format( marker, self.BBB, C, V, text ) )

            self.addLine( marker, text ) # Call the function in the base class to save the line (or the remainder of the line if we split it above)
        # end of ESFMBibleBook.doaddLine


        # Main code for ESFMBibleBook.load
        if BibleOrgSysGlobals.verbosityLevel > 2: print( "  " + _("Loading {}…").format( filename ) )
        #self.BBB = BBB
        #self.isSingleChapterBook = BibleOrgSysGlobals.BibleBooksCodes.isSingleChapterBook( BBB )
        self.sourceFilename = filename
        self.sourceFolder = folder
        self.sourceFilepath = os.path.join( folder, filename ) if folder else filename
        originalBook = ESFMFile()
        originalBook.read( self.sourceFilepath )

        # Do some important cleaning up before we save the data
        C, V = '-1', '-1' # So first/id line starts at -1:0
        lastMarker = lastText = ''
        loadErrors = []
        for marker,originalText in originalBook.lines: # Always process a line behind in case we have to combine lines
            #print( "After {} {}:{} \\{} {!r}".format( self.BBB, C, V, marker, originalText ) )

            # Keep track of where we are for more helpful error messages
            if marker=='c' and originalText: C, V = originalText.split()[0], '0'
            elif marker=='v' and originalText:
                V = originalText.split()[0]
                if C == '-1': C = '1' # Some single chapter books don't have an explicit chapter 1 marker
            elif C == '-1' and marker!='intro': V = str( int(V) + 1 )
            elif marker=='restore': continue # Ignore these lines completely

            # Now load the actual Bible book data
            if marker in USFMMarkers.OFTEN_IGNORED_USFM_HEADER_MARKERS:
                text = originalText
            else:
                text = ESFMPreprocessing( self.BBB, C, V, marker, originalText ) # Convert ESFM encoding to pseudo-USFM
            if BibleOrgSysGlobals.USFMMarkers.isNewlineMarker( marker ):
                if lastMarker: doaddLine( lastMarker, lastText )
                lastMarker, lastText = marker, text
            elif BibleOrgSysGlobals.USFMMarkers.isInternalMarker( marker ) \
            or marker.endswith('*') and BibleOrgSysGlobals.USFMMarkers.isInternalMarker( marker[:-1] ): # the line begins with an internal marker -- append it to the previous line
                if text:
                    loadErrors.append( _("{} {}:{} Found '\\{}' internal marker at beginning of line with text: {!r}").format( self.BBB, C, V, marker, text ) )
                    logging.warning( _("Found '\\{}' internal marker after {} {}:{} at beginning of line with text: {!r}").format( marker, self.BBB, C, V, text ) )
                else: # no text
                    loadErrors.append( _("{} {}:{} Found '\\{}' internal marker at beginning of line (with no text)").format( self.BBB, C, V, marker ) )
                    logging.warning( _("Found '\\{}' internal marker after {} {}:{} at beginning of line (with no text)").format( marker, self.BBB, C, V ) )
                self.addPriorityError( 27, C, V, _("Found \\{} internal marker on new line in file").format( marker ) )
                if not lastText.endswith(' '): lastText += ' ' # Not always good to add a space, but it's their fault!
                lastText +=  '\\' + marker + ' ' + text
                if BibleOrgSysGlobals.verbosityLevel > 3: print( "{} {} {} Appended {}:{!r} to get combined line {}:{!r}".format( self.BBB, C, V, marker, text, lastMarker, lastText ) )
            elif BibleOrgSysGlobals.USFMMarkers.isNoteMarker( marker ) \
            or marker.endswith('*') and BibleOrgSysGlobals.USFMMarkers.isNoteMarker( marker[:-1] ): # the line begins with a note marker -- append it to the previous line
                if text:
                    loadErrors.append( _("{} {}:{} Found '\\{}' note marker at beginning of line with text: {!r}").format( self.BBB, C, V, marker, text ) )
                    logging.warning( _("Found '\\{}' note marker after {} {}:{} at beginning of line with text: {!r}").format( marker, self.BBB, C, V, text ) )
                else: # no text
                    loadErrors.append( _("{} {}:{} Found '\\{}' note marker at beginning of line (with no text)").format( self.BBB, C, V, marker ) )
                    logging.warning( _("Found '\\{}' note marker after {} {}:{} at beginning of line (with no text)").format( marker, self.BBB, C, V ) )
                self.addPriorityError( 26, C, V, _("Found \\{} note marker on new line in file").format( marker ) )
                if not lastText.endswith(' ') and marker!='f': lastText += ' ' # Not always good to add a space, but it's their fault! Don't do it for footnotes, though.
                lastText +=  '\\' + marker + ' ' + text
                if BibleOrgSysGlobals.verbosityLevel > 3: print( "{} {} {} Appended {}:{!r} to get combined line {}:{!r}".format( self.BBB, C, V, marker, text, lastMarker, lastText ) )
            else: # the line begins with an unknown marker (ESFM doesn't allow custom markers)
                if text:
                    loadErrors.append( _("{} {}:{} Found '\\{}' unknown marker at beginning of line with text: {!r}").format( self.BBB, C, V, marker, text ) )
                    logging.error( _("Found '\\{}' unknown marker after {} {}:{} at beginning of line with text: {!r}").format( marker, self.BBB, C, V, text ) )
                else: # no text
                    loadErrors.append( _("{} {}:{} Found '\\{}' unknown marker at beginning of line (with no text").format( self.BBB, C, V, marker ) )
                    logging.error( _("Found '\\{}' unknown marker after {} {}:{} at beginning of line (with no text)").format( marker, self.BBB, C, V ) )
                self.addPriorityError( 100, C, V, _("Found \\{} unknown marker on new line in file").format( marker ) )
                for tryMarker in sortedNLMarkers: # Try to do something intelligent here -- it might be just a missing space
                    if marker.startswith( tryMarker ): # Let's try changing it
                        if lastMarker: doaddLine( lastMarker, lastText )
                        lastMarker, lastText = tryMarker, marker[len(tryMarker):] + ' ' + text
                        loadErrors.append( _("{} {}:{} Changed '\\{}' unknown marker to {!r} at beginning of line: {}").format( self.BBB, C, V, marker, tryMarker, text ) )
                        logging.warning( _("Changed '\\{}' unknown marker to {!r} after {} {}:{} at beginning of line: {}").format( marker, tryMarker, self.BBB, C, V, text ) )
                        break
                # Otherwise, don't bother processing this line -- it'll just cause more problems later on
        if lastMarker: doaddLine( lastMarker, lastText ) # Process the final line

        if not originalBook.lines: # There were no lines!!!
            loadErrors.append( _("{} This ESFM file was totally empty: {}").format( self.BBB, self.sourceFilename ) )
            logging.error( _("ESFM file for {} was totally empty: {}").format( self.BBB, self.sourceFilename ) )
            lastMarker, lastText = 'rem', 'This (ESFM) file was completely empty' # Save something since we had a file at least

        if loadErrors: self.errorDictionary['Load Errors'] = loadErrors
        if 0 and BibleOrgSysGlobals.debugFlag and self.BBB=='JNA':
            for name,thisDict in  ( ('SEM',self.containerBibleObject.semanticDict), ('STR',self.containerBibleObject.StrongsDict) ):
                if 'Tag errors' in thisDict:
                    print( "\n{} Tag errors: {}".format( name, thisDict['Tag errors'] ) )
                if 'Missing' in thisDict:
                    print( "\n{} Missing: {}".format( name, thisDict['Missing'] ) )
                if thisDict == self.containerBibleObject.semanticDict:
                    for tag in ESFM_SEMANTIC_TAGS:
                        if tag in thisDict:
                            print( "\n{} Found {}: {}".format( name, tag, thisDict[tag] ) )
                elif thisDict == self.containerBibleObject.StrongsDict:
                    for tag in ESFM_STRONGS_TAGS:
                        for num in thisDict[tag]:
                            if isinstance( thisDict[tag][num], list ):
                                print( "\n{} Found {} {}: {}".format( name, tag, num, thisDict[tag][num] ) )
            halt
        #if debugging: print( self._rawLines ); halt
    # end of ESFMBibleBook.load
# end of class ESFMBibleBook



def demo():
    """
    Demonstrate reading and processing some ESFM Bible databases.
    """
    if BibleOrgSysGlobals.verbosityLevel > 0: print( ProgNameVersion )


    def demoFile( name, filename, folder, BBB ):
        if BibleOrgSysGlobals.verbosityLevel > 1: print( _("Loading {} from {}…").format( BBB, filename ) )
        EBB = ESFMBibleBook( name, BBB )
        EBB.load( filename, folder )
        if BibleOrgSysGlobals.verbosityLevel > 1: print( "  ID is {!r}".format( EBB.getField( 'id' ) ) )
        if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Header is {!r}".format( EBB.getField( 'h' ) ) )
        if BibleOrgSysGlobals.verbosityLevel > 1: print( "  Main titles are {!r} and {!r}".format( EBB.getField( 'mt1' ), EBB.getField( 'mt2' ) ) )
        #if BibleOrgSysGlobals.verbosityLevel > 0: print( EBB )
        EBB.validateMarkers()
        EBBVersification = EBB.getVersification ()
        if BibleOrgSysGlobals.verbosityLevel > 2: print( EBBVersification )
        UBBAddedUnits = EBB.getAddedUnits ()
        if BibleOrgSysGlobals.verbosityLevel > 2: print( UBBAddedUnits )
        discoveryDict = EBB._discover()
        #print( "discoveryDict", discoveryDict )
        EBB.check()
        EBErrors = EBB.getErrors()
        if BibleOrgSysGlobals.verbosityLevel > 2: print( EBErrors )
    # end of demoFile


    import USFMFilenames

    if 1: # Test individual files
        #name, testFolder, filename, BBB = "WEB", "../../../../../Data/Work/Bibles/English translations/WEB (World English Bible)/2012-06-23 eng-web_usfm/", "06-JOS.usfm", "JOS" # You can put your test file here
        #name, testFolder, filename, BBB = "WEB", "../../../../../Data/Work/Bibles/English translations/WEB (World English Bible)/2012-06-23 eng-web_usfm/", "44-SIR.usfm", "SIR" # You can put your test file here
        #name, testFolder, filename, BBB = "Matigsalug", "../../../../../Data/Work/Matigsalug/Bible/MBTV/", "MBT102SA.SCP", "SA2" # You can put your test file here
        #name, testFolder, filename, BBB = "Matigsalug", "../../../../../Data/Work/Matigsalug/Bible/MBTV/", "MBT15EZR.SCP", "EZR" # You can put your test file here
        name, testFolder, filename, BBB = "Matigsalug", "../../../../../Data/Work/Matigsalug/Bible/MBTV/", "MBT41MAT.SCP", "MAT" # You can put your test file here
        #name, testFolder, filename, BBB = "Matigsalug", "../../../../../Data/Work/Matigsalug/Bible/MBTV/", "MBT67REV.SCP", "REV" # You can put your test file here
        if os.access( testFolder, os.R_OK ):
            demoFile( name, filename, testFolder, BBB )
        else: print( "Sorry, test folder {!r} doesn't exist on this computer.".format( testFolder ) )

    if 1: # Test a whole folder full of files
        name, testFolder = "Matigsalug", "../../../../../Data/Work/Matigsalug/Bible/MBTV/" # You can put your test folder here
        #name, testFolder = "WEB", "../../../../../Data/Work/Bibles/English translations/WEB (World English Bible)/2012-06-23 eng-web_usfm/" # You can put your test folder here
        if os.access( testFolder, os.R_OK ):
            if BibleOrgSysGlobals.verbosityLevel > 1: print( _("Scanning {} from {}…").format( name, testFolder ) )
            fileList = USFMFilenames.USFMFilenames( testFolder ).getMaximumPossibleFilenameTuples()
            for BBB,filename in fileList:
                demoFile( name, filename, testFolder, BBB )
        else: print( "Sorry, test folder {!r} doesn't exist on this computer.".format( testFolder ) )
# end of demo

if __name__ == '__main__':
    # Configure basic set-up
    parser = BibleOrgSysGlobals.setup( ProgName, ProgVersion )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    demo()

    BibleOrgSysGlobals.closedown( ProgName, ProgVersion )
# end of ESFMBibleBook.py
