from emoji_parser import EmojiParseResult, Emoji, Status, SkinTone, Group
import os
import re
from uharfbuzz import Face, Font, Buffer, ot_font_set_funcs, shape
import sys

class GenCSharp:

    def __init__(self, fontPath: str, srcUrl: str):
        # Load font:
        with open(fontPath, 'rb') as fontfile:
            self.fontdata = fontfile.read()

        self.srcUrl = srcUrl

    def __genCamelCaseName(self, emoji: Emoji) -> str:
        return "".join([s.capitalize() for s in emoji.searchTerms if s.isalnum()])

    def __genSearchTerms(self, emoji: Emoji) -> str:
        return "\"" + "\", \"".join(emoji.searchTerms) + "\""

    def __genSkinTones(self, emoji: Emoji) -> str:
        if len(emoji.skinTones) > 1 or len(emoji.skinTones) == 1 and emoji.skinTones[0] != SkinTone.NONE:
            return " SkinTones." + ", SkinTones.".join([self.__genSkinToneString(tone) for tone in emoji.skinTones if tone != SkinTone.NONE]) + " "
        else:
            return " "
    
    def __genSkinToneString(self, skinTone: SkinTone) -> str:
        return "".join([s.lower().capitalize() for s in skinTone.name.split("_")])

    def __genCodePoints(self, emoji: Emoji) -> str:
        return ", ".join([hex(cp) for cp in emoji.codePoints])

    def __genGroup(self, emoji: Emoji) -> str:
        return "SkinTone." + ", SkinTone.".join([tone.name for tone in emoji.skinTones])

    def __genMachinegeneratedHeader(self) -> str:
        return ("\t// This file is machine-generated based on the official Unicode Consortium publication (" + self.srcUrl + ").\n"
            "\t// See https://github.com/UWPX/Emoji-List-Parser for the generator.\n")

    def genEmojiString(self, emoji: Emoji):
        return ("\t\t/* " + emoji.emoji + " */\n"
            "\t\tpublic static readonly SingleEmoji " + self.__genCamelCaseName(emoji) + " = new SingleEmoji(\n"
            "\t\t\tsequence: new UnicodeSequence(new int[] { " + self.__genCodePoints(emoji) + " }),\n"
            "\t\t\tname: \"" + emoji.name + "\",\n"
            "\t\t\tsearchTerms: new string[] { " + self.__genSearchTerms(emoji) + " },\n"
            "\t\t\tskinTones: new Codepoint[] {" + self.__genSkinTones(emoji) + "},\n"
            "\t\t\tgroup: Group." + emoji.group.name + ",\n"
            "\t\t\tsubgroup: Subgroups." + self.__genSubGroupName(emoji.subgroup) + ",\n"
            "\t\t\thasGlyph: " + str(self.__isEmojiSupportedByFont(emoji)).lower() + ",\n"
            "\t\t\tsortOrder: " + str(emoji.index) + "\n"
            "\t\t);\n")

    def genEmojiDeclarationsFile(self, result: EmojiParseResult):
        print("Generating \"Emoji-Emojis.cs\"...")
        outFile = self.__openFile("Emoji-Emojis.cs")

        output = ("namespace NeoSmart.Unicode\n"
            "{\n"
            + self.__genMachinegeneratedHeader()
            + "\tpublic static partial class Emoji\n"
            "\t{\n")

        output += "\n".join([self.genEmojiString(e) for e in result.emoji if e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED])

        output += "\t}\n}\n"
        self.__writeAndCloseFile(outFile, output)
        print("Finished generating \"Emoji-Emojis.cs\".")

    def genEmojiAllFile(self, result: EmojiParseResult):
        print("Generating \"Emoji-All.cs\"...")
        outFile = self.__openFile("Emoji-All.cs")

        output = ("using System.Collections.Generic;\n"
            "\n"
            "namespace NeoSmart.Unicode\n"
            "{\n"
            + self.__genMachinegeneratedHeader()
            + "\tpublic static partial class Emoji\n"
            "\t{\n"
            "\t\t/// <summary>\n"
            "\t\t/// A (sorted) enumeration of all emoji.\n"
            "\t\t/// Only contains fully-qualified and component emoji.\n"
            "\t\t/// <summary>\n")
        output += self.__genSingleEmojiStart("All")

        for e in result.emoji:
            if e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED:
                output += "\t\t\t/* " + e.emoji + " */ " + self.__genCamelCaseName(e) + ",\n"

        output += "\t\t};\n\t}\n}\n"
        self.__writeAndCloseFile(outFile, output)
        print("Finished generating \"Emoji-All.cs\".")

    def genEmojiGroupFile(self, result: EmojiParseResult, group: Group):
        groupName = "".join([s.lower().capitalize() for s in group.name.split("_")])
        print("Generating \"Emoji-" + groupName + ".cs\"...")
        outFile = self.__openFile("Emoji-" + groupName + ".cs")

        output = ("using System.Collections.Generic;\n"
            "\n"
            "namespace NeoSmart.Unicode\n"
            "{\n"
            + self.__genMachinegeneratedHeader()
            + "\tpublic static partial class Emoji\n"
            "\t{\n"
            "\t\t/// <summary>\n"
            "\t\t/// A (sorted) enumeration of all emoji in group: " + group.name + "\n"
            "\t\t/// Only contains fully-qualified and component emoji.\n"
            "\t\t/// <summary>\n")
        output += self.__genSingleEmojiStart(groupName)

        for e in result.emoji:
            if (e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED) and e.group == group:
                output += "\t\t\t/* " + e.emoji + " */ " + self.__genCamelCaseName(e) + ",\n"

        output += "\t\t};\n\t}\n}\n"
        self.__writeAndCloseFile(outFile, output)
        print("Finished generating \"Emoji-" + groupName + ".cs\".")

    def __isEmojiSupportedByFont(self, emoji: Emoji) -> bool:
        # Load font (has to be done for call):
        face = Face(self.fontdata)
        font = Font(face)
        upem = face.upem
        font.scale = (upem, upem)
        ot_font_set_funcs(font)

        # Create text buffer:
        buf = Buffer()
        buf.add_str(emoji.emoji)
        buf.guess_segment_properties()

        # Shape text:
        features = {"kern": True, "liga": True}
        shape(font, buf, features)
        infos = buf.glyph_infos

        # Remove all variant selectors:
        while len(infos) > 0 and infos[-1].codepoint == 3:
            infos = infos[:-1]

        # Filter empty:
        if len(infos) <= 0:
            return False

        # Remove uncombined ending with skin tone like "👭🏿":
        lastCp = infos[-1].codepoint
        if lastCp == 1076 or lastCp == 1079 or lastCp == 1082 or lastCp == 1085 or lastCp == 1088:
            return False
            
        # If there is a code point 0 => Emoji not fully supported by font:
        return all(info.codepoint != 0 and info.codepoint != 3 for info in infos)
    
    def testIsEmojiSupportedByFont(self):
        self.__testEvalIsEmojiSupportedByFont("☹️", True)
        self.__testEvalIsEmojiSupportedByFont("👨‍👨‍👧‍👦", True)
        self.__testEvalIsEmojiSupportedByFont("🐱‍👤", True)
        self.__testEvalIsEmojiSupportedByFont("❤", True)
        self.__testEvalIsEmojiSupportedByFont("🐱‍👤", True)
        self.__testEvalIsEmojiSupportedByFont("☺️", True)
        self.__testEvalIsEmojiSupportedByFont("🕵🏻‍♀️", True)
        self.__testEvalIsEmojiSupportedByFont("⛷️", True)
        self.__testEvalIsEmojiSupportedByFont("👁️‍🗨️", True)
        self.__testEvalIsEmojiSupportedByFont("🧔🏼", True)

        self.__testEvalIsEmojiSupportedByFont("", False)
        self.__testEvalIsEmojiSupportedByFont("🧏🏻‍♀️", False)
        self.__testEvalIsEmojiSupportedByFont("🧍🏼", False)
        self.__testEvalIsEmojiSupportedByFont("🧍🏿‍♀", False)
        self.__testEvalIsEmojiSupportedByFont("👩🏿‍🦽", False)
        self.__testEvalIsEmojiSupportedByFont("👩🏽‍🤝‍👨🏿", False)
        self.__testEvalIsEmojiSupportedByFont("👭🏻", False)
        self.__testEvalIsEmojiSupportedByFont("👭🏼", False)
        self.__testEvalIsEmojiSupportedByFont("👭🏽", False)
        self.__testEvalIsEmojiSupportedByFont("👭🏾", False)
        self.__testEvalIsEmojiSupportedByFont("👭🏿", False)

    def __testEvalIsEmojiSupportedByFont(self, emoji: str, expected: bool):
        print(emoji + " " + str(self.__isEmojiSupportedByFont(Emoji([], emoji, "", [], [], Status.FULLY_QUALIFIED, Group.COMPONENT, "", 0)) == expected))

    def __genSingleEmojiStart(self, name: str):
        return ("#if NET20 || NET30 || NET35\n"
            "\t\tpublic static readonly List<SingleEmoji> " + name + " = new List<SingleEmoji>() {\n"
            "#else\n"
            "\t\tpublic static SortedSet<SingleEmoji> " + name + " => new SortedSet<SingleEmoji>() {\n"
            "#endif\n")

    def genEmojiBasicFile(self, result: EmojiParseResult):
        outFile = self.__openFile("Emoji-Basic.cs")

        output = ("using System.Collections.Generic;\n"
            "\n"
            "namespace NeoSmart.Unicode\n"
            "{\n"
            + self.__genMachinegeneratedHeader()
            + "\tpublic static partial class Emoji\n"
            "\t{\n"
            "\t\t/// <summary>\n"
            "\t\t/// A (sorted) enumeration of all emoji without skin variations and no duplicate gendered vs gender-neutral emoji, ideal for displaying.\n"
            "\t\t/// Emoji without supported glyphs in Segoe UI Emoji are also omitted from this list.\n"
            "\t\t/// <summary>\n")
        output += self.__genSingleEmojiStart("Basic")

        # The path to the Segoe UI Emoji font file under Windows 10:
        for e in result.emoji:
            if (e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED) and SkinTone.NONE in e.skinTones and self.__isEmojiSupportedByFont(e):
                output += "\t\t\t/* " + e.emoji + " */ " + self.__genCamelCaseName(e) + ",\n"

        output += "\t\t};\n\t}\n}\n"
        self.__writeAndCloseFile(outFile, output)
        print("Finished generating \"Emoji-Basic.cs\".")

    def __genSubGroupName(self, subgroup: str) -> str:
        parts = re.sub(r"[,.'’“”!():\-&]", " ", subgroup).split()
        return "_".join(part.upper() for part in parts if part)

    def __openFile(self, name: str):
        if not os.path.exists("out"):
            os.makedirs("out")
        return open("out/" + name, "w", encoding="utf-8")

    def __writeAndCloseFile(self, file, text: str):
        # Replace \t with 4 spaces to match the VS identation:
        file.write(text.replace("\t", "    "))
        file.close()

    def genSubgroupsFile(self, result: EmojiParseResult):
        print("Generating \"Emoji-Subgroups.cs\"...")
        outFile = self.__openFile("Emoji-Subgroups.cs")

        output = ("namespace NeoSmart.Unicode\n"
            "{\n"
            + self.__genMachinegeneratedHeader()
            + "\tpublic static partial class Emoji\n"
            "\t{\n"
            "\t\tpublic static class Subgroups\n"
            "\t\t{\n")
        output += "\n".join("\t\t\tpublic static readonly string " + self.__genSubGroupName(subgroup) + " = \"" + subgroup + "\";" for subgroup in result.subgroups) + "\n"
        output += "\t\t}\n\t}\n}\n"

        self.__writeAndCloseFile(outFile, output)
        print("Finished generating \"Subgroups.cs\".")

    def gen(self, result: EmojiParseResult):
        # Emoji-Emojis.cs
        self.genEmojiDeclarationsFile(result)
        # Subgroups.cs
        self.genSubgroupsFile(result)
        # Emoji-All.cs
        self.genEmojiAllFile(result)
        # Emoji-Basic.cs
        self.genEmojiBasicFile(result)

        # Emoji-SmileysAndEmotion.cs
        self.genEmojiGroupFile(result, Group.SMILEYS_AND_EMOTION)
        # Emoji-PeopleAndBody.cs
        self.genEmojiGroupFile(result, Group.PEOPLE_AND_BODY)
        # Emoji-Component.cs
        self.genEmojiGroupFile(result, Group.COMPONENT)
        # Emoji-AnimalsAndNature.cs
        self.genEmojiGroupFile(result, Group.ANIMALS_AND_NATURE)
        # Emoji-FoodAndDrink.cs
        self.genEmojiGroupFile(result, Group.FOOD_AND_DRINK)
        # Emoji-TravelAndPlaces.cs
        self.genEmojiGroupFile(result, Group.TRAVEL_AND_PLACES)
        # Emoji-Activities.cs
        self.genEmojiGroupFile(result, Group.ACTIVITIES)
        # Emoji-Objects.cs
        self.genEmojiGroupFile(result, Group.OBJECTS)
        # Emoji-Symbols.cs
        self.genEmojiGroupFile(result, Group.SYMBOLS)
        # Emoji-Flags.cs
        self.genEmojiGroupFile(result, Group.FLAGS)

        print("Done generating all C# source code files!")

        