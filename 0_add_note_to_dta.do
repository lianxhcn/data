
global path "D:\github_lianxh\data"
cd $path

*-2026/1/26 10:08
/*
  use "smoking", clear
  label data "Aabdie 2010 https://doi.org/10.1198/jasa.2009.ap08746"
  save "smoking", replace 
  
  use "synth_smoking", clear
  label data "Chen 2023 https://journals.sagepub.com/doi/10.1177/1536867X231195278"
  save "synth_smoking", replace 
  
  use "Hansen1999", clear
  label data "Wang 2015 10.1177/1536867X1501500108"
  save "Hansen1999", replace
*/