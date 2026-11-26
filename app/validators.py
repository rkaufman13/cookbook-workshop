import re

def contains_url(message_body):
    pattern = re.compile(
        "[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}/[-a-zA-Z0-9()@:%_+.~#?&/=]*")
    matched_list = re.findall(pattern,message_body)
    return [add_protocol(trunc(matched)) for matched in matched_list]


def trunc(str):
    if str.endswith("."):
        str = str[:-1]
    return str

def add_protocol(str):
    return "https://"+str