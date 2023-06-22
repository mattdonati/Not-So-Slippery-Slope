SHELL = /bin/sh

STATES = Illinois Indiana Iowa Kentucky Michigan Minnesota Missouri Ohio Pennsylvania Tennessee West_Virginia Wisconsin
START_YEAR = 2014
END_YEAR = 2022
YEARS := $(shell seq $(START_YEAR) $(END_YEAR))
.DEFAULT_GOAL := help

state_roads_data: $(foreach state,$(STATES), data/raw/roads_data_$(state).csv) ## Download and save dataframes of North American Roads (NAR) data for each state
data/raw/roads_data_%.csv:
	python src/get_state_roads_data.py $*

winter_iowa_salt_data: data/raw/winter_iowa_salt_data.csv ## Download and save Iowa DOT Winter Operations Salt data: Winter Iowa Salt data
data/raw/winter_iowa_salt_data.csv:
	python src/get_winter_iowa_data.py --output $@

storm_dates: data/interim/winter_iowa_salt_data_with_stormdates.csv ## Infer storm dates and add to Winter Iowa Salt data
data/interim/winter_iowa_salt_data_with_stormdates.csv: data/raw/winter_iowa_salt_data.csv
	python src/storm_dates.py --input $< --output $@

date_range: data/interim/winter_iowa_unique_dates.pkd ## Extract and save list of unique dates for purpose of determining range of SNODAS download
data/interim/winter_iowa_unique_dates.pkd: data/interim/winter_iowa_salt_data_with_stormdates.csv
	python src/extract_storm_dates.py --input $< --output $@

winter_iowa_snodas_download_file: ## Winter Iowa Salt data SNODAS download. Download and unpack tar files for all winter iowa dates
	python src/get_snodas_data_winter_iowa.py --input data/interim/winter_iowa_unique_dates.pkd --tardir data/raw/snodas_tar_files --unpackeddir data/raw/snodas_params
	touch winter_iowa_snodas_download_file

winter_iowa_grid: data/processed/iowa_poly10_grid.csv ## Winter Iowa grid
data/processed/iowa_poly10_grid.csv:
	python src/save_iowa_grid.py --output $@

winter_iowa_overlay: data/interim/winter_iowa_overlay_saltbypoly.csv ## Winter Iowa overlay. Overlay of Winter Iowa Salt data and Iowa grid. Salt data aggregated by polygon
data/interim/winter_iowa_overlay_saltbypoly.csv: data/interim/winter_iowa_salt_data_with_stormdates.csv data/processed/iowa_poly10_grid.csv
	python src/save_overlay_iowa_winter.py --output $@ --saltfile $< --gridfile $(word 2, $^)

#create snodas dataset covering iowa for dates in iowa data set. observations are snodas variables for each date by each
#SNODAS polygon
winter_iowa_snodas_params: data/interim/winter_iowa_snodas_params_poly10.csv ## Create SNODAS DataFrame for Winter Iowa Data.
data/interim/winter_iowa_snodas_params_poly10.csv: winter_iowa_snodas_download_file data/interim/winter_iowa_unique_dates.pkd
	python src/save_winter_iowa_snodas.py --output $@ --datefile $(word 2, $^)

#Overlay of iowa NAR roads data and iowa grid
winter_iowa_road_overlay: data/interim/winter_iowa_road_overlay.csv ## Winter Iowa road overlay. Overlay of roads with grid.
data/interim/winter_iowa_road_overlay.csv: data/raw/roads_data_Iowa.csv data/processed/iowa_poly10_grid.csv
	python src/save_winter_iowa_road_overlay.py --output $@ --roadfile $< --gridfile $(word 2, $^)

#Combine Iowa Datasets (salt, roads, snodas)
winter_iowa_joined: data/processed/winter_iowa_joined.csv ## Winter Iowa join features (salt, snodas, roads)
data/processed/winter_iowa_joined.csv: data/interim/winter_iowa_overlay_saltbypoly.csv data/interim/winter_iowa_snodas_params_poly10.csv data/interim/winter_iowa_road_overlay.csv
	python src/save_winter_iowa_joined.py --output $@ --saltfile $< --snodasfile $(word 2, $^) --roadsfile $(word 3, $^)

fit_salt_model: models/fitted_salt_model.pkd ## Fit salt model
models/fitted_salt_model.pkd: data/processed/winter_iowa_joined.csv
	python src/fit_salt_model.py --output $@ --input $<

regional_grid: data/processed/regional_poly10_grid.csv ## Regional grid
data/processed/regional_poly10_grid.csv:
	python src/save_regional_grid.py --output $@

depot_distances: data/interim/depot_distances.csv ## Depot distances
data/interim/depot_distances.csv: data/processed/regional_poly10_grid.csv data/raw/salt_depots.csv
	python src/save_depot_distances.py --output $@ --gridfile $(word 1, $^) --depotfile $(word 2, $^)

regional_snodas_download_file: ## Regional SNODAS download. Download and unpack tar files for all dates in timeframe
	python src/get_regional_snodas.py --tardir data/raw/snodas_tar_files --unpackeddir data/raw/snodas_params
	touch regional_snodas_download_file

regional_snodas_params: $(foreach year,$(YEARS), data/interim/snodas_params_regional_poly10_Q1$(year).csv) $(foreach year,$(YEARS), data/interim/snodas_params_regional_poly10_Q4$(year).csv) ## Regional SNODAS dataframes by quarter
data/interim/snodas_params_regional_poly10_Q%.csv:
	python src/save_regional_snodas.py --output $@

regional_state_overlays: $(foreach state,$(STATES), data/interim/regional_poly_10_road_overlay_$(state).csv) ## Overlay of regional grid and state road data for each state
data/interim/regional_poly_10_road_overlay_%.csv: data/processed/regional_poly10_grid.csv data/raw/roads_data_%.csv
	python src/save_state_road_overlays.py --output $@ --state $* --gridfile $(word 1, $^) --roadsfile $(word 2, $^)

regional_road_overlay: data/interim/regional_road_overlay.csv ## Complete regional overlay of grid and roads data
data/interim/regional_road_overlay.csv: $(foreach state,$(STATES), data/interim/regional_poly_10_road_overlay_$(state).csv)
	python src/save_regional_road_overlay.py --output $@ --directory data/interim

quarterly_salt_predictions: models/quarterly_salt_predictions.csv ## Save quarterly salt predictions for each quarter in time frame
models/quarterly_salt_predictions.csv: models/fitted_salt_model.pkd data/interim/regional_road_overlay.csv
	python src/save_quarterly_salt_predictions.py --output $@ --snodasdirectory data/interim --saltmodelfile $(word 1, $^) --roadoverlayfile $(word 2, $^)

sales_estimates: models/sales_estimates.csv ## Sales estimates
models/sales_estimates.csv: models/quarterly_salt_predictions.csv data/raw/sales_actual.csv data/interim/depot_distances.csv
	python src/company_sales.py --output $@ --predictions $(word 1, $^) --actualsales $(word 2, $^) --distances $(word 3, $^)

quarterly_solid_precip: data/processed/quarterly_solid_precip.csv ## Quarterly solid precipitation figures by polygon
data/processed/quarterly_solid_precip.csv: $(foreach year,$(YEARS), data/interim/snodas_params_regional_poly10_Q1$(year).csv) $(foreach year,$(YEARS), data/interim/snodas_params_regional_poly10_Q4$(year).csv)
	python src/quarterly_solid_precip.py --globpattern data/interim/snodas_params_regional_poly10_Q\*.csv --output $@

.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

