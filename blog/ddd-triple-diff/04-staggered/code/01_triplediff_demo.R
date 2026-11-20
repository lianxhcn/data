# =====================================================================
# 三重差分 (DDD) 之四：交错处理下的估计
# triplediff 最小示例：RA / IPW / DR 三类估计量与事件研究聚合
# 运行环境：R 4.6.2，triplediff 0.2.4
# 如需切换工作目录，请把下一行的注释打开并改为本机完整路径 (使用正斜杠)
# setwd("C:/your-path/04-交错处理")
# =====================================================================

# ---- 0. 环境信息 ---------------------------------------------------
cat("R version:", R.version.string, "\n")
cat("triplediff version:", as.character(packageVersion("triplediff")), "\n")
suppressMessages(library(triplediff))
set.seed(2025)

# ---- 1. 生成交错处理的三期面板数据 ----------------------------------
# 三个时期 time = 1,2,3；处理队列 state = 2,3；state = 0 表示从未处理
# partition = 1 表示符合资格，0 表示不符合
d <- gen_dgp_mult_periods(size = 5000, dgp_type = 1)$data
cat("\nDimensions:", nrow(d), "rows x", ncol(d), "cols\n")
cat("Periods:", sort(unique(d$time)), "\n")
cat("Cohorts (state):", sort(unique(d$state)), "\n")
cat("\nCohort x eligibility counts (one period):\n")
print(table(d$state[d$time == 1], d$partition[d$time == 1]))

# ---- 2. 三类估计量：DR / RA / IPW -----------------------------------
# 真实参数为 ATT(2,2)=10, ATT(2,3)=20, ATT(3,3)=25
fit_dr  <- ddd(yname = "y", tname = "time", idname = "id", gname = "state",
               pname = "partition", xformla = ~cov1 + cov2 + cov3 + cov4,
               data = d, control_group = "nevertreated",
               base_period = "varying", est_method = "dr")

fit_ra  <- ddd(yname = "y", tname = "time", idname = "id", gname = "state",
               pname = "partition", xformla = ~cov1 + cov2 + cov3 + cov4,
               data = d, control_group = "nevertreated",
               base_period = "varying", est_method = "reg")

fit_ipw <- ddd(yname = "y", tname = "time", idname = "id", gname = "state",
               pname = "partition", xformla = ~cov1 + cov2 + cov3 + cov4,
               data = d, control_group = "nevertreated",
               base_period = "varying", est_method = "ipw")

extract <- function(obj) {
  data.frame(group = obj$groups, time = obj$periods,
             ATT = round(obj$ATT, 3), SE = round(obj$se, 3))
}
cat("\n=== DR (doubly robust) ===\n")
print(extract(fit_dr))
cat("\n=== RA (regression adjustment) ===\n")
print(extract(fit_ra))
cat("\n=== IPW (inverse probability weighting) ===\n")
print(extract(fit_ipw))

# ---- 3. 两类对照组：never-treated vs not-yet-treated ----------------
fit_nyt <- ddd(yname = "y", tname = "time", idname = "id", gname = "state",
               pname = "partition", xformla = ~cov1 + cov2 + cov3 + cov4,
               data = d, control_group = "notyettreated",
               base_period = "varying", est_method = "dr")
cat("\n=== DR with not-yet-treated controls ===\n")
print(extract(fit_nyt))

# ---- 4. 事件研究聚合 ------------------------------------------------
es <- agg_ddd(fit_dr, type = "eventstudy")
cat("\n=== Event-study aggregation ===\n")
print(es)

# ---- 5. 其他聚合：simple / group / calendar -------------------------
simple <- agg_ddd(fit_dr, type = "simple")
group  <- agg_ddd(fit_dr, type = "group")
cal    <- agg_ddd(fit_dr, type = "calendar")
cat("\n=== Simple overall ATT ===\n"); print(simple)
cat("\n=== Group aggregation ===\n"); print(group)
cat("\n=== Calendar aggregation ===\n"); print(cal)

# ---- 6. 乘子 bootstrap 与同时置信带 ---------------------------------
fit_boot <- ddd(yname = "y", tname = "time", idname = "id", gname = "state",
                pname = "partition", xformla = ~cov1 + cov2 + cov3 + cov4,
                data = d, control_group = "nevertreated",
                base_period = "varying", est_method = "dr",
                boot = TRUE, nboot = 999, cband = TRUE)
cat("\n=== Multiplier bootstrap (999), uniform confidence band ===\n")
print(fit_boot)

cat("\nDemo finished.\n")
