import tornado.web

from handlers.base import RequestHandler, reqenv
from services.api import get_school_year_data, a0410S_StdSemeView_select, get_term_scores, get_subject_term_scores
from utils.error import RemoteServerError

class TermHandler(RequestHandler):
    @reqenv
    async def get(self):
        if self.session is None:
            await self.render("goto-login.html")
            return

        session_id = self.session.session_id

        try:
            std_seme_id = self.get_argument("stdSemeId")

        except tornado.web.HTTPError:
            std_seme_id = None

        err, std_seme_view = await a0410S_StdSemeView_select(session_id, self.session.student_id)
        if err == RemoteServerError:
            await self.render("remote-server-error.html")
            return

        item_ids = [
            {
                "stdSemeId": std["stdSemeId"],
                "year": std["syear"],
                "seme": std["seme"],
            } for std in std_seme_view
        ]

        subject_scores, term_scores = None, None
        if std_seme_id is not None:
            err, subject_scores = await get_subject_term_scores(session_id, std_seme_id)
            err, term_scores = await get_term_scores(session_id, self.session.student_id)

            if err == RemoteServerError:
                await self.render("remote-server-error.html")
                return

            term_scores = list(filter(lambda score: str(score["stdSemeId"]) == std_seme_id, term_scores))
            if len(term_scores) != 0:
                term_scores = term_scores[0]
            else:
                term_scores = None
        await self.render("term.html", item_ids=item_ids, subject_scores=subject_scores, term_scores=term_scores, std_seme_id=std_seme_id)