from fastapi.testclient import TestClient
from electricity import app

client = TestClient(app)

def test_electricity_fetch():
    response = client.post("/electricity_fetch/", json = {
    "year_to": 2022,
    "month_to": 7,
    "day_to": 1,
    "hour_to": 0,
    "past_days": 5,
    "earthquake_regions": ["北", "中"],
  },
    headers = {
        "Content-Type": "application/json"
    })
    
    assert response.status_code == 422
    assert response.json() == {"detail":[{"loc":["body","power_plant_regions"],"msg":"field required","type":"value_error.missing"}]}
    
    
    response = client.post("/electricity_fetch/", json = {
        "year_to": 2022,
        "month_to": 7,
        "day_to": 1,
        "hour_to": 0,
        "past_days": 5,
        "power_plant_regions": ["北", "中"],
    },
    headers = {
        "Content-Type": "application/json"
    })
    
    assert response.status_code == 200
    assert response.json() == {"data":[{"區":"中","時間":["2022-06-26 00:00:00","2022-06-27 00:00:00","2022-06-28 00:00:00","2022-06-29 00:00:00","2022-06-30 00:00:00","2022-07-01 00:00:00"],"供電(萬瓩)":[1007.3336000000002,1154.6634,1145.1282,1105.8914,1149.9232000000002,1158.9926],"負載(萬瓩)":[875.3130000000001,1047.1950000000002,1048.842,1054.2150000000001,1042.443,1037.9070000000002]},{"區":"北","時間":["2022-06-26 00:00:00","2022-06-27 00:00:00","2022-06-28 00:00:00","2022-06-29 00:00:00","2022-06-30 00:00:00","2022-07-01 00:00:00"],"供電(萬瓩)":[900.7180000000001,1032.4545,1023.9285,988.8444999999999,1028.216,1036.3255],"負載(萬瓩)":[1160.6002,1388.503,1390.6868,1397.811,1382.2022,1376.1878]}]}