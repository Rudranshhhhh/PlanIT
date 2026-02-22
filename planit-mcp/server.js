import {
  Server
} from "@modelcontextprotocol/sdk/server/index.js";

import {
  StdioServerTransport
} from "@modelcontextprotocol/sdk/server/stdio.js";

import {
  ListToolsRequestSchema,
  CallToolRequestSchema
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  {
    name: "planit-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/* ---------------- LIST TOOLS ---------------- */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "calculate_budget",
        description: "Calculate daily budget for a trip",
        inputSchema: {
          type: "object",
          properties: {
            days: { type: "number" },
            budget: { type: "number" }
          },
          required: ["days", "budget"]
        }
      }
    ]
  };
});

/* ---------------- TOOL EXECUTION ---------------- */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "calculate_budget") {
    const { days, budget } = request.params.arguments;
    const daily = budget / days;

    return {
      content: [
        {
          type: "text",
          text: `Estimated daily budget: ₹${daily}`
        }
      ]
    };
  }

  throw new Error("Unknown tool");
});

/* ---------------- START SERVER ---------------- */
const transport = new StdioServerTransport();
await server.connect(transport);
console.log("MCP Server is running...");
