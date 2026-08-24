version 17.0
cd "D:/github_lianxh/data/blog/reproai-stata/reference-package"
estimates use "data/regression_robust.ster"
matrix list e(V)
display _se[mpg]
display _se[weight]
display _se[1.foreign]
display _se[foreign]
exit
