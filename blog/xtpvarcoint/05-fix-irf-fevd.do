*! 03-fix-irf-fevd.do
*! 自包含修复：正确的简化式 IRF（B=I）与 FEVD，结果存 Stata 矩阵
clear all
set more off

webuse grunfeld, clear
xtset company year
xtpvarcoint pvar invest mvalue kstock, lags(2) type(const)

mata:
mata set matastrict off
void _fix_irf_fevd(real scalar n_ahead)
{
  real scalar K, p, h, j, jmax, a, b
  real matrix A, Aj, IRF, FEVD, cum, mse, th
  pointer colvector PHI

  A = st_matrix("_xpvc_A")
  K = rows(A)
  p = st_numscalar("_xpvc_max_p")

  // 正确的 MA 系数递推：每个指针指向独立新矩阵
  PHI = J(n_ahead+1, 1, NULL)
  PHI[1] = &(I(K))
  for (h=1; h<=n_ahead; h++) {
    PHI[h+1] = &(J(K,K,0))
    jmax = min((h,p))
    for (j=1; j<=jmax; j++) {
      Aj = A[., (j-1)*K+1..j*K]
      *PHI[h+1] = *PHI[h+1] + *PHI[h-j+1]*Aj
    }
  }

  // 简化式 IRF（B=I，theta=phi），向量化为 (n_ahead+1) x K*K
  IRF = J(n_ahead+1, K*K, 0)
  for (h=0; h<=n_ahead; h++) {
    th = *PHI[h+1]
    for (a=1; a<=K; a++)
      for (b=1; b<=K; b++)
        IRF[h+1, (a-1)*K+b] = th[a,b]
  }

  // FEVD：累积平方后按行归一化
  FEVD = J(n_ahead+1, K*K, 0)
  cum = J(K,K,0)
  for (h=0; h<=n_ahead; h++) {
    th = *PHI[h+1]
    cum = cum + th:^2
    mse = rowsum(cum)
    mse = mse + (mse:==0)
    for (a=1; a<=K; a++)
      for (b=1; b<=K; b++)
        FEVD[h+1, (a-1)*K+b] = cum[a,b]/mse[a]
  }

  st_matrix("_fix_IRF", IRF)
  st_matrix("_fix_FEVD", FEVD)
}
_fix_irf_fevd(8)
end

// 列名设置后查看
matrix colnames _fix_IRF = i->i i->m i->k m->i m->m m->k k->i k->m k->k
matrix rownames _fix_IRF = h0 h1 h2 h3 h4 h5 h6 h7 h8
matrix list _fix_IRF, format(%7.4f)

matrix colnames _fix_FEVD = shock_i shock_m shock_k shock_i shock_m shock_k shock_i shock_m shock_k
matrix rownames _fix_FEVD = h0 h1 h2 h3 h4 h5 h6 h7 h8
matrix list _fix_FEVD, format(%7.4f)
