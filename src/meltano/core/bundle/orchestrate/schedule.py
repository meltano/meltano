#!/usr/bin/env python3

import os
import logging
import yaml

from meltano.core.schedule_service import ScheduleService
from meltano.core.project import Project

CRON_INTERVALS = {
    "@once": None,
    "@hourly": "0 * * * *",
    "@daily": "0 0 * * *",
    "@weekly": "0 0 * * 0",
    "@monthly": "0 0 1 * *",
    "@yearly": "0 0 1 1 *",
}

project = Project.find()
schedule_service = ScheduleService(project)

elt_schedules = []
for schedule in schedule_service.schedules():
    cron_interval = CRON_INTERVALS.get(schedule.interval, schedule.interval)

    if not cron_interval:
        logging.info(
            f"Skipping schedule '{schedule.name}' because its interval is set to '@once'."
        )
        continue

    elt_schedules.append(
        {
            "name": schedule.name,
            "cron": cron_interval,
            "ref": "master",
            "variables": {
                "MELTANO_ELT_EXTRACTOR": schedule.extractor,
                "MELTANO_ELT_LOADER": schedule.loader,
                "MELTANO_ELT_TRANSFORM": schedule.transform,
            },
        }
    )

namespace = "elt"
config = {namespace: elt_schedules}

print(yaml.dump(config, default_flow_style=False))
