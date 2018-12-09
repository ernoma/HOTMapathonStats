import pstats
p = pstats.Stats('profile_results')
p.strip_dirs().sort_stats('cumulative').print_stats(20)