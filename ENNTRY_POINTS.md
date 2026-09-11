# APIs
GUI API: /airembr/sdk/airembr_api/endpoint/gui
COLLECTOR API: /airembr/sdk/airembr_api/endpoint/collector

# Workers
COLLECTOR WORKER: /airembr/sdk/airembr/system/process/background/worker/sys_worker.py; CONSUER_TYPE=system.collector
STORAGE_WORKER: /airembr/sdk/airembr/system/process/background/worker/sys_worker.py; CONSUMER_TYPE=system.storage
DESTINATION_WORKER: /airembr/sdk/airembr/system/process/background/worker/sys_worker.py; CONSUMER_TYPE=system.destination
OBSERVATION_WORKER: /airembr/sdk/airembr/system/process/background/worker/sys_worker.py; CONSUMER_TYPE=system.storage.observation
LOG_WORKER: /airembr/sdk/airembr/system/process/background/worker/sys_worker.py; CONSUMER_TYPE=system.logger

# Jobs
BACKGROUND_JOBS: /dev/airembr/sdk/airembr/system/process/background/job/sys_job.py
