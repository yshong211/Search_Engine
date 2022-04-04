import json

def load_indexes(): # load the index into a dict
    with open('indexes_test_ver2_1.json', 'r') as j:
        dict_index = json.load(j)
    with open('indexes_test_ver2_2.json', 'r') as b:
        update_dict(dict_index, json.load(b))
    with open('indexes_test_ver2_3.json', 'r') as c:
        update_dict(dict_index, json.load(c))
    return dict_index

def update_dict(dict1, dict2):
    for k, sub_dict in dict2.items():
        if k in dict1:
            dict1[k].update(sub_dict)
        else:
            dict1[k] = sub_dict
    return dict1

def split_dict(dict_index):
    dict_numbers = dict()
    lst_dict = []
    for i in range(26):
        lst_dict.append(dict())
    for k, val in dict_index.items():
        if ord(k[0]) >= 48 and ord(k[0]) <= 57:
            # number
            dict_numbers[k] = val
        elif ord(k[0]) >= 97 and ord(k[0]) <= 97+26:
            print(ord(k[0]))
            lst_dict[ord(k[0]) - 97][k] = val
    with open('index_number.json', 'w') as j:
        json.dump(dict_numbers, j)
    for i in range(13):
        with open('index_'+str(i)+'.json', 'w') as j:
            json.dump(lst_dict[i], j)


if __name__ == '__main__':
    split_dict(load_indexes())
