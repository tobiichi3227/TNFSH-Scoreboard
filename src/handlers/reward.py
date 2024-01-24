import itertools

import tornado.web

from handlers.base import RequestHandler, reqenv
from services.api import a0410S_StdSemeView_select, get_rewards_record
from utils.error import RemoteServerError


class RewardHandler(RequestHandler):
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

        rewards, stats = None, None
        if year is not None and seme is not None:
            stats = [0] * 6
            err, r = await get_rewards_record(session_id)
            if err == RemoteServerError:
                await self.render("remote-server-error.html")
                return

            for key, group in itertools.groupby(r, key=lambda obj: (obj["syear"], obj["seme"])):
                if key == (year, seme):
                    rewards = list(group)
                    break

            if rewards is not None:
                for reward in rewards:
                    for i in range(6):
                        stats[i] += reward["rewards"][i]

        await self.render("reward.html", item_ids=item_ids, rewards=rewards, stats=stats,
                          year=year, seme=seme)
