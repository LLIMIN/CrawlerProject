import requests
from fake_useragent import UserAgent

headers = {
    'User-Agent': UserAgent().random,
    'cookie': 'cookie: dy_did=0f49745f19a6d4192c7a142400001501; acf_did=0f49745f19a6d4192c7a142400001501; acf_uid=20343485; acf_username=qq_lSiOqpVu; acf_nickname=llll%E7%B1%B3%E5%B0%8F%E7%B1%B3llll; acf_ltkid=36998839; acf_auth=2204UaB%2Fr7eKFevpto1ZYsV3IKMchW%2B8augVOfNMvooZEjvfL0Zpp%2FaU4a1H5ogWToreNeJffppHLdAPRXbf14SUmff18IxUeKTHe%2FOrwkmHx3okUWsOw5w5; wan_auth37wan=de55da068e521FR1kap0Uu5FMxqo0FKE7hY0BPaXW9Rik65xnmhPZ7jNBaXm9sc2xrXvF91PA9EcOCdzVPyLYFUL%2B1wEq1k%2FWQyRSi7gBznwDzKRrw; acf_own_room=0; acf_groupid=1; acf_phonestatus=1; acf_ct=0; acf_biz=1; acf_stk=7792cdbeec14156a; Hm_lvt_e99aee90ec1b2106afe7ec3b199020a7=1523339724,1523372744,1523510881,1523676745; PHPSESSID=g49rfg0faif88th8anmghjl117; smidV2=2018041423361430480cd7121e06aa79208b9180cdb3e000f8c0ecb47058770; _dys_lastPageCode=page_studio_normal,page_studio_normal; Hm_lpvt_e99aee90ec1b2106afe7ec3b199020a7=1523797563'
}


def douyu():
    url = 'https://www.douyu.com/688'
    html = requests.get(url, headers=headers)
    print(html.status_code)
    print(html.text)


def qqq():
    import json
    url = 'https://dotcounter.douyucdn.cn/deliver/fish2'
    payload = {
        'multi': [{"d": "0f49745f19a6d4192c7a142400001501", "i": "20343485", "rid": 19223, "u": "/3q3q",
                   "ru": "/directory/game/jdqs", "ac": "click_msg_send", "rpc": "page_studio_normal",
                   "pc": "page_studio_normal", "pt": 1523798779307, "oct": 1523798967450, "dur": 0, "pro": "host_site",
                   "ct": "web", "e": {"type": 2, "rac": "show_recom_video"}, "av": "", "up": ""}],
        'v': 1.5
    }
    response = requests.post(url, data=json.dumps(payload))
    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    # douyu()
    qqq()
