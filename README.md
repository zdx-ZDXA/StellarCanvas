# 🎨 星绘 StellarCanvas

星缀套件的生图执行器，支持 NAI v3 / OpenAI 兼容接口。

## 功能

- 对外提供 `draw_for()` 接口，供星缀调用
- 配额管理（每日限制）
- 失败不抛异常，返回 None 让上层处理

## 配置

| 项 | 默认 | 说明 |
|---|---|---|
| backend | nai | 后端类型：nai / openai |
| api_key | | API 密钥 |
| api_base | | 自定义接口地址 |
| daily_limit | 0 | 每日上限，0=不限 |

## 支持后端

- **nai** — NovelAI v3 (`image.novelai.net`)
- **openai** — OpenAI DALL-E 3 或兼容接口

---
v1.0.2 · 星缀套件 | https://github.com/zdx-ZDXA/StellarCanvas
