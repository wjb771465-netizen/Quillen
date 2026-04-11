# PostureReward

总奖励为各敌机分项之和；每项为**朝向因子**与**距离因子**的乘积。距离自仿真以米计，代码中除以 $1000$ 得到千米 $R$。

$$
R_{\mathrm{posture}}
= \sum_{\text{enemy}}
f_{\mathrm{orn}}(AO,\, TA)\cdot f_{\mathrm{range}}(R),\qquad
R = \frac{R_{\mathrm{m}}}{1000}
$$

$AO$、$TA$ 为方位角与目标角（rad），由 `get_AO_TA_R` 计算；默认朝向版本 `v2`、距离版本 `v3`，目标距离 `target_dist` 记为 $d_{\mathrm{tgt}}$（默认 $3$ km）。

---

## 朝向因子 $f_{\mathrm{orn}}(AO,\, TA)$

记 $\varepsilon = 10^{-4}$，

$$
z = \max\!\left(\frac{2\,TA}{\pi},\, \varepsilon\right),\qquad
g(TA) = \min\!\left(\frac{\operatorname{arctanh}(1-z)}{2\pi},\, 0\right) + 0.5
$$

### v0

$$
f_{\mathrm{orn}}^{\mathrm{v0}}
= \frac{1 - \tanh\!\bigl(9(AO - \pi/9)\bigr)}{3} + \frac{1}{3}
+ g(TA)
$$

### v1

$$
f_{\mathrm{orn}}^{\mathrm{v1}}
= \frac{1 - \tanh\!\bigl(2(AO - \pi/2)\bigr)}{2}
\cdot \frac{\operatorname{arctanh}(1-z)}{2\pi} + 0.5
$$

### v2（默认）

$$
f_{\mathrm{orn}}^{\mathrm{v2}}
= \frac{1}{\dfrac{50\,AO}{\pi} + 2} + \frac{1}{2} + g(TA)
$$

---

## 距离因子 $f_{\mathrm{range}}(R)$

$R$ 单位为 km；$\sigma$ 表示 $\mathrm{sign}$。

### v0

$$
f_{\mathrm{range}}^{\mathrm{v0}}(R)
= \frac{\exp\!\bigl(-(R - d_{\mathrm{tgt}})^2 \cdot 0.004\bigr)}
{1 + \exp\!\bigl(-(R - d_{\mathrm{tgt}} + 2)\cdot 2\bigr)}
$$

### v1

$$
f_{\mathrm{range}}^{\mathrm{v1}}(R)
= \mathrm{clip}\!\left(
\frac{1.2 \cdot \min\!\bigl(\exp(-(R - d_{\mathrm{tgt}})\cdot 0.21),\, 1\bigr)}
{1 + \exp\!\bigl(-(R - d_{\mathrm{tgt}} + 1)\cdot 0.8\bigr)},\,
0.3,\, 1
\right)
$$

### v2

与 v1 相同内层表达式，再与 $\sigma(7-R)$ 取较大值：

$$
f_{\mathrm{range}}^{\mathrm{v2}}(R)
= \max\!\left( f_{\mathrm{range}}^{\mathrm{v1}}(R),\, \sigma(7-R) \right)
$$

（$\sigma(7-R)$ 在 $R<7$ 为 $+1$，$R>7$ 为 $-1$，$R=7$ 为 $0$。）

### v3（默认）

$$
f_{\mathrm{range}}^{\mathrm{v3}}(R)
= \mathbf{1}_{R<5}
+ \mathbf{1}_{R\ge 5}\cdot \mathrm{clip}(-0.032 R^2 + 0.284 R + 0.38,\, 0,\, 1)
+ \mathrm{clip}(\exp(-0.16 R),\, 0,\, 0.2)
$$

（可乘 `PostureReward_scale` 并经 `_process` 做势函数整形；分项名含 `_orn`、`_range`。）
