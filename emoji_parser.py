import requests

class Emoji:

    def __init__(self, codePoint: str, emoji: str, name: str, searchTerms: list, status: str, group: str, subgroup: str):
        self.codePoint = codePoint
        self.emoji = emoji
        self.name = name
        self.searchTerms = searchTerms
        self.status = status
        self.group = group
        self.subgroup = subgroup

class EmojiParser:

    def __init__(self, url: str):
        self.url = url

    def parse(self):
        text = self.__downloadList()
        if text is None:
            return None
        
        lines = text.splitlines()
        lines = self.__removeNotImpLines(lines)

        emoji = []
        group = ""
        subgroup = ""
        for l in lines:
            if l.startswith("# group:"):
                group = self.__parseGroup(l)
            elif l.startswith("# subgroup:"):
                subgroup = self.__parseSubgroup(l)
            elif not l.startswith("#"):
                e = self.__parseEmoji(l, group, subgroup)
                if e:
                    emoji.append(e)

        return emoji

    def __downloadList(self) -> str: 
        resp = requests.get(self.url)
        return resp.text

    def __removeNotImpLines(self, lines: list) -> list:
        # Remove start comment:
        result = []
        for l in lines:
            if not l.startswith("#") or l.startswith("# group:") or l.startswith("# subgroup:"):
                result.append(l)

        # Remove empty lines:
        return [l for l in result if l]

    def __parseGroup(self, s: str) -> str:
        return s.replace("# group: ", "").strip()

    def __parseSubgroup(self, s: str) -> str:
        return s.replace("# subgroup: ", "").strip()

    def __parseEmoji(self, s: str, group: str, subgroup: str) -> Emoji:
        parts = s.split(";")
        if len(parts) != 2:
            print("Invalid line for parsing emoji part 1:" + s)
            return None

        codePoint = parts[0].strip()

        # Special case for the 'keycap' subgroup:
        endWithSeperator = s.strip().endswith('#')
        
        parts = parts[1].split("#")
        parts = [l for l in parts if l and l.strip()]
        if len(parts) != 2:
            print("Invalid line for parsing emoji part 2:" + s)
            return None

        if endWithSeperator:
            parts[1] = parts[1] + "#"
        status = parts[0].strip()

        parts = parts[1].strip().split()

        if len(parts) < 2:
            print("Invalid line for parsing emoji part 3:" + s)
            return None

        emoji = parts[0]

        del parts[0]

        name = " ".join(parts)
        searchTermsS = name.replace("-", " ").replace(" with", "").replace(" and", "").replace(" of", "").replace(" in", "").replace(":", "")
        searchTerms = searchTermsS.split()

        return Emoji(codePoint, emoji, name, searchTerms, status, group, subgroup)