# Phase 1 Consolidated Research — 6 Android File Managers

**Date**: 2026-07-07
**Purpose**: Input for Phase 2 team discussion on which features to include in the final comparison table.

---

## App Roster

| # | App | Type | Latest Version |
|---|---|---|---|
| 1 | Material Files | FOSS (GPL-3.0) | v1.7.4 (tag Jun 2024), master active to Apr 2026 |
| 2 | Voyager | FOSS (GPL-3.0) | v1.2.0 (Jul 7, 2026) |
| 3 | FileExplorer (SysAdminDoc) | FOSS (MIT) | v1.4.0 (Jul 1, 2026) |
| 4 | MiXplorer (free + Silver) | Closed source | v6.70.3 (Feb 2026) |
| 5 | Solid Explorer | Closed source | 3.4.10 stable / 3.5.13 beta (Jul 2026) |
| 6 | X-plore | Closed source | 4.49.00 (Jun 27, 2026) |

---

## Pricing Summary

| App | Free | Ads | Paid | IAP | Subscription |
|---|---|---|---|---|---|
| Material Files | ✅ | ❌ | ❌ | ❌ | ❌ |
| Voyager | ✅ | ❌ | ❌ | ❌ | ❌ |
| FileExplorer | ✅ | ❌ | ❌ | ❌ | ❌ |
| MiXplorer free | ✅ | ❌ | — | ❌ | ❌ |
| MiXplorer Silver | — | ❌ | $5.99 one-time (bundles 4 add-ons) | ❌ | ❌ |
| Solid Explorer | 14-day trial | ✅ (after trial) | ~$2.99–$4.99 one-time | ✅ (Mega plugin $0.99, icon packs) | ❌ |
| X-plore | ✅ | ✅ | ~$3–5 one-time ("3 beers") unlocks all | ❌ | ❌ |

---

## Feature Matrix (raw, pre-discussion)

### Basics

| Feature | Material Files | Voyager | FileExplorer | MiXplorer | Solid Explorer | X-plore |
|---|---|---|---|---|---|---|
| minSdk | 23 (6.0) | 26 (8.0) | 26 (8.0) | 9 (2.3) | 23 (6.0) | 21 (5.0) |
| Material You | ❓ unclear | ✅ | ✅ | ❌ (custom skins) | ✅ | ❌ (dated UI) |
| Dual-pane | ❌ | ❌ | ❌ | ✅ (landscape) | ✅ (signature) | ✅ (tree-view, signature) |
| Tabs / Sessions | ❌ | ✅ sessions | ❌ | ✅ unlimited tabs | ❌ | ❌ |
| Breadcrumbs | ✅ | ❓ | ✅ | ❓ | ❓ | ❓ |
| Recycle bin / Trash | ❌ | ❌ | ✅ (TTL 7–90 days) | ❓ | ❌ | ✅ |

### Network Protocols (Client)

| Protocol | Material Files | Voyager | FileExplorer | MiXplorer | Solid Explorer | X-plore |
|---|---|---|---|---|---|---|
| SMB | ✅ SMB2+ (smbj) | ✅ SMB2+ (smbj) | ✅ smbj 0.13.0, domain auth | ✅ SMB1/2/3 | ✅ SMB2 (SMB3 ❓) | ✅ SMB1/2 (SMB3 ❓) |
| SFTP | ✅ sshj | ✅ JSch | ✅ sshj, known_hosts | ✅ | ✅ private key | ✅ (paid) |
| FTP | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| FTPS | ❓ | ❓ | ✅ TLS toggle | ✅ | ✅ (Pro-only) | ✅ |
| WebDAV | ✅ dav4jvm | ✅ Sardine | ✅ Sardine | ✅ | ✅ | ✅ |
| DLNA | ❌ | ❌ | ❌ | ✅ server+renderer | ❓ | ✅ client |

### Network (Server / Host mode)

| Feature | Material Files | Voyager | FileExplorer | MiXplorer | Solid Explorer | X-plore |
|---|---|---|---|---|---|---|
| FTP server | ✅ | ❌ | ❌ | ✅ | ✅ (FTPES Pro-only) | ✅ (read-only free) |
| SMB server | ❌ | ❌ | ❌ | ✅ (SMBv2, up to 3.1.1) | ❌ | ❓ |
| WebDAV/HTTP server | ❌ | ❌ | ❌ | ✅ | ✅ HTTP | ✅ (paid) |
| DLNA server | ❌ | ❌ | ❌ | ✅ | ❌ | ❓ |

### Cloud Storage

| Provider | Material Files | Voyager | FileExplorer | MiXplorer | Solid Explorer | X-plore |
|---|---|---|---|---|---|---|
| Any cloud | ❌ | ❌ | GDrive/Dropbox/OneDrive (own OAuth) | 19+ providers | GDrive/OneDrive/Dropbox/Box/Mega($)/MediaFire/Yandex/OwnCloud/SugarSync | GDrive/OneDrive/Dropbox/Box/MEGA/Degoo/WebDAV |
| Count | 0 | 0 | 3 | 19+ | 9+ | 7 |

### Root Access

| Feature | Material Files | Voyager | FileExplorer | MiXplorer | Solid Explorer | X-plore |
|---|---|---|---|---|---|---|
| Root | ✅ libsu | ❌ | ✅ libsu 6.0.0 | ✅ | ✅ | ✅ |
| SELinux context | ✅ | ❌ | ✅ | ❓ | ❓ | ❓ |
| chmod/chown | ✅ | ❌ | ✅ | ❓ | ✅ | ✅ |
| Shizuku | ❓ | ❌ | ❌ | ❓ | ✅ | ✅ |

### Archive Support

| Feature | Material Files | Voyager | FileExplorer | MiXplorer | Solid Explorer | X-plore |
|---|---|---|---|---|---|---|
| ZIP create/extract | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| 7z | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| RAR | ✅ | ❌ | ❌ | ✅ RAR5 | ✅ extract | ✅ extract |
| TAR/GZ/BZ2/XZ | ✅ | ❌ | ✅ | ✅ | ✅ | ❓ |
| Encrypted archives | ✅ ZIP pw | ❌ | ✅ AES-256 | ✅ AES | ✅ | ❓ |
| Browse-as-folder | ✅ | ❌ | ✅ virtual | ✅ | ✅ | ✅ |

### Themes & UI

| Feature | Material Files | Voyager | FileExplorer | MiXplorer | Solid Explorer | X-plore |
|---|---|---|---|---|---|---|
| Custom colors | ✅ | ✅ 20 themes | ✅ 5 modes | ✅ full picker + skins | ✅ | ❓ |
| AMOLED true black | ✅ | ✅ | ✅ OLED | ❓ | ❓ | ❓ |
| Night mode | ✅ | ✅ | ✅ | ❓ | ✅ | ❓ |
| Icon packs | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |

### Built-in Tools

| Tool | Material Files | Voyager | FileExplorer | MiXplorer | Solid Explorer | X-plore |
|---|---|---|---|---|---|---|
| Text editor | ✅ | ❌ | ✅ syntax hl | ✅ + code editor | ✅ | ✅ |
| Image viewer | ✅ | ❌ (thumbs only) | ❌ (thumbs only) | ✅ RAW/GIF/SVG | ✅ | ✅ |
| PDF reader | ❌ | ❌ | ❌ | ✅ (add-on) | ❌ | ✅ |
| Hex viewer | ❌ | ❌ | ❌ | ✅ | ❓ | ✅ |
| Media player | ❌ | ❌ | ❌ | ✅ Chromecast/DLNA | ✅ | ✅ (paid) |
| APK manager/signer | ✅ open | ❌ | ✅ app mgr | ✅ signer v1/v2/v3 | ❌ | ✅ backup |
| SQLite viewer | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ (read-only) |
| Storage analyzer | ❌ | ✅ (basic) | ❌ (roadmap) | ❌ (folder sizes) | ✅ (cloud=Pro) | ✅ disk map |

### Search & Navigation

| Feature | Material Files | Voyager | FileExplorer | MiXplorer | Solid Explorer | X-plore |
|---|---|---|---|---|---|---|
| Search | ✅ | ✅ | ✅ streaming | ✅ advanced | ✅ indexed | ✅ |
| Regex search | ❓ | ❌ | ✅ | ❓ pattern-based | ❓ | ❓ |
| Bookmarks | ✅ | ✅ | ✅ | ✅ categories | ✅ folders | ✅ |
| Checksum/hash | ✅ v1.7.2 | ❌ | ✅ MD5/SHA1/256/512 | ✅ | ❓ | ❓ |

### Security & Encryption

| Feature | Material Files | Voyager | FileExplorer | MiXplorer | Solid Explorer | X-plore |
|---|---|---|---|---|---|---|
| File/folder encryption | ❌ | ❌ | ✅ AES-256-GCM vault (v1.4.0) | ✅ Aescrypt + EncFS | ✅ AES-256 + fingerprint | ✅ Vault (paid) |
| Biometric lock | ❌ | ❌ | ✅ | ❓ | ✅ | ✅ |
| App lock | ❌ | ❌ | ❓ | ❓ | ❓ | ✅ |

### Other Notable

| Feature | Material Files | Voyager | FileExplorer | MiXplorer | Solid Explorer | X-plore |
|---|---|---|---|---|---|---|
| External SD / USB OTG | ✅ SAF | ✅ SD/USB/OTG/SAF | ❓ (roadmap) | ✅ NTFS R | ✅ OTG plugin | ✅ NTFS/HFS+ plugin |
| Symlinks | ✅ | ❓ | ❓ (NIO2) | ✅ create | ❓ | ❓ |
| Android TV | ✅ | ❌ | ❌ | ❓ | ✅ | ✅ |
| Open in terminal | ✅ partial | ❌ | ❌ | ✅ Termux | ❓ | ✅ SSH shell (paid) |
| Automation | ❌ | ❌ | ❌ | ✅ Auto Tasks | ❌ | ❌ |
| Secure delete | ❌ | ❌ | ✅ DoD 5220.22-M | ❓ | ❌ | ❌ |

---

## Notes for Team Discussion

- Several cells are ❓ (unclear) — these are verification candidates for Phase 3.
- MiXplorer is the feature-count leader by far (archives, clouds, servers, tools).
- FOSS apps (Material Files, Voyager, FileExplorer) have varying maturity.
- Pricing models differ structurally: free / trial+IAP / free+ads+donation / free+paid-bundle.
- "Dual-pane" means different things: Solid Explorer (flat split), X-plore (tree view), MiXplorer (landscape only).
- Cloud support in FileExplorer requires user to register own OAuth apps — functionally present but high friction.
