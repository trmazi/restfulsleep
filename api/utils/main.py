from flask import Flask
from flask.helpers import get_root_path
from flask_restful import Api
from typing import Any, Dict
import argparse

#import the services
from api.services.login import guidesLoginStatus
from api.services.user import userFromPIN
from api.services.news import getAllNews

app = Flask(__name__)
api = Api(app)
config: Dict[str, Any] = {}

#add services
api.add_resource(guidesLoginStatus, '/guidelogin')
api.add_resource(userFromPIN, '/userfrompin')
api.add_resource(getAllNews, '/getallnews')

def main() -> None:
    parser = argparse.ArgumentParser(description="PhaseII's powerful API, RestfulSleep. Built with Flask and restful.")
    parser.add_argument("-p", "--port", help="Port to listen on. Defaults to 8000", type=int, default=8000)
    args = parser.parse_args()

    # Run the app
    app.run(host='0.0.0.0', port=args.port, debug=True)

if __name__ == '__main__':
    main()