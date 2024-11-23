import json
import glob
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, Scrollbar
import gc
from functools import wraps
from time import time

#just a flag
# Constants
hex_pattern1_Fixed = '00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00'
possible_name_distances_for_name_tap = [-199]
souls_distance = -219
hp_distance= -303
fp_distance= -291
stamina_distance= -275
goods_magic_offset = 0
goods_magic_range = 30000
storage_box_distance = 35900   
drawer_range = 4000
gesture_offsets= -3800
hex_pattern2_Fixed= 'FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF'


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
    "Estus Flask Max (20 MAX)": -31,
    "Ashen Estus Flask Max (20 MAX)": -30,
}

#for bosses
bosses_offsets_for_bosses_tap = {
    "Iudex Gundyr": 23254,
    "Vordt of the Boreal Valley": 4054,
    "Curse-Rotted Greatwood": 19337,
    "Crystal Sage": 11736,
    "Abyss Watchers": 11734,
    "High Lord Wolnir": 15574,
    "Oceiros, the Consumed King": 4051,
    "Champion Gundyr": 23251,
    "Dancer of the Boreal Valley": 4059,
    "Deacons of the Deep": 6614,## unsure need testing
    "Old Demon King": 21174,## unsure need testing
    "Pontiff Sulyvahn": 3999 ,## unsure need testing
    "Aldrich, Devourer of Gods": 3997,## unsure need testing
    "Dragonslayer Armour": 5334,## unsure need testing
    "Yhorm the Giant": 21974,## unsure need testing
    "Nameless King": 15510,
    "Twin Princes": 14291,
    "Soul of Cinder": 24534,
    "Champion's Gravetender (DLC)": 25815,
    "Father Ariandel and Sister Friede (DLC)": 25814,
    "Halflight, Spear of the Church (DLC)": 30934,
    "Darkeater Midir (DLC)": 30936,
    "Slave Knight Gael (DLC)": 32214,
    "Demon Prince (DLC)": 29654,


}

##For bonfire
bonfire_offsets_for_bonfire_tap = {
    "Activate Lord of Cinders in Firelink Shrine": 1288,
    "Cemetary of Ash": 23154,
    "High Wall of Lothric": 3953,
    "Undead Settlement": 19314, #need testing
    "Archdragon Peak": 9074,
    "Kiln of the First Flame": 24434,
    "Catacombs of Carthus": 20594,
    "Irithyll of the Boreal Valley": 19313,
    "The Dreg Heap": 29554,
    "Irithyll Dungeon": 21874,
    "Road of Sacrifices": 11634,
    "Cathedral of the Deep": 6514,
    "Lothric Castle": 5234,
    "Painted World of Ariandel (DLC)": 25714,
    "The Ringed City (DLC)": 30834,
}
# Set the working directory
working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)

# load and copy JSON data from files in the working directory
def load_and_copy_json(file_name):
    file_path = os.path.join(working_directory, "Resources/Json", file_name)
    with open(file_path, "r") as file:
        return json.load(file).copy()

# Load and copy data from JSON files within the specified working directory
inventory_item_hex_patterns = load_and_copy_json("itemshex.json")
inventory_replacement_items = inventory_item_hex_patterns.copy()
#for bosses
bosses_data = load_and_copy_json("Bosses.json")

##bonfire
bonfire_data = load_and_copy_json("bonfire.json")

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


# Main window
window = tk.Tk()
window.title("Dark Souls 3 Save Editor")

# Load and configure the Azure theme
try:
    # Set Theme Path
    azure_path = os.path.join(os.path.dirname(__file__), "Resources/Azure", "azure.tcl")
    window.tk.call("source", azure_path)
    window.tk.call("set_theme", "dark")  # or "light" for light theme
except tk.TclError as e:
    messagebox.showwarning("Theme Warning", f"Azure theme could not be loaded: {str(e)}")

# Function to update button styles based on the current theme
def update_button_styles():
    if current_theme.get() == "dark":
        # Set dark theme styles
        theme_button.config(style="TButton")  # Use default Azure button style
    else:
        # Set light theme styles
        theme_button.config(style="TButton")  # Use default Azure button style

# Add theme toggle button
current_theme = tk.StringVar(value="dark")

def toggle_theme():
    if current_theme.get() == "dark":
        window.tk.call("set_theme", "light")
        current_theme.set("light")
    else:
        window.tk.call("set_theme", "dark")
        current_theme.set("dark")
    
    # Update button styles after toggling the theme
    update_button_styles()

# Globll variables
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
current_fp_var= tk.StringVar(value="N/A")
new_hp_var= tk.StringVar()
new_fp_var= tk.StringVar()
current_stamina_var= tk.StringVar(value="N/A")
current_souls_var = tk.StringVar(value="N/A")
new_stamina_var= tk.StringVar()
new_souls_var = tk.StringVar()
found_storage_items_with_quantity = []
found_items = []
found_armor= []
found_ring= []
file_path_var = tk.StringVar()

# Variables to hold current and new values for each stat
current_stats_vars = {stat: tk.StringVar(value="N/A") for stat in stats_offsets_for_stats_tap}
new_stats_vars = {stat: tk.StringVar() for stat in stats_offsets_for_stats_tap}

# Utility Functions
def find_hex_offset(file_path, hex_pattern):
    try:
        pattern_bytes = bytes.fromhex(hex_pattern)
        chunk_size = 4096
        with open(file_path, 'rb') as file:
            offset = 0
            while chunk := file.read(chunk_size):
                if pattern_bytes in chunk:
                    byte_offset = chunk.index(pattern_bytes)
                    return offset + byte_offset
                offset += len(chunk)
                del chunk
        gc.collect()
        return None
    except (IOError, ValueError) as e:
        messagebox.showerror("Error", f"Failed to read file: {str(e)}")
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
   
    # Convert the new name into bytes
    name_bytes = []
    for char in new_name:
        name_bytes.append(ord(char))
        name_bytes.append(0)  # Add null byte for UTF-16 encoding
    
    # Pad the name with null bytes to match the fixed byte size
    name_bytes = name_bytes[:byte_size]  # Truncate if name is too long
    name_bytes += [0] * (byte_size - len(name_bytes))  # Pad if name is too short

    # Write the name to the file
    with open(file_path, 'r+b') as file:
        file.seek(offset)
        file.write(bytes(name_bytes))

#
def open_single_file():
    file_path = filedialog.askopenfilename(filetypes=[("Save Files", "userdata*")])
    if not file_path:
        return

    # Set the file path variable to the selected file
    file_path_var.set(file_path)

    # Try to find the character name and display it
    offset1 = find_hex_offset(file_path, hex_pattern1_Fixed)
    if offset1 is not None:
        for distance in possible_name_distances_for_name_tap:
            name_offset = calculate_offset2(offset1, distance)
            character_name = find_character_name(file_path, name_offset)
            if character_name and character_name != "N/A":
                # Display the single file's character name
                display_character_names([(file_path, character_name)])
                return

    messagebox.showerror("Error", "Unable to find a valid character name in the file!")


# Function to open the file
def open_folder():
    folder_path = filedialog.askdirectory()
    if not folder_path:
        return

    userdata_files = sorted(glob.glob(os.path.join(folder_path, "userdata*")))
    character_names = []

    for file_path in userdata_files:
        offset1 = find_hex_offset(file_path, hex_pattern1_Fixed)
        if offset1 is not None:
            for distance in possible_name_distances_for_name_tap:
                name_offset = calculate_offset2(offset1, distance)
                character_name = find_character_name(file_path, name_offset)
                if character_name and character_name != "N/A":
                    character_names.append((file_path, character_name))
                    break

    display_character_names(character_names)

def display_character_names(character_names):
    # Clear any existing character list
    for widget in character_list_frame.winfo_children():
        widget.destroy()

    for file_path, name in character_names:
        def on_character_click(selected_file=file_path):
            file_path_var.set(selected_file)
            load_file_data(selected_file)

    character_button = ttk.Button(character_list_frame, text=name, command=on_character_click, width=15)  # Set width to 15
    character_button.pack(fill="x", padx=5, pady=2)  # Use pack for layout


def load_file_data(file_path):
    offset1 = find_hex_offset(file_path, hex_pattern1_Fixed)
    if offset1 is not None:
        # Load character name
        refresh_storage_quantity_list(file_path)
        for distance in possible_name_distances_for_name_tap:
            name_offset = calculate_offset2(offset1, distance)
            current_name = find_character_name(file_path, name_offset)
            if current_name and current_name != "N/A":
                current_name_var.set(current_name)
                break
        else:
            current_name_var.set("N/A")

        # Load other data (e.g., stats, souls, etc.)
        # Souls
        souls_offset = calculate_offset2(offset1, souls_distance)
        current_souls = find_value_at_offset(file_path, souls_offset)
        current_souls_var.set(current_souls if current_souls is not None else "N/A")

        # Stats
        for stat, distance in stats_offsets_for_stats_tap.items():
            stat_offset = calculate_offset2(offset1, distance)
            current_stat_value = find_value_at_offset(file_path, stat_offset, byte_size=1)
            current_stats_vars[stat].set(current_stat_value if current_stat_value is not None else "N/A")

        # HP
        hp_offset = calculate_offset2(offset1, hp_distance)
        current_hp = find_value_at_offset(file_path, hp_offset)
        current_hp_var.set(current_hp if current_hp is not None else "N/A")

        #FP
        fp_offset = calculate_offset2(offset1, fp_distance)
        current_fp = find_value_at_offset(file_path, fp_offset)
        current_fp_var.set(current_fp if current_fp is not None else "N/A")
        #STAMINA
        stamina_offset = calculate_offset2(offset1, stamina_distance)
        current_stamina = find_value_at_offset(file_path, stamina_offset)
        current_stamina_var.set(current_stamina if current_stamina is not None else "N/A")



        # Refresh UI elements (e.g., inventory, stats, etc.)
    
        refresh_item_list(file_path)
        refresh_weapon_list(file_path)
        refresh_armor_list(file_path)
        refresh_ring_list(file_path)
        refresh_boss_tab()
        refresh_bonfire_tab()

       

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
        messagebox.showinfo("Success", f"Souls value updated to {new_souls_value}")
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
        messagebox.showinfo("Success", f"Hp value updated to {new_hp_value}")
    else:
        messagebox.showerror("Pattern Not Found", "Pattern not found in the file.")
#FP update
def update_fp_value():
    file_path = file_path_var.get()
    if not file_path or not new_fp_var.get():
        messagebox.showerror("Input Error", "Please fill in the file path and new FP value!")
        return
    
    try:
        new_fp_value = int(new_fp_var.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid decimal number for FP.")
        return

    offset1 = find_hex_offset(file_path, hex_pattern1_Fixed)
    if offset1 is not None:
        fp_offset = calculate_offset2(offset1, fp_distance)
        write_value_at_offset(file_path, fp_offset, new_fp_value)
        # Refresh the FP value to reflect the updated value
        current_fp = find_value_at_offset(file_path, fp_offset)
        current_fp_var.set(current_fp if current_fp is not None else "N/A")
        messagebox.showinfo("Success", f"FP value updated to {new_fp_value}")
    else:
        messagebox.showerror("Pattern Not Found", "Pattern not found in the file.")

#STAMINA UPDATE
def update_stamina_value():
    file_path = file_path_var.get()
    if not file_path or not new_stamina_var.get():
        messagebox.showerror("Input Error", "Please fill in the file path and new stamina value!")
        return
    
    try:
        new_stamina_value = int(new_stamina_var.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid decimal number for stamina.")
        return

    offset1 = find_hex_offset(file_path, hex_pattern1_Fixed)
    if offset1 is not None:
        stamina_offset = calculate_offset2(offset1, stamina_distance)
        write_value_at_offset(file_path, stamina_offset, new_stamina_value)
        # Refresh the stamina value to reflect the updated value
        current_stamina = find_value_at_offset(file_path, stamina_offset)
        current_stamina_var.set(current_stamina if current_stamina is not None else "N/A")
        messagebox.showinfo("Success", f"Stamina value updated to {new_stamina_value}")
    else:
        messagebox.showerror("Pattern Not Found", "Pattern not found in the file.")

#  update namw
def update_character_name():
    file_path = file_path_var.get()
    new_name = new_name_var.get()

    if not file_path or not new_name:
        messagebox.showerror("Input Error", "Please fill in the file path and new character name!")
        return

    offset1 = find_hex_offset(file_path, hex_pattern1_Fixed)
    if offset1 is not None:
        for distance in possible_name_distances_for_name_tap:
            name_offset = calculate_offset2(offset1, distance)
            current_name = find_character_name(file_path, name_offset)
            if current_name and current_name != "N/A":
                write_character_name(file_path, name_offset, new_name)
                messagebox.showinfo("Success", f"Character name updated to '{new_name}'.")
                current_name_var.set(new_name)
                return

    messagebox.showerror("Error", "Unable to find the character name offset!")


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




#Bosses
def find_last_hex_offset(file_path, hex_pattern):
    try:
        pattern_bytes = bytes.fromhex(hex_pattern)
        chunk_size = 4096
        last_offset = None
        
        with open(file_path, 'rb') as file:
            offset = 0
            while chunk := file.read(chunk_size):
                # Search for the pattern within the chunk
                byte_offset = chunk.rfind(pattern_bytes)
                
                # If the pattern is found, update the last_offset to the current location
                if byte_offset != -1:
                    last_offset = offset + byte_offset
                
                # Update the offset to the next chunk
                offset += len(chunk)
                del chunk
        
        gc.collect()
        return last_offset
    except (IOError, ValueError) as e:
        messagebox.showerror("Error", f"Failed to read file: {str(e)}")
        return None

# Function to get the current status of each boss, using the last occurrence of the hex pattern
def get_boss_status(file_path):
    global bosses_data
    bosses_status = {}
    # Use find_last_hex_offset to locate the last occurrence of the fixed pattern
    offset1 = find_last_hex_offset(file_path, hex_pattern2_Fixed)
    if offset1 is not None:
        for boss, defeat_hex in bosses_data.items():
            defeat_value = int(defeat_hex, 16)  # Convert hex string to integer for comparison
            boss_distance = bosses_offsets_for_bosses_tap.get(boss)  # Retrieve distance for boss
            
            if boss_distance is not None:
                # Calculate the offset based on fixed offset and boss distance
                boss_offset = calculate_offset2(offset1, boss_distance)
                
                # Read only 1 byte at the boss offset
                boss_value = find_value_at_offset(file_path, boss_offset, byte_size=1)
                
                # Determine if the boss is defeated or alive
                bosses_status[boss] = "Defeated" if boss_value == defeat_value else "Alive"
            else:
                print(f"Warning: Offset for boss '{boss}' not found.")
    return bosses_status




def update_boss_status(file_path, boss_name, new_status):
    global bosses_data
    offset1 = find_last_hex_offset(file_path, hex_pattern2_Fixed)
    if offset1 is not None and boss_name in bosses_data:
        # Calculate offset for the specific boss
        boss_distance = bosses_offsets_for_bosses_tap[boss_name]
        boss_offset = calculate_offset2(offset1, boss_distance)
        defeat_value = int(bosses_data[boss_name], 16)
        
        # Set the value to 1 byte: defeat value for "Defeated" or 0 for "Alive"
        value = defeat_value if new_status == "Defeated" else 0  # 0 for alive
        write_value_at_offset(file_path, boss_offset, value, byte_size=1)  # Write only 1 byte
        messagebox.showinfo("Success", f"{boss_name} status updated to {new_status}.")
        
        # Refresh display to reflect changes
        display_boss_status(file_path)
    else:
        messagebox.showerror("Error", "Failed to update boss status. Boss data or offset not found.")

def display_boss_status(file_path):
    bosses_status = get_boss_status(file_path)
    
    # Clear previous entries
    for widget in boss_list_canvas.winfo_children():
        widget.destroy()
    
    # Create a frame inside the canvas
    boss_list_frame = ttk.Frame(boss_list_canvas)
    boss_list_canvas.create_window((0, 0), window=boss_list_frame, anchor="nw")

    # Populate the frame with the boss list
    for boss, status in bosses_status.items():
        boss_frame = ttk.Frame(boss_list_frame)
        boss_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(boss_frame, text=f"{boss} - Status:", anchor="w").pack(side="left", fill="x", padx=5)
        
        # Dropdown to change status with direct update
        new_status_var = tk.StringVar(value=status)
        def on_status_change(selected_status, boss=boss):
            update_boss_status(file_path, boss, selected_status)

        status_options = tk.OptionMenu(boss_frame, new_status_var, "Alive", "Defeated", command=lambda selection, boss=boss: on_status_change(selection, boss))
        status_options.pack(side="right", padx=5)

    # Update the scroll region of the canvas
    boss_list_frame.update_idletasks()
    boss_list_canvas.config(scrollregion=boss_list_canvas.bbox("all"))

def refresh_boss_tab():
    file_path = file_path_var.get()
    if file_path:
        display_boss_status(file_path)
        
def on_world_flag_tab_selected(event):
    selected_tab = notebook.tab(notebook.select(), "text")
    if selected_tab == "World Flag":
        refresh_boss_tab()

##bonfire
def get_bonfire_status(file_path):
    global bonfire_data
    bonfire_status = {}
    offset1 = find_last_hex_offset(file_path, hex_pattern2_Fixed)  # Find the last fixed offset
    if offset1 is not None:
        for bonfire, bonfire_hex in bonfire_data.items():
            bonfire_value = int(bonfire_hex, 16)  # Convert hex string to integer
            bonfire_distance = bonfire_offsets_for_bonfire_tap.get(bonfire)  # Retrieve offset distance
            
            if bonfire_distance is not None:
                # Calculate the offset based on fixed offset and bonfire distance
                bonfire_offset = calculate_offset2(offset1, bonfire_distance)
                
                # Read the value (try 1 byte first, then 2 bytes)
                read_value = find_value_at_offset(file_path, bonfire_offset, byte_size=1)
                if read_value != bonfire_value:
                    read_value = find_value_at_offset(file_path, bonfire_offset, byte_size=2)

                # Determine bonfire status
                bonfire_status[bonfire] = "Unlocked" if read_value == bonfire_value else "Locked"
            else:
                print(f"Warning: Offset for bonfire '{bonfire}' not found.")
    return bonfire_status

def update_bonfire_status(file_path, bonfire_name, bonfire_status):
    global bonfire_data
    offset1 = find_last_hex_offset(file_path, hex_pattern2_Fixed)  # Find the last fixed offset
    if offset1 is not None and bonfire_name in bonfire_data:
        # Calculate offset for the specific bonfire
        bonfire_distance = bonfire_offsets_for_bonfire_tap[bonfire_name]
        bonfire_offset = calculate_offset2(offset1, bonfire_distance)
        unlock_value = int(bonfire_data[bonfire_name], 16)  
        # Determine the byte size based on the unlock_value
        byte_size = 1 if unlock_value <= 0xFF else 2  # Use 1 byte if unlock_value fits, otherwise 2 bytes
        
        # Determine value to write: unlock_value for "Unlocked", 0 for "Locked"
        if bonfire_status == "Unlocked":
            value = unlock_value
        else:
            value = 0  # Write 0 using the same byte size as the unlock_value
        
        # Write the value at the calculated offset
        write_value_at_offset(file_path, bonfire_offset, value, byte_size=byte_size)
        
        messagebox.showinfo("Success", f"{bonfire_name} status updated to {bonfire_status}.")
        
        # Refresh display to reflect changes
        display_bonfire_status(file_path)
    else:
        messagebox.showerror("Error", "Failed to update bonfire status. Bonfire data or offset not found.")


def display_bonfire_status(file_path):
    bonfire_status = get_bonfire_status(file_path)
    
    # Clear previous entries
    for widget in bonfire_list_canvas.winfo_children():
        widget.destroy()
    
    # Create a frame inside the canvas
    bonfire_list_frame = ttk.Frame(bonfire_list_canvas)
    bonfire_list_canvas.create_window((0, 0), window=bonfire_list_frame, anchor="nw")

    # Populate the frame with the bonfire list
    for bonfire, status in bonfire_status.items():
        bonfire_frame = ttk.Frame(bonfire_list_frame)
        bonfire_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(bonfire_frame, text=f"{bonfire} - Status:", anchor="w").pack(side="left", fill="x", padx=5)
        
        # Dropdown to change status with direct update
        new_status_var = tk.StringVar(value=status)
        def on_status_bonfire_change(selected_status, bonfire=bonfire):
            update_bonfire_status(file_path, bonfire, selected_status)

        status_options = tk.OptionMenu(bonfire_frame, new_status_var, "Locked", "Unlocked", command=lambda selection, bonfire=bonfire: on_status_bonfire_change(selection, bonfire))
        status_options.pack(side="right", padx=5)

    # Update the scroll region of the canvas
    bonfire_list_frame.update_idletasks()
    bonfire_list_canvas.config(scrollregion=bonfire_list_canvas.bbox("all"))


def refresh_bonfire_tab():
    file_path = file_path_var.get()
    if file_path:
        display_bonfire_status(file_path)
        
def on_world_flag_tab_selected(event):
    selected_tab = notebook.tab(notebook.select(), "text")
    if selected_tab == "World Flag":
        refresh_bonfire_tab()


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
        ring_list_frame_inner = ttk.Frame(ring_list_canvas)

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
            ring_frame = ttk.Frame(ring_list_frame_inner)
            ring_frame.pack(fill="x", padx=10, pady=5)

            ring_label = tk.Label(ring_frame, text=f"{ring_name} (Quantity: {quantity})", anchor="w")
            ring_label.pack(side="left", fill="x", padx=5)

            replace_button = ttk.Button(ring_frame, text="Replace", command=lambda ring=ring_name: choose_ring_replacement(ring))
            replace_button.pack(side="right", padx=5)
    else:
        messagebox.showinfo("Info", "No rings found.")

def choose_ring_replacement(ring_name):
    window2 = tk.Toplevel(window)
    window2.title(f"Choose replacement for {ring_name}")

    tk.Label(window2, text="Choose replacement ring:").pack(pady=5)
    search_bar_frame = ttk.Frame(window2)
    search_bar_frame.pack(pady=5)
    tk.Label(search_bar_frame, text="Search:").pack(side="left", padx=5)
    search_entry = ttk.Entry(search_bar_frame, textvariable=ring_search_var)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", lambda event: filter_ring_replacement_list())

    canvas = tk.Canvas(window2)
    scrollbar = Scrollbar(window2, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

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

            replacement_button = ttk.Button(filter_ring_replacement_list_frame, text=name, command=on_replace_click)
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


# Gesture Hex Definitions
gesture_old_id = bytes.fromhex("03 00 00 00 05")
gesture_new_id = bytes.fromhex(
    "03 00 00 00 05 00 01 00 07 00 02 00 09 00 03 00 0B 00 04 00 0D 00 05 00 0F 00 06 00 11 00 07 00 13 00 08 00 15 00 09 00 17 00 0A 00 19 00 0B 00 1B 00 0C 00 1D 00 0D 00 1F 00 0E 00 21 00 0F 00 23 00 10 00 25 00 11 00 27 00 12 00 29 00 13 00 2B 00 14 00 2D 00 15 00 2F 00 16 00 31 00 17 00 33 00 18 00 35 00 19 00 37 00 1A 00 39 00 1B 00 3B 00 1C 00 3D 00 1D 00 3F 00 1E 00 41 00 1F 00 43 00 20 00 45"
)

gesture_distance = -3800  # Offset from Fixed Pattern 2
gesture_search_range = 500  # Range to search for the gesture ID

def replace_gesture_hex_within_range(file_path):
    offset1 = find_last_hex_offset(file_path, hex_pattern2_Fixed)
    if offset1 is not None:
        search_start_offset = calculate_offset2(offset1, gesture_distance)
        try:
            with open(file_path, 'r+b') as file:
                # Read the 500-byte range for the old gesture ID
                file.seek(search_start_offset)
                data_chunk = file.read(gesture_search_range)
                
                # Find the old gesture ID within the range
                gesture_offset = data_chunk.find(gesture_old_id)
                if gesture_offset != -1:
                    actual_gesture_offset = search_start_offset + gesture_offset
                    file.seek(actual_gesture_offset)
                    file.write(gesture_new_id)
                    messagebox.showinfo("Success", "All gestures unlocked successfully!")
                else:
                    messagebox.showerror("Error", "Old gesture ID not found within the specified range.")
        except IOError as e:
            messagebox.showerror("File Error", f"Failed to open or modify the file: {e}")
    else:
        messagebox.showerror("Pattern Not Found", "Pattern not found in the file.")


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
            item_frame = ttk.Frame(storage_list_frame)
            item_frame.pack(fill="x", padx=10, pady=5)

            item_label = tk.Label(item_frame, text=f"{item_name} (Quantity: {quantity})", anchor="w")
            item_label.pack(side="left", fill="x", padx=5)

            new_quantity_var = tk.StringVar()
            new_quantity_entry = ttk.Entry(item_frame, textvariable=new_quantity_var, width=10)
            new_quantity_entry.pack(side="left", padx=5)

            update_button = ttk.Button(item_frame, text="Update Quantity", command=lambda item_offset=item_offset, new_quantity_var=new_quantity_var: update_item_quantity_in_file(file_path, item_offset, new_quantity_var))
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

    search_bar_frame = ttk.Frame(window2)
    search_bar_frame.pack(pady=5)
    tk.Label(window2, text="Choose replacement item:").pack(pady=5)
    scrollable_frame = ttk.Frame(window2)
    scrollable_frame.pack(padx=10, pady=5, fill="both", expand=True)
    tk.Label(search_bar_frame, text="Search:").pack(side="left", padx=5)
    search_entry = ttk.Entry(search_bar_frame, textvariable=search_var)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", lambda event: filter_replacement_list())

    canvas = tk.Canvas(window2)
    scrollbar = Scrollbar(window2, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

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
                    
                    
                replacement_button = ttk.Button(filter_replacement_list_frame, text=name, command=on_replace_click)
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

    search_bar_frame = ttk.Frame(window2)
    search_bar_frame.pack(pady=5)
    tk.Label(window2, text="Choose replacement item:").pack(pady=5)
    scrollable_frame = ttk.Frame(window2)
    scrollable_frame.pack(padx=10, pady=5, fill="both", expand=True)
    tk.Label(search_bar_frame, text="Search:").pack(side="left", padx=5)
    search_entry = ttk.Entry(search_bar_frame, textvariable=armor_search_var)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", lambda event: filter_armor_replacement_list())

    canvas = tk.Canvas(window2)
    scrollbar = Scrollbar(window2, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

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

                replacement_button = ttk.Button(filter_armor_replacement_list_frame, text=name, command=on_replace_click)
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
    # Clear previous items to free memory
    for widget in items_list_frame.winfo_children():
        widget.destroy()
    gc.collect()  # Force garbage collection

    key_offset = find_hex_offset(file_path, hex_pattern1_Fixed) + goods_magic_offset
    updated_items = find_key_items(file_path, key_offset)

    # Clear the previous list and display the updated items
    for widget in items_list_frame.winfo_children():
        widget.destroy()

    if updated_items:
        # Create a canvas and scrollbar to contain the items
        items_list_canvas = tk.Canvas(items_list_frame)
        items_list_scrollbar = Scrollbar(items_list_frame, orient="vertical", command=items_list_canvas.yview)
        items_list_frame_inner = ttk.Frame(items_list_canvas)

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
            item_frame = ttk.Frame(items_list_frame_inner)
            item_frame.pack(fill="x", padx=10, pady=5)

            item_label = tk.Label(item_frame, text=f"{item_name} (Quantity: {quantity})", anchor="w")
            item_label.pack(side="left", fill="x", padx=5)

            replace_button = ttk.Button(item_frame, text="Replace", command=lambda item=item_name: choose_replacement(item))
            replace_button.pack(side="right", padx=5)
    else:
        messagebox.showinfo("Info", "No items found.")

# refresh rings

def refresh_weapon_list(file_path):
    # Clear previous weapons to free memory
    for widget in weapons_list_frame.winfo_children():
        widget.destroy()
    gc.collect()

    updated_weapons = find_weapon_items(file_path)
    
    # Clear the previous list and display the updated items
    for widget in weapons_list_frame.winfo_children():
        widget.destroy()

    if updated_weapons:
        canvas = tk.Canvas(weapons_list_frame)
        scrollbar = Scrollbar(weapons_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

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
            weapon_frame = ttk.Frame(scrollable_frame)
            weapon_frame.pack(fill="x", padx=10, pady=5)
            
            weapon_label = tk.Label(weapon_frame, text=f"{weapon_name}", anchor="w")
            weapon_label.pack(side="left", fill="x", padx=5)
            
            replace_button = ttk.Button(weapon_frame, text="Replace", command=lambda weapon=weapon_name: replace_weapon(weapon))
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
        scrollable_frame = ttk.Frame(canvas)

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
            armor_frame = ttk.Frame(scrollable_frame)
            armor_frame.pack(fill="x", padx=10, pady=5)
            
            armor_label = tk.Label(armor_frame, text=f"{armor_name}", anchor="w")
            armor_label.pack(side="left", fill="x", padx=5)
            
            replace_button = ttk.Button(armor_frame, text="Replace", command=lambda armor=armor_name: replace_armor(armor))
            replace_button.pack(side="right", padx=5)
    else:
        messagebox.showinfo("Info", "No armor found.")

def replace_weapon(weapon_name):

    window2 = tk.Toplevel(window)
    window2.title(f"Replace {weapon_name}")

    tk.Label(window2, text="Choose replacement weapon:").pack(pady=5)
    search_bar_frame = ttk.Frame(window2)
    search_bar_frame.pack(pady=5)
    tk.Label(search_bar_frame, text="Search:").pack(side="left", padx=5)
    search_entry = ttk.Entry(search_bar_frame, textvariable=weapon_search_var)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", lambda event: filter_replacement_list())

    canvas = tk.Canvas(window2)
    scrollbar = Scrollbar(window2, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

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

            replacement_button = ttk.Button(filter_replacement_list_frame, text=name, command=on_replace_click)
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
    search_bar_frame = ttk.Frame(window2)
    search_bar_frame.pack(pady=5)
    tk.Label(search_bar_frame, text="Search:").pack(side="left", padx=5)
    search_entry = ttk.Entry(search_bar_frame, textvariable=armor_search_var)
    search_entry.pack(side="left", padx=5)
    search_entry.bind("<KeyRelease>", lambda event: filter_armor_replacement_list())

    canvas = tk.Canvas(window2)
    scrollbar = Scrollbar(window2, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

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

            replacement_button = ttk.Button(filter_armor_replacement_list_frame, text=name, command=on_replace_click)
            replacement_button.grid(row=row, column=col, padx=5, pady=5)
            
            col += 1
            if col > 3:
                col = 0
                row += 1


notebook = ttk.Notebook(window)
inventory_tab = ttk.Frame(notebook)
sub_notebook = ttk.Notebook(inventory_tab)

def on_tab_changed(event):
    file_path = file_path_var.get()
    if not file_path:  # Skip refresh if no file is selected
        return
        
    gc.collect()
    selected_tab = event.widget.tab(event.widget.index("current"))["text"]
    
    if selected_tab == "Rings":
        refresh_ring_list(file_path)
    elif selected_tab == "Inventory":
        refresh_item_list(file_path)
    elif selected_tab == "Weapons":
        refresh_weapon_list(file_path)
    elif selected_tab == "Armor":
        refresh_armor_list(file_path)
    elif selected_tab == "Bosses":
        refresh_boss_tab()

# Bind the NotebookTabChanged event to trigger the refresh when switching tabs
notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
# Character Tab
name_tab = ttk.Frame(notebook)
tk.Label(name_tab, text="Current Character Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
tk.Label(name_tab, textvariable=current_name_var).grid(row=0, column=1, padx=10, pady=10)
tk.Label(name_tab, text="New Character Name:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
ttk.Entry(name_tab, textvariable=new_name_var, width=20).grid(row=1, column=1, padx=10, pady=10)
ttk.Button(name_tab, text="Update Name", command=update_character_name).grid(row=2, column=0, columnspan=2, pady=20)

# Souls Tab
souls_tab = ttk.Frame(notebook)
tk.Label(souls_tab, text="Current Souls:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
tk.Label(souls_tab, textvariable=current_souls_var).grid(row=0, column=1, padx=10, pady=10)
tk.Label(souls_tab, text="New Souls Value (MAX 999999999):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
ttk.Entry(souls_tab, textvariable=new_souls_var, width=20).grid(row=1, column=1, padx=10, pady=10)
ttk.Button(souls_tab, text="Update Souls", command=update_souls_value).grid(row=2, column=0, columnspan=2, pady=20)
#rings
rings_tab = ttk.Frame(sub_notebook)
ring_list_frame = ttk.Frame(rings_tab)
ring_list_frame.pack(fill="x", padx=10, pady=5)
refresh_ring_button = ttk.Button(rings_tab, text="Refresh Ring List", command=lambda: refresh_ring_list(file_path_var.get()))
refresh_ring_button.pack(pady=10)


#hp Tap
tk.Label(name_tab, text="Current HP:").grid(row=5, column=0, padx=10, pady=10, sticky="e")
tk.Label(name_tab, textvariable=current_hp_var).grid(row=5, column=1, padx=10, pady=10)
tk.Label(name_tab, text="New HP:").grid(row=7, column=0, padx=10, pady=10, sticky="e")
ttk.Entry(name_tab, textvariable=new_hp_var, width=20).grid(row=7, column=1, padx=10, pady=10)
ttk.Button(name_tab, text="Update HP", command=update_hp_value).grid(row=8, column=0, columnspan=2, pady=20)

#FP Tap
tk.Label(name_tab, text="Current FP:").grid(row=9, column=0, padx=10, pady=10, sticky="e")
tk.Label(name_tab, textvariable=current_fp_var).grid(row=9, column=1, padx=10, pady=10)
tk.Label(name_tab, text="New FP:").grid(row=11, column=0, padx=10, pady=10, sticky="e")
ttk.Entry(name_tab, textvariable=new_fp_var, width=20).grid(row=11, column=1, padx=10, pady=10)
ttk.Button(name_tab, text="Update FP", command=update_fp_value).grid(row=12, column=0, columnspan=2, pady=20)

#STAMINA tap

tk.Label(name_tab, text="Current Stamina:").grid(row=0, column=5, padx=10, pady=10, sticky="e")
tk.Label(name_tab, textvariable=current_stamina_var).grid(row=0, column=4, padx=10, pady=10)
tk.Label(name_tab, text="New Stamina:").grid(row=1, column=5, padx=10, pady=10, sticky="e")
ttk.Entry(name_tab, textvariable=new_stamina_var, width=20).grid(row=1, column=4, padx=10, pady=10)
ttk.Button(name_tab, text="Update Stamina", command=update_stamina_value).grid(row=2, column=5, columnspan=2, pady=20)


# Stats Tab
stats_tab = ttk.Frame(notebook)
for idx, (stat, stat_offset) in enumerate(stats_offsets_for_stats_tap.items()):
    tk.Label(stats_tab, text=f"Current {stat}:").grid(row=idx, column=0, padx=10, pady=5, sticky="e")
    tk.Label(stats_tab, textvariable=current_stats_vars[stat]).grid(row=idx, column=1, padx=10, pady=5)
    ttk.Entry(stats_tab, textvariable=new_stats_vars[stat], width=10).grid(row=idx, column=2, padx=10, pady=5)
    ttk.Button(stats_tab, text=f"Update {stat}", command=lambda s=stat: update_stat(s)).grid(row=idx, column=3, padx=10, pady=5)

# Storage Box Tab
storage_box_tab = ttk.Frame(notebook)

storage_list_frame = ttk.Frame(storage_box_tab)
storage_list_frame.pack(fill="x", padx=10, pady=5)


# Items Tab
items_tab = ttk.Frame(sub_notebook)
items_list_frame = ttk.Frame(items_tab)
items_list_frame.pack(fill="x", padx=10, pady=5)


#ddd
left_frame = ttk.Frame(window, width=200)
left_frame.pack(side="left", fill="y")

# Right frame for the main content
right_frame = ttk.Frame(window)
right_frame.pack(side="right", fill="both", expand=True)

# Frame to display character names
character_list_frame = ttk.Frame(left_frame)
character_list_frame.pack(fill="y", padx=10, pady=10)

# Change to ttk.Button for Azure theme
button_width = 15  # Adjust this value to make buttons wider or narrower

# Define button width (assuming this is the same width used for character buttons)
button_width = 15  # Adjust this value as needed

# Define button width and padding
button_width = 15  # Adjust this value to make buttons wider or narrower
button_padding = 5  # Set padding for buttons

ttk.Button(left_frame, text="Load Folder", width=button_width, command=open_folder).pack(pady=10, padx=10)  # Added padx
ttk.Button(left_frame, text="Load File", width=button_width, command=open_single_file).pack(pady=10, padx=10)  # Added padx

# Create the "Toggle Theme" button in the left frame at the bottom
theme_button = ttk.Button(left_frame, text="Toggle Theme", width=button_width, command=toggle_theme)
theme_button.pack(side="bottom", pady=10, padx=10)

# Weapons Tab
weapons_tab = ttk.Frame(sub_notebook)
weapons_list_frame = ttk.Frame(weapons_tab)
weapons_list_frame.pack(fill="x", padx=10, pady=5)


# armmor tap
armor_tab = ttk.Frame(sub_notebook)
armor_list_frame = ttk.Frame(armor_tab)
armor_list_frame.pack(fill="x", padx=10, pady=5)



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
            current_stat_value = find_value_at_offset(file_path_var.get(), stat_offset, byte_size=1)
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

def update_fp_value_and_refresh():
    update_fp_value()
    refresh_on_click()

def update_stamina_value_and_refresh():
    update_stamina_value()
    refresh_on_click()


def refresh_storage_box_tab():
    storage_offset = find_hex_offset(file_path_var.get(), hex_pattern1_Fixed) + storage_box_distance
    refresh_storage_quantity_list(file_path_var.get())

ttk.Button(souls_tab, text="Update Souls", command=update_souls_value_and_refresh).grid(row=2, column=0, columnspan=2, pady=20)

# Character Tab
ttk.Button(name_tab, text="Update Name", command=update_character_name_and_refresh).grid(row=2, column=0, columnspan=2, pady=20)
ttk.Button(name_tab, text="Update HP", command=update_hp_value_and_refresh).grid(row=8, column=0, columnspan=2, pady=20)

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




# Add a main "World Flag" tab to the main notebook
world_flag_tab = ttk.Frame(notebook)
notebook.add(world_flag_tab, text="World Flag")

# Create a sub-notebook within the "World Flag" tab for "Bosses" and other sub-tabs
world_flag_sub_notebook = ttk.Notebook(world_flag_tab)
world_flag_sub_notebook.pack(expand=1, fill="both")

# Create the "Bosses" tab as a sub-tab within the "World Flag" sub-notebook
boss_tab = ttk.Frame(world_flag_sub_notebook)
world_flag_sub_notebook.add(boss_tab, text="Bosses")

# Canvas and scrollbar for the boss list
boss_list_canvas = tk.Canvas(boss_tab)
boss_list_scrollbar = tk.Scrollbar(boss_tab, orient="vertical", command=boss_list_canvas.yview)
boss_list_canvas.configure(yscrollcommand=boss_list_scrollbar.set)

# Pack the canvas and scrollbar
boss_list_canvas.pack(side="left", fill="both", expand=True)
boss_list_scrollbar.pack(side="right", fill="y")


# Function to handle auto-refresh on tab change within the World Flag sub-notebook
def on_world_flag_tab_changed(event):
    selected_tab = world_flag_sub_notebook.tab(world_flag_sub_notebook.select(), "text")
    if selected_tab == "Bosses":
        refresh_boss_tab()

world_flag_sub_notebook.bind("<<NotebookTabChanged>>", on_world_flag_tab_changed)

#for gesture
# Add Gesture Tab
gesture_tab = ttk.Frame(world_flag_sub_notebook)
world_flag_sub_notebook.add(gesture_tab, text="Gestures")

# Unlock All Gestures Button
unlock_gesture_button = ttk.Button(
    gesture_tab,
    text="Unlock All Gestures",
    command=lambda: replace_gesture_hex_within_range(file_path_var.get())
)
unlock_gesture_button.pack(pady=20)

gesture_instruction = """
Clicking 'Unlock All Gestures' Will also unlock Unmannered Bow.
"""
gesture_label = tk.Label(gesture_tab, text=gesture_instruction, wraplength=400, justify="left", anchor="nw")
gesture_label.pack(padx=10, pady=10, fill="x")

#for bonfire
# Create the "bonfire" tab as a sub-tab within the "World Flag" sub-notebook
bonfire_tab = ttk.Frame(world_flag_sub_notebook)
world_flag_sub_notebook.add(bonfire_tab, text="Bonfire")

# Canvas and scrollbar for the bonfire list
bonfire_list_canvas = tk.Canvas(bonfire_tab)
bonfire_list_scrollbar = tk.Scrollbar(bonfire_tab, orient="vertical", command=bonfire_list_canvas.yview)
bonfire_list_canvas.configure(yscrollcommand=bonfire_list_scrollbar.set)

# Pack the canvas and scrollbar
bonfire_list_canvas.pack(side="left", fill="both", expand=True)
bonfire_list_scrollbar.pack(side="right", fill="y")


# Function to handle auto-refresh on tab change within the World Flag sub-notebook
def on_world_flag_tab_changed(event):
    selected_tab = world_flag_sub_notebook.tab(world_flag_sub_notebook.select(), "text")
    if selected_tab == "Bonfire":
        refresh_bonfire_tab()
    elif selected_tab == "Bosses":
        refresh_boss_tab()


notebook.pack(expand=1, fill="both")
canvas = tk.Canvas(storage_box_tab)
scrollbar = ttk.Scrollbar(storage_box_tab, orient="vertical", command=canvas.yview)
storage_list_frame = ttk.Frame(canvas)
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


goods_text = """
For titanite Slab don't add over 15
"""


goods_label = tk.Label(items_tab, text=goods_text, wraplength=400, justify="left", anchor="nw")
goods_label.pack(padx=10, pady=10, fill="x") 


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

# Define styles for buttons
style = ttk.Style()
style.configure("Dark.TButton", background="black", foreground="white")
style.configure("Light.TButton", background="white", foreground="black")
style.configure("TButton", font=("Caskaydia Code NF", 12), padding=5)
style.configure("TLabel", font=("Caskaydia Code NF", 12), background="lightgray")
style.configure("TEntry", font=("Caskaydia Code NF", 12), padding=5)
