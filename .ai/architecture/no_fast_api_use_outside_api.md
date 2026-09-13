# No FastAPI use outside API folder airembr_api

It is not allowed to use fastapi package in the core system logic. Its purpose it for use inside api related packages. e.g airembr
FastAPi can be used inside endpoints for request, response modifications. If needed it may remap the data returned form the system command.
All access to system is done via /home/risto/PycharmProjects/dev/airembr/sdk/airembr/system/command.


