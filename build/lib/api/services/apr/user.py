from flask_restful import Resource
from api.data.apr import APRConstants, RequestData

@staticmethod
def format_player(uuid, name) -> dict:
    profile = {
        'PlayerId': '1234567',
        'PlayerName': name,
        'InviteCnt': 1,
        'ArcadePt': 100,
        'FriendRequested': 0,
        'UpdateDate': '9/1/2022',
        'LoginBonusId': 0,
        'LoginCount': 69,
        'Login': 1,
    }
    return profile

class APRPlayer(Resource):
    def post(self):
        request = RequestData.get_request_data()
        print(request)
        if request != None:
            uuid = request['uuid']

            if uuid == None:
                return APRConstants.bad_end(1)

            return format_player(uuid, 'deez')

        else: return APRConstants.bad_end(1)

class APRNewPlayer(Resource):
    def post(self):
        request = RequestData.get_request_data()
        if request != None:
            uuid = request['uuid']
            name = request['name']

            if uuid == None:
                return APRConstants.bad_end(1)
            if name == None:
                return APRConstants.bad_end(1)

            return format_player(uuid, name)

        else: return APRConstants.bad_end(1)

class APRLinkAccount(Resource):
    def post(self):
        request = RequestData.get_request_data()
        if request != None:
            uuid = request['uuid']
            konami_id = request['konami_id']
            password = request['password']

            if konami_id == None:
                return APRConstants.bad_end(1)
            if uuid == None:
                return APRConstants.bad_end(1)
            if password == None:
                return APRConstants.bad_end(1)

            return APRConstants.bad_end(2)

        else: return APRConstants.bad_end(1)

class APRInvited(Resource):
    def post(self):
        request = RequestData.get_request_data()
        if request != None:
            uuid = request['uuid']
            player_id = request['player_id']

            if uuid == None:
                return APRConstants.bad_end(4)
            if player_id == None:
                return APRConstants.bad_end(4)

            return {
                'ErrorCode': 2,
            }

        else: return APRConstants.bad_end(4)

class APRPresentList(Resource):
    def post(self):
        request = RequestData.get_request_data()
        if request != None:
            uuid = request['uuid']

            if uuid == None:
                return APRConstants.bad_end(4)

            presents = []
            presents.append({
                'PresentId': 1,
                'ItemId': 1,
                'ItemNum': 1,
                'Info': 'A gift for you!'
            })

            return {'PresentList': presents}

        else: return APRConstants.bad_end(4)