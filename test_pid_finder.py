import pid_finder


browsers = ['Chrome', 'Firefox', 'Ie']
for b in browsers:
    print(
        pid_finder.get_all_pids(b)
    )
