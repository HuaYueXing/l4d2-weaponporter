<div align="center">

# L4D2 Weapon Porter

### 求生之路2武器模型转换工具

把一个“替换武器 A”的 VPK，快速转换成“替换武器 B”的 VPK。  
面向《Left 4 Dead 2》武器 MOD 转槽位、批量测试、手工转模辅助流程。

![Platform](https://img.shields.io/badge/platform-Windows-0078D6?style=for-the-badge&logo=windows)
![Game](https://img.shields.io/badge/game-Left%204%20Dead%202-b22222?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-initial%20release-orange?style=for-the-badge)

**工具制作人 / Tool Creator：爱芳乃岁岁年年**

</div>

---

## 🚨 使用前必看：VPK 内部路径不要含中文

![Important](https://img.shields.io/badge/IMPORTANT-VPK路径不要含中文-red?style=for-the-badge)
![Check](https://img.shields.io/badge/Before%20Convert-Check%20VPK%20Paths-orange?style=for-the-badge)

> [!IMPORTANT]
> **转换前请确认 VPK 内部的文件夹名、文件名、模型路径、材质路径、音效路径中没有中文字符。**
>
> 如果 VPK 内部存在中文字符，请先拆包，把中文路径或中文文件名改成英文、数字或下划线后，再导入本工具进行转换。
>
> 转换完成后，如果你必须保留原来的中文命名，可以再根据需要手动改回。
>
> 中文路径可能导致识别失败、打包异常、模型丢失、材质丢失、音效丢失，或者进游戏后无法正确加载。

---

## 重要声明

这是工具的**初版 / Initial Release**。当前版本已经可以完成基础的 VPK 武器转槽位流程，但不同 MOD 的模型、动画、音频制作方式并不完全一致，因此转换结果仍需要进游戏实测。

可能出现的问题包括：

- 开火、换弹、部署、开镜等动作错位；
- 部分音效出现爆音、截断、播放异常；
- 跨动画族转换时，手部姿势或武器动作不自然；
- 少数结构特殊的 VPK 无法被正确识别或完整转换；
- 未适配**necola**，转模后的子弹计数器或机瞄无法使用（有时间再弄，，，可能）。

推荐优先进行**同动画族转换**。跨动画族转换可以用于快速测试，但不保证达到手工精修效果。

---

## 它能做什么

- 自动识别输入 VPK 替换的源武器；
- 按规则生成可转换目标列表；
- 支持一次勾选多个目标武器批量输出；
- 主武器只转主武器，近战只转近战；
- 自动排除源武器自身、手枪、马格南、电锯；
- 重定向 v_model / w_model 文件组；
- 修正 MDL 内嵌模型名；
- 转换武器音效目录与标准音效文件名；
- 转换 HUD 图标文件名；
- 尝试改写 `scripts/vscripts/*.nut` 中的武器引用；
- 输出新的 VPK，并写入转换说明。

本工具尽量保留原 MOD 的模型、材质、动作和作者制作细节。

---

## 支持范围

### 主武器互转

M16、AK47、SCAR、SG552、M60、UZI、MAC-10、MP5、木喷、铁喷、连喷、SPAS、猎枪、军狙、AWP、Scout、榴弹发射器。

### 近战互转

砍刀、消防斧、撬棍、平底锅、板球拍、棒球棍、警棍、武士刀、电吉他、高尔夫球杆、草叉、铁铲、小刀。

### 暂不转换

普通手枪、马格南、电锯。

---

## 快速开始

1. 安装 Python 3+，并确认命令行可以运行：

   ```bat
   python --version
   ```

2. 双击运行：

   ```text
   启动转换工具.bat
   ```
   #### 若双击启动转换工具.bat无法打开启动界面，可在该项目下启动cmd输入 python weapon_porter.py 手动打开！

3. 在界面中配置：

   - `vpk.exe`：通常位于 `Left 4 Dead 2\bin\vpk.exe`；
   - 输出目录：转换后的 VPK 保存位置；
   - 缓存目录：临时处理目录。

4. 拖入或选择需要转换的 `.vpk` 文件。

5. 勾选目标武器，点击开始转换。

6. 在输出目录中获取转换后的 VPK。

---

## 可选依赖

拖拽 VPK 需要安装：

```bat
pip install tkinterdnd2
```

未安装时仍然可以点击选择 VPK，不影响转换功能。

---

## 项目结构

```text
WeaponPorter/
├─ 启动转换工具.bat
├─ README.md
├─ weapon_porter.py
├─ converter.py
├─ weapon_data.py
├─ vpk_tool.py
├─ mdl_tool.py
├─ sound_map.py
├─ config.json
├─ tools/
├─ 输出/
└─ 缓存/
```

核心文件说明：

| 文件 | 作用 |
|---|---|
| `weapon_porter.py` | 图形界面入口 |
| `converter.py` | 转换流程编排 |
| `weapon_data.py` | 武器数据、分类、路径、动画族信息 |
| `vpk_tool.py` | VPK 解包与打包调用 |
| `mdl_tool.py` | 模型文件重定向与 MDL 内嵌名修正 |
| `sound_map.py` | 音效角色识别与目标音效映射 |
| `启动转换工具.bat` | Windows 双击启动脚本 |

---

## 转换过程参考

```mermaid
flowchart LR
    A[导入源 VPK] --> B[自动识别源武器]
    B --> C[选择目标武器]
    C --> D[解包 VPK]
    D --> E[重定向模型文件]
    E --> F[转换模型、音效与图标]
    F --> G[重新打包 VPK]
```

---

## 已知限制

- 多分卷 VPK 暂未作为主要测试目标；
- 跨动画族转换无法保证动作完全匹配；
- 少数 WAV 可能因源文件格式特殊而出现爆音或播放异常；
- 特殊脚本、特殊材质路径、非标准目录结构可能需要手工修正；
- 当前版本更适合快速转槽位与批量测试，不等于最终手工精修版。

---

## 鸣谢

特别感谢B站@ **Miztis** 对本工具制作与测试过程中的帮助。

---

## 作者与版权说明

- 工具制作人：**爱芳乃岁岁年年**
- 本工具只负责转换 VPK 结构与武器槽位，不自动取得原 MOD 的再发布授权，任何版权纠纷概不负责！
- 发布转换后的 MOD 前，请尊重原作者署名与授权要求。

