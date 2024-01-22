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
