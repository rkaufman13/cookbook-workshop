import re

def contains_url(message_body):
    pattern = re.compile(
        "https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}([-a-zA-Z0-9()@:%_+.~#?&/=]*)")
    matched_list = pattern.search(message_body)
    return [trunc(matched) for matched in matched_list]


def trunc(str):
    if str.endswith("."):
        str = str[:-1]
    return str