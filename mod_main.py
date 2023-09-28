from datetime import datetime
import os
from tool import ToolUtil
from flask import Response
from .setup import *

try:
    if os.path.exists(os.path.join(os.path.dirname(__file__), "source_spotv_handler.py")):
        from .source_spotv_handler import SPOTV_Handler

    else:
        from support import SupportSC

        SPOTV_Handler = SupportSC.load_module_f(__file__, "source_spotv_handler").SPOTV_Handler
except:
    pass


class ModuleMain(PluginModuleBase):
    def __init__(self, P):
        super(ModuleMain, self).__init__(P, name="main", first_menu="setting")
        self.db_default = {
            f"{self.name}_db_version": "1",
            "use_spotv": "True",
            "use_spotvnow": "False",
            "use_today_vod": "False",
            "use_popular_vod": "False",
            "use_etc_vod": "True",
            "use_spotv_quality": "1920x1080",
            "spotv_streaming_type": "redirect",
            "spotv_username": "",
            "spotv_password": "",
            "use_proxy": "False",
            "use_proxy2": "False",
            "proxy_url": "",
        }

    def process_menu(self, sub, req):
        arg = P.ModelSetting.to_dict()
        arg["api_m3u"] = ToolUtil.make_apikey_url(f"/{P.package_name}/api/m3u")
        arg["api_yaml"] = ToolUtil.make_apikey_url(f"/{P.package_name}/api/yaml")
        if sub == "setting":
            arg["is_include"] = F.scheduler.is_include(self.get_scheduler_name())
            arg["is_running"] = F.scheduler.is_running(self.get_scheduler_name())
        return render_template(f"{P.package_name}_{self.name}_{sub}.html", arg=arg)

    def process_command(self, command, arg1, arg2, arg3, req):
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if command == "broad_list":
            return jsonify({"list": SPOTV_Handler.ch_list(), "updated_at": updated_at})
        elif command == "schedule_list":
            return jsonify({"list": SPOTV_Handler.schedule_list(), "updated_at": updated_at})
        elif command == "play_url":
            url = ToolUtil.make_apikey_url(f"/{P.package_name}/api/url.m3u8?ch_id={arg1}&type={arg3}")
            ret = {"ret": "success", "data": url, "title": arg2}
        return jsonify(ret)

    def process_api(self, sub, req):
        try:
            if sub == "m3u":
                return SPOTV_Handler.make_m3u()
            elif sub == "yaml":
                return SPOTV_Handler.make_yaml()
            elif sub == "url.m3u8":
                return SPOTV_Handler.url_m3u8(req)
            elif sub == "play":
                return SPOTV_Handler.play(req)
            elif sub == "segment":
                return SPOTV_Handler.segment(req)

        except Exception as e:
            P.logger.error(f"Exception:{str(e)}")
            P.logger.error(traceback.format_exc())
