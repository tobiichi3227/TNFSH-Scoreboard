import base64

import orjson

import const
from utils.error import ReturnType, Success, RemoteServerError
from services.service import client_session


async def get_validate_pic() -> ReturnType:
    async with client_session.post(const.VALIDATE_URL) as resp:
        if not resp.ok:
            return RemoteServerError, None

        res = await resp.json()
        return Success, {
            "picture": res["src"],
            "src": res["validateSrc"],
        }


async def get_student_info(session_key: str) -> ReturnType:
    """
    Get student info from index page
    <div style="display: none;" id="userInfo">Base64 encoded string</div>

    :param session_key:
    :return: student info dict
    """

    data = {
        "session_key": session_key
    }

    async with client_session.post(const.INDEX_URL, data=data) as resp:
        if not resp.ok:
            return RemoteServerError, None

        res = await resp.text()

    i = res.find("id=\"userInfo\">") + 14
    j = res.find("<", i)

    tmp = orjson.loads(base64.b64decode(res[i:j]).decode('utf-8'))
    return Success, {
        "studentId": tmp["childId"],
        "name": tmp["name"]
    }


async def get_exam_stats(session_key: str, item_id: str, std_seme_id: str) -> ReturnType:
    """
    Get specific exam statistics data such as rank, score sum of all subjects, score average.
    If the statistics info has not been published, data will be empty.

    :param session_key: connection session key
    :param item_id: the exam id from StdSemeView function
    :param std_seme_id: from StdSemeView function
    :return:
    """

    data = {
        "session_key": session_key,
        "itemId": item_id,
        "stdSemeId": std_seme_id,
    }

    async with client_session.post(f"{const.MAIN_URL}/A0410S_ItemScoreStat_select.action", data=data) as resp:
        if not resp.ok:
            return RemoteServerError, None

        res = await resp.json(loads=orjson.loads)

    # stats not publish
    if len(res["dataRows"]) == 0:
        return Success, {
            "class_rank": "",
            "class_cnt": "",
            "group_rank": "",
            "group_cnt": "",
            "all_rank": "",
            "all_cnt": "",
            "score_sum": "",
            "average": "",
        }

    r = res["dataRows"][0]
    return Success, {
        "class_rank": r.get("orderC", ""),
        "class_cnt": r.get("pnmC", ""),
        "group_rank": r.get("orderS", ""),
        "group_cnt": r.get("pnmS", ""),
        "all_rank": r.get("orderG", ""),
        "all_cnt": r.get("pnmG", ""),
        "score_sum": r.get("scoreT", ""),
        "average": r.get("scoreV", ""),
    }


async def a0410S_StdSemeView_select(session_key: str, std_id: str) -> ReturnType:
    """


    :param session_key: connection session key
    :param std_id: student id from student info
    :return:
    """

    data = {
        "session_key": session_key,
        "stdId": std_id,
        "statusM": 15,
    }

    async with client_session.post(f"{const.MAIN_URL}/A0410S_StdSemeView_select.action", data=data) as resp:
        if not resp.ok:
            return RemoteServerError, None

        res = await resp.json(loads=orjson.loads)

    return Success, [{
        "stdSemeId": obj["id"],
        "syear": obj["syear"],
        "seme": obj["seme"],
        "grade": obj["grade"],
    } for obj in res["dataRows"]]


async def get_school_year_data(session_key: str, year: int = None, seme: int = None) -> ReturnType:
    """
    Get school year data
    If year and seme is null, you will get all year data

    :param session_key: connection session key
    :param year: query year
    :param seme: query semester
    :return: data for a given year and semester
    :rtype: list[dict]
    """

    data = {
        "session_key": session_key
    }
    if year:
        data["syear"] = year

    if seme:
        data["seme"] = seme

    async with client_session.post(f"{const.MAIN_URL}/A0410S_Item_select.action", data=data) as resp:
        if not resp.ok:
            return RemoteServerError, None

        res = await resp.json(loads=orjson.loads)

    return Success, [{
        "itemId": obj["id"],
        "year": obj["syear"],
        "semester": obj["seme"],
        "exam_name": obj["name"],
    } for obj in res["dataRows"]]


async def get_single_exam_scores(session_key: str, item_id: str, std_seme_id: str) -> ReturnType:
    """
    Get single exam scores data
    Have subject name, exam name, subject score, class average for subject

    :param session_key: the connection session key
    :param item_id: the exam id from StdSemeView function
    :param std_seme_id: from StdSemeView function
    :return: List of score data
    :rtype: list[dict]
    """

    data = {
        "session_key": session_key,
        "itemId": item_id,
        "stdSemeId": std_seme_id,
    }

    async with client_session.post(f"{const.MAIN_URL}/A0410S_OpenItemScoreView_selectA0410s.action", data=data) as resp:
        if not resp.ok:
            return RemoteServerError, None

        res = await resp.json(loads=orjson.loads)

    scores = [{
        "subject": score_obj["subjId"],
        "exam_name": score_obj["itemId"],
        "score": score_obj.get("score", ""),
        "class_average": score_obj.get("yl", ""),
        "is_participated": score_obj["noExamMark"],
    } for score_obj in res['dataRows']]

    for score in scores:
        if score["score"] is None:
            score["score"] = ""

        if score["class_average"] is None:
            score["class_average"] = ""

    return Success, scores
