import time

from bemani.backend.jubeat.base import JubeatBase
from bemani.protocol import Node


class JubeatLoggerReportHandler(JubeatBase):
    def handle_logger_report_request(self, request: Node) -> Node:
        # Handle this by returning nothing, game doesn't care
        root = Node.void("logger")
        return root

    def handle_logger_ave_report_request(self, request: Node) -> Node:
        # Handle this by returning nothing, game doesn't care
        root = Node.void("logger_ave")
        return root

    def handle_logger_ave2_report_request(self, request: Node) -> Node:
        # Handle this by returning nothing, game doesn't care
        root = Node.void("logger_ave2")
        return root


class JubeatDemodataGetNewsHandler(JubeatBase):
    def handle_demodata_get_news_request(self, request: Node) -> Node:
        demodata = Node.void("demodata")
        data = Node.void("data")
        demodata.add_child(data)

        officialnews = Node.void("officialnews")
        data.add_child(officialnews)
        officialnews.set_attribute("count", "0")

        return demodata

    def handle_demodata_ave_get_news_request(self, request: Node) -> Node:
        demodata_ave = Node.void("demodata_ave")
        data = Node.void("data")
        demodata_ave.add_child(data)

        officialnews = Node.void("officialnews")
        data.add_child(officialnews)
        officialnews.set_attribute("count", "0")

        return demodata_ave

    def handle_demodata_ave2_get_news_request(self, request: Node) -> Node:
        demodata_ave2 = Node.void("demodata_ave2")
        data = Node.void("data")
        demodata_ave2.add_child(data)

        officialnews = Node.void("officialnews")
        data.add_child(officialnews)
        officialnews.set_attribute("count", "0")

        return demodata_ave2


class JubeatDemodataGetHitchartHandler(JubeatBase):
    def handle_demodata_get_hitchart_request(self, request: Node) -> Node:
        demodata = Node.void("demodata")
        data = Node.void("data")
        demodata.add_child(data)

        # Not sure what this is, maybe date?
        data.add_child(Node.string("update", time.strftime("%d/%m/%Y")))

        # No idea which songs are licensed or regular, so only return hit chart
        # for all songs on regular mode.
        hitchart_lic = Node.void("hitchart_lic")
        data.add_child(hitchart_lic)
        hitchart_lic.set_attribute("count", "0")

        songs = self.data.local.music.get_hit_chart(self.game, self.music_version, 10)
        hitchart_org = Node.void("hitchart_org")
        data.add_child(hitchart_org)
        hitchart_org.set_attribute("count", str(len(songs)))
        rank = 1
        for song in songs:
            rankdata = Node.void("rankdata")
            hitchart_org.add_child(rankdata)
            rankdata.add_child(Node.s32("music_id", song[0]))
            rankdata.add_child(Node.s16("rank", rank))
            rankdata.add_child(Node.s16("prev", rank))
            rank = rank + 1

        return demodata

    def handle_demodata_ave_get_hitchart_request(self, request: Node) -> Node:
        demodata_ave = Node.void("demodata_ave")
        data = Node.void("data")
        demodata_ave.add_child(data)

        # Not sure what this is, maybe date?
        data.add_child(Node.string("update", time.strftime("%d/%m/%Y")))

        # No idea which songs are licensed or regular, so only return hit chart
        # for all songs on regular mode.
        hitchart_lic = Node.void("hitchart_lic")
        data.add_child(hitchart_lic)
        hitchart_lic.set_attribute("count", "0")

        songs = self.data.local.music.get_hit_chart(self.game, self.music_version, 10)
        hitchart_org = Node.void("hitchart_org")
        data.add_child(hitchart_org)
        hitchart_org.set_attribute("count", str(len(songs)))
        rank = 1
        for song in songs:
            rankdata = Node.void("rankdata")
            hitchart_org.add_child(rankdata)
            rankdata.add_child(Node.s32("music_id", song[0]))
            rankdata.add_child(Node.s16("rank", rank))
            rankdata.add_child(Node.s16("prev", rank))
            rank = rank + 1

        return demodata_ave

    def handle_demodata_ave2_get_hitchart_request(self, request: Node) -> Node:
        demodata_ave2 = Node.void("demodata_ave2")
        data = Node.void("data")
        demodata_ave2.add_child(data)

        # Not sure what this is, maybe date?
        data.add_child(Node.string("update", time.strftime("%d/%m/%Y")))

        # No idea which songs are licensed or regular, so only return hit chart
        # for all songs on regular mode.
        hitchart_lic = Node.void("hitchart_lic")
        data.add_child(hitchart_lic)
        hitchart_lic.set_attribute("count", "0")

        songs = self.data.local.music.get_hit_chart(self.game, self.music_version, 10)
        hitchart_org = Node.void("hitchart_org")
        data.add_child(hitchart_org)
        hitchart_org.set_attribute("count", str(len(songs)))
        rank = 1
        for song in songs:
            rankdata = Node.void("rankdata")
            hitchart_org.add_child(rankdata)
            rankdata.add_child(Node.s32("music_id", song[0]))
            rankdata.add_child(Node.s16("rank", rank))
            rankdata.add_child(Node.s16("prev", rank))
            rank = rank + 1

        return demodata_ave2


class JubeatLobbyCheckHandler(JubeatBase):
    def handle_lobby_check_request(self, request: Node) -> Node:
        root = Node.void("lobby")
        data = Node.void("data")
        root.add_child(data)

        data.add_child(Node.s16("interval", 0))
        data.add_child(Node.s16("entry_timeout", 0))
        entrant_nr = Node.u32("entrant_nr", 0)
        entrant_nr.set_attribute("time", "0")
        data.add_child(entrant_nr)

        return root

    def handle_lobby_ave_check_request(self, request: Node) -> Node:
        root = Node.void("lobby_ave")
        data = Node.void("data")
        root.add_child(data)

        data.add_child(Node.s16("interval", 0))
        data.add_child(Node.s16("entry_timeout", 0))
        entrant_nr = Node.u32("entrant_nr", 0)
        entrant_nr.set_attribute("time", "0")
        data.add_child(entrant_nr)

        return root

    def handle_lobby_ave2_check_request(self, request: Node) -> Node:
        root = Node.void("lobby_ave2")
        data = Node.void("data")
        root.add_child(data)

        data.add_child(Node.s16("interval", 0))
        data.add_child(Node.s16("entry_timeout", 0))
        entrant_nr = Node.u32("entrant_nr", 0)
        entrant_nr.set_attribute("time", "0")
        data.add_child(entrant_nr)

        return root


class JubeatGamendRegisterHandler(JubeatBase):
    def handle_gameend_regist_request(self, request: Node) -> Node:
        data = request.child("data")
        player = data.child("player")

        if player is not None:
            refid = player.child_value("refid")
        else:
            refid = None

        if refid is not None:
            userid = self.data.remote.user.from_refid(self.game, self.version, refid)
        else:
            userid = None

        if userid is not None:
            oldprofile = self.get_profile(userid)
            newprofile = self.unformat_profile(userid, request, oldprofile)
        else:
            newprofile = None

        if userid is not None and newprofile is not None:
            self.put_profile(userid, newprofile)

        gameend = Node.void("gameend")
        data = Node.void("data")
        gameend.add_child(data)
        player = Node.void("player")
        data.add_child(player)
        player.add_child(Node.s32("session_id", 1))
        player.add_child(Node.s32("end_final_session_id", 1))
        return gameend

    def handle_gameend_ave_regist_request(self, request: Node) -> Node:
        data = request.child("data")
        player = data.child("player")

        if player is not None:
            refid = player.child_value("refid")
        else:
            refid = None

        if refid is not None:
            userid = self.data.remote.user.from_refid(self.game, self.version, refid)
        else:
            userid = None

        if userid is not None:
            oldprofile = self.get_profile(userid)
            newprofile = self.unformat_profile(userid, request, oldprofile)
        else:
            newprofile = None

        if userid is not None and newprofile is not None:
            self.put_profile(userid, newprofile)

        gameend_ave = Node.void("gameend_ave")
        data = Node.void("data")
        gameend_ave.add_child(data)
        player = Node.void("player")
        data.add_child(player)
        player.add_child(Node.s32("session_id", 1))
        player.add_child(Node.s32("end_final_session_id", 1))
        return gameend_ave

    def handle_gameend_ave2_regist_request(self, request: Node) -> Node:
        data = request.child("data")
        player = data.child("player")

        if player is not None:
            refid = player.child_value("refid")
        else:
            refid = None

        if refid is not None:
            userid = self.data.remote.user.from_refid(self.game, self.version, refid)
        else:
            userid = None

        if userid is not None:
            oldprofile = self.get_profile(userid)
            newprofile = self.unformat_profile(userid, request, oldprofile)
        else:
            newprofile = None

        if userid is not None and newprofile is not None:
            self.put_profile(userid, newprofile)

        gameend_ave2 = Node.void("gameend_ave2")
        data = Node.void("data")
        gameend_ave2.add_child(data)
        player = Node.void("player")
        data.add_child(player)
        player.add_child(Node.s32("session_id", 1))
        player.add_child(Node.s32("end_final_session_id", 1))
        return gameend_ave2


class JubeatGametopGetMeetingHandler(JubeatBase):
    def handle_gametop_get_meeting_request(self, request: Node) -> Node:
        gametop = Node.void("gametop")
        data = Node.void("data")
        gametop.add_child(data)
        meeting = Node.void("meeting")
        data.add_child(meeting)
        single = Node.void("single")
        meeting.add_child(single)
        single.set_attribute("count", "0")
        tag = Node.void("tag")
        meeting.add_child(tag)
        tag.set_attribute("count", "0")
        reward = Node.void("reward")
        data.add_child(reward)
        reward.add_child(Node.s32("total", -1))
        reward.add_child(Node.s32("point", -1))
        return gametop

    def handle_gametop_ave_get_meeting_request(self, request: Node) -> Node:
        gametop_ave = Node.void("gametop_ave")
        data = Node.void("data")
        gametop_ave.add_child(data)
        meeting = Node.void("meeting")
        data.add_child(meeting)
        single = Node.void("single")
        meeting.add_child(single)
        single.set_attribute("count", "0")
        # tag = Node.void("tag")
        # meeting.add_child(tag)
        # tag.set_attribute("count", "0")
        reward = Node.void("reward")
        data.add_child(reward)
        reward.add_child(Node.s32("total", 0))
        reward.add_child(Node.s32("point", 0))
        return gametop_ave

    def handle_gametop_ave2_get_meeting_request(self, request: Node) -> Node:
        gametop_ave2 = Node.void("gametop_ave2")
        data = Node.void("data")
        gametop_ave2.add_child(data)
        meeting = Node.void("meeting")
        data.add_child(meeting)
        single = Node.void("single")
        meeting.add_child(single)
        single.set_attribute("count", "0")
        # tag = Node.void("tag")
        # meeting.add_child(tag)
        # tag.set_attribute("count", "0")
        reward = Node.void("reward")
        data.add_child(reward)
        reward.add_child(Node.s32("total", 0))
        reward.add_child(Node.s32("point", 0))
        return gametop_ave2


# Jubeat Ave specific handlers. Really I think these should be moved into Avenue.py
# Largely because there's no reason to import them when playing any other Jubeat game lol
# Other option is to leave them here and import the Classes into Avenue.py


# class JubeatAveLoggerReportHandler(JubeatBase):
#     def handle_logger_ave_report_request(self, request: Node) -> Node:
#         # Handle this by returning nothing, game doesn't care
#         root = Node.void("logger_ave")
#         return root


# class JubeatDemodataAveGetNewsHandler(JubeatBase):
#     def handle_demodata_ave_get_news_request(self, request: Node) -> Node:
#         demodata_ave = Node.void("demodata_ave")
#         data = Node.void("data")
#         demodata_ave.add_child(data)

#         officialnews = Node.void("officialnews")
#         data.add_child(officialnews)
#         officialnews.set_attribute("count", "0")

#         return demodata_ave


# class JubeatDemodataAveGetHitchartHandler(JubeatBase):
#     def handle_demodata_ave_get_hitchart_request(self, request: Node) -> Node:
#         demodata_ave = Node.void("demodata_ave")
#         data = Node.void("data")
#         demodata_ave.add_child(data)

#         # Not sure what this is, maybe date?
#         data.add_child(Node.string("update", time.strftime("%d/%m/%Y")))

#         # No idea which songs are licensed or regular, so only return hit chart
#         # for all songs on regular mode.
#         hitchart_lic = Node.void("hitchart_lic")
#         data.add_child(hitchart_lic)
#         hitchart_lic.set_attribute("count", "0")

#         songs = self.data.local.music.get_hit_chart(self.game, self.music_version, 10)
#         hitchart_org = Node.void("hitchart_org")
#         data.add_child(hitchart_org)
#         hitchart_org.set_attribute("count", str(len(songs)))
#         rank = 1
#         for song in songs:
#             rankdata = Node.void("rankdata")
#             hitchart_org.add_child(rankdata)
#             rankdata.add_child(Node.s32("music_id", song[0]))
#             rankdata.add_child(Node.s16("rank", rank))
#             rankdata.add_child(Node.s16("prev", rank))
#             rank = rank + 1

#         return demodata_ave


# class JubeatAveLobbyCheckHandler(JubeatBase):
#     def handle_lobby_ave_check_request(self, request: Node) -> Node:
#         root = Node.void("lobby_ave")
#         data = Node.void("data")
#         root.add_child(data)

#         data.add_child(Node.s16("interval", 0))
#         data.add_child(Node.s16("entry_timeout", 0))
#         entrant_nr = Node.u32("entrant_nr", 0)
#         entrant_nr.set_attribute("time", "0")
#         data.add_child(entrant_nr)

#         return root


# class JubeatGamendAveRegisterHandler(JubeatBase):
#     def handle_gameend_ave_regist_request(self, request: Node) -> Node:
#         data = request.child("data")
#         player = data.child("player")

#         if player is not None:
#             refid = player.child_value("refid")
#         else:
#             refid = None

#         if refid is not None:
#             userid = self.data.remote.user.from_refid(self.game, self.version, refid)
#         else:
#             userid = None

#         if userid is not None:
#             oldprofile = self.get_profile(userid)
#             newprofile = self.unformat_profile(userid, request, oldprofile)
#         else:
#             newprofile = None

#         if userid is not None and newprofile is not None:
#             self.put_profile(userid, newprofile)

#         gameend_ave = Node.void("gameend_ave")
#         data = Node.void("data")
#         gameend_ave.add_child(data)
#         player = Node.void("player")
#         data.add_child(player)
#         player.add_child(Node.s32("session_id", 1))
#         player.add_child(Node.s32("end_final_session_id", 1))
#         return gameend_ave


# class JubeatGametopAveGetMeetingHandler(JubeatBase):
#     def handle_gametop_ave_get_meeting_request(self, request: Node) -> Node:
#         gametop_ave = Node.void("gametop_ave")
#         data = Node.void("data")
#         gametop_ave.add_child(data)
#         meeting = Node.void("meeting")
#         data.add_child(meeting)
#         single = Node.void("single")
#         meeting.add_child(single)
#         single.set_attribute("count", "0")
#         tag = Node.void("tag")
#         meeting.add_child(tag)
#         tag.set_attribute("count", "0")
#         reward = Node.void("reward")
#         data.add_child(reward)
#         reward.add_child(Node.s32("total", -1))
#         reward.add_child(Node.s32("point", -1))
#         return gametop_ave
