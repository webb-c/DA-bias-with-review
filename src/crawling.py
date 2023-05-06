import argparse

import time
import pickle
import pandas as pd
from tqdm import trange, tqdm
import warnings

warnings.filterwarnings("ignore")

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

# 현재까지 모은 데이터 카운팅 하기 위한 변수
global COUNT_Y
global COUNT_N
COUNT_Y = 0
COUNT_N = 0

# 스크롤 내리기
def scroll_bottom():
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")


# 1. 해당 카테고리 음식점 리스트 리턴
def get_restaurant_list(lat, lng, items=100):

    restaurant_list = []
    # 헤더 선언 및 referer, User-Agent 전송
    headers = {
        "referer": "https://www.yogiyo.co.kr/mobile/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
        "Accept": "application/json",
        "x-apikey": "iphoneap",
        "x-apisecret": "fe5183cc3dea12bd0ce299cf110a75a2",
    }
    params = {
        "items": items,
        "lat": lat,
        "lng": lng,
        "order": ORDER_OPTION,
        "page": 0,
        "search": "",
    }
    host = "https://www.yogiyo.co.kr"
    path = "/api/v1/restaurants-geo/"
    url = host + path

    response = requests.get(url, headers=headers, params=params)

    count = 0
    for item in response.json()["restaurants"]:
        restaurant_list.append(item["id"])
        count += 1
    return list(restaurant_list)


# 2. 검색한 음식점 페이지 들어가기
def go_to_restaurant(id):
    try:
        restaurant_url = "https://www.yogiyo.co.kr/mobile/#/{}/".format(id)
        driver.get(url=restaurant_url)
        print(driver.current_url)
    except Exception as e:
        print("go_to_restaurant 에러")
    time.sleep(2)


# 3-1. 해당 음식점의 정보 페이지로 넘어가기
def go_to_info():
    print("정보 페이지 로드중...")
    driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/ul/li[3]/a').click()
    time.sleep(1)
    print("정보 페이지 로드 완료")


# 3-2. 정보 더보기 클릭하기
def get_info():
    op_time = driver.find_element(By.XPATH, '//*[@id="info"]/div[2]/p[1]/span').text
    addr = driver.find_element(By.XPATH, '//*[@id="info"]/div[2]/p[3]/span').text
    print(op_time)
    print(addr)
    return op_time, addr


# 4-1. 해당 음식점의 리뷰 페이지로 넘어가기
def go_to_review():
    print("리뷰 페이지 로드중...")
    driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/ul/li[2]/a').click()
    time.sleep(2)
    print("리뷰 페이지 로드 완료")


# 4-2. 리뷰 더보기 클릭하기
def click_more_review():
    driver.find_element(By.CLASS_NAME, "btn-more").click()
    time.sleep(1)


# 5. 리뷰 페이지 모두 펼치기
def stretch_review_page(rornot):
    global COUNT_N
    global COUNT_Y
    local_count = 0
    review_count = int(
        driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div[1]/ul/li[2]/a/span').text
    )
    click_count = int((review_count / 10))
    print("모든 리뷰 불러오기 시작...")
    for _ in trange(click_count):
        try:
            if local_count >= 1000 : break
            scroll_bottom()
            click_more_review()
            local_count += 10
            if rornot == 'Y':  COUNT_Y += 10
            else: COUNT_N += 10
            print(COUNT_Y, COUNT_N)

        except Exception as e:
            pass
    scroll_bottom()
    print("모든 리뷰 불러오기 완료")


# 6. 해당 음식점의 모든 리뷰 객체 리턴
def get_all_review_elements():
    try:
        reviews = driver.find_elements(
            By.CSS_SELECTOR,
            "#review > li.list-group-item.star-point.ng-scope"
        )
    except Exception as e:
        print("리뷰 객체 반환 오류")
        print(e)
    return reviews


# 7. 페이지 뒤로 가기 (한 음식점 리뷰를 모두 모았으면 다시 음식점 리스트 페이지로 돌아감)
def go_back_page():
    print("페이지 돌아가기중...")
    driver.execute_script("window.history.go(-1)")
    time.sleep(2)
    print("페이지 돌아가기 완료" + "\n")


# 8. 크롤링과 결과 데이터를 pickle 파일과 csv파일로 저장
def save_pickle_csv(location, yogiyo_df, id):
    yogiyo_df.to_csv("C:/Users/CoIn240/PycharmProjects/DA/data/origin/{}_{}_{}df.csv".format(location[0], location[1], id), encoding='utf-8-sig')
    pickle.dump(yogiyo_df, open("C:/Users/CoIn240/PycharmProjects/DA/data/origin/pkl/{}_{}_{}df.pkl".format(location[0], location[1], id), "wb"))
    print("{} {} pikcle save complete.".format(location[0], location[1]))


# 9. 크롤링 메인 함수
def yogiyo_crawling(location):
    # 전역 선언
    global COUNT_N
    global COUNT_Y
    global REVIEW_COUNT

    # 에러 발생하는 가게 / 이미 방문한 가게제거를 위한 코드
    f = open("../data/id.txt", 'r')
    errList = []
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        errList.append(int(line))
    f.close()

    print(errList)

    # 데이터 프레임 구조 설정
    df = pd.DataFrame(
        columns=[
            "Restaurant",
            "UserID",
            "Menu",
            "Review",
            "Total",
            "Taste",
            "Quantity",
            "Delivery",
            "image",
            "event",
            "Date",
            "OperationTime",
            "Address",
            
        ]
    )

    try:
        restaurant_list = get_restaurant_list(
            location[0], location[1], RESTAURANT_COUNT
        )
        for restaurant_id in restaurant_list:
            try:

                print(
                    "********** "
                    + str(restaurant_list.index(restaurant_id) + 1)
                    + "/"
                    + str(len(restaurant_list))
                    + " 번째 ("
                    + str(restaurant_id)
                    + ") **********"
                )

                if restaurant_id in errList : continue # 오류나는 곳이면 skip

                go_to_restaurant(restaurant_id)  # 검색한 음식점 클릭
                go_to_info()  # 음식점 정보창 클릭

                infotext = driver.find_element(By.XPATH, '//*[@id="info"]/div[1]/div[2]').text
                print(infotext)

                # 리뷰이벤트 유무 확인
                rornot ='N'

                if "리뷰이벤트" in infotext:
                    rornot = "Y"
                if "이벤트" in infotext:
                    rornot = "Y"
                if "리뷰" in infotext:
                    rornot = "Y"
                if "별점" in infotext:
                    rornot = "Y"
                if "5점" in infotext:
                    rornot = "Y"

                if rornot == 'Y' and COUNT_Y >= REVIEW_COUNT : continue
                if rornot == 'N' and COUNT_N >= REVIEW_COUNT : continue
                op_time, addr = get_info()

                go_to_review()
                stretch_review_page(rornot)
                reviews = get_all_review_elements()

                for review in tqdm(reviews):  # 해당 음식점의 리뷰 수 만큼 데이터를 가져옴
                    try:
                        review.find_element(By.CSS_SELECTOR, "table.info-images > tbody > tr > td > div > img")
                        image = "T"
                    except:
                        image = "F"

                    try:
                        df.loc[len(df)] = {
                            "Restaurant": driver.find_element(By.CLASS_NAME, "restaurant-name").text,
                            "UserID": review.find_element(By.CSS_SELECTOR, "span.review-id.ng-binding").text,
                            "Menu": review.find_element(By.CSS_SELECTOR, "div.order-items.default.ng-binding").text,
                            "Review": review.find_element(By.CSS_SELECTOR, "p").text,
                            "image": image,
                            "Total": str(
                                len(review.find_elements(By.CSS_SELECTOR, "div > span.total > span.full.ng-scope"))
                            ),
                            "Taste": review.find_element(By.CSS_SELECTOR, "div:nth-child(2) > div > span.category > span:nth-child(3)").text,
                            "Quantity": review.find_element(By.CSS_SELECTOR, "div:nth-child(2) > div > span.category > span:nth-child(6)").text,
                            "Delivery": review.find_element(By.CSS_SELECTOR, "div:nth-child(2) > div > span.category > span:nth-child(9)").text,
                            "Date": review.find_element(By.CSS_SELECTOR,  "div:nth-child(1) > span.review-time.ng-binding").text,
                            "OperationTime": op_time,
                            "Address": addr,
                            "event": rornot,
                        }
                    except Exception as e:
                        print("리뷰 페이지 에러")
                        print(e)
                        pass
                
                # 가게 별 (1000개) 저장
                save_pickle_csv(location, df, COUNT_Y+COUNT_N)
                print("save "+str(COUNT_Y)+" : "+str(COUNT_N)+" data.")
                f = open("../data/id.txt", 'a')
                f.write(str(restaurant_id)+"\n")
                f.close()

                if COUNT_N >= REVIEW_COUNT and COUNT_N >= REVIEW_COUNT : break

                del[[df]]
                df = pd.DataFrame(
                    columns=[
                        "Restaurant",
                        "UserID",
                        "Menu",
                        "Review",
                        "Total",
                        "Taste",
                        "Quantity",
                        "Delivery",
                        "image",
                        "event",
                        "Date",
                        "OperationTime",
                        "Address",

                    ]
                )

            except Exception as e:
                print("*** 음식점 ID: " + restaurant_id + " *** 음식점 페이지 에러")
                print(e)
                f = open("../data/id.txt", 'a')
                f.write(str(restaurant_id)+"\n")
                f.close()
                pass

            print("음식점 리스트 페이지로 돌아가는중...")
            go_back_page()

    except Exception as e:
        print("*** 음식점 ID: " + restaurant_id + " *** 접근 에러")
        print(e)
        f = open("../data/id.txt", 'a')
        f.write(str(restaurant_id)+"\n")
        f.close()
        pass

    print("End of [ {} - {} ] Crawling.".format(location[0], location[1]))
    print("{} {} crawling finish.".format(location[0], location[1]))

    return df


# 10. 요기요 크롤링 실행 함수
def start_yogiyo_crawling():

    locations = [[LAT, LON]]

    for location in locations:
        try:
            yogiyo_crawling(location)
        except Exception as e:
            print(e)
            pass

# 실행 환경
parser = argparse.ArgumentParser(description="Arguments for Crawler")
parser.add_argument(
    "--order",
    required=False,
    default="review_count",
    help="option for restaurant list order / choose one \
    -> [rank, review_avg, review_count, min_order_value, distance, estimated_delivery_time]",
)
parser.add_argument("--num", required=False, default=2000, help="option for amount of review data")
parser.add_argument("--lat", required=False, default=37.5128, help="latitude for search")
parser.add_argument("--lon", required=False, default=126.9240, help="longitude for search")
args = parser.parse_args()

ORDER_OPTION = args.order
REVIEW_COUNT = int(args.num)
RESTAURANT_COUNT = 50
LAT = float(args.lat)
LON = float(args.lon)

# 크롬 드라이버 경로 설정
chromedriver = "C:/Users/CoIn240/PycharmProjects/DA/Application/chrome.exe"
driver = webdriver.Chrome(chromedriver)

url = "https://www.yogiyo.co.kr/mobile/#/"

# fake_useragent 모듈을 통한 User-Agent 정보 생성
driver.get(url=url)
print(driver.current_url)

start_yogiyo_crawling()