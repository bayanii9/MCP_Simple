import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Homework Helper")


# Tool: يقترح أولوية الواجب بحسب الأيام المتبقية
@mcp.tool()
def plan_homework(subject: str, assignment: str, days_left: int) -> dict:
    """Suggest a priority for a homework assignment."""
    if days_left < 0:
        return {"error": "الأيام المتبقية لا يمكن أن تكون سالبة."}

    if days_left <= 1:
        priority = "عاجل"
    elif days_left <= 3:
        priority = "قريب"
    else:
        priority = "عادي"

    return {
        "subject": subject,
        "assignment": assignment,
        "days_left": days_left,
        "priority": priority,
    }


# Resource: معلومات مرجعية عن مستويات الأولوية
@mcp.resource("homework://priority-rules")
def priority_rules() -> str:
    """Reference rules for homework priority."""
    return json.dumps(
        {
            "عاجل": "متبقي يوم واحد أو أقل",
            "قريب": "متبقي من يومين إلى ثلاثة أيام",
            "عادي": "متبقي أكثر من ثلاثة أيام",
        },
        ensure_ascii=False,
    )


# Prompt: تعليمات قابلة لإعادة الاستخدام للمساعد
@mcp.prompt()
def homework_helper_prompt() -> str:
    """Instructions for helping a student organize homework."""
    return (
        "اسأل عن المادة واسم الواجب وعدد الأيام المتبقية. "
        "اقرأ مورد قواعد الأولوية، ثم استخدم أداة plan_homework "
        "واشرح النتيجة للطالب."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")