import random

input_list = ['file_1', 'file_2']

print(input_list)

def select_delete_random_item_from_list(input_list):
    index = random.randint(0, len(input_list) - 1)
    item = input_list[index]
    del input_list[index]
    return item

print(select_delete_random_item_from_list(input_list))

print(input_list)