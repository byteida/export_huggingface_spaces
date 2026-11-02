Hugging Face 的全部公开 Spaces 整理成一个完整的 Markdown 文件，方便后续检索、筛选和建立 AI 工具资源库。

目标文件： `huggingface_spaces_all.md`

## 1. 文件内容结构

每个项目记录以下信息：

| 字段 | 说明 |
| --- | --- |
| 序号 | 自动编号 |
| 模型名称 | Space 项目名称 |
| 作者 | 创建者或组织 |
| URL | 项目访问地址 |
| 简要描述 | 项目的功能和用途 |
| 分类 | AI 对话、图像生成、视频、音频等 |
| SDK | Gradio、Streamlit、Docker 等 |
| 关联模型 | 项目使用的 Hugging Face 模型 |
| 关联数据集 | 使用的数据集 |
| Likes | 点赞数量 |
| 更新时间 | 最近修改时间 |
| Tags | 项目标签 |
| 状态 | 正常、暂停或禁用 |

## 2. 自动生成完整 MD 文件

Hugging Face 官方提供了全量 Spaces 查询接口。下面使用官方 Python SDK 自动获取数据，而不是只抓取网页当前显示的项目。

支持全量分页获取安装依赖

bash

```bash
pip install -U huggingface_hub
```

导出脚本：export\_spaces.py

python

```python

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
```

运行：

bash

```bash
python export_spaces.py
```

运行完成后，会在当前目录生成：

`huggingface_spaces_all.md`

## 3. 数据来源与说明

- 官方 Spaces 列表：[Hugging Face Spaces](<https://huggingface.co/spaces?utm_source=chatgpt.com>)
- 官方 API 文档：[Hugging Face HfApi](<https://huggingface.co/docs/huggingface_hub/package_reference/hf_api?utm_source=chatgpt.com>)
- 官方 API 接口说明：[Hub API Endpoints](<https://huggingface.co/docs/hub/api?utm_source=chatgpt.com>)

注意：简介取自 Space 卡片元数据，部分项目可能没有填写简介；此时会标注为「暂无项目简介」。导出数量以实际 API 返回结果为准。

最终效果： 一个包含全站公开 Spaces 项目的 Markdown 索引文件，可使用 VS Code、Obsidian、Typora 或 GitHub 阅读，也可以进一步转换成 Excel、CSV 或数据库。