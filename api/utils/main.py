from flask import Flask
from flask_cors import CORS # type: ignore
from flask_restful import Api, Resource
from typing import Any, Dict
import argparse
import yaml

# External APIs
from api.data.mysql import MySQLBase
from api.external.pfsense import PFSense
from api.external.backblaze import BackBlazeCDN
from api.external.mailjet import MailjetSMTP

# Bad Maniac Discord Bot
from api.external.badmaniac import BadManiac

# Services
from api.services.discord import OnboardingVPN, OnboardingArcade
from api.services.admin import AdminDashboard, OnboardArcade, Maintenance
from api.services.arcade import Arcades, ArcadeSettings, Paseli, VPN, CheckArcadeName, CheckPCBID, ArcadeTakeover
from api.services.news import getAllNews, getNews
from api.services.auth import UserSession, emailAuth, check2FAKey, resetPassword
from api.services.user import UserAccount, UserUpdatePassword, UserCard, UserTakeover, UserPlayVideos, UserContent, UserCustomize
from api.services.profiles import allPlayers, Profile, Achievements
from api.services.music import Music
from api.services.score import Attempts, Records

# Share server
from api.services.share import ShareServer, shareServerStatus, shareNewSession, shareBeginUpload, shareVideoUpload, shareEndUpload, shareLPACUpload

# Integrations
from api.services.integrate import Integrations, IntegrateDiscord, IntegrateTachi

# pop'n rhythmin API server
from api.services.apr.events import APREventInfo, APRFileList
from api.services.apr.session import APRNewSession, APRSaveSession
from api.services.apr.music import APRRecommendList, APRPackList
from api.services.apr.network import APRSearchMaster
from api.services.apr.user import APRPlayer, APRNewPlayer, APRLinkAccount, APRInvited, APRPresentList

app = Flask(__name__)
CORS(app)
api = Api(app)
config: Dict[str, Any] = {}

class restfulTop(Resource):
    def get(self):
        return "RestfulSleep is alive! PhaseII's powerful API used for bots, apps, and more."

# Base keep-alive
api.add_resource(restfulTop, '/')

# Admin
api.add_resource(AdminDashboard, '/v1/admin')
api.add_resource(OnboardArcade, '/v1/admin/onboardArcade')
api.add_resource(Maintenance, '/v1/admin/maint')

# Arcades
api.add_resource(Arcades, '/v1/arcade/<arcadeId>')
api.add_resource(ArcadeSettings, '/v1/arcade/<arcadeId>/settings')
api.add_resource(Paseli, '/v1/arcade/<arcadeId>/paseli')
api.add_resource(VPN, '/v1/arcade/<arcadeId>/exportVPN')
api.add_resource(CheckArcadeName, '/v1/arcade/checkName')
api.add_resource(CheckPCBID, '/v1/arcade/checkPCBID')
api.add_resource(ArcadeTakeover, '/v1/arcade/takeover')

# BadManiac Calls
api.add_resource(OnboardingVPN, '/v1/discord/exportVPN/<arcadeId>')
api.add_resource(OnboardingArcade, '/v1/discord/onboardArcade/<arcadeId>')

# News
api.add_resource(getAllNews, '/v1/news')
api.add_resource(getNews, '/v1/news/<newsId>')

# Authentication
api.add_resource(UserSession, '/v1/auth/session')
api.add_resource(emailAuth, '/v1/auth/emailAuth')
api.add_resource(check2FAKey, '/v1/auth/check2FAKey')
api.add_resource(resetPassword, '/v1/auth/changePassword')

# User Data
api.add_resource(UserAccount, '/v1/user')
api.add_resource(UserUpdatePassword, '/v1/user/updatePassword')
api.add_resource(UserCard, '/v1/user/card')
api.add_resource(UserTakeover, '/v1/user/takeover')
api.add_resource(UserPlayVideos, '/v1/user/playVideos')
api.add_resource(UserContent, '/v1/user/content')
api.add_resource(UserCustomize, '/v1/user/customize')

# Integration callbacks
api.add_resource(IntegrateDiscord, '/v1/user/integrate/discord')
api.add_resource(IntegrateTachi, '/v1/user/integrate/tachi')

# Game Data
api.add_resource(allPlayers, '/v1/game/<game>/profiles')
api.add_resource(Profile, '/v1/profile/<game>')
api.add_resource(Achievements, '/v1/profile/<game>/achievements')

# Music DB Data
api.add_resource(Music, '/v1/music')

# Scores
api.add_resource(Attempts, '/v1/attempts/<game>')
api.add_resource(Records, '/v1/records')

# Game Upload API
api.add_resource(shareServerStatus, '/share/server/status')
api.add_resource(shareNewSession, '/share/sessions/new')
api.add_resource(shareBeginUpload, '/share/sessions/<session_id>/videos/<video_id>/begin-upload')
api.add_resource(shareVideoUpload, '/share/videoUpload/<session_id>/<video_id>')
api.add_resource(shareEndUpload, '/share/sessions/<session_id>/videos/<video_id>/end-upload')
api.add_resource(shareLPACUpload, '/share/lpac/<session_id>')

# pop'n Rhythmin API
app.route('/apr/main/cgi/new/index.jsp')
def new():
    return {'status': 200}

api.add_resource(APRFileList, f'/apr/main/cgi/get_dl_file_list/index.jsp')
api.add_resource(APREventInfo, f'/apr/main/cgi/get_event_info/index.jsp')
api.add_resource(APRNewSession, f'/apr/main/cgi/new/index.jsp')
api.add_resource(APRSaveSession, f'/apr/main/cgi/save_apns_token/index.jsp')
api.add_resource(APRPlayer, f'/apr/main/cgi/get_player/index.jsp')
api.add_resource(APRNewPlayer, f'/apr/main/cgi/new_player/index.jsp')
api.add_resource(APRLinkAccount, f'/apr/main/cgi/link_kid/index.jsp')
api.add_resource(APRInvited, f'/apr/main/cgi/invited/index.jsp')
api.add_resource(APRPresentList, f'/apr/main/cgi/get_present_list/index.jsp')
api.add_resource(APRRecommendList, f'/apr/main/cgi/get_recommend_list/index.jsp')
api.add_resource(APRPackList, f'/apr/main/cgi/packlist/index.jsp')
api.add_resource(APRSearchMaster, f'/apr/main/cgi/search_master/index.jsp')

def load_config(filename: str) -> None:
    global config

    with open(filename, 'r') as file:
        config.update(yaml.safe_load(file))

    # Update the MySQLBase engine with the new connection string
    db_config = config.get('database', {})
    if db_config:
        MySQLBase.update_connection(db_config)

    pf_config = config.get('pfsense', {})
    if pf_config:
        PFSense.update_config(pf_config)

    mail_config = config.get('email', {})
    if mail_config:
        MailjetSMTP.update_config(mail_config)

    b2_config = config.get('backblaze', {})
    if b2_config:
        BackBlazeCDN.update_config(b2_config)

    share_config = config.get('share', {})
    if share_config:
        ShareServer.update_config(share_config)

    discord_config = config.get('discord', {})
    tachi_config = config.get('tachi', {})
    if share_config:
        Integrations.update_config(discord_config, tachi_config)

    badmaniac_config = config.get('bad-maniac', {})
    if badmaniac_config:
        BadManiac.update_config(badmaniac_config)

def main() -> None:
    parser = argparse.ArgumentParser(description="PhaseII's powerful API, RestfulSleep. Built with Flask and restful.")
    parser.add_argument("-p", "--port", help="Port to listen on. Defaults to 8000", type=int, default=8000)
    parser.add_argument("-c", "--config", help="Path to configuration file. Defaults to 'config.yaml'", type=str, default='config.yaml')
    args = parser.parse_args()

    # Load configuration
    load_config(args.config)

    # Run the app
    app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    main()