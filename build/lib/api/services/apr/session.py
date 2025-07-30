from flask_restful import Resource
from api.data.apr import APRConstants, RequestData

class APRNewSession(Resource):
    def post(self):
        request = RequestData.get_request_data()
        print(request)

        return APRConstants.bad_end(1)
    
class APRSaveSession(Resource):
    def post(self):
        request = RequestData.get_request_data()
        print(request)

        return APRConstants.bad_end(1)