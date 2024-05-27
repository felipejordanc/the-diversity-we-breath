***********************************************
* Table A3
*
* author: Felipe Jordan
***********************************************

*Import Data***********************************
cap global data_path = "/Users/felipe/projects/the-diversity-we-breath"

insheet using "$data_path/data/final/leaksAsObs/LeaksData_Radio_500.csv", c clear
keep if grade==3
gen cambridge=(town=="CAMBRIDGE")

bysort cambridge: tab neighborhood
