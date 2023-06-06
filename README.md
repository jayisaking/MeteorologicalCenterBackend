# Meterorological Center Backend

## Requirements

- PostgreSQL
- Python >= 3.8
- chromedriver

## Installation

1. Python requirements
   ```shell
   pip install requirements.txt
   ```
2. Database
   In config.json : 以下是 PostgreSQL 的參數，要根據自己 build 的時候改
   ```shell
    "db_name": "test1", //是自己在PostgreSQL創建時 自己CREATE的DB
    "db_user": "jaysun", // 自己的名字
    "db_password": "", // 自己的密碼
    "db_host": "/tmp", // 自己的host
    "db_port": "5432", //自己的post
   ```
3. Server

   以下皆在 config.json

   ```

   "chromedriver_path": "./chromedriver", //自己的chromedriver的路徑

   // 還沒設定 不用管
   "endpoint_host": "127.0.0.1",
   "endpoint_port": 8000,
   "endpoint_allowed_origins": ["*"],


   // CORS的，也不用改
   "data_allowed_origins": ["*"],

   // 以下的host和post可以自己改

   "reservoir_host": "127.0.0.1",
   "reservoir_port": 7000,

   "electricity_host": "127.0.0.1",
   "electricity_port": 8551,

   "earthquake_host": "127.0.0.1",
   "earthquake_port": 8400,
   ```

## Run

裝完 PostgreSQL, Python；設定好 config.json 後

1. Database Basic Setup

   ```
   python setup.py
   python online_crawler.py //定時爬
   ```


2. Reservoir

   ```
   python reservoir.py
   ```

3. Earthquake

   ```
   python earthquake.py
   ```

4. Electricity

   ```
   python electricity.py
   ```

### 以下的 API 在 call 的時候 如果資料庫裡沒有就需要重爬，特別 Reservoir 會花超久所以盡量不要用太久的時間區段，或是可以先 call 幾次讓它爬完存好再 demo

## Resorvoir

1. API: [host]:[port]/reservoir_fetch/ (都是用 POST)

2. Body Parameters

   ```shell
   reservoir_names: 水庫名字 (array of strings)

   // 以下都是int
   year_to: 終止年
   month_to: 終止月
   day_to: 終止日
   hour_to: 終止時 (optional)
   minute_to: 終止分 (optional)
   second_to: 終止秒 (optional)

   past_hours: 過去幾個小時 (optional, 填了以下就不用填)

   year_from: 起始年
   month_from: 起始月
   day_from: 起始日
   hour_from: 起始時
   minute_from: 起始分
   second_from: 起始秒

   ```

3. Example Return

```
{
  "data": [
    {
      "水庫名稱": "曾文水庫",
      "時間": [
        "2023-06-03 16:00:00",
        "2023-06-03 17:00:00",
        "2023-06-03 18:00:00"
      ],
      "本日集水區累積降雨量(mm)": [
        29.7,
        30.5,
        30.8
      ],
      "進流量(cms)": [
        -1,
        -1,
        -1
      ],
      "水位(公尺)": [
        191.54,
        191.56,
        191.56
      ],
      "滿水位(公尺)": [
        230,
        230,
        230
      ],
      "有效蓄水量(萬立方公尺)": [
        3699,
        3706,
        3706
      ],
      "蓄水百分比(%)": [
        7.3,
        7.31,
        7.31
      ],
      "取水流量(cms)": [
        -1,
        -1,
        -1
      ],
      "發電放水口": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "排砂道/PRO": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "排洪隧道": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "溢洪道": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "其他": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "小計": [
        -1,
        -1,
        -1
      ],
      "目前狀態": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "預定時間": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "預定放流量(cms)": [
        -1,
        -1,
        -1
      ]
    },
    {
      "水庫名稱": "石門水庫",
      "時間": [
        "2023-06-03 16:00:00",
        "2023-06-03 17:00:00",
        "2023-06-03 18:00:00"
      ],
      "本日集水區累積降雨量(mm)": [
        -1,
        -1,
        -1
      ],
      "進流量(cms)": [
        -1,
        -1,
        -1
      ],
      "水位(公尺)": [
        231.75,
        231.74,
        231.73
      ],
      "滿水位(公尺)": [
        245,
        245,
        245
      ],
      "有效蓄水量(萬立方公尺)": [
        10690.57,
        10684.58,
        10678.59
      ],
      "蓄水百分比(%)": [
        52.08,
        52.05,
        52.02
      ],
      "取水流量(cms)": [
        -1,
        -1,
        -1
      ],
      "發電放水口": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "排砂道/PRO": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "排洪隧道": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "溢洪道": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "其他": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "小計": [
        -1,
        -1,
        -1
      ],
      "目前狀態": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "預定時間": [
        "-1.0",
        "-1.0",
        "-1.0"
      ],
      "預定放流量(cms)": [
        -1,
        -1,
        -1
      ]
    }
  ]
}
```

## Electricity

1. API: [host]:[port]/electricity_fetch/ (都是用 POST)

2. Body Parameters

   ```shell
   power_plant_regions: 地點 (array of strings, Ex: ['北'])

   // 以下都是int
   year_to: 終止年
   month_to: 終止月
   day_to: 終止日
   hour_to: 終止時 (optional)
   minute_to: 終止分 (optional)
   second_to: 終止秒 (optional)

   past_days: 過去幾天 (optional, 填了以下就不用填)

   year_from: 起始年
   month_from: 起始月
   day_from: 起始日
   hour_from: 起始時
   minute_from: 起始分
   second_from: 起始秒

   ```

3. Example Return

```
{
    "data": [
        {
            "區": "中",
            "時間": [
            "2023-04-02 00:00:00",
            "2023-04-03 00:00:00"
            ],
            "供電(萬瓩)": [
            855.5924000000001,
            831.8640000000001
            ],
            "負載(萬瓩)": [
            693.414,
            693.7650000000001
            ]
        },
        {
            "區": "北",
            "時間": [
            "2023-04-02 00:00:00",
            "2023-04-03 00:00:00"
            ],
            "供電(萬瓩)": [
            765.037,
            743.8199999999999
            ],
            "負載(萬瓩)": [
            919.4155999999999,
            919.881
            ]
        }
    ]
}

```

## Earthquake

1. API: [host]:[port]/earthquake_fetch/ (都是用 POST)

2. Body Parameters

   ```shell
   earthquake_regions: 地點 (array of strings, Ex: ['北'])

   // 以下都是int
   year_to: 終止年
   month_to: 終止月
   day_to: 終止日
   hour_to: 終止時 (optional)
   minute_to: 終止分 (optional)
   second_to: 終止秒 (optional)

   past_hours: 過去幾小時
   past_days: 過去幾天
   past_months: 過去幾月

   (optional, 上面三個填了一個以上以下就不用填)

   year_from: 起始年
   month_from: 起始月
   day_from: 起始日
   hour_from: 起始時
   minute_from: 起始分
   second_from: 起始秒

   ```

3. Example Returns

```shell
{
    "data": [
        {
            "區": "北",
            "時間": [
                "2021-03-30 06:06:55",
                "2021-03-30 22:16:42",
                "2021-03-31 03:07:20",
                "2021-04-02 13:50:56",
                "2021-04-03 15:31:18"
            ],
            "震度階級": [
                0,
                0,
                0,
                0,
                0
            ],
            "震央經度": [
                122.02,
                121.15,
                121.81,
                121.07,
                120.14
            ],
            "震央緯度": [
                24.81,
                21.91,
                24.45,
                22.5,
                22.88
            ],
            "震央規模": [
                4.01,
                3.93,
                2.86,
                4.1,
                3.77
            ],
            "震央深度": [
                13.72,
                32.39,
                17.38,
                24.58,
                15.67
            ],
            "震央震度階級": [
                2,
                2,
                4,
                2,
                3
            ]
        }
    ]
}
```
