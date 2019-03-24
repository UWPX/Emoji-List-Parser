# Emoji-List-Parser

A parser for the emoji-test.txt provided by the [Unicode Consortium](http://unicode.org/consortium/consort.html).

## Example:

```python
url = "https://unicode.org/Public/emoji/12.0/emoji-test.txt"
parser = EmojiParser(url)
result = parser.parse()
```

As input it takes an url to the `emoji-test.txt` provided by the [Unicode Consortium](http://unicode.org/consortium/consort.html).  
[Here](https://unicode.org/Public/emoji/) you find the current `emoji-test.txt` files for all Unicode versions.

One successfully run `result` will be a list of [Emoji](emoji_parser.py) objects parsed from the downloaded [Unicode 12.0 Emoji list](https://unicode.org/Public/emoji/12.0/emoji-test.txt).  
If the download failed `result` will be `None`.