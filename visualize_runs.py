import sys
import numpy as np
import matplotlib.pyplot as plt
import pickle
import sys
import argparse
import os


def load_data_v0(log_dict):
    print("Loading log...")
    num_runs = len(nn_dict['experiment_log'])
    len_runs = len(nn_dict['experiment_log'][0])

    gens = np.arange(0, len_runs)
    best = np.zeros((num_runs, len_runs))
    means = np.zeros((num_runs, len_runs))
    medians = np.zeros((num_runs, len_runs))
    pop_stds = np.zeros((num_runs, len_runs))
    timesteps = np.zeros((num_runs, len_runs))


    for run_idx, run_log in enumerate(nn_dict['experiment_log']):
        for gen_idx, data_dict in enumerate(run_log):
            timesteps[run_idx][gen_idx] = data_dict['timesteps']
            best[run_idx][gen_idx] = data_dict['fit_best']
            means[run_idx][gen_idx] = data_dict['fit_mean']
            medians[run_idx][gen_idx] = data_dict['fit_med']
            pop_stds[run_idx][gen_idx] = data_dict['fit_std']

    print("Log Loaded.")
    return timesteps, best, means, medians, pop_stds, stds


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('log_paths', metavar='log files or folders', type=str, nargs='+',
                         help='log files or folder to scan')

    parser.add_argument('--f', action='store_true', dest='folder_flag',
                         help='scan entire folder of logs')

    parser.add_argument('--i', action='store_true', dest='ignore_failed',
                         help='ignore runs that didn\'t solve the task')

    return parser.parse_args()

def scan_folder(folder_paths):
    log_files = []
    for folder_path in folder_paths:
        for file in os.listdir(folder_path):
            if file.endswith('.p'):
                log_files.append(os.path.join(folder_path, file))
    return log_files

def get_log_name(path):
    log_name = path
    if '\\' in path:
        log_name = path[path.rfind('\\') + 1:path.rfind('.')]
    elif '/' in path:
        log_name = path[path.rfind('/') + 1:path.rfind('.')]
    return log_name



if __name__ == '__main__':
    parser = parse_arguments()

    if parser.folder_flag:
        print(parser.log_paths)
        log_paths = scan_folder(parser.log_paths)
    else:
        log_paths = parser.log_paths

    plotted_log_paths = []
    timesteps = []
    bests = []
    means = []
    medians = []
    pop_stds = []
    stds = []
    for path in log_paths:
        nn_dict = pickle.load(open(path, 'rb'))
    
        timestep, best, mean, median, pop_std, std = load_data_v0(nn_dict)

        if parser.ignore_failed and best[-1] < 50:
            continue

        plotted_log_paths.append(path)
        timesteps.append(timestep)
        bests.append(best)
        means.append(mean)
        medians.append(median)
        pop_stds.append(pop_std)
        stds.append(std)



    # Calculate the average and variance of solve time. 
    if not parser.folder_flag:
        solve_score = 500.0
        solve_times = []
        did_solve = 0

        for path_idx, path in enumerate(plotted_log_paths):
            solves = []
            for run_idx, runs in enumerate(bests[path_idx]):
                for best, timestep in zip(bests[path_idx][run_idx], timesteps[path_idx][run_idx]):
                    if best >= solve_score:
                        solves.append(timestep)
                        did_solve += 1
                        break
            solve_times.append(solves)
                
        print(f"Num Runs: {len(bests[0])}")
        print(f"Num Solves: {did_solve}")
        print(f"Average Solve Timesteps: {np.mean(solve_times)}" )
        print(f"Standard Deviation of Solve Timesteps: {np.std(solve_times)}")



        # Graph data
        fig, (ax_h, ax_l) = plt.subplots(2, 1, figsize=(13,7), sharex=True)
        ax_h.set_ylabel("Best Fitness", fontsize=15)
        ax_l.set_ylabel("Population Fitness", fontsize=15)
        ax_l.set_xlabel("Timesteps", fontsize=15)


    for path_idx, path in enumerate(plotted_log_paths):
        for run_idx, runs in enumerate(bests[path_idx]):
            run_name = f"Run: run_idx {run_idx}"

            ax_h.plot(timesteps[path_idx][run_idx], bests[path_idx][run_idx], label=run_name)
            ax_l.plot(timesteps[path_idx][run_idx], means[path_idx][run_idx], label=run_name)

    ax_l.legend(loc='upper center', bbox_to_anchor=(1.05, 1.5), shadow=True, fontsize=7)
    #ax_l.legend()
    fig.suptitle("Fitness Graph", fontsize=25)

    plt.show()