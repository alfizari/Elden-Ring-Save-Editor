import json
import glob
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, Scrollbar
import gc
from functools import wraps
from time import time

# Constants
hex_pattern1_Fixed = '00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF'
possible_name_distances_for_name_tap = [-283]
souls_distance = -219
stamina_distance= -275
ng_distance=-5 ##new game from pattern2
goods_magic_offset = 0
goods_magic_range = 30000
hex_pattern2_Fixed= 'FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF'
hex_pattern5_Fixed='00 00 00 00 00 00 00 FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF'

# Section Definitions
SECTIONS = {
    1: {'start': 0, 'end': 0x28006F},
    2: {'start': 0x280070, 'end': 0x50006F},
    3: {'start': 0x500070, 'end': 0x78006F},
    4: {'start': 0x780070, 'end': 0xA0006F}
}


# Set the working directory
working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)

# load and copy JSON data from files in the working directory
def load_and_copy_json(file_name):
    file_path = os.path.join(working_directory, "Resources/Json", file_name)
    with open(file_path, "r") as file:
        return json.load(file).copy()



inventory_goods_magic_hex_patterns = load_and_copy_json("goods.json")
replacement_items = inventory_goods_magic_hex_patterns.copy()
item_hex_patterns = inventory_goods_magic_hex_patterns



inventory_weapons_hex_patterns = load_and_copy_json("weapons.json")
weapon_item_patterns = inventory_weapons_hex_patterns.copy()
inventory_armor_hex_patterns = load_and_copy_json("armor.json")
armor_item_patterns = inventory_armor_hex_patterns

inventory_talisman_hex_patterns = load_and_copy_json("talisman.json")
talisman_item_patterns = inventory_talisman_hex_patterns

# Main window
window = tk.Tk()
window.title("Elden Ring Save Editor")

# Global variables
file_path_var = tk.StringVar()
current_name_var = tk.StringVar(value="N/A")
new_name_var = tk.StringVar()
current_souls_var = tk.StringVar(value="N/A")
new_souls_var = tk.StringVar()
current_section_var = tk.IntVar(value=0)
loaded_file_data = None
# Load and configure the Azure theme
try:
    # Set Theme Path
    azure_path = os.path.join(os.path.dirname(__file__), "Resources/Azure", "azure.tcl")
    window.tk.call("source", azure_path)
    window.tk.call("set_theme", "dark")  # or "light" for light theme
except tk.TclError as e:
    messagebox.showwarning("Theme Warning", f"Azure theme could not be loaded: {str(e)}")


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
current_stamina_var= tk.StringVar(value="N/A")
current_souls_var = tk.StringVar(value="N/A")
current_ng_var = tk.StringVar(value="N/A")
new_ng_var = tk.StringVar()
found_items = []
found_armor= []
found_ring= []

# Utility Functions
def read_file_section(file_path, start_offset, end_offset):
    try:
        with open(file_path, 'rb') as file:
            file.seek(start_offset)
            section_data = file.read(end_offset - start_offset + 1)
        return section_data
    except IOError as e:
        messagebox.showerror("Error", f"Failed to read file section: {str(e)}")
        return None

def find_hex_offset(section_data, hex_pattern):
    try:
        pattern_bytes = bytes.fromhex(hex_pattern)
        if pattern_bytes in section_data:
            return section_data.index(pattern_bytes)
        return None
    except ValueError as e:
        messagebox.showerror("Error", f"Failed to find hex pattern: {str(e)}")
        return None

def calculate_relative_offset(section_start, offset):
    return section_start + offset

def find_value_at_offset(section_data, offset, byte_size=4):
    try:
        value_bytes = section_data[offset:offset+byte_size]
        if len(value_bytes) == byte_size:
            return int.from_bytes(value_bytes, 'little')
    except IndexError:
        pass
    return None

def find_character_name(section_data, offset, byte_size=32):
    try:
        value_bytes = section_data[offset:offset+byte_size]
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
    except IndexError:
        return "N/A"

def open_file():
    global loaded_file_data
    file_path = filedialog.askopenfilename(filetypes=[("Save Files", "*")])
    if file_path:
        file_path_var.set(file_path)
        file_name_label.config(text=f"File: {os.path.basename(file_path)}")
        
        # Read the entire file content
        with open(file_path, 'rb') as file:
            loaded_file_data = file.read()
        
        # Enable section buttons
        for btn in section_buttons:
            btn.config(state=tk.NORMAL)

def load_section(section_number):
    if not loaded_file_data:
        messagebox.showerror("Error", "Please open a file first")
        return

    current_section_var.set(section_number)
    section_info = SECTIONS[section_number]
    section_data = loaded_file_data[section_info['start']:section_info['end']+1]

    # Try to find hex pattern in the section
    offset1 = find_hex_offset(section_data, hex_pattern1_Fixed)
    
    if offset1 is not None:
        # Display Souls value
        souls_offset = offset1 + souls_distance
        current_souls = find_value_at_offset(section_data, souls_offset)
        current_souls_var.set(current_souls if current_souls is not None else "N/A")

        # Display character name
        for distance in possible_name_distances_for_name_tap:
            name_offset = offset1 + distance
            current_name = find_character_name(section_data, name_offset)
            if current_name and current_name != "N/A":
                current_name_var.set(current_name)
                break
        else:
            current_name_var.set("N/A")
    else:
        current_souls_var.set("N/A")
        current_name_var.set("N/A")

def write_value_at_offset(file_path, offset, value, byte_size=4):
    value_bytes = value.to_bytes(byte_size, 'little')
    with open(file_path, 'r+b') as file:
        file.seek(offset)
        file.write(value_bytes)

def write_character_name(file_path, base_offset, section_start, new_name, byte_size=32):
    name_bytes = []
    for char in new_name:
        name_bytes.append(ord(char))
        name_bytes.append(0) 
    name_bytes = name_bytes[:byte_size]
    
    with open(file_path, 'r+b') as file:
        file.seek(base_offset + section_start)
        file.write(bytes(name_bytes))

def update_souls_value():
    file_path = file_path_var.get()
    section_number = current_section_var.get()
    
    if not file_path or not new_souls_var.get() or section_number == 0:
        messagebox.showerror("Input Error", "Please open a file and select a section!")
        return
    
    try:
        new_souls_value = int(new_souls_var.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid decimal number for Souls.")
        return

    section_info = SECTIONS[section_number]
    section_data = loaded_file_data[section_info['start']:section_info['end']+1]
    offset1 = find_hex_offset(section_data, hex_pattern1_Fixed)
    
    if offset1 is not None:
        souls_offset = offset1 + souls_distance
        write_value_at_offset(file_path, section_info['start'] + souls_offset, new_souls_value)
        messagebox.showinfo("Success", f"Souls value updated to {new_souls_value}. Reload section to verify.")
    else:
        messagebox.showerror("Pattern Not Found", "Pattern not found in the selected section.")

def update_character_name():
    file_path = file_path_var.get()
    section_number = current_section_var.get()
    new_name = new_name_var.get()

    if not file_path or not new_name or section_number == 0:
        messagebox.showerror("Input Error", "Please open a file, select a section, and enter a name!")
        return

    section_info = SECTIONS[section_number]
    section_data = loaded_file_data[section_info['start']:section_info['end']+1]
    offset1 = find_hex_offset(section_data, hex_pattern1_Fixed)
    
    if offset1 is not None:
        for distance in possible_name_distances_for_name_tap:
            name_offset = offset1 + distance
            write_character_name(file_path, name_offset, section_info['start'], new_name)
            messagebox.showinfo("Success", f"Character name updated to '{new_name}'.")
            current_name_var.set(new_name)
            return
    
    messagebox.showerror("Error", "Could not find name offset in the selected section.")


## ADD items
def find_and_replace_pattern_with_item_and_update_counters(item_name, quantity):
    global loaded_file_data  # Add this to ensure we can modify the global variable
    try:
        # Validate item name and fetch its ID
        item_id = inventory_goods_magic_hex_patterns.get(item_name)
        if not item_id:
            messagebox.showerror("Error", f"Item '{item_name}' not found in goods_magic.json.")
            return

        item_id_bytes = bytes.fromhex(item_id)
        if len(item_id_bytes) != 4:
            messagebox.showerror("Error", f"Invalid ID for '{item_name}'. ID must be exactly 4 bytes.")
            return

        max_quantity = 99
        quantity = min(quantity, max_quantity)  # Ensure quantity does not exceed max

        # Get file path
        file_path = file_path_var.get()
        section_number = current_section_var.get()
        if not file_path or section_number == 0:
            messagebox.showerror("Error", "No file selected or section not chosen. Please load a file and select a section.")
            return

        # Get section information
        section_info = SECTIONS[section_number]
        
        # Convert loaded_file_data to bytearray if it's not already
        if isinstance(loaded_file_data, bytes):
            loaded_file_data = bytearray(loaded_file_data)
        
        # Get current section data from loaded_file_data
        section_data = loaded_file_data[section_info['start']:section_info['end']+1]

        # Locate Fixed Pattern 1
        fixed_pattern_offset = find_hex_offset(section_data, hex_pattern1_Fixed)
        if fixed_pattern_offset is None:
            messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
            return

        with open(file_path, 'r+b') as file:
            loaded_file_data = bytearray(file.read())
            # Check if item exists in current section
            for idx in range(len(section_data) - 4):
                if section_data[idx:idx + 4] == item_id_bytes:
                    # Update quantity if the item exists
                    quantity_offset = section_info['start'] + idx + 4
                    file.seek(quantity_offset)
                    existing_quantity = int.from_bytes(file.read(1), 'little')
                    new_quantity = min(existing_quantity + quantity, max_quantity)
                    file.seek(quantity_offset)
                    file.write(new_quantity.to_bytes(1, 'little'))
                    
                    # Update the in-memory section data
                    loaded_file_data[section_info['start'] + idx + 4] = new_quantity
                    
                    messagebox.showinfo("Success", 
                        f"Updated quantity of '{item_name}' to {new_quantity} in section {section_number}.")
                    increment_counters(file, section_info['start'] + fixed_pattern_offset)
                    return

            # Add new item if it doesn't exist
            empty_pattern = bytes.fromhex("00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            empty_offset = section_data.find(empty_pattern)
            if empty_offset == -1:
                messagebox.showerror("Error", "No empty slot found to add the item in the selected section.")
                return

            # Calculate actual offset for empty slot
            actual_offset = section_info['start'] + empty_offset + 2

            # Create the default pattern
            default_pattern = bytearray.fromhex("A4 06 00 B0 03 00 00 00 1F 01")
            default_pattern[:4] = item_id_bytes[:4]  # First 3 bytes from the item ID
            default_pattern[4] = quantity  # Quantity at 9th byte
            
            # Counters logic
            reference_offset = actual_offset - 4
            file.seek(reference_offset)
            reference_value = int.from_bytes(file.read(1), 'little')
            new_third_counter_value = (reference_value + 2) & 0xFF
            default_pattern[8] = new_third_counter_value

            # Fourth counter logic
            reference_offset_4th = actual_offset - 3
            file.seek(reference_offset_4th)
            third_byte_value = int.from_bytes(file.read(1), 'little')
            decimal_value = third_byte_value & 0xF
            if decimal_value > 9:
                decimal_value = decimal_value % 10
            if new_third_counter_value == 0:  # Rollover happened
                decimal_value = (decimal_value + 1) % 10
            default_pattern[9] = (default_pattern[9] & 0xF0) | decimal_value

            # Write the new item pattern
            file.seek(actual_offset)
            file.write(default_pattern)

            # Update the in-memory section data
            for i, byte in enumerate(default_pattern):
                loaded_file_data[actual_offset + i] = byte

            # Increment counters because a new item was added
            increment_counters(file, section_info['start'] + fixed_pattern_offset)

            messagebox.showinfo("Success", 
                f"Added '{item_name}' with quantity {quantity} to section {section_number}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to add or update item: {e}")
##Talisman
def find_and_replace_pattern_with_talisman_and_update_counters(item_name):
    global loaded_file_data  # Add this to ensure we can modify the global variable
    try:
        # Validate item name and fetch its ID
        item_id = inventory_talisman_hex_patterns.get(item_name)
        if not item_id:
            messagebox.showerror("Error", f"Item '{item_name}' not found in goods_magic.json.")
            return

        item_id_bytes = bytes.fromhex(item_id)
        if len(item_id_bytes) != 4:
            messagebox.showerror("Error", f"Invalid ID for '{item_name}'. ID must be exactly 4 bytes.")
            return

        # Get file path
        file_path = file_path_var.get()
        section_number = current_section_var.get()
        if not file_path or section_number == 0:
            messagebox.showerror("Error", "No file selected or section not chosen. Please load a file and select a section.")
            return

        # Get section information
        section_info = SECTIONS[section_number]
        
        # Convert loaded_file_data to bytearray if it's not already
        if isinstance(loaded_file_data, bytes):
            loaded_file_data = bytearray(loaded_file_data)
        
        # Get current section data from loaded_file_data
        section_data = loaded_file_data[section_info['start']:section_info['end']+1]

        # Locate Fixed Pattern 1
        fixed_pattern_offset = find_hex_offset(section_data, hex_pattern1_Fixed)
        if fixed_pattern_offset is None:
            messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
            return

        with open(file_path, 'r+b') as file:
            loaded_file_data = bytearray(file.read())
            # Add new item if it doesn't exist
            empty_pattern = bytes.fromhex("00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            empty_offset = section_data.find(empty_pattern)
            if empty_offset == -1:
                messagebox.showerror("Error", "No empty slot found to add the item in the selected section.")
                return

            # Calculate actual offset for empty slot
            actual_offset = section_info['start'] + empty_offset + 2

            # Create the default pattern
            default_pattern = bytearray.fromhex("B2 1B 00 A0 01 00 00 00 AE 00")
            default_pattern[:2] = item_id_bytes[:2]  # First 3 bytes from the item ID
            
            
            # Counters logic
            reference_offset = actual_offset - 4
            file.seek(reference_offset)
            reference_value = int.from_bytes(file.read(1), 'little')
            new_third_counter_value = (reference_value + 2) & 0xFF
            default_pattern[8] = new_third_counter_value

            # Fourth counter logic
            reference_offset_4th = actual_offset - 3
            file.seek(reference_offset_4th)
            third_byte_value = int.from_bytes(file.read(1), 'little')
            decimal_value = third_byte_value & 0xF
            if decimal_value > 9:
                decimal_value = decimal_value % 10
            if new_third_counter_value == 0:  # Rollover happened
                decimal_value = (decimal_value + 1) % 10
            default_pattern[9] = (default_pattern[9] & 0xF0) | decimal_value

            # Write the new item pattern
            file.seek(actual_offset)
            file.write(default_pattern)

            # Update the in-memory section data
            for i, byte in enumerate(default_pattern):
                loaded_file_data[actual_offset + i] = byte

            # Increment counters because a new item was added
            increment_counters(file, section_info['start'] + fixed_pattern_offset)


    except Exception as e:
        messagebox.showerror("Error", f"Failed to add or update item: {e}")

def find_and_replace_pattern_with_item_and_update_counters_bulk(item_name, quantity):
    global loaded_file_data  # Add this to ensure we can modify the global variable
    try:
        # Validate item name and fetch its ID
        item_id = inventory_goods_magic_hex_patterns.get(item_name)
        if not item_id:
            messagebox.showerror("Error", f"Item '{item_name}' not found in goods_magic.json.")
            return

        item_id_bytes = bytes.fromhex(item_id)
        if len(item_id_bytes) != 4:
            messagebox.showerror("Error", f"Invalid ID for '{item_name}'. ID must be exactly 4 bytes.")
            return

        max_quantity = 99
        quantity = min(quantity, max_quantity)  # Ensure quantity does not exceed max

        # Get file path
        file_path = file_path_var.get()
        section_number = current_section_var.get()
        if not file_path or section_number == 0:
            messagebox.showerror("Error", "No file selected or section not chosen. Please load a file and select a section.")
            return

        # Get section information
        section_info = SECTIONS[section_number]
        
        # Convert loaded_file_data to bytearray if it's not already
        if isinstance(loaded_file_data, bytes):
            loaded_file_data = bytearray(loaded_file_data)
        
        # Get current section data from loaded_file_data
        section_data = loaded_file_data[section_info['start']:section_info['end']+1]

        # Locate Fixed Pattern 1
        fixed_pattern_offset = find_hex_offset(section_data, hex_pattern1_Fixed)
        if fixed_pattern_offset is None:
            messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
            return

        with open(file_path, 'r+b') as file:
            # Check if item exists in current section
            for idx in range(len(section_data) - 4):
                if section_data[idx:idx + 4] == item_id_bytes:
                    # Update quantity if the item exists
                    quantity_offset = section_info['start'] + idx + 4
                    file.seek(quantity_offset)
                    existing_quantity = int.from_bytes(file.read(1), 'little')
                    new_quantity = min(existing_quantity + quantity, max_quantity)
                    file.seek(quantity_offset)
                    file.write(new_quantity.to_bytes(1, 'little'))
                    
                    # Update the in-memory section data
                    loaded_file_data[section_info['start'] + idx + 4] = new_quantity
                    
                    
                    increment_counters(file, section_info['start'] + fixed_pattern_offset)
                    return

            # Add new item if it doesn't exist
            empty_pattern = bytes.fromhex("00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
            empty_offset = section_data.find(empty_pattern)
            if empty_offset == -1:
                messagebox.showerror("Error", "No empty slot found to add the item in the selected section.")
                return

            # Calculate actual offset for empty slot
            actual_offset = section_info['start'] + empty_offset + 2

            # Create the default pattern
            default_pattern = bytearray.fromhex("A4 06 00 B0 03 00 00 00 1F 01")
            default_pattern[:4] = item_id_bytes[:4]  # First 3 bytes from the item ID
            default_pattern[4] = quantity  # Quantity at 9th byte
            
            # Counters logic
            reference_offset = actual_offset - 4
            file.seek(reference_offset)
            reference_value = int.from_bytes(file.read(1), 'little')
            new_third_counter_value = (reference_value + 2) & 0xFF
            default_pattern[8] = new_third_counter_value

            # Fourth counter logic
            reference_offset_4th = actual_offset - 3
            file.seek(reference_offset_4th)
            third_byte_value = int.from_bytes(file.read(1), 'little')
            decimal_value = third_byte_value & 0xF
            if decimal_value > 9:
                decimal_value = decimal_value % 10
            if new_third_counter_value == 0:  # Rollover happened
                decimal_value = (decimal_value + 1) % 10
            default_pattern[9] = (default_pattern[9] & 0xF0) | decimal_value

            # Write the new item pattern
            file.seek(actual_offset)
            file.write(default_pattern)

            # Update the in-memory section data
            for i, byte in enumerate(default_pattern):
                loaded_file_data[actual_offset + i] = byte

            # Increment counters because a new item was added
            increment_counters(file, section_info['start'] + fixed_pattern_offset)

        

    except Exception as e:
        messagebox.showerror("Error", f"Failed to add or update item: {e}")
###Talisman
def show_talisman_list_bulk():
    talisman_window = tk.Toplevel(window)
    talisman_window.title("Add or Update Items by Category")
    talisman_window.geometry("600x600")
    talisman_window.attributes("-topmost", True)
    talisman_window.focus_force()

    # Define categories
    categories = {
        "Base Game": list(inventory_talisman_hex_patterns.items())[:115],
        "DLC": list(inventory_talisman_hex_patterns.items())[115:155],
    }

    # Store the selected categories
    selected_categories = {category: tk.BooleanVar() for category in categories}

    # Create category selection section
    category_frame = ttk.Frame(talisman_window)
    category_frame.pack(fill="x", padx=10, pady=10)
    tk.Label(category_frame, text="Select Categories to Add:").pack(anchor="w")
    for category, var in selected_categories.items():
        ttk.Checkbutton(
            category_frame,
            text=category,
            variable=var
        ).pack(anchor="w")

    # Action frame
    action_frame = ttk.Frame(talisman_window)
    action_frame.pack(fill="x", padx=10, pady=10)

    def add_selected_items():
        success_items = []
        error_items = []

        # Loop through selected categories and process items
        for category, items in categories.items():
            if selected_categories[category].get():  # Check if category is selected
                for item_name, item_id in items:
                    try:
                        find_and_replace_pattern_with_talisman_and_update_counters(item_name)
                        success_items.append(item_name)
                    except Exception as e:
                        error_items.append(f"{item_name}: {str(e)}")

        # Consolidate success and error messages
        if success_items:
            messagebox.showinfo(
                "Success",
                f"Successfully added/updated the following items:\n{', '.join(success_items)}"
            )
        if error_items:
            messagebox.showerror(
                "Error",
                f"Failed to add/update the following items:\n{', '.join(error_items)}"
            )


    # Add button
    ttk.Button(
        action_frame,
        text="Add Selected Items",
        command=add_selected_items
    ).pack(fill="x", padx=5, pady=5)

    # Close button
    ttk.Button(
        action_frame,
        text="Close",
        command=talisman_window.destroy
    ).pack(fill="x", padx=5, pady=5)

def add_item_from_talisman(item_name, item_id, parent_window):
    
    find_and_replace_pattern_with_talisman_and_update_counters(item_name)

def show_talisman_list():
    
    talisman_window = tk.Toplevel(window)
    talisman_window.title("Add Items")
    talisman_window.geometry("600x400")
    talisman_window.attributes("-topmost", True)  # Keeps the window on top
    talisman_window.focus_force()  # Brings the window into focus

    # Search bar for filtering items
    search_frame = ttk.Frame(talisman_window)
    search_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Create a scrollable frame for the item list
    canvas = tk.Canvas(talisman_window)
    scrollbar = ttk.Scrollbar(talisman_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def filter_items():
        
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        search_term = search_var.get().lower()
        filtered_items = {k: v for k, v in inventory_talisman_hex_patterns.items() if search_term in k.lower()}

        for item_name, item_id in filtered_items.items():
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill="x", padx=5, pady=2)

            # Display item name
            tk.Label(item_frame, text=item_name, anchor="w").pack(side="left", fill="x", expand=True)

            # "Add/Update" button for each item
            add_button = ttk.Button(
                item_frame,
                text="Add",
                command=lambda name=item_name, hex_id=item_id: add_item_from_talisman(name, hex_id, talisman_window)
            )
            add_button.pack(side="right", padx=5)

    # Filter items on search input
    search_entry.bind("<KeyRelease>", lambda event: filter_items())

    # Initially populate the list with all items
    filter_items()
    ##

def show_goods_magic_list_bulk():
    goods_magic_window = tk.Toplevel(window)
    goods_magic_window.title("Add or Update Items by Category")
    goods_magic_window.geometry("600x600")
    goods_magic_window.attributes("-topmost", True)
    goods_magic_window.focus_force()

    # Define categories
    categories = {
        "Base Game": list(inventory_goods_magic_hex_patterns.items())[:173],
        "DLC": list(inventory_goods_magic_hex_patterns.items())[:227],
        
    }

    # Store the selected categories
    selected_categories = {category: tk.BooleanVar() for category in categories}

    # Create category selection section
    category_frame = ttk.Frame(goods_magic_window)
    category_frame.pack(fill="x", padx=10, pady=10)
    tk.Label(category_frame, text="Select Categories to Add:").pack(anchor="w")
    for category, var in selected_categories.items():
        ttk.Checkbutton(
            category_frame,
            text=category,
            variable=var
        ).pack(anchor="w")

    # Action frame
    action_frame = ttk.Frame(goods_magic_window)
    action_frame.pack(fill="x", padx=10, pady=10)

    def add_selected_items():
        success_items = []
        error_items = []


        # Loop through selected categories and process items
        for category, items in categories.items():
            if selected_categories[category].get():  # Check if category is selected
                for item_name, item_id in items:
                    try:
                        find_and_replace_pattern_with_item_and_update_counters_bulk(item_name, quantity=99)
                        success_items.append(item_name)
                    except Exception as e:
                        error_items.append(f"{item_name}: {str(e)}")

        # Consolidate success and error messages
        if success_items:
            messagebox.showinfo(
                "Success",
                f"Successfully added/updated the following items:\n{', '.join(success_items)}"
            )
        if error_items:
            messagebox.showerror(
                "Error",
                f"Failed to add/update the following items:\n{', '.join(error_items)}"
            )


    # Add button
    ttk.Button(
        action_frame,
        text="Add Selected Items",
        command=add_selected_items
    ).pack(fill="x", padx=5, pady=5)

    # Close button
    ttk.Button(
        action_frame,
        text="Close",
        command=goods_magic_window.destroy
    ).pack(fill="x", padx=5, pady=5)

def add_item_from_goods_magic(item_name, item_id, parent_window):
    
    # Use the parent window to keep the input dialog on top
    quantity = simpledialog.askinteger(
        "Input Quantity",
        f"Enter the quantity for {item_name} (1-99):",
        minvalue=1,
        maxvalue=99,
        parent=parent_window  # Attach the dialog to the "Add Items" list window
    )

    # Proceed to add the item if quantity is specified
    if quantity is not None:
        find_and_replace_pattern_with_item_and_update_counters(item_name, quantity)

def show_goods_magic_list():
    
    goods_magic_window = tk.Toplevel(window)
    goods_magic_window.title("Add or Update Items")
    goods_magic_window.geometry("600x400")
    goods_magic_window.attributes("-topmost", True)  # Keeps the window on top
    goods_magic_window.focus_force()  # Brings the window into focus

    # Search bar for filtering items
    search_frame = ttk.Frame(goods_magic_window)
    search_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Create a scrollable frame for the item list
    canvas = tk.Canvas(goods_magic_window)
    scrollbar = ttk.Scrollbar(goods_magic_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def filter_items():
        
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        search_term = search_var.get().lower()
        filtered_items = {k: v for k, v in inventory_goods_magic_hex_patterns.items() if search_term in k.lower()}

        for item_name, item_id in filtered_items.items():
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill="x", padx=5, pady=2)

            # Display item name
            tk.Label(item_frame, text=item_name, anchor="w").pack(side="left", fill="x", expand=True)

            # "Add/Update" button for each item
            add_button = ttk.Button(
                item_frame,
                text="Add/Update",
                command=lambda name=item_name, hex_id=item_id: add_item_from_goods_magic(name, hex_id, goods_magic_window)
            )
            add_button.pack(side="right", padx=5)

    # Filter items on search input
    search_entry.bind("<KeyRelease>", lambda event: filter_items())

    # Initially populate the list with all items
    filter_items()

def find_last_fixed_pattern_1_above_character(section_data, fixed_pattern_1, char_name_offset):
    fixed_pattern_1_bytes = bytes.fromhex(fixed_pattern_1)
    
    # Initialize variables for searching
    last_fixed_pattern_1_offset = -1
    start_search = 0
    
    while True:
        # Find the next occurrence of fixed_pattern_1 starting from the last found position
        offset = section_data.find(fixed_pattern_1_bytes, start_search)
        if offset == -1 or offset >= char_name_offset:
            break  # Stop searching once we go beyond the character name or no more patterns are found
        
        # Update the last known position of fixed_pattern_1
        last_fixed_pattern_1_offset = offset
        # Move search forward
        start_search = offset + 1

    # Return the last occurrence, or raise an error if not found
    if last_fixed_pattern_1_offset == -1:
        raise ValueError("No Fixed Pattern 1 found above the character name.")
    
    return last_fixed_pattern_1_offset

def delete_fixed_pattern_3_bytes(file, section_start, section_end, fixed_pattern_offset, distance_above_large_pattern):
    # Define the patterns
    large_pattern = bytes.fromhex(
        "00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 "
        "00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 "
        "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 "
        "00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 "
        "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 "
        "00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 "
        "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 "
        "00 00 00 00 00 00 00 00 FF FF FF FF"
    )
    trailing_pattern = bytes.fromhex("00 00 00 00 FF FF FF FF")

    # Calculate absolute fixed pattern offset
    absolute_fixed_pattern_offset = section_start + fixed_pattern_offset

    if not (section_start <= absolute_fixed_pattern_offset < section_end):
        print("Fixed pattern offset is outside the specified section.")
        return

    # Read the entire section
    file.seek(section_start)
    section_data = bytearray(file.read(section_end - section_start))

    # Find the patterns within the section
    search_start = absolute_fixed_pattern_offset - section_start
    large_pattern_offset = section_data.find(large_pattern, search_start)
    
    if large_pattern_offset == -1:
        print("Large pattern not found within the section.")
        return

    # Calculate where to look for trailing pattern
    target_offset = large_pattern_offset + distance_above_large_pattern
    trailing_offset = section_data.find(trailing_pattern, target_offset)

    if trailing_offset == -1:
        print("Trailing pattern not found after the large pattern.")
        return

    # Remove only the trailing pattern bytes
    del section_data[trailing_offset:trailing_offset + len(trailing_pattern)]

    # Write the modified data back to the file
    file.seek(section_start)
    file.write(section_data)
    
    # Properly handle the file size
    remaining_data_start = section_end
    
    # Copy any remaining data after the section
    file.seek(remaining_data_start)
    remaining_data = file.read()
    file.write(remaining_data)
    
    # Truncate to the correct length
    file.truncate(file.tell() - len(trailing_pattern))








def delete_bytes_dynamically_from_section_end(distance_from_end, bytes_to_delete):
    try:
        # Get the file path and selected section
        file_path = file_path_var.get()  # Variable holding the file path in the app
        section_number = current_section_var.get()  # Variable holding the selected section number

        if not file_path:
            messagebox.showerror("Error", "No file selected. Please select a file.")
            return
        
        if section_number not in SECTIONS:
            messagebox.showerror("Error", "Invalid section selected. Please choose a valid section.")
            return

        # Retrieve the section info
        section_info = SECTIONS[section_number]
        section_start = section_info['start']
        section_end = section_info['end']

        # Calculate the start position for deletion
        deletion_start = section_end - distance_from_end
        if deletion_start < section_start:
            messagebox.showerror(
                "Error",
                "Distance from the end exceeds the section boundary. Cannot delete bytes."
            )
            return

        # Ensure we do not delete beyond the section start
        deletion_start = max(deletion_start, section_start)
        deletion_end = deletion_start + bytes_to_delete

        # Open the file and delete the bytes
        with open(file_path, 'r+b') as file:
            # Read all data after the deletion end
            file.seek(deletion_end)
            remaining_data = file.read()

            # Move to the deletion start and write remaining data
            file.seek(deletion_start)
            file.write(remaining_data)

            # Truncate the file to remove extra bytes at the end
            file.truncate()

        messagebox.showinfo(
            "Success",
            f"Successfully deleted {bytes_to_delete} bytes from Section {section_number}."
        )

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def search_fixed_pattern(file_path, pattern_hex, start_offset):
   try:
       # Convert pattern_hex to bytes if it's a string
       if isinstance(pattern_hex, str):
           pattern = bytes.fromhex(pattern_hex.replace(" ", ""))
       else:
           pattern = pattern_hex
          
       pattern_length = len(pattern)
      
       # If file_path is actually bytes/bytearray data
       if isinstance(file_path, (bytes, bytearray)):
           data = file_path
           current_offset = start_offset
           
           # Search upwards from start_offset
           while current_offset >= 0:
               if data[current_offset:current_offset + pattern_length] == pattern:
                   return current_offset
               current_offset -= 1
           return None
          
       # If file_path is an actual file path
       with open(file_path, 'rb') as file:
           current_offset = start_offset
           
           # Search upwards from start_offset
           while current_offset >= 0:
               file.seek(current_offset)
               chunk = file.read(pattern_length)
               
               if chunk == pattern:
                   return current_offset
               
               current_offset -= 1
               
       return None
   except Exception as e:
       print(f"Error in search_fixed_pattern: {e}")
       return None

def add_weapon(item_name, upgrade_level, parent_window):
    try:
        global loaded_file_data
        # Validate weapon name and fetch its ID
        weapon_id = inventory_weapons_hex_patterns.get(item_name)
        if not weapon_id:
            messagebox.showerror("Error", f"Weapon '{item_name}' not found in weapons.json.")
            return
        weapon_id_bytes = bytearray.fromhex(weapon_id)
        if len(weapon_id_bytes) != 4:
            messagebox.showerror("Error", f"Invalid ID for '{item_name}'. ID must be exactly 4 bytes.")
            return

        # Validate upgrade level
        if not (0 <= upgrade_level <= 10):
            messagebox.showerror("Error", "Upgrade level must be between 0 (base level) and 10.")
            return

        # Increment the first byte of the weapon ID by the upgrade level
        weapon_id_bytes[0] = (weapon_id_bytes[0] + upgrade_level) & 0xFF

        # Get the file path
        file_path = file_path_var.get()
        section_number = current_section_var.get()
        if not file_path or section_number == 0:
            messagebox.showerror("Error", "No file selected or section not chosen. Please load a file and select a section.")
            return

        section_info = SECTIONS[section_number]
        section_start = section_info['start']
        section_end = section_info['end']

        with open(file_path, 'r+b') as file:
            # Read the entire file content
            file.seek(0)
            entire_file = bytearray(file.read())
            original_size = len(entire_file)
            
            # Read section data
            section_data = entire_file[section_start:section_end + 1]
            
            

            # Define Fixed Pattern 3
            fixed_pattern_3 = bytearray.fromhex(
                "00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF"
            )

            # Locate Fixed Pattern 3
            fixed_pattern_3_offset = find_hex_offset(section_data, fixed_pattern_3.hex())
            if fixed_pattern_3_offset is None:
                messagebox.showerror("Error", "Fixed Pattern 3 not found in the file.")
                return
            # Update counters FIRST and write them immediately
            counter1_offset = section_info['start'] + fixed_pattern_3_offset + 501
            counter2_offset = section_info['start'] + fixed_pattern_3_offset + 37373
            counter3_offset = section_info['start'] + fixed_pattern_3_offset + 37377
            # Read current counter values
            file.seek(counter1_offset)
            counter1_value = int.from_bytes(file.read(2), 'little')
            file.seek(counter2_offset)
            counter2_value = int.from_bytes(file.read(2), 'little')
            file.seek(counter3_offset)
            counter3_value = int.from_bytes(file.read(2), 'little')
            # Calculate new values
            counter1_new_value = (counter1_value + 1) & 0xFFFF
            counter2_new_value = (counter2_value + 1) & 0xFFFF
            counter3_new_value = (counter3_value + 1) & 0xFFFF
            # Write new counter values immediately
            file.seek(counter1_offset)
            file.write(counter1_new_value.to_bytes(2, 'little'))
            file.seek(counter2_offset)
            file.write(counter2_new_value.to_bytes(2, 'little'))
            file.seek(counter3_offset)
            file.write(counter3_new_value.to_bytes(2, 'little'))
            
            # Ensure counter updates are written to disk
            file.flush()
            os.fsync(file.fileno())
            # Now proceed with weapon addition
            file.seek(0)
            entire_file = bytearray(file.read())
            section_data = entire_file[section_info['start']:section_info['end']+1]
            
            # Search for Fixed Pattern 1
            pattern_1_hex = "00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF"
            fixed_pattern_1 = bytearray.fromhex(pattern_1_hex)

            fixed_pattern_1_offset = search_fixed_pattern(
                section_data,
                fixed_pattern_1,
                fixed_pattern_3_offset
            )

            if fixed_pattern_1_offset is None:
                messagebox.showerror("Error", "Fixed Pattern 1 not found in the file.")
                return

            
            default_pattern_1= bytearray.fromhex("0B 11 80 80 F0 3B 2E 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
        
            weapon_id_offset = 4
            byte_60th_offset = fixed_pattern_1_offset + 8 - 21
            byte_59th_offset = fixed_pattern_1_offset + 8 - 20

            # Update default pattern with weapon ID and counter values
            default_pattern_1[weapon_id_offset:weapon_id_offset + 4] = weapon_id_bytes

            # Read and update counter values
            byte_60th = section_data[byte_60th_offset]
            byte_59th = section_data[byte_59th_offset]
            new_byte_60th = (byte_60th + 1) & 0xFF
            default_pattern_1[0] = new_byte_60th
            if new_byte_60th == 0:
                new_byte_59th = (byte_59th + 1) & 0xFF
                default_pattern_1[1] = new_byte_59th
            else:
                default_pattern_1[1] = byte_59th
                    
            # Inject first pattern
            inject_offset = fixed_pattern_1_offset + 8
            section_data[inject_offset:inject_offset] = default_pattern_1


            # Search for empty pattern
            empty_pattern = bytes.fromhex("00" * 1024)  # 1024 zeros
            empty_offset = section_data.find(empty_pattern)
            if empty_offset == -1:
                messagebox.showerror("Error", "No empty slot found to add the item in the selected section.")
                return

            # Calculate actual offset for empty slot
            actual_offset = empty_offset + 2

            # Create and update default pattern 2
            default_pattern_2 = bytearray.fromhex("35 02 80 80 01 00 00 00 6B 01")
            default_pattern_2[0] = new_byte_60th
            default_pattern_2[1] = byte_59th

            # Update counters for pattern 2
            reference_value = section_data[actual_offset - 4]
            new_third_counter_value = (reference_value + 2) & 0xFF
            default_pattern_2[8] = new_third_counter_value

            third_byte_value = section_data[actual_offset - 3]
            decimal_value = third_byte_value & 0xF
            if decimal_value > 9:
                decimal_value = decimal_value % 10
            if new_third_counter_value == 0:
                decimal_value = (decimal_value + 1) % 10
            default_pattern_2[9] = (default_pattern_2[9] & 0xF0) | decimal_value

            # Inject second pattern
            section_data[actual_offset:actual_offset + len(default_pattern_2)] = default_pattern_2

            trailing_pattern = bytes.fromhex("00 00 00 00 FF FF FF FF")
            section_trailing_offset = search_fixed_pattern(
                section_data,
                trailing_pattern,
                fixed_pattern_3_offset
            )
            
            if section_trailing_offset != -1 and section_trailing_offset is not None:
                # Remove the trailing pattern from section_data
                section_data = section_data[:section_trailing_offset] + section_data[section_trailing_offset + 8:]
                
                # Update the section in the entire file
                entire_file[section_info['start']:section_info['start'] + len(section_data)] = section_data
            else:
                print("No trailing pattern found above Fixed Pattern 3 within section boundaries")

            # Remove bytes from section end
            bytes_to_remove = 13

            # Find the new position of the section's end based on bytes_to_remove
            # Remove bytes from above the end of the section (above section_end)
            section_data = section_data[:-bytes_to_remove]
            if len(section_data) > section_end - section_start + 1:
                section_data = section_data[:section_end - section_start + 1]
            entire_file[section_info['start']:section_info['start'] + len(section_data)] = section_data
            

            # Write the entire updated file content
            file.seek(0)
            file.write(entire_file)
            file.flush()
            os.fsync(file.fileno())
            file.truncate()
            file.seek(0)
            loaded_file_data = bytearray(file.read())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add weapon: {str(e)}")

## armor
def add_armor(item_name, parent_window):
    try:
        global loaded_file_data
        # Validate weapon name and fetch its ID
        armor_id = inventory_armor_hex_patterns.get(item_name)
        if not armor_id:
            messagebox.showerror("Error", f"Weapon '{item_name}' not found in weapons.json.")
            return
        armor_id_bytes = bytearray.fromhex(armor_id)
        if len(armor_id_bytes) != 4:
            messagebox.showerror("Error", f"Invalid ID for '{item_name}'. ID must be exactly 4 bytes.")
            return

        # Get the file path
        file_path = file_path_var.get()
        section_number = current_section_var.get()
        if not file_path or section_number == 0:
            messagebox.showerror("Error", "No file selected or section not chosen. Please load a file and select a section.")
            return

        section_info = SECTIONS[section_number]
        section_start = section_info['start']
        section_end = section_info['end']

        with open(file_path, 'r+b') as file:
            # Read the entire file content
            file.seek(0)
            entire_file = bytearray(file.read())
            original_size = len(entire_file)
            
            # Read section data
            section_data = entire_file[section_start:section_end + 1]
            
            

            # Define Fixed Pattern 3
            fixed_pattern_3 = bytearray.fromhex(
                "00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF"
            )

            # Locate Fixed Pattern 3
            fixed_pattern_3_offset = find_hex_offset(section_data, fixed_pattern_3.hex())
            if fixed_pattern_3_offset is None:
                messagebox.showerror("Error", "Fixed Pattern 3 not found in the file.")
                return
            # Update counters FIRST and write them immediately
            counter1_offset = section_info['start'] + fixed_pattern_3_offset + 501
            counter2_offset = section_info['start'] + fixed_pattern_3_offset + 37373
            counter3_offset = section_info['start'] + fixed_pattern_3_offset + 37377
            # Read current counter values
            file.seek(counter1_offset)
            counter1_value = int.from_bytes(file.read(2), 'little')
            file.seek(counter2_offset)
            counter2_value = int.from_bytes(file.read(2), 'little')
            file.seek(counter3_offset)
            counter3_value = int.from_bytes(file.read(2), 'little')
            # Calculate new values
            counter1_new_value = (counter1_value + 1) & 0xFFFF
            counter2_new_value = (counter2_value + 1) & 0xFFFF
            counter3_new_value = (counter3_value + 1) & 0xFFFF
            # Write new counter values immediately
            file.seek(counter1_offset)
            file.write(counter1_new_value.to_bytes(2, 'little'))
            file.seek(counter2_offset)
            file.write(counter2_new_value.to_bytes(2, 'little'))
            file.seek(counter3_offset)
            file.write(counter3_new_value.to_bytes(2, 'little'))
            
            # Ensure counter updates are written to disk
            file.flush()
            os.fsync(file.fileno())
            # Now proceed with weapon addition
            file.seek(0)
            entire_file = bytearray(file.read())
            section_data = entire_file[section_info['start']:section_info['end']+1]
            
            # Search for Fixed Pattern 1
            pattern_1_hex = "00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF"
            fixed_pattern_1 = bytearray.fromhex(pattern_1_hex)

            fixed_pattern_1_offset = search_fixed_pattern(
                section_data,
                fixed_pattern_1,
                fixed_pattern_3_offset
            )

            if fixed_pattern_1_offset is None:
                messagebox.showerror("Error", "Fixed Pattern 1 not found in the file.")
                return

            
            default_pattern_1= bytearray.fromhex("CD 12 80 90 3C 28 00 10 00 00 00 00 00 00 00 00")
        
            armor_id_offset = 4
            byte_60th_offset = fixed_pattern_1_offset + 8 - 16
            byte_59th_offset = fixed_pattern_1_offset + 8 - 15

            # Update default pattern with weapon ID and counter values
            default_pattern_1[armor_id_offset:armor_id_offset + 4] = armor_id_bytes

            # Read and update counter values
            byte_60th = section_data[byte_60th_offset]
            byte_59th = section_data[byte_59th_offset]
            new_byte_60th = (byte_60th + 1) & 0xFF
            default_pattern_1[0] = new_byte_60th
            if new_byte_60th == 0:
                new_byte_59th = (byte_59th + 1) & 0xFF
                default_pattern_1[1] = new_byte_59th
            else:
                default_pattern_1[1] = byte_59th
                    
            # Inject first pattern
            inject_offset = fixed_pattern_1_offset + 8
            section_data[inject_offset:inject_offset] = default_pattern_1


            # Search for empty pattern
            empty_pattern = bytes.fromhex("00" * 1024)  # 1024 zeros
            empty_offset = section_data.find(empty_pattern)
            if empty_offset == -1:
                messagebox.showerror("Error", "No empty slot found to add the item in the selected section.")
                return

            # Calculate actual offset for empty slot
            actual_offset = empty_offset + 2

            # Create and update default pattern 2
            default_pattern_2 = bytearray.fromhex("35 02 80 90 01 00 00 00 6B 01")
            default_pattern_2[0] = new_byte_60th
            default_pattern_2[1] = byte_59th

            # Update counters for pattern 2
            reference_value = section_data[actual_offset - 4]
            new_third_counter_value = (reference_value + 2) & 0xFF
            default_pattern_2[8] = new_third_counter_value

            third_byte_value = section_data[actual_offset - 3]
            decimal_value = third_byte_value & 0xF
            if decimal_value > 9:
                decimal_value = decimal_value % 10
            if new_third_counter_value == 0:
                decimal_value = (decimal_value + 1) % 10
            default_pattern_2[9] = (default_pattern_2[9] & 0xF0) | decimal_value

            # Inject second pattern
            section_data[actual_offset:actual_offset + len(default_pattern_2)] = default_pattern_2

            trailing_pattern = bytes.fromhex("00 00 00 00 FF FF FF FF")
            section_trailing_offset = search_fixed_pattern(
                section_data,
                trailing_pattern,
                fixed_pattern_3_offset
            )
            
            if section_trailing_offset != -1 and section_trailing_offset is not None:
                # Remove the trailing pattern from section_data
                section_data = section_data[:section_trailing_offset] + section_data[section_trailing_offset + 8:]
                
                # Update the section in the entire file
                entire_file[section_info['start']:section_info['start'] + len(section_data)] = section_data
                
            else:
                print("No trailing pattern found above Fixed Pattern 3 within section boundaries")

            # Remove bytes from section end
            bytes_to_remove = 8

            # Find the new position of the section's end based on bytes_to_remove
            # Remove bytes from above the end of the section (above section_end)
            section_data = section_data[:-bytes_to_remove]
            if len(section_data) > section_end - section_start + 1:
                section_data = section_data[:section_end - section_start + 1]
            entire_file[section_info['start']:section_info['start'] + len(section_data)] = section_data
            

            # Write the entire updated file content
            file.seek(0)
            file.write(entire_file)
            file.flush()
            os.fsync(file.fileno())
            file.truncate()
            file.seek(0)
            loaded_file_data = bytearray(file.read())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add weapon: {str(e)}")
def show_armor_list():
   
    armor_window = tk.Toplevel(window)
    armor_window.title("Add Armors")
    armor_window.geometry("600x400")
    armor_window.attributes("-topmost", True)  # Keep the window on top
    armor_window.focus_force()  # Bring the window to the front

    # Search bar for filtering weapons
    search_frame = ttk.Frame(armor_window)
    search_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
    armor_search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=armor_search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Create a scrollable frame for the weapon list
    canvas = tk.Canvas(armor_window)
    scrollbar = ttk.Scrollbar(armor_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def filter_armor():
        
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        search_term = armor_search_var.get().lower()
        filtered_armor = {
            k: v for k, v in inventory_armor_hex_patterns.items() if search_term in k.lower()
        }

        for armor_name, armor_id in filtered_armor.items():
            armor_frame = ttk.Frame(scrollable_frame)
            armor_frame.pack(fill="x", padx=5, pady=2)

            # Display weapon name
            tk.Label(armor_frame, text=armor_name, anchor="w").pack(side="left", fill="x", expand=True)

            # "Add" button for each weapon
            add_button = ttk.Button(
                armor_frame,
                text="Add",
                command=lambda name=armor_name: add_armor(name, armor_window)
            )
            add_button.pack(side="right", padx=5)

    # Filter weapons on search input
    search_entry.bind("<KeyRelease>", lambda event: filter_armor())

    # Initially populate the list with all weapons
    filter_armor()

def show_armor_window_bulk():
    armor_window = tk.Toplevel(window)
    armor_window.title("Add All Armors")
    armor_window.geometry("300x150")
    armor_window.attributes("-topmost", True)  # Keep the window on top
    armor_window.focus_force()  # Bring the window to the front

    # Add a label for instructions
    tk.Label(
        armor_window, 
        text="Click the button below to add all armors.", 
        wraplength=280, 
        justify="center"
    ).pack(pady=20)

    # Bulk Add All Weapons Button
    bulk_add_button = ttk.Button(
        armor_window,
        text="Add All Armor",
        command=lambda: bulk_add_armor(armor_window)
    )
    bulk_add_button.pack(fill="x", padx=20, pady=10)

def bulk_add_armor(parent_window):
    try:
        for armor_name in inventory_armor_hex_patterns.keys():
            add_armor(armor_name, parent_window)
        messagebox.showinfo("Success", "All weapons added successfully at upgrade level 0.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add all weapons: {e}")    

def increment_counters(file, fixed_pattern_offset, counter1_distance=501, counter2_distance=37373, counter3_distance=37377, should_increment=True):
    try:
        if not should_increment:
            print("No new item added. Counters not incremented.")
            return
            # Store original file position
        original_position = file.tell()
            # Counter 1
        counter1_offset = fixed_pattern_offset + counter1_distance
        file.seek(counter1_offset)
        counter1_value = int.from_bytes(file.read(2), 'little')
        counter1_new_value = (counter1_value + 1) & 0xFFFF
            # Counter 2
        counter2_offset = fixed_pattern_offset + counter2_distance
        file.seek(counter2_offset)
        counter2_value = int.from_bytes(file.read(2), 'little')
        counter2_new_value = (counter2_value + 1) & 0xFFFF
            # Counter 3
        counter3_offset = fixed_pattern_offset + counter3_distance
        file.seek(counter3_offset)
        counter3_value = int.from_bytes(file.read(2), 'little')
        counter3_new_value = (counter3_value + 1) & 0xFFFF
            # Write all counter values back to file
        file.seek(counter1_offset)
        file.write(counter1_new_value.to_bytes(2, 'little'))
        
        file.seek(counter2_offset)
        file.write(counter2_new_value.to_bytes(2, 'little'))
        
        file.seek(counter3_offset)
        file.write(counter3_new_value.to_bytes(2, 'little'))
            # Ensure changes are written to disk
        file.flush()
        os.fsync(file.fileno())
            # Restore original file position
        file.seek(original_position)
    except Exception as e:
        print(f"Error incrementing counters: {e}")
        raise



def log_file_data_at_offset(file, offset, length=16):
    file.seek(offset)
    data = file.read(length)
    






def show_weapons_list():
   
    weapons_window = tk.Toplevel(window)
    weapons_window.title("Add Weapons")
    weapons_window.geometry("600x400")
    weapons_window.attributes("-topmost", True)  # Keep the window on top
    weapons_window.focus_force()  # Bring the window to the front

    # Search bar for filtering weapons
    search_frame = ttk.Frame(weapons_window)
    search_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
    weapon_search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=weapon_search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Create a scrollable frame for the weapon list
    canvas = tk.Canvas(weapons_window)
    scrollbar = ttk.Scrollbar(weapons_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def filter_weapons():
        
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        search_term = weapon_search_var.get().lower()
        filtered_weapons = {
            k: v for k, v in inventory_weapons_hex_patterns.items() if search_term in k.lower()
        }

        for weapon_name, weapon_id in filtered_weapons.items():
            weapon_frame = ttk.Frame(scrollable_frame)
            weapon_frame.pack(fill="x", padx=5, pady=2)

            # Display weapon name
            tk.Label(weapon_frame, text=weapon_name, anchor="w").pack(side="left", fill="x", expand=True)

            # "Add" button for each weapon
            add_button = ttk.Button(
                weapon_frame,
                text="Add",
                command=lambda name=weapon_name: select_weapon_upgrade(name, weapons_window)
            )
            add_button.pack(side="right", padx=5)

    # Filter weapons on search input
    search_entry.bind("<KeyRelease>", lambda event: filter_weapons())

    # Initially populate the list with all weapons
    filter_weapons()


def select_weapon_upgrade(weapon_name, weapons_window):
    upgrade_level = simpledialog.askinteger(
        title="Upgrade Level",
        prompt="Enter the upgrade level (0-10):",
        parent=weapons_window,
        minvalue=0,
        maxvalue=10
    )

    if upgrade_level is not None:  # Check if the user clicked "OK" and didn't cancel
        add_weapon(weapon_name, upgrade_level, weapons_window)
    else:
        print("Upgrade level selection was cancelled.")


def show_weapons_window_bulk():
    weapons_window = tk.Toplevel(window)
    weapons_window.title("Add All Weapons")
    weapons_window.geometry("300x150")
    weapons_window.attributes("-topmost", True)  # Keep the window on top
    weapons_window.focus_force()  # Bring the window to the front
    # Define categories
    categories = {
        "Base Game": list(inventory_weapons_hex_patterns.items())[:250],
        "DLC": list(inventory_weapons_hex_patterns.items())[250:264],
    }

    # Store the selected categories
    selected_categories = {category: tk.BooleanVar() for category in categories}

    # Create category selection section
    category_frame = ttk.Frame(weapons_window)
    category_frame.pack(fill="x", padx=10, pady=10)
    tk.Label(category_frame, text="Select Categories to Add:").pack(anchor="w")
    for category, var in selected_categories.items():
        ttk.Checkbutton(
            category_frame,
            text=category,
            variable=var
        ).pack(anchor="w")

    # Action frame
    action_frame = ttk.Frame(weapons_window)
    action_frame.pack(fill="x", padx=10, pady=10)

    def add_selected_items():
        success_items = []
        error_items = []

        # Loop through selected categories and process items
        for category, items in categories.items():
            if selected_categories[category].get():  # Check if category is selected
                for weapon_name, item_id in items:
                    try:
                        add_weapon(weapon_name, 0, weapons_window)
                        success_items.append(weapon_name)
                    except Exception as e:
                        error_items.append(f"{weapon_name}: {str(e)}")

        # Consolidate success and error messages
        if success_items:
            messagebox.showinfo(
                "Success",
                f"Successfully added/updated the following items:\n{', '.join(success_items)}"
            )
        if error_items:
            messagebox.showerror(
                "Error",
                f"Failed to add/update the following items:\n{', '.join(error_items)}"
            )


    # Add button
    ttk.Button(
        action_frame,
        text="Add Selected Items",
        command=add_selected_items
    ).pack(fill="x", padx=5, pady=5)

    # Close button
    ttk.Button(
        action_frame,
        text="Close",
        command=weapons_window.destroy
    ).pack(fill="x", padx=5, pady=5)





# UI Layout
file_open_frame = tk.Frame(window)
file_open_frame.pack(fill="x", padx=10, pady=5)

tk.Button(file_open_frame, text="Open Save File", command=open_file).pack(side="left", padx=5)
file_name_label = tk.Label(file_open_frame, text="No file selected", anchor="w")
file_name_label.pack(side="left", padx=10, fill="x")

# Section Selection Frame
section_frame = tk.Frame(window)
section_frame.pack(fill="x", padx=10, pady=5)
section_buttons = []

for i in range(1, 5):
    btn = tk.Button(section_frame, text=f"Slot {i}", command=lambda x=i: load_section(x), state=tk.DISABLED)
    btn.pack(side="left", padx=5)
    section_buttons.append(btn)

notebook = ttk.Notebook(window)


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





# Main Tab Container
# Main Tab Container
add_tab = ttk.Frame(notebook)

notebook.add(name_tab, text="Character (OFFLINE ONLY)")
notebook.add(add_tab, text="ADD")

notebook.add(souls_tab, text="Souls")

notebook.pack(expand=1, fill="both")
# Sub-Notebook inside "ADD" tab
add_sub_notebook = ttk.Notebook(add_tab)
add_sub_notebook.pack(expand=1, fill="both")

# Now add "add_tab" to the main notebook correctly
notebook.add(add_tab, text="ADD")


# Adding "Add Weapons" tab
add_weapons_tab = ttk.Frame(add_sub_notebook)
add_sub_notebook.add(add_weapons_tab, text="Add Weapons")

ttk.Button(
    add_weapons_tab,
    text="Add Weapons",
    command=show_weapons_list  # Opens the weapon list window
).pack(pady=20, padx=20)

ttk.Button(
    add_weapons_tab,
    text="Add All Weapons",
    command=show_weapons_window_bulk  # Opens the weapon list window
).pack(pady=20, padx=20)

# Add instruction for "Add Weapons" tab
add_weapons_instructions = """
MAKE SURE WHEN CHOOSING THE UPGRADE LEVEL THAT THE WEAPON COULD BE UPGRADED TO THAT OR YOU WILL GET BANNED.
"""
tk.Label(
    add_weapons_tab,
    text=add_weapons_instructions,
    wraplength=500,
    justify="left",
    anchor="nw"
).pack(padx=10, pady=10, fill="x")

# Adding "Add Items" tab
add_items_tab = ttk.Frame(add_sub_notebook)
add_sub_notebook.add(add_items_tab, text="Add Items")

ttk.Button(
    add_items_tab,
    text="Add or Update Items (SINGLE)",
    command=show_goods_magic_list  # Opens the item list window
).pack(pady=20, padx=20)

ttk.Button(
    add_items_tab,
    text="Add Bulk Items",
    command=show_goods_magic_list_bulk  # Opens the item list window
).pack(pady=20, padx=20)

# Add instruction for "Add Items" tab
add_items_instructions = """
Don't add too much
"""
tk.Label(
    add_items_tab,
    text=add_items_instructions,
    wraplength=500,
    justify="left",
    anchor="nw"
).pack(padx=10, pady=10, fill="x")

add_armor_tab = ttk.Frame(notebook)
add_sub_notebook.add(add_armor_tab, text="Add Armors")

ttk.Button(
    add_armor_tab,
    text="Add Armors",
    command=show_armor_list  # Opens the item list window
).pack(pady=20, padx=20)

ttk.Button(
    add_armor_tab,
    text="Add All Armors",
    command=show_armor_window_bulk  # Opens the item list window
).pack(pady=20, padx=20)

add_talisman_tab = ttk.Frame(add_sub_notebook)
add_sub_notebook.add(add_talisman_tab, text="Add Talisman")

ttk.Button(
    add_talisman_tab,
    text="Add",
    command=show_talisman_list  # Opens the item list window
).pack(pady=20, padx=20)

ttk.Button(
    add_talisman_tab,
    text="Add Bulk Talisman",
    command=show_talisman_list_bulk  # Opens the item list window
).pack(pady=20, padx=20)


my_label = tk.Label(window, text="Made by Alfazari911 --   Thanks to Nox and BawsDeep for help", anchor="e", padx=10)
my_label.pack(side="top", anchor="ne", padx=10, pady=5)

we_label = tk.Label(window, text="USE AT YOUR OWN RISK. EDITING STATS AND HP COULD GET YOU BANNED", anchor="w", padx=10)
we_label.pack(side="bottom", anchor="nw", padx=10, pady=5)

# Run 
window.mainloop()
