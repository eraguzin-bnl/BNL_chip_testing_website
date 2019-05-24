from helpers.coldFeAsic import crawl
import os,sys
from jinja2 import Environment, FileSystemLoader
from helpers import prep
from ini_loader import INI_FILE

class main():

    def __init__(self, config_file = None):
        self.config = INI_FILE().load()
        self.start()
    
    def start(self):
        print("Main --> starting...")
        self.HTML_BASE = self.config["DEFAULT"]["HTML_BASE"]
        prep.confirm_path(self.HTML_BASE)
        #get the dictionaries from the clean_summary for a first time build
        master_dict = crawl(self.config).clean_summary()
        print("Main --> Entire dictionary is {} kB".format(sys.getsizeof(master_dict)/1000))
        env = Environment(loader=FileSystemLoader('j2'))
    
        self.build_summary_page(master_dict,env)
        
        generic_page_builder(master_run_dict, env, 'runid')
    
        generic_page_builder(master_chip_dict, env, 'asicid')
        
        generic_page_builder(master_board_dict, env, 'boardid')   
    
        build_rates_page(master_chip_dict, env)
        
        #TODO count socket uses
        
        print("...finished")
    
    
    def generic_page_builder(master_dict, env, subdir):
        #first build the summary page (coldfeasic/subdir/index.html)
        summary_dir = os.path.join(HTML_BASE,subdir)
        summary_dict = prep.prep_summary(master_dict, subdir)
        template_name = 'coldfeasic_' + subdir[:-2] + '_summary.html.j2'
        #ensure path exists
        prep.confirm_path(summary_dir)
        #get template
        template_obj = env.get_template(template_name)
        #write html file
        with open(os.path.join(summary_dir,'index.html'), 'w') as html_file:
            text = template_obj.render(summary_dict)
            html_file.write(text)
        
        #...and build the the individual run pages    
        for key in master_dict.keys():
            indiv_dir = os.path.join(summary_dir,key)
            prep.confirm_path(indiv_dir)
            indiv_dict = prep.prep(master_dict, key, subdir, indiv_dir)
            template_name = 'coldfeasic_' + subdir[:-2] + '.html.j2'
            template_obj = env.get_template(template_name)
            with open(os.path.join(indiv_dir,'index.html'), 'w') as html_file:
                text = template_obj.render(indiv_dict)
                html_file.write(text)
    
    
    def build_summary_page(self, master_dict, env):
        #build the summary html file (coldFeAsic/summary/index.html)
        #the summary list is a list of dictionaries
        #each dictionary contains boardid, chip names, run id
        #jinja prefers a dictionary not a list
    
#        summary_dict = {'summary_list':summary_list}
        template_obj = env.get_template('coldfeasic_summary.html.j2')
        summary_dir = os.path.join(self.HTML_BASE,'summary') 
        prep.confirm_path(summary_dir)
        print(master_dict['final_list'][0]["LN"].keys())
        print(master_dict['final_list'][0]["LN"]['sync_results'].keys())
        print(master_dict['final_list'][0]["LN"]['run_params'].keys())
        print(master_dict['final_list'][0]["LN"]['chip_results'].keys())
        print(master_dict['final_list'][0]["LN"]['final'])
        print(master_dict['final_list'][0]["LN"]['alive_results'].keys())
        print(master_dict['final_list'][0]["LN"]['baseline_results'].keys())
        print(master_dict['final_list'][0]["LN"]['monitor_results'].keys())
        with open(summary_dir+'/index.html', 'w') as html_file:
            text = template_obj.render(master_dict)
            html_file.write(text)
    
    def build_rates_page(summary_dict, env):
        #builds the
        rates_dict = prep.prep_rates(summary_dict)
        template_obj = env.get_template('coldfeasic_testingrates.html.j2')
    
        with open('../public_html/coldFeAsic/testingrates/index.html', 'w') as html_file:
            text = template_obj.render(rates_dict)
            html_file.write(text)
    
#    if __name__ == "__main__":
#        start()
