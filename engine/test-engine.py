import sys

input_file = sys.argv[1]
check_status = sys.argv[2]

def test_func(input_thing, check_thing):
    listy = check_thing.split(",")
    listy_out = "start"
    for li in listy:
        listy_out = listy_out + " " + li
        #input_thing = len(check_thing)
    return listy_out

print(test_func(input_file, check_status))
sys.stdout.flush()