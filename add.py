import tkinter as tk
import re
import json
from tkinter import scrolledtext
from tkinter import *
from webbrowser import BackgroundBrowser
from PIL import Image, ImageTk


# Hash table constants
BUCKET_SIZE = 3
BUCKET_CAPACITY = 3 # Maximum capacity for each bucket
window = tk.Tk()
window.title("Online shopping")
WINDOW_TITLE = "Online shopping"
WINDOW_WIDTH = 1980
WINDOW_HEIGHT = 1080


# File paths
HASH_TABLE_FILE = "hash_table.txt"
DATA_FILE = "data.txt"

# Create the hash table
hash_table = [[] for _ in range(BUCKET_SIZE)]

# Load hash table and data from files if they exist
try:
    with open(HASH_TABLE_FILE, "r") as file:
        hash_table = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    pass


try:
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = {}
except json.JSONDecodeError:
    data = {}


def hash_function(key):
    name_length = len(key)
    if name_length > 6:
        return 2  # Higher bucket index
    elif name_length < 6:
        return 0  # Lower bucket index
    else:
        return 1  # Middle bucket index


def insert_item(key, price, quantity):
    index = hash_function(key)

    if len(hash_table[index]) >= BUCKET_CAPACITY and '#' not in [item['name'] for item in hash_table[index]]:
        message_label.config(text=f"Overflow: Bucket {index} is already full and does not contain '#'. Cannot insert key {key}")
        return False

    for item in hash_table[index]:
        if item["name"] == key:
            message_label.config(text=f"Key {key} already exists in the hash table.")
            return False

    # Append new item if '#' is present
    for i, item in enumerate(hash_table[index]):
        if item["name"] == '#':
            hash_table[index][i] = {"name": key, "price": price, "quantity": quantity}
            message_label.config(text=f"Key {key} inserted into the hash table.")
            break
    else:
        item = {"name": key, "price": price, "quantity": quantity}
        hash_table[index].append(item)
        message_label.config(text=f"Key {key} inserted into the hash table.")

    data[key] = {"price": price, "quantity": quantity}

    # Save hash table and data to files
    save_hash_table()
    save_data()
    return True 

def delete_item(key):
    index = hash_function(key)

    for item in hash_table[index]:
        if item["name"] == key:
            item["name"] = '#' # Mark the item as deleted with '#'
            del data[key]
            message_label.config(text=f"Key {key} deleted from the hash table.")

            # Mark the deleted item in the hash_table.txt file
            with open("hash_table.txt", "r+") as file:
                lines = file.readlines()
                file.seek(0)
                for line in lines:
                    if key in line:
                        line = line.replace(line.strip(), "#" + line.strip())
                    file.write(line)
                file.truncate()

            # Save hash table and data to files
            save_hash_table()
            save_data()

            return True

    message_label.config(text=f"Key {key} not found in the hash table.")
    return False


def search_item(key):
    if not isinstance(key, str):
        message_label.config(text=f"Invalid key. Key must be a string.")
        return None

    if not key.isalpha():
        message_label.config(text=f"Invalid key. Key must contain only characters.")
        return None

    index = hash_function(key)

    for item in hash_table[index]:
        if item["name"] == key:
            message_label.config(text=f"Key {key} found in the hash table.")
            display_items()  # Call a function to display all items in the hash table
            return item

    message_label.config(text=f"Key {key} not found in the hash table.")
    return None



def modify_item(old_key, new_key, new_price, new_quantity):
    index = hash_function(old_key)

    for item in hash_table[index]:
        if item["name"] == old_key:
            item["name"] = new_key
            item["price"] = new_price
            item["quantity"] = new_quantity
            del data[old_key]
            data[new_key] = {"price": new_price, "quantity": new_quantity}
            message_label.config(text=f"Key {old_key} modified to {new_key} in the hash table.")

            # Save hash table and data to files
            save_hash_table()
            save_data()

            return True

    message_label.config(text="Old key not found in the hash table.")
    return False


def load_hash_table():
    global hash_table
    hash_table = [[] for _ in range(BUCKET_SIZE)]
    try:
        with open(HASH_TABLE_FILE, "r") as file:
            lines = file.readlines()
            for line in lines:
                parts = line.split("|")
                index = int(re.search(r'\d+', parts[0]).group())
                if parts[1] == "/":
                    continue
                elif parts[1] == "#":
                    continue
                else:
                    key = parts[2].strip()
                    item = {"name": key}
                    hash_table[index].append(item)
    except FileNotFoundError:
        pass


def load_data():
    global data
    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    except json.JSONDecodeError:
        data = {}

        
# GUI functions
def validate_item_name(name):
    if re.match("^[a-zA-Z]+$", name):
        return True
    return False


def validate_number(input):
    if re.match("^[0-9]*$", input):
        return True
    return False


def display_hash_table():
    global hashtable_frame

    hashtable_frame.destroy()

    hashtable_frame = tk.Frame(window, padx=10, pady=10, bd=1, relief="solid")
    hashtable_frame.pack(pady=20, side="left")  # Increase pady to move the table up

    header_row = tk.Frame(hashtable_frame, bg="gray", relief="solid", bd=1)  # Add relief and bd for border
    header_row.pack(fill="x", pady=5)

    header_bucket_label = tk.Label(header_row, text="Bucket", width=30, bg="gray", fg="white", relief="solid", bd=1)  # Increase width to make it larger
    header_bucket_label.pack(side="left")

    header_name_label = tk.Label(header_row, text="Name", width=45, bg="gray", fg="white", relief="solid", bd=1)  # Increase width to make it larger
    header_name_label.pack(side="left")

    for index, bucket in enumerate(hash_table):
        names = [item["name"] if item["name"] != '#' else '#' for item in bucket]
        names.extend(['/' * 4] * (BUCKET_CAPACITY - len(names)))  # Append '/' for unused space

        item_row = tk.Frame(hashtable_frame, relief="solid", bd=1)  # Add relief and bd for border
        item_row.pack(fill="x", pady=2)

        bucket_label = tk.Label(item_row, text=f"{index}", width=30, relief="solid", bd=1)  # Increase width to make it larger
        bucket_label.pack(side="left")

        item_name_label = tk.Label(item_row, text=" -> ".join(names), width=50, relief="solid", bd=1)  # Increase width to make it larger
        item_name_label.pack(side="left")

    

def display_items():
    global items_list_frame  # Declare items_list_frame as a global variable

    items_list_frame.destroy()

    items_list_frame = tk.Frame(window, padx=10, pady=10, bd=1, relief="solid")
    items_list_frame.pack(pady=(10, 20), side="right")  # Add vertical padding of 10 pixels at the top, 20 pixels at the bottom, and display on the right side

    header_row = tk.Frame(items_list_frame, bg="gray", relief="solid", bd=1)  # Add relief and bd for border
    header_row.pack(fill="x", pady=5)

    header_name_label = tk.Label(header_row, text="Name", width=35, bg="gray", fg="white", relief="solid", bd=1)  # Add relief and bd for border
    header_name_label.pack(side="left")

    header_price_label = tk.Label(header_row, text="Price", width=20, bg="gray", fg="white", relief="solid", bd=1)  # Add relief and bd for border
    header_price_label.pack(side="left")

    header_quantity_label = tk.Label(header_row, text="Quantity", width=20, bg="gray", fg="white", relief="solid", bd=1)  # Add relief and bd for border
    header_quantity_label.pack(side="left")

    for bucket in hash_table:
        for item in bucket:
            item_row = tk.Frame(items_list_frame, relief="solid", bd=1)  # Add relief and bd for border
            item_row.pack(fill="x", pady=2)

            item_name_label = tk.Label(item_row, text=item["name"], width=35, relief="solid", bd=1)  # Add relief and bd for border
            item_name_label.pack(side="left")

            item_price_label = tk.Label(item_row, text=item["price"], width=20, relief="solid", bd=1)  # Add relief and bd for border
            item_price_label.pack(side="left")

            item_quantity_label = tk.Label(item_row, text=item["quantity"], width=20, relief="solid", bd=1)  # Add relief and bd for border
            item_quantity_label.pack(side="left")
            

def save_hash_table():
    with open("hash_table.txt", "w") as file:
        for i, bucket in enumerate(hash_table):
            bucket_data = []

            # Sort items based on the length of item name
            bucket.sort(key=lambda x: len(x['name']))

            for item in bucket:
                if item['name'] != '#':
                    bucket_data.append(str(item['name']))
                else:
                    # Append new item if '#' is present
                    bucket_data.append("#")

            # Add '/' for unused space
            unused_space = BUCKET_CAPACITY - len(bucket_data)
            bucket_data.extend(['/' * 4] * unused_space)

            # Replace deleted items with '#'
            for j in range(len(bucket_data)):
                if bucket_data[j] == '#':
                    if j > 0:
                        bucket_data[j - 1] = '#'

            # Join items using '->'
            bucket_details = '->'.join(bucket_data)

            # Display '/' for empty bucket
            if len(bucket) == 0:
                bucket_details = f"{i}| {'->////' * BUCKET_CAPACITY}"
            else:
                bucket_details = f"{i}| {bucket_details}"

            file.write(bucket_details + "\n")
            
            
def save_data():
    with open("data.txt", "w") as file:
        for bucket in hash_table:
            for item in bucket:
                file.write(f"{item['name']}|{item['price']}|{item['quantity']}\n")


def open_add_window():
    def add_item():
        name = name_entry.get()
        price = price_entry.get()
        quantity = quantity_entry.get()

        if not validate_item_name(name):
            message_label.config(text="Invalid item name. Item name should only contain alphabets.")
            return

        if not validate_number(price):
            message_label.config(text="Invalid price. Price should be a numeric value.")
            return

        if not validate_number(quantity):
            message_label.config(text="Invalid quantity. Quantity should be a numeric value.")
            return

        if insert_item(name, price, quantity):
            add_window.destroy()
            display_items()
            display_hash_table()

    add_window = tk.Toplevel(window)
    add_background_image = Image.open("1.jpg")
    add_background_image = add_background_image.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.ANTIALIAS)
    add_background_photo = ImageTk.PhotoImage(add_background_image)

    background_label = tk.Label(add_window, image=add_background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    add_window.title("Add Item")
    add_window.configure(bg="lightgray")
    
    name_label = tk.Label(add_window, text="Name:", bg="lightgray", font=("Arial", 14))
    name_label.pack(pady=10)

    name_entry = tk.Entry(add_window, font=("Arial", 14))
    name_entry.pack(pady=5, padx=10)

    price_label = tk.Label(add_window, text="Price:", bg="lightgray", font=("Arial", 14))
    price_label.pack(pady=10)

    price_entry = tk.Entry(add_window, font=("Arial", 14))
    price_entry.pack(pady=5, padx=10)

    quantity_label = tk.Label(add_window, text="Quantity:", bg="lightgray", font=("Arial", 14))
    quantity_label.pack(pady=10)

    quantity_entry = tk.Entry(add_window, font=("Arial", 14))
    quantity_entry.pack(pady=5, padx=10)

    add_button = tk.Button(add_window, text="Add", command=add_item, bg="lightblue", fg="white", font=("Arial", 14))
    add_button.pack(pady=20, padx=10)

    message_label = tk.Label(add_window, text="", bg="lightgray", fg="red", font=("Arial", 14))
    message_label.pack()
    
    add_window.mainloop()
    

def open_delete_window():
    def delete_item_gui():
        name = name_entry.get()

        if delete_item(name):
            delete_window.destroy()
            display_items()
            display_hash_table()

    delete_window = tk.Toplevel(window)
    
    delete_background_image = Image.open("2.jpg")
    delete_background_image = delete_background_image.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.ANTIALIAS)
    delete_background_photo = ImageTk.PhotoImage(delete_background_image)

    background_label = tk.Label(delete_window, image=delete_background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    delete_window.title("Delete Item")
    delete_window.configure(bg="lightgray")

    name_label = tk.Label(delete_window, text="Name:", bg="lightgray", font=("Arial", 14))
    name_label.pack(pady=10)

    name_entry = tk.Entry(delete_window, font=("Arial", 14))
    name_entry.pack(pady=5, padx=10)

    delete_button = tk.Button(delete_window, text="Delete", command=delete_item_gui, bg="lightcoral", fg="white",
                              font=("Arial", 14))
    delete_button.pack(pady=20, padx=10)

    message_label = tk.Label(delete_window, text="", bg="lightgray", fg="red", font=("Arial", 14))
    message_label.pack()
    delete_window.mainloop()
    

def open_modify_window():
    def modify_item_gui():
        old_name = old_name_entry.get()
        new_name = new_name_entry.get()
        new_price = new_price_entry.get()
        new_quantity = new_quantity_entry.get()

        if not validate_item_name(new_name):
            message_label.config(text="Invalid item name. Item name should only contain alphabets.")
            return

        if not validate_number(new_price):
            message_label.config(text="Invalid price. Price should be a numeric value.")
            return

        if not validate_number(new_quantity):
            message_label.config(text="Invalid quantity. Quantity should be a numeric value.")
            return

        if modify_item(old_name, new_name, new_price, new_quantity):
            modify_window.destroy()
            display_items()
            display_hash_table()

    modify_window = tk.Toplevel(window)
    modify_background_image = Image.open("3.jpg")
    modify_background_image = modify_background_image.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.ANTIALIAS)
    modify_background_photo = ImageTk.PhotoImage(modify_background_image)

    background_label = tk.Label(modify_window, image=modify_background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    modify_window.title("Modify Item")
    modify_window.configure(bg="lightgray")

    old_name_label = tk.Label(modify_window, text="Old Name:", bg="lightgray", font=("Arial", 14))
    old_name_label.pack(pady=10)

    old_name_entry = tk.Entry(modify_window, font=("Arial", 14))
    old_name_entry.pack(pady=5, padx=10)

    new_name_label = tk.Label(modify_window, text="New Name:", bg="lightgray", font=("Arial", 14))
    new_name_label.pack(pady=10)

    new_name_entry = tk.Entry(modify_window, font=("Arial", 14))
    new_name_entry.pack(pady=5, padx=10)

    new_price_label = tk.Label(modify_window, text="New Price:", bg="lightgray", font=("Arial", 14))
    new_price_label.pack(pady=10)

    new_price_entry = tk.Entry(modify_window, font=("Arial", 14))
    new_price_entry.pack(pady=5, padx=10)

    new_quantity_label = tk.Label(modify_window, text="New Quantity:", bg="lightgray", font=("Arial", 14))
    new_quantity_label.pack(pady=10)

    new_quantity_entry = tk.Entry(modify_window, font=("Arial", 14))
    new_quantity_entry.pack(pady=5, padx=10)

    modify_button = tk.Button(modify_window, text="Modify", command=modify_item_gui, bg="lightgreen", fg="white",
                              font=("Arial", 14))
    modify_button.pack(pady=20, padx=10)

    message_label = tk.Label(modify_window, text="", bg="lightgray", fg="red", font=("Arial", 14))
    message_label.pack()
    modify_window.mainloop()
    

def open_search_window():
    def search():
        name = name_entry.get()

        item = search_item(name)

        if item:
            message_label.config(text=f"Name: {item['name']}\nPrice: {item['price']}\nQuantity: {item['quantity']}")
        else:
            message_label.config(text=f"Item '{name}' not found in the hash table.")

        search_window.destroy()

    search_window = tk.Toplevel(window)
    search_background_image = Image.open("4.jpg")
    search_background_image = search_background_image.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.ANTIALIAS)
    search_background_photo = ImageTk.PhotoImage(search_background_image)

    background_label = tk.Label(search_window, image=search_background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    search_window.title("Search Item")
    search_window.configure(bg="lightgray")

    name_label = tk.Label(search_window, text="Name:", bg="lightgray", font=("Arial", 14))
    name_label.pack(pady=10)

    name_entry = tk.Entry(search_window, font=("Arial", 14))
    name_entry.pack(pady=5, padx=10)

    search_button = tk.Button(search_window, text="Search", command=search, bg="lightyellow", fg="black",
                              font=("Arial", 14))
    search_button.pack(pady=20, padx=10)

    message_label = tk.Label(search_window, text="", bg="lightgray", fg="black", font=("Arial", 14))
    message_label.pack(pady=10)
    search_window.mainloop()
    
# Main GUI window
window.title("Online Shopping System using Hashing")
WINDOW_TITLE = "Online shopping system using hashing"
WINDOW_WIDTH = 2000
WINDOW_HEIGHT = 1500
background_image = Image.open("USU-Online-Shopping-2.jpg")
background_image = background_image.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.ANTIALIAS)
background_photo = ImageTk.PhotoImage(background_image)

# Create a label to hold the background image
background_label = tk.Label(window, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Add the heading text to the label
heading_text = "Online Shopping System using Hashing"
heading_label = tk.Label(window, text=heading_text, font=("Arial", 24, "bold"), pady=20)
heading_label.config(highlightthickness=0)
heading_label.place(relx=0, rely=0, anchor="nw")


# Create a frame to hold the controls
controls_frame = tk.Frame(window)
controls_frame.pack(pady=90)

add_button = tk.Button(controls_frame, text="Add Item", command=open_add_window, font=("Arial", 14), bg="grey",
                       fg="white", padx=10, pady=5)
add_button.pack(side="left", padx=(10, 5))

delete_button = tk.Button(controls_frame, text="Delete Item", command=open_delete_window, font=("Arial", 14),
                          bg="grey", fg="white", padx=10, pady=5)
delete_button.pack(side="left", padx=5)

modify_button = tk.Button(controls_frame, text="Modify Item", command=open_modify_window, font=("Arial", 14),
                          bg="grey", fg="white", padx=10, pady=5)
modify_button.pack(side="left", padx=5)

search_button = tk.Button(controls_frame, text="Search Item", command=open_search_window, font=("Arial", 14),
                          bg="grey", fg="white", padx=10, pady=5)
search_button.pack(side="left", padx=5)


# Create a label to display messages
message_label = tk.Label(window, text="", bg="lightgray", fg="red", font=("Arial", 14))
message_label.pack(pady=10)

# Create a frame to display the hash table
hashtable_frame = tk.Frame(window, padx=5, pady=5, bd=1, relief="solid")
hashtable_frame.pack(pady=(10, 0), padx=10, anchor="n")

header_row = tk.Frame(hashtable_frame, bg="gray")
header_row.pack(fill="x", pady=5)

header_bucket_label = tk.Label(header_row, text="Bucket", width=15, bg="gray", fg="white")
header_bucket_label.pack(side="left")

header_name_label = tk.Label(header_row, text="Name", width=30, bg="gray", fg="white")
header_name_label.pack(side="left")


# Create a frame to display the list of items
items_list_frame = tk.Frame(window, padx=10, pady=10, bd=1, relief="solid")
items_list_frame.pack(pady=(10, 0), anchor="n")


# Display the initial hash table and items list
display_hash_table()
display_items()

# Run the GUI
window.mainloop()

