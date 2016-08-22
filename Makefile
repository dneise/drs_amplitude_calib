all:
	python make_all_drs_step2_h5.py
	python download_drs_fits_files.py
	python make_bsl_gain_h5.py
	python do_fit.py

plots:
	python plot_fits_results.py