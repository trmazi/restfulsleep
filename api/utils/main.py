from flask import Flask
from flask_cors import CORS # type: ignore
from flask_restful import Api, Resource
from typing import Any, Dict
import argparse
import yaml

# DB Stuff
from api.data.mysql import MySQLBase

# Services
from api.services.news import getAllNews, getNews
from api.services.auth import createUserSession, checkUserSession, deleteUserSession
from api.services.user import getUserAccount, getGameProfile
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

# News
api.add_resource(getAllNews, '/v1/news/getAllNews')
api.add_resource(getNews, '/v1/news/getNews/<newsId>')

# Sessions
api.add_resource(createUserSession, '/v1/auth/createSession')
api.add_resource(checkUserSession, '/v1/auth/checkSession')
api.add_resource(deleteUserSession, '/v1/auth/deleteSession')

# User Data
api.add_resource(getUserAccount, '/v1/user/<userId>')

# Game Profiles
api.add_resource(getGameProfile, '/v1/user/getProfile')

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