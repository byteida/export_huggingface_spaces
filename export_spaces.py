
import json
from datetime import datetime, timezone
from huggingface_hub import HfApi

api = HfApi()

OUTPUT = "huggingface_spaces_all.md"

def get_value(obj, key, default=""):
    if isinstance(obj, dict):
        return obj.get(key, default) or default
    return getattr(obj, key, default) or default

def clean(value):
    return str(value or "").replace("|", "\\|").replace(
        "\n", " "
    ).strip()

print("正在获取 Hugging Face 全部公开 Spaces...")

spaces = list(api.list_spaces(
    full=True,
    limit=None
))

print(f"获取完成，共 {len(spaces)} 个项目")

lines = [
    "# Hugging Face Spaces 全量项目清单",
    "",
    f"> 导出时间：{datetime.now(timezone.utc).isoformat()}",
    f"> 项目总数：{len(spaces)}",
    "> 数据来源：Hugging Face Hub API",
    "",
    "## 项目列表",
    "",
    "| 序号 | 模型名称 | 作者 | URL | 简要描述 | 分类 | SDK | 关联模型 | 关联数据集 | Likes | 更新时间 | Tags | 状态 |",
    "|---:|---|---|---|---|---|---|---|---|---:|---|---|---|"
]

for index, space in enumerate(spaces, 1):
    # 排除非公开项目
    if get_value(space, "private", False):
        continue

    repo_id = get_value(space, "id")
    card = get_value(space, "card_data", {}) or {}

    description = (
        get_value(card, "short_description")
        or get_value(card, "description")
        or get_value(space, "description")
        or "暂无项目简介"
    )

    tags = get_value(space, "tags", []) or []
    models = get_value(space, "models", []) or []
    datasets = get_value(space, "datasets", []) or []

    sdk = get_value(space, "sdk", "未知")
    likes = get_value(space, "likes", 0)
    modified = get_value(space, "last_modified", "未知")
    disabled = get_value(space, "disabled", False)

    status = "已禁用" if disabled else "公开"

    url = f"https://huggingface.co/spaces/{repo_id}"

    category = ", ".join(
        t for t in tags
        if not t.startswith(("sdk:", "license:", "language:"))
    ) or "未分类"

    row = [
        index,
        repo_id,
        get_value(space, "author", ""),
        f"[访问项目]({url})",
        clean(description),
        clean(category),
        clean(sdk),
        clean(", ".join(models)),
        clean(", ".join(datasets)),
        likes,
        clean(modified),
        clean(", ".join(tags)),
        status
    ]

    lines.append("| " + " | ".join(map(str, row)) + " |")

    if index % 1000 == 0:
        print(f"已处理 {index} 个项目")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("=" * 50)
print(f"导出成功：{OUTPUT}")
print(f"总项目数：{len(spaces)}")
