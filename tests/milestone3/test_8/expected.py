def slice_me():
    hour = 0
    german_greetings = ['Guten Morgen', 'Guten Tag', 'Guten Abend', 'Gute Nacht']
    while hour < 24:
        if hour < 12:
            greeting = german_greetings[0]
            return greeting # slicing criterion

slice_me()
