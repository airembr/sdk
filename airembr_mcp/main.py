from mcp.server.mcpserver import MCPServer

from airembr_mcp import config
from airembr_mcp.tools.add_entities import add_entities_to_observation
from airembr_mcp.tools.ask import ask
from airembr_mcp.tools.remember import remember
from airembr_mcp.tools.search_observations import SEARCH_OBSERVATIONS_DESCRIPTION, search_observations

mcp = MCPServer(name=config.MCP_SERVER_NAME)

mcp.tool(name="remember", description=remember.__doc__)(remember)
mcp.tool(name="add_entities_to_observation", description=add_entities_to_observation.__doc__)(
    add_entities_to_observation
)
mcp.tool(name="ask", description=ask.__doc__)(ask)
mcp.tool(name="search_observations", description=SEARCH_OBSERVATIONS_DESCRIPTION)(search_observations)


def main() -> None:
    mcp.run(transport=config.MCP_TRANSPORT, host=config.MCP_HOST, port=config.MCP_PORT)


if __name__ == "__main__":
    main()
