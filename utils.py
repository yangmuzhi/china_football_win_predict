COACH_SET = {'沈祥福':1,'福拉多':2,'殷铁生':3,'戚务生':4,'朱广沪':5,
            '李铁':6,'高洪波':7,'佩兰':8,'里皮':9,'傅博':10,'卡马乔':11,
            '阿里汉':12,'霍顿':13,'米卢蒂诺维奇':14}


class chinawin:

    def __init__(self):
        pass

    def process_data(self, data):
        
        data = _process_colname(data)
        data = _process_match_type(data)
        data = _process_parse_match(data)
        data = _process_bad_case(data)

        data = _process_is_china(data)
        data = _process_coach(data)
        country = list(set(list(data['home']) + list(data['away'])))
        self.COUNTRY_SET = {k:v for k,v in zip(country, range(len(country)))}
        self.data = _process_team(data, self.COUNTRY_SET)

    
    def get_feature(self):
        self.fea = self.data[['type', 'coach_fea', 'is_cn_home', 'vs_team']].values
        self.score = self.data[['score']].values
        return self.fea, self.score
        

def _process_bad_case(data):

    # 一些特殊的例子处理
    data['home'][data['home'] == '中国中国'] = '中国'
    data['home'][data['home'] == '乌兹别克'] = '乌兹别克斯坦'
    data['home'][data['home'] == '印度尼西亚'] = '印尼'
    data['home'][data['home'] == '沙特阿拉伯'] = '沙特'
    data['home'][data['home'] == '英格兰业余队'] = '英格兰'

    data['away'][data['away'] == '乌兹别克'] = '乌兹别克斯坦'
    data['away'][data['away'] == '乌拉圭选拔队'] = '乌拉圭'
    data['away'][data['away'] == '印度尼西亚'] = '印尼'
    data['away'][data['away'] == '民主德国'] = '德国'
    data['away'][data['away'] == '马来西亚国奥'] = '马来西亚'

    data['away'][data['away']=='点'] = '伊朗'
    data[data['time']=='2002.02.15']['away'] = '中国'
    data[data['time']=='2002.02.12']['away'] = '中国'
    data[data['time']=='2001.08.03']['away'] = '朝鲜'
    data[data['time']=='2001.01.17']['away'] = '中国'
    data[data['coach']=='武磊']['coach'] = '里皮'

    return data

def _process_colname(data):
    data.columns = ['time', 'loc', 'match', 'type', 'coach']
    return data

def _process_match_type(data):
    """处理比赛性质"""
    high_level = ['12强赛', '世界杯', '世界杯预选赛亚洲区', '世预赛', '世预赛12强赛', '东亚杯',
                  '亚洲杯预选赛', '奥运会', '奥运会预选赛亚洲区']
    high_ind = data.index[data['type'].map(lambda x: x in high_level)]
    low_ind = data.index[data['type'].map(lambda x: x not in high_level)]
    data['type'][high_ind] = 1
    data['type'][low_ind] = 0

    return data

def _process_parse_match(data):
    """解析比赛球队和比分"""
    tmp= data['match'].str.split('-', expand=True)
    # 主队 
    data['home'] = tmp[0].str.findall('[\u4e00-\u9fa5]+')
    data['home'] = data['home'].map(lambda x: x[0])
    data['home_score'] = tmp[0].str.findall('\d+')
    data['home_score'] = data['home_score'].map(lambda x: x[0])
    # 客队
    data['away'] = tmp[1].str.findall('[\u4e00-\u9fa5]+')
    data['away'] = data['away'].map(lambda x: x[0])
    data['away_score'] = tmp[1].str.findall('\d+')
    data['away_score'] = data['away_score'].map(lambda x: x[0])

    data['home_score'] = data['home_score'].astype(int)
    data['away_score'] = data['away_score'].astype(int)

    return data

def _process_is_china(data):
    """判断是不是国足主场以及国足是否赢球"""

    data['is_cn_home'] = data['home'].map(lambda x: int(x == '中国'))
    
    # 中国队是否赢球
    data['is_cn_win'] = 0
    a = (data['home_score'] > data['away_score']).astype(int) & data['is_cn_home'] 
    b = (data['home_score'] < data['away_score']).astype(int) & (data['is_cn_home']*(-1) + 1)
    data['is_cn_win'] = a + b

    # 中国队是否平局
    data['is_cn_eql'] = 0
    data['is_cn_eql'] = (data['home_score'] == data['away_score']).astype(int)
    data['score'] = list(map(lambda x: _label_trans(x), zip(data['is_cn_win'], data['is_cn_eql'])))

    return data

def _label_trans(x):
    """把胜负关系转换为得分"""
    if x[0] == 1:
        return 2
    elif x[1] == 1:
        return 1
    else:
        return 0

def _process_coach(data):
    data['coach_fea'] = data['coach'].map(lambda x: _coach_trans(x))
    return data

def _coach_trans(x):
    # 将主教练转换为离散特征，不在集合里为0
    label = COACH_SET.get(x)
    if label:
        return label
    else:
        return 0

def _process_team(data, COUNTRY_SET):

    data['vs_team'] = list(map(lambda x: _team_trans(x[0], x[1], COUNTRY_SET, data), enumerate(data['is_cn_home'])))
    return data

def _team_trans(i, x, COUNTRY_SET, data):
    if x:
        team = data.iloc[i]['away']
    else:
        team = data.iloc[i]['home']
    label = COUNTRY_SET.get(team)
    if label:
        return label
    else:
        return 0