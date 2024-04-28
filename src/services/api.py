import base64

import orjson

import const
from handlers.base import Errors
from services.service import client_session
from services.utils import timeout_handle, ReturnType


def get_optional_str(obj):
    if obj is None:
        return ""

    return obj


@timeout_handle
async def get_validate_pic() -> ReturnType:
    async with client_session.post(const.VALIDATE_URL) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.json()
        if res is None:
            return Errors.RemoteServer, None

        return Errors.Success, {
            "picture": res["src"],
            "src": res["validateSrc"],
        }


@timeout_handle
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
            return Errors.RemoteServer, None

        res = await resp.text()

    i = res.find("id=\"userInfo\">") + 14
    j = res.find("<", i)

    tmp = orjson.loads(base64.b64decode(res[i:j]).decode("utf-8"))

    data["pId"] = tmp["childId"]
    async with client_session.post(f"{const.MAIN_URL}/B0410S_StdSemeView_select0410.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    return Errors.Success, {
        "studentId": tmp["childId"],
        "name": tmp["name"],
        "seat_number": res["data"]["seat"],
        "class_number": res["data"]["clsNo"][3:],
    }


@timeout_handle
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
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    # stats not publish
    if len(res["dataRows"]) == 0:
        return Errors.Success, {
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
    return Errors.Success, {
        "class_rank": r.get("orderC", ""),
        "class_cnt": r.get("pnmC", ""),
        "group_rank": r.get("orderS", ""),
        "group_cnt": r.get("pnmS", ""),
        "all_rank": r.get("orderG", ""),
        "all_cnt": r.get("pnmG", ""),
        "score_sum": r.get("scoreT", ""),
        "average": r.get("scoreV", ""),
    }


@timeout_handle
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
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    return Errors.Success, [{
        "stdSemeId": obj["id"],
        "syear": obj["syear"],
        "seme": obj["seme"],
        "grade": obj["grade"],
    } for obj in res["dataRows"]]


@timeout_handle
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
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    return Errors.Success, [{
        "itemId": obj["id"],
        "year": obj["syear"],
        "semester": obj["seme"],
        "exam_name": obj["name"],
    } for obj in res["dataRows"]]


@timeout_handle
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
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    scores = [{
        "subject": score_obj["subjId"],
        "exam_name": score_obj["itemId"],
        "score": get_optional_str(score_obj["score"]),
        "class_average": get_optional_str(score_obj.get("yl")),
        "is_participated": score_obj["noExamMark"],
    } for score_obj in res["dataRows"]]

    return Errors.Success, scores


@timeout_handle
async def get_term_scores(session_key: str, student_id: str) -> ReturnType:
    """

    :param session_key: the connection session key
    :param student_id: student id from student info
    :return: List of all year term data
    :rtype: list[dict]
    """

    data = {
        "session_key": session_key,
        "stdId": student_id,
        "statusM": 15,
        "queryKind": "a0410s",
    }

    async with client_session.post(f"{const.MAIN_URL}/A0410S_StdSemeView_select.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    scores = [{
        "stdSemeId": score_obj["id"],
        "score": score_obj["sco6"],
        "all_score": score_obj["scoreT"],
        "deserved_credits": score_obj["credSum"],
        "observed_credits": score_obj["credTot"],
        "total_observed_credits_sum": score_obj["credAdd"],
    } for score_obj in res["dataRows"]]

    return Errors.Success, scores


@timeout_handle
async def get_subject_term_scores(session_key: str, std_seme_id: str) -> ReturnType:
    """
    Get single term all subject scores

    :param session_key: the connection session key
    :param std_seme_id: from StdSemeView function
    :return: List of all term subject scores
    :rtype: list[dict]
    """

    data = {
        "session_key": session_key,
        "pId": std_seme_id,
    }

    async with client_session.post(f"{const.MAIN_URL}/A0410S_OpenStdView_selectA0410s.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    scores = [{
        "subject": score_obj["subjId"],
        "course_type": score_obj["courseType"],
        "credits": score_obj["credits"],
        "pass": score_obj["passYn"],
        "score": get_optional_str(score_obj["score"]),
        "score_original": get_optional_str(score_obj["scoreSrc"]),
        "score_examed": get_optional_str(score_obj.get("scoreExam")),
        "score_retake": get_optional_str(score_obj.get("scoreRem")),
        "class_average": get_optional_str(score_obj.get("yl"))
    } for score_obj in res["dataRows"]]

    return Errors.Success, scores


def _get_rewards(reward_obj) -> tuple[int, int, int, int, int, int]:
    c1 = reward_obj["reward1"]
    c2 = reward_obj["reward2"]
    c3 = reward_obj["reward3"]
    c4 = reward_obj["reward4"]
    c5 = reward_obj["reward5"]
    c6 = reward_obj["reward6"]

    return c1, c2, c3, c4, c5, c6


@timeout_handle
async def get_rewards_record(session_key: str) -> ReturnType:
    """
    Get all reward record

    :param session_key: the connection session key
    :return: List of all reward record
    :rtype: list[dict]
    """

    data = {
        "session_key": session_key,
    }

    async with client_session.post(f"{const.MAIN_URL}/B0305S_Reward_select.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    rewards = [{
        "syear": obj["syear"],
        "seme": obj["seme"],
        "fact": obj["fact"],
        "desc": get_optional_str(obj["rewardArticleId"]),
        "rewards": _get_rewards(obj),
        "cancel": get_optional_str(obj["cancelYn"]),
        "cancel_date": obj["cancelDt"],
    } for obj in res["dataRows"]]

    return Errors.Success, rewards


def _get_absences(absence_obj):
    return [
        absence_obj["morn"],
        absence_obj["raiseFlag"],
        absence_obj["lesson1"],
        absence_obj["lesson2"],
        absence_obj["lesson3"],
        absence_obj["lesson4"],
        absence_obj["rest"],
        absence_obj["lesson5"],
        absence_obj["lesson6"],
        absence_obj["lesson7"],
        absence_obj["lesson8"],
    ]


@timeout_handle
async def get_absence_record(session_key: str) -> ReturnType:
    """
    Get all absence records

    :param session_key: the connection session key
    :return:
    :rtype: list[dict]
    """

    data = {
        "session_key": session_key,
        "rows": 365 * 3,
    }

    async with client_session.post(f"{const.MAIN_URL}/B0209S_Absence_select.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    absences = [{
        "syear": obj["syear"],
        "seme": obj["seme"],
        "date": obj["absenceDt"],
        "absences": _get_absences(obj),
    } for obj in res["dataRows"]]

    return Errors.Success, absences


@timeout_handle
async def update_password(session_key: str, original_password: str, new_password: str,
                          confirm_new_password: str) -> ReturnType:
    data = {
        "session_key": session_key,
        "oldpd": original_password,
        "newpd": new_password,
        "agnpd": confirm_new_password
    }
    async with client_session.post(f"{const.MAIN_URL}/changecheck.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    if res["parameterMap"] and res["parameterMap"]["status"] == 200 and res["message"] is None:
        res["message"] = "S"

    return Errors.Success, res["message"]


def _get_credits_type(t) -> str:
    if t == "C1":
        return "all_credit"

    elif t == "C2":
        return "graduation_credit"

    elif t == "C4":
        return "required_courses_credit"

    elif t == "C9":
        return "elective_courses_credit"


@timeout_handle
async def get_graduation_credits(session_key: str, std_seme_id: str) -> ReturnType:
    data = {
        "session_key": session_key,
        "stdSemeId": std_seme_id,
        "pId": 2,
    }
    async with client_session.post(f"{const.MAIN_URL}/A0410S_GradCredit_select.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    graduation_credits = {
        _get_credits_type(obj["areaM"]): {
            "required_credits": obj["credSum"],
            "observed_credits": obj["credits"],
        } for obj in res["dataRows"]}

    return Errors.Success, graduation_credits
