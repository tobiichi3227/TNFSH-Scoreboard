import csv
import base64

import bs4
import orjson
from aiohttp import ContentTypeError, FormData

import config
import const
from handlers.base import Errors
from services.cache import CacheService
from services.service import client_session
from services.utils import timeout_handle, ReturnType


def get_optional_str(obj):
    """
    This function is designed for situations where the academic system might return None or indicate the absence of a value for results that are not yet available.
    While .get("key", "") function can handle cases where the value does not exist, this function should be used when the return value is None.
    """

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

        if "src" not in res or res["src"] is None:
            return Errors.RemoteServer, None

        return Errors.Success, {
            "picture": res["src"],
            "src": "",
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
        if not res["data"]:
            res = {"data": {"seat": "-1", "clsNo": "000-1"}}

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
    :param std_seme_id: semester id
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
async def get_all_semester_info(session_key: str, student_id: int) -> ReturnType:
    """
    Get all semester info including semester id, grade, semester year.
    Semester id is a necessary parameter in many data queries.

    :param session_key: connection session key
    :param student_id: student id from student info
    :return: data for semester info
    :rtype: list[dict]
    """

    data = {
        "session_key": session_key,
        "stdId": student_id,
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
async def get_school_year_data(session_key: str, year: int | None=None, seme: int | None=None) -> ReturnType:
    """
    Get school year data
    If year and seme is null, you will get all year data

    :param session_key: connection session key
    :param year: query year
    :param seme: query semester
    :return: data for a given year and semester
    :rtype: list[dict]
    """

    data: dict = {
        "session_key": session_key,
        "sidx": "syear,seme,itemNo",
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
    :param std_seme_id: semester id
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
        "score": get_optional_str(score_obj.get("score", "")),
        "class_average": get_optional_str(score_obj.get("yl", "")),
        "is_participated": score_obj["noExamMark"],
    } for score_obj in res["dataRows"]]

    return Errors.Success, scores


@timeout_handle
async def get_term_scores(session_key: str, student_id: int) -> ReturnType:
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
        "score": get_optional_str(score_obj.get("sco6", "")),
        "all_score": get_optional_str(score_obj.get("scoreT", "")),
        "deserved_credits": get_optional_str(score_obj.get("credSum", "")),
        "observed_credits": get_optional_str(score_obj.get("credTot", "")),
        "total_observed_credits_sum": get_optional_str(score_obj.get("credAdd", "")),
    } for score_obj in res["dataRows"]]

    return Errors.Success, scores

@timeout_handle
async def get_term_scores_ranking(session_key: str, std_seme_id: str) -> ReturnType:
    """
    Get single term ranking data

    :param session_key: the connection session key
    :param std_seme_id: semester id
    :return: List of all term subject scores
    :rtype: dict
    """

    data = {
        "session_key": session_key,
        "pId": std_seme_id,
    }

    async with client_session.post(f"{const.MAIN_URL}/A0410S_OpenStdView_selectA0410s.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)

    ranking = {
        "class_rank": "",
        "group_rank": "",
        "all_rank": "",
    }
    if res["dataRows"]:
        ranking["class_rank"] = get_optional_str(res["dataRows"][0].get("orderCQ", ""))
        ranking["group_rank"] = get_optional_str(res["dataRows"][0].get("orderSQ", ""))
        ranking["all_rank"] = get_optional_str(res["dataRows"][0].get("orderGQ", ""))

    return Errors.Success, ranking

@timeout_handle
async def get_subject_term_scores(session_key: str, std_seme_id: str) -> ReturnType:
    """
    Get single term all subject scores

    :param session_key: the connection session key
    :param std_seme_id: semester id
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
        "pass": score_obj["passYn"] == "是",
        "score": get_optional_str(score_obj.get("score", "")),
        "score_original": get_optional_str(score_obj.get("scoreSrc", "")),
        "score_examed": get_optional_str(score_obj.get("scoreExam", "")),
        "score_retake": get_optional_str(score_obj.get("scoreRem", "")),
        "class_average": get_optional_str(score_obj.get("yl", "")),
        "class_rank": get_optional_str(score_obj.get("orderC", "")),
        "group_rank": get_optional_str(score_obj.get("orderS", "")),
        "all_rank": get_optional_str(score_obj.get("orderG", "")),
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
        "desc": get_optional_str(obj.get("rewardArticleId", "")),
        "rewards": _get_rewards(obj),
        "cancel": get_optional_str(obj.get("cancelYn", "")),
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
    """
    Update password by using 180 days check password api(180天密碼重設).

    :param session_key: the connection session key
    :param original_password: original password
    :param new_password: new password
    :param confirm_new_password: new password repeat
    :return:
    """
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

    return ""

@timeout_handle
async def get_graduation_credits(session_key: str, std_seme_id: str) -> ReturnType:
    """
    Get all information regarding course credit types for graduation credits.

    :param session_key: the connection session key
    :param std_seme_id: semester id
    :return:
    """
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


@timeout_handle
async def get_single_exam_scores_and_stats_from_report(session_key: str, syear: int, seme: int, item_id: int):
    """
    Get the exam score and statistics through the report API.

    :param session_key: the connection session key
    :param syear: semester year
    :param seme: first semester (1) / second semester (2)
    :param item_id: the exam id from StdSemeView function
    :return: a dict contain subjects score and stats
    """
    data = {
        "session_key": session_key,
        "syse": f"{syear}{seme}",
        "syear": syear,
        "seme": seme,
        "item": item_id,
        "item2": item_id,

        "format": "CSV",
        "headSign": False,
        "mail": 5,
        "showWhat": "on",
        "showOrd": "on",
        "showOrd2": "on",
        "raDt": "",
    }

    async with client_session.post(f"{const.MAIN_URL}/A0492R1.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.text(encoding='utf-8')

    res = res.split('\n')
    reader = csv.reader(res, delimiter=',')
    is_end = False
    stats: dict = {
        "score_sum": None,
        "average": None,
        "class_rank": None,
        "class_cnt": None,
        "group_rank": None,
        "group_cnt": None,
        "all_rank": None,
        "all_cnt": None,
    }
    subjects = []

    for idx, row in enumerate(reader):
        if '應修學分' in row:
            stats["score_sum"] = row[20]
            stats["average"] = row[26]

        elif '全班名次' in row:
            if row[6] != '':
                stats["class_rank"], stats["class_cnt"] = row[6].split('/') # class rank
            if row[20] != '':
                stats["group_rank"], stats["group_cnt"] = row[20].split('/') # group rank
            if row[32] != '':
                stats["all_rank"], stats["all_cnt"] = row[32].split('/')
            is_end = True


        elif idx > 19 and not is_end:
            subjects.append({
                "subject": row[0].replace('\u3000', ''),
                "score": row[5].replace('#', ''),
                "class_rank": row[9],
                "group_rank": row[12],
                "class_average": row[15]
            })

            if len(row) > 18: # contain two subject
                subjects.append({
                    "subject": row[0 + 18].replace('\u3000', ''),
                    "score": row[5 + 18].replace('#', ''),
                    "class_rank": row[12 + 18],
                    "group_rank": row[16 + 18],
                    "class_average": row[17 + 18]
                })

    return Errors.Success, {
        "stats": stats,
        "scores": subjects,
    }

@timeout_handle
async def forget_password(account: str, username: str, idnumber: str, birth: str) -> ReturnType:
    """
    Send forget password request to school server.

    :param account:
    :param username:
    :param idnumber: Identity Number
    :param birth:
    :return:
    """

    data = f"act={account},name={username},idno={idnumber},schNo={config.SCHNO},typs=s,birth={birth}"

    async with client_session.post(f"{const.MAIN_URL}/Fta.action?a={data}", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        try:
            res = await resp.json(loads=orjson.loads)
        except ContentTypeError:
            return Errors.RemoteServerBlock, None

    err = Errors.General
    if m := res["parameterMap"]:
        if m.get("status") == "200":
            err = Errors.Success
        elif m["msg"] == "無此帳號":
            err = Errors.NotExist
        elif m["msg"].find("空白") != -1:
            err = Errors.WrongParam

    return err, None


def _parse_tr(section_tr: bs4.Tag, section_number: int, curriculum: dict[int, str]):
    for (weekday, course_td) in enumerate(section_tr.select("td")[2:]):
        teacher_texts = []
        for a in course_td.select('a'):
            if a is not None:
                teacher_texts.append(a.text.strip())

        course_name = ""
        for t in course_td.text.strip().split("\n"):
            if t in teacher_texts or t == "":
                continue
            for name in teacher_texts:
                t = t.replace(name, '')

            course_name += t

        course_name = course_name.strip().replace(u'\xa0', '')  # remove html nbsp
        if course_name == "":
            continue

        curriculum[(weekday + 1) * 10 + (section_number + 1)] = course_name


@timeout_handle
async def get_curriculum(class_number: int) -> ReturnType:
    cache_res = CacheService.inst.get(class_number)
    if cache_res is not None:
        return Errors.Success, cache_res

    year = 101
    if str(class_number).endswith("18"):
        year = 106
    elif str(class_number).endswith("19"):
        year = 108

    url = f"http://w3.tnfsh.tn.edu.tw/deanofstudies/course/C{year}{class_number}.HTML"

    async with client_session.get(url) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        html = await resp.content.read()

    soup = bs4.BeautifulSoup(html, "html.parser")
    soup.encoding = "utf-8"

    curriculum = {}

    for i in range(3, 6 + 1):
        _parse_tr(soup.select_one(f'tr[style="mso-yfti-irow:{i}"]'), i - 3, curriculum)
    for i in range(9, 11 + 1):
        _parse_tr(soup.select_one(f'tr[style="mso-yfti-irow:{i}"]'), i - 5, curriculum)

    _parse_tr(soup.select_one('tr[style="mso-yfti-irow:12;mso-yfti-lastrow:yes"]'), 10 - 3, curriculum)

    CacheService.inst.set(class_number, curriculum)
    return Errors.Success, curriculum

@timeout_handle
async def get_leave_requests(session_key: str):
    data = {
        "session_key": session_key,
    }

    async with client_session.post(f"{const.MAIN_URL}/B0207S1_LeaveAction_execute.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)


    t = [
        {
            "reviewer": obj["examineStatus"],
            "review_status": obj["examineM"],
            "leave_reason": obj["cause"],
            "reject_reason": obj["causeBack"],
            "leave_request_id": int(obj["leaveGatId"]),
            "request_date": obj["applyDt"],
            "leave_date": obj["leaveDt"],
            "absences": _get_absences(obj),
            "stdSemeId": obj["stdSemeId"],
        }
        for obj in res["dataRows"]
    ]
    return Errors.Success, t

@timeout_handle
async def add_leave_request(session_key: str, student_id: str, reason: str, leavetype: str, from_date: str,
                            to_date: str, lessons: str, weeks: str, file: bytes, filename: str):

    data = FormData()
    data.add_field("session_key", session_key)
    data.add_field("addIds", str(student_id))
    data.add_field("absenceM", leavetype)
    data.add_field("dt1Q", from_date)
    data.add_field("dt2Q", to_date)
    data.add_field("lesson", lessons)
    data.add_field("dayOfWeek", weeks)
    data.add_field("cause", reason)
    data.add_field("file", file, filename=filename)

    async with client_session.post(f"{const.MAIN_URL}/B0207S1_B0207sAction_add.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = await resp.json(loads=orjson.loads)


    if res['data'] and res['data']['status'] == '200':
        return Errors.Success, ''

    return Errors.General, res['message']

@timeout_handle
async def delete_leave_request(session_key: str, leave_request_id: int):
    data = {
        "session_key": session_key,
        "id": leave_request_id,
        "oper": "del",
    }

    async with client_session.post(f"{const.MAIN_URL}/B0207S1_LeaveGatAction_delete1.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None


    return Errors.Success, None


@timeout_handle
async def get_leave_request_file(session_key: str, leave_request_id: int):
    data = {
        "session_key": session_key,
        "pid": leave_request_id,
    }

    async with client_session.post(f"{const.MAIN_URL}/B0207S1_LeaveGatAction_downloadFile.action", data=data) as resp:
        if not resp.ok:
            return Errors.RemoteServer, None

        res = {
            "file_content": await resp.content.read(),
            "content_type": resp.headers['Content-Type'],
            "content_disp": resp.headers['Content-Disposition'],
        }

    return Errors.Success, res
