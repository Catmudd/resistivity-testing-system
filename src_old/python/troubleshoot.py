import tkinter as tk



#----------------------------------------
# ethernet_issue()
#
# function description:
#	This function is called when an exception is encountered while opening
#	the PyVISA power supply resource. It creates a popup window that prompts the user to check the
#	ethernet cable connection before continuing, as this was the most commonly
#	encountered ethernet connectivity issue. However, if fixing the cable
#	connection does not fix the issue, further troubleshooting is necessary. 
#----------------------------------------
def ethernet_issue():
    # Popup window setup
    popup = tk.Tk()
    popup.title('Ethernet Connection Issue Occurred')
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    popup_width = 0.5 * screen_width
    popup_height = 0.5 * screen_height
    horizontal_offset = 0.25 * screen_width
    vertical_offset = 0.25 * screen_height
    popup.geometry('%dx%d+%d+%d' % (popup_width, popup_height, horizontal_offset, vertical_offset))
    
    # Popup window content
    text = tk.Text(popup, wrap=tk.WORD, padx=5, pady=5)
    text.pack()
    text.insert(tk.END, 'Ethernet cable may be loose or disconnected\n\n')
    text.insert(tk.END, 'Please check that the  blue ethernet cable is properly connected to the Raspberry Pi and the power supply\n\n')
    text.insert(tk.END, 'Refer to Developer Documentation page ___ for more information if needed')
    
    button = tk.Button(popup, text='Continue', command=lambda: popup.destroy())
    button.pack()
    
    popup.mainloop()



#----------------------------------------
# USB_not_detected()
#
# function description:
#	This function is called when the startup function that checks for
#	a connected USB drive does not find one. This function creates a popup
#	window that prompts the user to connect a USB drive before continuing (so
#	that the result files can be copied over at the end of testing). 
#----------------------------------------
def USB_not_detected():
    # Popup window setup
    popup = tk.Tk()
    popup.title('No USB Drive Detected')
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    popup_width = 0.5 * screen_width
    popup_height = 0.5 * screen_height
    horizontal_offset = 0.25 * screen_width
    vertical_offset = 0.25 * screen_height
    popup.geometry('%dx%d+%d+%d' % (popup_width, popup_height, horizontal_offset, vertical_offset))
    
    # Popup window content
    text = tk.Text(popup, wrap=tk.WORD, padx=5, pady=5)
    text.pack()
    text.insert(tk.END, 'No USB drive was detected\n\n')
    text.insert(tk.END, 'Please connect a USB drive to one of the USB ports on the Raspberry Pi to receive the result files after testing completes\n\n')
    text.insert(tk.END, 'Or, continue without a USB drive --- the result files will be stored in the Results folder of the program directory, and can be accessed  from there')
    
    button = tk.Button(popup, text='Continue', command=lambda: popup.destroy())
    button.pack()
    
    popup.mainloop()



#----------------------------------------
# lead_connection_issue()
#
# function description:
#	This function is called when the low-voltage startup test measures
#	currents at levels that are not expected for that applied voltage, indicating
#	a possible issue with the lead connections. This function creates a popup window
#	that prompts the user to check the lead connections before continuing. 
#----------------------------------------
def lead_connection_issue():
    # Popup window setup
    popup = tk.Tk()
    popup.title('Possible Lead Connection Issue')
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    popup_width = 0.5 * screen_width
    popup_height = 0.5 * screen_height
    horizontal_offset = 0.25 * screen_width
    vertical_offset = 0.25 * screen_height
    popup.geometry('%dx%d+%d+%d' % (popup_width, popup_height, horizontal_offset, vertical_offset))
    
    # Popup window content
    text = tk.Text(popup, wrap=tk.WORD, padx=5, pady=5)
    text.pack()
    text.insert(tk.END, 'A low-voltage test has detected the possibility of an open circuit\n\n')
    text.insert(tk.END, 'Please re-check the lead connections, then click Continue\n\n')
    text.insert(tk.END, 'If the leads are already properly connected, click Continue. This message may simply be the result of an unusually high-resistance cell')
    
    button = tk.Button(popup, text='Continue', command=lambda: popup.destroy())
    button.pack()
    
    popup.mainloop()