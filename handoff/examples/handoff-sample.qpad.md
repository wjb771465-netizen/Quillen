---
quillen_pad:
  version: 1
  kind: report
  title: "推荐系统迭代复盘报告（Q1）"
  lang: zh-CN
template: report
layout:
  list_left: 0
  list_hanging: 0
---

# 背景与目标

## 问题描述

上季度用户留存率环比下降 **3.2%**，归因分析指向推荐多样性不足——头部内容过度曝光，用户产生审美疲劳。

## 本次迭代目标

| 目标维度 | 上季度基线 | 本季度目标 | 实际达成 |
|----------|-----------|-----------|---------|
| 点击率 (CTR) | 8.1% | 9.0% | **9.1%** ✅ |
| 长尾内容占比 | 11% | 18% | 14% ⚠️ |
| 新用户满意度 | 3.2 / 5 | 3.8 / 5 | 3.4 / 5 ❌ |
| NDCG@10 | 0.61 | 0.66 | **0.68** ✅ |

---

# 系统架构变更

## 召回层：双塔模型替换协同过滤

原有方案使用基于 ItemCF 的协同过滤，候选集生成依赖共现矩阵：

$$
\text{sim}(i, j) = \frac{\sum_{u} r_{ui} \cdot r_{uj}}{\sqrt{\sum_u r_{ui}^2} \cdot \sqrt{\sum_u r_{uj}^2}}
$$

新方案改用双塔模型，用户侧与物品侧分别编码，内积打分：

$$
\hat{y}_{ui} = \langle \mathbf{e}_u,\ \mathbf{e}_i \rangle = \sum_{k=1}^{d} e_{u,k} \cdot e_{i,k}
$$

其中 $d = 128$，训练目标为 in-batch softmax：

$$
\mathcal{L} = -\frac{1}{N} \sum_{n=1}^{N} \log \frac{\exp(\hat{y}_{u_n i_n} / \tau)}{\sum_{j=1}^{B} \exp(\hat{y}_{u_n i_j} / \tau)}
$$

$\tau$ 为温度系数，实验中取 $\tau = 0.05$。

## 排序层：LambdaRank

排序模型从 LR 升级为 LambdaRank，梯度定义如下：

$$
\lambda_{ij} = \frac{-\sigma}{1 + e^{\sigma(s_i - s_j)}} \cdot |\Delta \text{NDCG}_{ij}|
$$

其中 $s_i, s_j$ 为模型对文档 $i, j$ 的打分，$|\Delta \text{NDCG}_{ij}|$ 为交换两文档后 NDCG 的绝对变化量。

## 重排层：MMR 多样性控制

使用 Maximal Marginal Relevance 控制结果多样性：

$$
\text{MMR} = \arg\max_{d_i \in R \setminus S} \left[ \lambda \cdot \text{Rel}(d_i) - (1-\lambda) \cdot \max_{d_j \in S} \text{Sim}(d_i, d_j) \right]
$$

当前 $\lambda = 0.7$，倾向相关性；后续可考虑动态调整。

---

# 实验设计

## A/B 分流方案

- 实验组（双塔 + LambdaRank）：**20%** 流量
- 对照组（ItemCF + LR）：**20%** 流量
- 实验周期：2025-01-06 至 2025-01-20（两周）

## 核心指标定义

- **CTR**：$\text{CTR} = \frac{\text{点击次数}}{\text{曝光次数}}$
- **NDCG@K**：

$$
\text{NDCG@K} = \frac{\text{DCG@K}}{\text{IDCG@K}}, \quad \text{DCG@K} = \sum_{i=1}^{K} \frac{2^{r_i} - 1}{\log_2(i+1)}
$$

- **长尾内容占比**：曝光中尾部 20% 物料（按热度排序）的占比

---

# 效果数据

## 离线评估

```
模型对比（测试集）：
─────────────────────────────────────────
模型            Precision@10   NDCG@10   AUC
─────────────────────────────────────────
ItemCF + LR     0.312          0.610     0.741
双塔 + LR       0.334          0.641     0.768
双塔 + Lambda   0.351          0.683     0.779
─────────────────────────────────────────
```

## 在线 A/B 结果

```python
# 简化统计显著性检验（双尾 t-test）
from scipy import stats

control_ctr = [0.081, 0.079, 0.083, ...]  # 对照组每日 CTR
treatment_ctr = [0.090, 0.092, 0.091, ...]  # 实验组每日 CTR

t_stat, p_value = stats.ttest_ind(control_ctr, treatment_ctr)
print(f"t={t_stat:.3f}, p={p_value:.4f}")
# 输出：t=-4.821, p=0.0003  → 显著
```

---

# 问题与风险

## 长尾曝光不达标

- **现象：** 长尾占比仅达 14%，目标 18%
- **原因假设：** 双塔训练数据本身偏向热门物料，embedding 空间中冷门内容聚集在边缘
- **待验证：** 对冷门物料做 embedding 上采样后重新训练

## 冷启动未改善

新用户前 3 次请求无历史行为，双塔退化为随机召回。建议：

1. 引入用户画像侧特征（设备、地区、注册渠道）
2. 设计独立冷启动召回路径，与主路径合并排序

## 线上延迟波动

| 阶段 | P50 延迟 | P99 延迟 | 目标 P99 |
|------|---------|---------|---------|
| 召回 | 18ms | 67ms | 50ms ❌ |
| 排序 | 12ms | 34ms | 40ms ✅ |
| 重排 | 5ms | 11ms | 20ms ✅ |

召回层 P99 超标，需对 ANN 检索做缓存优化。

---

# 下一步计划（Q2）

- [ ] 冷启动专项：引入用户画像特征，目标新用户满意度 ≥ 3.7
- [ ] 长尾治理：embedding 上采样 + 曝光惩罚机制
- [ ] 延迟优化：召回结果缓存，P99 目标压至 50ms 以内
- [ ] 多目标排序：在 CTR 之外引入时长、完播率联合优化

---

# 附录

## 关键素材 / 数据

- 实验日志路径：`s3://rec-logs/2025-q1-ab/`
- 离线评估脚本：`/repo/eval/ndcg_eval.py`
- 用户满意度调研原始数据：见附件（survey_q1.xlsx）

## 禁区

- ❌ 不要把"长尾目标未达成"写成成功，数据是 14% vs 目标 18%，如实呈现
- ❌ 不要出现"积极推进""稳步提升"等空洞措辞
- ❌ 冷启动问题未解决，不要在结论里轻描淡写带过
- ⚠️ 奎琳注意：延迟数据是初步测量，上线版本可能有出入，排版时加"待确认"备注
