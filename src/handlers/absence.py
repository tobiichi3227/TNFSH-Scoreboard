import datetime
import collections
import itertools

import tornado

from handlers.base import reqenv, RequestHandler, Errors
from services.api import get_all_semester_info, get_absence_record, get_curriculum


class AbsenceHandler(RequestHandler):
    @reqenv
    async def get(self):
        if self.session is None:
            await self.render("goto-login.html")
            return

        session_id = self.session.session_id

        try:
            year = int(self.get_argument("year"))
            seme = int(self.get_argument("seme"))

        except (tornado.web.HTTPError, ValueError):
            year = None
            seme = None

        err, std_seme_view = await get_all_semester_info(session_id, self.session.student_id)
        if err == Errors.RemoteServer:
            await self.render_remote_server_err()
            return

        item_ids = [{
            "year": std["syear"],
            "seme": std["seme"]
        } for std in std_seme_view]
        item_ids.sort(key=lambda std: (-std["year"], -std["seme"]))
        if year is None and seme is None:
            year = max(item_ids, key=lambda std: std["year"])["year"]
            seme = max(item_ids, key=lambda std: std["seme"])["seme"]

        absences, stats = None, None
        if year is not None and seme is not None:
            err, r = await get_absence_record(session_id)
            if err == Errors.RemoteServer:
                await self.render_remote_server_err()
                return

            for key, group in itertools.groupby(r, key=lambda obj: (obj["syear"], obj["seme"])):
                if key == (year, seme):
                    absences = list(group)
                    break

            if absences is not None:
                stats = collections.defaultdict(int)
                for absence in absences:
                    for lesson in absence["absences"]:
                        if lesson is None or lesson == "":
                            continue

                        stats[lesson] += 1

        await self.render("absence.html", item_ids=item_ids, absences=absences, stats=stats,
                          year=year, seme=seme)


class SubjectAbsenceCountHandler(RequestHandler):
    @reqenv
    async def get(self):
        if self.session is None:
            await self.render("goto-login.html")
            return

        session_id = self.session.session_id
        if self.session.student_class_number == -1 and self.session.student_seat_number == -1:
            await self.finish('出席數無法計算')
            return

        err, std_seme_view = await get_all_semester_info(session_id, self.session.student_id)
        if err == Errors.RemoteServer:
            await self.render_remote_server_err()
            return

        year = max(std_seme_view, key=lambda std: std["syear"])["syear"]
        seme = max(std_seme_view, key=lambda std: std["seme"])["seme"]

        absences = None
        err, r = await get_absence_record(session_id)
        if err == Errors.RemoteServer:
            await self.render_remote_server_err()
            return

        for key, group in itertools.groupby(r, key=lambda obj: (obj["syear"], obj["seme"])):
            if key == (year, seme):
                absences = list(group)
                break

        err, curriculum = await get_curriculum(self.session.student_class_number)
        if err == Errors.RemoteServer:
            await self.render_remote_server_err()
            return

        subject_absence_cnts = collections.defaultdict(int)
        for absence in absences:
            d = list(map(int, absence["date"].split("/")))
            weekday = datetime.date(d[0] + 1911, d[1], d[2]).weekday() + 1

            # 2 ~ 5代表第1到第4節，要i - 1是因為absence["absences"]還有早修與升旗
            for i in range(2, 5 + 1):
                if absence["absences"][i] in ["1", "2"]:  # 1: 曠課 2: 事假
                    curr = curriculum[(weekday * 10) + i - 1]
                    if curr == "":
                        continue

                    subject_absence_cnts[curr] += 1

            # 7 ~ 10代表第5到第8節，要i - 2是因為absence["absences"]有午休
            for i in range(7, 10 + 1):
                if absence["absences"][i] in ["1", "2"]:  # 1: 曠課 2: 事假
                    curr = curriculum[(weekday * 10) + i - 2]  # weekday * 10 + i - 2 為編碼
                    if curr == "":
                        continue

                    subject_absence_cnts[curr] += 1

        await self.render("subject-absence-count.html", subject_absence_cnts=subject_absence_cnts)
