#!/usr/bin/env python3

import argparse
from datetime import datetime
import json

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

    needed_hours = 0

    total_soc = args.target - args.soc + 1

    for section in params['charging-efficiency']:
        section_capacity = (section['range'][1] - section['range'][0]) * params['capacity']
        section_time = section_capacity / (params['power'] * section['efficiency'])

        if args.soc < section['range'][1]:
            rhs = args.target
            if rhs > section['range'][1]:
                rhs = section['range'][1]

            lhs = args.soc
            if lhs < section['range'][0]:
                lhs = section['range'][0]


            print(section_capacity, section_time, lhs, rhs)



    print(params)
