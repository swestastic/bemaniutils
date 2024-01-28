import random
import time
from typing import Any, Dict, List, Optional

from bemani.client.base import BaseClient
from bemani.common import CardCipher, Time
from bemani.protocol import Node


class JubeatAvenueBeyondClient(BaseClient):
    NAME = "TEST"

    def __verify_info(self, resp: Node, base: str) -> None:
        # Verify that response is correct
        self.assert_path(resp, f"response/{base}/data/info/event_info")
        self.assert_path(resp, f"response/{base}/data/info/genre_def_music")
        self.assert_path(resp, f"response/{base}/data/info/black_jacket_list")
        self.assert_path(resp, f"response/{base}/data/info/white_music_list")
        self.assert_path(resp, f"response/{base}/data/info/white_marker_list")
        self.assert_path(resp, f"response/{base}/data/info/white_theme_list")
        self.assert_path(resp, f"response/{base}/data/info/open_music_list")
        self.assert_path(resp, f"response/{base}/data/info/shareable_music_list")
        self.assert_path(resp, f"response/{base}/data/info/hot_music_list")
        self.assert_path(resp, f"response/{base}/data/info/jbox/point")
        self.assert_path(resp, f"response/{base}/data/info/jbox/emblem/normal/index")
        self.assert_path(resp, f"response/{base}/data/info/jbox/emblem/premium/index")
        self.assert_path(resp, f"response/{base}/data/info/born/status")
        self.assert_path(resp, f"response/{base}/data/info/born/year")
        self.assert_path(resp, f"response/{base}/data/info/konami_logo_50th/is_available")
        self.assert_path(resp, f"response/{base}/data/info/expert_option/is_available")
        self.assert_path(resp, f"response/{base}/data/info/all_music_matching/is_available")
        self.assert_path(resp, f"response/{base}/data/info/department/shop_list")
        self.assert_path(resp, f"response/{base}/data/info/question_list")
        # Don't bother asserting on actual courses, this is highly specific.
        self.assert_path(resp, f"response/{base}/data/info/course_list")
        self.assert_path(resp, f"response/{base}/data/info/share_music")
        self.assert_path(resp, f"response/{base}/data/info/weekly_music/value")
        self.assert_path(resp, f"response/{base}/data/info/weekly_music/music_list")
        self.assert_path(resp, f"response/{base}/data/info/add_default_music_list")

        # These below I'm not sure are needed, and I think some of them mess with stone tablet.
        self.assert_path(resp, f"response/{base}/data/info/team_battle")
        # self.assert_path(resp, f"response/{base}/data/info/emo_list")
        # self.assert_path(resp, f"response/{base}/data/info/hike_event")
        # self.assert_path(resp, f"response/{base}/data/info/tip_list")
        # self.assert_path(resp, f"response/{base}/data/info/travel")
        # self.assert_path(resp, f"response/{base}/data/info/stamp")

    def verify_shopinfo_ave2_regist(self) -> None:
        call = self.call_node()

        # Construct node
        shopinfo_ave2 = Node.void("shopinfo_ave2")
        shopinfo_ave2.set_attribute("method", "regist")
        call.add_child(shopinfo_ave2)
        shop = Node.void("shop")
        shopinfo_ave2.add_child(shop)
        shop.add_child(Node.string("name", ""))
        shop.add_child(Node.string("pref", "JP-14"))
        shop.add_child(Node.string("softwareid", ""))
        shop.add_child(Node.string("systemid", self.pcbid))
        shop.add_child(Node.string("hardwareid", "01020304050607080900"))
        shop.add_child(Node.string("locationid", "US-1"))
        shop.add_child(Node.string("monitor", "D26L155             6252     151"))
        testmode = Node.void("testmode")
        shop.add_child(testmode)
        sound = Node.void("sound")
        testmode.add_child(sound)
        sound.add_child(Node.u8("volume_in_attract", 0))
        game = Node.void("game")
        testmode.add_child(game)
        play_settings = Node.void("play_settings")
        game.add_child(play_settings)
        play_settings.add_child(Node.u8("max_member", 1))
        game_settings = Node.void("game_settings")
        game.add_child(game_settings)
        game_settings.add_child(Node.u8("close_set", 0))
        game_settings.add_child(Node.s32("close_time", 0))
        display_type_settings = Node.void("display_type_settings")
        game.add_child(display_type_settings)
        display_type_settings.add_child(Node.u8("display_type", 2))
        coin = Node.void("coin")
        testmode.add_child(coin)
        coin.add_child(Node.u8("free_play", 0))
        coin.add_child(Node.u8("free_first_play", 1))
        coin.add_child(Node.u8("coin_slot", 8))
        coin.add_child(Node.u8("start", 1))
        network = Node.void("network")
        testmode.add_child(network)
        network.add_child(Node.u8("cabinet_id", 1))
        bookkeeping = Node.void("bookkeeping")
        testmode.add_child(bookkeeping)
        bookkeeping.add_child(Node.u8("enable", 0))
        clock = Node.void("clock")
        testmode.add_child(clock)
        clock.add_child(Node.u8("enable", 1))
        clock.add_child(Node.s32("offset", 0))
        virtual_coin = Node.void("virtual_coin")
        testmode.add_child(virtual_coin)
        pattern1 = Node.void("pattern1")
        virtual_coin.add_child(pattern1)
        pattern1.add_child(Node.u16("basic_rate", 1000))
        pattern1.add_child(Node.u8("balance_of_credit", 0))
        pattern1.add_child(Node.u8("is_premium_start", 0))
        pattern1.add_child(Node.u8("service_value", 10))
        pattern1.add_child(Node.u8("service_limit", 10))
        pattern1.add_child(Node.u8("service_time_start_h", 7))
        pattern1.add_child(Node.u8("service_time_start_m", 0))
        pattern1.add_child(Node.u8("service_time_end_h", 11))
        pattern1.add_child(Node.u8("service_time_end_m", 0))
        pattern2 = Node.void("pattern2")
        virtual_coin.add_child(pattern2)
        pattern2.add_child(Node.u16("basic_rate", 1000))
        pattern2.add_child(Node.u8("balance_of_credit", 0))
        pattern2.add_child(Node.u8("is_premium_start", 0))
        pattern2.add_child(Node.u8("service_value", 10))
        pattern2.add_child(Node.u8("service_limit", 10))
        pattern2.add_child(Node.u8("service_time_start_h", 7))
        pattern2.add_child(Node.u8("service_time_start_m", 0))
        pattern2.add_child(Node.u8("service_time_end_h", 11))
        pattern2.add_child(Node.u8("service_time_end_m", 0))
        pattern3 = Node.void("pattern3")
        virtual_coin.add_child(pattern3)
        pattern3.add_child(Node.u16("basic_rate", 1000))
        pattern3.add_child(Node.u8("balance_of_credit", 0))
        pattern3.add_child(Node.u8("is_premium_start", 0))
        pattern3.add_child(Node.u8("service_value", 10))
        pattern3.add_child(Node.u8("service_limit", 10))
        pattern3.add_child(Node.u8("service_time_start_h", 7))
        pattern3.add_child(Node.u8("service_time_start_m", 0))
        pattern3.add_child(Node.u8("service_time_end_h", 11))
        pattern3.add_child(Node.u8("service_time_end_m", 0))
        schedule = Node.void("schedule")
        virtual_coin.add_child(schedule)
        schedule.add_child(Node.u8("mon", 0))
        schedule.add_child(Node.u8("tue", 0))
        schedule.add_child(Node.u8("wed", 0))
        schedule.add_child(Node.u8("thu", 0))
        schedule.add_child(Node.u8("fri", 0))
        schedule.add_child(Node.u8("sat", 0))
        schedule.add_child(Node.u8("sun", 0))
        schedule.add_child(Node.u8("holi", 0))
        tax = Node.void("tax")
        testmode.add_child(tax)
        tax.add_child(Node.u8("tax_phase", 0))
        tax.add_child(Node.u8("tax_mode", 0))

        # Swap with server
        resp = self.exchange("", call)

        self.assert_path(resp, "response/shopinfo_ave2/data/cabid")
        self.assert_path(resp, "response/shopinfo_ave2/data/locationid")
        self.assert_path(resp, "response/shopinfo_ave2/data/tax_phase")
        self.assert_path(resp, "response/shopinfo_ave2/data/facility/exist")

        # Verify server flags for events and stuff.
        self.__verify_info(resp, "shopinfo_ave2")

    def verify_logger_ave2_report(self) -> None:
        call = self.call_node()

        # Construct node
        logger_ave2 = Node.void("logger_ave2")
        call.add_child(logger_ave2)
        logger_ave2.set_attribute("method", "report")
        logger_ave2.add_child(Node.s32("retry", 0))
        data = Node.void("data")
        logger_ave2.add_child(data)
        data.add_child(Node.string("code", "pcbinfo_01"))
        data.add_child(Node.string("information", "u can literally put anything here lmao"))

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/2/@status")

    def verify_demodata_ave2_get_info(self) -> None:
        call = self.call_node()

        # Construct node
        demodata_ave2 = Node.void("demodata_ave2")
        call.add_child(demodata_ave2)
        demodata_ave2.set_attribute("method", "get_info")
        pcbinfo = Node.void("pcbinfo")
        demodata_ave2.add_child(pcbinfo)
        pcbinfo.set_attribute("client_data_version", "0")

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/demodata_ave2/data/info/black_jacket_list")

    def verify_demodata_ave2_get_news(self) -> None:
        call = self.call_node()

        # Construct node
        demodata_ave2 = Node.void("demodata_ave2")
        call.add_child(demodata_ave2)
        demodata_ave2.set_attribute("method", "get_news")

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/demodata_ave2/data/officialnews/@count")

    def verify_demodata_ave2_get_jbox_list(self) -> None:
        call = self.call_node()

        # Construct node
        demodata_ave2 = Node.void("demodata_ave2")
        call.add_child(demodata_ave2)
        demodata_ave2.set_attribute("method", "get_jbox_list")

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/demodata_ave2/@status")

    def verify_lab_ave2_get_ranking(self) -> None:
        call = self.call_node()

        # Construct node
        lab_ave2 = Node.void("lab_ave2")
        call.add_child(lab_ave2)
        lab_ave2.set_attribute("method", "get_ranking")
        lab_ave2.add_child(Node.s32("retry", 0))
        lab_ave2.add_child(Node.s8("category", 1))

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/lab_ave2/category")
        self.assert_path(resp, "response/lab_ave2/entries/@count")

        # Category should be the same as when we requested it.
        if resp.child_value("lab_ave2/category") != 1:
            raise Exception("Lab_ave category did not get round-tripped!")

    def __verify_profile(self, resp: Node, should_inherit: bool) -> int:
        for item in [
            "tune_cnt",
            "save_cnt",
            "saved_cnt",
            "fc_cnt",
            "ex_cnt",
            "clear_cnt",
            "match_cnt",
            "beat_cnt",
            "mynews_cnt",
            "bonus_tune_points",
            "is_bonus_tune_played",
            "inherit",
            "mtg_entry_cnt",
            "mtg_hold_cnt",
            "mtg_result",
        ]:
            self.assert_path(resp, f"response/gametop_ave2/data/player/info/{item}")

        # Technically we could use this to check profile succession doesn't show the
        # tutorial, but we don't go that far yet.
        if resp.child_value("gametop_ave2/data/player/info/inherit") != should_inherit:
            raise Exception("Inherit flag wrong for profile!")

        for item in [
            "music_list",
            "secret_list",
            "theme_list",
            "marker_list",
            "title_list",
            "parts_list",
            "emblem_list",
            "commu_list",
            "new/secret_list",
            "new/theme_list",
            "new/marker_list",
        ]:
            self.assert_path(resp, f"response/gametop_ave2/data/player/item/{item}")

        for item in [
            "play_time",
            "shopname",
            "areaname",
            "music_id",
            "seq_id",
            "sort",
            "category",
            "expert_option",
        ]:
            self.assert_path(resp, f"response/gametop_ave2/data/player/last/{item}")

        for item in [
            "marker",
            "theme",
            "title",
            "parts",
            "rank_sort",
            "combo_disp",
            "emblem",
            "matching",
            "hard",
            "hazard",
        ]:
            self.assert_path(resp, f"response/gametop_ave2/data/player/last/settings/{item}")

        # Misc stuff
        self.assert_path(resp, "response/gametop_ave2/data/player/session_id")
        self.assert_path(resp, "response/gametop_ave2/data/player/event_flag")

        # Profile settings
        self.assert_path(resp, "response/gametop_ave2/data/player/name")
        self.assert_path(resp, "response/gametop_ave2/data/player/jid")
        if resp.child_value("gametop_ave2/data/player/name") != self.NAME:
            raise Exception("Unexpected name received from server!")

        # Required nodes for events and stuff
        self.assert_path(resp, "response/gametop_ave2/data/player/rivallist")
        self.assert_path(resp, "response/gametop_ave2/data/player/lab_edit_seq")
        self.assert_path(resp, "response/gametop_ave2/data/player/fc_challenge/today/music_id")
        self.assert_path(resp, "response/gametop_ave2/data/player/fc_challenge/today/state")
        self.assert_path(resp, "response/gametop_ave2/data/player/fc_challenge/whim/music_id")
        self.assert_path(resp, "response/gametop_ave2/data/player/fc_challenge/whim/state")
        self.assert_path(resp, "response/gametop_ave2/data/player/official_news/news_list")
        self.assert_path(resp, "response/gametop_ave2/data/player/history/@count")
        self.assert_path(resp, "response/gametop_ave2/data/player/free_first_play/is_available")
        self.assert_path(resp, "response/gametop_ave2/data/player/event_info")
        self.assert_path(resp, "response/gametop_ave2/data/player/jbox/point")
        self.assert_path(resp, "response/gametop_ave2/data/player/jbox/emblem/normal/index")
        self.assert_path(resp, "response/gametop_ave2/data/player/jbox/emblem/premium/index")
        self.assert_path(resp, "response/gametop_ave2/data/player/new_music")
        self.assert_path(resp, "response/gametop_ave2/data/player/navi/flag")
        self.assert_path(resp, "response/gametop_ave2/data/player/gift_list")
        self.assert_path(resp, "response/gametop_ave2/data/player/born/status")
        self.assert_path(resp, "response/gametop_ave2/data/player/born/year")
        self.assert_path(resp, "response/gametop_ave2/data/player/question_list")
        self.assert_path(resp, "response/gametop_ave2/data/player/emo_list")
        self.assert_path(resp, "response/gametop_ave2/data/player/server")
        self.assert_path(resp, "response/gametop_ave2/data/player/course_list")
        self.assert_path(resp, "response/gametop_ave2/data/player/course_list/category_list")
        self.assert_path(
            resp,
            "response/gametop_ave2/data/player/fill_in_category/normal/no_gray_flag_list",
        )
        self.assert_path(
            resp,
            "response/gametop_ave2/data/player/fill_in_category/normal/all_yellow_flag_list",
        )
        self.assert_path(
            resp,
            "response/gametop_ave2/data/player/fill_in_category/normal/full_combo_flag_list",
        )
        self.assert_path(
            resp,
            "response/gametop_ave2/data/player/fill_in_category/normal/excellent_flag_list",
        )
        self.assert_path(
            resp, "response/gametop_ave2/data/player/fill_in_category/hard/no_gray_flag_list"
        )
        self.assert_path(
            resp,
            "response/gametop_ave2/data/player/fill_in_category/hard/all_yellow_flag_list",
        )
        self.assert_path(
            resp,
            "response/gametop_ave2/data/player/fill_in_category/hard/full_combo_flag_list",
        )
        self.assert_path(
            resp,
            "response/gametop_ave2/data/player/fill_in_category/hard/excellent_flag_list",
        )
        self.assert_path(resp, "response/gametop_ave2/data/player/department/shop_list")
        self.assert_path(resp, "response/gametop_ave2/data/player/stamp/sheet_list")
        self.assert_path(resp, "response/gametop_ave2/data/player/festo_dungeon/phase")
        self.assert_path(resp, "response/gametop_ave2/data/player/festo_dungeon/clear_flag")

        # Return the jid
        return resp.child_value("gametop_ave2/data/player/jid")

    def verify_gameend_ave2_regist(
        self,
        ref_id: str,
        jid: int,
        scores: List[Dict[str, Any]],
    ) -> None:
        call = self.call_node()

        # Construct node
        gameend_ave2 = Node.void("gameend_ave2")
        call.add_child(gameend_ave2)
        gameend_ave2.set_attribute("method", "regist")
        gameend_ave2.add_child(Node.s32("retry", 0))
        pcbinfo = Node.void("pcbinfo")
        gameend_ave2.add_child(pcbinfo)
        pcbinfo.set_attribute("client_data_version", "0")
        data = Node.void("data")
        gameend_ave2.add_child(data)
        player = Node.void("player")
        data.add_child(player)
        player.add_child(Node.string("refid", ref_id))
        player.add_child(Node.s32("jid", jid))
        player.add_child(Node.string("name", self.NAME))
        result = Node.void("result")
        data.add_child(result)
        result.set_attribute("count", str(len(scores)))

        # Send scores
        scoreid = 0
        for score in scores:
            # Always played
            bits = 0x1
            if score["clear"]:
                bits |= 0x2
            if score["fc"]:
                bits |= 0x4
            if score["ex"]:
                bits |= 0x8

            # Intentionally starting at 1 because that's what the game does
            scoreid = scoreid + 1
            tune = Node.void("tune")
            result.add_child(tune)
            tune.set_attribute("id", str(scoreid))
            tune.add_child(Node.s32("music", score["id"]))
            tune.add_child(Node.s64("timestamp", Time.now() * 1000))
            player_1 = Node.void("player")
            tune.add_child(player_1)
            player_1.set_attribute("rank", "1")
            scorenode = Node.s32("score", score["score"])
            player_1.add_child(scorenode)
            scorenode.set_attribute("seq", str(score["chart"]))
            scorenode.set_attribute("clear", str(bits))
            scorenode.set_attribute("combo", "69")
            player_1.add_child(
                Node.u8_array(
                    "mbar",
                    [
                        239,
                        175,
                        170,
                        170,
                        190,
                        234,
                        187,
                        158,
                        153,
                        230,
                        170,
                        90,
                        102,
                        170,
                        85,
                        150,
                        150,
                        102,
                        85,
                        234,
                        171,
                        169,
                        157,
                        150,
                        170,
                        101,
                        230,
                        90,
                        214,
                        255,
                    ],
                )
            )
            player_1.add_child(Node.bool("is_hard_mode", score["hard"]))
            player_1.add_child(Node.s32("music_rate", score["rate"]))

        # Swap with server
        resp = self.exchange("", call)
        self.assert_path(resp, "response/gameend_ave2/data/player/session_id")
        self.assert_path(resp, "response/gameend_ave2/data/player/end_final_session_id")

    def verify_gameend_ave2_final(
        self,
        ref_id: str,
        jid: int,
    ) -> None:
        call = self.call_node()

        # Construct node
        gameend_ave2 = Node.void("gameend_ave2")
        call.add_child(gameend_ave2)
        gameend_ave2.set_attribute("method", "final")
        gameend_ave2.add_child(Node.s32("retry", 0))
        pcbinfo = Node.void("pcbinfo")
        gameend_ave2.add_child(pcbinfo)
        pcbinfo.set_attribute("client_data_version", "0")
        data = Node.void("data")
        gameend_ave2.add_child(data)
        info = Node.void("info")
        data.add_child(info)
        born = Node.void("born")
        info.add_child(born)
        born.add_child(Node.s8("status", 3))
        born.add_child(Node.s16("year", 0))
        info.add_child(Node.void("question_list"))
        player = Node.void("player")
        data.add_child(player)
        player.add_child(Node.string("refid", ref_id))
        player.add_child(Node.s32("jid", jid))
        jbox = Node.void("jbox")
        player.add_child(jbox)
        jbox.add_child(Node.s32("point", 0))
        emblem = Node.void("emblem")
        jbox.add_child(emblem)
        emblem.add_child(Node.u8("type", 0))
        emblem.add_child(Node.s16("index", 0))

        # Swap with server
        resp = self.exchange("", call)
        self.assert_path(resp, "response/gameend_ave2/@status")

    def verify_gametop_ave2_regist(self, card_id: str, ref_id: str) -> int:
        call = self.call_node()

        # Construct node
        gametop_ave2 = Node.void("gametop_ave2")
        call.add_child(gametop_ave2)
        gametop_ave2.set_attribute("method", "regist")
        data = Node.void("data")
        gametop_ave2.add_child(data)
        player = Node.void("player")
        data.add_child(player)
        player.add_child(Node.string("refid", ref_id))
        player.add_child(Node.string("datid", ref_id))
        player.add_child(Node.string("uid", card_id))
        player.add_child(Node.bool("inherit", True))
        player.add_child(Node.string("name", self.NAME))

        # Swap with server
        resp = self.exchange("", call)

        # Verify server flags for events and stuff.
        self.__verify_info(resp, "gametop_ave2")

        # Verify nodes that cause crashes or failed card-ins if they don't exist
        return self.__verify_profile(resp, False)

    def verify_gametop_ave2_get_pdata(self, card_id: str, ref_id: str) -> int:
        call = self.call_node()

        # Construct node
        gametop_ave2 = Node.void("gametop_ave2")
        call.add_child(gametop_ave2)
        gametop_ave2.set_attribute("method", "get_pdata")
        retry = Node.s32("retry", 0)
        gametop_ave2.add_child(retry)
        data = Node.void("data")
        gametop_ave2.add_child(data)
        player = Node.void("player")
        data.add_child(player)
        player.add_child(Node.string("refid", ref_id))
        player.add_child(Node.string("datid", ref_id))
        player.add_child(Node.string("uid", card_id))
        player.add_child(Node.string("card_no", CardCipher.encode(card_id)))

        # Swap with server
        resp = self.exchange("", call)

        # Verify nodes that cause crashes if they don't exist
        return self.__verify_profile(resp, False)

    def verify_gametop_ave2_get_mdata(self, jid: int) -> Dict[str, List[Dict[str, Any]]]:
        ret = {}
        for ver in [1, 2, 3]:
            # Construct node
            call = self.call_node()
            gametop_ave2 = Node.void("gametop_ave2")
            call.add_child(gametop_ave2)
            gametop_ave2.set_attribute("method", "get_mdata")
            retry = Node.s32("retry", 0)
            gametop_ave2.add_child(retry)
            data = Node.void("data")
            gametop_ave2.add_child(data)
            player = Node.void("player")
            data.add_child(player)
            player.add_child(Node.s32("jid", jid))
            player.add_child(Node.s8("mdata_ver", ver))
            player.add_child(Node.bool("rival", False))

            # Swap with server
            resp = self.exchange("", call)

            # Parse out scores
            self.assert_path(resp, "response/gametop_ave2/data/player/jid")
            self.assert_path(resp, "response/gametop_ave2/data/player/mdata_list")
            if resp.child_value("gametop_ave2/data/player/jid") != jid:
                raise Exception("Unexpected jid received from server!")

            for musicdata in resp.child("gametop_ave2/data/player/mdata_list").children:
                if musicdata.name != "musicdata":
                    raise Exception("Unexpected node in playdata!")

                music_id = musicdata.attribute("music_id")
                scores_by_chart: List[Dict[str, int]] = [{}, {}, {}, {}, {}, {}]

                def extract_cnts(name: str, offset: int, val: List[int]) -> None:
                    scores_by_chart[offset + 0][name] = val[0]
                    scores_by_chart[offset + 1][name] = val[1]
                    scores_by_chart[offset + 2][name] = val[2]

                for subdata in musicdata.children:
                    if subdata.name == "normal":
                        offset = 0
                    elif subdata.name == "hard":
                        offset = 3
                    else:
                        raise Exception(f"Unexpected chart type {subdata.name}!")

                    extract_cnts("plays", offset, subdata.child_value("play_cnt"))
                    extract_cnts("clears", offset, subdata.child_value("clear_cnt"))
                    extract_cnts("full_combos", offset, subdata.child_value("fc_cnt"))
                    extract_cnts("excellents", offset, subdata.child_value("ex_cnt"))
                    extract_cnts("score", offset, subdata.child_value("score"))
                    extract_cnts("medal", offset, subdata.child_value("clear"))
                    extract_cnts("rate", offset, subdata.child_value("music_rate"))

                ret[music_id] = scores_by_chart

        return ret

    def verify_gametop_ave2_get_meeting(self, jid: int) -> None:
        call = self.call_node()

        # Construct node
        gametop_ave2 = Node.void("gametop_ave2")
        call.add_child(gametop_ave2)
        gametop_ave2.set_attribute("method", "get_meeting")
        gametop_ave2.add_child(Node.s32("retry", 0))
        data = Node.void("data")
        gametop_ave2.add_child(data)
        player = Node.void("player")
        data.add_child(player)
        player.add_child(Node.s32("jid", jid))
        pcbinfo = Node.void("pcbinfo")
        gametop_ave2.add_child(pcbinfo)
        pcbinfo.set_attribute("client_data_version", "0")

        # Swap with server
        resp = self.exchange("", call)

        # Verify expected nodes
        self.assert_path(resp, "response/gametop_ave2/data/meeting/single/@count")
        # self.assert_path(resp, "response/gametop_ave2/data/meeting/tag/@count") # BROKEN! FIX ME!
        self.assert_path(resp, "response/gametop_ave2/data/reward/total")
        self.assert_path(resp, "response/gametop_ave2/data/reward/point")

    def verify_recommend_ave2_get_recommend(self, jid: int) -> None:
        call = self.call_node()

        # Construct node
        recommend_ave2 = Node.void("recommend_ave2")
        call.add_child(recommend_ave2)
        recommend_ave2.set_attribute("method", "get_recommend")
        recommend_ave2.add_child(Node.s32("retry", 0))
        player = Node.void("player")
        recommend_ave2.add_child(player)
        player.add_child(Node.s32("jid", jid))
        player.add_child(Node.void("music_list"))

        # Swap with server
        resp = self.exchange("", call)

        # Verify expected nodes
        self.assert_path(resp, "response/recommend_ave2/data/player/music_list")

    def verify_demodata_ave2_get_hitchart(self) -> None:
        call = self.call_node()

        # Construct node
        gametop_ave2 = Node.void("demodata_ave2")
        call.add_child(gametop_ave2)
        gametop_ave2.set_attribute("method", "get_hitchart")

        # Swap with server
        resp = self.exchange("", call)

        # Verify expected nodes
        self.assert_path(resp, "response/demodata_ave2/data/update")
        self.assert_path(resp, "response/demodata_ave2/data/hitchart_lic/@count")
        self.assert_path(resp, "response/demodata_ave2/data/hitchart_org/@count")

    def verify_jbox_ave2_get_list(self, jid: int) -> None:
        call = self.call_node()

        # Construct node
        jbox_ave2 = Node.void("jbox_ave2")
        call.add_child(jbox_ave2)
        jbox_ave2.set_attribute("method", "get_list")
        data = Node.void("data")
        jbox_ave2.add_child(data)
        player = Node.void("player")
        data.add_child(player)
        player.add_child(Node.s32("jid", jid))

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/jbox_ave2/selection_list")

    def verify_jbox_ave2_get_agreement(self, jid: int) -> None:
        call = self.call_node()

        # Construct node
        jbox_ave2 = Node.void("jbox_ave2")
        call.add_child(jbox_ave2)
        jbox_ave2.set_attribute("method", "get_agreement")
        data = Node.void("data")
        jbox_ave2.add_child(data)
        player = Node.void("player")
        data.add_child(player)
        player.add_child(Node.s32("jid", jid))

        # Swap with server
        resp = self.exchange("", call)

        # Verify that response is correct
        self.assert_path(resp, "response/jbox_ave2/is_agreement")

    def verify(self, cardid: Optional[str]) -> None:
        # Verify boot sequence is okay
        self.verify_services_get(
            expected_services=[
                "pcbtracker",
                "pcbevent",
                "local",
                "message",
                "facility",
                "cardmng",
                "package",
                "posevent",
                "pkglist",
                "dlstatus",
                "eacoin",
                "lobby",
                "netlog",
                "slocal",
                "ntp",
                "keepalive",
            ],
            include_net=True,
        )
        paseli_enabled = self.verify_pcbtracker_alive(ecflag=3)
        self.verify_package_list()
        self.verify_message_get()
        self.verify_facility_get(encoding="Shift-JIS")
        self.verify_pcbevent_put()
        self.verify_logger_ave2_report()
        self.verify_shopinfo_ave2_regist()
        self.verify_demodata_ave2_get_info()
        self.verify_demodata_ave2_get_jbox_list()
        self.verify_demodata_ave2_get_news()
        self.verify_demodata_ave2_get_hitchart()
        self.verify_lab_ave2_get_ranking()

        # Verify card registration and profile lookup
        if cardid is not None:
            card = cardid
        else:
            card = self.random_card()
            print(f"Generated random card ID {card} for use.")

        if cardid is None:
            self.verify_cardmng_inquire(card, msg_type="unregistered", paseli_enabled=paseli_enabled)
            ref_id = self.verify_cardmng_getrefid(card)
            if len(ref_id) != 16:
                raise Exception(f"Invalid refid '{ref_id}' returned when registering card")
            if ref_id != self.verify_cardmng_inquire(card, msg_type="new", paseli_enabled=paseli_enabled):
                raise Exception(f"Invalid refid '{ref_id}' returned when querying card")
            self.verify_gametop_ave_regist(card, ref_id)
        else:
            print("Skipping new card checks for existing card")
            ref_id = self.verify_cardmng_inquire(card, msg_type="query", paseli_enabled=paseli_enabled)

        # Verify pin handling and return card handling
        self.verify_cardmng_authpass(ref_id, correct=True)
        self.verify_cardmng_authpass(ref_id, correct=False)
        if ref_id != self.verify_cardmng_inquire(card, msg_type="query", paseli_enabled=paseli_enabled):
            raise Exception(f"Invalid refid '{ref_id}' returned when querying card")

        if cardid is None:
            # Verify score handling
            jid = self.verify_gametop_ave2_get_pdata(card, ref_id)
            self.verify_recommend_ave2_get_recommend(jid)
            scores = self.verify_gametop_ave2_get_mdata(jid)
            self.verify_gametop_ave2_get_meeting(jid)
            if scores is None:
                raise Exception("Expected to get scores back, didn't get anything!")
            if len(scores) > 0:
                raise Exception("Got nonzero score count on a new card!")

            # Verify end of game behavior
            self.verify_jbox_ave2_get_list(jid)
            self.verify_jbox_ave2_get_agreement(jid)
            self.verify_gameend_ave2_final(ref_id, jid)

            for phase in [1, 2]:
                if phase == 1:
                    dummyscores = [
                        # An okay score on a chart
                        {
                            "id": 40000059,
                            "chart": 2,
                            "hard": False,
                            "clear": True,
                            "fc": False,
                            "ex": False,
                            "score": 800000,
                            "rate": 567,
                            "expected_medal": 0x3,
                        },
                        # A good score on an easier chart of the same song
                        {
                            "id": 40000059,
                            "chart": 1,
                            "hard": False,
                            "clear": True,
                            "fc": True,
                            "ex": False,
                            "score": 990000,
                            "rate": 456,
                            "expected_medal": 0x5,
                        },
                        # A perfect score on an easiest chart of the same song
                        {
                            "id": 40000059,
                            "chart": 0,
                            "hard": False,
                            "clear": True,
                            "fc": True,
                            "ex": True,
                            "score": 1000000,
                            "rate": 678,
                            "expected_medal": 0x9,
                        },
                        # A bad score on a hard chart
                        {
                            "id": 30000027,
                            "chart": 2,
                            "hard": False,
                            "clear": False,
                            "fc": False,
                            "ex": False,
                            "score": 400000,
                            "rate": 123,
                            "expected_medal": 0x1,
                        },
                        # A terrible score on an easy chart
                        {
                            "id": 50000045,
                            "chart": 0,
                            "hard": False,
                            "clear": False,
                            "fc": False,
                            "ex": False,
                            "score": 100000,
                            "rate": 69,
                            "expected_medal": 0x1,
                        },
                        # A good score on a hard chart to make sure
                        # it doesn't pollute regular charts.
                        {
                            "id": 40000059,
                            "chart": 2,
                            "hard": True,
                            "clear": True,
                            "fc": False,
                            "ex": False,
                            "score": 812300,
                            "rate": 666,
                            "expected_medal": 0x3,
                        },
                    ]
                if phase == 2:
                    dummyscores = [
                        # A better score on the same chart
                        {
                            "id": 50000045,
                            "chart": 0,
                            "hard": False,
                            "clear": True,
                            "fc": False,
                            "ex": False,
                            "score": 850000,
                            "rate": 555,
                            "expected_medal": 0x3,
                        },
                        # A worse score on another same chart
                        {
                            "id": 40000059,
                            "chart": 1,
                            "hard": False,
                            "clear": True,
                            "fc": False,
                            "ex": False,
                            "score": 925000,
                            "rate": 432,
                            "expected_score": 990000,
                            "expected_rate": 456,
                            "expected_medal": 0x7,
                        },
                    ]

                self.verify_gameend_ave2_regist(ref_id, jid, dummyscores)
                jid = self.verify_gametop_ave2_get_pdata(card, ref_id)
                scores = self.verify_gametop_ave2_get_mdata(jid)

                for score in dummyscores:
                    chart = score["chart"] + (3 if score["hard"] else 0)
                    newscore = scores[str(score["id"])][chart]

                    if "expected_score" in score:
                        expected_score = score["expected_score"]
                    else:
                        expected_score = score["score"]

                    if "expected_rate" in score:
                        expected_rate = score["expected_rate"]
                    else:
                        expected_rate = score["rate"]

                    if newscore["score"] != expected_score:
                        raise Exception(
                            f'Expected a score of \'{expected_score}\' for song \'{score["id"]}\' chart \'{chart}\' but got score \'{newscore["score"]}\''
                        )

                    if newscore["rate"] != expected_rate:
                        raise Exception(
                            f'Expected a rate of \'{expected_rate}\' for song \'{score["id"]}\' chart \'{chart}\' but got rate \'{newscore["rate"]}\''
                        )

                    if newscore["medal"] != score["expected_medal"]:
                        raise Exception(
                            f'Expected a medal of \'{score["expected_medal"]}\' for song \'{score["id"]}\' chart \'{chart}\' but got medal \'{newscore["medal"]}\''
                        )

                # Sleep so we don't end up putting in score history on the same second
                time.sleep(1)

        else:
            print("Skipping score checks for existing card")

        # Verify paseli handling
        if paseli_enabled:
            print("PASELI enabled for this PCBID, executing PASELI checks")
        else:
            print("PASELI disabled for this PCBID, skipping PASELI checks")
            return

        sessid, balance = self.verify_eacoin_checkin(card)
        if balance == 0:
            print("Skipping PASELI consume check because card has 0 balance")
        else:
            self.verify_eacoin_consume(sessid, balance, random.randint(0, balance))
        self.verify_eacoin_checkout(sessid)
