__author__ = 'ugonzjo'


import re

from Activity import Activity
# from als.models import Exercise
# from als.models import DBSession
# from als.util.common import *
import math
import numpy as np
import matplotlib.pylab as pl


class Feature:
    def __init__(self, column_name, shifted, cumulative):
        self.column_name = column_name
        self.shifted = shifted
        self.cumulative = cumulative


class FeatureExtractor:
    default_kcs = ["kc"]
    PRIOR_PSEUDOCOUNTS = 19
    default_sort_order = ["user_id", "kc", "handedin", "xml_qno" ]

    def __init__(self, default_kc=default_kcs, debug=False):
        self.debug=debug
        # Define Knowledge Components:
        self.default_kcs = default_kc
        #Features to extract:
        self.features = [Feature("got_wrong", True, True),
                         Feature("got_correct",True, True),
                         Feature("po", True, True),
                         Feature("last_correct", True, False),
                         Feature("dummy", False, False)]
        # Convenience variables / legacy variables:
        self.template_features  = [x.column_name for x in self.features]

        self.shifted_features   = [x.column_name for x in self.features if x.shifted]
        self.cum_features       = [x.column_name for x in self.features if x.cumulative]
        self.fixed_features     = [x.column_name for x in self.features if not x.cumulative]

    def df_to_features(self, df,  shifting=False, debug_kcs=None, sort_data=True): #["160", "113"]
        """ Extracts features suitable to model student learning
            Args:
                df (DataFrame): A pandas data frame of the log of student activities.  This assumes that the data has been cleaned by importer.py and sorted in sort_order. It expects an index on user_id, self.kcs[0], id columns.
                shifting (boolean, optional): Shifting allows multiple KCs, but it' slower.  If not it uses a heuristic that is faster, but allows only a single kc
                debug_kcs (list, optional): If a list of KC identifiers is specified, a subset of the data will be printed to the screen
            Returns: Creates a design matrix suitable for a logistic regression.  Columns created follow the pattern:
            [KC_COLUMN]_[KC_ID]_[FEATURE_NAME]. For example:
            [KC_COLUMN]_[KC_ID]_got_correct: number of previous correct attempts
            [KC_COLUMN]_[KC_ID]_got_wrong: number of previous incorrect attempts
            [KC_COLUMN]_[KC_ID]_po:  practice opportunities
        """
        if shifting == False:
            assert(len(FeatureExtractor.default_kcs) == 1), "Heuristic will not work with multiple KCs"

        assert len(self.default_kcs) == 1, "Code has bugs for  multiple KCs... Need to debug"

        if sort_data:
            df = FeatureExtractor.sort(df, self.default_sort_order)

        # Create helpful columns:
        df_features = df

        self.debug_msg( df_features.head(10) )
        df_features['outcome']      = df_features['got_correct']
        df_features['last_correct'] = df_features['got_correct']
        df_features['got_wrong']    = (df_features['got_correct'] == 0).astype(int)
        df_features['dummy'] = 1
        df_features['po']    = 1

        for kc in self.default_kcs:  # Not sure if this for loop is needed
            # Get a column for each KC:
            df_features = df_features.reset_index().set_index(["user_id", kc, "id"])
            self.debug_msg( "Unstacking...")
            df_kc = df_features[self.template_features ].unstack(kc).fillna(0)
            # Rename hierarchical index:
            df_kc.columns = [FeatureExtractor.get_feature_name(kc, c[1], c[0]) for c in df_kc.columns]
            # Re-add kc column:
            self.debug_msg( "Adding column...")
            df_kc[kc] = df_features.index.get_level_values(kc)
            df_kc = df_kc.set_index(kc, append=True)

            # Get column names:
            kc_ids = df_features.index.get_level_values(kc).unique()
            shifted_columns = self.get_columns_for_id(kc,kc_ids, self.shifted_features )
            cum_columns = self.get_columns_for_id(kc,kc_ids, self.cum_features )
            fixed_columns = self.get_columns_for_id(kc,kc_ids, self.fixed_features )

            # Create columns:
            df_kc = df_kc.reset_index()

            if shifting:
                df_kc["ukc"] = df_kc["user_id"].apply(intstr) +"|" + df_kc[kc]
                group_columns = ["ukc"] #["user_id", kc]
            else:
                group_columns = ["user_id"]

            self.debug_msg( "Shifting rows...")
            df_shifted =  df_kc.groupby(by=group_columns, sort=False)[shifted_columns].shift(1)
            df_shifted[group_columns] = df_kc.loc[:, group_columns] # !!!! This is a bug fix
            self.debug_msg( "Cumulative sums...")
            df_shifted[cum_columns] = df_shifted[cum_columns].fillna(0).astype(np.uint8)
            df_cumsum  = df_shifted.groupby(by=group_columns, sort=False)[cum_columns].cumsum()


            df_kc[shifted_columns] = df_shifted[shifted_columns]
            df_kc[cum_columns]     = df_cumsum[cum_columns].fillna(0).astype(np.uint8)
            df_kc[fixed_columns]   = df_kc[fixed_columns].fillna(0).astype(np.uint8)

            # Join the good stuff:

            #TODO fix:
            self.debug_msg( "Building final answer...")
            df_features = df_features.reset_index().set_index("id").join(df_kc.set_index("id") [cum_columns + fixed_columns]   )

        if debug_kcs != None:
            a = df_features[ df_features[kc].isin( debug_kcs)] #df_features.index.get_level_values(kc) == "113"]
            #a = a.reset_index().sort(columns=["user_id",  "kc", "handedin", "xml_qno"])
            columns =    ["user_id", "handedin", "xml_qno", "objective_id", kc, "outcome"]
            for c in df_features.columns:
                if any([ (debug_kc in c) for debug_kc in debug_kcs ]):
                    columns.append(c)
            print columns

            print df_features.columns
            print a[ columns ].head(100)
            print time(), "exiting because of debugging"


            exit(-1)

        df_features.drop(['last_correct', 'got_wrong', 'got_correct','dummy', 'po'], inplace=True, axis=1)
        self.debug_msg(df_features.head(10))
        return df_features.reset_index()


    @staticmethod
    def sort(df, columns=default_sort_order):
        print df
        return df.sort(columns)

    @staticmethod
    def get_batting_rate(df_features):
        return df_features

    @staticmethod
    def get_batting_rate_experimental(df_features):
        exkey = ["chapter_id", "section_id", "objective_id", "exercise_id"]
        irt = pd.read_csv("data/tdx_profiles.csv")

        df_features = df_features.merge(irt[exkey + ["irtDiff"] ], on=exkey, how="left")
        df_features = df_features.sort(columns=FeatureExtractor.default_sort_order)



        # Correct = +1, Wrong = -1
        df_features["correct"] = df_features["got_correct"]
        df_features.loc[df_features["correct"] == 0, "correct"] = -1

        # Group by user
        user_group = df_features.set_index(["id", "user_id"]).groupby(level=["user_id"], sort=False)

        # Rolling (expanding) average and count:
        df = pd.DataFrame()
        df["exp_count"] = user_group["correct"].apply(pd.expanding_count)
        df["exp_mean"]  = user_group["correct"].apply(pd.expanding_mean)
        df["exp_std"]  = user_group["correct"].apply(pd.expanding_std)

        #df = df.groupby(level=["user_id", "handedin"]).last()  # Consider by homework average

        # Avoid looking into the future:
        df = df.groupby(level=["user_id"]).shift().fillna(0)

        # Smooth 'batting average' by adding pseudo observations:
        df["batting"] = (df["exp_mean"] * df["exp_count"]) / (df["exp_count"] + FeatureExtractor.PRIOR_PSEUDOCOUNTS)

        #df_features["batting"] = df.reset_index()["batting"] #Should have merged? it looks like it' slower and equivalent

        df_features.drop("correct", axis=1, inplace=True)
        df_features =  df_features.set_index("id").join(df.reset_index().set_index("id")[ ["exp_count", "exp_mean", "exp_std", "batting"]])

        print df_features
        exit(-1)
        return df_features





    def debug_msg(self, message):
        if self.debug:
            print time(), message



    def df_to_features_old(self, df,  debug_obj=""):  # 2.4
        df = df.reset_index()
        # Create helpful columns:
        df['outcome'] = df['got_correct']
        df['got_wrong'] = (df['got_correct'] == 0).astype(int)
        df['dummy'] = 1
        df['po'] = 1

        # Get a column for each KC:
        df = df.set_index(["user_id", "id"])

        df_features = df
        all_slope_columns = []
        all_dummy_columns = []
        for kc in self.default_kcs:  # Not sure if this for loop is needed
            # Get a column for each KC:
            df_kc = df.set_index(keys=kc, append=True)
            df_kc = df_kc[self.template_features + ['dummy']].unstack(kc).fillna(0)
            # Rename hierarchical index
            df_kc.columns = [FeatureExtractor.get_feature_name(kc, c[1], c[0]) for c in df_kc.columns]

            # Create dummy features:
            kc_dummy_columns = [
                c for c in df_kc.columns if any((s in c) for s in ['dummy'])]
            df_kc[kc_dummy_columns] = df_kc[kc_dummy_columns].fillna(0).astype(np.int8)

            # Calculate slope features:
            cumsum = df_kc.groupby(level=["user_id"], sort=False).cumsum().groupby(level=["user_id"], sort=False).shift(1).fillna(0)

            kc_slope_columns = []
            for k in df[kc].unique():
                dummy = kc + "_" + str(k) + "_dummy"
                slopes = self.get_columns_for_id(kc, k)

                df_kc[slopes] = cumsum[slopes].astype(np.int32)

                #print df_kc

                df_kc.loc[df_kc[dummy] == 0, slopes] = 0
                kc_slope_columns += slopes

            # Concatenate the good stuff:
            df_features = df_features.join(df_kc)
            all_slope_columns += kc_slope_columns
            all_dummy_columns += kc_dummy_columns

        if debug_obj != "":
            print df_features.columns
            a = df_features[ df_features[kc] == debug_obj]
            a = a.reset_index().sort(columns=["user_id",  kc, "handedin", "xml_qno"])
            columns =  ["user_id", "handedin", "xml_qno", "objective_id", "outcome"]
            for c in df_features.columns:
                if debug_obj in c:
                    columns.append(c)
            print columns

            print a[ columns ].head(100)
            exit(-1)

        return df_features.reset_index(), all_slope_columns, all_dummy_columns


    def get_columns_for_id(self, kc_column, ids, templates=None):
        if templates == None:
            templates = self.template_features
        if  not isinstance(ids, (np.ndarray, np.generic, list) ):
            ids = [ids]

        if kc_column not in self.default_kcs:
            raise RuntimeError("KC not defined")

        ans = []
        for kc_id in ids:
            ans += [FeatureExtractor.get_feature_name(kc_column, kc_id,  type) for type in templates]

        return ans

    @staticmethod
    def get_feature_name(kc, number, template_type):
        return kc + "_" + str(number) + "_" + template_type

    def activitylist_to_features(self, activitylist, activity_df=Activity.get_empty_dataframe(), starting_id=0):
        #activity_df.set_index(["user_id",FeatureExtractor.default_kcs[0],  "id"])
        for i, act in enumerate(activitylist):
            activity_df = activity_df.append(
                {Activity.id.name: starting_id + i,
                 Activity.handedin.name: act.handedin,
                 Activity.xml_qno.name: act.xml_qno,
                 Activity.user_id.name: act.user_id,
                 Activity.chapter_id.name: act.chapter_id,
                 Activity.section_id.name: act.section_id,
                 Activity.objective_id.name: act.objective_id,
                 Activity.exercise_id.name: act.exercise_id,
                 Activity.got_correct.name: act.got_correct,
                 Activity.kc.name: act.kc,
                 }, ignore_index=True)

        #activity_df = activity_df.set_index([ "user_id", FeatureExtractor.default_kcs[0], "id"])
        df_features = self.df_to_features(activity_df)

        return df_features
