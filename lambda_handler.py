import os

from main import calculate_charge_windows, update_inverter_charge_time, update_cloud_watch

from project.givenergy import GivEnergy
from project.secrets import get_secret_or_env

time_offsets = {'local_time': 0,
                'octopus_time': -1,
                'giv_energy_time': 0,
                'aws': -1}


def handler(event, context):
    if context:
        arn = context.invoked_function_arn
    else:
        arn = "a:b:c:d:e:f"
    aws_fields = {"region": arn.split(":")[3],
                  "account_id": arn.split(":")[4]}

    msg = event["msg"]

    if msg == 'calculate':
        return calculate_charge_windows(aws_fields)
    elif msg == 'update':
        data = event["data"]
        offline_debug = True if os.environ.get("OFFLINE_DEBUG") == 'true' else False
        giv_energy = GivEnergy(offline_debug, get_secret_or_env("GE_API_KEY"))
        update_inverter_charge_time(giv_energy, offline_debug,
                                    data[0]['from_hours'],
                                    data[0]['too_hours'])
        response_data = update_cloud_watch(data, time_offsets, aws_fields)
        return response_data
    else:
        return {
            'message': 'unknown command'
        }


if __name__ == '__main__':
    event = {
        "msg": "update",
        "data": [
            {
                "from_hours": "05:30",
                "too_hours": "06:00"
            },
            {
                "from_hours": "22:30",
                "too_hours": "23:00"
            }
        ]
    }
    handler(event, None)
