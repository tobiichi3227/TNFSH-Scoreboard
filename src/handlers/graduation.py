from handlers.base import RequestHandler, reqenv, Errors
from services.api import a0410S_StdSemeView_select, get_graduation_credits, get_subject_term_scores


class GraduationCreditsHandler(RequestHandler):
    async def _get_current_seme_credits(self, std_seme_id):
        err, subject_scores = await get_subject_term_scores(self.session.session_id, std_seme_id)
        if err == Errors.RemoteServer:
            return err, None

        elective_course_credit_in_last_seme = 0
        required_course_credit_in_last_seme = 0
        for subject in subject_scores:
            if subject["course_type"] == "校選":
                elective_course_credit_in_last_seme += int(subject["credits"])
            elif subject["course_type"] == "部必":
                required_course_credit_in_last_seme += int(subject["credits"])
        return Errors.Success, {
            "elective_course": elective_course_credit_in_last_seme,
            "required_course": required_course_credit_in_last_seme,
        }

    async def _set_pass_status(self, credit: dict[str, dict[str, str | int]], std_seme_id):
        observed = int(credit["all_credit"]["observed_credits"])
        required = 150
        credit["all_credit"]["pass_status"] = 0 if observed >= required else 1

        observed = int(credit["graduation_credit"]["observed_credits"])
        required = int(credit["graduation_credit"]["required_credits"])
        if observed >= required:
            status = 0
        elif required - observed <= 30:
            status = 1
        else:
            status = 2
        credit["graduation_credit"]["pass_status"] = status

        err, credits_in_current_seme = await self._get_current_seme_credits(std_seme_id)
        if err == Errors.RemoteServer:
            return err

        observed = credit["required_courses_credit"]["observed_credits"]
        required = credit["required_courses_credit"]["required_credits"]
        if observed >= required:
            status = 0
        elif required - observed <= credits_in_current_seme["required_course"]:
            status = 1
        else:
            status = 2
        credit["required_courses_credit"]["pass_status"] = status

        observed = credit["elective_courses_credit"]["observed_credits"]
        required = credit["elective_courses_credit"]["required_credits"]
        if observed >= required:
            status = 0
        elif required - observed <= credits_in_current_seme["elective_course"]:
            status = 1
        else:
            status = 2
        credit["elective_courses_credit"]["pass_status"] = status

    @reqenv
    async def get(self):
        if self.session is None:
            await self.render("goto-login.html")
            return

        session_id = self.session.session_id

        err, std_seme_view = await a0410S_StdSemeView_select(session_id, self.session.student_id)
        if err == Errors.RemoteServer:
            await self.render_remote_server_err()
            return

        credit = None
        std_seme_view.reverse()
        std_seme_id = None
        for std in std_seme_view:
            err, credit = await get_graduation_credits(session_id, std["stdSemeId"])
            if err == Errors.RemoteServer:
                await self.render_remote_server_err()
                return

            if credit:
                std_seme_id = std["stdSemeId"]
                break

        if credit:
            err = await self._set_pass_status(credit, std_seme_id)
            if err == Errors.RemoteServer:
                await self.render_remote_server_err()
                return

        err, credits_in_current_seme = await self._get_current_seme_credits(std_seme_id)
        if err == Errors.RemoteServer:
            await self.render_remote_server_err()
            return

        await self.render("graduation-credit.html", credits=credit, credits_in_current_seme=credits_in_current_seme)
