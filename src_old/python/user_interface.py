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
# parameter:
#	- type: a string representing the file type
#
# function description:
#	takes in a 'type' argument and sets the program result file type
#	to 'type'. Options are PDF, CSV, or both. This function is called
#	when a file type button on the user interface is pressed. 
#----------------------------------------
def set_results_file_type(type):
    results_file_type.set(type)
    print('Results file type set to ', results_file_type.get())



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
    
    csv_button = tk.Button(main_window, text='CSV', font=('Helvetica', 30), command=lambda: set_results_file_type('csv'))
    pdf_button = tk.Button(main_window, text='PDF', font=('Helvetica', 30), command=lambda: set_results_file_type('pdf'))
    both_button = tk.Button(main_window, text='CSV & PDF', font=('Helvetica', 30), command=lambda: set_results_file_type('both'))
    
    csv_button.place(x=100, y=360)
    pdf_button.place(x=250, y=360)
    both_button.place(x=400, y=360)
    
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
