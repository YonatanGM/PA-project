def slice_me():
    ages = [0, 25, 50, 75, 100, 150]
    current_age = ages[0]
    while current_age < ages[-1]:
        current_age += 1
    if current_age == ages[-1]:
        ages[-1] += 50       
    return ages # slicing criterion

slice_me()