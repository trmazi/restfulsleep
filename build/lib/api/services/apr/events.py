from flask_restful import Resource
from api.data.apr import RequestData
from api.services.apr.lists import DataLists

class APREventInfo(Resource):
    def post(self):
        return {'GamePlay': []}

class APRFileList(Resource):
    '''
    This is used to download the stock music, so that the game has something to download.
    '''
    def post(self):
        request = RequestData.get_request_data()
        if request['client_ver'] != '200':
            return {'ErrorCode': '4'}

        return {'List': DataLists.stockList}