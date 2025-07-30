from flask_restful import Resource
from api.data.apr import APRConstants, RequestData

class APRRecommendList(Resource):
    def post(self):
        request = RequestData.get_request_data()
        if request != None:
            uuid = request['uuid']

            if uuid == None:
                return APRConstants.bad_end('bad uuid!')

            return {
                'List': [],
                'Over': []
            }

        else: return APRConstants.bad_end('bad request!')

class APRPackList(Resource):
    def get(self):
        '''
        Stuff that is used but not here.
            'MusicList': [int(filename), 1, 2, 3],
            'AcvMusicList': [int(filename), 1, 2, 3],
            'Name': f'Rhythmin Pack #{index}',
            'Comment': 'Brought to you by PhaseII',
            'ShortComment': 'Brought to you by PhaseII',
            'IsNew': 1,
            'Copyright': '2022',
            'ArtworkURL': f'https://popapp.ez4dj.com/cdn/store/{filename}.acv',
            'ArtistURL': 'https://iidxfan.xyz',
            'ArtistBunnerURL': 'https://iidxfan.xyz',
            'AcvNum': index,
        '''

        filelist = []
        # if os.path.exists(StorePath.getStorePath()):
        #     index = 0
        #     for subdir, dirs, files in os.walk(StorePath.getStorePath()):
        #         for filename in files:
        #             if filename[-3:] != 'orb':
        #                 continue
        #             filename = filename.replace('.orb', '')
        #             filelist.append({
        #                 'ID': 1,
        #             })
        #             index += 1

        return {
            'Version': '2.0.0',
            'PackList': filelist,
            'Promotion': []
        }