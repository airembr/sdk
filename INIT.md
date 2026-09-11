# How the system is build


AiRembr is organized as a layered system. Each layer has a clearly defined responsibility and communicates with the layers below it through explicit interfaces.

The main principle is that the core system is independent of the way it is exposed or consumed. The same system commands can be used through the REST API, SDK, CLI, background processes, or MCP without duplicating the underlying business logic.

## System dictionaries

# airembr

airembr - folder that contains core system code. Inside the airembr/system is the actual system code. Outside are the adapters, code that can be used outside the system.

### airembr/system

The airembr/system directory contains the actual system implementation. It should contain the logic that defines what AiRembr does, rather than how the system is exposed to external applications.
Code outside airembr/system is primarily concerned with adapters and integrations. These components allow the core system to be used by different interfaces and environments without introducing interface-specific logic into the core.
This separation is important because the core system should not depend on FastAPI, MCP, a particular CLI implementation, or another external interface.

* airembr/system/command - here should be all the functions that are responsible for system commands, like collecting data, retirival etc.
Conceptually: External interface calls command that runs core system process. The important rule is that the command itself should contain or invoke the appropriate system logic rather than the API layer implementing that logic.
For example, the FastAPI layer should not contain the implementation of data collection. Instead, it should translate an HTTP request into a call to the appropriate system command.

* airembr/system/command/collect - all data collections commands (they go into endpoints in API, or commend in CLI - if any.)
* airembr/system/command/retrieve - all data retrival commands (they go into endpoints in API, or commend in CLI - if any.)
* airembr/system/process - main system processed
* airembr/system/processes/background - starting points for system background processes - files that can be run to do some processing. These are jobs or workers.

* airembr_api - is the FastAPi server that uses airembr/system/command fo expose it via API.

* airembr_sdk - this is a layer that uses airembr_api for programmatically access to the system. it lays on top of airembr APi and API users airembr system via commands. 
* airembr_mcp - uses some of airembr_api to expose it via MCP protocol