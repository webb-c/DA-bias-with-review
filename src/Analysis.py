import csv

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go
import kaleido
from nltk import FreqDist
from nltk import Text
from wordcloud import WordCloud
from collections import Counter

#fontPath = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
fontPath = "C:/Windows/Fonts/malgun.ttf"
font = font_manager.FontProperties(fname=fontPath).get_name()
rc('font', family=font)

readDirPath = '../data/test'
tableSaveDirPath = '../data/test' # ../data/analytics/table
imgSaveDirPath = '../data/test'   # ../data/analytics/visualization
def read_file() :
    '''
    dataframe structure =
        index, restaurant(str), review(str), length(int), totalRate(int), image(int; 1_0), event(int; 1_0)
    '''
    filepath_Y = readDirPath+'/노원구_전처리_Y.csv'
    filepath_N = readDirPath+'/노원구_전처리_N.csv'
    df_Y = pd.read_csv(filepath_Y)
    df_N = pd.read_csv(filepath_N)
    return df_Y, df_N

def analysis_aggregate(df, event):
    length = df.shape[0]
    photoCount = len(df.loc[df['image'] == 1])
    photoList = df['image'].value_counts().tolist()
    photoRate = photoCount / length
    scoreRate = df['totalRate'].value_counts().tolist()
    scoreRate_list = [x / length for x in scoreRate]
    # 시각화
    rate_fig = go.Figure(data=[go.Pie(labels=['5', '4', '3', '2', '1'], values=scoreRate, pull=[0.05, 0, 0, 0, 0])])
    rate_fig.update_layout(title="Pie graph : total score Rate")
    photo_fig = go.Figure(data=[go.Pie(labels=['True', 'False'], values=photoList, pull=[0.05, 0])])
    photo_fig.update_layout(title="Pie graph : photo Review Rate")
    pio.write_image(rate_fig, imgSaveDirPath + '/score_pie_{}.png'.format(event))
    pio.write_image(photo_fig, imgSaveDirPath + '/photo_pie_{}.png'.format(event))
    return photoRate, scoreRate_list

# 분포 분석 (histogram)
def analysis_distribution(df, event) :
    # length
    len_df = df['length'].value_counts().to_frame().reset_index()
    len_df = len_df.rename(columns={'index':'length', 'length': 'count'})
    len_df.to_csv( tableSaveDirPath + "/length_count_{}.csv".format(event), encoding='utf-8-sig')
    len_info = []
    len_info.append(df['length'].mean())
    len_info.append(df['length'].std())
    len_info.append(df['length'].max())
    len_info.append(df['length'].min())
    # rate
    rate_df = df['totalRate'].value_counts().to_frame().reset_index()
    rate_df = rate_df.rename(columns={'index': 'totalRate', 'totalRate': 'count'})
    rate_df.to_csv(tableSaveDirPath + "/score_count_{}.csv".format(event), encoding='utf-8-sig')
    rate_info = []
    rate_info.append(df['totalRate'].mean())
    rate_info.append(df['totalRate'].std())

    # 시각화
    len_fig = px.histogram(df, x='length')
    rate_fig = px.histogram(df, x='totalRate', barmode='group')
    rate_fig.update_layout(bargap=0.5)
    len_fig.update_layout(
        title="Histogram : Review Length",
        xaxis_title="Length",
        yaxis_title="Frequency",
    )
    rate_fig.update_layout(
        title="Histogram : total score Length",
        xaxis_title="Score",
        yaxis_title="Frequency",
    )
    pio.write_image(len_fig, imgSaveDirPath + '/len_histo_{}.png'.format(event))
    pio.write_image(rate_fig, imgSaveDirPath + '/score_histo_{}.png'.format(event))

    return len_info, rate_info

def analysis_text(df, event):
    reviewList = list(df['review'])
    wordList = list(word for review in reviewList for word in review.split())
    # 단어 개수 카운트
    words = Text(wordList, name="요기요 리뷰데이터")
    dic = FreqDist(wordList)
    plt.figure(figsize=(13,9))
    words.plot(10)
    plt.show() # 직접 저장
    print("총 단어의 개수: ", dic.N())
    print("고유 단어의 개수: ", dic.B())
    print("===== 빈도수 정렬 =====")
    print(dic.most_common(n=10))
    countData = pd.DataFrame(dic.most_common(), columns=['word', 'frequency'])
    countData.to_csv(tableSaveDirPath + '/words_{}.csv'.format(event), encoding='utf-8-sig')
    # 시각화
    word_cloud = WordCloud (
        font_path=fontPath,
        min_font_size=1,
        max_font_size=40,
        relative_scaling=0.2,
        background_color='white',
        prefer_horizontal=0.6,
    ).generate_from_frequencies(dic)
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()
    return countData

def analysis_print(distribution_info, aggregate_info, text_info) :
    len_info, rate_info = distribution_info
    photoRate, scoreRate_list = aggregate_info
    print("1) 리뷰 텍스트의 길이 분석")
    print("평균: " + str(len_info[0]) + " 표준편차: " + str(len_info[1]) + " 최대길이: " + str(len_info[2]) + " 최소길이: " + str(len_info[3]))
    print("\n2) 별점 분석")
    print("평균: " + str(rate_info[0]) + " 표준편차: " + str(rate_info[1]))
    for i, rate in enumerate(scoreRate_list):
        print(str(5 - i) + "점의 비율 : " + str(rate))
    print("\n3) 포토 리뷰의 비율: "+str(photoRate))


def analysis() :
    df_Y, df_N = read_file()
    print("***** 리뷰이벤트를 진행하는 곳 *****")
    #analysis_print(analysis_distribution(df_Y, 'Y'), analysis_aggregate(df_Y, 'Y'), 0)
    analysis_text(df_Y, 'Y')
    #print("\n***** 리뷰이벤트를 진행하지 않는 곳 *****")
    #analysis_print(analysis_distribution(df_N, 'N'), analysis_aggregate(df_N, 'N'), 0)

analysis()