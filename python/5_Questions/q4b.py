def trim_whitespace(string_list):
    return list(x.strip() for x in string_list)

test_list = ["Hi        ", "hello   ", "    testing \n", "  Cool"]
print(test_list)
print(trim_whitespace(test_list))