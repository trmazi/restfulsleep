from flask import Flask
from flask_restful import Api, Resource
from typing import Any, Dict
import argparse

#import the services
from api.services.news import getAllNews, getLatestNews
from api.services.user import userIDFromUsername
from api.services.user import validateUserPassword

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
api.add_resource(userIDFromUsername, '/v1/auth/user/fromName')
api.add_resource(validateUserPassword, '/v1/auth/user/validatePassword')

def main() -> None:
    parser = argparse.ArgumentParser(description="PhaseII's powerful API, RestfulSleep. Built with Flask and restful.")
    parser.add_argument("-p", "--port", help="Port to listen on. Defaults to 8000", type=int, default=8000)
    args = parser.parse_args()

    # Run the app
    app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    main()