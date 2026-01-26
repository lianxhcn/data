# data

datasets used for blogs in https://www.lianxh.cn

- [list of datasets](https://github.com/lianxhcn/data/blob/main/_list_of_datastes.md)

## .dta 导入方法

```stata
* Du2021EE_ERdata.dta
use "https://github.com/lianxhcn/data/raw/refs/heads/main/stata/Du2021EE_ERdata.dta", clear
```

or

```stata
global gitdata "https://github.com/lianxhcn/data/raw/refs/heads/main/stata"

use "$gitdata/Du2021EE_ERdata.dta", clear

use "$gitdata/hansen1999.dta", clear
```

