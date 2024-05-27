***********************************************
* Figure 5
*
* author: Felipe Jordan & Enrico Di Gregorio
***********************************************

*Import Data***********************************
cap global data_path = "/Users/felipe/projects/the-diversity-we-breath"

global esttab_options		starlevels(* 0.1 ** 0.05 *** 0.01) ///
							 noconstant   replace compress	 ///
							 booktabs	 nonotes 	nonumbers		 b(3)   se(3)

global conley_th 2

global ER_SHARES er1_share er2_share er3_share er4_share er5_share er6_share er7_share

global infrastructure density log_closer_g1

global demo_controls occu_frac l_tot_pop average_age female_frac

global econ_controls poverty_rate rent_frac l_pc_income lim_english e_highschool_frac-e_graduate_frac

forval r = 50(50)1000 {
	
	insheet using "$data_path/data/final/leaksAsObs/LeaksData_Radio_`r'.csv", c clear
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
	gen density = (total1) / (3.14*(`r'/1000)^2)
	gen l_tot_pop =log(tot_pop)
	gen l_pc_income = log(pc_income)


	quietly: xi: acreg repaired ethno_racial_frac $ER_SHARES i.neighborhoodname $infrastructure $demo_controls $econ_controls if grade==3, spatial latitude(latitude) longitude(longitude) dist($conley_th) bartlett
	est sto r`r'
	
	global zscore95 1.96 // for 95% CI
    global zscore90 1.645 // for 90% CI
    global zscore68 1 // for 68% CI
	
	global CI 90
	
	global b_`r' = _b[ethno_racial_frac]
	global ub_b_`r' = _b[ethno_racial_frac] + (${zscore${CI}} * _se[ethno_racial_frac])
	global lb_b_`r' = _b[ethno_racial_frac] - (${zscore${CI}} * _se[ethno_racial_frac])
	
}
		
// New dataset with coefficients and bounds

clear
set obs 20 // vs. 10 in case with only 100 meters radius
gen radius = _n * 50

gen b = .
gen lb_b = .
gen ub_b = .

forval r = 50(50)1000 {
	
replace b = ${b_`r'} if radius == `r'
replace lb_b = ${lb_b_`r'} if radius == `r'
replace ub_b = ${ub_b_`r'} if radius == `r'	
	
}

// In percentage point terms:
foreach var in b lb_b ub_b {
	
replace `var' = `var' * 100

}

twoway  (rarea ub_b lb_b radius, fcolor(stc1%30) lcolor(blue%80) lw(none) lpattern(solid)) /// 
         (connected b radius, lcolor(midblue) lpattern(solid) lwidth(thick) msize(medsmall) mfcolor(white) mlcolor(midblue)), ///
			yline(0, lcolor(cranberry%80) lpattern(solid)) xlabel(100(100)1000)	/// dkgreen%80
			  ytitle("{stSerif:Estimate, {it:p.p.}}", size(medium)) /// percentage points
			   xtitle("{stSerif:Buffer radius length, {it:m}}", size(medium)) /// {it:meters}
			    ylabel(-40(10)10) ///
			graphregion(color(white)) plotregion(color(white)) ///
			 legend(order(2 "Point estimates" 1 "90% confidence intervals") ring(1) pos(6) row(1) col(3) region(color(none)) /// 
			  color(black%50) size(medium)) //   note("{stSerif:test notes.}")
graph export "${graph_path}/results/connected_reg_1_robustness_radio_50m.png", replace 			  
			  