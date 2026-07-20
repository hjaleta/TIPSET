import os

import matplotlib.pyplot as plt


from tips import config



def make_plots(tournament):
    ...
    os.makedirs(config.PLOTS_DIR, exist_ok=True)

    PIE_CHART_DIR = os.path.join(config.PLOTS_DIR, "pie_charts")
    os.makedirs(PIE_CHART_DIR, exist_ok=True)   

    for player in tournament.players:
        fig, ax = plt.subplots(figsize=(6, 6))
        
        phases, points_per_phase = [], []
        for phase, questions_in_phase in player.questions.items():
            phases.append(phase)
            points = []

            for q in questions_in_phase:
                if hasattr(q, "points") and isinstance(q.points, (int, float)):
                    points.append(q.points)
                # else:
                #     print(f"Warning: Question {q.question} in phase {phase} for player {player.name} has non-numeric points: {q.points}")

            
            points_per_phase.append(sum(points))
        
        total_points = sum(points_per_phase)

        def format_label(pct):
            absolute = int(round(pct/100.*total_points))
            return f"{absolute:d}" if absolute > 0 else ""

        
        pie = ax.pie(points_per_phase, labels=phases, startangle=90, autopct=format_label, pctdistance=0.6, 
                     wedgeprops={'edgecolor': 'black'})
        ax.set_title(f"{player.nick} - {total_points} points")

        fig.savefig(os.path.join(PIE_CHART_DIR, f"{player.name}_points_distribution.png"))
        plt.close(fig)