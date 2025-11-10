from flask_restful import Resource
from api.data.apr import RequestData
from api.services.apr.lists import DataLists

class APREventInfo(Resource):
    def post(self):
        return {
            "Treasure": [
                {"EventId": 1},
            ],
            "GamePlay": [
                # {"EventId": 1},
            ],
        }

class APRFileList(Resource):
    '''
    This is used to download the stock music, so that the game has something to download.
    '''
    def post(self):
        request = RequestData.get_request_data()
        if request['client_ver'] != '200':
            return {'ErrorCode': '4'}
        
        fileList = []

        for index, file in enumerate(DataLists.bootList + DataLists.stockList):
            fileList.append(
                {
                    "Id": index,
                    "Url": file.get("Url", ""),
                    "Size": file.get("Size", 0)
                }
            )

        return {'List': fileList} # + DataLists.stockList}