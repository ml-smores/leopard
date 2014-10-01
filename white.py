

def main(filename):
    ___


class white:
           aggregation_types = [ "weighted" ]
           policies = ["single_kc"]

	def __init__(self, df):
""" df has a column for student, kc, timestep, p(correct) """
 	     self.grades = {}
                self.practices = {}
                self.thresholds ={}
                self.students = {}
	    self.df = df

	@staticmethod
def expected_grade(df_kc, threshold):
   ____

@staticmethod
def expected_practice(df_kc, threshold):

    ___

           def get_thresholds(df):
   do_something_with(df)
  if 0 not in self.thresholds:
        self.thresholds = [0] + self.thresholds
   if 1 not in self.thresholds:
        self.thresholds = self.thresholds + [1]

def calculate(self, policy):
   assert policy in policies, " We only support " + list(policies)
    self.grades = {}
   self.practices = {}
   self.students = {}

kcs = df["kc"].unique()
  for kc in kcs:
           df_kc = df[  df["kc"] == kc ]
            kc_thresholds = get_thresholds(df_kc)
	previous_grade = 0
previous_practice = 0
kc_grades = []
kc_practices = []
kc_students = []
  	for threshold in thresholds:
           		kc_grades.append(  max( expected_grade(threshold, df_kc), previous_grade )    )
		kc_practices.append(  max( expected_practice(threshold, df_kc), previous_practice))
		kc_students.append(  # of students that reach this threshold )
	self.expected_grades[kc] = kc_grades
self.expected_practices[kc] = kc_practices
self.students[kc] = kc_students





# explore how to divide



def aggregate(self, type):
     assert type in aggregation_types, "Unknown parameter"
    do something



class white_visualization()

         def __init__(self, white_obj)



def graph_curve(self)


def graph_path(self, filename, threshold=None)
'''" this should save the image to file """

   if threshold == None:
       #draw path for aggregated
  else:
       #draw a single path




