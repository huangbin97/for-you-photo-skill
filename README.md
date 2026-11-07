# 为你拍照 · For You Photo Skill

Turn two photos into a natural “taking your photo” diptych, with coordinated outfits, realistic poses, and consistent lighting and color.

把两张照片变成“我在为你拍照”的上下拼图。只生成上方拍摄者，下方使用第二张原照裁切排版。

## 效果与规则

- 图1：拍摄者 A 的身份参考；图2：被拍摄者 B 的原始成片与场景依据。
- 两张等宽等高横图上下拼接，默认每幅 3:2、整体 3:4；可以根据主体调整共同横图比例。
- 保持 A 的辨识度、合理拍摄角度、自然肩颈与手部；允许轻微轮廓优化和局部细纹淡化。
- 保留自然肤质、正常清晰度，检查瞳孔、发丝与相机遮挡，避免过锐或磨皮。
- 以下图校准上图色调；下图不重绘，最终可轻微全局调色。

## 使用方式

### 支持 Skills 的工具

下载仓库，将包含 `SKILL.md`、`references/`、`scripts/` 和 `requirements.txt` 的文件夹按宿主说明导入；如工具要求文件夹与技能名称相同，将本地文件夹命名为 `make-couple-photo-diptych`。安装目录和触发方式由宿主决定，本仓库不宣称所有工具均已验证兼容。

上传两张图后说：

> 使用为你拍照技能。第一张是拍摄者，第二张是被拍摄者。只生成上方拍照视角，下方保留第二张原照，做成两个横图上下拼接，保持自然肤质、动作和统一色调。

### 普通聊天或生图工具

使用 [通用提示词](references/portable-prompt.md)，同时上传两张参考图。若工具只能生图，先保存生成的上图，再在本地或支持代码的工具中运行拼接脚本。

### 确定性拼接

需要 Python 3.10+ 与 Pillow。此脚本不调用任何付费 API，也不生成或美化人物。

```bash
python3 -m pip install -r requirements.txt
python3 scripts/compose.py --upper inputs/upper.png --lower inputs/person-b.jpg --lower-crop 0,300,1440,1260 --width 1200 --panel-height 800 --output outputs/diptych.png
```

裁切坐标必须根据实际照片选择，示例仅适用于对应尺寸。下图本身已经是匹配比例的横图时可省略 `--lower-crop`。脚本会拒绝明显不符的比例、越界裁切及覆盖已有结果。

可选 `--upper-curves curves.json` 对上图执行观察驱动的 RGB 曲线校色。例如下面是**不改变颜色**的基准，不是通用滤镜：

```json
{"r": [[0, 0], [255, 255]], "g": [[0, 0], [255, 255]], "b": [[0, 0], [255, 255]]}
```

全局亮度、对比度、饱和度参数默认为 1.0，可在 0.9–1.1 范围轻调。输出包括成品 PNG、全局调色前拼图和参数 JSON。色调与人物质量需要人工或视觉模型检查，脚本不会自动验收。

## 能力与限制

完整执行需要参考图生图/编辑能力、图片查看能力与脚本运行环境。技能本身不包含生图模型、API 密钥或会员权限；不同模型效果会有差异。无生图能力的 AI 可以整理提示词，不能独立完成成品。局部光影或眼手结构错误需要图像编辑能力修正。

## 文件

- `SKILL.md`：完整执行流程与验收规则。
- `references/prompt-template.md`：详细上图生成模板。
- `references/portable-prompt.md`：可复制的简化提示词。
- `scripts/compose.py`：裁切、可选校色、拼接和下图像素校验。
- `requirements.txt`：图片处理依赖。

本仓库不包含私人照片或密钥。仅使用你有权处理和分享的图片；生成的场景属于合成创作，不表示真实发生。
