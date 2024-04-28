def get_color_style_html(color: str) -> str:
    return f"style=\"color: {color}\""


def get_reward_chinese_str(reward) -> str:
    res = []

    c1 = reward[0]
    c2 = reward[1]
    c3 = reward[2]
    c4 = reward[3]
    c5 = reward[4]
    c6 = reward[5]

    if c1:
        res.append(f"嘉獎{c1}支 ")

    if c2:
        res.append(f"小功{c2}支 ")

    if c3:
        res.append(f"大功{c3}支 ")

    if c4:
        res.append(f"警告{c4}支 ")

    if c5:
        res.append(f"小過{c5}支 ")

    if c6:
        res.append(f"大過{c6}支")

    return "".join(res)


ABSENCE_SHORT_REASON = {
    "": "",
    "1": "曠",
    "2": "事",
    "3": "病",
    "4": "喪",
    "5": "公",
    "7": "遲",
    "E": "退",
    "B": "補",
    "C": "減",
    "N": "抵",
    "O": "空",
    "J": "婚",
    "X": "產前",
    "M": "娩",
    "K": "陪產",
    "Y": "流產",
    "Z": "育嬰",
    "W": "生理",
    "9": "其他",
    "F": "新冠",
    "A": "跨",
}

ABSENCE_LONG_REASON = {
    "1": "曠課",
    "2": "事假",
    "3": "病假",
    "4": "喪假",
    "5": "公假",
    "7": "遲到",
    "E": "早退",
    # "B": "補",
    # "C": "減",
    # "N": "抵",
    # "O": "空",
    # "J": "婚",
    # "X": "產前",
    # "M": "娩",
    "K": "陪產假",
    "Y": "流產假",
    "Z": "育嬰假",
    "W": "生理假",
    "9": "其他",
    "F": "新冠",
    # "A": "跨",
}


def get_short_absence_reason_str(reason_code: str) -> str:
    if reason_code is None or reason_code == "":
        return ""

    return ABSENCE_SHORT_REASON[reason_code]


def get_long_absence_reason_str(reason_code: str) -> str:
    if reason_code is None or reason_code == "":
        return ""

    return ABSENCE_LONG_REASON[reason_code]


def get_credit_type_chinese_str(type: str) -> str:
    TYPE_NAMES = {
        "all_credit": "應修習學分",
        "graduation_credit": "畢業學分",
        "required_courses_credit": "必修學分",
        "elective_courses_credit": "選修學分",
    }

    return TYPE_NAMES[type]