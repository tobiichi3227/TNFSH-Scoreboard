import itertools

import tornado.web

from handlers.base import RequestHandler, reqenv, Errors
from services.api import a0410S_StdSemeView_select, get_rewards_record


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
        if err == Errors.RemoteServer:
            await self.render_remote_server_err()
            return

        item_ids = [{
            "year": std["syear"],
            "seme": std["seme"]
        } for std in std_seme_view]
        item_ids.sort(key=lambda std: (-std["year"], -std["seme"]))
        if year is None and seme is None:
            year = max(item_ids, key=lambda std: std["year"])["year"]
            seme = max(item_ids, key=lambda std: std["seme"])["seme"]

        rewards, stats = None, None
        if year is not None and seme is not None:
            stats = [0] * 6
            err, r = await get_rewards_record(session_id)
            if err == Errors.RemoteServer:
                await self.render_remote_server_err()
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
