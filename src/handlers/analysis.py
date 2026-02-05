import tornado.web
import tornado.escape

from handlers.base import RequestHandler, reqenv, Errors
from services.api import get_all_semester_info, get_school_year_data, get_single_exam_scores, get_single_exam_scores_and_stats_from_report


class AnalysisHandler(RequestHandler):
    """
    Handler for the grade analysis page.
    
    Fetches all exam scores across all semesters for the logged-in student
    and renders them in an interactive chart for analysis.
    """
    
    @reqenv
    async def get(self):
        """
        GET endpoint for the analysis page.
        
        Retrieves all semester information, fetches scores for each exam,
        and passes the data to the template for visualization.
        """
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
                # Log error but continue with other semesters
                import traceback
                print(f"Error fetching school year data for year {year}, semester {seme}")
                continue

            for item in school_year_data:
                item_id = item["itemId"]
                exam_name = item["exam_name"]
                
                # Filter out semester grades and regular grades - these are not exams
                if exam_name and ("學期成績" in exam_name or "平常成績" in exam_name):
                    continue
                
                # Get scores for this exam - prefer report API for class_rank and group_rank
                scores = []
                try:
                    err, report_data = await get_single_exam_scores_and_stats_from_report(session_id, int(year), int(seme), item_id)
                    if err == Errors.Success and report_data:
                        scores = report_data["scores"]
                        # Report API doesn't include is_participated, set default value "否" (participated)
                        for score in scores:
                            if "is_participated" not in score:
                                score["is_participated"] = "否"
                except Exception as e:
                    print(f"Error fetching report data for exam {item_id}: {e}")
                
                # Fallback to regular API if report API fails
                if not scores:
                    err, scores = await get_single_exam_scores(session_id, item_id, s_id)
                    if err == Errors.RemoteServer:
                        # Log error but continue with other exams
                        print(f"Error fetching scores for exam {item_id}")
                        continue

                all_exams.append({
                    "stdSemeId": s_id,
                    "itemId": item_id,
                    "year": year,
                    "seme": seme,
                    "exam_name": exam_name,
                    "scores": scores,
                })

        # Sort by year and semester (most recent first)
        all_exams.sort(key=lambda x: (-int(x["year"]), -int(x["seme"])))

        # Convert to JSON for JavaScript - use json_encode for safety
        all_exams_json = tornado.escape.json_encode(all_exams)

        await self.render("analysis.html", all_exams_json=all_exams_json)
