# SBW 的 R 对照实现，供本地 Codex 执行和核验。
# 状态：2026-09-07 已用 R 4.4.3、optweight 2.0.1、osqp 1.0.0 实测。
# 共同索引下 2,000 次 bootstrap 全部通过，与 Python 参考差异小于 1e-5。
# 调用：Rscript sbw_optweight.R sbw-trial.csv r-results bootstrap-indices.csv.gz
# 第三个参数可省略；提供它时使用与 Python 完全相同的重抽样索引。
# 索引文件：每行一次 bootstrap，每列一个抽取位置，位置编号从 1 开始。

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  stop("用法：Rscript sbw_optweight.R <CSV路径> <输出目录> [共同索引.csv.gz]")
}
if (!requireNamespace("optweight", quietly = TRUE)) {
  stop("请先安装 optweight：install.packages('optweight')")
}
csv_path <- args[1]
out_dir <- args[2]
covariates <- c("age", "education", "pre_income")
metrics <- c("income_ate", "employment_rd", "employment_rr", "income_mw")
d <- read.csv(csv_path, fileEncoding = "UTF-8-BOM", check.names = FALSE)
required <- c("A", covariates, "income", "employed")
if (!all(required %in% names(d))) stop("输入 CSV 缺少必需列")
d <- d[required]
if (!all(vapply(d, is.numeric, logical(1)))) stop("所有必需列都应为数值型")
if (!all(is.finite(as.matrix(d)))) stop("输入存在缺失或无限值")
if (!all(d$A %in% c(0, 1)) || !all(d$employed %in% c(0, 1))) {
  stop("A 和 employed 必须取 0/1")
}

fit_weights <- function(dat, covs = covariates) {
  # 精确平衡到每次抽样自己的全样本均值；没有使用结果变量。
  X <- as.matrix(dat[covs])
  scale_x <- apply(X, 2, sd)
  if (any(!is.finite(scale_x)) || any(scale_x < 1e-12)) {
    stop("协变量为常数或样本不足")
  }
  for (arm in c(0, 1)) {
    z <- scale(X[dat$A == arm, , drop = FALSE],
               center = colMeans(X), scale = scale_x)
    h <- cbind(1, z)
    if (nrow(h) == 0 || qr(h)$rank < ncol(h)) stop("组内变量完全共线或组为空")
  }
  ow <- optweight::optweight(
    reformulate(covs, response = "A"), data = dat,
    estimand = "ATE", norm = "l2",
    tols = 0, target.tols = 0, min.w = 0,
    solver = "osqp", eps_abs = 1e-9, eps_rel = 1e-9
  )
  w <- as.numeric(ow$weights)
  if (length(w) != nrow(dat) || !all(is.finite(w)) || min(w) < -1e-9) {
    stop("权重长度、有穷性或非负性检查失败")
  }
  # 只清除浮点误差造成的极小负数，随后重新检查全部约束。
  w[w < 0] <- 0
  for (arm in c(0, 1)) {
    m <- dat$A == arm
    if (abs(sum(w[m]) / sum(m) - 1) > 1e-7) stop("组内权重均值不等于 1")
    after <- colSums(X[m, , drop = FALSE] * w[m]) / sum(w[m])
    if (max(abs(after - colMeans(X)) / scale_x) > 1e-7) {
      stop("协变量未达到规定的数值平衡精度")
    }
  }
  w
}

effects <- function(dat, w) {
  m0 <- dat$A == 0
  m1 <- dat$A == 1
  mu0 <- weighted.mean(dat$income[m0], w[m0])
  mu1 <- weighted.mean(dat$income[m1], w[m1])
  p0 <- weighted.mean(dat$employed[m0], w[m0])
  p1 <- weighted.mean(dat$employed[m1], w[m1])
  if (min(p0, p1) <= 0) stop("某组就业率为零，无法使用 log(RR) 区间")
  # 两组独立配对，收入相同计半分，按两人的权重乘积求平均。
  scores <- outer(dat$income[m1], dat$income[m0],
                  function(x, y) (x > y) + 0.5 * (x == y))
  mw <- sum(scores * outer(w[m1], w[m0])) / (sum(w[m1]) * sum(w[m0]))
  setNames(c(mu1 - mu0, p1 - p0, p1 / p0, mw), metrics)
}

w <- fit_weights(d)
point <- effects(d, w)
raw <- effects(d, rep(1, nrow(d)))
if (length(args) >= 3) {
  con <- if (grepl("\\.gz$", args[3])) gzfile(args[3], "rt") else file(args[3], "rt")
  indices <- as.matrix(read.csv(con, header = FALSE))
  close(con)
  if (ncol(indices) != nrow(d) || any(!is.finite(indices)) ||
      any(indices < 1 | indices > nrow(d) | indices != floor(indices))) {
    stop("共同重抽样索引无效")
  }
} else {
  set.seed(20260910)
  indices <- t(replicate(2000, sample.int(nrow(d), nrow(d), replace = TRUE)))
}
B <- nrow(indices)
draws <- matrix(NA_real_, nrow = B, ncol = length(metrics),
                dimnames = list(NULL, metrics))
for (b in seq_len(B)) {
  # 每次重新求取目标均值和权重；失败则终止，不删除失败的重抽样。
  db <- d[indices[b, ], , drop = FALSE]
  rownames(db) <- NULL
  draws[b, ] <- tryCatch(effects(db, fit_weights(db)),
                         error = function(e) stop(sprintf("Bootstrap %d 失败：%s", b, e$message)))
}
transformed <- draws
transformed[, "employment_rr"] <- log(draws[, "employment_rr"])
center <- point
center["employment_rr"] <- log(point["employment_rr"])
se <- apply(transformed, 2, sd)
interval <- cbind(center - 1.96 * se, center + 1.96 * se)
interval["employment_rr", ] <- exp(interval["employment_rr", ])
summary <- data.frame(metric = metrics, unadjusted = unname(raw), sbw = unname(point),
                      se_working_scale = unname(se), ci_low = interval[, 1],
                      ci_high = interval[, 2],
                      se_scale = c("original", "original", "log_RR", "original"))

balance <- do.call(rbind, lapply(c(0, 1), function(arm) {
  m <- d$A == arm
  data.frame(arm = arm, covariate = covariates,
             target = colMeans(d[covariates]), before = colMeans(d[m, covariates]),
             after = vapply(d[m, covariates], weighted.mean, numeric(1), w = w[m]))
}))
diagnostics <- do.call(rbind, lapply(c(0, 1), function(arm) {
  wa <- w[d$A == arm]
  data.frame(arm = arm, n = length(wa), weight_sum = sum(wa), max_weight = max(wa),
             zero_share = mean(wa <= 1e-10), weight_ess = sum(wa)^2 / sum(wa^2))
}))
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
write.csv(summary, file.path(out_dir, "effects.csv"), row.names = FALSE)
write.csv(balance, file.path(out_dir, "balance.csv"), row.names = FALSE)
write.csv(cbind(d, sbw = w), file.path(out_dir, "weighted-data.csv"), row.names = FALSE)
write.csv(draws, file.path(out_dir, "bootstrap.csv"), row.names = FALSE)
write.csv(diagnostics, file.path(out_dir, "diagnostics.csv"), row.names = FALSE)
capture.output(sessionInfo(), file = file.path(out_dir, "session-info.txt"))
print(summary, digits = 9, row.names = FALSE)
print(diagnostics, digits = 9, row.names = FALSE)
cat("已完成", B, "次 bootstrap；输出目录：", out_dir, "\n")
