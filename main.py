# A script that connects to both giv energy and octopus
# Get next days rates
# Checks battery percentage
# Checks prices
# Controls when inverter charges battery

# First get Octopus prices

# prices for Agile go live for next day at 4pm

"""
TODO:
    - make services use example data sets (ability to run offline on same json files)
    - if the service needs to be triggered 2 to 3 times a day, how to design the architecture
    - the service needs to set when it next needs to run.
    - trigger the service every 5/15/30 minutes to check if it should run. TICK

    - get inverter specs (battery capacity, max grid charge)
    - calculate how many hours would be required to charge the batterys to full from empty
    - filter for next days data
    - find x many cheapest time slots for that day

Charging logic
    - e.g. 10.10pm, 65% charge, cheapest rate is following day between lunch 1.30 - 2, and 2.30 - 3.
    - what would be the expected battery charge by the time we get to 1.30 tomorrow
    - how long would it take to charge to full
    - if additional charge is going to be needed in order to get to the cheapest rate, what cheaper rates are available before hand
    - perhaps better to calculate the latest estimated time that will need to charge from grid, factor in time of year, day of week, solar estimation etc
    - compare with agile rates

    - get the last 4 weekday electricity home usage and average per half hour slot
    - e.g. the last 4 Tuesday usage in half hour slots
    - 2 week holiday is going to produce outliers. how to deal with this?
"""
from datetime import datetime, timedelta
import os

from givenergy import GivEnergy, save_json_file
from analysis import *

from octopus import Octopus


def logic_index_to_time(index):
    time = (index * 0.5) - 0.5
    return time


def analyse_energy_usage(giv_energy, weeks):
    """
    Get the average of the last 4 weekdays energy usage in half hour slots, for the following day
    """
    previous_dates = get_x_weeks_previous_weekday_dates(weeks)
    data = get_energy_usage_days(giv_energy, previous_dates, [0, 3, 5])
    avg_half_hour_kwh, all_days = avg_half_hour_consumption_data(data, weeks)
    return {"avg": avg_half_hour_kwh,
            "all": all_days}


def analyse_solar_production(giv_energy, days):
    """
    Get the average of the last x days solar production in half hour slots
    """
    previous_dates = get_x_previous_days_dates(days)
    data = get_energy_usage_days(giv_energy, previous_dates, [0, 1, 2])
    avg_half_hour_kwh, all_days = avg_half_hour_consumption_data(data, days)
    return {"avg": avg_half_hour_kwh,
            "all": all_days}


def get_x_weeks_previous_weekday_dates(weeks):
    """
    Using tomorrow's day of the week, return the previous x weeks dates for that same weekday
    e.g. Saturday today, so get the previous 4 Sunday dates
    """
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    last_same_weekday = tomorrow - timedelta(days=7)
    previous_dates = []
    # Get the 4 previous dates
    for i in range(weeks):
        weekday_date = last_same_weekday - timedelta(days=i * 7)
        previous_dates.append({'start_date': weekday_date.strftime('%Y-%m-%d'),
                               'end_date': (weekday_date + timedelta(days=1)).strftime('%Y-%m-%d')})
    return previous_dates


def get_x_previous_days_dates(days):
    """
    Get the dates for the previous x days
    """

    today = datetime.today()
    previous_dates = []
    # Get the 4 previous dates
    for i in range(days):
        previous_day = today - timedelta(days=i)
        previous_dates.append({'start_date': previous_day.strftime('%Y-%m-%d'),
                               'end_date': (previous_day + timedelta(days=1)).strftime('%Y-%m-%d')})
    return previous_dates


def get_energy_usage_days(giv_energy, previous_dates, e_types):
    """
    Request energy usage data for the given dates
    """
    data = []
    for dates in previous_dates:
        # filter the data
        raw_data = giv_energy.get_energy_usage(dates['start_date'], dates['end_date'], e_types)
        data.append(raw_data['data'])
    return data


def avg_half_hour_consumption_data(data, weeks):
    """
    Average each half hour time slot between the number of weeks
    """
    all_days = []
    for day in data:
        day.popitem()
        day_total = []
        for half_hour in day.values():
            day_total.append(sum(half_hour["data"].values()))
        all_days.append(day_total)

    avg_consumption_kwh_per_half_hour = [round(sum(values) / weeks, 4) for values in zip(*all_days)]
    return avg_consumption_kwh_per_half_hour, all_days


if __name__ == '__main__':
    logic_index_to_time(5)
    offline_debug = True if os.environ.get("OFFLINE_DEBUG") == '1' else False

    giv_energy = GivEnergy(offline_debug, os.environ.get("GE_API_KEY"))

    # get renewable system specs
    giv_energy.extract_system_spec()

    # get average energy consumption
    """
    NOTE: this does not currently take into consideration the current time. Fix this
    at the moment its taking the average half hour slot of the previous 4 days,
    it needs to factor in the average daily usage, average daily weekday usage and then bias against the half hour time slots
    """
    house_consumption = analyse_energy_usage(giv_energy, 4)

    # get watt hour capacity remaining in battery
    inverter_data = giv_energy.get_inverter_systems_data()
    battery_watt_hours_remaining = ((inverter_data["data"]["battery"]["percent"] / 100) * \
                                    giv_energy.system_specs["battery_spec"]["watt_hour"]) / 1000

    # get weather forecast in half hour slots

    # get average production of panels in half hour slots for last 30 days
    solar_production = analyse_solar_production(giv_energy, 30)

    # sum solar data to historic consumption data

    # compare against half hour historic time slot data to get an estimated hours left until depleted, tolerance this?
    total_energy_consumed = 0
    no_half_hour_slots = 0
    for energy in house_consumption["avg"]:
        if total_energy_consumed + energy < battery_watt_hours_remaining:
            total_energy_consumed += energy
            no_half_hour_slots += 1
        else:
            break

    time_taken_until_empty = logic_index_to_time(no_half_hour_slots)

    # once have hours left to depleted, filter Octopus data to find cheapest value in time frame available

    # octopus = Octopus(offline_debug, os.environ.get("OCTOPUS_API_KEY"))
    # agile_data = octopus.get_tariff_data()

    analyse_data(house_consumption, solar_production)

    print('complete')
    # data = giv_energy.get_inverter_systems_data()
    # inverter_settings = giv_energy.read_inverter_setting(64)
    # print(inverter_settings)
    # octopus.save_json_file("agile-18-july", agile_data)

