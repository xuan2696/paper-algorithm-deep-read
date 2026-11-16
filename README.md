# Paper Algorithm Deep Read

**论文精读：算法详解**

一个以算法理解为重点的 Codex skill。沿 **What → Why → How → Experiment → Question** 串起论文，结合全文和原始方法图，讲清输入如何经过各个模块变成输出、模型如何训练和执行，以及作者为什么这样设计。

本项目基于 [MoonKirito/evidence-grounded-paper-deep-read](https://github.com/MoonKirito/evidence-grounded-paper-deep-read) 定制，保留原作者的五段叙事、证据约束和 pdffigures2 提图方式，重点细化 **How 的解释颗粒度与验收要求**。感谢原作者提供的工作流。

## 重点讲清什么

- **全文补图**：联查方法正文、公式、伪代码、实验实现设置和附录，补足图中省略的关键步骤。
- **逐图、逐子图走读**：解释总览、局部模块、关键箭头、并行分支和循环，说明各图之间如何衔接。
- **模块输入与输出**：说明数据来自哪里、表示什么、怎样处理、送到哪里，以及如何影响最终任务。
- **公式对应计算**：将核心公式接回具体模块或算法步骤，解释运算和设计目的。
- **训练与推理分开**：走通学习信号、参数更新及一次实际执行；非学习算法则解释初始化、迭代、停止条件与输出。
- **保留未知与歧义**：区分作者陈述、读者推断和未披露细节，不用常见实现补造维度、层数或参数共享方案。

How 的篇幅由方法复杂度决定，不设短篇幅目标。完整报告保留五段结构；也支持只深化已有报告的 How，或只讲用户指定的图。

## 安装

将整个仓库放入个人 skills 目录，目标目录名称为 `paper-algorithm-deep-read`。仓库根目录就是 skill 根目录。

### Windows / PowerShell

```powershell
$skillBase = if ($env:CODEX_HOME) {
    Join-Path $env:CODEX_HOME 'skills'
} else {
    Join-Path $env:USERPROFILE '.codex\skills'
}
New-Item -ItemType Directory -Path $skillBase -Force | Out-Null
git clone https://github.com/xuan2696/paper-algorithm-deep-read.git (Join-Path $skillBase 'paper-algorithm-deep-read')
```

### macOS / Linux

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/xuan2696/paper-algorithm-deep-read.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/paper-algorithm-deep-read"
```

如果目标目录已经安装过此 skill，先检查已有改动，再更新；不要覆盖个人修改。无需安装原版 skill，本仓库包含所需指令、模板和本地辅助脚本。

## 使用

向 Codex 提供论文 PDF 的路径或附件，并明确调用：

```text
使用 $paper-algorithm-deep-read 精读这篇论文，生成中文图文报告。
```

深化已有报告：

```text
使用 $paper-algorithm-deep-read，结合论文全文深化这份报告的 How。
逐图解释算法框架、子图和关键箭头，讲清模块输入输出、公式对应、
训练与推理，并标明论文未披露的实现细节。
```

批量阅读：

```text
使用 $paper-algorithm-deep-read 精读指定目录中的 PDF，
每篇建立独立目录，输出一份中文图文报告。
```

skill 在当前 Codex 会话中指导阅读和写作。辅助脚本负责提取、建目录和校验，**不会单独调用 LLM 生成报告**。本仓库没有独立的 API 批跑服务，也不会自动替换上游 `paperdeepread` CLI 的提示词。

## 工具依赖

| 依赖 | 用途 |
| --- | --- |
| 能读取图像的 Codex 会话 | 实际查看方法图和实验图，并结合全文分析 |
| Python 3.10+ | 运行本地辅助脚本 |
| PyMuPDF | 提取带页码和段落锚点的正文 |
| Java 与 pdffigures2 assembly JAR | 提取论文图表和原始元数据 |
| pdfplumber（可选） | PyMuPDF 不可用时的正文提取回退 |

在本仓库根目录安装正文提取依赖：

```text
python -m pip install -r requirements.txt
```

pdffigures2 JAR 需要自行准备，参见 [pdffigures2 官方项目](https://github.com/allenai/pdffigures2)。提图时通过 `--jar` 指定路径；Java 不在 PATH 时通过 `--java` 指定可执行文件。仓库不附带 JAR、Java 运行时或论文 PDF。

## 辅助脚本

在仓库根目录执行，替换示例路径；`<paper-output>` 使用第一步返回的实际目录。

```text
python scripts/make_report_scaffold.py "<paper.pdf>" --title "<unique-title>" --language zh-CN --out-root reports
python scripts/extract_pdf_text.py "<paper-output>/source.pdf" --out "<paper-output>/extracted"
python scripts/extract_figures.py "<paper-output>/source.pdf" --jar "<pdffigures2.jar>" --out "<paper-output>/extracted"
python scripts/build_paper_index.py --extracted "<paper-output>/extracted" --out "<paper-output>/paper_index.json"
```

上述命令准备阅读材料，随后由 Codex 按 [SKILL.md](SKILL.md) 实际通读论文、查看全部可用图表，完成索引、图表分析、选图计划和报告正文。索引脚本生成的是待核实的脚手架，不能当成已经理解论文。

完整报告写好后执行：

```text
python scripts/validate_report.py "<paper-output>/report.md"
```

已有报告和索引需要继续修改时，直接读取并更新现有文件，不重新运行创建脚本。提图工具拒绝覆盖已有提取证据，重试应使用新的报告目录。

## 输出示例

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

完整报告的正文顺序：

1. **What**：任务、关键做法与实际贡献。
2. **Why**：已有方法的具体不足、观察与设计目标。
3. **How**：沿原图和计算流程展开算法、训练及推理。
4. **Experiment**：围绕作者目的串起实验证明链和边界。
5. **Question**：区分作者局限与读者判断，提出有依据的疑问。

重要事实通过章节、图表、公式或 PDF 页码定位。图片仅使用实际提取、检查并选定的 pdffigures2 图像。漏提取、不可读和图文冲突明确记录。

## 质量边界

验证器检查五节结构、证据锚点的存在、数学定界符、图像来源、图号与路径对应，以及选图计划的章节覆盖。它不能验证事实真伪、视觉分析是否真实或算法解释是否充分，仍需依据论文做语义复核。

只讲某图或 How 的局部请求不强制生成五节，也不运行完整报告验证器。缺少图像能力或提图失败时，保留可完成的文字分析并说明限制，不声称完成全部视觉核查。

## 项目结构

```text
SKILL.md                      # skill 入口
agents/openai.yaml            # 显示名与默认调用提示
references/how_protocol.md    # 算法逐图讲解标准
references/figure_protocol.md # 图表预读与全局选图协议
references/report_contract.md # 五段报告结构与验收
assets/report_template.md    # 报告脚手架模板
scripts/                      # 提取、索引与校验工具
tests/                        # 不依赖论文文件的工具回归检查
```

运行工具回归检查：

```text
python -m unittest discover -s tests -v
```

## 来源与许可

上游项目：[MoonKirito/evidence-grounded-paper-deep-read](https://github.com/MoonKirito/evidence-grounded-paper-deep-read)，原作者 MoonKirito。本项目复用其基础脚本和阅读规范，并增加算法讲解协议、独立提图入口、旧产物保护及图像证据一致性检查。

采用 [MIT License](LICENSE)，保留原作者版权声明。论文及其图表的权利归各自权利人，未包含在本仓库发布内容中。
