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

1. **在 Gateway 环境变量中设置**：
   ```json
   {
     "env": {
       "vars": {
         "TVLY_API_KEY": "tvly-xxx"
       }
     }
   }
   ```

2. **直接运行脚本时设置**：
   ```bash
   TVLY_API_KEY=tvly-xxx node search.js "查询内容"
   ```

## 搜索结果格式

返回格式：
- **标题** - 文章标题
- **链接** - 来源 URL
- **摘要** - 内容摘要
- **分数** - 相关性评分 (0-1)

## 使用示例

```bash
# 搜索并返回5个结果
node search.js "OpenClaw AI" 5

# 搜索并返回3个结果
node search.js "闪迪涨价" 3
```

## 注意事项

1. Tavily 免费额度：每月 1000 次搜索
2. API Key 不要硬编码到 skill 中
3. 搜索结果已缓存 15 分钟
