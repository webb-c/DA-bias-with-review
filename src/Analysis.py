import csv

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

fontPath = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
#fontPath = "C:/Windows/Fonts/malgun.ttf"
font = font_manager.FontProperties(fname=fontPath).get_name()
rc('font', family=font)

readDirPath = '../data/dataset'
tableSaveDirPath = '../data/analytics/table'
imgSaveDirPath = '../data/analytics/visualization'

def read_file() :
    '''
    dataframe structure =
        index, restaurant(str), review(str), length(int), totalRate(int), image(int; 1_0), event(int; 1_0)
    '''
    filepath_Y = readDirPath+'/dataset_Y.csv'
    filepath_N = readDirPath+'/dataset_N.csv'
    filepath = readDirPath+'/dataset_All.csv'
    df_Y = pd.read_csv(filepath_Y)
    df_N = pd.read_csv(filepath_N)
    df = pd.read_csv(filepath)
    return df_Y, df_N, df

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
    words.plot(10)
    plt.show() # 직접 저장
    print("총 단어의 개수: ", dic.N())
    print("고유 단어의 개수: ", dic.B())
    print("===== 빈도수 정렬 =====")
    print(dic.most_common(n=10))
    countData = pd.DataFrame(dic.most_common(), columns=['word', 'frequency'])
    countData.to_csv(tableSaveDirPath + '/words_{}.csv'.format(event), encoding='utf-8-sig')
    # 시각화
    # text_visualization(dic)
    return countData

def analysis_print(distribution_info, aggregate_info) :
    len_info, rate_info = distribution_info
    photoRate, scoreRate_list = aggregate_info
    print("1) 리뷰 텍스트의 길이 분석")
    print("평균: " + str(len_info[0]) + " 표준편차: " + str(len_info[1]) + " 최대길이: " + str(len_info[2]) + " 최소길이: " + str(len_info[3]))
    print("\n2) 별점 분석")
    print("평균: " + str(rate_info[0]) + " 표준편차: " + str(rate_info[1]))
    for i, rate in enumerate(scoreRate_list):
        print(str(5 - i) + "점의 비율 : " + str(rate))
    print("\n3) 포토 리뷰의 비율: "+str(photoRate))

def text_visualization(fdic):
    font_path = '/Users/vaughan/Library/Fonts/NanumBarunGothic.otf'  # 윈도우 ?
    word_cloud = WordCloud(
        font_path=font_path,
        min_font_size=1,
        max_font_size=40,
        relative_scaling=0.2,
        background_color='white',
        prefer_horizontal=0.6,
    ).generate_from_frequencies(fdic)
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

def between_review(countY, countN):
    # 음식 이름 제거 (시각화)
    f = open("../data/food_words.txt", 'r')
    foodList = [line.strip() for line in f.readlines()]
    f.close()
    countY = countY[~countY['word'].isin(foodList)]
    countN = countN[~countN['word'].isin(foodList)]
    fdistY = FreqDist(dict(zip(list(countY['word']), list(countY['frequency']))))
    fdistN = FreqDist(dict(zip(list(countN['word']), list(countN['frequency']))))
    #text_visualization(fdistY)
    #text_visualization(fdistN)

    # 단어별 비율 계산
    countY['count_rate'] = countY['frequency'] / sum(countY['frequency'])
    countN['count_rate'] = countN['frequency'] / sum(countN['frequency'])
    countY_del = countY[countY['count_rate'] >= 0.0003]
    countN_del = countN[countN['count_rate'] >= 0.0003]
    countY_del.to_csv(tableSaveDirPath + '/words_norm_Y.csv', encoding='utf-8-sig')
    countN_del.to_csv(tableSaveDirPath + '/words_norm_N.csv', encoding='utf-8-sig')

    # 한 곳에서만 나타나는 단어
    countY_only = countY_del[~countY_del['word'].isin(countN_del['word'])]
    countN_only = countN_del[~countN_del['word'].isin(countY_del['word'])]
    print("1) 한 곳에서만 나타나는 단어 (unique)")
    print(countY_only)
    print(countN_only)

    # 동시에 나타나지만 빈도수 차이가 큰 단어
    merge_df = pd.merge(countY_del, countN_del, on='word', suffixes=('_Y', '_N'))
    merge_df['diff'] = merge_df['count_rate_Y'] - merge_df['count_rate_N']
    diff_df_Y = merge_df[merge_df['diff'] > 0.001][['word', 'frequency_Y', 'count_rate_Y']]
    diff_df_Y = diff_df_Y.rename(columns={'count_rate_Y': 'count_rate', 'frequency_Y':'frequency'})
    diff_df_N = merge_df[merge_df['diff'] < -0.001][['word', 'frequency_N', 'count_rate_N']]
    diff_df_N = diff_df_N.rename(columns={'count_rate_N': 'count_rate', 'frequency_N':'frequency'})
    print("2) 비율이 0.001보다 크게 차이나는 단어들")
    print(diff_df_Y)
    print(diff_df_N)

    # 1, 2번 함께 시각화
    visual_Y = pd.concat([countY_only, diff_df_Y], axis=0)
    visual_N = pd.concat([countN_only, diff_df_N], axis=0)
    # text_visualization(visual_Y)
    # text_visualization(visual_N)

    # 부정 단어 빈도 비교
    print("\n3) 부정 단어가 차지하는 비율")
    negative = ['실망', '후회', '최악', '별로']
    for word in negative :
        rowsY = countY_del.loc[countY_del['word'] == word]
        print("===== " + word + " : Y =====")
        if not rowsY.empty : print(rowsY)
        print("===== " + word + " : N =====")
        rowsN = countN_del.loc[countN_del['word'] == word]
        if not rowsN.empty : print(rowsN)

    # 이벤트 관련 단어 빈도 비교
    print("\n4) 리뷰 이벤트 관련 단어가 차지하는 비율")
    event = ['리뷰', '이벤트']
    for word in event:
        rowsY = countY_del.loc[countY_del['word'] == word]
        print("===== " + word + " : Y =====")
        if not rowsY.empty : print(rowsY)
        print("===== " + word + " : N =====")
        rowsN = countN_del.loc[countN_del['word'] == word]
        if not rowsN.empty : print(rowsN)

def score_and_rivew(df):
    # 3점 이하 / 3점 이상 데이터끼리 모아서 감성분석
    positive_df = df[df['totalRate'] > 3]
    analysis_text(positive_df, 'Positive')
    negative_df = df[df['totalRate'] < 3]
    analysis_text(negative_df, 'Negative')


def analysis() :
    df_Y, df_N, df = read_file()
    print("***** 리뷰이벤트를 진행하는 곳 *****")
    analysis_print(analysis_distribution(df_Y, 'Y'), analysis_aggregate(df_Y, 'Y'))
    countY = analysis_text(df_Y, 'Y')

    print("\n***** 리뷰이벤트를 진행하지 않는 곳 *****")
    analysis_print(analysis_distribution(df_N, 'N'), analysis_aggregate(df_N, 'N'))
    countF = analysis_text(df_N, 'N')

    print("\n***** 진행하는 곳과 진행하지 않는 곳의 텍스트 차이 *****")
    between_review(countY, countF)

    print("\n***** 별점(긍정/부정)에 따른 리뷰 텍스트 차이 *****")
    score_and_rivew(df)


analysis()