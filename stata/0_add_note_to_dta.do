
global path "D:\github_lianxh\data\stata"
cd $path



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

