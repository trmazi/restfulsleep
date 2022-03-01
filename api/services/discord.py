from flask_restful import Resource, reqparse
from flask import redirect
from api.data.mysql import MySQLBase
import requests

class linkDiscordToUser(Resource):
    '''
    Allows a discord account to be linked to a User Profile.
    '''
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int)
        parser.add_argument('code', type=str)

        args = parser.parse_args()
        user_id = args['user_id']
        code = args['code']

        if user_id == None or user_id == 0:
            return 205
        elif code == None or code == "":
            return 205

        oauthresult = requests.post(
            'https://discord.com/api/oauth2/token',
            data={
                'client_id': 947985989421395988,
                'client_secret': "0-cVg17SZRpFdX1lKvMWQRqI2us_ofuW",
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'https://restfulsleep.phaseii.network/discordauth?user_id=1',
                'scope': 'identify',
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        )
        jsonstat = oauthresult.json()

        if 'error' in jsonstat:
            print(jsonstat['error'] + ", " + jsonstat['error_description'])
            return jsonstat
        else:
            token = jsonstat['access_token']
            token_type = jsonstat['token_type']

            user_auth = requests.get(
                'https://discord.com/api/users/@me',
                headers={
                    'authorization': f'{token_type} {token}'
                }
            )

            user_json = user_auth.json()

            expires_in = jsonstat['expires_in']
            refresh_token = jsonstat['refresh_token']

            discord_info = {
                'id': user_json['id'],
                'username': user_json['username'] + "#" + user_json['discriminator'],
                'avatar': user_json['avatar'],
                'expires_in': expires_in,
                'refresh_token': refresh_token,
            }

            MySQLBase.putUserDiscordData(user_id, discord_info)

        return redirect("https://phaseii.network", code=302)