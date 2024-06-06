
# Developer Name: Sree
import tkinter as tk
from tkinter import ttk
from pandastable import Table, TableModel
import pandas as pd
from sqlalchemy import create_engine, text
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from tkinter import simpledialog

###################################sql #################################################

nested_buttons = {}
nested_button= ""
database = "factcheck"
username = ""
password = ""
g_db = ""
g_tbl = ""
df = pd.DataFrame()


def check_connection(username, password):
    try:
        global engine
        engine = create_engine(f'mysql+pymysql://{username}:{password}@localhost:3306/{database}')
        connection = engine.connect()
        connection.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False



def get_sql_databases(engine):
    df = pd.read_sql("show databases;", engine)
    return list(df["Database"].values)


def get_nested_tables(engine,database_name):

    new_url = engine.url.set(database=database_name)
    engine = create_engine(new_url)
    df = pd.read_sql("show tables;", engine)

    column_name = f"Tables_in_{database_name}"
    tables = list(df[column_name])
    return tables

def get_df(us, pw,  database,table):
    try:
        engine = create_engine(f'mysql+pymysql://{us}:{pw}@localhost:3306/{database}')
        df = pd.read_sql(f"select * from {table};", engine)
        return database, table , df
    except Exception as e:
        # print(f"An error occurred: {e}")
        return database, table , pd.DataFrame()


def custome_query_df(query):

    engine = create_engine(f'mysql+pymysql://{username}:{password}@localhost:3306/{g_db}')
    try:
        query_df = pd.read_sql(query , engine)
        return query_df
    except Exception as e:
        return pd.DataFrame()


def delete_query_data(delete_query):
    try:

        engine = create_engine(f'mysql+pymysql://{username}:{password}@localhost:3306/{g_db}')
        with engine.connect() as connection:
            result = connection.execute(text(delete_query))
            connection.commit()  
        return True, result.rowcount
    except Exception as e:
        return False, e

def dropdown_action(us, pw, database_name, table_name, database_label ,table_label):
    # Simulate a pandas DataFrame
    global df
    global g_tbl
    global g_db
    g_db, g_tbl, df = get_df(us, pw, database_name, table_name)
    # Display the DataFrame in the right container

    update_labels(g_db,database_label,  g_tbl ,table_label)
    display_dataframe(df)



def download_table():
    # Prompt user to select download location
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"{g_tbl}.csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        # Save DataFrame to the selected file path
        if len(df) != 0:
            print(df.shape,"=====================")
            df.to_csv(file_path, index=False)
            print(f"Table downloaded successfully at {file_path}!")
            messagebox.showinfo("Success", "File downloaded successfully!", icon="info")
        else:
            messagebox.showwarning("Warning", "Please select the data correctly!", icon="warning")



####################################Sql end #############################################


############################### ui code #########################################
def login(event=None):
    global username
    global password
    username = entry_username.get()
    password = entry_password.get()

    if check_connection(username, password):
        print("connection created successfullY!")
        # Change login page into home page
        create_home_page(username, password)
    else:
        print("Invalid username or password.")
        warning_label.config(text="Invalid username or password.")

def run_own_query():
    # Create a new window for entering SQL queries
    query_window = tk.Toplevel(app)
    query_window.title("SQL Query Editor")

    # Create a Text widget for entering the SQL query
    query_text = tk.Text(query_window, wrap=tk.WORD, height=15, width=50)
    query_text.pack(padx=10, pady=10)

    # Function to handle running the query
    def run_query():
        query = query_text.get("1.0", tk.END).strip()  # Get the entered query
        if query:
            if query.startswith("select"):
                global df
                df = custome_query_df(query)  # Call the dummy function with the query
                if len(df) != 0:
                    display_dataframe(df)
                    query_window.destroy()  # Close the query window
                else:
                    # Show a message indicating that the query is empty or invalid
                    tk.messagebox.showerror("Error", "Please enter a valid SQL query.")

            else:
                sc_or_not , affected_rows = delete_query_data(query)
                if sc_or_not:
                    dropdown_action(username, password, g_db, g_tbl, database_label, table_label)
                    tk.messagebox.showinfo("Success", f"{affected_rows} no of rows affected.")

                    query_window.destroy()  # Close the query window

                else:
                    tk.messagebox.showerror("Error", f"Reason: {affected_rows}")



    # Create a "Cancel" button to close the window
    cancel_button = tk.Button(query_window, text="Cancel", command=query_window.destroy, bg="red", fg="white" )
    cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Create a "Run" button to execute the query
    run_button = tk.Button(query_window, text="Run", command=run_query,bg="blue", fg="white")
    run_button.pack(side=tk.RIGHT, padx=5, pady=5)


def update_labels(database, database_label, table,table_label):
    database_label.config(text=f"Database: {database}")
    table_label.config(text=f"Table: {table}")


def create_home_page(username, password):
    global right_container
    global database
    global engine
    refresh_action = None

    engine = create_engine(f'mysql+pymysql://{username}:{password}@localhost:3306/{database}')
    database_buttons = get_sql_databases(engine)

    # Clear login widgets
    label_username.grid_forget()
    entry_username.grid_forget()
    label_password.grid_forget()
    entry_password.grid_forget()
    button_login.grid_forget()
    warning_label.grid_forget()

    # Create PanedWindow for resizable containers
    paned_window = tk.PanedWindow(app, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
    paned_window.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew", padx=5, pady=5)

    left_container = tk.Frame(paned_window, bg="lightgray")
    left_container_scrollbar = tk.Scrollbar(left_container, orient=tk.VERTICAL)
    left_container_canvas = tk.Canvas(left_container, bg="lightgray", yscrollcommand=left_container_scrollbar.set)
    left_container_scrollbar.config(command=left_container_canvas.yview)
    left_container_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    left_container_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    left_container_scrollbar.bind("<Configure>", lambda e: left_container_canvas.configure(scrollregion=left_container_canvas.bbox("all")))
    paned_window.add(left_container, width=app.winfo_width() * 0.15)

    # Add a frame inside the canvas to hold buttons
    left_container_frame = tk.Frame(left_container_canvas, bg="lightgray")
    left_container_canvas.create_window((0, 0), window=left_container_frame, anchor="nw")

    # Bind mousewheel event to the left container canvas globally
    def _on_mousewheel(event):
        x, y = app.winfo_pointerxy()  # Get mouse coordinates
        left_container_x = left_container.winfo_rootx()  # Get left container x coordinate
        left_container_y = left_container.winfo_rooty()  # Get left container y coordinate
        left_container_width = left_container.winfo_width()  # Get left container width
        left_container_height = left_container.winfo_height()  # Get left container height
        
        # Check if mouse is within left container boundaries
        if (left_container_x <= x <= left_container_x + left_container_width) and \
           (left_container_y <= y <= left_container_y + left_container_height):
            left_container_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    app.bind_all("<MouseWheel>", _on_mousewheel)



    left_container_scrollbar.bind("<Configure>", lambda e: left_container_canvas.configure(scrollregion=left_container_canvas.bbox("all")))
    paned_window.add(left_container, width=app.winfo_width() * 0.15)

    # Add a frame inside the canvas to hold buttons
    left_container_frame = tk.Frame(left_container_canvas, bg="lightgray")
    left_container_canvas.create_window((0, 0), window=left_container_frame, anchor="nw")

    # Create a label widget for the title "SCHEMA"
    schema_title_label = tk.Label(left_container_frame, text="SCHEMA", bg="lightgray", fg="black", font=("Helvetica", 14, "bold"))
    schema_title_label.pack(pady=(10, 5))  # Adjust padding as needed

    # Create a list to hold the buttons for later access
    button_list = []

    for db in database_buttons:
        button = tk.Menubutton(
            left_container_frame,
            text=f"D: {db}",
            bg="lightgray",
            fg="black",
            activebackground="blue",
            activeforeground="white",
            relief=tk.RAISED,
            direction=tk.RIGHT
        )
        button.pack(pady=5, fill=tk.X)
        button_list.append(button)

        # Create a menu for each button
        menu = tk.Menu(button, tearoff=0)
        nested_tables = get_nested_tables(engine, db)

        for tbl in nested_tables:  # Adding 5 buttons to the dropdown menu as an example
            menu.add_command(label=f"{tbl}", command=lambda db=db, tbl=tbl: dropdown_action(username, password, db, tbl, database_label, table_label))

        button.config(menu=menu)

    # Create a right PanedWindow for resizable containers
    right_paned_window = tk.PanedWindow(paned_window, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=5)
    paned_window.add(right_paned_window, width=app.winfo_width() * 0.85)

    # Add a frame for the menu at the top of the right container
    menu_frame = tk.Frame(right_paned_window, bg="lightgray")
    right_paned_window.add(menu_frame, height=app.winfo_height() * 0.10)

    # Create a Label to show the purpose of the menu frame
    menu_label = tk.Label(menu_frame, text="Developer Mode.", bg="lightgray", fg="black")
    menu_label.pack(padx=5, pady=5)

    # Create labels to display database and table variables
    global database_label
    database_label = tk.Label(menu_frame, text="Database: ", bg="lightgray", fg="black")
    database_label.pack(side=tk.LEFT, padx=5, pady=5)

    global table_label
    table_label = tk.Label(menu_frame, text="Table: ", bg="lightgray", fg="black")
    table_label.pack(side=tk.LEFT, padx=5, pady=5)

    # Create a Download Button
    download_button = tk.Button(menu_frame, text="Download Table", command=download_table, bg="green", fg="white", relief=tk.RAISED)
    download_button.pack(side=tk.RIGHT, padx=5, pady=5)

    # Create the "Run Own Query" button
    run_query_button = tk.Button(menu_frame, text="Run Own Query", command=run_own_query, bg="white", fg="black")
    run_query_button.pack(side=tk.RIGHT, padx=5, pady=5)

    refresh_button = tk.Button(menu_frame, text="Refresh", command=lambda: dropdown_action(username, password, g_db, g_tbl, database_label, table_label), bg="white", fg="black", relief=tk.RAISED)
    refresh_button.pack(side=tk.RIGHT, padx=5, pady=5)

    # Add a right container for the main content
    right_container = tk.Frame(right_paned_window, bg="white")
    right_paned_window.add(right_container, height=app.winfo_height() * 0.9)

    # Configure row and column weights for resizing
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)




def display_dataframe(df):
    global right_container

    # Clear the right container
    for widget in right_container.winfo_children():
        widget.destroy()

    # Create a frame to hold the table
    frame = tk.Frame(right_container)
    frame.pack(expand=True, fill=tk.BOTH)

    # Create a pandastable Table widget
    table = Table(frame, dataframe=df, showtoolbar=False, showstatusbar=True)
    table.show()



# Create the main application window
app = tk.Tk()
app.title("SrEE")
app.iconbitmap("logo.ico")

# Set initial window size to maximize
# app.geometry("{0}x{1}+0+0".format(app.winfo_screenwidth(), app.winfo_screenheight()))
app.geometry("800x600")

# Define colors from the palette
BG_COLOR = "#DEEFE7"
BUTTON_COLOR = "#159A9C"
TEXT_COLOR = "#002333"
WARNING_COLOR = "red"
FOOTER_COLOR = "#B4BEC9"

# Set background color
app.configure(bg=BG_COLOR)

# Create a container frame to center the login form
login_frame = tk.Frame(app, bg=BG_COLOR)
login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Create a container frame for the title
title_frame = tk.Frame(app, bg=BG_COLOR)
title_frame.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

# Define fonts for the title and other widgets
title_font = ('Helvetica', 24, 'bold')
large_font = ('Helvetica', 14)

# Create and pack the title label in the title_frame
title_label = tk.Label(title_frame, text="SreeQL Easy Explorer", font=title_font, bg=BG_COLOR, fg=TEXT_COLOR)
title_label.pack()

# Create and pack widgets for login page in the login_frame
label_username = tk.Label(login_frame, text="Username:", font=large_font, bg=BG_COLOR, fg=TEXT_COLOR)
label_username.grid(row=0, column=0, padx=10, pady=10)

entry_username = tk.Entry(login_frame, font=large_font)
entry_username.grid(row=0, column=1, padx=10, pady=10)

label_password = tk.Label(login_frame, text="Password:", font=large_font, bg=BG_COLOR, fg=TEXT_COLOR)
label_password.grid(row=1, column=0, padx=10, pady=10)

entry_password = tk.Entry(login_frame, show="*", font=large_font)  
entry_password.grid(row=1, column=1, padx=10, pady=10)

button_login = tk.Button(login_frame, text="Login", font=large_font, command=login, bg=BUTTON_COLOR, fg="white")
button_login.grid(row=2, columnspan=2, padx=10, pady=10)

warning_label = tk.Label(login_frame, font=large_font, fg=WARNING_COLOR, bg=BG_COLOR)
warning_label.grid(row=3, columnspan=2, padx=10, pady=10)

app.bind('<Return>', login)

# Create and place a footer label
footer_label = tk.Label(app, text="Tailored for those who embrace the art of laziness. 🎨💤", font=large_font, bg=FOOTER_COLOR, fg=TEXT_COLOR)
footer_label.place(relx=0.5, rely=0.9, anchor=tk.CENTER)




# Start the application
app.mainloop()