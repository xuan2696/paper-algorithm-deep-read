---
name: paper-algorithm-deep-read
description: "生成以算法理解为重点的论文精读 Markdown 报告，保留 What/Why/How/Experiment/Question 叙事，结合全文逐图讲清框架、模块输入输出、公式、训练与推理。用于单篇或批量 PDF 精读，以及已有报告的 How 深化。"
license: MIT
---

# 论文精读：算法详解

核心要求：**结合全文，详细解释算法部分涉及的图片，让读者能够沿图追踪输入如何经过各个模块变成输出，并理解这些模块如何学习、为什么这样设计。**

保留 What → Why → How → Experiment → Question 的论证线索。How 的深度由方法复杂度决定，通常是全文篇幅最大的一节；不沿用原版 How 的短篇幅目标。删去重复背景，不压缩独立机制。默认使用用户语言，中文请求输出中文。

## 使用范围

- 完整精读：每篇 PDF 形成独立图文 `report.md`，先读全文和全部图表，再写作。
- How 深化：已有报告需要补讲算法时，复用并核实原始 PDF、正文和提图结果，重点改写 How；用户指定的其他修改一并完成。
- 批量精读：一个 PDF 一个输出目录，允许复用工具配置，不交叉借用论文证据。不承诺无人值守的运行时长。

用户明确指定仅讲某图、某节或快速阅读时，遵循其范围；仍保留相应的输入输出、证据和不确定性说明，不强制生成其余四节。完整五节报告才运行完整报告验证器。

## 阅读与写作流程

1. **定位材料。** 使用用户指定的 PDF 和输出位置；缺省在当前项目的 `reports/paper-deep-read/` 下按论文分目录。已有目录先检查，避免覆盖原始材料或未授权重写旧报告。保留 `source.pdf`，提取带 PDF 页码和段落 ID 的全文。
2. **提图并读全图。** 按 [references/figure_protocol.md](references/figure_protocol.md) 使用 pdffigures2 提取全部图表和原始元数据。实际查看每张可用图片，联查图注、引用正文、定义和附录，完成 `visual_analysis.json`。核对正文引用以发现漏提取、错图、合并子图；不能仅凭图注声称看过图。
3. **通读全文并建立算法路径。** 通读任务定义、方法、伪代码、实验设置、实现细节、附录及局限，建立贡献到证据的对应。依据 [references/how_protocol.md](references/how_protocol.md)，把算法输入、模块衔接、核心公式、训练与执行路径及尚未披露的细节记入 `paper_index.json` 的 `method_modules` 和 `notes`；无需另造每模块一份文件。
4. **先规划，再成文。** 在 `visual_plan.json` 统一决定选图和章节。涉及技术路线的可用方法图去除真正重复的信息后展示并讲解；总览图和局部图、不同训练/推理路径以及独立子图通常互补。实验图按核心主张选择代表性证据，避免把全部实验堆入报告。
5. **沿执行顺序讲算法。** 完整报告按 [references/report_contract.md](references/report_contract.md) 写五节。How 先交代任务输入和全局路径，再沿方法图讲核心模块，接回对应公式、训练、一次推理及最终输出。图中有独特作用的子图、分支和重要箭头不能只靠“如图所示”带过；设计原因要区分作者说明与读者推断。
6. **做语义复核。** 按 How 协议检查：不翻回论文，读者是否能追踪关键量从何而来、怎样变换、流向何处、怎样学习和实际执行？每个关键步骤有证据或明确未知；每幅独立方法图有实质讲解。发现缺项先回原文补读，不能用标准实现填空。
7. **检查文件与格式。** 完整报告运行 `scripts/validate_report.py`，再核对原文事实。脚本检查结构、数学格式、图像来源和选图覆盖，**不能判定算法是否讲透，也不能证明公式或论文结论正确**。检查记录留在工作文件，不追加到报告正文。

## How 的最低交付标准

- 全局交代一次任务的输入、核心变换、输出，以及输出如何用于任务。
- 每个核心模块讲清输入来源与语义、内部操作、输出去向、前后衔接和设计作用，不能只罗列名称。
- 沿原图解释重要子图、箭头、循环、信息分支与训练边界；颜色或线型的含义必须能从论文确认。
- 核心公式落到具体模块或步骤，解释运算、关键符号和目的；说明原式、等价改写或读者补充推导。
- 有学习过程时分别走通训练和推理；非学习算法则说明初始化、迭代/求解过程、终止条件和输出。
- 从正文、伪代码、附录和实现细节补充图中未画出的步骤，保留图文冲突与披露不足。维度、层数、共享参数、通信需求等只写有依据的内容。

细则和易错情形见 [references/how_protocol.md](references/how_protocol.md)。这些标准是语义要求，不是要求正文反复填写固定字段表。

## 输出与证据

```text
paper-output/
  source.pdf
  report.md
  paper_index.json
  extracted/
    full_text.md
    sections.json
    pdffigures2-data/
      source.json
    pdffigures2.log
    figure_manifest.json
    visual_analysis.json
    visual_plan.json
    figures/
```

重要事实附真实位置，如 `(Evidence: Sec. 3.2, Fig. 2, Eq. 5, PDF p. 6)`；页码指 PDF 页序，避免与印刷页码混淆。自己的推断写明“我的理解”或 `(Inference from ...)`。没有证据的实现细节写“论文未说明”，不写成作者做法。

图片使用相对路径 `![图 2：方法框架](extracted/figures/source-Figure2-1.png)`，与图注、图片内容和 manifest 对得上。行内公式用 `$...$`；行间公式使用各自独占一行的 `$$`。不得把公式放进代码块。

## 本地工具

将下例中的 `<skill>` 替换为本 skill 所在目录；`<paper-output>` 使用脚手架实际返回的目录，不把占位符原样运行。

```text
python "<skill>/scripts/make_report_scaffold.py" "<paper.pdf>" --title "<unique-title>" --language zh-CN --out-root "<reports>"
python "<skill>/scripts/extract_pdf_text.py" "<paper-output>/source.pdf" --out "<paper-output>/extracted"
python "<skill>/scripts/extract_figures.py" "<paper-output>/source.pdf" --jar "<pdffigures2.jar>" --out "<paper-output>/extracted"
python "<skill>/scripts/build_paper_index.py" --extracted "<paper-output>/extracted" --out "<paper-output>/paper_index.json"
python "<skill>/scripts/validate_report.py" "<paper-output>/report.md"
```

正文提取需要 PyMuPDF，或作为回退的 pdfplumber。提图需要 Java 和 pdffigures2 JAR，`extract_figures.py --java "<java可执行文件>"` 可指定 Java。先检查用户给定配置和项目已有工具，不把本机绝对路径写入可分发的 skill。

脚手架及索引生成器用于**新目录**；已有报告继续修改时直接读取并更新现有文件，不重跑脚手架覆盖正文或重建索引丢失笔记。图像提取失败或缺少视觉能力时，继续可完成的正文阅读，明确当前限制；不得将文字解读冒充完整图文精读，不静默改用自行截图、嵌入图像提取或裁剪补图。

本 skill 在 Codex 中使用当前会话阅读和撰写；上游 `paperdeepread` API 批跑程序的提示词不会因安装本 skill 自动改变。需要改造该程序时另按用户指定范围处理。

## 来源

基于 `evidence-grounded-paper-deep-read` 定制，保留原作者的五段叙事、证据约束及 pdffigures2 提图方式。上游：[MoonKirito/evidence-grounded-paper-deep-read](https://github.com/MoonKirito/evidence-grounded-paper-deep-read)。原作者及复用代码的 MIT 声明保留于 `LICENSE`。
