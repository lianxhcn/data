
global path "D:\github_lianxh\data\stata"
cd $path

*-Cepni-2024-EE-xtabond2 

尚未完成：https://chatgpt.com/share/6977ab16-1a70-8005-a963-e438e75d2a74

  cd "D:\stata\personal\PX_B_2026a\B2_DPanel\Cepni-2024-EE-xtabond2-DID-robust\Data_Code_Lian"
  use "_00_main_reg.dta", clear 
  des, fullnames


  keep ///
    GVKEY GVKEY_num year ///
    GICIndustries GICSectors industry_num state ///
    CoE ///
    ln_cc_expo cc_expo ///
    ln_op_expo ln_rg_expo ln_ph_expo ///
    firmSize bm npm roa debt_at rd_sale ///
    ESGScore EScore ///
    AssetsTotal beta ///
    int_totdebt pe_inc ///
    capital_ratio cash_lt evm

  * 2) double -> float（立刻减半存储空间）
/*
    ds, has(type double)
    foreach v of varlist `r(varlist)' {
        recast float `v'
    }    
*/
    
  compress
  
  label data "Cepni 2024, EE, 10.1016/j.eneco.2023.107288"
  char _dta[ref] "getiref 10.1016/j.eneco.2023.107288"
  
  save "$path/Cepni_2024_EE.dta", replace
  dir Cep*
  
  
*- Ding2024_mini.dta
* Goal: 转存一份精简的数据, 用于演示 heckman 估计过程
  
  preserve 
      use "$data/data2.dta", clear
      gen ESGDUM = (ESG != .)
      label var ESGDUM "equals one if a firm discloses ESG information and zero otherwise"
      gen L_Outside = L.Outside  
      label var Outside "whether a firm is audited by overseas auditing companies"
      
      //---- 1st stage
      gen Citycd_Year=Citycd*Year
      winsor2 $SW, replace cuts(1 99) 
      xtprobit ESGDUM L_DFI $X L_Outside, vce(cluster Stkcd) 
      gen Sample_1st = e(sample)  //标记第一阶段的样本 
      
      local vlist "ESGDUM Citycd Stkcd Year $X L_DFI L_Outside"
      qui reg `vlist'
      keep if Sample_1st
      keep ESG `vlist'
      label data "Ding-2024-EE, 10.1016/j.eneco.2024.107387"
      save "$data/Ding2024_mini.dta", replace
  restore 
*----------------------------------------------------  
  
  
*-2026/1/26 17:40
  
  * net get st0715.pkg, from(http://www.stata-journal.com/software/sj23-2)

  local fn "kpr2021_hpdata"
  use "`fn'", clear
  
  label data "Ditzen 2023 SJ23-2, 10.1177/1536867X231175305"
  char _dta[ref1] "getiref 10.1177/1536867X231175305"
  char _dta[ref2] "getiref 10.1016/j.jeconom.2020.05.001"
  char _dta[datasource] "Kapetanios, Pesaran, and Reese (2021, JoE), https: //doi.org/10.1016/j.jeconom.2020.05.001"
  
  label var d_lrhp "rate of change of real house prices after seasonal adjustment and nominal price deflation"
  save "`fn'", replace 


*-2026/1/26 10:08


  use "smoking", clear
  label data "Aabdie 2010 https://doi.org/10.1198/jasa.2009.ap08746"
  save "smoking", replace 
  
  * net get synth.pkg, replace   
  use "synth_smoking", clear
  label data "Chen 2023 https://journals.sagepub.com/doi/10.1177/1536867X231195278"
  save "synth_smoking", replace 
  
  
  use "Hansen1999", clear
  label data "Wang 2015 https://journals.sagepub.com/doi/10.1177/1536867X1501500108"
  save "Hansen1999", replace

