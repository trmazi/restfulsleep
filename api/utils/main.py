from flask import Flask
from flask_cors import CORS # type: ignore
from flask_restful import Api, Resource
from typing import Any, Dict
import argparse
import yaml

# DB Stuff
from api.data.mysql import MySQLBase

# PFSense Stuff
from api.data.endpoints.pfsense import PFSenseData

# Services
from api.services.discord import OnboardingVPN, OnboardingArcade
from api.services.admin import AdminDashboard, OnboardArcade
from api.services.arcade import Arcades, Paseli, VPN, CheckArcadeName, CheckPCBID
from api.services.news import getAllNews, getNews
from api.services.auth import createUserSession, checkUserSession, deleteUserSession, emailAuth, check2FAKey, changePassword
from api.services.user import getUserAccount, userCards
from api.services.profiles import allPlayers, Profile
from api.services.music import Music
from api.services.score import Attempts, Records
from api.services.share import shareServerStatus, shareNewSession, shareBeginUpload, shareVideoUpload, shareEndUpload

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

# Arcades
api.add_resource(Arcades, '/v1/arcade/<arcadeId>')
api.add_resource(Paseli, '/v1/arcade/<arcadeId>/paseli')
api.add_resource(VPN, '/v1/arcade/<arcadeId>/exportVPN')
api.add_resource(CheckArcadeName, '/v1/arcade/checkName')
api.add_resource(CheckPCBID, '/v1/arcade/checkPCBID')

# BadManiac Calls
api.add_resource(OnboardingVPN, '/v1/discord/exportVPN/<arcadeId>')
api.add_resource(OnboardingArcade, '/v1/discord/onboardArcade/<arcadeId>')

# News
api.add_resource(getAllNews, '/v1/news/getAllNews')
api.add_resource(getNews, '/v1/news/getNews/<newsId>')

# Sessions
api.add_resource(createUserSession, '/v1/auth/createSession')
api.add_resource(checkUserSession, '/v1/auth/checkSession')
api.add_resource(deleteUserSession, '/v1/auth/deleteSession')

# Email Auth
api.add_resource(emailAuth, '/v1/auth/emailAuth')
api.add_resource(check2FAKey, '/v1/auth/check2FAKey')
api.add_resource(changePassword, '/v1/auth/changePassword')

# User Data
api.add_resource(getUserAccount, '/v1/user/<userId>')
api.add_resource(userCards, '/v1/user/cards')

# Game Data
api.add_resource(allPlayers, '/v1/game/<game>/profiles')
api.add_resource(Profile, '/v1/profile/<game>')

# Music DB Data
api.add_resource(Music, '/v1/music')

# Scores
api.add_resource(Attempts, '/v1/attempts/<game>')
api.add_resource(Records, '/v1/records')

# Video sharing API
api.add_resource(shareServerStatus, '/share/server/status')
api.add_resource(shareNewSession, '/share/sessions/new')
api.add_resource(shareBeginUpload, '/share/sessions/<sessionId>/videos/<videoId>/begin-upload')
api.add_resource(shareVideoUpload, '/share/videoUpload/<sessionId>')
api.add_resource(shareEndUpload, '/share/sessions/<sessionId>/videos/<videoId>/end-upload')

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
        PFSenseData.update_config(pf_config)

    mail_config = config.get('email', {})
    if mail_config:
        emailAuth.update_config(mail_config)

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