from emoji_parser import EmojiParser

if __name__ == "__main__":
    parser = EmojiParser("https://unicode.org/Public/emoji/12.0/emoji-test.txt")
    result = parser.parse()