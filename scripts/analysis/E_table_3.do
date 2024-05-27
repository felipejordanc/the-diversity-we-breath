***********************************************
* Table 3
*
* author: Felipe Jordan
***********************************************

*Import Data***********************************
cap global data_path = "/Users/felipe/projects/the-diversity-we-breath"


insheet using "$data_path/data/final/leaksAsObs/LeaksData_Radio_500.csv", c clear
keep if grade==3

global esttab_options		starlevels(* 0.1 ** 0.05 *** 0.01) ///
							 noconstant   replace compress	 ///
							 booktabs	 nonotes 	nonumbers		 b(3)   se(3)

global conley_th 2
global radio 0.5
***********************************************
****NEW VARIABLES
gen leng1_share = leng1 / total_hh_leng
gen leng2_share = leng2 / total_hh_leng
gen leng3_share = leng3 / total_hh_leng
gen leng4_share = leng4 / total_hh_leng
gen leng5_share = leng5 / total_hh_leng

* Individual shares
gen er1_share = nl_white / nl_total
gen er2_share = nl_black / nl_total
gen er3_share = nl_native / nl_total
gen er4_share = nl_asian / nl_total
gen er5_share = nl_other / nl_total
gen er6_share = nl_multiple / nl_total
gen er7_share = nl_latino / nl_total

* Density of leaks
gen density = (total1) / (3.14*($radio)^2)
gen pop_density =tot_pop / (1000*3.14*($radio)^2)
gen l_pc_income = log(pc_income)



* Regressions *********************************
* DEFINE SETS OF CONTROLS
global LENG_SHARES leng1_share leng2_share leng3_share leng4_share
global ER_SHARES er1_share er2_share er3_share er4_share er5_share er6_share er7_share
global infrastructure density log_closer_g1
global demo_controls occu_frac pop_density average_age female_frac
global econ_controls poverty_rate rent_frac l_pc_income lim_english e_highschool_frac-e_graduate_frac

* Summarize diversity indices
summ ethno_racial_frac ling_frac dis_idx iso_idx spp_idx con_idx, d 
* trim con_idx between -1 to 1, for which a small fraction (only ten cases) is less than -1 given discrete approximation
count if con_idx<-1
replace con_idx=-1 if con_idx<-1

* BASELINE
gen V = ling_frac
xi: acreg repaired V $ER_SHARES $LENG_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto IDX_0
xi: acreg repaired V ethno_racial_frac  $ER_SHARES $LENG_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto ETIDX_0

replace V = dis_idx
xi: acreg repaired V $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto IDX_1
xi: acreg repaired V ethno_racial_frac  $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto ETIDX_1

replace V = iso_idx
xi: acreg repaired V $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto IDX_2
xi: acreg repaired V ethno_racial_frac  $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto ETIDX_2

replace V = spp_idx
xi: acreg repaired V $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto IDX_3
xi: acreg repaired V ethno_racial_frac  $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto ETIDX_3

replace V = con_idx
xi: acreg repaired V $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto IDX_4
xi: acreg repaired V ethno_racial_frac  $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto ETIDX_4


esttab IDX_* using "$data_path/results/table3a.tex", $esttab_options keep(V)
esttab ETIDX_* using "$data_path/results/table3b.tex", $esttab_options keep(ethno_racial_frac V)



