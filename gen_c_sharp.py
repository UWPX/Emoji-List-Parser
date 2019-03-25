from emoji_parser import Emoji

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
            "\t\t\tsearchTerms: new[] { " + self.genSearchTerms(emoji) + " },\n"
            "\t\t\tsortOrder: " + str(emoji.index) + "\n"
            "\t\t);\n")

    @classmethod
    def gen(self, emojis: list):
        outFile = open("out.txt", "w")

        output = ("namespace NeoSmart.Unicode\n"
            "{\n"
            "\tpublic static partial class Emoji\n"
            "\t{\n")

        for e in emojis:
            output += self.genEmojiString(e)

        output += "\t}\n}\n"
        outFile.write(output)

        outFile.close()