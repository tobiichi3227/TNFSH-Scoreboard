from handlers.base import RequestHandler, reqenv, Errors
from services.api import get_all_semester_info, get_subject_term_scores
from utils.htmlgen import get_color_style_html


class GraduationCreditsHandler(RequestHandler):
    async def _get_seme_credits(self, std_seme_id):
        err, subject_scores = await get_subject_term_scores(self.session.session_id, std_seme_id)
        if err == Errors.RemoteServer:
            return err, None

        c1, c2, c3 = 0, 0, 0 # 部定必修, 校訂必修, 選修
        pass_c1, pass_c2, pass_c3 = 0, 0, 0 # 部定必修, 校訂必修, 選修
        for subject in subject_scores:
            credit = int(subject["credits"])
            if subject["course_type"] == "部必":
                c1 += credit
                if subject["pass"]:
                    pass_c1 += credit
            elif subject["course_type"] == "校必":
                c2 += credit
                if subject["pass"]:
                    pass_c2 += credit
            elif subject["course_type"] == "校選":
                c3 += credit
                if subject["pass"]:
                    pass_c3 += credit
        return Errors.Success, {
            "total": (c1, c2, c3),
            "pass": (pass_c1, pass_c2, pass_c3)
        }

    def get_credit_status_style(self, pass_c, final_c, require_c):
        if pass_c >= require_c:
            return ''
        elif pass_c + final_c >= require_c:
            return get_color_style_html('#ffc107')
        elif pass_c + final_c < require_c:
            return get_color_style_html('#dc3545')

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

        final_credit = (0, 0, 0)
        final_stdid = -1
        credits = (0, 0, 0)
        for std in std_seme_view:
            try:
                err, c = await self._get_seme_credits(std["stdSemeId"])
            except:
                continue
            if err == Errors.RemoteServer:
                await self.render_remote_server_err()
                return
            pass_c: tuple[int, int, int] = c["pass"]
            credits = (credits[0] + pass_c[0], credits[1] + pass_c[1], credits[2] + pass_c[2])
            if int(std["stdSemeId"]) > final_stdid:
                final_stdid = std["stdSemeId"]
                final_credit = c["total"]

        await self.render("graduation-credit.html", credits=credits, final_credit=final_credit, get_credit_status_style=self.get_credit_status_style)
