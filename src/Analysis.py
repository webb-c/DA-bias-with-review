import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from nltk import FreqDist
from wordcloud import WordCloud
from collections import Counter

def read_file() :
    '''
    dataframe structure =
        index, restaurant(str), review(str), length(int), totalRate(int), image(int; 1_0), event(int; 1_0)
    '''
    filepath_Y = '../data/test/노원구_전처리_Y.csv'
    filepath_N = '../data/test/노원구_전처리_N.csv'
    df_Y = pd.read_csv(filepath_Y)
    df_N = pd.read_csv(filepath_N)
    return df_Y, df_N

def analysis_aggregate(df):
    length = df.shape[0]
    photoCount = len(df.loc[df['image'] == 1])
    photoRate = photoCount / length
    scoreRate_list = [x / length for x in df['totalRate'].value_counts().tolist()]

    return photoRate, scoreRate_list

# 분포 분석 (histogram)
def analysis_distribution(df) :
    len = df.shape[0]
    # length
    len_df = df['length'].value_counts().to_frame().reset_index()
    len_df = len_df.rename(columns={'index':'length', 'length': 'count'})

    plt.hist(df.iloc[:, 3], bins=50)
    plt.show()

    len_info = []
    len_info.append(df['length'].mean())
    len_info.append(df['length'].std())
    len_info.append(df['length'].max())
    len_info.append(df['length'].min())

    # rate
    rate_df = df['totalRate'].value_counts().to_frame().reset_index()
    rate_df = rate_df.rename(columns={'index': 'totalRate', 'totalRate': 'count'})

    plt.hist(df.iloc[:, 4], bins=5)
    plt.show()

    rate_info = []
    rate_info.append(df['totalRate'].mean())
    rate_info.append(df['totalRate'].std())

    return len_info, rate_info

# def analysis_text(df):

def analysis_print(distribution_info, aggregate_info, text_info) :
    len_info, rate_info = distribution_info
    photoRate, scoreRate_list = aggregate_info
    print("1) 리뷰 텍스트의 길이 분석")
    print("평균: " + str(len_info[0]) + " 표준편차: " + str(len_info[1]) + " 최대길이: " + str(len_info[2]) + " 최소길이: " + str(
        len_info[3]))
    print("\n2) 별점 분석")
    print("평균: " + str(rate_info[0]) + " 표준편차: " + str(rate_info[1]))
    for i, rate in enumerate(scoreRate_list):
        print(str(5 - i) + "점의 비율 : " + str(rate))
    print("\n3) 포토 리뷰의 비율: "+str(photoRate))


def analysis() :
    df_Y, df_N = read_file()
    print("***** 리뷰이벤트를 진행하는 곳 *****")
    analysis_print(analysis_distribution(df_Y), analysis_aggregate(df_Y), 0)

    print("\n***** 리뷰이벤트를 진행하지 않는 곳 *****")
    analysis_print(analysis_distribution(df_N), analysis_aggregate(df_N), 0)


analysis()