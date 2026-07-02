# Coding/Token Plan

## Opencode GO

### 实测记录

- Requests: 604
  - GLM-5.2：376
  - Kimi K2.7 Code: 91
  - Deepseek V4 Flash: 71
  - Mimimax M3: 27
- Total Tokens: 39.16M
  - GLM-5.2：30.26M
  - Kimi K2.7 Code: 5.94M
  - Deepseek V4 Flash: 2.07M
  - Mimimax M3: 170.82K
- Input Tokens: 38.75M
- Output Tokens: 401.68K
- Cached Tokens: 29.41M（75.9%）
- Total Cost: $18.8
- Avg Latency: 23265.02ms

### 换算额度

- Requests: 2000
- Total Tokens: 125M
- Total Cost: $60

### 总结

整体来说是非常不划算的。

对于高强度使用的情况，每天应该消耗在 0.5-2 亿 Token，这个套餐算总配额也就只够用一天。就算是低强度，大概也就只够用一周左右。

但这也是为数不多国内能够用上 GLM-5.2 的性价比比较高的途径（官方的套餐基本上可以认为是不放货的，只能买海外版贵三倍）。

比较适合想要尝鲜试用国内模型的用户。

> [!ATTENTION]
>
> 另外需要注意的是 Opencode GO 的 Deepseek 和 Mimo 都还是原价，在套餐里使用这两个模型都是巨亏的，甚至不如直接按量付费，请不要使用这两个模型。

> [!NOTE]
>
> 另外截至目前 Opencode GO 的 GLM 供应商使用的是 q8 量化的模型，虽然几乎可以认为是满血，但也需要注意。
