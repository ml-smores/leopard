__author__ = 'ugonzjo'

#2 hours for 500*20*500*10=10000*5000=50,000,000 rows

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.join(os.getcwd(), os.pardir), os.pardir)))
import random
import numpy as np
import pickle
import os.path
import pandas as pd
from  importer import Importer
from feature_extractor import *
pd.set_option('display.max_columns', 100)#510)
pd.set_option('display.width', 100)#1200)


class IntermediateData():
    input_path = "./data/"
    output_path="./intermediate/"

    def __init__(self, chapter, kc, df, train_rows, dev_rows, test_rows):
        self.chapter_id = chapter
        self.kc_id = kc
        self.df_features = df
        self.train_rows = train_rows
        self.dev_rows = dev_rows
        self.test_rows = test_rows

    @staticmethod
    def get_filename(kctype, kc):
        return kctype +  "_" + str(kc)

    @staticmethod
    def load(kc_id, kctype, index):
        path = os.path.join(IntermediateData.output_path, index, IntermediateData.get_filename(kctype, kc_id))
        try:
            f_output = open(path, "r")
            ans = pickle.load(f_output)
            f_output.close()
        except IOError:
            print "Can't load model ", path
            raise

        return ans


    @staticmethod
    def create(chapter_id, kctype, file_kcids=None, debug=False, train_pct= 0.6, dev_pct=0.2, index=""):
        file_name =  IntermediateData.input_path + "homework_xref_" + str(chapter_id) + "_decompressed.csv"

        print "CLEANING DATA..."
        imp = Importer()
        df_imp = imp.get_data(file_name, kctype, debug)


        kc_col = "kc"
        if kctype == "tom":
            kc_definition = [kc_col]
        else:
            #TODO:  We should extracting features from exercises, but feature extracting does not support this
            kc_definition = [kc_col] #",exercise_id]"

        # Sort data
        df_imp = FeatureExtractor.sort(df_imp)

        for kc in df_imp[kc_col].unique():
            print kc_col, kc

            # GET SUBSET of data
            df = df_imp[ df_imp[kc_col] == kc]

            # "EXTRACTING FEATURES..."
            fe = FeatureExtractor(default_kc=kc_definition)
            df_features = fe.df_to_features(df, sort_data=False) # No need to sort data

            # "SUBSET OF DATA..."
            df_train, df_dev, df_test = split(df_features, train_pct, dev_pct)

            # "STORING"
            chapter_data = IntermediateData(chapter_id, kc, df_features, train_rows=df_train, dev_rows=df_dev, test_rows=df_test)

            filename = os.path.join(IntermediateData.output_path, index, IntermediateData.get_filename(kctype, kc))
            f_output = open( filename, "w")
            pickle.dump(chapter_data, f_output)
            f_output.close()

            #hy commented
            #df_features.to_csv(filename + ".csv")

            if file_kcids != None:
                file_kcids.write( str(chapter_id)  +","+  str(kc) + "," + index + "\n")
                file_kcids.flush()








def split( df, train_pct= 0.6, dev_pct=0.2):

    #assert train_pct + dev_pct < 1, "Training and development set have to be (strictly) less than 100% of the students"

    students = df.user_id.unique()
    random.shuffle(students)

    train_number = int(train_pct * len(students))
    dev_number = int(dev_pct * len(students))

    train_students = students[0:train_number]
    dev_students = students[train_number: train_number+dev_number]
    test_students = students[train_number+dev_number : ]

    #print train_students, len(train_students)
    #print dev_students, len(dev_students)
    #print test_students, len(test_students)

    print "Students in training ", len(train_students), "dev", len(dev_students), " and test", len(test_students)

    df_train =  df.user_id.isin(train_students)
    df_dev   =  df.user_id.isin(dev_students)
    df_test  =  df.user_id.isin(test_students)

    return df_train, df_dev, df_test



def split_by_year(self, df):
    # Split into two sets (training and test) using year

    train =  df["handedin"].map(lambda x: x.year == 2013)
    return train, ~train

def main(debug=False, chapters=range(100, 101)): #[5]):
    random.seed(0)
    np.random.seed(0)


    file_kcids = open( os.path.join(IntermediateData.output_path, "identifiers_" + kctype +  ".txt"), "w")
    for chapter_id in chapters:
        print "-----------------"
        print kctype, chapter_id
        print "-----------------"
        IntermediateData.create(chapter_id, kctype, file_kcids, debug=debug)#, train_pct=1.0, dev_pct=0.0)






if __name__ == "__main__":
    import sys
    args = sys.argv
    print args
    cl = {}
    for i in range(1, len(args)): # index 0 is the filename
        pair  =  args[i].split('=')
        if pair[1].isdigit():
            cl[pair[0]] = int(pair[1])
        elif pair[1].lower() in ("true", "false"):
            cl[pair[0]] = (pair[1].lower() == 'true')
        else:
            cl[pair[0]] = pair[1]

    main(**cl)