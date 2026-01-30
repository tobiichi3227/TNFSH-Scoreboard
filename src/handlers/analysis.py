import tornado.web

from handlers.base import RequestHandler, reqenv, Errors
from services.api import get_all_semester_info, get_school_year_data, get_single_exam_scores, get_exam_stats


class AnalysisHandler(RequestHandler):
    @reqenv
    async def get(self):
        if self.session is None:
            await self.render("goto-login.html")
            return

        session_id = self.session.session_id

        err, std_seme_view = await get_all_semester_info(session_id, self.session.student_id)
        if err == Errors.RemoteServer:
            await self.render_remote_server_err()
            return

        # Collect all exams and scores across all semesters
        all_exams = []
        
        for std in std_seme_view:
            s_id, year, seme = std["stdSemeId"], std["syear"], std["seme"]
            err, school_year_data = await get_school_year_data(session_id, int(year), int(seme))
            if err == Errors.RemoteServer:
                await self.render_remote_server_err()
                return

            for item in school_year_data:
                item_id = item["itemId"]
                
                # Get scores for this exam
                err, scores = await get_single_exam_scores(session_id, item_id, s_id)
                if err == Errors.RemoteServer:
                    continue
                    
                err, stats = await get_exam_stats(session_id, item_id, s_id)
                if err == Errors.RemoteServer:
                    continue

                all_exams.append({
                    "stdSemeId": s_id,
                    "itemId": item_id,
                    "year": year,
                    "seme": seme,
                    "exam_name": item["exam_name"],
                    "scores": scores,
                    "stats": stats
                })

        # Sort by year and semester (most recent first)
        all_exams.sort(key=lambda x: (-int(x["year"]), -int(x["seme"])))

        await self.render("analysis.html", all_exams=all_exams)
