import sys
sys.path.append("lib.bs4")
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import urllib.request
import re


CODE_LIST = {
    "01" : "札幌",
    "02" : "函館",
    "03" : "福島",
    "04" : "新潟",
    "05" : "東京",
    "06" : "中山",
    "07" : "中京",
    "08" : "京都",
    "09" : "阪神",
    "10" : "小倉"
}

def parse_id(race_id):
    year = race_id[:4]
    course_code = race_id[4:6]
    held_count = race_id[6:8]
    day = race_id[8:10]
    race_num = race_id[10:12]
    
    print(f"{year}年 {held_count}回 {CODE_LIST[course_code]} {day}日目 第{race_num}レース")

def get_race(race_id):
    parse_id(race_id)
    url = "https://db.netkeiba.com/race/" + race_id
    print(url)
    get_race_name(url)
    race_info = pd.read_html(url)[0]
    odds_1 = pd.read_html(url)[1]
    odds_2 = pd.read_html(url)[2]
    
    
    ## 1着〜3着までの馬番の人気を取得
    NUM_RANK_DICT = {}
    RANK_1_TO_3_LIST = []
    for row in race_info.itertuples():
        try:
            if row[11] != "NaN":
                NUM_RANK_DICT[int(row[3])] = int(row[11])
                if len(RANK_1_TO_3_LIST) < 3:
                    RANK_1_TO_3_LIST.append(row[11])
        except:
            pass
    
    result_safe = True
    for rk in RANK_1_TO_3_LIST:
        if rk > 4:
            result_safe = False
            break
    
    odds = pd.concat([odds_1,odds_2])
    
    # print(race_info)
    # print(odds)
    
    # 3連単の馬順のみを取得
    three_part_unit = str(odds.iat[6,1])
    three_part_unit_odds = int(odds.iat[6,2])
    three_part_unit = three_part_unit.split("→")
    print(f"[[ {result_safe} ]] {RANK_1_TO_3_LIST}  >>> ODDS : {three_part_unit_odds}円")
    return result_safe,three_part_unit_odds
    # race_info.to_csv('/Users/sirius1000/keiba/scraping/csv/sample_pandas_normal2.csv')
    # odds.to_csv('/Users/sirius1000/keiba/scraping/csv/sample_pandas_normal.csv')

def get_race_name(race_url):
    try:
        html = urllib.request.urlopen(race_url).read()
        root = BeautifulSoup(html, 'lxml')
        race_dict = {}
        race_dict['race_title'] = root.find('dl', class_='racedata fc').dd.h1.contents[0]
        print(race_dict)
        return race_dict['race_title']
    except:
        return "ERROR"
    
    
def gen_race_id():
    race_id_list = []
    for place in range(1, 11, 1):
        for kai in range(1, 6, 1):
            for day in range(1, 9, 1):
                for r in range(1, 13, 1):
                    race_id = (
                        "2022"
                        + str(place).zfill(2)
                        + str(kai).zfill(2)
                        + str(day).zfill(2)
                        + str(r).zfill(2)
                    )
                    race_id_list.append(race_id)
    return race_id_list

def main():
    PAY_NUM = 3600
    
    race_id_list = gen_race_id()
    count = 0
    get_odds = 0
    pay = 0
    for index, ril in enumerate(race_id_list):
        try:
            print("========")
            count += 1
            result_safe,three_part_unit_odds = get_race(ril)
            if result_safe:
                get_odds += three_part_unit_odds
            print(f"""
            count : {count}回 , 獲得金額 : {get_odds}円 , 収支 : {get_odds - count*PAY_NUM} 割合 : {get_odds / (get_odds - count*PAY_NUM) * 100}
            """)
        except KeyboardInterrupt:
            print("bye")
        except:
            pass
    
    ALL_PAYED = PAY_NUM * count
    print(f"""
        count : {count}回 , 獲得金額 : {get_odds}円 , 収支 : {get_odds - ALL_PAYED}
        """)
    
if __name__ == "__main__":
    main()