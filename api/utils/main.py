from flask import Flask
from flask_restful import Api, Resource
from typing import Any, Dict
import argparse

#import the services
from api.services.news import getAllNews, getLatestNews
from api.services.user import logUserIn, deleteUserSession, getGameProfile

# Video sharing stuff
from api.services.share import shareServerStatus, shareNewSession, shareBeginUpload, shareVideoUpload, shareEndUpload

app = Flask(__name__)
api = Api(app)
config: Dict[str, Any] = {}

class restfulTop(Resource):
    def get(self):
        return "RestfulSleep is alive! PhaseII's powerful API used for bots, apps, and more."

#add services
api.add_resource(restfulTop, '/')
api.add_resource(getAllNews, '/v1/news/getAllNews')
api.add_resource(getLatestNews, '/v1/news/getLatestNews')
api.add_resource(logUserIn, '/v1/auth/user/createSession')
api.add_resource(deleteUserSession, '/v1/auth/user/deleteSession')
api.add_resource(getGameProfile, '/v1/user/getProfile')

# Add video sharing stuff
api.add_resource(shareServerStatus, '/share/server/status')
api.add_resource(shareNewSession, '/share/sessions/new')
api.add_resource(shareBeginUpload, '/share/sessions/<sessionId>/videos/<videoId>/begin-upload')
api.add_resource(shareVideoUpload, '/share/videoUpload/<sessionId>')
api.add_resource(shareEndUpload, '/share/sessions/<sessionId>/videos/<videoId>/end-upload')

def main() -> None:
    parser = argparse.ArgumentParser(description="PhaseII's powerful API, RestfulSleep. Built with Flask and restful.")
    parser.add_argument("-p", "--port", help="Port to listen on. Defaults to 8000", type=int, default=8000)
    args = parser.parse_args()

    # Run the app
    app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    main()