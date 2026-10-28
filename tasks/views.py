import json
import sys
from pathlib import Path

from asgiref.sync import async_to_sync
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rest_framework.response import Response
from rest_framework.views import APIView

BASE_DIR = Path(__file__).resolve().parent.parent


async def connect_to_mcp(action, arguments=None):
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(BASE_DIR / "mcp_server" / "server.py")],
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            if action == "capabilities":
                tools = await session.list_tools()
                resources = await session.list_resources()
                prompts = await session.list_prompts()

                return {
                    "tools": [item.name for item in tools.tools],
                    "resources": [str(item.uri) for item in resources.resources],
                    "prompts": [item.name for item in prompts.prompts],
                }

            resource = await session.read_resource("homework://priority-rules")
            resource_text = next(
                item.text for item in resource.contents if hasattr(item, "text")
            )

            prompt = await session.get_prompt("homework_helper_prompt")
            prompt_text = "\n".join(
                item.content.text
                for item in prompt.messages
                if hasattr(item.content, "text")
            )

            result = await session.call_tool(
                name="plan_homework",
                arguments=arguments,
            )

            data = result.structuredContent
            if data is None:
                text = next(
                    item.text for item in result.content if hasattr(item, "text")
                )
                data = json.loads(text)

            return {
                "result": data,
                "mcp": {
                    "tool": "plan_homework",
                    "resource": json.loads(resource_text),
                    "prompt": prompt_text,
                },
            }


class HomeworkAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        data = async_to_sync(connect_to_mcp)("capabilities")
        return Response(data)

    def post(self, request):
        subject = request.data.get("subject")
        assignment = request.data.get("assignment")

        try:
            days_left = int(request.data.get("days_left"))
        except (TypeError, ValueError):
            return Response(
                {"error": "أرسلي days_left كعدد صحيح."},
                status=400,
            )

        if not subject or not assignment:
            return Response(
                {"error": "أرسلي subject وassignment."},
                status=400,
            )

        data = async_to_sync(connect_to_mcp)(
            "plan",
            {
                "subject": str(subject),
                "assignment": str(assignment),
                "days_left": days_left,
            },
        )
        return Response(data)