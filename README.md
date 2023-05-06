# 2023-1 DA Term Project

### Introduction

---

_2023 Spring, Data Analytics (Yoon) Term Project Code._

리뷰 이벤트로 인해 고객이 작성한 리뷰에 대한 신뢰성이 떨어지고 가게의 평점 평균이 실제 값보다 더 높게 표현되는 편향현상이 발생할 수 있다.

본 연구에서는 리뷰 데이터를 크롤링을 이용하여 수집하여 분석하고, 실제로 리뷰이벤트를 진행하는 매장에 편향이 얼마나 크게 발생하는지 분포를 확인할 것이다.

최종적으로는 리뷰 데이터의 특징을 이용하여 해당 리뷰에 대한 신뢰도 추정하는 신경망 모델을 기반으로 가게의 평균 별점에서 편향치를 어느정도 제거한 신뢰성 높은 평점을 제공하는 것을 목적으로 한다.

<br>

### Environment

---

The `requirements.txt` file should list All Python Libraries that your PC depends on. installed by :
```bash
pip install -r requirement.txt
```

<br>

### Run : Crawler

---
move `src` directory and Using :
``` bash
python crawling.py --order [ORDER] --num [NUM] --lat [LAT] --lon [LON]
```
_where_ option is 

- order : order criteria
  - rank
  - review_avg
  - review_count (default)
  - min_order_value
  - distance
- num : # review (each)
- lat : latitude
- lon : longitude

Basically, more than 500 reviews are collected each for stores that hold review events and stores that do not. 

@ crawler reference : https://github.com/ariels1996/Yogiyo-Review-Crawling-with-Selenium