***********************************************
* Table 4
*
* author: Felipe Jordan
***********************************************

*Import Data***********************************
cap global data_path = "/Users/felipe/projects/the-diversity-we-breath"


insheet using "$data_path/data/final/leaksAsObs/LeaksData_Radio_500.csv", c clear
keep if grade==3
drop if town=="CAMBRIDGE"

global esttab_options		starlevels(* 0.1 ** 0.05 *** 0.01) ///
							 noconstant   replace compress	 ///
							 booktabs	 nonotes 	nonumbers		 b(3)   se(3)

global conley_th 2
global radio 0.5
***********************************************
****NEW VARIABLES

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
global ER_SHARES er1_share er2_share er3_share er4_share er5_share er6_share er7_share
global infrastructure density log_closer_g1
global demo_controls occu_frac pop_density average_age female_frac
global econ_controls poverty_rate rent_frac l_pc_income lim_english e_highschool_frac-e_graduate_frac


* ADD DEMO & ECON CONTROLS

foreach v in soccon_0810 soccoh_0810 socnet_0810 intgenclos_0810 recipexch_0810 ns2 nbhdinv_0810{
	summarize `v'	
	replace `v' = (`v' -r(mean))/r(sd)
}

foreach v in soccon_0810 soccoh_0810 socnet_0810 intgenclos_0810 recipexch_0810 ns2 nbhdinv_0810{
xi: acreg `v' ethno_racial_frac $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls , spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto R`v'
}

esttab R* using "$data_path/results/table4a.tex", $esttab_options keep(ethno_racial_frac)

gen m=.
foreach v in soccon_0810 soccoh_0810 socnet_0810 intgenclos_0810 recipexch_0810 ns2 nbhdinv_0810{
replace m=`v'
xi: acreg repaired m $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
est sto F`v'
}

esttab F* using "$data_path/results/table4b.tex", $esttab_options keep(m)

