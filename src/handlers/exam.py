import tornado.web

from handlers.base import RequestHandler, reqenv
from services.api import get_school_year_data, a0410S_StdSemeView_select, get_single_exam_scores, get_exam_stats
from utils.error import RemoteServerError


class ExamHandler(RequestHandler):

    @reqenv
    async def get(self):
        if self.session is None:
            await self.render('goto-login.html')
            return

        session_id = self.session.session_id

        try:
            item_id = self.get_argument("itemId")
            std_seme_id = self.get_argument("stdSemeId")

        except tornado.web.HTTPError:
            item_id = None
            std_seme_id = None

        err, std_seme_view = await a0410S_StdSemeView_select(session_id, self.session.student_id)
        if err == RemoteServerError:
            await self.render('remote-server-error.html')
            return

        item_ids = []

        for std in std_seme_view:
            s_id, year, seme = std["stdSemeId"], std["syear"], std["seme"]
            err, school_year_data = await get_school_year_data(session_id, int(year), int(seme))
            if err == RemoteServerError:
                await self.render('remote-server-error.html')
                return

            for item in school_year_data:
                if item["exam_name"] in ["學期成績", "平常成績"]:
                    continue

                item_ids.append({
                    "stdSemeId": s_id,
                    "itemId": item["itemId"],
                    "year": year,
                    "seme": seme,
                    "exam_name": item["exam_name"]
                })

        scores, stats = None, None
        if item_id is not None and std_seme_id is not None:
            err, scores = await get_single_exam_scores(session_id, item_id, std_seme_id)
            err, stats = await get_exam_stats(session_id, item_id, std_seme_id)

            if err == RemoteServerError:
                await self.render('remote-server-error.html')
                return

        await self.render('exam.html', item_ids=item_ids, scores=scores, stats=stats,
                          item_id=item_id, std_seme_id=std_seme_id)
