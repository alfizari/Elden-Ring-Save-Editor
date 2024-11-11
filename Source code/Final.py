import json
import glob
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, Scrollbar



# Constants
hex_pattern1_Fixed = '00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00'
possible_name_distances_for_name_tap = [-199]
souls_distance = -219
hp_distance= -303
goods_magic_offset = 0
goods_magic_range = 30000
storage_box_distance = 35900   
drawer_range = 4000 


# Stats offsets
stats_offsets_for_stats_tap = {
    "Level": -223,
    "Vigor": -267,
    "Attunement": -263,
    "Endurance": -259,
    "Vitality": -227,
    "Strength": -255,
    "Dexterity": -251,
    "Intelligence": -247,
    "Faith": -243,
    "Luck": -239,
}

# Set directory
working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)

# load and copy JSON data from files in the current working directory
def load_and_copy_json(file_name):
    file_path = os.path.join(working_directory, file_name)
    with open(file_path, "r") as file:
        return json.load(file).copy()

# Load and copy data from JSON files within the current working directory
inventory_item_hex_patterns = load_and_copy_json("itemshex.json")
inventory_replacement_items = inventory_item_hex_patterns.copy()

inventory_goods_magic_hex_patterns = load_and_copy_json("goods_magic.json")
replacement_items = inventory_goods_magic_hex_patterns.copy()
item_hex_patterns = inventory_goods_magic_hex_patterns

inventory_weapons_hex_patterns = load_and_copy_json("weapons.json")
weapon_item_patterns = inventory_weapons_hex_patterns.copy()

inventory_armor_hex_patterns = load_and_copy_json("armor.json")
armor_item_patterns = inventory_armor_hex_patterns
armor_replacement_items = inventory_armor_hex_patterns.copy()

inventory_ring_hex_patterns = load_and_copy_json("ring.json")
replacement_ring_items = inventory_ring_hex_patterns.copy()
ring_hex_patterns = inventory_ring_hex_patterns
ring_hex_patterns = inventory_ring_hex_patterns

# Main window
window = tk.Tk()
window.title("Dark Souls 3 Save Editor")


# Global variables
file_path_var = tk.StringVar()
current_name_var = tk.StringVar(value="N/A")
new_name_var = tk.StringVar()
current_quantity_var = tk.StringVar(value="N/A")
new_quantity_var = tk.StringVar()
search_var = tk.StringVar()
weapon_search_var = tk.StringVar()
armor_search_var= tk.StringVar()
ring_search_var = tk.StringVar()
current_hp_var= tk.StringVar(value="N/A")
new_hp_var= tk.StringVar()
current_souls_var = tk.StringVar(value="N/A")
new_souls_var = tk.StringVar()
found_storage_items_with_quantity = []
found_items = []
found_armor= []
found_ring= []

# Variables to hold current and new values for each stat
current_stats_vars = {stat: tk.StringVar(value="N/A") for stat in stats_offsets_for_stats_tap}
new_stats_vars = {stat: tk.StringVar() for stat in stats_offsets_for_stats_tap}

# Utility Functions
def find_hex_offset(file_path, hex_pattern):
    pattern_bytes = bytes.fromhex(hex_pattern)
    with open(file_path, 'rb') as file:
        chunk_size = 100034
        offset = 0
        while chunk := file.read(chunk_size):
            if pattern_bytes in chunk:
                byte_offset = chunk.index(pattern_bytes)
                return offset + byte_offset
            offset += chunk_size
    return None

def calculate_offset2(offset1, distance):
    return offset1 + distance

def find_value_at_offset(file_path, offset, byte_size=4):
    with open(file_path, 'rb') as file:
        file.seek(offset)
        value_bytes = file.read(byte_size)
        if len(value_bytes) == byte_size:
            return int.from_bytes(value_bytes, 'little')
    return None

def write_value_at_offset(file_path, offset, value, byte_size=4):
    value_bytes = value.to_bytes(byte_size, 'little')
    with open(file_path, 'r+b') as file:
        file.seek(offset)
        file.write(value_bytes)

# Functions for character name
def find_character_name(file_path, offset, byte_size=32):
    with open(file_path, 'rb') as file:
        file.seek(offset)
        value_bytes = file.read(byte_size)
        name_chars = []
        for i in range(0, len(value_bytes), 2):
            char_byte = value_bytes[i]
            if char_byte == 0:
                break
            if 32 <= char_byte <= 126:
                name_chars.append(chr(char_byte))
            else:
                name_chars.append('.')
        return ''.join(name_chars)

def write_character_name(file_path, offset, new_name, byte_size=32):
    name_bytes = []
    for char in new_name:
        name_bytes.append(ord(char))
        name_bytes.append(0) 
    name_bytes = name_bytes[:byte_size]
    with open(file_path, 'r+b') as file:
        file.seek(offset)
        file.write(bytes(name_bytes))

# Function to open the file
def open_file():
    global name_offset
    file_path = filedialog.askopenfilename(filetypes=[("inventory Files", "*")])
    if file_path:
        file_path_var.set(file_path)
        file_name_label.config(text=f"File: {os.path.basename(file_path)}")
        
        offset1 = find_hex_offset(file_path, hex_pattern1_Fixed)
        if offset1 is not None:
            # Display Souls value
            souls_offset = calculate_offset2(offset1, souls_distance)
            current_souls = find_value_at_offset(file_path, souls_offset)
            current_souls_var.set(current_souls if current_souls is not None else "N/A")

                # Display character name
            for distance in possible_name_distances_for_name_tap:
                name_offset = calculate_offset2(offset1, distance)
                current_name = find_character_name(file_path, name_offset)
                if current_name and current_name != "N/A":
                    current_name_var.set(current_name)
                    break
            else:
                current_name_var.set("N/A")

            for stat, distance in stats_offsets_for_stats_tap.items():
                stat_offset = calculate_offset2(offset1, distance)
                current_stat_value = find_value_at_offset(file_path, stat_offset)
                current_stats_vars[stat].set(current_stat_value if current_stat_value is not None else "N/A")
# For health (test)
            if isinstance(hp_distance, int):
                # Handle the case where hp_distance is a single value
                hp_offset = calculate_offset2(offset1, hp_distance)
                current_hp = find_value_at_offset(file_path, hp_offset)
                current_hp_var.set(current_hp if current_hp is not None else "N/A")
            else:
                # Handle the case where hp_distance is iterable
                for distance in hp_distance:
                    hp_offset = calculate_offset2(offset1, distance)
                    current_hp = find_value_at_offset(file_path, hp_offset)
                    if current_hp and current_hp != "N/A":
                        current_hp_var.set(current_hp)
                        break
                else:
                    current_hp_var.set("N/A")
            # Automatically refresh the item list for the Items tab
            refresh_storage_quantity_list(file_path)
            refresh_item_list(file_path)
            refresh_weapon_list(file_path)
            refresh_armor_list(file_path)
              
        else:
            messagebox.showerror("Pattern Not Found", "Pattern not found in the file.")
        refresh_item_list(file_path)
        refresh_weapon_list(file_path)
        refresh_armor_list(file_path)
       

###### for updating values
def update_souls_value():
    file_path = file_path_var.get()
    if not file_path or not new_souls_var.get():
        messagebox.showerror("Input Error", "Please fill in the file path and new Souls value!")
        return
    
    try:
        new_souls_value = int(new_souls_var.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid decimal number for Souls.")
        return

    offset1 = find_hex_offset(file_path, hex_pattern1_Fixed)
    if offset1 is not None:
        souls_offset = calculate_offset2(offset1, souls_distance)
        write_value_at_offset(file_path, souls_offset, new_souls_value)
        messagebox.showinfo("Success", f"Souls value updated to {new_souls_value}. Open Save Again to see if applied")
    else:
        messagebox.showerror("Pattern Not Found", "Pattern not found in the file.")

#------------------------HP
def update_hp_value():
    file_path = file_path_var.get()
    if not file_path or not new_hp_var.get():
        messagebox.showerror("Input Error", "Please fill in the file path and new hp value!")
        return
    
    try:
        new_hp_value = int(new_hp_var.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid decimal number for hp.")
        return

    offset1 = find_hex_offset(file_path, hex_pattern1_Fixed)
    if offset1 is not None:
        hp_offset = calculate_offset2(offset1, hp_distance)
        write_value_at_offset(file_path, hp_offset, new_hp_value)
        messagebox.showinfo("Success", f"Hp value updated to {new_hp_value}. Open Save Again to see if applied")
    else:
        messagebox.showerror("Pattern Not Found", "Pattern not found in the file.")

#  update namw
def update_character_name():
    file_path = file_path_var.get()
    new_name = new_name_var.get()

    if not file_path or not new_name:
        messagebox.showerror("Input Error", "Please fill in the file path and new character name!")
        return

    write_character_name(file_path, name_offset, new_name)
    messagebox.showinfo("Success", f"Character name updated to '{new_name}'.")
    current_name_var.set(new_name)
    refresh_item_list(file_path)
    refresh_weapon_list(file_path)
    refresh_armor_list(file_path)

def update_stat(stat):
    file_path = file_path_var.get()
    if not file_path or not new_stats_vars[stat].get():
        messagebox.showerror("Input Error", f"Please fill in the new value for {stat}.")
        return

    try:
        new_stat_value = int(new_stats_vars[stat].get())
    except ValueError:
        messagebox.showerror("Invalid Input", f"Please enter a valid decimal number for {stat}.")
        return

    offset1 = find_hex_offset(file_path, hex_pattern1_Fixed)
    if offset1 is not None:
        stat_offset = calculate_offset2(offset1, stats_offsets_for_stats_tap[stat])
        write_value_at_offset(file_path, stat_offset, new_stat_value)
        messagebox.showinfo("Success", f"{stat} updated to {new_stat_value}.")
        current_stats_vars[stat].set(new_stat_value)
    else:
        messagebox.showerror("Pattern Not Found", "Pattern not found in the file.")
# Goods-related function
def find_goods_offset(file_path, key_offset):
    global found_items
    found_items = []
    with open(file_path, 'rb') as file:
        file.seek(key_offset)
        data_chunk = file.read(goods_magic_range)
        print(f"Searching for goods items in range {goods_magic_range}")  # Debugging line
        for item_name, item_hex in item_hex_patterns.items():
            item_bytes = bytes.fromhex(item_hex)
            if item_bytes in data_chunk:
                item_offset = data_chunk.index(item_bytes)
                quantity_offset = key_offset + item_offset + len(item_bytes)
                quantity = find_value_at_offset(file_path, quantity_offset, byte_size=1)
                found_items.append((item_name, quantity))
                print(f"Found {item_name} with quantity {quantity}")  # Debugging line
    return found_items

def find_ring_items(file_path):
    global found_ring
    found_ring = []
    with open(file_path, 'rb') as file:
        data_chunk = file.read()
        for ring_name, ring_hex in ring_hex_patterns.items():
            ring_bytes = bytes.fromhex(ring_hex)
            idx = data_chunk.find(ring_bytes)
            if idx != -1:
                # Assuming quantity is stored right after the ring ID in little-endian format
                quantity_offset = idx + len(ring_bytes)
                quantity = find_value_at_offset(file_path, quantity_offset, byte_size=1)
                found_ring.append((ring_name, quantity))
    return found_ring

def refresh_ring_list(file_path):
    # Find rings in the save file
    updated_rings = find_ring_items(file_path)
    
    # Clear the previous list and display the updated rings
    for widget in ring_list_frame.winfo_children():
        widget.destroy()

    if updated_rings:
        # Create a canvas and scrollbar to contain the rings
        ring_list_canvas = tk.Canvas(ring_list_frame)
        ring_list_scrollbar = Scrollbar(ring_list_frame, orient="vertical", command=ring_list_canvas.yview)
        ring_list_frame_inner = tk.Frame(ring_list_canvas)

        ring_list_frame_inner.bind(
            "<Configure>",
            lambda e: ring_list_canvas.configure(
                scrollregion=ring_list_canvas.bbox("all")
            )
        )

        ring_list_canvas.create_window((0, 0), window=ring_list_frame_inner, anchor="nw")
        ring_list_canvas.configure(yscrollcommand=ring_list_scrollbar.set)

        ring_list_canvas.pack(side="left", fill="both", expand=True)
        ring_list_scrollbar.pack(side="right", fill="y")

        # Add rings to the inner frame
        for ring_name, quantity in updated_rings:
            ring_frame = tk.Frame(ring_list_frame_inner)
            ring_frame.pack(fill="x", padx=10, pady=5)

            ring_label = tk.Label(ring_frame, text=f"{ring_name} (Quantity: {quantity})", anchor="w")
            ring_label.pack(side="left", fill="x", padx=5)

            replace_button = tk.Button(ring_frame, text="Replace", command=lambda ring=ring_name: choose_ring_replacement(ring))
            replace_button.pack(side="right", padx=5)
    else:
        messagebox.showinfo("Info", "No rings found.")

def choose_ring_replacement(ring_name):
    window2 = tk.Toplevel(window)
    window2.title(f"Choose replacement for {ring_name}")

    tk.Label(window2, text="Choose replacement ring:").pack(pady=5)
    search_bar_frame = tk.Frame(window2)
    search_bar_frame.pack(pady=5)
    tk.Label(search_bar_frame, text="Search:").pack(side="left", padx=5)
    search_entry = tk.Entry(search_bar_frame, textvariable=ring_search_var)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", lambda event: filter_ring_replacement_list())

    canvas = tk.Canvas(window2)
    scrollbar = Scrollbar(window2, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    filter_ring_replacement_list_frame = scrollable_frame

    def filter_ring_replacement_list():
        for widget in filter_ring_replacement_list_frame.winfo_children():
            widget.destroy()

        search_term = ring_search_var.get().lower()
        filtered_rings = {k: v for k, v in replacement_ring_items.items() if search_term in k.lower()}

        col = 0
        row = 0
        for name, replacement_hex in filtered_rings.items():
            def on_replace_click(name=name, replacement_hex=replacement_hex):
                quantity = simpledialog.askinteger("Input", f"Enter new quantity for {name}:")
                if quantity is not None:
                    replace_ring(file_path_var.get(), ring_name, replacement_hex, new_quantity=quantity)
                window2.destroy()

            replacement_button = tk.Button(filter_ring_replacement_list_frame, text=name, command=on_replace_click)
            replacement_button.grid(row=row, column=col, padx=5, pady=5)
            
            col += 1
            if col > 3:
                col = 0
                row += 1

def replace_ring(file_path, ring_name, replacement_hex, new_quantity=None):
    if new_quantity is None or not isinstance(new_quantity, int):
        messagebox.showerror("Input Error", "Please enter a valid quantity.")
        return

    replacement_bytes = bytes.fromhex(replacement_hex)
    original_bytes = bytes.fromhex(ring_hex_patterns[ring_name])
    key_offset = find_hex_offset(file_path, hex_pattern1_Fixed) + goods_magic_offset

    with open(file_path, 'r+b') as file:
        file.seek(key_offset)
        data_chunk = file.read(goods_magic_range)

        # Search for the full pattern `original_bytes` in the file
        pattern = original_bytes[:3] + b'\xA0' + original_bytes
        pattern_offset = data_chunk.find(pattern)

        if pattern_offset != -1:
            # Position the file to replace the four bytes after `A0`
            ring_id_offset = key_offset + pattern_offset + 4  # Four bytes after `A0`
            file.seek(ring_id_offset)
            file.write(replacement_bytes)  # Replace with new ID bytes

            # Replace the three bytes before `A0`
            pre_a0_offset = key_offset + pattern_offset  # Three bytes before `A0`
            file.seek(pre_a0_offset)
            file.write(replacement_bytes[:3])  # Replace the first three bytes

            # Update quantity if specified
            quantity_offset = ring_id_offset + len(replacement_bytes)
            write_value_at_offset(file_path, quantity_offset, new_quantity, byte_size=1)

            # Update the displayed rings list
            for i, (found_ring_name, _) in enumerate(found_ring):
                if found_ring_name == ring_name:
                    found_ring[i] = (ring_name, new_quantity)
                    break

            # Refresh the ring list after replacement
            refresh_ring_list(file_path)
            messagebox.showinfo("Success", f"{ring_name} has been replaced.")
        else:
            messagebox.showerror("Not Found", f"Failed to find {ring_name} to replace.")
    refresh_ring_list(file_path)




# Weapon-related functions
def find_weapon_items(file_path, start_offset=0, range_size=543168):
 
    global found_weapons
    found_weapons = []

    with open(file_path, 'rb') as file:
        # Set the file position to the specified starting offset
        file.seek(start_offset)
        
        # Read only the specified range
        data_chunk = file.read(range_size) if range_size is not None else file.read()
        
        for weapon_name, weapon_hex in weapon_item_patterns.items():
            weapon_bytes = bytes.fromhex(weapon_hex)
            if weapon_bytes in data_chunk:
                found_weapons.append(weapon_name)

    return found_weapons

# for armors will show some unused items
def find_armor_items(file_path, start_offset=71550, range_size=None):
 
    global found_armor
    found_armor = []

    with open(file_path, 'rb') as file:
        # Set the file position to the specified starting offset
        file.seek(start_offset)
        
        # Read only the specified range
        data_chunk = file.read(range_size) if range_size is not None else file.read()
        
        for armor_name, armor_hex in armor_item_patterns.items():
            armor_bytes = bytes.fromhex(armor_hex)
            if armor_bytes in data_chunk:
                found_armor.append(armor_name)

    return found_armor




# weappons could be used for armor
def replace_all_occurrences(file_path, old_hex, new_hex):
    old_bytes = bytes.fromhex(old_hex)
    new_bytes = bytes.fromhex(new_hex)
    with open(file_path, 'r+b') as file:
        data_chunk = file.read()
        modified_chunk = data_chunk.replace(old_bytes, new_bytes)
        file.seek(0)
        file.write(modified_chunk)

###storage 
def update_item_quantity_in_file(file_path, item_offset, new_quantity_var):
    try:
        # Retrieve the new quantity value from the user input
        new_quantity = int(new_quantity_var.get())

        # Convert the quantity to bytes (2 bytes, little-endian)
        quantity_bytes = new_quantity.to_bytes(2, 'little')

        # Update the file with the new quantity value
        with open(file_path, 'r+b') as file:
            # Adjust the item_offset to point to the quantity bytes, which are located right after the item's hex
            quantity_offset = item_offset + len(bytes.fromhex(item_hex_patterns["Lift Chamber Key"]))
            file.seek(quantity_offset)
            file.write(quantity_bytes)

        # Inform the user of success and refresh the list
        messagebox.showinfo("Success", f"Quantity updated to {new_quantity}.")
        refresh_storage_quantity_list(file_path)  # Refresh the list after updating

    except ValueError:
        # Handle invalid input
        messagebox.showerror("Invalid Input", "Please enter a valid quantity.")



def refresh_storage_quantity_list(file_path):
    storage_offset = find_hex_offset(file_path, hex_pattern1_Fixed) + storage_box_distance
    updated_items = find_storage_items_with_quantity(file_path, storage_offset, drawer_range)

    # Clear the previous list and display the updated items
    for widget in storage_list_frame.winfo_children():
        widget.destroy()

    if updated_items:
        for item_name, quantity, item_offset in updated_items:
            item_frame = tk.Frame(storage_list_frame)
            item_frame.pack(fill="x", padx=10, pady=5)

            item_label = tk.Label(item_frame, text=f"{item_name} (Quantity: {quantity})", anchor="w")
            item_label.pack(side="left", fill="x", padx=5)

            new_quantity_var = tk.StringVar()
            new_quantity_entry = tk.Entry(item_frame, textvariable=new_quantity_var, width=10)
            new_quantity_entry.pack(side="left", padx=5)

            update_button = tk.Button(item_frame, text="Update Quantity", command=lambda item_offset=item_offset, new_quantity_var=new_quantity_var: update_item_quantity_in_file(file_path, item_offset, new_quantity_var))
            update_button.pack(side="right", padx=5)
    else:
        messagebox.showinfo("Info", "No items found.")

def find_storage_items_with_quantity(file_path, storage_offset, storage_range):
    global found_storage_items_with_quantity
    found_storage_items_with_quantity = []
    with open(file_path, 'rb') as file:
        file.seek(storage_offset)
        data_chunk = file.read(storage_range)
        for item_name, item_hex in {**item_hex_patterns, **inventory_item_hex_patterns}.items():
            item_bytes = bytes.fromhex(item_hex)
            idx = 0
            while (idx := data_chunk.find(item_bytes, idx)) != -1:
                quantity_offset = idx + len(item_bytes)
                quantity_bytes = data_chunk[quantity_offset:quantity_offset + 2]
                quantity = int.from_bytes(quantity_bytes, 'little')
                found_storage_items_with_quantity.append((item_name, quantity, storage_offset + idx))
                idx += len(item_bytes) + 2
    return found_storage_items_with_quantity


def choose_replacement(item):

    window2 = tk.Toplevel(window)
    window2.title(f"Choose replacement for {item}")
    window2.geometry("400x300")  # Set window size to make it fit the screen better

    search_bar_frame = tk.Frame(window2)
    search_bar_frame.pack(pady=5)
    tk.Label(window2, text="Choose replacement item:").pack(pady=5)
    scrollable_frame = tk.Frame(window2)
    scrollable_frame.pack(padx=10, pady=5, fill="both", expand=True)
    tk.Label(search_bar_frame, text="Search:").pack(side="left", padx=5)
    search_entry = tk.Entry(search_bar_frame, textvariable=search_var)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", lambda event: filter_replacement_list())

    canvas = tk.Canvas(window2)
    scrollbar = Scrollbar(window2, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    filter_replacement_list_frame = scrollable_frame
    def filter_replacement_list():
            for widget in filter_replacement_list_frame.winfo_children():
                widget.destroy()

            search_term = search_var.get().lower()
            filtered_items = {k: v for k, v in replacement_items.items() if search_term in k.lower()}

            col = 0
            row = 0
            for name, replacement_hex in filtered_items.items():
                def on_replace_click(name=name, replacement_hex=replacement_hex):
                    quantity = simpledialog.askinteger("Input", f"Enter new quantity for {name}:")
                    if quantity is not None:
                        replace_item(file_path_var.get(), item, replacement_hex, new_quantity=quantity)
                    
                    
                replacement_button = tk.Button(filter_replacement_list_frame, text=name, command=on_replace_click)
                replacement_button.grid(row=row, column=col, padx=5, pady=5)
                
                col += 1
                if col > 3:
                    col = 0
                    row += 1
# for rings 


## for armor
def choose_replacement_armor(item):

    window2 = tk.Toplevel(window)
    window2.title(f"Choose replacement for {item}")
    window2.geometry("400x300")  # Set window size to make it fit the screen better

    search_bar_frame = tk.Frame(window2)
    search_bar_frame.pack(pady=5)
    tk.Label(window2, text="Choose replacement item:").pack(pady=5)
    scrollable_frame = tk.Frame(window2)
    scrollable_frame.pack(padx=10, pady=5, fill="both", expand=True)
    tk.Label(search_bar_frame, text="Search:").pack(side="left", padx=5)
    search_entry = tk.Entry(search_bar_frame, textvariable=armor_search_var)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", lambda event: filter_armor_replacement_list())

    canvas = tk.Canvas(window2)
    scrollbar = Scrollbar(window2, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    filter_armor_replacement_list_frame = scrollable_frame
    def filter_armor_replacement_list():
            for widget in filter_armor_replacement_list_frame.winfo_children():
                widget.destroy()

            search_term = armor_search_var.get().lower()
            filtered_items = {k: v for k, v in armor_replacement_items.items() if search_term in k.lower()}

            col = 0
            row = 0
            for name, replacement_hex in filtered_items.items():
                def on_replace_click(name=name, replacement_hex=replacement_hex):
                    quantity = simpledialog.askinteger("Input", f"Enter new quantity for {name}:")
                    if quantity is not None:
                        replace_item(file_path_var.get(), item, replacement_hex, new_quantity=quantity)

                replacement_button = tk.Button(filter_armor_replacement_list_frame, text=name, command=on_replace_click)
                replacement_button.grid(row=row, column=col, padx=5, pady=5)
                
                col += 1
                if col > 3:
                    col = 0
                    row += 1

def find_key_items(file_path, key_offset):
    global found_items
    found_items = []
    with open(file_path, 'rb') as file:
        file.seek(key_offset)
        data_chunk = file.read(goods_magic_range)
        for item_name, item_hex in item_hex_patterns.items():
            item_bytes = bytes.fromhex(item_hex)
            if item_bytes in data_chunk:
                item_offset = data_chunk.index(item_bytes)
                quantity_offset = key_offset + item_offset + len(item_bytes)
                quantity = find_value_at_offset(file_path, quantity_offset, byte_size=1)
                found_items.append((item_name, quantity))
    
    return found_items

#for rings 

# Goods items
def replace_item(file_path, item_name, replacement_hex, new_quantity=None):
    if new_quantity is None or not isinstance(new_quantity, int):
        messagebox.showerror("Input Error", "Please enter a valid quantity.")
        return

    replacement_bytes = bytes.fromhex(replacement_hex)
    original_bytes = bytes.fromhex(item_hex_patterns[item_name])
    key_offset = find_hex_offset(file_path, hex_pattern1_Fixed) + goods_magic_offset

    with open(file_path, 'r+b') as file:
        file.seek(key_offset)
        data_chunk = file.read(goods_magic_range)

        # Search for the full pattern `original_bytes` in the file
        pattern = original_bytes[:3] + b'\xB0' + original_bytes
        pattern_offset = data_chunk.find(pattern)

        if pattern_offset != -1:
            # Position the file to replace the four bytes after `A0`
            item_id_offset = key_offset + pattern_offset + 4  # Four bytes after `A0`
            file.seek(item_id_offset)
            file.write(replacement_bytes)  # Replace with new ID bytes

            # Replace the three bytes before `A0`
            pre_b0_offset = key_offset + pattern_offset  # Three bytes before `A0`
            file.seek(pre_b0_offset)
            file.write(replacement_bytes[:3])  # Replace the first three bytes

            # Update quantity if specified
            quantity_offset = item_id_offset + len(replacement_bytes)
            write_value_at_offset(file_path, quantity_offset, new_quantity, byte_size=1)

            # Update the displayed rings list
            for i, (found_item_name, _) in enumerate(found_items):
                if found_item_name == item_name:
                    found_items[i] = (item_name, new_quantity)
                    break

            # Refresh the ring list after replacement
            refresh_item_list(file_path)
            messagebox.showinfo("Success", f"{item_name} has been replaced.")
            if item_name not in item_hex_patterns:
                messagebox.showerror("Item Not Found", f"Item '{item_name}' not found in item patterns.")
                return

        else:
            messagebox.showerror("Not Found", f"Failed to find {item_name} to replace.")
    refresh_ring_list(file_path)


    
#for ring   


def refresh_item_list(file_path):
    key_offset = find_hex_offset(file_path, hex_pattern1_Fixed) + goods_magic_offset
    updated_items = find_key_items(file_path, key_offset)

    # Clear the previous list and display the updated items
    for widget in items_list_frame.winfo_children():
        widget.destroy()

    if updated_items:
        # Create a canvas and scrollbar to contain the items
        items_list_canvas = tk.Canvas(items_list_frame)
        items_list_scrollbar = Scrollbar(items_list_frame, orient="vertical", command=items_list_canvas.yview)
        items_list_frame_inner = tk.Frame(items_list_canvas)

        items_list_frame_inner.bind(
            "<Configure>",
            lambda e: items_list_canvas.configure(
                scrollregion=items_list_canvas.bbox("all")
            )
        )

        items_list_canvas.create_window((0, 0), window=items_list_frame_inner, anchor="nw")
        items_list_canvas.configure(yscrollcommand=items_list_scrollbar.set)

        items_list_canvas.pack(side="left", fill="both", expand=True)
        items_list_scrollbar.pack(side="right", fill="y")

        # Now add the items to the inner frame
        for item_name, quantity in updated_items:
            item_frame = tk.Frame(items_list_frame_inner)
            item_frame.pack(fill="x", padx=10, pady=5)

            item_label = tk.Label(item_frame, text=f"{item_name} (Quantity: {quantity})", anchor="w")
            item_label.pack(side="left", fill="x", padx=5)

            replace_button = tk.Button(item_frame, text="Replace", command=lambda item=item_name: choose_replacement(item))
            replace_button.pack(side="right", padx=5)
    else:
        messagebox.showinfo("Info", "No items found.")

# refresh rings

def refresh_weapon_list(file_path):
    updated_weapons = find_weapon_items(file_path)
    
    # Clear the previous list and display the updated items
    for widget in weapons_list_frame.winfo_children():
        widget.destroy()

    if updated_weapons:
        canvas = tk.Canvas(weapons_list_frame)
        scrollbar = Scrollbar(weapons_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for weapon_name in updated_weapons:
            weapon_frame = tk.Frame(scrollable_frame)
            weapon_frame.pack(fill="x", padx=10, pady=5)
            
            weapon_label = tk.Label(weapon_frame, text=f"{weapon_name}", anchor="w")
            weapon_label.pack(side="left", fill="x", padx=5)
            
            replace_button = tk.Button(weapon_frame, text="Replace", command=lambda weapon=weapon_name: replace_weapon(weapon))
            replace_button.pack(side="right", padx=5)
    else:
        messagebox.showinfo("Info", "No weapons found.")

# for armor
def refresh_armor_list(file_path):
    updated_armor = find_armor_items(file_path)
    
    # Clear the previous list and display the updated items
    for widget in armor_list_frame.winfo_children():
        widget.destroy()

    if updated_armor:
        canvas = tk.Canvas(armor_list_frame)
        scrollbar = Scrollbar(armor_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for armor_name in updated_armor:
            armor_frame = tk.Frame(scrollable_frame)
            armor_frame.pack(fill="x", padx=10, pady=5)
            
            armor_label = tk.Label(armor_frame, text=f"{armor_name}", anchor="w")
            armor_label.pack(side="left", fill="x", padx=5)
            
            replace_button = tk.Button(armor_frame, text="Replace", command=lambda armor=armor_name: replace_armor(armor))
            replace_button.pack(side="right", padx=5)
    else:
        messagebox.showinfo("Info", "No armor found.")

def replace_weapon(weapon_name):

    window2 = tk.Toplevel(window)
    window2.title(f"Replace {weapon_name}")

    tk.Label(window2, text="Choose replacement weapon:").pack(pady=5)
    search_bar_frame = tk.Frame(window2)
    search_bar_frame.pack(pady=5)
    tk.Label(search_bar_frame, text="Search:").pack(side="left", padx=5)
    search_entry = tk.Entry(search_bar_frame, textvariable=weapon_search_var)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", lambda event: filter_replacement_list())

    canvas = tk.Canvas(window2)
    scrollbar = Scrollbar(window2, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    filter_replacement_list_frame = scrollable_frame

    def filter_replacement_list():
        for widget in filter_replacement_list_frame.winfo_children():
            widget.destroy()

        search_term = weapon_search_var.get().lower()
        filtered_items = {k: v for k, v in weapon_item_patterns.items() if search_term in k.lower()}

        col = 0
        row = 0
        for name, replacement_hex in filtered_items.items():
            def on_replace_click(name=name, replacement_hex=replacement_hex):
                replace_all_occurrences(file_path_var.get(), weapon_item_patterns[weapon_name], replacement_hex)
                refresh_weapon_list(file_path_var.get())
                window2.destroy()

            replacement_button = tk.Button(filter_replacement_list_frame, text=name, command=on_replace_click)
            replacement_button.grid(row=row, column=col, padx=5, pady=5)
            
            col += 1
            if col > 3:
                col = 0
                row += 1

#for armor
def replace_armor(armor_name):

    window2 = tk.Toplevel(window)
    window2.title(f"Replace {armor_name}")

    tk.Label(window2, text="Choose replacement armor:").pack(pady=5)
    search_bar_frame = tk.Frame(window2)
    search_bar_frame.pack(pady=5)
    tk.Label(search_bar_frame, text="Search:").pack(side="left", padx=5)
    search_entry = tk.Entry(search_bar_frame, textvariable=armor_search_var)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", lambda event: filter_armor_replacement_list())

    canvas = tk.Canvas(window2)
    scrollbar = Scrollbar(window2, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    filter_armor_replacement_list_frame = scrollable_frame

    def filter_armor_replacement_list():
        for widget in filter_armor_replacement_list_frame.winfo_children():
            widget.destroy()

        search_term_armor = armor_search_var.get().lower()
        filtered_items_armor = {k: v for k, v in armor_item_patterns.items() if search_term_armor in k.lower()}

        col = 0
        row = 0
        for name, replacement_armor_hex in filtered_items_armor.items():
            def on_replace_click(name=name, replacement_armor_hex=replacement_armor_hex):
                replace_all_occurrences(file_path_var.get(), armor_item_patterns[armor_name], replacement_armor_hex)
                refresh_armor_list(file_path_var.get())
                window2.destroy()

            replacement_button = tk.Button(filter_armor_replacement_list_frame, text=name, command=on_replace_click)
            replacement_button.grid(row=row, column=col, padx=5, pady=5)
            
            col += 1
            if col > 3:
                col = 0
                row += 1

# UI Layout
file_open_frame = tk.Frame(window)
file_open_frame.pack(fill="x", padx=10, pady=5)

tk.Button(file_open_frame, text="Open Save File", command=open_file).pack(side="left", padx=5)
file_name_label = tk.Label(file_open_frame, text="No file selected", anchor="w")
file_name_label.pack(side="left", padx=10, fill="x")

notebook = ttk.Notebook(window)
inventory_tab = ttk.Frame(notebook)
sub_notebook = ttk.Notebook(inventory_tab)

def on_tab_changed(event):
    selected_tab = event.widget.tab(event.widget.index("current"))["text"]
    if selected_tab == "Rings":
        refresh_ring_list(file_path_var.get())

# Bind the NotebookTabChanged event to trigger the refresh when switching tabs
notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
# Character Tab
name_tab = ttk.Frame(notebook)
tk.Label(name_tab, text="Current Character Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
tk.Label(name_tab, textvariable=current_name_var).grid(row=0, column=1, padx=10, pady=10)
tk.Label(name_tab, text="New Character Name:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
tk.Entry(name_tab, textvariable=new_name_var, width=20).grid(row=1, column=1, padx=10, pady=10)
tk.Button(name_tab, text="Update Name", command=update_character_name).grid(row=2, column=0, columnspan=2, pady=20)

# Souls Tab
souls_tab = ttk.Frame(notebook)
tk.Label(souls_tab, text="Current Souls:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
tk.Label(souls_tab, textvariable=current_souls_var).grid(row=0, column=1, padx=10, pady=10)
tk.Label(souls_tab, text="New Souls Value (MAX 999999999):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
tk.Entry(souls_tab, textvariable=new_souls_var, width=20).grid(row=1, column=1, padx=10, pady=10)
tk.Button(souls_tab, text="Update Souls", command=update_souls_value).grid(row=2, column=0, columnspan=2, pady=20)
#rings
rings_tab = ttk.Frame(sub_notebook)
ring_list_frame = tk.Frame(rings_tab)
ring_list_frame.pack(fill="x", padx=10, pady=5)
refresh_ring_button = tk.Button(rings_tab, text="Refresh Ring List", command=lambda: refresh_ring_list(file_path_var.get()))
refresh_ring_button.pack(pady=10)


#hp Tap
tk.Label(name_tab, text="Current HP:").grid(row=5, column=0, padx=10, pady=10, sticky="e")
tk.Label(name_tab, textvariable=current_hp_var).grid(row=5, column=1, padx=10, pady=10)
tk.Label(name_tab, text="New HP:").grid(row=7, column=0, padx=10, pady=10, sticky="e")
tk.Entry(name_tab, textvariable=new_hp_var, width=20).grid(row=7, column=1, padx=10, pady=10)
tk.Button(name_tab, text="Update HP", command=update_hp_value).grid(row=8, column=0, columnspan=2, pady=20)

# Stats Tab
stats_tab = ttk.Frame(notebook)
for idx, (stat, stat_offset) in enumerate(stats_offsets_for_stats_tap.items()):
    tk.Label(stats_tab, text=f"Current {stat}:").grid(row=idx, column=0, padx=10, pady=5, sticky="e")
    tk.Label(stats_tab, textvariable=current_stats_vars[stat]).grid(row=idx, column=1, padx=10, pady=5)
    tk.Entry(stats_tab, textvariable=new_stats_vars[stat], width=10).grid(row=idx, column=2, padx=10, pady=5)
    tk.Button(stats_tab, text=f"Update {stat}", command=lambda s=stat: update_stat(s)).grid(row=idx, column=3, padx=10, pady=5)

# Storage Box Tab
storage_box_tab = ttk.Frame(window)

storage_list_frame = tk.Frame(storage_box_tab)
storage_list_frame.pack(fill="x", padx=10, pady=5)

refresh_storage_button = tk.Button(storage_box_tab, text="Refresh Storage Box with Quantity", command=lambda: refresh_storage_quantity_list(file_path_var.get()))
refresh_storage_button.pack(pady=10)
# Items Tab
items_tab = ttk.Frame(sub_notebook)
items_list_frame = tk.Frame(items_tab)
items_list_frame.pack(fill="x", padx=10, pady=5)
refresh_button = tk.Button(items_tab, text="Refresh Items List", command=lambda: refresh_item_list(file_path_var.get()))
refresh_button.pack(pady=10)



# Weapons Tab
weapons_tab = ttk.Frame(sub_notebook)
weapons_list_frame = tk.Frame(weapons_tab)
weapons_list_frame.pack(fill="x", padx=10, pady=5)
refresh_weapons_button = tk.Button(weapons_tab, text="Refresh Weapons List", command=lambda: refresh_weapon_list(file_path_var.get()))
refresh_weapons_button.pack(pady=10)

# armmor tap
armor_tab = ttk.Frame(sub_notebook)
armor_list_frame = tk.Frame(armor_tab)
armor_list_frame.pack(fill="x", padx=10, pady=5)
refresh_armor_button = tk.Button(armor_tab, text="Refresh armor List", command=lambda: refresh_armor_list(file_path_var.get()))
refresh_armor_button.pack(pady=10)


# Define specific refresh functions for each tab
def refresh_souls_tab():
    offset1 = find_hex_offset(file_path_var.get(), hex_pattern1_Fixed)
    if offset1 is not None:
        souls_offset = calculate_offset2(offset1, souls_distance)
        current_souls = find_value_at_offset(file_path_var.get(), souls_offset)
        current_souls_var.set(current_souls if current_souls is not None else "N/A")

def refresh_character_tab():
    offset1 = find_hex_offset(file_path_var.get(), hex_pattern1_Fixed)
    if offset1 is not None:
        for distance in possible_name_distances_for_name_tap:
            name_offset = calculate_offset2(offset1, distance)
            current_name = find_character_name(file_path_var.get(), name_offset)
            if current_name and current_name != "N/A":
                current_name_var.set(current_name)
                break
        else:
            current_name_var.set("N/A")

        hp_offset = calculate_offset2(offset1, hp_distance)
        current_hp = find_value_at_offset(file_path_var.get(), hp_offset)
        current_hp_var.set(current_hp if current_hp is not None else "N/A")

def refresh_stats_tab():
    offset1 = find_hex_offset(file_path_var.get(), hex_pattern1_Fixed)
    if offset1 is not None:
        for stat, distance in stats_offsets_for_stats_tap.items():
            stat_offset = calculate_offset2(offset1, distance)
            current_stat_value = find_value_at_offset(file_path_var.get(), stat_offset)
            current_stats_vars[stat].set(current_stat_value if current_stat_value is not None else "N/A")
def refresh_storage_box_tab():
    storage_offset = find_hex_offset(file_path_var.get(), hex_pattern1_Fixed) + storage_box_distance
    refresh_storage_quantity_list(file_path_var.get())
    
def refresh_on_click():
    refresh_souls_tab()
    refresh_character_tab()

def refresh_souls_tab():
    offset1 = find_hex_offset(file_path_var.get(), hex_pattern1_Fixed)
    if offset1 is not None:
        souls_offset = calculate_offset2(offset1, souls_distance)
        current_souls = find_value_at_offset(file_path_var.get(), souls_offset)
        current_souls_var.set(current_souls if current_souls is not None else "N/A")

def refresh_character_tab():
    offset1 = find_hex_offset(file_path_var.get(), hex_pattern1_Fixed)
    if offset1 is not None:
        for distance in possible_name_distances_for_name_tap:
            name_offset = calculate_offset2(offset1, distance)
            current_name = find_character_name(file_path_var.get(), name_offset)
            if current_name and current_name != "N/A":
                current_name_var.set(current_name)
                break
        else:
            current_name_var.set("N/A")

        hp_offset = calculate_offset2(offset1, hp_distance)
        current_hp = find_value_at_offset(file_path_var.get(), hp_offset)
        current_hp_var.set(current_hp if current_hp is not None else "N/A")

def update_souls_value_and_refresh():
    update_souls_value()
    refresh_on_click()

def update_character_name_and_refresh():
    update_character_name()
    refresh_on_click()

def update_hp_value_and_refresh():
    update_hp_value()
    refresh_on_click()


def refresh_storage_box_tab():
    storage_offset = find_hex_offset(file_path_var.get(), hex_pattern1_Fixed) + storage_box_distance
    refresh_storage_quantity_list(file_path_var.get())

tk.Button(souls_tab, text="Update Souls", command=update_souls_value_and_refresh).grid(row=2, column=0, columnspan=2, pady=20)

# Character Tab
tk.Button(name_tab, text="Update Name", command=update_character_name_and_refresh).grid(row=2, column=0, columnspan=2, pady=20)
tk.Button(name_tab, text="Update HP", command=update_hp_value_and_refresh).grid(row=8, column=0, columnspan=2, pady=20)
storage_box_tab = ttk.Frame(notebook)

sub_notebook.add(items_tab, text="Items")
sub_notebook.add(rings_tab, text="Rings")
sub_notebook.add(weapons_tab, text="Weapons")
sub_notebook.add(armor_tab, text="Armor")
sub_notebook.pack(expand=1, fill="both")

# Add Inventory tab with sub-tabs to the main notebook
notebook.add(inventory_tab, text="Inventory")
notebook.add(name_tab, text="Character (OFFLINE ONLY)")
notebook.add(souls_tab, text="Souls")
notebook.add(stats_tab, text="Stats (OFFLINE ONLY)")

notebook.add(storage_box_tab, text="Storage Box")



notebook.pack(expand=1, fill="both")
canvas = tk.Canvas(storage_box_tab)
scrollbar = ttk.Scrollbar(storage_box_tab, orient="vertical", command=canvas.yview)
storage_list_frame = tk.Frame(canvas)
canvas.configure(yscrollcommand=scrollbar.set)

# Pack the canvas and scrollbar in the storage box tab
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
def update_storage_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

# Bind the configuration event of storage_list_frame to update the scroll region
storage_list_frame.bind("<Configure>", update_storage_scroll_region)
inventory_text = """
DO NOT REPLACE ANY ITEM THAT YOU ARE CURRENTLY HAVE EQUIPED. (IF YOU DON'T HAVE THE DLC'S, DON NOT REPLACE AN ITEM FOR A DLC ITEM)
"""


inventory_label = tk.Label(weapons_tab, text=inventory_text, wraplength=400, justify="left", anchor="nw")
inventory_label.pack(padx=10, pady=10, fill="x") 

storage_text = """
600 IS THE MAXIMIM.
"""


storage_label = tk.Label(storage_box_tab, text=storage_text, wraplength=400, justify="left", anchor="nw")
storage_label.pack(padx=10, pady=10, fill="x") 

canvas_frame = canvas.create_window((0, 0), window=storage_list_frame, anchor="nw")

my_label = tk.Label(window, text="Made by Alfazari911 --   Thanks to Nox and BawsDeep for help", anchor="e", padx=10)
my_label.pack(side="top", anchor="ne", padx=10, pady=5)

we_label = tk.Label(window, text="USE AT YOUR OWN RISK. EDITING STATS AND HP COULD GET YOU BANNED", anchor="w", padx=10)
we_label.pack(side="bottom", anchor="nw", padx=10, pady=5)

# Run 
window.mainloop()
