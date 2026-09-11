We need to move the GUI API endpoint from:

`/home/risto/PycharmProjects/dev/bizmory/api/endpoint/gui`

to:

`/home/risto/PycharmProjects/dev/airembr/sdk/airembr_api/endpoint/gui`

The migration should include the current endpoint implementation and all files that are required for the endpoint to work correctly in its new location.
Basic operation is moving the files to the /home/risto/PycharmProjects/dev/airembr/sdk/airembr_api/endpoint/gui and making sure the imports work.
Keep the existing folder structure form old API.  

After the endpoint has been successfully moved, remove the original implementation from:

`/home/risto/PycharmProjects/dev/bizmory/api/endpoint/gui`

The old location must not remain as a duplicate implementation.

During the migration, carefully verify the architecture and dependencies of the endpoint. In particular, **always check that the endpoint uses the system commands layer** rather than implementing or calling business logic directly. It should be already implemented. If implemented then list this as error.

The GUI endpoint should delegate operations to the appropriate commands located in the system command layer. 
Do not duplicate command logic inside the GUI endpoint. If the endpoint currently contains logic that should belong to a command, identify it and use the existing command instead.
After moving the endpoint, update any imports, references, paths, or configuration that still point to the old `/home/risto/PycharmProjects/dev/bizmory/api/endpoint/gui` location.

# How to do such bug task

* Split it into smoller tasks.
* First move the dependencies like /home/risto/PycharmProjects/dev/bizmory/api/endpoint/gui/auth/...
* Then check i

Finally, verify that:

1. The GUI endpoint exists in `airembr_api/endpoint/gui`.
2. The old endpoint has been removed from `bizmory/api/endpoint/gui`.
3. All imports reference the new location.
4. The endpoint uses the appropriate system commands.
5. No business or system logic has been unnecessarily duplicated in the API layer.
6. The endpoint can be loaded and used from its new location without import or dependency errors.
7. API can have al fastAPI related logic.
8. No fastapi can be used in commands.
