import os
import pandas as pd

def combine_each() :
    read_folder_path = '../data/preprocessing'
    fileList_Y = [ f for f in os.listdir(read_folder_path) if f.endswith('_Y.csv')]
    fileList_N = [ f for f in os.listdir(read_folder_path) if f.endswith('_N.csv')]

    combined_Y = pd.concat([pd.read_csv(os.path.join(read_folder_path, f)) for f in fileList_Y])
    combined_N = pd.concat([pd.read_csv(os.path.join(read_folder_path, f)) for f in fileList_N])

    combined_Y.to_csv("../data/dataset/dataset_Y.csv", encoding='utf-8-sig')
    combined_N.to_csv("../data/dataset/dataset_N.csv", encoding='utf-8-sig')

def combine_all() :
    read_folder_path = '../data/dataset'
    fileList = [f for f in os.listdir(read_folder_path) if f.startswith('dataset_')]
    combined = pd.concat([pd.read_csv(os.path.join(read_folder_path, f)) for f in fileList])
    combined.to_csv("../data/dataset/dataset_All.csv", encoding='utf-8-sig')

# combine_each()
combine_all()