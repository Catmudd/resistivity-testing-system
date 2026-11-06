#----------------------------------------
# Library Imports
#----------------------------------------

import tkinter as tk
from tkinter import ttk
from datetime import datetime

import main



#----------------------------------------
# Variables
#----------------------------------------

# Window
main_window = tk.Tk()

# Entry box inputs
tester_name_input = tk.StringVar()
sample_id_input = tk.StringVar()

# Test start time and date
current_date = datetime.now().strftime('%B %d, %Y')
start_time = datetime.now().strftime('%I%M %p')

# Variables to hold inputted values
tester_name = ''
sample_id = ''
results_file_type = tk.StringVar(value='csv')   # default to CSV



#----------------------------------------
# Functions
#----------------------------------------

#----------------------------------------
# set_results_file_type(type)
#
# parameters:
#	- file_type: a string representing the file type
#
# function description:
#	takes in a 'type' argument and sets the program result file type
#	to 'type'. This function is called when a file type button on the 
#   user interface is pressed.
#----------------------------------------
def set_results_file_type(file_type: str):
    results_file_type.set(file_type)
    print('Results file type set to ', results_file_type.get())

#----------------------------------------
# update_button_visuals()
# 
# Updates the visuals of the given buttons to reflect which button is
# currently selected.
#
# buttons:          Dictionary of buttons to update.
# selected:         Key of button in buttons which is selected.
#----------------------------------------
def update_button_visuals(file_buttons : dict, key: str):
    for k, v in file_buttons.items():
        if k == key:
            v.config(bg="#89B2FF")
        else:
            v.config(bg="#ebebeb")

#----------------------------------------
# on_file_button_pressed()
# 
# Called when button file_button is pressed. Sets the results file type.
#
# file_buttons:     Dictionary of buttons to update, which contains 
#                   file_button.
# file_type:        Button that was pressed, also type of file to submit.
#----------------------------------------
def on_file_button_pressed(file_buttons: dict, file_button_key: str):
    set_results_file_type(file_button_key)
    update_button_visuals(file_buttons, file_button_key)

#----------------------------------------
# create_button_lambda()
# 
# Safely creates a lambda for the given list of buttons and button key.
# This is needed, because lambdas cannot be created in the button for-
# loop correctly; Variables in py are not truly locally scoped, and
# the lambda will always use the variables in the lambda as they are
# at the end of the loop. THIS IS SCARY!!! But, there's not much we can do 
# about it other than avoiding it.
#
# file_buttons:     Dictionary of buttons to update, which contains 
#                   file_button_key.
# file_button_key:  Button that was pressed.
#----------------------------------------
def create_button_lambda(file_buttons: dict, file_button_key: str):
    return lambda : on_file_button_pressed(file_buttons, file_button_key)

#----------------------------------------
# start_button_pressed()
#
# function description:
#	Is called when the Start Test button on the interface is pressed. Gets
#	the values from the text entry boxes and stores them as variables, then
#	calls the run_test() function in main.py to start the automated test
#	sequence, passing in variables so that they can be used in the scope of main.py. 
#----------------------------------------
def start_button_pressed():
    print('Start button pressed')
    
    # Getting values of input boxes
    tester_name = tester_name_input.get()
    sample_id = sample_id_input.get()
    
    print('Starting test sequence with the following parameters: ')
    print('   Tester name: ', tester_name)
    print('   Sample ID: ', sample_id)
    print('   Results file type: ', results_file_type.get())
    print('   Start Date and time: ', current_date, ' ', start_time)
    print('')
    
    # Closing start menu
    main_window.destroy()
    
    # Starting automation sequence by calling the run_test(0 function in main.py
    main.run_test(tester_name, sample_id, results_file_type.get(), current_date, start_time)



#----------------------------------------
# setup_window()
#
# function description:
#	Prepares a Tkinter window for the user interface, filling
#	80% of screen width and height and centered on the page. 
#----------------------------------------
def setup_window():
    # Terminal logging
    print('Starting: Setting up interface window')
    
    # Window title
    main_window.title('Rock Resistivity Test')
    
    # Getting the screen dimensions of the device in use
    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()
    
    # Setting window dimensions so 80% width & 80% screen height are initially occupied by window
    window_width = 0.8 * screen_width
    window_height = 0.8 * screen_height
    
    # Window offset of 10% in each dimension results in a centered window
    horizontal_offset = 0.1 * screen_width
    vertical_offset = 0.1 * screen_height
    
    # Applying window geometry
    main_window.geometry('%dx%d+%d+%d' % (window_width, window_height, horizontal_offset, vertical_offset))
       
    # Terminal logging
    print('Completed: Setting up interface window\n')

#----------------------------------------
# setup_file_buttons()
# 
# Creates all the file type selection buttons.
#----------------------------------------
def setup_file_buttons():
    # Create file buttons. These are created from a list of keys and labels for each.
    # Each file button will set the type of file to its own key, so file_button_keys
    # should match the kinds of files available. However, this should eventually be
    # separated.
    file_button_keys = ['csv', 'pdf', 'both']
    file_button_lables = ['CSV', 'PDF', 'CSV & PDF']
    file_buttons = dict()

    # Keep track of previous width of each button, so they space nicely
    FILE_BUTTON_SPACING = 30
    file_button_next_start = FILE_BUTTON_SPACING
    
    for i in range(0, file_button_keys.__len__()):

        file_button = tk.Button(
            main_window, 
            text=file_button_lables[i], 
            font=('Helvetica', 30))

        file_button.place(x=(file_button_next_start), y=360)
        file_button.config(command=create_button_lambda(file_buttons, file_button_keys[i]))
        file_buttons[file_button_keys[i]] = file_button
        file_button_next_start += file_button.winfo_reqwidth() + FILE_BUTTON_SPACING

    update_button_visuals(file_buttons, results_file_type.get())

#----------------------------------------
# display_start_menu()
#
# function description:
#	Places elements on the previously created window to display
#	the user interface. 
#----------------------------------------
def display_start_menu():
    # Terminal logging
    print('Starting: Displaying interface start menu')
    
    # Title
    title_label = tk.Label(main_window, text='Rock Resistivity Testing System', font=('Helvetica', 40))
    title_label.place(x=10, y=10)
    
    # Tester name input
    name_label = tk.Label(main_window, text='Tester name: ', font=('Helvetica', 30))
    name_label.place(x=30, y=120)
    
    name_entry = tk.Entry(main_window,textvariable=tester_name_input, font=('Helvetica', 30))
    name_entry.place(x=350, y=120)
    
    # Sample ID input
    sample_id_label = tk.Label(main_window, text='Sample ID: ', font=('Helvetica', 30))
    sample_id_label.place(x=30, y=180)
    
    sample_id_entry = tk.Entry(main_window, textvariable=sample_id_input, font=('Helvetica', 30))
    sample_id_entry.place(x=350, y=180)
    
    # Result file type selection
    prompt_label = tk.Label(main_window, text='Select results file type: ', font=('Helvetica', 30))
    prompt_label.place(x=30, y=300)

    # Setup file selection buttons
    setup_file_buttons()
    
    # Date & time display 
    date_display = tk.Label(main_window, text=current_date, font=('Helvetica', 30))
    time_display = tk.Label(main_window, text=start_time, font=('Helvetica', 30))
    
    date_display.place(x=30, y=730)
    time_display.place(x=30, y=780)
    
    # 'Start Test' button
    start_button = tk.Button(main_window, text='Start Test', font=('Helvetica', 30), command=lambda: start_button_pressed())
    start_button.place(x=30, y=520)
    
    # Terminal logging
    print('Completed: Displaying interface start menu\n')



#----------------------------------------
# Program Flow
#----------------------------------------

setup_window()
display_start_menu()

main_window.mainloop()
