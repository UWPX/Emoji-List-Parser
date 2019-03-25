from emoji_parser import Emoji, Status, SkinTone, Group
from fontTools.ttLib import TTFont
import os

class GenCSharp:

    @classmethod
    def __genCamelCaseName(self, emoji: Emoji) -> str:
        return "".join([s.capitalize() for s in emoji.searchTerms if s.isalnum()])

    @classmethod
    def __genSearchTerms(self, emoji: Emoji) -> str:
        return "\"" + "\", \"".join(emoji.searchTerms) + "\""

    @classmethod
    def __genSkinTones(self, emoji: Emoji) -> str:
        return "SkinTone." + ", SkinTone.".join([tone.name for tone in emoji.skinTones])

    @classmethod
    def __genGroup(self, emoji: Emoji) -> str:
        return "SkinTone." + ", SkinTone.".join([tone.name for tone in emoji.skinTones])

    @classmethod
    def genEmojiString(self, emoji: Emoji):
        return ("\t\tpublic static readonly SingleEmoji " + self.__genCamelCaseName(emoji) + " = new SingleEmoji(\n"
            "\t\t\tsequence: new UnicodeSequence(\"" + emoji.codePoint + "\"),\n"
            "\t\t\tname: \"" + emoji.name + "\",\n"
            "\t\t\tsearchTerms: new[] { " + self.__genSearchTerms(emoji) + " },\n"
            "\t\t\tskinTones: new[] { " + self.__genSkinTones(emoji) + " },\n"
            "\t\t\tgroup: Group." + emoji.group.name + ",\n"
            "\t\t\tsubgroup: \"" + emoji.subgroup + "\",\n"
            "\t\t\tsortOrder: " + str(emoji.index) + "\n"
            "\t\t);\n")

    @classmethod
    def genEmojiDeclarationsFile(self, emoji: list, srcUrl: str):
        if not os.path.exists("out"):
            os.makedirs("out")
        outFile = open("out/Emoji-Emojis.cs", "w", encoding="utf-8")

        output = ("namespace NeoSmart.Unicode\n"
            "{\n"
            "\t// This file is machine-generated based on the official Unicode Consortium publication (" + srcUrl + ").\n"
            "\t// See https://github.com/UWPX/Emoji-List-Parser for the generator.\n"
            "\tpublic static partial class Emoji\n"
            "\t{\n")

        for e in emoji:
            if e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED:
                output += self.genEmojiString(e)

        output += "\t}\n}\n"
        outFile.write(output)
        outFile.close()

    @classmethod
    def genEmojiAllFile(self, emoji: list, srcUrl: str):
        if not os.path.exists("out"):
            os.makedirs("out")
        outFile = open("out/Emoji-All.cs", "w", encoding="utf-8")

        output = ("using System.Collections.Generic;\n"
            "\n"
            "namespace NeoSmart.Unicode\n"
            "{\n"
            "\t// This file is machine-generated based on the official Unicode Consortium publication (" + srcUrl + ").\n"
            "\t// See https://github.com/UWPX/Emoji-List-Parser for the generator.\n"
            "\tpublic static partial class Emoji\n"
            "\t{\n"
            "\t\t/// <summary>\n"
            "\t\t/// A (sorted) enumeration of all emoji.\n"
            "\t\t/// Only contains fully-qualified and component emoji.\n"
            "\t\t/// <summary>\n"
            "\t\tpublic static IEnumerable<SingleEmoji> All => new[] {\n")

        for e in emoji:
            if e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED:
                output += "\t\t\t/* " + e.emoji + " */ " + self.__genCamelCaseName(e) + ",\n"

        output += "\t\t};\n\t}\n}\n"
        outFile.write(output)
        outFile.close()

    @classmethod
    def genEmojiGroupFile(self, emoji: list, group: Group, srcUrl: str):
        if not os.path.exists("out"):
            os.makedirs("out")

        groupName = "".join([s.lower().capitalize() for s in group.name.split("_")])
        outFile = open("out/Emoji-" + groupName + ".cs", "w", encoding="utf-8")

        output = ("using System.Collections.Generic;\n"
            "\n"
            "namespace NeoSmart.Unicode\n"
            "{\n"
            "\t// This file is machine-generated based on the official Unicode Consortium publication (" + srcUrl + ").\n"
            "\t// See https://github.com/UWPX/Emoji-List-Parser for the generator.\n"
            "\tpublic static partial class Emoji\n"
            "\t{\n"
            "\t\t/// <summary>\n"
            "\t\t/// A (sorted) enumeration of all emoji in group: " + group.name + "\n"
            "\t\t/// Only contains fully-qualified and component emoji.\n"
            "\t\t/// <summary>\n"
            "\t\tpublic static IEnumerable<SingleEmoji> " + groupName + " => new[] {\n")

        for e in emoji:
            if (e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED) and e.group == group:
                output += "\t\t\t/* " + e.emoji + " */ " + self.__genCamelCaseName(e) + ",\n"

        output += "\t\t};\n\t}\n}\n"
        outFile.write(output)
        outFile.close()

    @classmethod
    def __isEmojiSupportedByFont(self, emoji: Emoji, font):
        code = sum([ord(i) for i in emoji.emoji])
        for table in font['cmap'].tables:
            for char_code, glyph_name in table.cmap.items():
                if char_code == code:
                    return True
        return False

    @classmethod
    def genEmojiBasicFile(self, emoji: list, srcUrl: str):
        if not os.path.exists("out"):
            os.makedirs("out")
        outFile = open("out/Emoji-Basic.cs", "w", encoding="utf-8")

        output = ("using System.Collections.Generic;\n"
            "\n"
            "namespace NeoSmart.Unicode\n"
            "{\n"
            "\t// This file is machine-generated based on the official Unicode Consortium publication (" + srcUrl + ").\n"
            "\t// See https://github.com/UWPX/Emoji-List-Parser for the generator.\n"
            "\tpublic static partial class Emoji\n"
            "\t{\n"
            "\t\t/// <summary>\n"
            "\t\t/// A (sorted) enumeration of all emoji without skin variations and no duplicate gendered vs gender-neutral emoji, ideal for displaying.\n"
            "\t\t/// Emoji without supported glyphs in Segoe UI Emoji are also omitted from this list.\n"
            "\t\t/// <summary>\n"
            "\t\tpublic static IEnumerable<SingleEmoji> Basic => new[] {\n")

        # The path to the Segoe UI Emoji font file under Windows 10:
        font = TTFont(r"C:\Windows\Fonts\seguiemj.ttf")
        for e in emoji:
            if (e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED) and SkinTone.NONE in e.skinTones and self.__isEmojiSupportedByFont(e, font):
                output += "\t\t\t/* " + e.emoji + " */ " + self.__genCamelCaseName(e) + ",\n"

        output += "\t\t};\n\t}\n}\n"
        outFile.write(output)
        outFile.close()

    @classmethod
    def gen(self, emoji: list, srcUrl: str):
        # Emoji-Emojis.cs
        self.genEmojiDeclarationsFile(emoji, srcUrl)
        # Emoji-All.cs
        self.genEmojiAllFile(emoji, srcUrl)
        # Emoji-Basic.cs
        self.genEmojiBasicFile(emoji, srcUrl)

        # Emoji-SmileysAndEmotion.cs
        self.genEmojiGroupFile(emoji, Group.SMILEYS_AND_EMOTION, srcUrl)
        # Emoji-PeopleAndBody.cs
        self.genEmojiGroupFile(emoji, Group.PEOPLE_AND_BODY, srcUrl)
        # Emoji-Component.cs
        self.genEmojiGroupFile(emoji, Group.COMPONENT, srcUrl)
        # Emoji-AnimalsAndNature.cs
        self.genEmojiGroupFile(emoji, Group.ANIMALS_AND_NATURE, srcUrl)
        # Emoji-FoodAndDrink.cs
        self.genEmojiGroupFile(emoji, Group.FOOD_AND_DRINK, srcUrl)
        # Emoji-TravelAndPlaces.cs
        self.genEmojiGroupFile(emoji, Group.TRAVEL_AND_PLACES, srcUrl)
        # Emoji-Activities.cs
        self.genEmojiGroupFile(emoji, Group.ACTIVITIES, srcUrl)
        # Emoji-Objects.cs
        self.genEmojiGroupFile(emoji, Group.OBJECTS, srcUrl)
        # Emoji-Symbols.cs
        self.genEmojiGroupFile(emoji, Group.SYMBOLS, srcUrl)
        # Emoji-Flags.cs
        self.genEmojiGroupFile(emoji, Group.FLAGS, srcUrl)

        