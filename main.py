from emoji_parser import EmojiParser
from gen_c_sharp import GenCSharp

if __name__ == "__main__":
    url = "https://unicode.org/Public/emoji/14.0/emoji-test.txt"
    parser = EmojiParser(url)
    result = parser.parse()

    gen = GenCSharp(r"C:\Windows\Fonts\seguiemj.ttf", url)
    # gen.testIsEmojiSupportedByFont()
    gen.gen(result)