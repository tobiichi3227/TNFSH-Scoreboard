import json
import base64
import requests
from typing import List, Dict

import const


def get_student_info(session_key: str) -> Dict[str, str]:
    """
    Get student info from index page
    <div style="display: none;" id="userInfo">Base64 encoded string</div>

    :param session_key:
    :return: student info dict
    """

    data = {
        "session_key": session_key
    }

    res = requests.post(const.INDEX_URL, data=data, timeout=20)

    i = res.text.find("id=\"userInfo\">") + 14
    j = res.text.find("<", i)

    tmp = json.loads(base64.b64decode(res.text[i:j]).decode('utf-8'))
    return {
        "studentId": tmp["id"],
        "name": tmp["name"]
    }


def get_exam_stats(session_key: str, item_id: str, std_seme_id: str) -> Dict:
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

    res = requests.post(f"{const.MAIN_URL}/A0410S_ItemScoreStat_select.action", data=data, timeout=20)
    res = json.loads(res.text)

    # stats not publish
    if len(res["dataRows"]) == 0:
        return {
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
    return {
        "class_rank": r.get("orderC", ""),
        "class_cnt": r.get("pnmC", ""),
        "group_rank": r.get("orderS", ""),
        "group_cnt": r.get("pnmS", ""),
        "all_rank": r.get("orderG", ""),
        "all_cnt": r.get("pnmG", ""),
        "score_sum": r.get("scoreT", ""),
        "average": r.get("scoreV", ""),
    }


def a0410S_StdSemeView_select(session_key: str, std_id: str) -> list[dict]:
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

    res = requests.post(f"{const.MAIN_URL}/A0410S_StdSemeView_select.action", data=data, timeout=20)
    res = json.loads(res.text)
    return [{
        "stdSemeId": obj["id"],
        "syear": obj["syear"],
        "seme": obj["seme"],
        "grade": obj["grade"],
    } for obj in res["dataRows"]]


def get_school_year_data(session_key: str, year: int = None, seme: int = None) -> List[Dict]:
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

    res = requests.post(f"{const.MAIN_URL}/A0410S_Item_select.action", data=data, timeout=20)
    res = json.loads(res.text)
    return [{
        "itemId": obj["id"],
        "year": obj["syear"],
        "semester": obj["seme"],
        "exam_name": obj["name"],
    } for obj in res["dataRows"]]


def get_single_exam_scores(session_key: str, item_id: str, std_seme_id: str) -> List[Dict]:
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

    res = requests.post(f"{const.MAIN_URL}/A0410S_OpenItemScoreView_selectA0410s.action", data=data, timeout=20)
    res = json.loads(res.text)

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

    return scores
