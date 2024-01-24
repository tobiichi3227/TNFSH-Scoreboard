import collections
import itertools

import tornado

from handlers.base import reqenv, RequestHandler
from services.api import a0410S_StdSemeView_select, get_absence_record
from utils.error import RemoteServerError


class AbsenceHandler(RequestHandler):
    @reqenv
    async def get(self):
        if self.session is None:
            await self.render("goto-login.html")
            return

        session_id = self.session.session_id

        try:
            year = int(self.get_argument("year"))
            seme = int(self.get_argument("seme"))

        except (tornado.web.HTTPError, ValueError):
            year = None
            seme = None

        err, std_seme_view = await a0410S_StdSemeView_select(session_id, self.session.student_id)
        if err == RemoteServerError:
            await self.render("remote-server-error.html")
            return

        item_ids = [{
            "year": std["syear"],
            "seme": std["seme"]
        } for std in std_seme_view]
        item_ids.sort(key=lambda std: (std["year"], std["seme"]))

        absences, stats = None, None
        if year is not None and seme is not None:
            err, r = await get_absence_record(session_id)
            if err == RemoteServerError:
                await self.render("remote-server-error.html")
                return

            for key, group in itertools.groupby(r, key=lambda obj: (obj["syear"], obj["seme"])):
                if key == (year, seme):
                    absences = list(group)
                    break

            if absences is not None:
                stats = collections.defaultdict(int)
                for absence in absences:
                    for lesson in absence["absences"]:
                        if lesson is None or lesson == "":
                            continue

                        stats[lesson] += 1

        await self.render("absence.html", item_ids=item_ids, absences=absences, stats=stats,
                          year=year, seme=seme)
