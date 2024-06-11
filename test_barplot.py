import matplotlib.pyplot as plt
import numpy as np
# plt.style.use('dark_background')
# plt.style.use()

from matplotlib import rcParams

rcParams['font.family'] = 'sans-serif'
# rcParams['font.sans-serif'] 

N_SAMPLES = 100000
fig, ax = plt.subplots()

goal_difference = np.arange(-10, 10)

gio_mu, gio_sigma = 3.5, 3
no_gio_mu, no_gio_sigma =  4, 2

gio = np.round( np.random.normal(gio_mu, gio_sigma, N_SAMPLES))
no_gio = np.round( np.random.normal(no_gio_mu, no_gio_sigma, N_SAMPLES))

print(gio)
print(no_gio)
# exit()

gio_hist, gio_bins = np.histogram(gio, bins=goal_difference, density=True)
no_gio_hist, no_gio_bins = np.histogram(no_gio, bins=goal_difference, density=True)



width = 0.4
ax.bar(gio_bins[:-1], gio_hist, width=width, color='b', align='center', label='Goalkeeper=Giorgone')
ax.bar(no_gio_bins[:-1]+width, no_gio_hist, width=width, color='r', align='center', label='Goalkeeper =/= Giorgone')

ax.set_xticks(goal_difference)
ax.set_xticklabels(goal_difference)

ax.set_xlabel('Goal Difference')
ax.set_ylabel('Probability')

ax.title.set_text('Goal Difference Distribution vs Kaasnaaiers')

ax.legend()

fig.tight_layout()
fig.savefig('barplot.png')