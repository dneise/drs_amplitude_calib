all:
	python make_all_drs_step2_h5.py
	python make_bsl_gain_h5.py
	python do_fit.py

plots:
	python plot_fits_results.py
	python plot_residual_hist2d_for_certain_pixel.py
	python look_at_bsl_and_residual.py