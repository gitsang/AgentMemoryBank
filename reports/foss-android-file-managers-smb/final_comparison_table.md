# Android 文件管理器功能对比表（最终版）

**编译日期:** 2026-07-08  
**方法:** 6 个子代理初始调研 → 3 人团队辩论（86 → 31 行功能列表）→ 5 个验证代理解决所有 ❓ 项  
**应用:** MF = Material Files, VY = Voyager, FE = FileExplorer (SysAdminDoc), MX = MiXplorer, SE = Solid Explorer, XP = X-plore

---

> **通用功能（6 个应用全部支持）:** 复制/移动/重命名/删除、多选、FTP 客户端、WebDAV 客户端、书签、基础搜索、列表/网格视图。

---

## 第 1 节：基本信息

| # | 功能 | MF | VY | FE | MX | SE | XP |
|---|------|----|----|----|----|----|----|
| 1 | **许可证** | GPL-3.0 | GPL-3.0 | MIT | 闭源 | 闭源 | 闭源 |
| 2 | **价格与广告** | 免费·无广告 | 免费·无广告 | 免费·无广告 | 免费无广告 + Silver $5.99 | 14 天试用 → ~$2.99–4.99 内购·试用期有广告 | 免费含广告·$1.50 去广告·$5.00 解锁全部 |
| 3 | **最低 Android** | 6.0 | 8.0 | 8.0 | 2.3 | 6.0 | 5.0 |
| 4 | **最近更新** | 2026.04 (master)；v1.7.4 tag 2024.06 | 2026.07.07 | 2026.07.01 | 2026.02 稳定版, 2026.07 beta | 2026.07 | 2026.06.27 |

## 第 2 节：网络协议与云存储

| # | 功能 | MF | VY | FE | MX | SE | XP |
|---|------|----|----|----|----|----|----|
| 5 | **SMB 版本** | SMB2+ (smbj) | SMB2+ (smbj) | SMB2+ (smbj) | SMB1/2/3 | SMB2/3 | SMB1/2 |
| 6 | **SFTP** | ✅ | ✅ | ✅ (known_hosts) | ✅ | ✅ (私钥) | ⚠️ 付费 |
| 7 | **FTPS** | ✅ (客户端) | ❌ | ✅ | ✅ | ⚠️ Pro 专享 | ✅ |
| 8 | **DLNA 客户端** | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| 9 | **云服务商数量** | 0 | 0 | 3 (自带 OAuth) | 19+ | 9 (Mega $0.99) | 7 |

## 第 3 节：服务器功能

| # | 功能 | MF | VY | FE | MX | SE | XP |
|---|------|----|----|----|----|----|----|
| 10 | **FTP 服务器** | ✅ | ❌ | ❌ | ✅ | ⚠️ FTPES Pro 专享 | ⚠️ 免费版只读 |
| 11 | **SMB 服务器** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| 12 | **HTTP/WebDAV 服务器** | ❌ | ❌ | ❌ | ✅ | ✅ HTTP | ⚠️ 付费 |

## 第 4 节：界面与导航

| # | 功能 | MF | VY | FE | MX | SE | XP |
|---|------|----|----|----|----|----|----|
| 13 | **双栏模式** | ❌ | ❌ (有会话) | ❌ | ⚠️ 仅横屏 | ✅ 平铺双栏 | ✅ 树形视图 |
| 14 | **标签页/会话** | ❌ | ✅ 会话 | ❌ | ✅ 不限标签 | ❌ | ❌ |
| 15 | **Material You** | ✅ MD3 动态色彩 | ✅ | ✅ | ❌ (自定义皮肤) | ✅ | ❌ |
| 16 | **AMOLED 真黑** | ✅ | ✅ | ✅ | ✅ (可调至 #000) | ⚠️ 暗色模式·真黑未验证 | ⚠️ 暗色模式·真黑未验证 |
| 17 | **回收站** | ❌ | ❌ | ✅ 7-90 天可配 | ✅ | ❌ | ✅ |

## 第 5 节：系统与存储访问

| # | 功能 | MF | VY | FE | MX | SE | XP |
|---|------|----|----|----|----|----|----|
| 18 | **Root 访问** | ✅ +SELinux+Shizuku | ❌ | ✅ +SELinux | ✅ | ✅ | ✅ |
| 19 | **Shizuku 支持** | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| 20 | **外置 SD / USB OTG** | ✅ SAF | ✅ | ❌ (路线图) | ✅ NTFS 读 | ✅ 插件 | ✅ NTFS/HFS+ 插件 |

## 第 6 节：压缩归档

| # | 功能 | MF | VY | FE | MX | SE | XP |
|---|------|----|----|----|----|----|----|
| 21 | **RAR / RAR5** | ✅ | ❌ | ❌ (路线图) | ✅ RAR5 | ⚠️ 仅解压 | ⚠️ 仅解压 |
| 22 | **加密归档 (AES)** | ✅ ZIP 密码 | ❌ | ✅ AES-256 | ✅ AES | ✅ | ❌ |

## 第 7 节：内置查看器与工具

| # | 功能 | MF | VY | FE | MX | SE | XP |
|---|------|----|----|----|----|----|----|
| 23 | **文本编辑器** | ✅ 基础 | ❌ | ✅ 语法高亮 | ✅ 代码编辑器 | ✅ | ✅ |
| 24 | **图片查看器** | ✅ | ⚠️ 仅缩略图 | ⚠️ 仅缩略图 | ✅ RAW/GIF/SVG | ✅ | ✅ |
| 25 | **PDF 阅读器** | ❌ | ❌ | ❌ | ⚠️ 插件 | ❌ | ✅ |
| 26 | **媒体播放器** | ❌ | ❌ | ❌ | ✅ Chromecast+DLNA | ✅ | ⚠️ 付费 |
| 27 | **空间分析器** | ❌ | ⚠️ 基础 | ❌ (路线图) | ⚠️ 仅文件夹大小 | ⚠️ Pro 专享 | ✅ 磁盘地图 |

## 第 8 节：安全与隐私

| # | 功能 | MF | VY | FE | MX | SE | XP |
|---|------|----|----|----|----|----|----|
| 28 | **文件加密/保险库** | ❌ | ❌ | ✅ AES-256-GCM 保险库 | ✅ Aescrypt+EncFS | ✅ AES+指纹 | ⚠️ 付费保险库 |
| 29 | **生物识别锁** | ❌ | ❌ | ✅ | ✅ | ✅ 指纹 | ✅ |
| 30 | **安全擦除** | ❌ | ❌ | ✅ DoD 5220.22-M | ❌ | ❌ | ❌ |
| 31 | **自动化** | ❌ | ❌ | ❌ | ✅ Auto Tasks | ❌ | ❌ |

---

## 脚注

1. **云服务商详情:** FE 支持 Google Drive/Dropbox/OneDrive，但需要用户自行注册 OAuth 应用——非即插即用。MX 支持 19+ 家：GDrive、OneDrive、Dropbox、Box、Mega、pCloud、Yandex、MailRu、HiDrive、MediaFire、IDrive、4Sync、4Shared、Meo、SugarSync、Amazon、Hubic、Baidu、VDisk。SE 支持 9 家：GDrive、OneDrive、Dropbox、Box、Mega ($0.99 插件)、MediaFire、Yandex、OwnCloud、SugarSync。XP 支持 7 家：GDrive、OneDrive、Dropbox、Box、MEGA、Degoo、WebDAV。

2. **MiXplorer 插件模块 (共 10 个):** Archiver、Image、PDF、Tagger、Codecs、Encrypt、Signer、SMB、AutoTag、Metadata。Silver 套装 ($5.99) 包含 4 个：Archiver、Image、Tagger、PDF。

3. **Solid Explorer 插件:** 独立的 Megacloud 插件 ($0.99) 和 Cast 插件可通过内购获得。

4. **Voyager 范围说明:** 无归档支持、无 root 访问、无云存储——均为 v1.x 项目的刻意范围限制。

5. **SFTP 说明:** X-plore 的 SFTP 需要付费"3 beers"解锁。Solid Explorer 的 SFTP 支持私钥认证。

6. **FTPS 说明:** Solid Explorer 的 FTPS 为 Pro 内购专享。

7. **Root 访问说明:** MF 和 FE 显示 SELinux 上下文。MF 还支持 Shizuku 作为非 root 提权方式。

8. **AMOLED 说明:** SE 和 XP 有暗色模式，但未验证 #000 真黑主题。MX 可通过自定义皮肤配置达到真黑效果。

9. **Material Files 说明:** `master` 分支持续活跃至 2026 年 4 月；最新 tag (v1.7.4) 为 2024 年 6 月。开发仍在进行中。

10. **回收站:** FE 可配置保留时间从 7 天到 90 天。
