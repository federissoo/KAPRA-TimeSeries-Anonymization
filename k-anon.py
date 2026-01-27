

# Implement a function to check if dataset D is k-anonymous
# according to the list of QI
'''
name -> EI
age, nationality -> QI
salary -> SD
[
    {"name": "matt", "age": 23, "nationality": "italy", "salary": 10000},
    {"name": "david", "age": 21, "nationality": "canadian", "salary": 12000},
    {"name": "bob", "age": 20, "nationality": "usa", "salary": 7123},
]

groups:
    [23, italy]
    [21, canadian]
    [20, usa]
'''


from generate import generateRandom


def isKAnon(dataset, k, QI):

    # print("--------------")
    # print("isKAnon", k, QI)
    kanon = False

    '''
        gruop dataset according to the values of QI
        find the size of each group
        k = min(size of each group)
    '''
    groups = {}

    # split dataset in groups
    for d in dataset:

        # Find the group in which put the entry d
        key = []
        for qi in QI:
            key.append(str(d[qi]))

        key = "-".join(key)

        # If the entry d is the first one of the group
        # create a new empty group
        if key not in groups:
            groups[key] = []

        # append the entry d inside the existing group
        groups[key].append(d)

    '''
        group 1: of size 3
        group 2: of size 5
        group 3: of size 4

        => 3-anonymous
    '''
    kdataset = len(dataset)
    for group in groups:
        #  print("\t", "group", group, len(groups[group]))
        kdataset = min(len(groups[group]), kdataset)

    if kdataset >= k:
        kanon = True
    # True is dataset is k-anonymous
    # False is dataset is NOT k-anonymous
    return kanon


def findK2(dataset, QI):
    groups = {}
    for d in dataset:
        key = []
        for qi in QI:
            key.append(str(d[qi]))
        key = "-".join(key)
        if key not in groups:
            groups[key] = []
        groups[key].append(d)
    return min(len(groups[group]) for group in groups)


'''
if dataset is 7-anonymous

isKAnon(dataset, 4, QI) -> true
isKAnon(dataset, 5, QI) -> true
isKAnon(dataset, 6, QI) -> true
isKAnon(dataset, 7, QI) -> true
isKAnon(dataset, 8, QI) -> false
'''


def findK(dataset, QI):
    for k in range(2, len(dataset)+1):
        if not isKAnon(dataset, k, QI):
            return k-1


dataset = [

    # 3 diverse group (10000, 1300, 10400)
    {"name": "matt", "age": 23, "nationality": "genoa", "salary": 10000},
    {"name": "alice", "age": 23, "nationality": "genoa", "salary": 10400},
    {"name": "david", "age": 23, "nationality": "genoa", "salary": 1300},
    {"name": "greg", "age": 23, "nationality": "genoa", "salary": 10400},
    {"name": "george", "age": 23, "nationality": "genoa", "salary": 1300},

    # 3 diverse group (12400, 52000, 15000)
    {"name": "david", "age": 21, "nationality": "torino", "salary": 12400},
    {"name": "mark", "age": 21, "nationality": "torino", "salary": 12400},
    {"name": "george", "age": 21, "nationality": "torino", "salary": 52000},
    {"name": "alice", "age": 21, "nationality": "torino", "salary": 15000},

    # 3 diverse group (71342, 712, 12345)
    {"name": "joe", "age": 21, "nationality": "milano", "salary": 71342},
    {"name": "john", "age": 21, "nationality": "milano", "salary": 712},
    {"name": "jack", "age": 21, "nationality": "milano", "salary": 12345},
    {"name": "michael", "age": 21, "nationality": "milano", "salary": 71342},
    {"name": "david", "age": 21, "nationality": "milano", "salary": 712},

    # new record added after
    {"name": "luigi", "age": 30, "nationality": "estonia", "salary": 1234}
]

# before adding one random record
# 4-anonymous
# 3-diverse

# after adding one random record
# 1-anonymous
# 1-diverse

print("Dataset is 1-anonymous? ", isKAnon(dataset, 1, ["age", "nationality"]))
print("Dataset is 2-anonymous? ", isKAnon(dataset, 2, ["age", "nationality"]))
print("Dataset is 3-anonymous? ", isKAnon(dataset, 3, ["age", "nationality"]))
print("Dataset is 4-anonymous? ", isKAnon(dataset, 4, ["age", "nationality"]))
print("Dataset is 5-anonymous? ", isKAnon(dataset, 5, ["age", "nationality"]))


print("Dataset is", findK(dataset, ["age", "nationality"]), "anonymous")
print("Dataset is", findK2(dataset, ["age", "nationality"]), "anonymous")

print("Dataset is", findK2(dataset, ["age"]), "anonymous")


'''
geographical data:
- list of cities, regions, countries, continents, ...

numbers:
- suppress the last n digits

ages:
- suppress day, month, year, decade, centuries, ...
'''


def generalizeNumber(value, level):
    '''
    0->123456
    1->123450
    2->123400
    3->123000
    4->120000
    5->100000
    6->000000
    7->000000
    '''
    value = str(value)
    level = min(level, len(value))  # cap the level to the number of digits
    length = len(value)
    value = value[:length-level] + "0" * (level)
    return value


'''
number = [1234]56
length = 6
level = 2
'''

# mapping to point -> parent
cities = {
    "genoa": "liguria",
    "savona": "liguria",
    "imperia": "liguria",
    "la spezia": "liguria",
    "milano": "lombardia",
    "crema": "lombardia",
    "bergamo": "lombardia",
    "torino": "piemonte",
    "liguria": "italy",
    "lombardia": "italy",
    "piemonte": "italy",
    "italy": "europe",
    "europe": "world",
    "world": "world"
}


def generalizeCategorical(value, level, mapping):
    for _ in range(level):
        # print("GENERALIZE", value, "->", mapping[value])
        value = mapping[value]
    return value


print("Generalize 0-time 123456:", generalizeNumber(123456, 0))
print("Generalize 1-time 123456:", generalizeNumber(123456, 1))
print("Generalize 2-time 123456:", generalizeNumber(123456, 2))
print("Generalize 3-time 123456:", generalizeNumber(123456, 3))
print("Generalize 4-time 123456:", generalizeNumber(123456, 4))
print("Generalize 5-time 123456:", generalizeNumber(123456, 5))
print("Generalize 6-time 123456:", generalizeNumber(123456, 6))
print("Generalize 7-time 123456:", generalizeNumber(123456, 7))


print("Generalize 0-time genoa", generalizeCategorical("genoa", 0, cities))
print("Generalize 1-time genoa", generalizeCategorical("genoa", 1, cities))
print("Generalize 2-time genoa", generalizeCategorical("genoa", 2, cities))
print("Generalize 3-time genoa", generalizeCategorical("genoa", 3, cities))
print("Generalize 4-time genoa", generalizeCategorical("genoa", 4, cities))
print("Generalize 5-time genoa", generalizeCategorical("genoa", 5, cities))

print("Generalize 0-time milano", generalizeCategorical("milano", 0, cities))
print("Generalize 1-time milano", generalizeCategorical("milano", 1, cities))
print("Generalize 2-time milano", generalizeCategorical("milano", 2, cities))
print("Generalize 3-time milano", generalizeCategorical("milano", 3, cities))
print("Generalize 4-time milano", generalizeCategorical("milano", 4, cities))
print("Generalize 5-time milano", generalizeCategorical("milano", 5, cities))


# Implement a bruteforce algorithm to make a dataset k-anonymous

# dataset = ["name", "nationality", "age", "salary"]
# EI = ["name"]
# QI = ["nationality", "age"]
# age -> 31
# 0-level generalization age -> 31
# 1-level generalization age -> 30
# 2-level generalization age -> 00
# nationality
# 0-level generalization nationality -> genoa
# 1-level generalization nationality -> liguria
# 2-level generalization nationality -> italy
# 3-level generalization nationality -> europe
# 4-level generalization nationality -> world
'''
age         -> 3 level of generalization
nationality -> 5 level of generalization
(age, nationality) -> 15 level of generalization
'''
# SD = ["salary"]


def makeDatasetKAnon(dataset, k, QI):

    best_generalization = None

    def generalize(dataset, generalization=[0, 0]):
        '''
        take in input the original dataset and the number of generalization for all the attributes
        return
        a new dataset with the generalized QI
        '''
        dataset_new = []
        for entry in dataset:
            # anonymized entry in the dataset
            anon_entry = {}
            for attr in entry:
                if attr == "age":
                    anon_entry[attr] = generalizeNumber(
                        entry[attr], generalization[0])
                elif attr == "nationality":
                    anon_entry[attr] = generalizeCategorical(
                        entry[attr], generalization[1], cities)
                else:
                    anon_entry[attr] = entry[attr]
            dataset_new.append(anon_entry)
        return dataset_new

    for age_generalization in range(3):
        for nationality_generalization in range(5):

            option = (age_generalization, nationality_generalization)
            dataset_anon = generalize(dataset, option)
            # find anonimized dataset
            dataset_anon_k = findK2(dataset_anon, ["age", "nationality"])
            if dataset_anon_k >= k:
                # valid option
                # Select the "best" generalization
                # Where "best" = minimum amount of generalization applied
                if best_generalization is None or sum(option) < sum(best_generalization):
                    best_generalization = option

                '''
                (0,0) <- 0 times age, 0 times nationality
                ...
                (1, 3)                                      (4 times in total)
                (2, 1)                                      (3 times in total)
                (2, 4) <- 2 times age, 4 times nationality. (6 times in total)
                '''

    # I was not able to reach the k-anonymous level by applying all the possible combination
    if best_generalization is None:
        '''
        this happens only if len(dataset) < K

        if I suppress (generalize at maximum) al the QI in the dataset
        I make the dataset len(dataset)-anonymous
        '''
        return None

    anon_dataset = generalize(dataset, best_generalization)

    return anon_dataset
    '''
    input:
    - original dataset
    - k: level of anonymization to reach
    - QI: array of quasi identifiers

    output:
    - k-anonymous dataset with higher utility
    '''

    '''
        best_generalization = [0, 0, 0, 0, 0]

        for combination in **all the possibile QI generalization*
            anonDataset = apply combination of dataset
            check the level of K
            if combination is better than best_generalization
                best_generalization = combination
    '''


dataset_fake = generateRandom(1000)
dataset_fake_anon = makeDatasetKAnon(dataset_fake, 10, ["nationality", "age"])

print("dataset_fake is ", findK2(
    dataset_fake, ["nationality", "age"]), "anonymous")
# print(isKAnon(dataset_fake, 10, ["nationality", "age"]))
print("dataset_fake_anon is ", findK2(
    dataset_fake_anon, ["nationality", "age"]), "anonymous")


# return True if dataset is l-diverse according to QI and SD
# return False is dataset is not l-diverse according to QI and SD
def isLDiverse(dataset, l, QI, SD):
    ldiverse = False

    # Create the blocks with the same QI
    groups = {}
    for d in dataset:
        key = []
        for qi in QI:
            key.append(str(d[qi]))
        key = "-".join(key)
        if key not in groups:
            groups[key] = []
        groups[key].append(d)

    # check the diversity for each group
    # count the number of different SD in each group
    # choose the smallest (fewer diverse) group
    smallest_diverse = len(dataset)

    for group in groups:
        sensitive_data = set()

        # Iterate over all the record in the group
        for record in groups[group]:
            record_sd = []
            # Iterate over all the SD attributes
            # Create a subset with only the SD
            for sd in SD:
                record_sd.append(str(record[sd]))
            record_sd = "-".join(record_sd)

            sensitive_data.add(record_sd)

        if len(sensitive_data) < smallest_diverse:
            smallest_diverse = len(sensitive_data)

    if smallest_diverse >= l:
        ldiverse = True
    return ldiverse


def findLDiverse(dataset, QI, SD):
    # Find in one step the maximum level of l-diversity of dataset

    # Create the blocks with the same QI
    groups = {}
    for d in dataset:
        key = []
        for qi in QI:
            key.append(str(d[qi]))
        key = "-".join(key)
        if key not in groups:
            groups[key] = []
        groups[key].append(d)

    # check the diversity for each group
    # count the number of different SD in each group
    # choose the smallest (fewer diverse) group
    smallest_diverse = len(dataset)

    for group in groups:
        sensitive_data = set()

        # Iterate over all the record in the group
        for record in groups[group]:
            record_sd = []
            # Iterate over all the SD attributes
            # Create a subset with only the SD
            for sd in SD:
                record_sd.append(str(record[sd]))
            record_sd = "-".join(record_sd)

            sensitive_data.add(record_sd)

        if len(sensitive_data) < smallest_diverse:
            smallest_diverse = len(sensitive_data)

    return smallest_diverse


print("DATASET is 1-diverse: ", isLDiverse(dataset,
      1, ["age", "nationality"], ["salary"]))
print("DATASET is 2-diverse: ", isLDiverse(dataset,
      2, ["age", "nationality"], ["salary"]))
print("DATASET is 3-diverse: ", isLDiverse(dataset,
      3, ["age", "nationality"], ["salary"]))
print("DATASET is 4-diverse: ", isLDiverse(dataset,
                                           4, ["age", "nationality"], ["salary"]))

print("DATASET is", findLDiverse(dataset,
      ["age", "nationality"], ["salary"]), "diverse")


''''
if dataset t is 4-diverse

t is NOT  5-diverse
t is      4-diverse
t is also 3-diverse
t is also 2-diverse
t is also 1-dverse
'''


'''

dataset
40% age > 50

group 1
35% age > 50 (5% difference)

group 2
43% age > 50 (3% difference)

group 3
41% age > 50 (1% difference)


global probability = 40%
local probabilities = 35%, 43%, 41%

dataset is 5% (or 6%, or 7%, or ...) t-closeness
dataset is NOT 1%, 2%, 3%, 4% t-closeness

0-closeness -> global distribution = local distribution

k-anonymity
l-diverse
t-closeness
'''
