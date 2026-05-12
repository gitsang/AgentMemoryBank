# Ctrip URL/API Pattern Reference — Xiamen↔Hefei (May 2026)

All city codes verified: Xiamen = XMN, Hefei = HFE. Train station names: 厦门, 合肥.

---

## PART 1: Ctrip Domestic Flights (Ctrip-only)

### A) Direct Browser UI URLs

**Outbound: XMN→HFE, Fri 2026-05-15 after 19:00**

| Version | URL |
|---------|-----|
| PC Oneway | `https://flights.ctrip.com/itinerary/oneway/xmn-hfe?date=2026-05-15` |
| PC Roundtrip | `https://flights.ctrip.com/itinerary/roundtrip/xmn-hfe?date=2026-05-15,2026-05-17` |
| Mobile Web | `https://m.ctrip.com/html5/flight/xmn-hfe-day-1.html` |
| Old Booking | `https://flights.ctrip.com/booking/XMN-HFE-day-1.html?DDate1=2026-05-15` |
| Schedule | `https://flights.ctrip.com/schedule/xmn.hfe.html` |

**Return: HFE→XMN, Sun 2026-05-17 evening / Mon 2026-05-18 early**

| Version | URL |
|---------|-----|
| PC Oneway (Sun) | `https://flights.ctrip.com/itinerary/oneway/hfe-xmn?date=2026-05-17` |
| PC Oneway (Mon) | `https://flights.ctrip.com/itinerary/oneway/hfe-xmn?date=2026-05-18` |
| Mobile Web | `https://m.ctrip.com/html5/flight/hfe-xmn-day-1.html` |

---

### B) Primary API — `products` (POST, returns full flight data)

**Endpoint:** `https://flights.ctrip.com/itinerary/api/12808/products`

**Outbound (XMN→HFE 2026-05-15):**
```bash
curl -s 'https://flights.ctrip.com/itinerary/api/12808/products' \
  -H 'Content-Type: application/json;charset=utf-8' \
  -H 'Origin: https://flights.ctrip.com' \
  -H 'Referer: https://flights.ctrip.com/itinerary/oneway/xmn-hfe?date=2026-05-15' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' \
  -d '{
    "flightWay":"Oneway",
    "classType":"ALL",
    "hasChild":false,
    "hasBaby":false,
    "searchIndex":1,
    "airportParams":[{
      "dcity":"xmn",
      "acity":"hfe",
      "dcityname":"厦门",
      "acityname":"合肥",
      "date":"2026-05-15"
    }]
  }'
```

**Return (HFE→XMN 2026-05-17):** Same endpoint, change `"date":"2026-05-17"`, swap dcity/acity.

**Roundtrip in one call:**
```json
{
  "flightWay": "Roundtrip",
  "classType": "ALL",
  "hasChild": false,
  "hasBaby": false,
  "searchIndex": 1,
  "airportParams": [
    {"dcity":"xmn","acity":"hfe","dcityname":"厦门","acityname":"合肥","date":"2026-05-15"},
    {"dcity":"hfe","acity":"xmn","dcityname":"合肥","acityname":"厦门","date":"2026-05-17"}
  ]
}
```

**Response structure (from [FlyCheap ctripcrawler.py](https://github.com/LF502/FlyCheap/blob/main/ctripcrawler.py)):**
```json
{
  "status": 0,
  "msg": "success",
  "data": {
    "routeList": [
      {
        "routeType": "Flight",
        "legs": [{
          "flightNumber": "...",
          "airline": "...",
          "departureDate": "2026-05-15 19:xx",
          "arrivalDate": "2026-05-15 21:xx",
          "price": ...
        }]
      }
    ]
  }
}
```

**IMPORTANT caveat:** This endpoint may require a valid session cookie and a `token` field in the payload (seen in some sources, e.g. `"token":"c44ac9b713d250d50e45dea7a60e18f0"`). If the bare POST fails, first fetch the referer page to extract the token, then include it.

---

### C) Lowest Price API (GET, lighter)

**Endpoint:** `https://flights.ctrip.com/itinerary/api/12808/lowestPrice`

```bash
curl 'https://flights.ctrip.com/itinerary/api/12808/lowestPrice?flightWay=Oneway&dcity=XMN&acity=HFE&direct=true&army=false'
```

Returns only lowest prices per carrier — useful for quick fare comparison, not full schedule.

---

### D) Mobile API (POST)

**Endpoint:** `https://m.ctrip.com/restapi/soa2/14022/flightListSearch?_fxpcqlniredt=09031039219678951998`

```bash
curl -s 'https://m.ctrip.com/restapi/soa2/14022/flightListSearch?_fxpcqlniredt=09031039219678951998' \
  -H 'Content-Type: application/json' \
  -d '{
    "preprdid":"",
    "trptpe":1,
    "flag":8,
    "searchitem":[{"dccode":"XMN","accode":"HFE","dtime":"2026-05-15"}],
    "subchannel":null,
    "head":{
      "cid":"09031039219678951998",
      "ctok":"",
      "cver":"1.0",
      "lang":"01",
      "sid":"8888",
      "syscode":"09",
      "auth":null,
      "extension":[{"name":"aid","value":"66672"},{"name":"sid","value":"1693366"},{"name":"protocal","value":"https"}]
    },
    "contentType":"json"
  }'
```

**Response field mapping (from mobile API):**
```json
{
  "fltitem": [{
    "basinfo": {"aircode":"MU","airsname":"东航","flgno":"MU1234"},
    "dateinfo": {"ddate":"2026-05-15 19:15:00","adate":"2026-05-15 21:00:00"},
    "policyinfo": [...]
  }]
}
```

---

### E) Older (deprecated) DOM-based JSON URL

```bash
curl 'http://flights.ctrip.com/domesticsearch/search/SearchFirstRouteFlights?DCity1=XMN&ACity1=HFE&SearchType=S&DDate1=2026-05-15'
```

May require rk/CK/r parameters extracted from the booking page. Not recommended as primary — `/api/12808/products` is newer and more stable.

---

## PART 2: Ctrip Trains (Ctrip-only)

### A) Direct Browser UI URLs

**Outbound: 厦门→合肥, Fri 2026-05-15**
```
https://trains.ctrip.com/trainbooking/xiamen-hefei/
```

With date parameter:
```
https://trains.ctrip.com/trainbooking/search?fromcn=%E5%8E%A6%E9%97%A8&tocn=%E5%90%88%E8%82%A5&day=2026-05-15
```

**Return: 合肥→厦门, Sun 2026-05-17 or Mon 2026-05-18**
```
https://trains.ctrip.com/trainbooking/search?fromcn=%E5%90%88%E8%82%A5&tocn=%E5%8E%A6%E9%97%A8&day=2026-05-17
https://trains.ctrip.com/trainbooking/search?fromcn=%E5%90%88%E8%82%A5&tocn=%E5%8E%A6%E9%97%A8&day=2026-05-18
```

---

### B) Train Transfer/Route API (POST)

**Endpoint:** `https://m.ctrip.com/restapi/soa2/14666/json/TrainGetTransferRouteV2?_fxpcqlniredt=09031078419575776586&x-traceID=09031078419575776586-1636965163954-7608539`

```bash
curl -s 'https://m.ctrip.com/restapi/soa2/14666/json/TrainGetTransferRouteV2?_fxpcqlniredt=09031078419575776586&x-traceID=09031078419575776586-1636965163954-7608539' \
  -H 'Content-Type: application/json' \
  -d '{
    "head": {
      "cid":"","ctok":"","cver":"1.0","lang":"01",
      "sid":"8888","syscode":"09","auth":"","xsid":"",
      "extension":[{"name":"protocal","value":"https"}],
      "clientID":"","APIKey":"CtripWap","source":"Online","version":"708.000"
    },
    "contentType":"json",
    "channel":"PC",
    "departureName":"厦门",
    "arrivalName":"合肥",
    "departureDate":"20260515",
    "serviceVersion":1,
    "OptionalFilter":{"TransferType":"Train"}
  }'
```

Returns `{"Train": {"TrainNumber": "...", "DepartTime": "...", ...}}` with direct and transfer routes.

---

### C) Transfer List API (GET)

**Endpoint:** `https://trains.ctrip.com/pages/booking/getTransferList`

```bash
curl 'https://trains.ctrip.com/pages/booking/getTransferList?departureStation=%E5%8E%A6%E9%97%A8&arrivalStation=%E5%90%88%E8%82%A5&departDateStr=2026-05-15'
```

Note: uses plain URL-encoded Chinese station names.

---

## PART 3: 12306 API (Non-Ctrip Fallback)

### Station Code Lookup
Fetch station codes: `https://kyfw.12306.cn/otn/resources/js/framework/station_name.js`

For Xiamen→Hefei: Xiamen station code is `XKS` (厦门北), Hefei station code is `HFH` (合肥). Find these in the station_name.js response by searching for "厦门" and "合肥".

### Train Query
```bash
curl 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date=2026-05-15&leftTicketDTO.from_station=XKS&leftTicketDTO.to_station=HFH&purpose_codes=ADULT'
```

Note: The query suffix letter (Z in `queryZ`) changes periodically — try `query`, `queryA`, `queryZ`, etc. The response includes a `c_url` field pointing to the latest endpoint.

---

## PART 4: Key Caveats Summary

| Issue | Details |
|-------|---------|
| **Anti-bot** | Ctrip APIs check `Referer` + `Origin` + `User-Agent` + sometimes Cookie/token. Always include proper headers. |
| **Token** | The `products` endpoint sometimes requires a `token` field in payload, scraped from referer page HTML/JS. |
| **Encoding** | Old endpoints return `gb2312` (not UTF-8). New ones return JSON. |
| **Rate limits** | Known Ctrip crawlers use 4-6s delays between requests. Rapid-fire will be blocked. |
| **URL stability** | The `/itinerary/oneway/{city}-{city}` pattern has been stable since ~2019. `booking/{CITY}-{CITY}-day-1.html` is legacy. |
| **12306 suffix** | 12306 API changes the final letter of `/queryX` regularly. Check `c_url` in response for latest. |

---

## Quick Reference Card

```
FLIGHTS
  PC search:    flights.ctrip.com/itinerary/oneway/{dcity}-{acity}?date={YYYY-MM-DD}
  API (POST):   flights.ctrip.com/itinerary/api/12808/products
  Lowest (GET): flights.ctrip.com/itinerary/api/12808/lowestPrice?flightWay=Oneway&dcity=XMN&acity=HFE
  Mobile:       m.ctrip.com/html5/flight/{dcity}-{acity}-day-1.html
  Mobile API:   m.ctrip.com/restapi/soa2/14022/flightListSearch

TRAINS
  PC search:    trains.ctrip.com/trainbooking/search?fromcn=厦门&tocn=合肥&day=2026-05-15
  Transfer API: trains.ctrip.com/pages/booking/getTransferList?departureStation=厦门&arrivalStation=合肥
  Mobile API:   m.ctrip.com/restapi/soa2/14666/json/TrainGetTransferRouteV2

FALLBACK
  12306 query:  kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date=2026-05-15&...
```

## Sources

- [FlyCheap ctripcrawler.py](https://github.com/LF502/FlyCheap/blob/main/ctripcrawler.py)
- [p32_get_ctrip.py](https://github.com/zzzzzzhu/py_application/blob/master/p32_get_ctrip.py)
- [ctrip flight spider (gist)](https://gist.github.com/DCMMC/32b1a713c15636de850b177e6922bbe8)
- [携程火车票API (CSDN)](https://blog.csdn.net/qq_36664772/article/details/121337832)
- [携程手机版国内机票数据 (CSDN)](https://blog.csdn.net/m0_58095675/article/details/121570321)
- [/xiechengjipiao_api (GitHub)](https://github.com/xiaoeno/-xiechengjipiao_api)
