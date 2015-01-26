__author__ = 'ugonzjo'

import numpy as np

from experiments.common import *
from Activity import *


class KCType:
    TDX = "tdx"
    TOM = "tom"
    OBJ = "obj"

    values =  [TDX, OBJ, TOM]

class Importer():
    def __init__(self, kc_model="./data/kc_model.csv"):
        self.kc_model= kc_model



    def get_data(self, filename, kc_type, debug=False, return_subset=True):

        if kc_type not in KCType.values:
            raise ReferenceError("Invalid Knowledge Component Definition")

        print time(), "Reading CSV file..."
        nrows= None
        if debug:
            print "****DEBUG CODE NOT USING ALL DATA!!****"
            nrows = 200000
        df = pd.read_csv(filename, nrows=nrows, dtype={"chapter_id": np.uint16,  "section_id": np.uint8,  "xml_qno": np.uint16, "objective_id": np.uint16,  "exercise_id": np.uint16, "user_id": np.uint32})

        print time(), "Getting qmatrix..."
        qmatrix = self.get_item_to_skill()

        print time(), "Joining dataframes..."

        df = df.merge(qmatrix, how='left', on=["chapter_id", "section_id", "objective_id", "exercise_id"])

        print "# of observations before cleaning", len(df)

        print time(), "Cleaning..."
        # 1. Users that only looked at the item but didn' attempt it
        print time(), "1/11"
        df = df.dropna(subset=["xml_correct_first"], inplace=False)
        # 2. Users that are teachers
        print time(), "2/11"
        df = df[df["isTeacher"] == 0]
        # 3. Users that didn't submit the item (similar to 1)
        print time(), "3/11"
        df = df[ df["xml_state"]  == "complete"]
        # 4. Data inconsistencies
        print time(), "4/11"
        df = df[ df["numberCorrect"] <= df["numberAttempts" ]]
        # 5. Filter observations that were not worked for enough time
        print time(), "5/11"
        df = df[ df["duration"] > 3]
        # 6. Use latest year
        print time(), "6/11 Only observations after a specific date"
        df = df[df["handedin"].map(lambda x: x[0:4]) == "2013"]
        #df["handedin"] = pd.to_datetime(df["handedin"])
        #df = df[df["handedin"]  > datetime.datetime(2012, 8,1) ]

        #7 Missing column?
        print time(), "7/11 Creating KC column"

        if kc_type == KCType.OBJ:
            df["kc"] = df["chapter_id"].astype(str) + "." + df["section_id"].astype(str) + "." + df["objective_id"].astype(str)
        elif kc_type == KCType.TOM:
            df["kc"] = df["factor_id"]
        elif kc_type == KCType.TDX:
            df["kc"] = df["chapter_id"].astype(str) + "." + df["section_id"].astype(str) + "." + df["objective_id"].astype(str) + "." + df["exercise_id"].astype(str)
            if "ex_idalias" in df.columns.values.tolist():
                df["kc"] = df["kc"] + "_" +  df["ex_idalias"].astype(str)


        # 8. Drop observations with no kc
        print time(), "8/11 Drop items with no KCs"
        if kc_type == KCType.TOM:
            kc_missing = df["kc"].apply(np.isnan)
            #example =  kc_missing[ ["chapter_id", "section_id", "exercise_id"], kc_missing].unique()
            print "Dropping ", sum(kc_missing), "observations with no KC"
            df = df[~kc_missing]
            df["kc"] = df["kc"].apply(intstr)


        #print time(), "9/11 Removing bad apples"
        #df["badapple"] = df["badapple"].fillna(False)
        #df = df[ df["badapple"] == False ]

        # 7. Remove students with too few observations
        # limit = 15
        # print time(), "11/12 Removing students with  fewer than", limit ,"observations"
        # users = df.groupby("user_id", sort=False)
        #user_counts = users["user_id"].count()

        #limit = user_counts.quantile(0.25)
        #print user_counts.describe()
        #print time(), "Removing observations on the bottom percentile", limit
        #df =  users.filter(lambda x : len(x) > limit)

        print time(), "# of observations after cleaning", len(df)

        df["id"] = range(0, len(df))
        df.set_index("id")

        df["got_correct"] = df["xml_correct_first"].astype(np.int8)

        if return_subset:
            return df.reset_index()[ [x.name for x in Activity.get_columns()] ]
        else:
            return df.reset_index()







    def get_item_to_skill(self):
        cols = ["chapter_id", "section_id", "objective_id", "exercise_id", "badapple","factor_id" ]
        try:
            qmatrix  = pd.read_csv(self.kc_model)
            qmatrix  = qmatrix[ cols ]

            qmatrix["factor_id"] = qmatrix["factor_id"].astype(np.int16)
            return qmatrix
        except IOError:
            print "NO QMATRIX FOUND"
            empty = pd.DataFrame(dict(zip(cols, [[] for i in range(0, len(cols))  ])))
            return empty





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




