# 更新日志

## 1.0.3

- 补齐 `CHANGELOG.md`（AstrBot 启动告警消除）。

## 1.0.2

- `_conf_schema.json` 改为 AstrBot 扁平字典格式，修复插件加载失败。

## 1.0.1

- 去掉 `@register` 装饰器，改为 `class StellarCanvas(Star)` 直接继承。
- 修复 AstrBot 4.x 导入路径。

## 1.0.0

- 对外接口 `draw_for(umo, uid, prompt, selfie, place, activity, zone)`，
  供星缀调用；失败一律返回 `None`，不抛异常。
- `quota(uid, umo, group)` 查询今日配额。
- 后端：NovelAI v3（`nai`）、OpenAI DALL·E 3 及兼容接口（`openai`）。
- 每日配额限制，0 表示不限量。
