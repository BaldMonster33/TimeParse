#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

import re


# Reconstuct to enable comparable time, and absolute time.
# IN the type, False means absolute time, True means relatively time.
class TimeRecognition(object):
    def __init__(self):
        self.__rules = self.__load_rules()

    @staticmethod
    def __load_rules():
        return {re.compile('(?P<num>几|\\d+)个?(?P<type>天|日|周|星期|月份?|季度?|半?年)前'): -1,
                re.compile('上一?个?(?P<type>天|日|月份?|季度?|半?年)(?<!末)'): -1,
                re.compile('(?:[之往以]?前|过去)(?P<num>几|些|\d+)个?(?P<type>天|日|周|星期|月份?|季度?|半?年)'): -1,
                re.compile('(?P<single>昨天|去年)(?!末)'): -1,
                re.compile('(?<! [下今本这当])大?上一?个?(?P<type>上?周|星期)(?P<weekday_num>\d|[一二三四五六七日天])?'): -1,

                re.compile('(?:最近|这)(?P<num>几|些|\d+)个?(?P<type>天|日|周|星期|月份?|季度?|半?年)子?'): 0,
                re.compile('[今本这当]一?个?(?P<type>天|日|月份?|季度?|半?年)(?![年月周季末])'): 0,
                re.compile('(?P<single>现在|近期|近日|这段(时间)?(?!几)(([这一])段)?|一会|这会|这时)'): 0,
                re.compile('(?<![上下个几后前])[今本这当]?一?个?(?P<type>周|星期)(?P<weekday_num>\d|[一二三四五六七日天])?'): 0,
                #      re.compile('(?<!上|下|个)(?P<type>周|星期)(?P<weekday_num>\d|[一二三四五六七日天末])'): 0,

                re.compile('(?P<num>几|\d+)个?(?P<type>天|日|周|星期|月份?|季度?|半?年)后'): 1,
                re.compile('下一?个?(?P<type>天|日|月份?|季度?|半?年)'): 1,
                re.compile('(?<![上今本这当])大?下一?个?(?P<type>下?周|星期)(?P<weekday_num>\d|[一二三四五六七日天])?'): 1,

                re.compile('(?:再过|未来|[往之以过]+后)(?P<num>几|些|\d+)个?(?P<type>天|日|周|星期|月份?|季度?|半?年)'): 1,
                re.compile('(?P<single>明天|明年|后天|来年)(?!末)'): 1,
                # Sole year, month, and day, and the mix of year and month, month and day. Total 5 conditions.
                re.compile('(?P<yr_num>\d{4}|\d{2})(?P<e_type>年)(?!末)'): 'E',
                re.compile('(?P<the>第)?(?P<quarter_num>\d)(?P<e_type>季度?)(?!末)'): 'E',
                re.compile('(?P<mon_num>\d{1,2})(?P<e_type>月份?)(?!末)'): 'E',
                re.compile('(?P<day_num>\d{1,2})(?P<e_type>[日天号])(?!末)'): 'E',
                #                 re.compile('(?<星期>周|星期)(?P<w_num>\d{1})(?P<e_type>季度?)'):'E
                # 月末 年末
                re.compile('((?P<ending_num>[上下明后来去今本这当]?一?个?|\d{1,4})(?P<end>[周月年季])(?:[周月年季])?末)'): 'M'

                }

    # Add support for 月末，周末，季末，年末
    #     本周末 本月末 本年末 本季末
    def __match_time(self, question):
        match_res = {}
        dict_list = []
        idx = 0
        flag_num = None
        a_rule = None
        for rule, flag in self.__rules.items():
            is_match = re.search(rule, question)
            if is_match is not None:
                idx += 1
                dict_list.append(is_match)
                match_res.update(is_match.groupdict())
                a_rule = rule
                flag_num = flag
                if type(flag) == int:
                    flag_num = flag
        if idx == 0:
            return None
        elif idx == 1:
            match_res = dict_list[0].groupdict()
            match_res['time'] = dict_list[0].group()
            match_res['flag'] = flag_num
            match_res['sub'] = re.sub(a_rule, "㠭", question)
            match_res['sub_word'] = dict_list[0].group()
            return match_res
        elif idx > 1:
            substr = ''
            timestr = ''
            for the_dict in dict_list:
                match_res.update(the_dict.groupdict())
                for num in list(the_dict.group()):
                    substr = substr + num
                    if 'e_type' not in the_dict.groupdict().keys():
                        timestr = timestr + num
            match_res['time'] = timestr
            match_res['flag'] = flag_num
            match_res['sub'] = re.sub(substr, "㠭", question)
            match_res['sub_word'] = substr
            return match_res

    @staticmethod
    def __se_time(match_res):
        if 'num' not in match_res.keys():
            match_res['num'] = 1
        else:
            if match_res['num'] in ['这', '几', '些', '这段', '段']:
                match_res['num'] = 3
        num = int(match_res['num'])
        flag = match_res['flag']
        if flag == -1:
            start = num * -1 - 1
            end = num * -1
        elif flag == 1:
            start = num * 1
            end = num * 1 + 1
        else:
            end = int(num * 1 / 2) + 1
            start = int(num * -1 / 2)
        return [start, end]

    @staticmethod
    def __parse_single_words(match_res):
        parse_res = {}
        single = match_res['single']
        #         if 'e_type' not in match_res.keys():
        # 这段|最近|一会|这会|这时
        if single == '昨天':
            parse_res = {'d_s': -2, 'd_e': -1, 'd_type': True}
        elif single == '去年':
            parse_res = {'y_s': -2, 'y_e': -1, 'y_type': True}
        elif single in ['近期', '近日', '这些天', '一会', '这会']:
            parse_res = {'d_s': -1, 'd_e': 2, 'd_type': True}
        elif single in ['最近这段', '这段时间', '这段', '最近一段']:
            parse_res = {'d_s': -3, 'd_e': 3, 'd_type': True}
        elif single in ['明天', '这会', '一会', '这时']:
            parse_res = {'d_s': 1, 'd_e': 2, 'd_type': True}
        elif single == '后天':
            parse_res = {'d_s': 2, 'd_e': 3, 'd_type': True}
        elif single == '明年':
            parse_res = {'y_s': 1, 'y_e': 2, 'y_type': True}
        elif single == '来年':
            parse_res = {'y_s': 1, 'y_e': 2, 'y_type': True}
        return parse_res

    @staticmethod
    def __parse_ending_word(match_res):
        parse_res = {}
        ending = match_res['end']
        ending_num = match_res['ending_num']
        if match_res['ending_num'] == '':
            ending_num = 0
        if ending_num in ['今', '本', '这', '当']:
            ending_num = 0
        elif ending_num in ['明', '来', '下', '下个']:
            ending_num = 1
        elif ending_num in ['去', '上', '上个']:
            ending_num = -1
        elif ending_num in ['后']:
            ending_num = -1
        if ending == '月':
            if int(ending_num) > 12:
                return None
            elif 12 > int(ending_num) >= 0:
                parse_res = {'m_s': int(ending_num), 'm_e': int(ending_num) + 1, 'm_type': True, 'd_s': 21, 'd_e': 32,
                             'd_type': True}
            elif int(ending_num) < 0:
                parse_res = {'m_s': int(ending_num) - 1, 'm_e': int(ending_num), 'm_type': True, 'd_s': 21, 'd_e': 32,
                             'd_type': True}
        elif ending == '年':
            if 99 > int(ending_num) > 50:
                ending = str(19) + str(ending_num)
            elif 50 > int(ending_num) > 0:
                ending = str(20) + str(ending_num)
            parse_res = {'y_s': int(ending), 'y_e': int(ending) + 1, 'y_type': True, 'm_s': 12, 'd_e': 13,
                         'd_type': True}
        return parse_res

    @staticmethod
    def __char_to_int(match_res):
        char = match_res['weekday_num']
        if char in ['一', 1, '1']:
            char = [1, 2]
        elif char in ['二', 2, '2']:
            char = [2, 3]
        elif char in ['三', 3, '3']:
            char = [3, 4]
        elif char in ['四', 4, '4']:
            char = [4, 5]
        elif char in ['五', 5, '5']:
            char = [5, 6]
        elif char in ['六', 6, '6']:
            char = [6, 7]
        elif char in ['七', '日', '天', 7, '7']:
            char = [7, 8]
        elif char in ['末']:
            char = [6, 8]
        else:
            return 'DemandsDemandsAlldaMnDemands'
        return char

    def __parse_time(self, match_res):
        if match_res is None:
            return None
        parse_res = {'sub': match_res['sub'], 'sub_word': match_res['sub_word']}
        if 'single' in match_res.keys():
            parse_res = self.__parse_single_words(match_res)
        else:
            if 'type' not in match_res.keys():
                return None
            time = self.__se_time(match_res)
            if match_res['type'] in ['日', '天']:
                parse_res['d_type'] = True
                parse_res['d_s'] = time[0]
                parse_res['d_e'] = time[1]
            elif match_res['type'] in ['星期', '这段', '一段', '周', '上周', '下周']:
                parse_res['w_type'] = True
                parse_res['w_s'] = time[0]
                parse_res['w_e'] = time[1]
            elif match_res['type'] in ['月份', '月']:
                parse_res['m_type'] = True
                parse_res['m_s'] = time[0]
                parse_res['m_e'] = time[1]
            elif match_res['type'] in ['季度', '季']:
                parse_res['q_type'] = True
                parse_res['q_s'] = time[0]
                parse_res['q_e'] = time[1]
            elif match_res['type'] in ['年', '半年']:
                parse_res['y_type'] = True
                parse_res['y_s'] = time[0]
                parse_res['y_e'] = time[1]
        if 'weekday_num' in match_res.keys():
            if match_res['weekday_num'] is not None:
                parse_res['wd_type'] = True
                weekday_num = self.__char_to_int(match_res)
                print(weekday_num)
                parse_res['wd_s'] = weekday_num[0]
                parse_res['wd_e'] = weekday_num[1]
        return parse_res

    def __parse_exact_time(self, match_res):
        if match_res is None:
            return None
        parse_res = {'sub': match_res['sub'], 'sub_word': match_res['sub_word']}
        try:
            parse_res.update(self.__parse_time(match_res))
        except:
            pass
        keys = match_res.keys()

        if 'yr_num' in keys:
            yer = match_res['yr_num']
            if len(yer) == 2:
                match_res['yr_num'] = int('20' + yer)
            mark = False  # This means exact time. Eg:2021-08-09
            parse_res['y_type'] = mark
            parse_res['y_s'] = match_res['yr_num']
            parse_res['y_e'] = int(parse_res['y_s']) + 1

            if 'mon_num' in keys:
                if int(match_res['mon_num']) > 12 or int(match_res['mon_num']) < 1:
                    return None
                parse_res['m_s'] = parse_res['m_e'] = match_res['mon_num']
                parse_res['m_type'] = False
                if 'day_num' in keys:
                    parse_res['d_s'] = match_res['day_num']
                    parse_res['d_e'] = int(parse_res['d_s']) + 1

                else:
                    parse_res['m_s'] = match_res['mon_num']
                    parse_res['m_e'] = int(parse_res['m_s']) + 1
            if 'quarter_num' in keys:
                if int(match_res['quarter_num']) > 4 or int(match_res['quarter_num']) < 1:
                    return None
                parse_res['q_s'] = match_res['quarter_num']
                parse_res['q_e'] = int(parse_res['q_s']) + 1
            # In case we need to support questions like '2018年第四季度3月' -- line 282
            # In case input is like 20-09-44.
            else:
                parse_res['y_e'] = int(parse_res['y_s']) + 1
        elif 'mon_num' in keys:
            mark = False
            parse_res['m_type'] = mark
            parse_res['m_s'] = match_res['mon_num']
            parse_res['m_e'] = int(parse_res['m_s']) + 1
            if 'day_num' in keys:  # 明年8月9日
                parse_res['d_s'] = match_res['day_num']
                parse_res['d_e'] = int(parse_res['d_s']) + 1
                parse_res['d_type'] = mark
        elif 'day_num' in keys:
            parse_res['d_s'] = match_res['day_num']
            parse_res['d_e'] = int(parse_res['d_s']) + 1
            parse_res['d_type'] = False
        # No month input, return Whole Year data, from 1.1 to 12.31
        elif 'ending_num' in keys:
            parse_res.update(self.__parse_ending_word(match_res))

        if 'single' in keys or 'type' in keys:
            if 'mon_num' in keys:
                # This means mixed time. Eg: 明年8月
                parse_res['m_type'] = False
                parse_res['m_s'] = match_res['mon_num']
                if 'day_num' in keys:  # 明年8月9日
                    parse_res['d_s'] = match_res['day_num']
                    parse_res['d_e'] = int(parse_res['d_s']) + 1
                else:
                    parse_res['m_e'] = int(parse_res['m_s']) + 1

            # Add support like '明年第四季度'
            elif 'quarter_num' in keys:
                parse_res['q_type'] = False
                parse_res['q_s'] = match_res['quarter_num']
                parse_res['q_e'] = int(parse_res['q_s']) + 1

            # In case situations in 243line.

            else:  # 下个月8日，下个月
                # TODO MATCH 下个月，过两天，return
                if 'e_type' not in keys:
                    raw_parse_res = self.__parse_time(match_res)
                    parse_res.update(raw_parse_res)

                if 'day_num' in keys:  # 明年8月9日
                    parse_res['d_s'] = match_res['day_num']
                    parse_res['d_e'] = int(parse_res['d_s']) + 1
                    parse_res['d_type'] = False

        return parse_res

    def recognize_time(self, question):
        match_res = self.__match_time(question)
        print(match_res)
        parse_res = self.__parse_exact_time(match_res)
        print(parse_res)
        return None if parse_res is None else parse_res



if __name__ == '__main__':
    tr = TimeRecognition()
    res = tr.recognize_time('我想看5月下周的展览')
    print(res)