import tkinter as tk
from tkinter import messagebox
import csv
from datetime import datetime
def create_idea():
    clear_content() #kills previous content
    category_label = tk.Label(content_frame, text="Enter the category (e.g., character, creature plot, setting):")
    category_label.grid(row=3, column=1)
    category_entry = tk.Entry(content_frame)
    category_entry.grid(row=3, column=2)
    name_label = tk.Label(content_frame, text="Enter the name of the idea or character:")
    name_label.grid(row=4, column=1)
    name_entry = tk.Entry(content_frame)
    name_entry.grid(row=4, column=2)
    description_label = tk.Label(content_frame, text="Enter a brief description:")
    description_label.grid(row=5, column=1)
    description_entry = tk.Text(content_frame, height=4, width=20)
    description_entry.grid(row=5, column=2, rowspan=3)
    #for entering data into csv
    def submit_idea():
        category = category_entry.get()
        name = name_entry.get()
        description = description_entry.get("1.0", tk.END).strip()
        if not category or not name or not description:
            messagebox.showerror("Input Error", "All fields must be filled out.")
            return
        date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_idea_to_csv(category, name, description, date_created)
        clear_entries(category_entry, name_entry, description_entry)
    #for calling submission
    submit_button = tk.Button(content_frame, text="Submit", command=submit_idea,)
    submit_button.grid(row=8, column=2)
   

#for clearing entries after submission

def clear_entries(first_entry, second_entry, text_entry):
    first_entry.delete(0, tk.END)
    second_entry.delete(0, tk.END)
    text_entry.delete("1.0", tk.END)
    

  #prints a list of all the ideas in ideas.csv  
def view_ideas():
    with open('final-project/ideas.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        ideas_window = tk.Toplevel(root)
        ideas_window.title("Existing Ideas and Characters")
        row_num = 0
        for row in reader:
            idea_text = f"Category: {row[0]} \nName: {row[1]} \nDescription: {row[2]} \nDate Created: {row[3]}"
            idea_label = tk.Label(ideas_window, text=idea_text, wraplength=400, justify="left")
            idea_label.grid(row=row_num, column=0, sticky="w")
            row_num += 1

#does not open a new window, rather alters the existing root window to display search results            
def search_ideas():
    clear_content() #kills previous content
    search_label = tk.Label(content_frame, text="Enter the category to search for:")
    search_label.grid(row=1, column=1)
    search_entry = tk.Entry(content_frame)
    search_entry.grid(row=1, column=2)
    def perform_search():
        clear_results_row()  # clears previous search results
        search_category = search_entry.get()
        results = search_ideas_in_csv(search_category)
        if results:
            results_text = ""
            for row in results:
                results_text += f"Name: {row[1]} \nDescription: {row[2]} \nDate Created: {row[3]}\n\n"
        else:
            results_text = f"No ideas found in category '{search_category}'."
        results_label = tk.Label(content_frame, text=results_text, wraplength=400, justify="left")
        results_label.grid(row=3, column=1, columnspan=2)
    search_button = tk.Button(content_frame, text="Search", command=perform_search)
    search_button.grid(row=2, column=2)

#for clearing the results of a search before a new search
def clear_results_row(row_num=3):
    for widget in content_frame.winfo_children():
        info = widget.grid_info()
        if info.get('row') == row_num:
            widget.destroy()

#gets rid of all content in the content frame before new content is added
def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()

def main(*args):
    if selected_option.get() == "Create a new idea or character":
        create_idea()
    elif selected_option.get() == "View existing ideas or characters":
        view_ideas()
    elif selected_option.get() == "Search specific ideas or characters by category":
        search_ideas()





root = tk.Tk()
root.title('Ideation Creation')
message = tk.Label(root, text="""Welcome to Ideation Creation! What would you like to do?""")
message.grid(row=1, column=1, columnspan=2)

options = ["Create a new idea or character", "View existing ideas or characters", "Search specific ideas or characters by category"]

selected_option = tk.StringVar(root)
selected_option.set(options[0])  # default value

option_menu = tk.OptionMenu(root, selected_option, *options, command=main)
option_menu.grid(row=2, column=1, columnspan=2)
#creates a frame to hold deleteable content
content_frame = tk.Frame(root)
content_frame.grid(row=3, column=1, columnspan=2)

#seperate functions for adding and searching ideas in the csv file and testing

def add_idea_to_csv(category, name, description, date_created, filename='final-project/ideas.csv'):
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([category, name, description, date_created])

def search_ideas_in_csv(category, filename='final-project/ideas.csv'):
    results = []
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0].lower() == category.lower():
                    results.append(row)
    except FileNotFoundError:
        pass
    return results


    
root.mainloop()




