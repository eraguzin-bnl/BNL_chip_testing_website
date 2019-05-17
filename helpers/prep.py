import os
from datetime import datetime

def prep_rates(chip_dict):
    #prepares lists to build the testingrates figure
    #accepts the master chip dict
    #returns lists that define an x axis (abs day), and several assciated data lists

    pass_per_day = {}
    fail_per_day = {}
    days_from_epoch = []
    first_day = 0 #normalize to zer0 to scale the x axis

    #get a list of all the days testing was performed 
    for chip in chip_dict.keys():
        for run in chip_dict[chip]:
            time_stamp = run['runid']
            abs_days = convert_days(time_stamp)
            if abs_days not in days_from_epoch:
                days_from_epoch.append(abs_days)

    days_from_epoch = sorted(days_from_epoch)
                
    for d,day in enumerate(days_from_epoch):
        if d == 0:
            first_day = day
        elif day < first_day:
            first_day = day
    
    days = []        
    for d,day in enumerate(days_from_epoch):
        days.append(day - first_day)

    for chip in chip_dict.keys():
        for run in chip_dict[chip]:
            result = run['result']
            time_stamp = run['runid']
            day = convert_days(time_stamp) - first_day
            if result == "Pass":
                try:
                    pass_per_day[day] = pass_per_day[day] + 1
                except KeyError:
                    pass_per_day[day] = 1
            if result == "Fail":
                try:
                    fail_per_day[day] = fail_per_day[day] + 1
                except KeyError:
                    fail_per_day[day] = 1

    cum_pass_list = []
    cum_fail_list = []
    pass_total = 0
    fail_total = 0
    for day in days:
        try:
            pass_total = pass_total + pass_per_day[day]
        except KeyError:
            print("No passes for the {} day".format(day))
        try:
            fail_total = fail_total + fail_per_day[day]
        except KeyError:
            print("no fails for the {} day".format(day))
        cum_pass_list.append(pass_total)
        cum_fail_list.append(fail_total)

    return {'days':days, 'pass':cum_pass_list, 'fail': cum_fail_list}
            
def convert_days(time_stamp):
    #time stamp will look like 20180725T230506 (yr mth dy T hr min sec)
    #want to return how many days have passed since the first day of testing
    #using the epoch time as intermediate reference
    pattern= '%Y%m%dT%H%M%S'
    return int(datetime.strptime(time_stamp,pattern).timestamp()/60/60/24)
    
def prep(d, key, subdir, rundir):
    if subdir == 'asicid':
        return prep_chip(d, key)
    elif subdir == 'runid':
        return prep_run(d, key, rundir)
    elif subdir == 'boardid':
        return prep_board(d, key)
                                

def prep_summary(d, subdir):
    #directs the dictionary to the correct function
    if subdir == 'asicid':
        return prep_chip_summary(d)
    elif subdir == 'runid':
        return prep_run_summary(d)
    elif subdir == 'boardid':
        return prep_board_summary(d)


def prep_board(d, board):
    d_out = {'boardid':board, 'runs':[]}
    for run in d[board]:
        d_out['runs'].append({'runid':run['runid'], 'chips':[]})
        for chip in run['chips']:
            d_out['runs'][-1]['chips'].append({'name':chip})
    return d_out
            
def prep_board_summary(d):
    board_list = []
    for board in d.keys():
        board_list.append({"boardid":board})
    return {'boards':board_list}

def prep_chip(d, chip):
    return {'chip':chip, 'runs':d[chip]}                        
        

def prep_chip_summary(d):
    #return a dictionary of a list of the chip values to be looped over
    chip_list = []
    for chip in d.keys():
        chip_list.append(chip)
    return {'chips':sorted(chip_list)}

def prep_run_summary(d):
    run_list = []
    for run in d.keys():
        run_list.append(run)
    return {'runs':run_list}

def prep_run(d, run, run_dir):
    methods = ["sync_adcs", "baseline_test_sequence-g2s2b0-0010", "baseline_test_sequence-g2s2b1-0010", "monitor_data_test_sequence-g2s2b0-0010", "input_alive_power_cycle_sequence-g2s2b0-0010"]
    #structure of d_out: {runid, dictionary of data about that run}
    d_out = {'runid':run, 'boardid':d[run]['boardid'], 'chips':d[run]['chips'], 'methods' : []}        
    for m,method in enumerate(methods):
        d_out['methods'].append({'method_name':method})
        for key,value in d[run][method].items():
            d_out['methods'][m][key] = value
        #make symbolic links of the png files for the webpages to look to
        png_paths_in_disk = d_out['methods'][m]['pngs']
        d_out['methods'][m]['pngs'] = []
        for p, png_location in enumerate(png_paths_in_disk):
            png_name = os.path.basename(png_location)
            png_method_path = os.path.dirname(png_location)
            png_method = os.path.basename(png_method_path)
            png_chip_path = os.path.dirname(png_method_path)
            png_chip = os.path.basename(png_chip_path)
            
            png_abs_dest_path = os.path.join(run_dir, png_chip, png_method, png_name)
            if not os.path.isfile(png_abs_dest_path):
                confirm_path(os.path.dirname(png_abs_dest_path))
                os.symlink(png_location,png_abs_dest_path)

            png_path_from_run_dir = os.path.join(png_chip,png_method,png_name)
            chip_index = d[run]['chips'].index(png_chip)
            if good_image(png_name, png_method):
                d_out['methods'][m]['results'][chip_index]['png'] = png_path_from_run_dir
                                        
    return d_out

def good_image(png_name, png_method):
    if png_name == "Sample_Pulses.png" and png_method == 'monitor_data_test_sequence-g2s2b0-0010':
        return False
    elif png_name == "Sync_Plot_Monitor.png":
        return False
    else:
        return True

def confirm_path(fp):
    if not os.path.exists(fp):
        os.makedirs(fp)