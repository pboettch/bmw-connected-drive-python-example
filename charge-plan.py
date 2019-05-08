#!/usr/bin/env python3

import argparse
from datetime import datetime, timedelta
import json

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def valid_date(s):
    try:
        return datetime.strptime(s, '%Y-%m-%d %H:%M')
    except ValueError:
        msg = 'Not a valid datetime: "{0}".'.format(s)
        raise argparse.ArgumentTypeError(msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-s', '--soc', help='current SoC', required=True, type=float)
    parser.add_argument('-t', '--target', help='target SoC', required=True, type=float)
    parser.add_argument('-d', '--departure', help='Departure time and date', required=True, type=valid_date)

    args = parser.parse_args()

    params = json.load(open('charge-plan.json', 'r'))

    # first calculate how many hours will be necessary to reach target SoC
    total_time = timedelta()

    lower_bound = 0
    for section in params['charging-efficiency']:

        section_capacity = (section['max'] - lower_bound) * params['capacity']
        section_time = section_capacity / (params['power'] * section['efficiency'])

        if args.soc < section['max']: # this section concerns the current charge-plan
            high = args.target
            if high > section['max']:
                high = section['max']

            low = args.soc
            if low < lower_bound:
                low = lower_bound

            part = high - low
            total = section['max'] - lower_bound
            ratio = part/total

            time = section_time * ratio

            total_time += timedelta(hours=time)

            # print(section_capacity, section_time, ratio, time)

        lower_bound = section['max']

    print("total charging time:", total_time)

    # off-peak times usable until departure
    now = datetime.now()

    periods = {}
    for date in daterange(datetime.now().date(), args.departure.date()):
        for period in params['hours']:
            begin = datetime.combine(date, datetime.strptime(period['begin'], '%H:%M').time())
            end = datetime.combine(date, datetime.strptime(period['end'], '%H:%M').time())

            # out of range
            if now > end:
                continue

            if begin > args.departure:
                break

            if end > args.departure:
                end = args.departure

            if datetime.now() > begin:
                begin = datetime.now();

            periods.setdefault(period['priority'], []).append({'begin': begin, 'end': end})

            #print(begin, end, period['priority'])

    used_periods = [] # [{'begin': datetime, 'end'}, ...]
    # chose timely closest and highest-priority periods
    for prio in reversed(sorted(periods.keys())):
        for period in periods[prio]:
            # duration
            duration = period['end'] - period['begin'] #.total_seconds() # /60/60
            if duration > total_time:
                duration = total_time

            used_periods.append([period['begin'], period['begin'] + duration])

            total_time -= duration
            if total_time <= timedelta(hours=0):
                break

        if total_time <= timedelta(hours=0):
            break

    for p in used_periods:
        print(p)


# find on/off off/on transitions

