from nba_api.stats.static import teams # For team list
from nba_api.stats.endpoints import teamdashptpass # For team passing stats
from nba_api.stats.endpoints import playerdashptpass # For player passing stats
from chord import Chord # For visualization

import pandas as pd
import time

from tkinter import *
from ttkthemes import themed_tk as tk
from tkinter import font
from tkinter import messagebox
from PIL import ImageTk,Image

def get_team_id(team_name):
    # Below returns a list of dictionaries, 1 for each NBA team
    nba_teams = teams.get_teams()

    # Let's create a Pandas DataFrame using extracted list of dictionaries
    df_nba_teams = pd.DataFrame(nba_teams)

    for team in nba_teams:
        if team_name == team['full_name']:
            team_id = team['id']
            break

    return team_id

def generate_chord(team_id, season_id, season_progress, team_name):
    team_passes = teamdashptpass.TeamDashPtPass(team_id=team_id, 
                                                season=season_id, 
                                                season_type_all_star=season_progress, 
                                                per_mode_simple='PerGame')
    # Print passes made
    df_team_passes_made = team_passes.get_data_frames()[0]
    #print(df_team_passes_made)

    # Print passes received
    df_team_passes_rec = team_passes.get_data_frames()[1]
    #print(df_team_passes_rec)

    player_ids = list(df_team_passes_made['PASS_TEAMMATE_PLAYER_ID'])
    #print(player_ids)

    # Create empty dataframes, one for passes made, another for passes received
    team_pp_made = pd.DataFrame()
    team_pp_rec = pd.DataFrame()

    # Cycle through each pleayer id and extract passes made and passes received 
    for pid in player_ids:
        player_pass = playerdashptpass.PlayerDashPtPass(team_id=team_id,
                                                        player_id=pid, 
                                                        season=season_id, 
                                                        season_type_all_star=season_progress, 
                                                        per_mode_simple='PerGame')
        # Get DataFrames
        player_pass_made=player_pass.get_data_frames()[0]
        player_pass_rec=player_pass.get_data_frames()[1]
        
        # Append
        team_pp_made = pd.concat([team_pp_made, player_pass_made], ignore_index=True, axis=0, sort=False)
        team_pp_rec = pd.concat([team_pp_rec, player_pass_rec], ignore_index=True, axis=0, sort=False)
        
        # Sleep for 5 seconds before moving to the next player
        time.sleep(0.5)

    # Create merge keys
    team_pp_made['key_pass_from_to'] = team_pp_made['PLAYER_NAME_LAST_FIRST'] + " : " + team_pp_made['PASS_TO']
    team_pp_made['key_pass_to_from'] = team_pp_made['PASS_TO'] + " : " + team_pp_made['PLAYER_NAME_LAST_FIRST']

    # Create a DataFrame based on key_pass_to_from
    team_pp_made_to_from = team_pp_made.loc[:, ['key_pass_to_from', 'PASS']]
    team_pp_made_to_from = team_pp_made_to_from.rename(columns={'PASS' : 'pass_to_from_cnt'})
    #print(team_pp_made_to_from)

    # Merge it back to the main DataFrame
    team_pp_comb = pd.merge(team_pp_made, team_pp_made_to_from, 
                         how='left', 
                         left_on='key_pass_from_to', right_on='key_pass_to_from')
    team_pp_comb['Total Passes'] = team_pp_comb['PASS'] + team_pp_comb['pass_to_from_cnt']
    #print(team_pp_comb)

    # Take a copy of DF
    df = team_pp_comb.copy()

    # Keep only required fields
    df = df.loc[:, ['PLAYER_NAME_LAST_FIRST', 'PASS_TO', 'Total Passes']]

    # Create crosstab (note, we replace NaN with 0's)
    df_tab = pd.crosstab(df['PLAYER_NAME_LAST_FIRST'],df['PASS_TO'],aggfunc='sum', values=df['Total Passes']).fillna(0)

    # Print resulting DataFrame
    #print(df_tab)

    # Player Names
    names = list(df_tab.columns)
    #names

    # Passing data (change from df to list of lists)
    matrix = df_tab.values.tolist()
    #matrix

    # Create our diagram
    diagram = Chord(matrix, names, font_size_large='10px', wrap_labels=False, margin=100, width=800)

    # Save it into HTML file
    team_name = team_name.replace(' ', '')
    season_progress = season_progress.replace(' ', '')
    diagram.to_html(team_name+season_id+season_progress+'Chord.html')

    popupmsg_success()

def popupmsg_success():
    response = messagebox.showinfo("Chord Diagram Successfully Generated", "Your Chord Diagram was successfully generated.\nCheck the folder where this folder is located!")

def popupmsg_error():
    response = messagebox.showinfo("Error", "It was not possible to generate this chord diagram")

def myClick():
    team_name = clicked.get()
    season_id = clicked2.get()
    if len(season_id) > 7:
        season_id = season_id[2:9]
    season_progress = clicked3.get()
    try:
        team_id = get_team_id(team_name)
        generate_chord(team_id, season_id, season_progress, team_name)
    except:
        popupmsg_error()
    
screen = tk.ThemedTk()
screen.get_themes()
screen.set_theme("breeze")

width_of_window = 500
height_of_window = 400

screen_width = screen.winfo_screenwidth()
screen_height = screen.winfo_screenheight()

x_coordinate = int((screen_width/2) - (width_of_window/2))
y_coordinate = int((screen_height/2) - (height_of_window/2))

screen.geometry("{}x{}+{}+{}".format(width_of_window, height_of_window, x_coordinate, y_coordinate))
screen.title("NBA Chord Diagram Generator")
screen.iconbitmap('nba.ico')
screen.config(background='#17408B')

img = Image.open("logo-nba.png")
resized = img.resize((70,70), Image.ANTIALIAS)
img = ImageTk.PhotoImage(resized)
Label(screen, image=img, background='#17408B').pack(pady=10)

all_teams = ['Atlanta Hawks',
            'Boston Celtics',
            'Brooklyn Nets',
            'Charlotte Hornets',
            'Chicago Bulls',
            'Cleveland Cavaliers',
            'Dallas Mavericks',
            'Denver Nuggets',
            'Detroit Pistons',
            'Golden State Warriors',
            'Houston Rockets',
            'Indiana Pacers',
            'Los Angeles Clippers',
            'Los Angeles Lakers',
            'Memphis Grizzlies',
            'Miami Heat',
            'Milwaukee Bucks',
            'Minnesota Timberwolves',
            'New Orleans Pelicans',
            'New York Knicks',
            'Oklahoma City Thunder',
            'Orlando Magic',
            'Philadelphia 76ers',
            'Phoenix Suns',
            'Portland Trail Blazers',
            'Sacramento Kings',
            'San Antonio Spurs',
            'Toronto Raptors',
            'Utah Jazz',
            'Washington Wizards']

seasons = ["2013-14",
           "2014-15",
           "2015-16",
           "2016-17",
           "2017-18",
           "2018-19",
           "2019-20",
           "2020-21"] # All seasons with valid data

clicked = StringVar()
clicked.set(all_teams[0])

season_frame = Frame(screen)
season_frame.pack(pady=20)
season_frame.config(background='#17408B')

season_frame_ = LabelFrame(season_frame, text="Select Team and Season:", font=('Helvetica', 14, 'bold'), background='#17408B', fg='white', labelanchor='n')
season_frame_.grid(row=0, column=0, padx=50)
    
drop = OptionMenu(season_frame_, clicked, *all_teams)
drop.pack(pady=10)
drop.config(highlightbackground='#17408B', fg='black')

clicked2 = StringVar()
clicked2.set(seasons[-1:])

drop = OptionMenu(season_frame_, clicked2, *seasons)
drop.pack(pady=10)
drop.config(highlightbackground='#17408B', fg='black')

reg_or_offs = ['Regular Season', 'Playoffs']

clicked3 = StringVar()
clicked3.set(reg_or_offs[0])

drop = OptionMenu(season_frame_, clicked3, *reg_or_offs)
drop.pack(pady=10)
drop.config(highlightbackground='#17408B', fg='black')

myButton2 = Button(screen, text="Generate Chord Diagram", command=myClick, fg='black', font=('Helvetica', 14, 'bold'))
myButton2.pack(pady=10)

screen.mainloop()
