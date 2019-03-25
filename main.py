from emoji_parser import EmojiParser
from gen_c_sharp import GenCSharp

if __name__ == "__main__":
    parser = EmojiParser("https://unicode.org/Public/emoji/12.0/emoji-test.txt")
    result = parser.parse()

    GenCSharp.gen(result)