---
name: http-probe
description: "Use when a web endpoint must be checked for liveness, status code, redirect chain and gzip/TLS behaviour before any deeper testing: returns status, final URL, timing and the headers that matter. Handles 302 vs 200 confusion and cached responses. Not for load testing or brute forcing paths."
version: 1.0.0
---

# http-probe

把「这个地址到底通不通、返回什么」变成四条可直接贴进报告的数字：状态码、最终 URL、耗时、关键响应头。

## 前置条件

- 有 `curl`（Windows 10+ 自带 `curl.exe`）。
- 目标站点属于**你自己或已获授权**的范围；本技能只做单请求探测，不扫路径、不打并发。

## 步骤

1. 一次请求拿到状态码、重定向终点与耗时：

```bash
curl -sS -o NUL -D - --max-time 30 \
  -w "\ncode=%{http_code} final=%{url_effective} time=%{time_total}s size=%{size_download}\n" \
  http://TARGET/PATH
```

Windows PowerShell 里 `-o NUL` 同样可用；Linux 用 `-o /dev/null`。

2. 只关心状态码时：

```bash
curl -sS -o /dev/null -w "%{http_code} -> %{redirect_url}\n" http://TARGET/PATH
```

3. 检查压缩是否真的生效（很多站 `.htaccess` 写了 `mod_deflate`，但前面是 nginx，规则根本不读）：

```bash
curl -sS -o /dev/null -D - -H "Accept-Encoding: gzip" http://TARGET/PATH
# 看响应头有没有 Content-Encoding: gzip，以及 Content-Length 是不是等于未压缩大小
```

4. 302 之后要看落地页，加 `-L` 并保留中间跳转：

```bash
curl -sSL -o /dev/null -w "%{http_code} %{num_redirects} %{url_effective}\n" http://TARGET/PATH
```

## 判据

- `code` 是你预期的那个：页面 200、受保护页 302 到登录、接口 200/401/403 各有含义，**302 不是失败**。
- 带 `-H "Accept-Encoding: gzip"` 时，若响应体是文本且 `Content-Encoding` 为空，说明压缩没生效（要单独排查，不是探测失败）。
- `time_total` 稳定（连续两次相差 <20%）；抖动大说明命中了缓存或后端不稳。

## 失败与回滚

| 现象 | 原因 | 处理 |
|---|---|---|
| `curl: (6) Could not resolve host` | DNS 或域名拼错 | 先 `nslookup DOMAIN` |
| `code=000` | 连接没建立（端口/防火墙/TLS 握手） | 换 `-v` 看握手阶段 |
| PowerShell 报 `The 'Range' header must be modified…` | 用了 `Invoke-WebRequest` 设置受限头 | 改用 `curl.exe -H` |
| 判断线上内容时 `Contains('中文')` 恒 False | PS 解码问题 | 判 ASCII 类名或改用字节比较 |
| 302 反复跳转 | 登录态缺失或 cookie 环 | 用 `-c/-b` 保存并复用 cookie |

只做了只读请求，无需回滚；若期间用测试账号登录过，退出登录即可。
