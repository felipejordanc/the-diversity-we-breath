***********************************************
* Table A5
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
gen pop_density =tot_pop / (3.14*($radio)^2)
gen l_pc_income = log(pc_income)

* Regressions *********************************
* DEFINE SETS OF CONTROLS
global ER_SHARES er1_share er2_share er3_share er4_share er5_share er6_share er7_share
global infrastructure density log_closer_g1
global demo_controls occu_frac pop_density average_age female_frac
global econ_controls poverty_rate rent_frac l_pc_income lim_english e_highschool_frac-e_graduate_frac

****** PAIRWISE CORRELATION
pwcorr repaired ethno_racial_frac, st(0.05)

****** ETHNIC
*  ONLY SHARES AS CONTROLS
xi: probit repaired ethno_racial_frac $ER_SHARES, vce(cluster neighborhoodname)
eststo ER1: margins, dydx(ethno_racial_frac) post

*  ADD NEIGHBORHOOD'S FE
xi: probit repaired ethno_racial_frac $ER_SHARES i.neighborhoodname, vce(cluster neighborhoodname)
eststo ER2: margins, dydx(ethno_racial_frac) post


* ADD INFRASTRUCTURE
xi: probit repaired ethno_racial_frac $ER_SHARES i.neighborhoodname $infrastructure, vce(cluster neighborhoodname)
eststo ER3: margins, dydx(ethno_racial_frac) post


* ADD DEMO & ECON CONTROLS
xi: probit repaired ethno_racial_frac $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls, vce(cluster neighborhoodname)
eststo ER4: margins, dydx(ethno_racial_frac) post



esttab ER* using "$data_path/results/tableA5.tex", $esttab_options keep(ethno_racial_frac)



