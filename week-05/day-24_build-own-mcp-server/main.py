from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Add_Hundred_Calculator")


@mcp.tool()
def add_hundred(a: int, b: int) -> int:
    """Add two numbers using custom calculator"""
    return a + b + 100  # deliberate debug proves claude is using our tool


if __name__ == "__main__":
    mcp.run()
