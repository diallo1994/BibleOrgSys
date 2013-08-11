// ./DataFiles/PunctuationSystems/../DerivedFiles/BiblePunctuationSystems_Tables.c
//
// This UTF-8 file was automatically generated by BiblePunctuationSystems.py V0.43 on 2013-08-09 22:29:13.029764
//
//   3 BiblePunctuationSystem loaded from the original XML file.
//

#include "BiblePunctuationSystems_Tables.h"


// English_brief
const static punctuationByRefEntry
 English_briefBookDataDict[27] = {
  // Fields (2) are const unsigned char referenceAbbreviation[3+1]; const int indexNumber;
  // Sorted by referenceAbbreviation
  {"allowedVerseSuffixes", "abcdef"},
  {"bookBridgeCharacter", "-"},
  {"bookChapterSeparator", " "},
  {"bookSeparator", ";"},
  {"booknameCase", "ME"},
  {"booknameLength", "3"},
  {"chapterBridgeCharacter", "-"},
  {"chapterSeparator", ";"},
  {"chapterVerseSeparator", ":"},
  {"commaPauseCharacter", ","},
  {"endQuoteLevel1", "”"},
  {"endQuoteLevel2", "’"},
  {"endQuoteLevel3", "”"},
  {"endQuoteLevel4", ""},
  {"exclamationTerminator", "!"},
  {"properNounCapitalisation", "Y"},
  {"punctuationAfterBookAbbreviation", ""},
  {"questionTerminator", "?"},
  {"sentenceCapitalisation", "Y"},
  {"spaceAllowedAfterBCS", "E"},
  {"startQuoteLevel1", "“"},
  {"startQuoteLevel2", "‘"},
  {"startQuoteLevel3", "“"},
  {"startQuoteLevel4", ""},
  {"statementTerminator", "."},
  {"verseBridgeCharacter", "-"},
  {"verseSeparator", ","},
}; // English_briefBookDataDict (27 entries)


// Matigsalug
const static punctuationByRefEntry
 MatigsalugBookDataDict[27] = {
  // Fields (2) are const unsigned char referenceAbbreviation[3+1]; const int indexNumber;
  // Sorted by referenceAbbreviation
  {"allowedVerseSuffixes", "ab"},
  {"bookBridgeCharacter", "–"},
  {"bookChapterSeparator", " "},
  {"bookSeparator", ";"},
  {"booknameCase", "ME"},
  {"booknameLength", "3"},
  {"chapterBridgeCharacter", "–"},
  {"chapterSeparator", ";"},
  {"chapterVerseSeparator", ":"},
  {"commaPauseCharacter", ","},
  {"endQuoteLevel1", "”"},
  {"endQuoteLevel2", "’"},
  {"endQuoteLevel3", "”"},
  {"endQuoteLevel4", ""},
  {"exclamationTerminator", "!"},
  {"properNounCapitalisation", "Y"},
  {"punctuationAfterBookAbbreviation", ""},
  {"questionTerminator", "?"},
  {"sentenceCapitalisation", "Y"},
  {"spaceAllowedAfterBCS", "E"},
  {"startQuoteLevel1", "“"},
  {"startQuoteLevel2", "‘"},
  {"startQuoteLevel3", "“"},
  {"startQuoteLevel4", ""},
  {"statementTerminator", "."},
  {"verseBridgeCharacter", "-"},
  {"verseSeparator", ","},
}; // MatigsalugBookDataDict (27 entries)


// English
const static punctuationByRefEntry
 EnglishBookDataDict[27] = {
  // Fields (2) are const unsigned char referenceAbbreviation[3+1]; const int indexNumber;
  // Sorted by referenceAbbreviation
  {"allowedVerseSuffixes", "abcdef"},
  {"bookBridgeCharacter", "-"},
  {"bookChapterSeparator", " "},
  {"bookSeparator", ";"},
  {"booknameCase", "ME"},
  {"booknameLength", "3"},
  {"chapterBridgeCharacter", "-"},
  {"chapterSeparator", ";"},
  {"chapterVerseSeparator", ":"},
  {"commaPauseCharacter", ","},
  {"endQuoteLevel1", "”"},
  {"endQuoteLevel2", "’"},
  {"endQuoteLevel3", "”"},
  {"endQuoteLevel4", ""},
  {"exclamationTerminator", "!"},
  {"properNounCapitalisation", "Y"},
  {"punctuationAfterBookAbbreviation", "."},
  {"questionTerminator", "?"},
  {"sentenceCapitalisation", "Y"},
  {"spaceAllowedAfterBCS", "E"},
  {"startQuoteLevel1", "“"},
  {"startQuoteLevel2", "‘"},
  {"startQuoteLevel3", "“"},
  {"startQuoteLevel4", ""},
  {"statementTerminator", "."},
  {"verseBridgeCharacter", "-"},
  {"verseSeparator", ","},
}; // EnglishBookDataDict (27 entries)


// Pointers to above data
const static tableEntry punctuationSystemTable[3] = {
  { "English_brief", English_briefBookDataDict, English_briefIndexNumberDataDict },
  { "Matigsalug", MatigsalugBookDataDict, MatigsalugIndexNumberDataDict },
  { "English", EnglishBookDataDict, EnglishIndexNumberDataDict },
}; // 3 entries

// end of BiblePunctuationSystems_Tables.c