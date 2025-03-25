from collections import defaultdict
import tornado.web

from handlers.base import RequestHandler, reqenv, Errors
from services.api import get_leave_requests, get_leave_request_file, delete_leave_request, add_leave_request, get_all_semester_info


class LeaveRequestHandler(RequestHandler):

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

        err, leave_requests = await get_leave_requests(session_id)
        if err == Errors.RemoteServer:
            await self.render_remote_server_err()
            return

        leave_forms = defaultdict(list)
        for request in leave_requests:
            if str(request["stdSemeId"]) != str(std_seme_id):
                continue


            leave_forms[request['leave_request_id']].append(request)


        await self.render("leave-request.html", std_seme_id=std_seme_id, item_ids=item_ids, leave_forms=leave_forms)

    @reqenv
    async def post(self):
        if self.session is None:
            await self.render("goto-login.html")
            return

        session_id = self.session.session_id
        reqtype = self.get_argument("reqtype")
        if reqtype == "download":
            leave_request_id = int(self.get_argument("leave_request_id"))
            err, file = await get_leave_request_file(session_id, leave_request_id)
            if err == Errors.RemoteServer:
                await self.render_remote_server_err()
                return

            self.set_header('Content-Type', file["content_type"])
            self.set_header('Content-Disposition', file["content_disp"])
            self.finish(file["file_content"])
            return

        elif reqtype == "delete":
            leave_request_id = int(self.get_argument("leave_request_id"))
            err, _ = await delete_leave_request(session_id, leave_request_id)
            self.finish('S')

        elif reqtype == "new":
            reason = self.get_argument('reason')
            leavetype = self.get_argument('leavetype')
            from_date = self.get_argument('from_date')
            to_date = self.get_argument('to_date')
            filename = self.get_argument('filename')
            weeks = self.get_argument('weeks')
            lessons = self.get_argument('lessons')
            files = self.request.files.get("file", [])
            if len(files) == 0:
                await self.error(Errors.WrongParam)
                return

            file: bytes = files[0].body

            err, msg = await add_leave_request(session_id, self.session.student_id, reason, leavetype, from_date, to_date,
                                               lessons, weeks, file, filename)
            if err == Errors.Success:
                await self.error(err)
                return

            self.finish(msg)
