from emoji_parser import Emoji, Status
import os

class GenCSharp:

    @classmethod
    def genCamelCaseName(self, emoji: Emoji) -> str:
        return "".join([s.capitalize() for s in emoji.searchTerms if s.isalnum()])

    @classmethod
    def genSearchTerms(self, emoji: Emoji) -> str:
        return "\"" + "\", \"".join(emoji.searchTerms) + "\""

    @classmethod
    def genEmojiString(self, emoji: Emoji):
        return ("\t\tpublic static readonly SingleEmoji " + self.genCamelCaseName(emoji) + " = new SingleEmoji(\n"
            "\t\t\tsequence: new UnicodeSequence(\"" + emoji.codePoint + "\"),\n"
            "\t\t\tname: \"" + emoji.name + "\",\n"
            "\t\t\tsearchTerms: new[] { " + self.genSearchTerms(emoji) + " },\n"
            "\t\t\tsortOrder: " + str(emoji.index) + "\n"
            "\t\t);\n")

    @classmethod
    def genEmojiDeclarationsFile(self, emoji: list):
        if not os.path.exists("out"):
            os.makedirs("out")
        outFile = open("out/Emoji-Emojis.cs", "w", encoding="utf-8")

        output = ("namespace NeoSmart.Unicode\n"
            "{\n"
            "\tpublic static partial class Emoji\n"
            "\t{\n")

        for e in emoji:
            if e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED:
                output += self.genEmojiString(e)

        output += "\t}\n}\n"
        outFile.write(output)
        outFile.close()

    @classmethod
    def genEmojiAllFile(self, emoji: list):
        if not os.path.exists("out"):
            os.makedirs("out")
        outFile = open("out/Emoji-All.cs", "w", encoding="utf-8")

        output = ("using System.Collections.Generic;\n"
            "\n"
            "namespace NeoSmart.Unicode\n"
            "{\n"
            "\tpublic static partial class Emoji\n"
            "\t{\n"
            "\t\tpublic static IEnumerable<SingleEmoji> All => new[] {\n")

        for e in emoji:
            if e.status == Status.COMPONENT or e.status == Status.FULLY_QUALIFIED:
                output += "\t\t\t/* " + e.emoji + " */ " + self.genCamelCaseName(e) + ",\n"

        output += "\t\t};\n\t}\n}\n"
        outFile.write(output)
        outFile.close()

    @classmethod
    def gen(self, emoji: list):
        # Emoji-Emojis.cs
        self.genEmojiDeclarationsFile(emoji)
        # Emoji-All.cs
        self.genEmojiAllFile(emoji)

        