import re
import os
import csv
from konlpy.tag import Okt
import pandas as pd
from tqdm import tqdm
import kss

okt = Okt()
f = open("../data/stopwords.txt", 'r')
stop_words = [line.strip() for line in f.readlines()]
f.close()

def extract_word(text):
    hangul = re.compile('[^가-힣]')
    result = hangul.sub(' ', text).strip()
    return result

def origin_to_processing(review) :
    # 원천 리뷰 길이
    length = len(review)
    # 문장 단위로 변환
    sentence_tokens = kss.split_sentences(review)
    clean_sentence_tokens = []
    for sentence in sentence_tokens :
        kor_sentence = extract_word(sentence)    # 한글 추출
        # 토큰화
        word_tokens = okt.pos(kor_sentence, norm=True)
        # 불용어 제거
        clean_word_tokens = []
        for word, pos in word_tokens :
            # 1. 명사, 동사, 형용사만 사용
            if pos in ['Noun', 'Verb', 'VerbPrefix', 'Adverb', 'Adjective'] :
                # 2. 불용어 사전 사용 (https://www.ranks.nl/stopwords/korean)
                if word not in stop_words :
                    clean_word_tokens.append(word)
        # 저장을 위해 원본 형태로 변경
        clean_sentence_tokens.append(" ".join(clean_word_tokens).strip())
    clean_review = ". ".join(clean_sentence_tokens).strip()
    return length, clean_review

# csv 파일 읽기 & 쓰기
dfY = pd.DataFrame(
    columns=[
        "restaurant",
        "review",
        "length",
        "totalRate",
        "image",
    ]
)

dfN = pd.DataFrame(
    columns=[
        "restaurant",
        "review",
        "length",
        "totalRate",
        "image",
    ]
)

db = open('../data/test/노원구.csv', 'r', encoding='utf-8-sig')
reader = csv.reader(db)
next(reader) # 헤더 제거
num = 0
for row in tqdm(reader):
    # Restaurant(str), Review,(str) avg rate(int; 0,5), image(T/F), event(Y/N)
    name, review, rate, image, event = row[1], row[4], row[5], row[9], row[10]
    length, new_review = origin_to_processing(review)
    # test
    test_review = new_review.replace(" ", "").replace(".", "")
    if len(test_review) == 0 : continue
    if event == "Y":
        dfY.loc[len(dfY)] = {
            "restaurant" : name,
            "review" : new_review,
            "length" : length,
            "totalRate" : rate,
            "image" : 1 if image == 'T' else 0,
        }
    else:
        dfN.loc[len(dfN)] = {
            "restaurant": name,
            "review": new_review,
            "length": length,
            "totalRate": rate,
            "image": 1 if image == 'T' else 0,
        }

db.close()

# 저장
dfY.to_csv("../data/test/노원구_전처리_Y.csv", encoding='utf-8-sig')
dfN.to_csv("../data/test/노원구_전처리_N.csv", encoding='utf-8-sig')
print("csv 파일 저장완료")