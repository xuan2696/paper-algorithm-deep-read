# 图表提取、预读与全局选图

## 提取与核对

使用 `scripts/extract_figures.py` 调用 pdffigures2。保留原始 JSON 与日志，生成 `extracted/figure_manifest.json`，可用图片置于 `extracted/figures/`。原始 `page` 是从 0 开始的索引，`pdf_page` 为 `page + 1`，报告引用从 1 开始的 PDF 页序。

manifest 的基本结构：

```json
{
  "source": "pdffigures2",
  "pdf": "source.pdf",
  "raw_metadata": "extracted/pdffigures2-data/source.json",
  "page_indexing": "page is zero-based; pdf_page is one-based",
  "items": []
}
```

每项保留 pdffigures2 的 `figType`、`name`、`caption`、`page`、边界等原始字段，补充 `pdf_page`、相对报告根目录的 `image` 和 `status`。无图像区域的图注保留为 `unavailable`，`image` 为空并说明原因。文件存在不代表提取正确，需要实际查看。

核对正文、图注和附录中的图表引用：

- 完全漏提取的图表，经正文核实后补充缺失记录，注明核实依据；不能把未核实的正则匹配当成真实图表。
- 错配图注、裁到其他表格、合并多图、丢失子图或文本模糊时记录问题，不改写原始 JSON。
- 无效图片在 manifest 中设为不可用，清空报告可用的 `image`，必要时保留 `rejected_image` 供追查。
- 一张提取图含多个原图/子图时，保持原图，记录其实际覆盖范围；不要虚构多个独立图像文件。

只使用 pdffigures2 提取图像。不能自行截图、用页面预览、嵌入图像提取或其他工具裁剪来补图。可以按工具支持的 DPI 重跑到新目录，保留已有证据；不可读/仍缺失时说明限制，继续有依据的正文分析，不声称完成视觉理解。

## 全部图表预读

写报告前查看每张实际可用图片，结合完整图注、定义和引用正文。记录它怎样读、观察到什么、支持什么主张、不能证明什么、是否适合插入以及原因。不能用模型对论文的既有印象或图注摘要冒充看图。

`extracted/visual_analysis.json` 使用如下结构。下面只是字段示例，示例图号与证据必须替换为实际论文内容：

```json
{
  "complete": true,
  "items": [
    {
      "figType": "Figure",
      "name": "2",
      "image": "extracted/figures/source-Figure2-1.png",
      "status": "analyzed",
      "readable": true,
      "summary": "实际图的用途与结构",
      "observation": "已确认的模块、箭头或实验关系",
      "supports": ["实际支持的主张"],
      "limitation": "这幅图本身不能支持的结论",
      "evidence": ["Sec. 3.2, Fig. 2, PDF p. 6"],
      "selected": true,
      "section": "how",
      "reason": "包含独立的技术信息"
    }
  ]
}
```

`items` 与 manifest 的 `(figType, name)` 一一对应，不重名。状态只能为 `analyzed`、`unreadable` 或 `unavailable`；后两者保留原因，不用于插图。`complete=true` 表示每项均已处理，不表示所有图片提取成功。没有图表时保留空清单并说明已核对的范围。

算法图按照 `how_protocol.md` 解释模块、箭头和子图；必要时在预读记录补充 `panels`、`trace`、`unknowns` 等简短笔记，无需为每张图另建文档。表格与曲线核对坐标/图例/行列、指标方向、基线、比较条件及数字可读性。

## 全局选图

预读后保存 `extracted/visual_plan.json`，一次性考虑完整叙事，不能让各节独立丢弃彼此需要的图。结构示例：

```json
{
  "complete": true,
  "items": [
    {
      "id": "Figure 2",
      "image": "extracted/figures/source-Figure2-1.png",
      "section": "how",
      "include": true,
      "covers": ["overview-data-flow"],
      "reason": "解释整体输入到输出的数据流",
      "duplicate_of": ""
    }
  ],
  "claims": [
    {
      "claim": "实际论文的一项核心贡献",
      "evidence": ["Sec. 4.2, Table 1"],
      "visuals": [],
      "presentation": "text",
      "reason": "实际选用文字呈现实验证据的具体理由"
    }
  ]
}
```

- `items` 对每个分析项目恰好决定一次，`id` 为 `figType + 空格 + name`。`section` 使用 `what/why/how/experiment/question/none`，不能自行改为数字或标题文本。
- 可用且属于技术路线的 How 图应展示；真正重复时 `include=false`、`duplicate_of` 直接指向已保留的 How 图，说明重合信息。被省略图的 `covers` 必须全部被代表图覆盖。不可读/不可用不需要伪造重复代表。
- 总览与局部、训练与推理、不同机制或独立子图不能因为属于同一方法就视为重复。
- 实验按“主张 → 设置 → 关键结果 → 结论边界”选择代表图表。独立核心收益各有证据；同一证明链的辅助诊断、完整明细或重复数值可以文字引用，理由具体。
- `claims` 至少记录实际核心主张、真实证据和图/文字呈现的理由；`visuals` 只引用已有 ID。`presentation=image` 必须有选定的支持图，`text` 不要求为装饰选图。

报告执行所有 `include=true` 的图表及章节决定，不额外插入 `include=false` 图表。需要改变时先改计划，不能以篇幅为由无记录删掉独立方法图。图前给阅读重点，图后讲具体机制/比较与证据边界。全部预读不等于全量插图。
