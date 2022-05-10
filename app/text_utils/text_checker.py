def utf8_length(string: str) -> int:
    return len(string.encode("utf-8"))


def all_text_length(*strings: str) -> int:
    length = 0

    for string in strings:
        length += len(string)
    return length
