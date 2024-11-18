import tornado.web

from handlers.base import RequestHandler, reqenv, Errors
from services.api import get_school_year_data, get_all_semester_info, get_single_exam_scores, get_exam_stats, get_single_exam_scores_and_stats_from_report


class ExamHandler(RequestHandler):

    @reqenv
    async def get(self):
        if self.session is None:
            await self.render("goto-login.html")
            return

        session_id = self.session.session_id

        try:
            item_id = self.get_argument("itemId")
            std_seme_id = self.get_argument("stdSemeId")

        except tornado.web.HTTPError:
            item_id = None
            std_seme_id = None

        err, std_seme_view = await get_all_semester_info(session_id, self.session.student_id)
        if err == Errors.RemoteServer:
            await self.render_remote_server_err()
            return

        item_ids = []

        current_year = -1
        current_seme = -1
        for std in std_seme_view:
            s_id, year, seme = std["stdSemeId"], std["syear"], std["seme"]
            err, school_year_data = await get_school_year_data(session_id, int(year), int(seme))
            if err == Errors.RemoteServer:
                await self.render_remote_server_err()
                return

            if item_id is not None and std_seme_id is not None:
                if str(std_seme_id) == str(s_id):
                    current_year = year
                    current_seme = seme

            for item in school_year_data:
                item_ids.append({
                    "stdSemeId": s_id,
                    "itemId": item["itemId"],
                    "year": year,
                    "seme": seme,
                    "exam_name": item["exam_name"]
                })

        item_ids.sort(key=lambda std: (-std["year"], -std["seme"]))

        try:
            err, r = await get_single_exam_scores_and_stats_from_report(session_id, current_year, current_seme, item_id)
            if err == Errors.RemoteServer:
                await self.render_remote_server_err()
                return

            scores = r["scores"]
            stats = r["stats"]
            await self.render("newexam.html", item_ids=item_ids, scores=scores, stats=stats,
                            item_id=item_id, std_seme_id=std_seme_id)

        except Exception as e:
            import traceback
            traceback.print_exception(e)

            scores, stats = None, None
            if item_id is not None and std_seme_id is not None:
                err, scores = await get_single_exam_scores(session_id, item_id, std_seme_id)
                err, stats = await get_exam_stats(session_id, item_id, std_seme_id)

                if err == Errors.RemoteServer:
                    await self.render_remote_server_err()
                    return

            await self.render("exam.html", item_ids=item_ids, scores=scores, stats=stats,
                            item_id=item_id, std_seme_id=std_seme_id)



