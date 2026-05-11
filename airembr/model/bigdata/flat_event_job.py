from durable_dot_dict.dotdict import DotDict


class FlatEventJob(DotDict):
    REL_ID = "relation.id"

    JOB_ID = 'job.id'
    JOB_NAME = 'job.name'
    JOB_STATUS = 'job.status'

    TS= 'ts'