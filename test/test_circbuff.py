
import random

l = [0] * 10

def add_to_buffer(val):
    l.pop(0)
    l.append(val)

while True:

    power_level = random.randint(0, 9)

    add_to_buffer(power_level)

    start = 0
    count = 0
    i = 0
    while i < len(l):
        i_start = i
        i_count = 0
        for j in range(i_start, len(l)):
            if l[j] > 0:
                i_count += 1
            else:
                break
        if i_count > count:
            start = i_start
            count = i_count
            i = i_start + i_count
        else:
            i += 1

        # comment this out to get biggest instead of first
        if count > 1:
            break

    # print(f"start: {start}")
    # print(f"count: {count}")

    stroke = l[start:start+count-1]
    # power_level = sum(stroke) / len(stroke)

    print(f"stroke: {stroke}")
    # print(f"power_level: {power_level}")
