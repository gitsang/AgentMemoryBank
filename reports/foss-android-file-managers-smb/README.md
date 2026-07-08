# 出色开源安卓文件管理器（支持 SMB）调研

**日期**: 2026-07-07
**范围**: 开源安卓文件管理器，需原生支持 SMB/CIFS 网络文件访问
**方法**: 并行网络搜索 + librarian 外部参考核对（仓库、F-Droid、issue tracker、许可证）

---

## 已排除（核实后）

| 应用 | 原因 |
|---|---|
| MiXplorer | ❌ 非开源。作者从未发布源码，GitHub 仅 Wiki 仓库 |
| CX File Explorer | ❌ 非开源。GitHub 仅有文档仓库（1 star） |
| Total Commander | ❌ 专有 |
| Solid Explorer | ❌ 专有 |
| X-plore | ❌ 专有 |
| AndFTP | ❌ 专有，且无 SMB |

---

## 推荐榜（按综合表现排序）

### Tier 1 — 首选

#### 1. Material Files —— 最稳妥之选

| | |
|---|---|
| Repo | https://github.com/zhanghai/MaterialFiles |
| F-Droid | `me.zhanghai.android.files` |
| License | GPL-3.0 |
| Stars | ~8,500 |
| 最新 release | v1.7.4（2024-06），但 master 持续提交至 2026-04 |
| SMB | ✅ smbj，SMB2+，SMB3 加密可按服务器开启 |
| 其他协议 | SFTP / FTP / WebDAV |
| Root | ✅ libsu，SELinux 上下文，chmod/chown，remount |
| Material You | ✅ 主题 + 夜间模式 + 真黑 |

**亮点**:
- NIO2 后端（非 `ls` 解析），Linux-aware：符号链接、权限、SELinux 上下文
- 面包屑导航，轻量、干净的 Material Design
- 社区口碑最佳（HN "我每天用 SMB/SFTP"）

**短板**:
- release tag 落后于 master 近 2 年（需自建或用 F-Droid 版）
- v1.7.0 曾有 SMB 读取回归（已在 master 修复，未发版）

**结论**: 架构最干净、最安全、最成熟的 FOSS 安卓文件管理器。日常用 SMB/SFTP 首选。

---

#### 2. Voyager —— 现代新锐

| | |
|---|---|
| Repo | https://github.com/AlanHuang99/Voyager |
| F-Droid | `com.voyagerfiles` |
| License | GPL-3.0 |
| Stars | ~47（3 个月内） |
| 最新 release | v1.1.4（2026-06），3 个月 9 个版本 |
| SMB | ✅ smbj，SMB2+ |
| 其他协议 | SFTP (JSch) / FTP (Commons Net) / WebDAV (Sardine) |
| Root | ❌ |
| Material You | ✅ 20 主题：Catppuccin / Nord / Solarized / Gruvbox / Rosé Pine / Tokyo Night / AMOLED |
| Min Android | 8.0+ |

**亮点**: Jetpack Compose + Material 3，纯 Kotlin 现代栈；本地↔远程双向复制；SD/USB/OTG 外置存储；F-Droid 上架；发版节奏快。

**短板**: 仅 3 个月大，用户基数小，无 root。

**结论**: 不需要 root 的用户最佳现代选择，主题系统尤其出色。

---

### Tier 2 —— 强力但有取舍

#### 3. Amaze File Manager —— 功能最全，但 SMB3 缺失

| | |
|---|---|
| Repo | https://github.com/TeamAmaze/AmazeFileManager |
| F-Droid | `com.amaze.filemanager` |
| License | GPL-3.0 |
| Stars | ~6,250 |
| 最新 release | v3.11.2（2025-12） |
| SMB | ⚠️ jcifs-ng，仅 SMB1/2。**SMB3 不支持**（issue #4639，2026-05 仍 open） |
| 其他协议 | SFTP / FTP/FTPS（客户端 + 服务器）/ 云插件（GDrive、Dropbox、OneDrive、Box） |
| Root | ✅ |
| Material You | ❌（有主题，无动态色） |

**亮点**: 功能最丰富——标签页、应用管理（APK 备份）、AES 加密、FTP 服务器模式、数据库/ZIP/RAR/APK/文本阅读器、书签、历史。

**短板**:
- **SMB3 完全缺失**，对现代 NAS / Windows 11 可能有兼容性问题
- 640+ open issues
- GrapheneOS 上 SMB 崩溃报告
- 旧 RxJava 栈

**结论**: 功能党适用，但若 NAS 强制 SMB3 必须避开。

---

#### 4. SambaLite —— 最佳专用 SMB 客户端

| | |
|---|---|
| Repo | https://github.com/egdels/SambaLite |
| F-Droid | `de.schliweb.sambalite` |
| License | Apache-2.0 |
| Stars | ~110 |
| 最新 release | v2.5.2（2026-06） |
| SMB | ✅ smbj 0.14.0，SMB2+ |
| 其他协议 | ❌ 仅 SMB |
| Root | N/A |
| Material You | ✅ 暗色模式 |

**亮点**: MVVM + Dagger 2，**文件夹后台同步**、加密凭据存储、无遥测、多连接管理、网络发现、通配符搜索。

**短板**: 仅 SMB，不是通用文件管理器。

**结论**: 如果只想要 SMB 访问（不做本地文件管理），这是最专注、最精简的选择。

---

### Tier 3 —— 小众 / 观望

#### 5. FileExplorer (SysAdminDoc) —— 技术栈最全但太新

| | |
|---|---|
| Repo | https://github.com/SysAdminDoc/FileExplorer |
| License | MIT（此类项目少见） |
| Stars | ~2 |
| 最新 release | v1.4.0（2026-07） |
| SMB | ✅ smbj 0.13.0，域认证 |
| 其他协议 | SFTP / FTP/FTPS / WebDAV / GDrive / Dropbox / OneDrive |
| Root | ✅ libsu |
| Material You | ✅ 5 模式含 OLED |

**亮点**: Compose + M3 + Hilt + NIO2，连接管理器，AES-256 归档。纸面协议+root 支持最全。

**短板**: 2026-02 才建，几乎无社区，未上 F-Droid/Play。

**结论**: 技术最完整，但太年轻，不可依赖，值得观望。

---

#### 6. Ghost Commander —— 双栏老兵，维护缓慢

| | |
|---|---|
| SourceForge | https://sourceforge.net/projects/ghostcommander/ |
| F-Droid | `com.ghostsq.commander` |
| License | GPL-3.0 |
| 最新稳定 | v1.64（2024-07）；beta v1.64.2b1（2025-10） |
| SMB | ⚠️ 需装 "SMB NG" 插件（jcifs-ng，最后更新 2022-07） |
| 其他协议 | FTP / SFTP（插件） |
| Root | ✅ |
| Material You | ❌ |

**亮点**: Norton/Midnight Commander 风格双栏，轻量。

**短板**: SMB 是二等公民（需插件且插件已停更），源码在 SVN，开发缓慢。

**结论**: 仅适合双栏死忠粉，SMB 维护风险高。

---

#### 7. SentryFileManager / Fossify+SMB fork 等

基于 Material Files 的衍生分支，继承其质量但社区极小，未形成独立生态。除非有特定功能需求，否则直接用上游 Material Files。

---

## 横向对比矩阵

| 项目 | SMB | SMB3 | SFTP | FTP | WebDAV | 云存储 | Root | M.You | License | 状态 |
|---|---|---|---|---|---|---|---|---|---|---|
| **Material Files** | ✅2+ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | GPL-3.0 | 🟢 成熟 |
| **Amaze FM** | ⚠️1/2 | ❌ | ✅ | ✅ | ❌ | ✅$ | ✅ | ❌ | GPL-3.0 | 🟢 活跃 |
| **Voyager** | ✅2+ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | GPL-3.0 | 🟢 新锐 |
| **FileExplorer** | ✅2+ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | MIT | 🟡 新生 |
| **Ghost Cmdr** | ⚠️插件 | ? | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | GPL-3.0 | 🟡 低 |
| **SambaLite** | ✅2+ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | Apache-2.0 | 🟢 专注 |
| **Fossify+SMB** | ✅ | ? | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | GPL-3.0 | 🟡 分支 |

## 选型建议

- **日常 SMB/SFTP + root** → **Material Files**（最稳）
- **现代 UI、不要 root** → **Voyager**（最潮）
- **功能最多、不在乎 SMB3** → **Amaze File Manager**
- **只要 SMB 同步** → **SambaLite**（最专）
- **双栏情节** → **Ghost Commander**（自担维护风险）

## 来源

- GitHub 仓库 README / issue tracker
- F-Droid 元数据
- Hacker News 讨论（item 38992689）
- HowToGeek / apksharp 评测（2025-12 / 2026-03）
- GrapheneOS discuss 论坛
