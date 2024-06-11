import matplotlib.pyplot as plt
plt.style.use('dark_background')

from matplotlib import rcParams

rcParams['font.family'] = 'Ubuntu'
# rcParams['font.sans-serif'] = ['Tahoma']


labels = 'Correct Result', 'Correct 1-X-2', 'Incorrect'
sizes = [15, 35, 50]
explode = (0.05, 0.05, 0.05)
colors = ["green", "orange", "red"]

fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, 
       explode=explode, 
       
       autopct='%1.1f%%',
       colors=colors,
        startangle=90)


ax.title.set_text('Prediction Accuracy\nGERMANY - SCOTLAND (2-0)')

fig.tight_layout()

fig.savefig('pie-chart.png')