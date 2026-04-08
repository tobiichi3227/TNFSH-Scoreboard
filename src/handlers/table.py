from handlers.base import RequestHandler, reqenv, Errors
from services.api import get_semester_grade_table, get_apply_semester_grade_table, get_student_officer_table, get_all_semester_info

class TableDownloadHandler(RequestHandler):

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

        item_ids = [
            {
                "year": std["syear"],
                "seme": std["seme"],
            } for std in std_seme_view
        ]
        item_ids.sort(key=lambda std: (-std["year"], -std["seme"]))

        await self.render("table-download.html", item_ids=item_ids)

    @reqenv
    async def post(self):
        if self.session is None:
            await self.render("goto-login.html")
            return

        session_id = self.session.session_id
        reqtype = self.get_argument("reqtype")
        if reqtype == "download":
            download_type = self.get_argument("download_type")
            seme = int(self.get_argument('seme'))
            year = int(self.get_argument('year'))
            if download_type not in ('apply_grade_table', 'grade_table', 'student_officer_table'):
                await self.error(Errors.WrongParam)
                return

            if download_type == 'apply_grade_table':
                err, file = await get_apply_semester_grade_table(session_id, self.session.student_id, year, seme)

                if err != Errors.Success:
                    await self.error(err)
                    return

            elif download_type == 'grade_table':
                rptKind = int(self.get_argument('rptKind'))
                if rptKind != 0 and rptKind != 1:
                    await self.error(Errors.WrongParam)
                    return

                err, file = await get_semester_grade_table(session_id, self.session.student_id, year, seme, rptKind)
                if err != Errors.Success:
                    await self.error(err)
                    return

            elif download_type == 'student_officer_table':
                err, file = await get_student_officer_table(session_id, year, seme)
                if err != Errors.Success:
                    await self.error(err)
                    return

            self.set_header('Content-Type', 'application/pdf')
            self.finish(file)
            return
