# HeadingReward

$$
R_{\mathrm{heading}}
= \exp\!\left(
-\frac{1}{4}
\left[
\frac{\Delta\psi^2}{\sigma_\psi^2}
+ \frac{\Delta h^2}{\sigma_h^2}
+ \frac{\phi^2}{\sigma_\phi^2}
+ \frac{\Delta u^2}{\sigma_u^2}
\right]
\right)
$$

（与四项高斯因子之几何平均等价。$\Delta\psi$、$\Delta h$、$\phi$、$\Delta u$ 分别为航向误差（$^\circ$）、高度误差（m）、滚转角（rad）、纵向速度误差（m/s）；$\sigma_\psi{=}5$，$\sigma_h{=}15.24$，$\sigma_\phi{=}0.35$，$\sigma_u{=}24$。可乘 `HeadingReward_scale` 并经 `_process` 做势函数整形。）
