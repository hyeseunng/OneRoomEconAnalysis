import requests
import pandas as pd
import geohash2


def get_oneroom_info(addr):  # 동이름 넣으면 정보 반환하도록 ex. 광진구 화양동
    # 동이름으로 원룸의 위도와 경도을 받기(1번째 request)
    url = f"https://apis.zigbang.com/v2/search?leaseYn=N&q={addr}&serviceType=원룸"
    response = requests.get(url)
    data = response.json()["items"][0]
    lat, lng = data["lat"], data["lng"]
    geohash = geohash2.encode(lat, lng, precision=5)

    # 범위 값으로 원룸 매물 아이디 값을 수집한다(2번째 request)
    url = f"https://apis.zigbang.com/v2/items?deposit_gteq=0&domain=zigbang\
&geohash={geohash}&needHasNoFiltered=true&rent_gteq=0&sales_type_in=월세&service_type_eq=원룸"
    response = requests.get(url)
    items = response.json()["items"]
    ids = [item["item_id"] for item in items]

    # 아이디 값으로 원룸 매물 정보를 추출한다(3번째 request)
    url = "https://apis.zigbang.com/v2/items/list"
    params = {"domain": "zigbang", "item_ids": ids[:900]}
    response = requests.post(url, params)
    items = response.json()["items"]
    # print(items)
    colums = [
        "item_id",
        "sales_type",
        "deposit",
        "rent",
        "address1",
        "manage_cost",
        "floor",
        "size_m2",
        "service_type",
    ]
    df = pd.DataFrame(items)[colums]
    print(df)
    df = df[df["address1"].str.contains(addr)].reset_index(drop=True)
    df = df.rename(
        columns={
            "address1": "주소",
            "sales_type": "유형",
            "deposit": "보증금",
            "rent": "월세",
            "manage_cost": "관리비",
            "floor": "층수",
            "size_m2": "평수",
            "service_type": "형태",
        }
    )

    print(df)
    return df
