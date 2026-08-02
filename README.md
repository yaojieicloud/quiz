# Quiz 题库系统

小朋友刷题系统（FastAPI + SQLite + Docker，部署于 ECS）。

## ⚠️ 出题铁律（永远遵守）

**小朋友的英语、语文、数学课本全部是人教版新课标课本。**

- 英语：人教 PEP 新课标（**2024 年秋季改版**，三年级上册单元为
  U1 Making friends / U2 Different families / U3 Amazing animals /
  U4 Plants around us / U5 The colourful world / U6 Useful numbers）
- 语文：部编版（统编版）
- 数学：人教版

后续为这三个科目生成/补充题目时，**单元、课时、知识点必须与课本保持一致**：
1. 单元名和顺序照课本目录
2. 课时按课本 Part / 课文拆分（英语按 Part A/B/C，语文按课文+语文园地）
3. 单词表、句型、课文内容以教材为准，出题前必须核对教材清单
4. 不得凭旧版教材或记忆杜撰单元内容

## 结构约定

- 文化类科目（语文/数学/英语）：Topic 表用 `unit`（单元）+ `name`（课时）两级组织
- 编程类科目（Python）：按"课"扁平组织，`unit` 留空
