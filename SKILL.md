---
name: tavily-search
description: Tavily 搜索工具，提供 AI 优化的搜索结果。每月免费 1000 次查询。
---

# Tavily 搜索

## 触发场景

用户需要搜索网络信息时使用此 skill：
- "搜索 xxx"
- "查一下 xxx"
- "找一下关于 xxx 的信息"
- 需要最新网络信息时

## 使用方法

此 skill 会调用 Tavily Search API 返回搜索结果。

## 环境配置

API Key 需要通过环境变量 `TVLY_API_KEY` 传入。

配置方式（任选一种）：

1. **在 TOOLS.md 中记录**（推荐）：
   ```
   TVLY_API_KEY=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
   ```

2. **在 Gateway 环境变量中设置**

## 搜索结果格式

返回格式：
- **标题** - 文章标题
- **链接** - 来源 URL
- **摘要** - 内容摘要
- **分数** - 相关性评分 (0-1)

## 注意事项

1. Tavily 免费额度：每月 1000 次搜索
2. API Key 不要硬编码到 skill 中
3. 搜索结果已缓存 15 分钟
