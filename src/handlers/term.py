import tornado.web

from handlers.base import RequestHandler, reqenv, Errors
from services.api import get_all_semester_info, get_term_scores, get_subject_term_scores, get_term_scores_ranking


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

        err, std_seme_view = await get_all_semester_info(session_id, self.session.student_id)
        if err == Errors.RemoteServer:
            await self.render_remote_server_err()
            return

        item_ids = [
            {
                "stdSemeId": std["stdSemeId"],
                "year": std["syear"],
                "seme": std["seme"],
            } for std in std_seme_view
        ]
        item_ids.sort(key=lambda std: (-std["year"], -std["seme"]))
        if std_seme_id is None:
            std_seme_id = max(item_ids, key=lambda std: std["stdSemeId"])["stdSemeId"]

        subject_scores, term_scores, term_ranking = None, None, None
        if std_seme_id is not None:
            err, subject_scores = await get_subject_term_scores(session_id, std_seme_id)
            err, term_ranking = await get_term_scores_ranking(session_id, std_seme_id)
            err, term_scores = await get_term_scores(session_id, self.session.student_id)

            if err == Errors.RemoteServer:
                await self.render_remote_server_err()
                return

            term_scores = list(filter(lambda score: str(score["stdSemeId"]) == str(std_seme_id), term_scores))
            if len(term_scores) != 0:
                term_scores = term_scores[0]
            else:
                term_scores = None
        await self.render("term.html", item_ids=item_ids, subject_scores=subject_scores, term_scores=term_scores, term_ranking=term_ranking,
                          std_seme_id=std_seme_id)
