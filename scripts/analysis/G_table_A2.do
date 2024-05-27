***********************************************
* Table A2
*
* author: Felipe Jordan
***********************************************

*Import Data***********************************
cap global data_path = "/Users/felipe/projects/the-diversity-we-breath"


insheet using "$data_path/data/final/leaksAsObs/LeaksData_Radio_500.csv", c clear
keep if grade==3

* trim con_idx between -1 to 1, for which a small fraction (only ten cases) is less than -1 given discrete approximation
count if con_idx<-1
replace con_idx=-1 if con_idx<-1

* Correlation between them
pwcorr ethno_racial_frac ling_frac dis_idx iso_idx spp_idx con_idx,  sig 
