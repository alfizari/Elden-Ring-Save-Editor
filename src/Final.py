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


# Main window
window = tk.Tk()
window.title("Dark Souls 3 Save Editor - Section-Based")

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

## Add rings( similar to items)
def find_and_replace_pattern_with_ring_and_update_counters(ring_name):
    try:
        # Validate item name and fetch its ID
        ring_id = inventory_ring_hex_patterns.get(ring_name)
        if not ring_id:
            messagebox.showerror("Error", f"Item '{ring_name}' not found in ring.json.")
            return

        ring_id_bytes = bytes.fromhex(ring_id)
        if len(ring_id_bytes) != 4:
            messagebox.showerror("Error", f"Invalid ID for '{ring_name}'. ID must be exactly 4 bytes.")
            return


        # Get file path
        file_path = file_path_var.get()
        section_number = current_section_var.get()
        if not file_path or section_number == 0:
            messagebox.showerror("Error", "No file selected or section not chosen. Please load a file and select a section.")
            return

        # Get section information
        section_info = SECTIONS[section_number]
        section_data = loaded_file_data[section_info['start']:section_info['end']+1]

        # Locate Fixed Pattern 1
        fixed_pattern_offset = find_hex_offset(section_data, hex_pattern1_Fixed)
        if fixed_pattern_offset is None:
            messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
            return

        search_start = fixed_pattern_offset
        search_range = 10000  # Range to search for the item
        with open(file_path, 'r+b') as file:
            file.seek(section_info['start'] + search_start)
            data_chunk = file.read(search_range)


            # Add new ring if it doesn't exist
            empty_pattern = bytes.fromhex("00 00 00 00 FF FF FF FF")
            empty_offset = data_chunk.find(empty_pattern)
            if empty_offset == -1:
                messagebox.showerror("Error", "No empty slot found to add the item.")
                return

            # Calculate actual offset for empty slot
            actual_offset = section_info['start'] + search_start + empty_offset

            # Create the default pattern
            default_pattern = bytearray.fromhex("20 4E 00 A0 20 4E 00 20 01 00 00 00 9B 40 E8 04")
            default_pattern[:3] = ring_id_bytes[:3]  # First 3 bytes from the item ID
            default_pattern[4:8] = ring_id_bytes  # Full 4 bytes after B0
            ###
            reference_offset = actual_offset - 4
            file.seek(reference_offset)
            reference_value = int.from_bytes(file.read(1), 'little')

            # Calculate new third counter value
            new_third_counter_value = (reference_value + 1) & 0xFF


            default_pattern[12] = new_third_counter_value

            # Fourth counter logic: Extract the second nibble (0-9) of the 3rd byte behind the search range pattern
            reference_offset_4th = actual_offset - 3
            file.seek(reference_offset_4th)
            third_byte_value = int.from_bytes(file.read(1), 'little')

            # Extract the decimal value (0-9) from the second nibble (bits 0–3)
            decimal_value = third_byte_value & 0xF  # Mask to keep only the lower nibble (bits 0-3)

            # Ensure the value is within 0-9 range
            if decimal_value > 9:
                decimal_value = decimal_value % 10

            # Check if the third counter rolled over
            if new_third_counter_value == 0:  # Rollover happened
                # Increment the fourth counter (represented by the second nibble of the 14th byte)
                decimal_value = (decimal_value + 1) % 10  # Increment within the range 0-9

            # Update the corresponding bits of the 14th byte in the default pattern
            # Store the decimal digit (0-9) in the least significant nibble of the 14th byte
            default_pattern[13] = (default_pattern[13] & 0xF0) | decimal_value


            # Write the new item pattern
            file.seek(actual_offset)
            file.write(default_pattern)

            # Update counters
            increment_counters(file, section_info['start'] + fixed_pattern_offset)

            # Success message
            messagebox.showinfo("Success", f"Added '{ring_name}'")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add ring: {e}")


def add_ring_from_ring(ring_name, ring_id):
    
    find_and_replace_pattern_with_ring_and_update_counters(ring_name)

def find_and_replace_pattern_with_ring_and_update_counters_bulk(ring_name, ring_id):
    try:
        ring_id_bytes = bytes.fromhex(ring_id)
        if len(ring_id_bytes) != 4:
            raise ValueError(f"Invalid ID for '{ring_name}'. ID must be exactly 4 bytes.")


        # Get file path
        file_path = file_path_var.get()
        section_number = current_section_var.get()
        if not file_path or section_number == 0:
            messagebox.showerror("Error", "No file selected or section not chosen. Please load a file and select a section.")
            return

        # Get section information
        section_info = SECTIONS[section_number]
        section_data = loaded_file_data[section_info['start']:section_info['end']+1]

        # Locate Fixed Pattern 1
        fixed_pattern_offset = find_hex_offset(section_data, hex_pattern1_Fixed)
        if fixed_pattern_offset is None:
            messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
            return

        search_start = fixed_pattern_offset
        search_range = 100000  # Range to search for the item
        with open(file_path, 'r+b') as file:
            file.seek(section_info['start'] + search_start)
            data_chunk = file.read(search_range)


            # Add new ring if it doesn't exist
            empty_pattern = bytes.fromhex("00 00 00 00 FF FF FF FF0")
            empty_offset = data_chunk.find(empty_pattern)
            if empty_offset == -1:
                raise ValueError("No empty slot found to add the item.")

            # Calculate actual offset for empty slot
            actual_offset = section_info['start'] + search_start + empty_offset

            # Create the default pattern
            default_pattern = bytearray.fromhex("20 4E 00 A0 20 4E 00 20 01 00 00 00 9B 40 E8 04")
            default_pattern[:3] = ring_id_bytes[:3]  # First 3 bytes from the item ID
            default_pattern[4:8] = ring_id_bytes  # Full 4 bytes after B0
            ###
            reference_offset = actual_offset - 4
            file.seek(reference_offset)
            reference_value = int.from_bytes(file.read(1), 'little')

            # Calculate new third counter value
            new_third_counter_value = (reference_value + 1) & 0xFF


            default_pattern[12] = new_third_counter_value

            # Fourth counter logic: Extract the second nibble (0-9) of the 3rd byte behind the search range pattern
            reference_offset_4th = actual_offset - 3
            file.seek(reference_offset_4th)
            third_byte_value = int.from_bytes(file.read(1), 'little')

            # Extract the decimal value (0-9) from the second nibble (bits 0–3)
            decimal_value = third_byte_value & 0xF  # Mask to keep only the lower nibble (bits 0-3)

            # Ensure the value is within 0-9 range
            if decimal_value > 9:
                decimal_value = decimal_value % 10

            # Check if the third counter rolled over
            if new_third_counter_value == 0:  # Rollover happened
                # Increment the fourth counter (represented by the second nibble of the 14th byte)
                decimal_value = (decimal_value + 1) % 10  # Increment within the range 0-9

            # Update the corresponding bits of the 14th byte in the default pattern
            # Store the decimal digit (0-9) in the least significant nibble of the 14th byte
            default_pattern[13] = (default_pattern[13] & 0xF0) | decimal_value

    
            # Write the new item pattern
            file.seek(actual_offset)
            file.write(default_pattern)

            # Update counters
            increment_counters(file, section_info['start'] + fixed_pattern_offset)

    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add ring: {e}")


def add_all_rings(filtered_rings):
    try:
        for ring_name, ring_id in filtered_rings.items():
            find_and_replace_pattern_with_ring_and_update_counters_bulk(ring_name, ring_id)
        messagebox.showinfo("Success", "All items added successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add all items: {e}")

def show_ring_from_list_bulk():
    ring_window = tk.Toplevel(window)
    ring_window.title("Add Rings")
    ring_window.geometry("600x400")
    ring_window.attributes("-topmost", True)  # Keeps the window on top
    ring_window.focus_force()  # Brings the window into focus

    # Search bar for filtering items
    search_frame = ttk.Frame(ring_window)
    search_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Create a scrollable frame for the item list
    canvas = tk.Canvas(ring_window)
    scrollbar = ttk.Scrollbar(ring_window, orient="vertical", command=canvas.yview)
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
        filtered_rings = {k: v for k, v in inventory_ring_hex_patterns.items() if search_term in k.lower()}

        # Add "Add All" button
        add_all_button = ttk.Button(
            scrollable_frame,
            text="Add All",
            command=lambda: add_all_rings(filtered_rings)
        )
        add_all_button.pack(fill="x", pady=5)

        for ring_name, ring_id in filtered_rings.items():
            ring_frame = ttk.Frame(scrollable_frame)
            ring_frame.pack(fill="x", padx=5, pady=2)

            # Display item name
            tk.Label(ring_frame, text=ring_name, anchor="w").pack(side="left", fill="x", expand=True)

    # Filter items on search input
    search_entry.bind("<KeyRelease>", lambda event: filter_items())

    # Initially populate the list with all items
    filter_items()

def show_ring_from_list():
    
    ring_window = tk.Toplevel(window)
    ring_window.title("Add Rings")
    ring_window.geometry("600x400")
    ring_window.attributes("-topmost", True)  # Keeps the window on top
    ring_window.focus_force()  # Brings the window into focus

    # Search bar for filtering items
    search_frame = ttk.Frame(ring_window)
    search_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Create a scrollable frame for the item list
    canvas = tk.Canvas(ring_window)
    scrollbar = ttk.Scrollbar(ring_window, orient="vertical", command=canvas.yview)
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
        filtered_ring = {k: v for k, v in inventory_ring_hex_patterns.items() if search_term in k.lower()}

        for ring_name, ring_id in filtered_ring.items():
            ring_frame = ttk.Frame(scrollable_frame)
            ring_frame.pack(fill="x", padx=5, pady=2)

            # Display item name
            tk.Label(ring_frame, text=ring_name, anchor="w").pack(side="left", fill="x", expand=True)

            # "Add/Update" button for each item
            add_button = ttk.Button(
                ring_frame,
                text="Add",
                command=lambda name=ring_name, hex_id=ring_id: add_ring_from_ring(name, hex_id)
            )
            add_button.pack(side="right", padx=5)

    # Filter items on search input
    search_entry.bind("<KeyRelease>", lambda event: filter_items())

    # Initially populate the list with all items
    filter_items()


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



def show_goods_magic_list_bulk():
    goods_magic_window = tk.Toplevel(window)
    goods_magic_window.title("Add or Update Items by Category")
    goods_magic_window.geometry("600x600")
    goods_magic_window.attributes("-topmost", True)
    goods_magic_window.focus_force()

    # Define categories
    categories = {
        "Consumables": list(inventory_goods_magic_hex_patterns.items())[:227],
        
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

        # Define category-specific quantity limits
        category_quantity_limits = {
            "Coals": 99,
            "Ashes/Bone": 99,
            "Tome/Scroll": 99,
            "Magic": 99, 

        }

        # Loop through selected categories and process items
        for category, items in categories.items():
            if selected_categories[category].get():  # Check if category is selected
                max_quantity = category_quantity_limits.get(category, 99)  # Default to 99 if not specified
                for item_name, item_id in items:
                    try:
                        find_and_replace_pattern_with_item_and_update_counters_bulk(item_name, quantity=max_quantity)
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

hex_pattern3_fixed = (
    "00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 "
    "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 "
    "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 "
    "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 "
    "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00"
)



def delete_fixed_pattern_3_bytes(file, fixed_pattern_offset):
    """
    Search for a specific pattern and delete the trailing bytes.
    """

    # Define the large pattern to search for
    large_pattern = bytes.fromhex(
        "'00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF"
    )

    # Define the trailing bytes to remove
    trailing_pattern = bytes.fromhex("00 00 00 00 FF FF FF FF")

    # Read a reasonable range to find the large pattern
    search_range = 250000  # Define how much of the file to search
    file.seek(max(0, fixed_pattern_offset - search_range))
    data_chunk = file.read(search_range + len(large_pattern))

    # Find the large pattern
    large_pattern_offset = data_chunk.find(large_pattern)
    if large_pattern_offset == -1:
        print("Large pattern not found.")
        return

    # Find the last occurrence of the trailing pattern within the large pattern
    trailing_offset = data_chunk.find(trailing_pattern, large_pattern_offset)
    if trailing_offset == -1:
        print("Trailing pattern not found after the large pattern.")
        return

    # Calculate the absolute file offset of the trailing pattern
    absolute_offset = max(0, fixed_pattern_offset - search_range) + trailing_offset

    # Delete the trailing bytes by rewriting the file without them
    file.seek(0)
    before_trailing_pattern = file.read(absolute_offset)

    file.seek(absolute_offset + len(trailing_pattern))
    after_trailing_pattern = file.read()

    # Write the updated content to the file
    file.seek(0)
    file.write(before_trailing_pattern + after_trailing_pattern)
    file.truncate()





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
   
    pattern = bytes.fromhex(pattern_hex)
    pattern_length = len(pattern)
    
    with open(file_path, 'rb') as file:
        offset = start_offset

        while offset >= 0:
            file.seek(offset)
            chunk = file.read(pattern_length)
            
            if chunk == pattern:
                return offset  # Pattern found
            
            offset -= 1  # Move upward byte by byte

    return None  # Pattern not found



def add_weapon(item_name, upgrade_level, parent_window):
    
    try:
        
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
        weapon_id_bytes[0] = (weapon_id_bytes[0] + upgrade_level) & 0xFF  # Wrap to a single byte in hex

        # Get the file path
        file_path = file_path_var.get()
        section_number = current_section_var.get()
        if not file_path or section_number == 0:
            messagebox.showerror("Error", "No file selected or section not chosen. Please load a file and select a section.")
            return

        # Get section information
        section_info = SECTIONS[section_number]
        section_data = loaded_file_data[section_info['start']:section_info['end']+1]

        # Define Fixed Patterns
        fixed_pattern_3 = bytes.fromhex(
            "00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 "
            "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 "
            "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 "
            "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 "
            "FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00"
        )

        # Locate Fixed Pattern 3
        fixed_pattern_3_offset = find_hex_offset(section_data, fixed_pattern_3.hex())
        if fixed_pattern_3_offset is None:
            messagebox.showerror("Error", "Fixed Pattern 3 not found in the file.")
            return
        fixed_pattern_1_offset = search_fixed_pattern(
            section_data,
            "80 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00",
            fixed_pattern_3_offset
        )
        

        with open(file_path, 'r+b') as file:
            increment_counters(file, section_info['start'] + fixed_pattern_3_offset)
            
            # Inject Default Pattern 1
            # Inject Default Pattern 1
            inject_offset = fixed_pattern_1_offset + section_info['start'] + 5  # Offset for injection
            default_pattern_1 = bytearray.fromhex(
                "B7 12 80 80 90 AB 1E 00 46 00 00 00 02 00 00 00 01 00 00 00 00 00 00 80 "
                "00 00 00 00 00 00 00 80 00 00 00 00 00 00 00 80 00 00 00 00 00 00 00 80 "
                "00 00 00 00 00 00 00 80 00 00 00 00"
            )
            default_pattern_1[4:8] = weapon_id_bytes  # Assign weapon ID

            # Inject the new pattern
            file.seek(inject_offset)
            remaining_data = file.read(section_info['end'] - inject_offset + 1)
  
            file.seek(inject_offset)
            file.write(default_pattern_1 + remaining_data)
            file.flush()  # Ensure data is written immediately


            # Calculate offsets for the 60th and 59th bytes **relative to the new pattern**
            byte_60th_offset = inject_offset - 60
            byte_59th_offset = inject_offset - 59


            # Read the current values of the 60th and 59th bytes for the new pattern
            file.seek(byte_60th_offset)
            byte_60th = int.from_bytes(file.read(1), 'little')

            file.seek(byte_59th_offset)
            byte_59th = int.from_bytes(file.read(1), 'little')

            # Update the values for the fifth counter
            new_byte_60th = (byte_60th + 1) & 0xFF  # Increment 60th byte
            default_pattern_1[0] = new_byte_60th  # Update first byte of the new pattern
            default_pattern_1[1] = byte_59th  # Keep 59th byte unchanged unless overflow

            # Handle overflow logic
            if new_byte_60th == 0:  # Overflow occurred
                new_byte_59th = (byte_59th + 1) & 0xFF
                default_pattern_1[1] = new_byte_59th  # Update second byte of the new pattern

            with open(file_path, 'r+b') as file:
                # Inject Default Pattern 1
                file.seek(inject_offset)
                file.write(default_pattern_1)
                file.flush()  # Ensure immediate write

                # Search for Default Pattern 2 within the section
                search_pattern = bytes.fromhex("00 00 00 00 FF FF FF FF")
                search_range = min(100000, section_info['end'] - fixed_pattern_3_offset + 1)  # Ensure search range is within bounds
                search_start = section_info['start'] + fixed_pattern_3_offset
                file.seek(search_start)
                data_chunk = file.read(search_range)
                pattern_offset = data_chunk.find(search_pattern)

                if pattern_offset == -1:
                    messagebox.showerror("Error", "Pattern not found in the specified range for Default Pattern 2.")
                    return

                default_pattern_2_offset = search_start + pattern_offset
                default_pattern_2 = bytearray.fromhex("B7 12 80 80 90 AB 1E 00 01 00 00 00 81 00 96 C9")
                default_pattern_2[0] = new_byte_60th      # Use the 60th byte for a specific field
                default_pattern_2[1] = byte_59th          # Use the 59th byte for another specific field
                default_pattern_2[4:8] = weapon_id_bytes  # Assign weapon ID

                # Third Counter Logic
                third_counter_offset = default_pattern_2_offset - 4
                if third_counter_offset < section_info['start']:
                    raise ValueError("Third counter offset is out of section bounds.")

                file.seek(third_counter_offset)
                reference_value = int.from_bytes(file.read(1), "little")

                # Calculate new third counter value
                new_third_counter_value = (reference_value + 1) & 0xFF
                default_pattern_2[12] = new_third_counter_value

                # Fourth Counter Logic
                reference_offset_4th = default_pattern_2_offset - 3
                if reference_offset_4th < section_info['start']:
                    raise ValueError("Fourth counter reference offset is out of section bounds.")

                file.seek(reference_offset_4th)
                third_byte_value = int.from_bytes(file.read(1), 'little')

                # Extract the decimal value (0-9) from the second nibble (bits 0–3)
                decimal_value = third_byte_value & 0xF  # Mask to keep only the lower nibble (bits 0-3)

                # Ensure the value is within the 0-9 range
                if decimal_value > 9:
                    decimal_value = decimal_value % 10

                # Check if the third counter rolled over
                if new_third_counter_value == 0:  # Rollover happened
                    decimal_value = (decimal_value + 1) % 10  # Increment within the range 0-9

                # Update the corresponding bits of the 14th byte in the default pattern
                default_pattern_2[13] = (default_pattern_2[13] & 0xF0) | decimal_value

                # Write Default Pattern 2
                if default_pattern_2_offset > section_info['end']:
                    raise ValueError("Default Pattern 2 offset exceeds the section bounds.")

                file.seek(default_pattern_2_offset)  # Move to the start of the pattern offset
                file.write(default_pattern_2)  # Write Default Pattern 2


            

            # Cleanup actions
            delete_fixed_pattern_3_bytes(file, section_info['start'] + fixed_pattern_3_offset)
            delete_bytes_dynamically_from_section_end(100, 20)


    except Exception as e:
        messagebox.showerror("Error", f"Failed to add weapon: {e}")
    

def increment_counters(file, fixed_pattern_offset, counter1_distance=501, counter2_distance=37373, counter3_distance= 37377, should_increment=True):
 
    try:
        if not should_increment:
            print("No new item added. Counters not incremented.")
            return

        # Counter 1
        counter1_offset = fixed_pattern_offset + counter1_distance
        file.seek(counter1_offset)
        counter1_value = int.from_bytes(file.read(2), 'little')  # Read 2 bytes

        # Increment the counter
        counter1_new_value = (counter1_value + 1) & 0xFFFF  # Ensure it stays within 2 bytes
        file.seek(counter1_offset)
        file.write(counter1_new_value.to_bytes(2, 'little'))


        # Counter 2
        counter2_offset = fixed_pattern_offset + counter2_distance
        file.seek(counter2_offset)
        counter2_value = int.from_bytes(file.read(2), 'little')  # Read 2 bytes
        

        # Increment the counter
        counter2_new_value = (counter2_value + 1) & 0xFFFF  # Ensure it stays within 2 bytes
        file.seek(counter2_offset)
        file.write(counter2_new_value.to_bytes(2, 'little'))

        # Counter 3
        counter3_offset = fixed_pattern_offset + counter3_distance
        file.seek(counter3_offset)
        counter3_value = int.from_bytes(file.read(2), 'little')  # Read 2 bytes
        

        # Increment the counter
        counter3_new_value = (counter3_value + 1) & 0xFFFF  # Ensure it stays within 2 bytes
        file.seek(counter3_offset)
        file.write(counter3_new_value.to_bytes(2, 'little'))
        

        # Log the updated file data at the offsets
        log_file_data_at_offset(file, counter1_offset, length=2)
        log_file_data_at_offset(file, counter2_offset, length=2)

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

    # Add a label for instructions
    tk.Label(
        weapons_window, 
        text="Click the button below to add all weapons at upgrade level 0.", 
        wraplength=280, 
        justify="center"
    ).pack(pady=20)

    # Bulk Add All Weapons Button
    bulk_add_button = ttk.Button(
        weapons_window,
        text="Add All Weapons",
        command=lambda: bulk_add_weapons(weapons_window)
    )
    bulk_add_button.pack(fill="x", padx=20, pady=10)

def bulk_add_weapons(parent_window):
    try:
        for weapon_name in inventory_weapons_hex_patterns.keys():
            add_weapon(weapon_name, 0, parent_window)
        messagebox.showinfo("Success", "All weapons added successfully at upgrade level 0.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add all weapons: {e}")


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
DO NOT ADD TITANITE SLAB OVER 15. DO NOT ADD ANY KEYS
"""
tk.Label(
    add_items_tab,
    text=add_items_instructions,
    wraplength=500,
    justify="left",
    anchor="nw"
).pack(padx=10, pady=10, fill="x")

# Add "Add Rings" tab
add_ring_tab = ttk.Frame(add_sub_notebook)
add_sub_notebook.add(add_ring_tab, text="Add Rings")

ttk.Button(
    add_ring_tab,
    text="Add Rings",
    command=show_ring_from_list  # Opens the item list window
).pack(pady=20, padx=20)

ttk.Button(
    add_ring_tab,
    text="Add All Rings",
    command=show_ring_from_list_bulk  # Opens the item list window
).pack(pady=20, padx=20)

my_label = tk.Label(window, text="Made by Alfazari911 --   Thanks to Nox and BawsDeep for help", anchor="e", padx=10)
my_label.pack(side="top", anchor="ne", padx=10, pady=5)

we_label = tk.Label(window, text="USE AT YOUR OWN RISK. EDITING STATS AND HP COULD GET YOU BANNED", anchor="w", padx=10)
we_label.pack(side="bottom", anchor="nw", padx=10, pady=5)

# Run 
window.mainloop()
