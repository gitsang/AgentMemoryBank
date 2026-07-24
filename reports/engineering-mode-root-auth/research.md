# 业内「解锁/root 动作本身的认证鉴权机制」调研

> 修正版。前一份把「流程门槛」(答题、等级、审批、等待期)误当成了「认证鉴权」。本文只回答一个问题:
> **流程走完之后,最后那一下 unlock,设备端到底是怎么验证"你被授权了"的?凭据是什么形态?信任根在哪?**

## 核心结论

业内最后一公里的认证鉴权,本质上只有 **5 种技术模式**。流程门槛(账号/答题/审批)只是决定**服务端肯不肯给你签发凭据**,而**设备端认不认这个凭据**才是真正的认证鉴权,两者是分离的:

```
流程门槛(人/服务端策略)  →  签发凭据  →  设备端验证凭据(认证鉴权)  →  执行 unlock
   (可绕过/可变)              (密码学)        (固化的信任根)            (状态写回)
```

关键洞察:**真正难绕过的是"设备端验证"这一环**,因为它的信任根是硬件烧录的密钥/一次性 fuse。前面所有流程门槛被绕过(比如小米的 Python 脚本跳过答题),最终还是要回到"拿到服务端签发的凭据"这一步。

---

## 五种认证鉴权模式对照表

| 模式 | 信任根 | 凭据形态 | 设备端如何验证 | 代表厂商 | 抗逆向 |
|------|--------|----------|----------------|----------|--------|
| **① 本地可写标志位** | bootloader 代码逻辑(检查标志) | 无凭据,仅 `get_unlock_ability=1` 标志 | bootloader 启动时读 persist 分区标志位,==1 才放行 `flashing unlock` | Google Pixel、旧一加、Fairphone | 弱(标志位可被 9008/漏洞篡改) |
| **② Challenge–Response + 服务端签名 token** | 设备预置厂商公钥(烧在 SoC/ABL) | 动态 token + 服务端签名打包的 `token.bin` | 设备出 token → 服务端私钥签名 → 设备用预置公钥验签,通过才执行 `oem unlock` | **小米** | 强(私钥在服务端,设备离线验签) |
| **③ 设备绑定静态解锁码** | 服务端解锁码生成算法 + IMEI 唯一性 | 与 IMEI 绑定的固定解锁码 | `fastboot oem unlock 0x<码>`,bootloader 校验码与设备 IMEI 的对应关系 | 索尼、Motorola、旧华为 | 中(码静态不变,但与设备绑定;有 reCAPTCHA 防批量) |
| **④ 服务端下发授权标志 + 本地分区校验** | ocdt 等配置分区的完整性(受安全启动保护) | 无凭据,服务端审核通过后远程置位 `ocdt` 分区标志 | bootloader 检查 ocdt 分区"是否已授权进 fastboot"标志 | **OPPO/realme**(深度测试)、一加(出厂即置位) | 中(可 9008 强刷一加 ocdt 绕过) |
| **⑤ 物理确认 + 一次性 eFuse 熔断** | 硬件一次性 fuse 的不可逆性 | 无凭据,物理按键确认即触发 | Download Mode 长按音量键确认 → 高压脉冲烧断 KNOX eFuse → VaultKeeper 联网确认状态 | **三星** | 极强(硬件不可逆),但"不验证授权"而是"留永久代价" |

---

## 各模式技术细节

### 模式① 本地可写标志位(AOSP 基线)

最朴素。AOSP 规定 bootloader 必须检查 `get_unlock_ability`:

```
开发者选项开 "OEM unlocking"  →  写 persist 分区 get_unlock_ability = 1
fastboot flashing unlock       →  bootloader 检查 get_unlock_ability == 1 ? 放行 : 拒绝
```

- **信任根**:就是 bootloader 代码里那行 `if (get_unlock_ability)`,无密码学
- **运营商锁增强**:支持被锁定的 SKU 联网校验服务器,设备是否被运营商锁定,锁定则永远灰掉 OEM unlocking 开关(Pixel 常见)
- **弱点**:标志位存在 persist 分区,9008/EDL 模式或漏洞可篡改 → 所以才有"强解"

### 模式② Challenge–Response + 服务端签名(小米,最完整)

小米官解看似黑箱,实际是标准的挑战-应答签名机制。Uotan Wiki 逆向出的流程:

```bash
# 1. 解锁工具向设备取 challenge(每次不同)
fastboot getvar token          # 高通平台
fastboot oem get_token         # MTK 平台
# → 设备返回一串动态 token

# 2. 工具拿 token + 产品代号,向小米服务器请求
#    服务器校验:账号资格 / 设备绑定状态 / 等待期 / 名额 / 风控
#    通过 → 用小米私钥签名,返回解锁码,打包成 token.bin

# 3. 把签名凭据喂给设备,设备验签后执行解锁
fastboot stage token.bin
fastboot oem unlock
```

- **信任根**:设备在出厂/ABL 阶段预置了**小米公钥**;签名私钥只在小米服务器
- **凭据**:`token.bin` = 服务端对 (设备 token + 授权信息) 的签名
- **设备端验证**:bootloader 用预置公钥验签,签名合法才执行 `oem unlock`
- **为什么难绕**:即便你跳过答题(曾有 Python 脚本漏洞),服务器不给你签 `token.bin`,设备就不认。攻击面只剩"服务端策略"或"提取设备私钥/预置公钥被攻破"
- **风控也在服务端**:"账号与设备不一致""权限不足""本月次数上限""今年累计上限"全是服务端在签发环节拦截的

### 模式③ 设备绑定静态解锁码(索尼/Motorola)

不动态挑战,而是服务端根据 IMEI 算一个**固定的解锁码**,一次性给你:

```
索尼:  拨号 *#*#7378423#*#* 查 Rooting Status 是否 Bootloader unlock allowed: Yes
       → 官网输入 IMEI + reCAPTCHA → 服务端返回解锁码
       → fastboot oem unlock 0x<解锁码>

Motorola: 绑定 My Moto Care 提交 → 邮箱收解锁文件 → fastboot 解锁
```

- **信任根**:服务端解锁码生成算法(与 IMEI 绑定)+ IMEI 唯一性
- **凭据**:与该设备 IMEI 绑定的固定十六进制码
- **设备端验证**:bootloader 校验"码 ↔ 本机 IMEI"对应关系
- **弱点**:码是静态的、不变的,拿到一次就永久可用;所以服务端加 reCAPTCHA + 设备白名单(Rooting Status 必须是 allowed)防批量。本质是"设备级密钥预共享"

### 模式④ 服务端下发授权标志 + 本地分区校验(OPPO/realme)

OPPO 系的认证动作发生在**深度测试 APK 联网申请**那一步,而不是 fastboot 命令本身:

```
深度测试 APK 联网登录欢太账号 → 申请 → 服务端审核通过
→ 点"开始深度测试" → 服务端下发指令 → 设备自动重启进 fastboot
→ 关键:服务端把"已授权进 fastboot"标志写入 ocdt 分区
→ 此后 fastboot flashing unlock 才能执行(bootloader 检查 ocdt 标志)
```

- **信任根**:`ocdt`(OEM Configuration Data Table)分区的完整性,依赖安全启动链保护该分区不被随意篡改
- **凭据**:无独立凭据,就是 ocdt 分区里的一个授权标志位
- **设备端验证**:bootloader 启动时读 ocdt,标志为"已授权"才允许进 fastboot 解锁
- **关键旁证**:一加手机**出厂 ocdt 就是"已通过深度测试"状态**,所以一加能秒解、无需申请。强解方法就是 **9008 模式刷入一加的 ocdt 分区**,欺骗 BL 校验 → 绕过深度测试限制(代价是只能用 FastbootD,不能用真 fastboot)
- **弱点**:ocdt 可被 9008 EDL 模式强刷替换 → 可绕过服务端授权

### 模式⑤ 物理确认 + eFuse 熔断(三星,不验证只留痕)

三星是反过来的思路——**不验证你是否被授权,而是"谁都能解,但解了就永久烧硬件留痕"**:

```
开 OEM unlocking → 进 Download Mode(私有 Odin 协议,非 fastboot)
→ 长按音量上键 3 秒,物理确认 "Unlock Bootloader?"
→ 高压脉冲烧断 KNOX Warranty Bit eFuse(0x0 → 0x1,不可逆)
→ 设备 wipe → 首次联网,VaultKeeper 服务把状态从 locked 改 unlocked(否则自动回锁)
```

- **信任根**:硬件一次性 eFuse 的**物理不可逆性**
- **凭据**:无,物理按键确认即触发
- **设备端验证**:**不验证授权**,只验证"用户物理确认"。安全靠"熔断的不可逆代价"威慑
- **Secure Boot 公钥**也烧在 OTP fuse 里(出厂时烧入三星公钥),验证整个启动链签名
- **效果**:KNOX 熔断后钱包/健康/Secure Folder/Samsung Pay 永久失效,部分机型相机报废;OneUI 8 起干脆移除解锁功能
- **为何有效**:不需要"认证你",因为熔断本身就是"永久记账",企业 MDM/服务端可据此拒服务

---

## 补充:另一种思路——不解锁,改信任根(avb_custom_key)

一加 9 及之前、部分设备支持**自定义信任根**:

```bash
fastboot flash avb_custom_key my_pubkey.bin   # 把自己的公钥加入 Verified Boot 白名单
fastboot erase avb_custom_key                 # 清除
```

- 不解锁 BL,而是把自己的签名公钥加入信任根 → 可启动自签名镜像,且能保持 BL 锁定(黄 boot 状态)
- 本质:**增删信任根**而非"提权解锁"。GrapheneOS 等就是靠这个在不解锁的前提下装第三方系统

---

## 模式选型建议(自研设备)

| 你的诉求 | 推荐模式 | 理由 |
|----------|----------|------|
| 开放生态、低风险 | ① 本地标志位 + 运营商锁联网校验 | 简单,AOSP 原生 |
| 要可控授权、防批量盗刷 | ② Challenge–Response + 服务端签名 token | 私钥在服务端,设备离线验签,最难绕 |
| 设备离线、无服务端 | ③ 设备绑定静态解锁码 | 适合售后场景,码与 IMEI 绑定 |
| 既要服务端管控又要设备端校验 | ②+④ 组合 | 服务端签发 + 写入受保护分区标志 |
| 强安全、需永久留痕威慑 | ⑤ eFuse 熔断(配合②) | 授权用②,留痕用⑤ |

**最佳实践组合**:模式②(认证鉴权)+ 模式⑤(熔断留痕)。即:服务端签名 token 授权解锁,解锁同时烧一次性 fuse 留不可逆痕迹,便于售后判定与风控。

---

## 参考来源

- AOSP: Lock and unlock the bootloader(get_unlock_ability 机制)— https://source.android.com/docs/core/architecture/bootloader/locking_unlocking
- Uotan Wiki: 解锁 Bootloader(小米 token.bin 流程、OPPO ocdt 分区机制)— https://wiki.uotan.cn/index.php?title=解锁Bootloader
- The Custom Droid: Samsung VaultKeeper 机制 — https://www.thecustomdroid.com/samsung-galaxy-bootloader-unlock-guide
- Samsung Knox 白皮书: Hardware-Backed Security / KNOX Warranty Bit eFuse / Trusted Boot — https://docs.samsungknox.com/admin/fundamentals/whitepaper/samsung-knox-mobile-security/system-security/hw-backed-security
- 维基百科:解锁 Bootloader(各厂难度)— https://zh.wikipedia.org/wiki/解锁Bootloader
