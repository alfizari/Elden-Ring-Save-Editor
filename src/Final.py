import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, Scrollbar
from functools import wraps
from time import time
import hashlib
import binascii
import shutil
# Constants
hex_pattern1_Fixed = '00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF'
possible_name_distances_for_name_tap = [-283]
souls_distance = -331
stamina_distance= -275
ng_distance=-280 ##new game from patternng
goods_magic_offset = 0
goods_magic_range = 30000
hex_pattern_ng= 'FF FF FF FF 00 00 00 00 00 00 00 00 00 01'
hex_pattern2_Fixed= 'FF FF 00 00 00 00 FF FF FF FF 00 00 00 00 FF FF FF FF'
hex_pattern5_Fixed='00 00 00 00 00 00 00 FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF FF FF FF FF FF FF 00 00 00 00 FF FF FF FF FF FF'
cookbook_hex= '80 00 00 02 00 80 20 08 02 00 80 20 00 02 00 80'
cookbook_id = bytes.fromhex("80 20 08 02 00 00 20 08 02 00 80 20 08 02 00 80 20 00 00 00 00 00 00 00 00 80 20 08 02 00 00 20 08 02 00 80 20 08 02 00 00 00 00 00 00 00 00 00 00 00 80 20 08 02 00 80 20 08 02 00 80 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 20 00 02 00 80 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 02 00 80 20 08 02 00 80 20 08 02 00 80 00 00 00 00 00 00 00 00 00 80 20 08 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 20 08 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 20 00 00 00 00 00 00 00 00 00 00 00 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02")
cookbook_distance= -250
hex_pattern_end= 'FF FF FF FF'
steamid_pattern_is='92 6F AC 6C'

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

inventory_aow_hex_patterns = load_and_copy_json("aow.json")
aow_item_patterns = inventory_aow_hex_patterns

inventory_all_hex_patterns = load_and_copy_json("output.json")
all_item_patterns = inventory_all_hex_patterns

# Main window
window = tk.Tk()
window.title("Elden Ring Save Editor")


stats_offsets_for_stats_tap = {
    "Level": -335,#find
    "Vigor": -379,
    "Mind": -375,
    "Endurance": -371,
    "Strength": -367,
    "Dexterity": -363,
    "Intelligence": -359,
    "Faith": -355,
    "Arcane": -351,
    "Gender": -249,
    "Class": -248,
}


GENDER_MAP = {
    1: "Male",
    0: "Female"
}
REVERSE_GENDER_MAP = {v: k for k, v in GENDER_MAP.items()}

CLASS_MAP = {
    0: "Vagabond",
    1: "Warrior",
    2: "Hero",
    3: "Bandit",
    4: "Astrologer",
    5: "Prophet",
    6: "Samurai",
    7: "Prisoner",
    8: "Confessor",
    9: "Wretch"
}
REVERSE_CLASS_MAP = {v: k for k, v in CLASS_MAP.items()}

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
current_stemaid_var= tk.StringVar()
current_stats_vars = {}
new_stats_vars = {}

# Initialize variables for each stat
for stat in stats_offsets_for_stats_tap:
    current_stats_vars[stat] = tk.StringVar()
    new_stats_vars[stat] = tk.StringVar()  # Use StringVar for all stats
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
    
def find_hex_offset_last(section_data, hex_pattern):
    try:
        pattern_bytes = bytes.fromhex(hex_pattern)
        last_index = section_data.rfind(pattern_bytes)
        if last_index != -1:
            return last_index
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
    global loaded_file_data, SECTIONS
    file_path = filedialog.askopenfilename(filetypes=[("Save Files", "*")])
    
    if file_path:
        file_name = os.path.basename(file_path)
        file_path_var.set(file_path)
        file_name_label.config(text=f"File: {file_name}")
        
        # Define sections based on file name
        if file_name.lower() == "memory.dat":
            SECTIONS = {
                1: {'start': 0x70, 'end': 0x28006F},
                2: {'start': 0x280070, 'end': 0x50006F},
                3: {'start': 0x500070, 'end': 0x78006F},
                4: {'start': 0x780070, 'end': 0xA0006F},
                5: {'start': 0xA00070, 'end': 0xC8006F},
                6: {'start': 0xC80070, 'end': 0xF0006F},
                7: {'start': 0xF00070, 'end': 0x118006F},
                8: {'start': 0x1180070, 'end': 0x140006F},
                9: {'start': 0x1400070, 'end': 0x168006F},
                10: {'start': 0x1680070, 'end': 0x190006F}
            }
        elif file_name.lower() == "er0000.sl2":
            SECTIONS = {
                1: {'start': 0x310, 'end': 0x28030F},
                2: {'start': 0x280320, 'end': 0x50031F},
                3: {'start': 0x500330, 'end': 0x78032F},
                4: {'start': 0x780340, 'end': 0xA0033F},
                5: {'start': 0xA00350, 'end': 0xC8034F},
                6: {'start': 0xC80360, 'end': 0xF0035F},
                7: {'start': 0xF00370, 'end': 0x118036F},
                8: {'start': 0x1180380, 'end': 0x140037F},
                9: {'start': 0x1400390, 'end': 0x168038F},
                10: {'start': 0x16803A0, 'end': 0x190039F}
            }
        try:
            with open(file_path, 'rb') as file:
                loaded_file_data = file.read()
            
            # Create a backup
            backup_path = f"{file_path}.bak1"
            with open(backup_path, 'wb') as backup_file:
                backup_file.write(loaded_file_data)
            
            messagebox.showinfo("Backup Created", f"Backup saved as {backup_path}")
            
            # Enable section buttons
            for btn in section_buttons:
                btn.config(state=tk.NORMAL)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file or create backup: {str(e)}")
            return
def calculate_offset2(offset1, distance):
    return offset1 + distance



def load_section(section_number):
    if not loaded_file_data:
        messagebox.showerror("Error", "Please open a file first")
        return

    current_section_var.set(section_number)
    section_info = SECTIONS[section_number]
    section_data = loaded_file_data[section_info['start']:section_info['end']+1]

    # Try to find hex pattern in the section
    offset1 = find_hex_offset(section_data, hex_pattern1_Fixed)
    offsetng = find_hex_offset(section_data, hex_pattern_ng)
    offset_steam = find_hex_offset_last(section_data, steamid_pattern_is)
    if offsetng is not None:
        #new game
        ng_offset = offsetng+ ng_distance
        current_ng = section_data[ng_offset] if ng_offset < len(section_data) else None
        current_ng_var.set(current_ng if current_ng is not None else "N/A")
    if offset_steam is not None:
        #steam id
        steam_offset = offset_steam - 130
        current_steamid = section_data[steam_offset:steam_offset + 8]
        set_steam_id(0, current_steamid)  # Save the current Steam ID (before import)
        current_stemaid_var.set(current_steamid)
        print("Current SteamID:", current_steamid)

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
        for stat, distance in stats_offsets_for_stats_tap.items():
            stat_offset = calculate_offset2(offset1, distance)
            byte_size = 2 if stat == "Level" else 1
            current_stat_value = find_value_at_offset(section_data, stat_offset, byte_size=byte_size)

            if current_stat_value is None:
                display_value = "N/A"
                new_stats_vars[stat].set("")  # Clear the input field
            elif stat == "Gender":
                display_value = GENDER_MAP.get(current_stat_value, f"Unknown ({current_stat_value})")
                # Update both display and input variables
                current_stats_vars[stat].set(display_value)
                new_stats_vars[stat].set(display_value)
                print(f"Setting {stat} to: {display_value}")
            elif stat == "Class":
                display_value = CLASS_MAP.get(current_stat_value, f"Unknown ({current_stat_value})")
                # Update both display and input variables
                current_stats_vars[stat].set(display_value)
                new_stats_vars[stat].set(display_value)
                print(f"Setting {stat} to: {display_value}")
            else:
                display_value = str(current_stat_value)
                # Update both display and input variables
                current_stats_vars[stat].set(display_value)
                new_stats_vars[stat].set(display_value)  # Set the StringVar for the Entry
                print(f"Setting {stat} to: {display_value}")

    else:
        current_souls_var.set("N/A")
        current_name_var.set("N/A")
        current_ng_var.set("N/A")
steam_id_storage = [None, None]  # index 0 = current, index 1 = post-import

def steam_id(index):
    if 0 <= index < len(steam_id_storage):
        return steam_id_storage[index]
    return None

def set_steam_id(index, value):
    if index >= len(steam_id_storage):
        steam_id_storage.extend([None] * (index - len(steam_id_storage) + 1))
    steam_id_storage[index] = value




def import_done():
    section_number = current_section_var.get()

    # Import the section
    import_section()


    

def import_section():
    global loaded_file_data
    global current_stemaid_var
    if not loaded_file_data:
        messagebox.showerror("Error", "Please open a file first")
        return

    current_section = current_section_var.get()
    if not current_section:
        messagebox.showerror("Error", "Please Choose a slot first")
        return
    

    import_path = filedialog.askopenfilename(filetypes=[("Save Files", "*")])
    if not import_path:
        return

    import_file_name = os.path.basename(import_path)

    # Define import sections
    if import_file_name.lower() == "memory.dat":
        import_sections = {
            1: {'start': 0x70, 'end': 0x28006F},
            2: {'start': 0x280070, 'end': 0x50006F},
            3: {'start': 0x500070, 'end': 0x78006F},
            4: {'start': 0x780070, 'end': 0xA0006F},
            5: {'start': 0xA00070, 'end': 0xC8006F},
            6: {'start': 0xC80070, 'end': 0xF0006F},
            7: {'start': 0xF00070, 'end': 0x118006F},
            8: {'start': 0x1180070, 'end': 0x140006F},
            9: {'start': 0x1400070, 'end': 0x168006F},
            10: {'start': 0x1680070, 'end': 0x190006F}
        }
    elif import_file_name.lower() == "er0000.sl2":
        import_sections = {
            1: {'start': 0x310, 'end': 0x28030F},
            2: {'start': 0x280320, 'end': 0x50031F},
            3: {'start': 0x500330, 'end': 0x78032F},
            4: {'start': 0x780340, 'end': 0xA0033F},
            5: {'start': 0xA00350, 'end': 0xC8034F},
            6: {'start': 0xC80360, 'end': 0xF0035F},
            7: {'start': 0xF00370, 'end': 0x118036F},
            8: {'start': 0x1180380, 'end': 0x140037F},
            9: {'start': 0x1400390, 'end': 0x168038F},
            10: {'start': 0x16803A0, 'end': 0x190039F}
        }
    else:
        messagebox.showerror("Unsupported File", "Unsupported file format for import.")
        return

    try:
        with open(import_path, 'rb') as f:
            import_data = f.read()
    except Exception as e:
        messagebox.showerror("Error", f"Could not read import file: {e}")
        return
    # Extract names for all sections
    section_names = []

    for sec_num, sec_info in import_sections.items():
        data = import_data[sec_info['start']:sec_info['end']+1]
        offset1 = find_hex_offset(data, hex_pattern1_Fixed)
        name_found = "N/A"
        if offset1 is not None:
            for distance in possible_name_distances_for_name_tap:
                name_offset = offset1 + distance
                name = find_character_name(data, name_offset)
                if name and name != "N/A":
                    name_found = name
                    break
        section_names.append((sec_num, name_found))


    # UI to choose section to import
    section_window = tk.Toplevel()
    section_window.title("Import Section")
    section_window.geometry("350x400")

    label = tk.Label(section_window, text="Choose a section to import from:")
    label.pack(pady=10)

    for sec_num, name in section_names:
        btn_text = f"Section {sec_num} - {name}"
        def make_callback(s=sec_num):
            def callback():
                global loaded_file_data

                # Get original Steam ID saved from current section
                original_steam_id = steam_id(0)
                if original_steam_id is None:
                    messagebox.showerror("Error", "Original Steam ID not loaded. Please load a section first.")
                    return

                # Extract the section chunk to import
                imported_chunk = import_data[import_sections[s]['start']:import_sections[s]['end']+1]

                # Try to locate the Steam ID in the imported chunk
                offset_steam = find_hex_offset_last(imported_chunk, steamid_pattern_is)
                if offset_steam is not None:
                    steam_offset = offset_steam - 130
                    if 0 <= steam_offset <= len(imported_chunk) - 130:
                        # Replace Steam ID in the imported chunk before writing it
                        imported_chunk = (
                            imported_chunk[:steam_offset] +
                            original_steam_id +
                            imported_chunk[steam_offset + 8:]
                        )
                        print(f"Patched Steam ID at offset {hex(steam_offset)} in imported chunk.")
                    else:
                        print("Steam offset out of range in imported chunk.")
                else:
                    print("No Steam ID pattern found in imported chunk.")

                # Replace the section in the loaded file data
                local_start = SECTIONS[current_section]['start']
                local_end = SECTIONS[current_section]['end']
                loaded_file_data = (
                    loaded_file_data[:local_start] +
                    imported_chunk +
                    loaded_file_data[local_end+1:]
                )

                # Save to file
                with open(file_path_var.get(), 'wb') as f:
                    f.write(loaded_file_data)

                messagebox.showinfo("Import Successful", f"Replaced current section with Section {s} from import file.")
                load_section(current_section)
                section_window.destroy()
            return callback

        btn = tk.Button(section_window, text=btn_text, command=make_callback())
        btn.pack(pady=5)



def recalc_checksum(file):
    """
    Recalculates and updates checksum values in a binary file. Copied from Ariescyn/EldenRing-Save-Manager
    """
    with open(file, "rb") as fh:
        dat = fh.read()
        slot_ls = []
        slot_len = 2621439
        cs_len = 15
        s_ind = 0x00000310
        c_ind = 0x00000300

        # Build nested list containing data and checksum related to each slot
        for i in range(10):
            d = dat[s_ind : s_ind + slot_len + 1]  # Extract data for the slot
            c = dat[c_ind : c_ind + cs_len + 1]  # Extract checksum for the slot
            slot_ls.append([d, c])  # Append the data and checksum to the slot list
            s_ind += 2621456  # Increment the slot data index
            c_ind += 2621456  # Increment the checksum index

        # Do comparisons and recalculate checksums
        for ind, i in enumerate(slot_ls):
            new_cs = hashlib.md5(i[0]).hexdigest()  # Recalculate the checksum for the data
            cur_cs = binascii.hexlify(i[1]).decode("utf-8")  # Convert the current checksum to a string

            if new_cs != cur_cs:  # Compare the recalculated and current checksums
                slot_ls[ind][1] = binascii.unhexlify(new_cs)  # Update the checksum in the slot list

        slot_len = 2621439
        cs_len = 15
        s_ind = 0x00000310
        c_ind = 0x00000300
        # Insert all checksums into data
        for i in slot_ls:
            dat = dat[:s_ind] + i[0] + dat[s_ind + slot_len + 1 :]  # Update the data in the original data
            dat = dat[:c_ind] + i[1] + dat[c_ind + cs_len + 1 :]  # Update the checksum in the original data
            s_ind += 2621456  # Increment the slot data index
            c_ind += 2621456  # Increment the checksum index

        # Manually doing General checksum
        general = dat[0x019003B0 : 0x019603AF + 1]  # Extract the data for the general checksum
        new_cs = hashlib.md5(general).hexdigest()  # Recalculate the general checksum
        cur_cs = binascii.hexlify(dat[0x019003A0 : 0x019003AF + 1]).decode("utf-8")  # Convert the current general checksum to a string

        writeval = binascii.unhexlify(new_cs)  # Convert the recalculated general checksum to bytes
        dat = dat[:0x019003A0] + writeval + dat[0x019003AF + 1 :]  # Update the general checksum in the original data

        with open(file, "wb") as fh1:
            fh1.write(dat)  # Write the updated data to the file

# Function to handle button click
def activate_checksum():
    file_path = filedialog.askopenfilename(
        title="Select Save File",
        filetypes=(("ER0000", "*.sl2"), ("All Files", "*.*"))
    )
    if file_path:
        try:
            recalc_checksum(file_path)
            messagebox.showinfo("Success", "Checksum recalculated and updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    else:
        messagebox.showwarning("No File Selected", "Please select a file to recalculate checksum.")

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

def update_ng_value():
    file_path = file_path_var.get()
    section_number = current_section_var.get()
    
    if not file_path or not new_ng_var.get() or section_number == 0:
        messagebox.showerror("Input Error", "Please open a file and select a section!")
        return
    
    try:
        new_ng_value = int(new_ng_var.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid decimal number for ng+.")
        return

    section_info = SECTIONS[section_number]
    section_data = loaded_file_data[section_info['start']:section_info['end']+1]
    offset1 = find_hex_offset(section_data, hex_pattern_ng)
    
    if offset1 is not None:
        ng_offset = offset1 + ng_distance
        write_value_at_offset(file_path, section_info['start'] + ng_offset, new_ng_value)
        messagebox.showinfo("Success", f"New game + value updated to {new_ng_value}.")
    else:
        messagebox.showerror("Pattern Not Found", "Pattern not found in the selected section.")

def update_stat(stat):
    file_path = file_path_var.get()
    section_number = current_section_var.get()
    print("file_path:", file_path)
    print("section_number:", section_number)
    
    if not file_path or section_number == 0:
        messagebox.showerror("Input Error", "Please open a file and select a section!")
        return
    
    try:
        if stat == "Gender":
            selected = new_stats_vars[stat].get()
            print(f"Selected {stat}: '{selected}'")
            if selected == "":  # Check if the user left the field empty
                raise ValueError("Please select a gender")
            new_stat_value = REVERSE_GENDER_MAP[selected]
        elif stat == "Class":
            selected = new_stats_vars[stat].get()
            print(f"Selected {stat}: '{selected}'")
            if selected == "":  # Check if the user left the field empty
                raise ValueError("Please select a class")
            new_stat_value = REVERSE_CLASS_MAP[selected]
        else:
            # Get the value from the StringVar
            user_input = new_stats_vars[stat].get().strip()
            print(f"User input for {stat}: '{user_input}'")
            if user_input == "":
                raise ValueError(f"Please enter a valid value for {stat}.")
            new_stat_value = int(user_input)
            print(f"Converted {stat} value: {new_stat_value}")
    except (ValueError, KeyError) as e:
        messagebox.showerror("Invalid Input", str(e))
        return
    
    section_info = SECTIONS[section_number]
    section_data = loaded_file_data[section_info['start']:section_info['end'] + 1]
    
    offset1 = find_hex_offset(section_data, hex_pattern1_Fixed)
    if offset1 is not None:
        # Calculate the correct offset in the section
        relative_offset = calculate_offset2(offset1, stats_offsets_for_stats_tap[stat])
        # Calculate the absolute file offset
        absolute_offset = section_info['start'] + relative_offset
        
        # Debug print
        print(f"Writing {stat} = {new_stat_value} (hex: {hex(new_stat_value)}) at file offset {absolute_offset} (hex: {hex(absolute_offset)})")
        
        # For Level stat, use 2 bytes
        byte_size = 2 if stat == "Level" else 1
        write_value_at_offset(file_path, absolute_offset, new_stat_value, byte_size=byte_size)
        
        # Set displayed value based on type
        if stat == "Gender":
            current_stats_vars[stat].set(GENDER_MAP[new_stat_value])
        elif stat == "Class":
            current_stats_vars[stat].set(CLASS_MAP[new_stat_value])
        else:
            current_stats_vars[stat].set(str(new_stat_value))
        
        messagebox.showinfo("Success", f"{stat} updated to {new_stat_value}.")
    else:
        messagebox.showerror("Pattern Not Found", "Pattern not found in the file.")



def cookbooks_unlock(section_number): ##not working
    file_path = file_path_var.get()
    current_section_var.set(section_number)
    section_info = SECTIONS[section_number]
    
    with open(file_path, 'r+b') as file:
        loaded_file_data = bytearray(file.read())
        section_data = loaded_file_data[section_info['start']:section_info['end']+1]
        
        # Add new item if it doesn't exist
        empty_pattern = bytes.fromhex("80 00 00 02 00 80 20 08 02 00 80 20 00 02 00 80")
        empty_offset = section_data.find(empty_pattern)
        
        if empty_offset == -1:
            messagebox.showerror("Error", "No empty slot found to add the item in the selected section.")
            return
            
        # Calculate actual offset for empty slot
        actual_offset = section_info['start'] + empty_offset - 250

        # Create the default pattern
        cookbook_id = bytes.fromhex("80 20 08 02 00 00 20 08 02 00 80 20 08 02 00 80 20 00 00 00 00 00 00 00 00 80 20 08 02 00 00 20 08 02 00 80 20 08 02 00 00 00 00 00 00 00 00 00 00 00 80 20 08 02 00 80 20 08 02 00 80 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 20 00 02 00 80 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 02 00 80 20 08 02 00 80 20 08 02 00 80 00 00 00 00 00 00 00 00 00 80 20 08 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 20 08 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 80 20 00 00 00 00 00 00 00 00 00 00 00 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02 00 80 20 08 02")
        
        # Write the new item pattern
        file.seek(actual_offset)
        file.write(cookbook_id)
        messagebox.showinfo("Success", "All Cookbooks unlocked")

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
####

def find_steam():    
    global loaded_file_data
    file_path = file_path_var.get()
    section_number = current_section_var.get()
    section_info = SECTIONS[section_number]
    hex_pattern1_Fixed = '00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF'
    hex_pattern2_Fixed='FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF'
    hex_pattern3_Fixed='FF FF FF FF 00 00 00 00 00 00 00 00 00 01 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 01 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 01 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 01 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 01 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 01 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 01 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 01 00 00 FF FF FF FF'
    hex_pattern4_Fixed='00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
    hex_pattern5_Fixed='FF FF FF FF'
    with open(file_path, 'r+b') as file:
        loaded_file_data = bytearray(file.read())
        section_data = loaded_file_data[section_info['start']:section_info['end']+1]
        inventory_begins= find_hex_offset(section_data, hex_pattern1_Fixed)+0x310+1
        print(inventory_begins)
        magic_start=inventory_begins+0x9204
        print(magic_start)
        absolute_start = section_info['start'] + magic_start
        search_data = loaded_file_data[absolute_start:absolute_start+9000]
        unk_pattern_offset = find_hex_offset(search_data, hex_pattern2_Fixed)
        if unk_pattern_offset is None:
            print("Pattern not found in search_data.")
            return  # or handle it appropriately
        print(unk_pattern_offset+absolute_start)

        end=unk_pattern_offset+absolute_start
        search_data1 = loaded_file_data[end:end+35716]
        unk_pattern_offset1 = find_hex_offset(search_data1, hex_pattern3_Fixed)
        
        end1=unk_pattern_offset1+end
        search_data2=loaded_file_data[end1:end1+90000]
        unk_pattern_offset2 = find_hex_offset(search_data2, hex_pattern4_Fixed)
        end2=unk_pattern_offset2+end1
        search_data3=loaded_file_data[end2:end2+2927596]
        unk_pattern_offset3 = find_hex_offset(search_data3, hex_pattern5_Fixed)
        end3=unk_pattern_offset3+end2+131216
        print('s', end3)
        file.seek(end3)
        print(file.read(8))

        



####

def save_file_as():
    global loaded_file_data
    
    if loaded_file_data is None or len(loaded_file_data) == 0:
        messagebox.showerror("Error", "No data loaded to save.")
        return
    
    # Open file dialog to let user choose where to save
    file_path = filedialog.asksaveasfilename(
        defaultextension="memory.dat",
        filetypes=[("All files", "*.*")],
        title="Save File As"
    )
    
    if not file_path:  # User canceled the dialog
        return
    
    try:
        # Write the entire loaded_file_data to the selected file
        with open(file_path, 'wb') as file:
            file.write(loaded_file_data)
        
        messagebox.showinfo("Success", f"File saved successfully to:\n{file_path}")
        
        # Optionally update the current file path if you want to continue working with this file
        file_path_var.set(file_path)
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {e}")

def save_file():
    global loaded_file_data
    
    current_file_path = file_path_var.get()
    if not current_file_path:
        # If no file is currently loaded, call save_file_as instead
        return save_file_as()
    
    try:
        # Create a backup of the current file
        backup_path = current_file_path + ".bak"
        if os.path.exists(current_file_path):
            shutil.copy2(current_file_path, backup_path)
        
        # Write the entire loaded_file_data to the file
        with open(current_file_path, 'wb') as file:
            file.write(loaded_file_data)
        
        messagebox.showinfo("Success", f"File saved successfully to:\n{current_file_path}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {e}")



def increment_counterss(counter_bytes: bytes, step=2) -> bytes:
    counter = list(counter_bytes)
    carry = step
    for i in range(4):
        total = counter[i] + carry
        counter[i] = total & 0xFF
        carry = total >> 8
        if carry == 0:
            break
    return bytes(counter)
###########
def increment_countersss(counter_bytes: bytes, step=1) -> bytes: # for top section
    counter = list(counter_bytes)
    carry = step
    for i in range(4):
        total = counter[i] + carry
        counter[i] = total & 0xFF
        carry = total >> 8
        if carry == 0:
            break
    return bytes(counter)
# for the top section
def get_slot_size(b4):

    if b4 == 0xC0:
        return 12
    elif b4 == 0x90:
        return 16
    elif b4 == 0x80:
        return 21
    else:
        return None

def find_ring_items(section_data, absolute_offset_start, limit=37310):
    found_ring = []

    # Limit section data to the defined range
    section_data = section_data[:limit]

    for ring_name, ring_hex in item_hex_patterns.items():
        ring_bytes = bytes.fromhex(ring_hex)
        search_pos = 0

        while search_pos < len(section_data):
            idx = section_data.find(ring_bytes, search_pos)
            if idx == -1:
                break

            quantity_offset = idx + len(ring_bytes)
            if quantity_offset < len(section_data):
                quantity = section_data[quantity_offset]
                found_ring.append((ring_name, quantity, absolute_offset_start + idx))

            search_pos = idx + 1  # Move forward

    return found_ring

def refresh_ring_list(file_path):
    global loaded_file_data
    section_number = current_section_var.get()
    
    if not file_path or section_number == 0:
        messagebox.showerror("Error", "No file selected or section not chosen. Please load a file and select a slot.")
        return

    section_info = SECTIONS[section_number]

    # Ensure bytearray
    if isinstance(loaded_file_data, bytes):
        loaded_file_data = bytearray(loaded_file_data)

    # Extract section data
    section_data = loaded_file_data[section_info['start']:section_info['end'] + 1]

    # Find fixed pattern
    fixed_pattern_offset = find_hex_offset(section_data, hex_pattern1_Fixed)
    if fixed_pattern_offset is None:
        messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
        return

    fixed_pattern_offset_start = fixed_pattern_offset
    search_start_position = fixed_pattern_offset_start + len(hex_pattern1_Fixed) + 1000

    if search_start_position >= len(section_data):
        print("Search start position beyond section data.")
        return

    fixed_pattern_offset_end = find_hex_offset(section_data[search_start_position:], hex_pattern_end)
    if fixed_pattern_offset_end is not None:
        fixed_pattern_offset_end += search_start_position
    else:
        print("End pattern not found")
        return

    # Define absolute search start and limit
    absolute_start = section_info['start'] + fixed_pattern_offset_start
    search_data = loaded_file_data[absolute_start:absolute_start + 37310]

    updated_rings = find_ring_items(search_data, absolute_start, limit=37310)

    # Clear UI
    for widget in ring_list_frame.winfo_children():
        widget.destroy()

    if updated_rings:
        # Create scrollable UI
        ring_list_canvas = tk.Canvas(ring_list_frame)
        ring_list_scrollbar = Scrollbar(ring_list_frame, orient="vertical", command=ring_list_canvas.yview)
        ring_list_frame_inner = ttk.Frame(ring_list_canvas)

        ring_list_frame_inner.bind(
            "<Configure>",
            lambda e: ring_list_canvas.configure(scrollregion=ring_list_canvas.bbox("all"))
        )

        ring_list_canvas.create_window((0, 0), window=ring_list_frame_inner, anchor="nw")
        ring_list_canvas.configure(yscrollcommand=ring_list_scrollbar.set)

        ring_list_canvas.pack(side="left", fill="both", expand=True)
        ring_list_scrollbar.pack(side="right", fill="y")

        # Populate ring items
        for ring_name, quantity, offset in updated_rings:
            ring_frame = ttk.Frame(ring_list_frame_inner)
            ring_frame.pack(fill="x", padx=10, pady=5)

            ring_label = tk.Label(ring_frame, text=f"{ring_name} (Quantity: {quantity})", anchor="w")
            ring_label.pack(side="left", fill="x", padx=5)

            delete_button = ttk.Button(ring_frame, text="Delete", command=lambda o=offset: choose_ring_delete(o))
            delete_button.pack(side="right", padx=5)
    else:
        messagebox.showinfo("Info", "No item found.")


def choose_ring_delete(offset):
    global loaded_file_data
    current_file_path = file_path_var.get()
    if not loaded_file_data:
        messagebox.showerror("Error", "No file loaded.")
        return

    try:

        for i in range(12):
            loaded_file_data[offset + i] = 0x00

        # Refresh the ring list to reflect changes
        refresh_ring_list(current_file_path)

        # Optionally notify user
        print(f"Deleted ring at offset {offset:X}")
        with open(current_file_path, 'wb') as f:
            f.write(loaded_file_data)
        messagebox.showinfo("Success", "Item deleted successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete ring: {e}")

#Talismans list
def find_talisman_items(file_path, pattern_offset_start, pattern_offset_end):

    global found_talisman
    found_talisman =[]
    pattern_offset_start = pattern_offset_start + 520
    pattern_offset_end = pattern_offset_end - 100

    
    
    with open(file_path, 'rb') as file:
        # Load section
        file.seek(pattern_offset_start)
        section_data = file.read(pattern_offset_end - pattern_offset_start)
        for ring_name, ring_hex in talisman_item_patterns.items():
            ring_bytes = bytes.fromhex(ring_hex)
            ring_bytes = ring_bytes[:3] + b'\xA0' + ring_bytes[4:]

            idx = section_data.find(ring_bytes)
            if idx != -1:
                # Assuming quantity is stored right after the ring ID in little-endian format
                quantity_offset = idx + len(ring_bytes)
                quantity = find_value_at_offset(file_path, quantity_offset, byte_size=1)
                found_talisman.append((ring_name, quantity))
    return found_talisman

def refresh_talisman_list(file_path):
    global loaded_file_data
    # Find rings in the save file
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
    
    fixed_pattern_offset_start= fixed_pattern_offset
    search_start_position = fixed_pattern_offset_start + len(hex_pattern1_Fixed) + 1000
    fixed_pattern_offset_end = find_hex_offset(section_data[search_start_position:], hex_pattern_end)
    if fixed_pattern_offset_end is not None:
        fixed_pattern_offset_end += search_start_position
    else:
        # Handle case where end pattern isn't found
        print("End pattern not found")
        return
    if search_start_position >= len(section_data):
        print("Search start position beyond section data.")
        return
    if fixed_pattern_offset is None:
        messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
        return
    updated_talisman = find_talisman_items(file_path,section_info['start'] + fixed_pattern_offset_start, section_info['start'] + fixed_pattern_offset_start + 37310)
    
    # Clear the previous list and display the updated rings
    for widget in talisman_list_frame.winfo_children():
        widget.destroy()

    if updated_talisman:
        # Create a canvas and scrollbar to contain the rings
        talisman_list_canvas = tk.Canvas(talisman_list_frame)
        talisman_list_scrollbar = Scrollbar(talisman_list_frame, orient="vertical", command=talisman_list_canvas.yview)
        talisman_list_frame_inner = ttk.Frame(talisman_list_canvas)

        talisman_list_frame_inner.bind(
            "<Configure>",
            lambda e: talisman_list_canvas.configure(
                scrollregion=talisman_list_canvas.bbox("all")
            )
        )

        talisman_list_canvas.create_window((0, 0), window=talisman_list_frame_inner, anchor="nw")
        talisman_list_canvas.configure(yscrollcommand=talisman_list_scrollbar.set)

        talisman_list_canvas.pack(side="left", fill="both", expand=True)
        talisman_list_scrollbar.pack(side="right", fill="y")

        # Add rings to the inner frame
        for talisman_name, quantity in updated_talisman:
            talisman_frame = ttk.Frame(talisman_list_frame_inner)
            talisman_frame.pack(fill="x", padx=10, pady=5)

            talisman_label = tk.Label(talisman_frame, text=f"{talisman_name} (Quantity: {quantity})", anchor="w")
            talisman_label.pack(side="left", fill="x", padx=5)

    else:
        messagebox.showinfo("Info", "No rings found.")
### Weapons list
def find_weapon_items(file_path, pattern_offset_start, pattern_offset_end):
    global found_weapon
    found_weapon = []

    # Adjust offsets
    pattern_offset_start += 30
    pattern_offset_end -= 100

    # Validate read range
    if pattern_offset_end <= pattern_offset_start:
        print(f"Invalid read range: start={pattern_offset_start}, end={pattern_offset_end}")
        return []

    with open(file_path, 'rb') as file:
        file.seek(pattern_offset_start)
        section_data = file.read(pattern_offset_end - pattern_offset_start)

        for ring_name, ring_hex in weapon_item_patterns.items():
            ring_bytes = bytes.fromhex(ring_hex)
            idx = section_data.find(ring_bytes)
            if idx != -1:
                quantity_offset = pattern_offset_start + idx + len(ring_bytes)
                quantity = find_value_at_offset(file_path, quantity_offset, byte_size=1)
                found_weapon.append((ring_name, quantity))

    return found_weapon

def refresh_weapon_list(file_path):
    global loaded_file_data
    # Find rings in the save file
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
    

    name_offset = fixed_pattern_offset + possible_name_distances_for_name_tap[0]
    updated_weapon = find_weapon_items(file_path,section_info['start'] + 10, section_info['start'] + name_offset)
    
    # Clear the previous list and display the updated rings
    for widget in weapons_list_frame.winfo_children():
        widget.destroy()

    if updated_weapon:
        # Create a canvas and scrollbar to contain the rings
        weapon_list_canvas = tk.Canvas(weapons_list_frame)
        weapon_list_scrollbar = Scrollbar(weapons_list_frame, orient="vertical", command=weapon_list_canvas.yview)
        weapon_list_frame_inner = ttk.Frame(weapon_list_canvas)

        weapon_list_frame_inner.bind(
            "<Configure>",
            lambda e: weapon_list_canvas.configure(
                scrollregion=weapon_list_canvas.bbox("all")
            )
        )

        weapon_list_canvas.create_window((0, 0), window=weapon_list_frame_inner, anchor="nw")
        weapon_list_canvas.configure(yscrollcommand=weapon_list_scrollbar.set)

        weapon_list_canvas.pack(side="left", fill="both", expand=True)
        weapon_list_scrollbar.pack(side="right", fill="y")

        # Add rings to the inner frame
        for weapon_name, quantity in updated_weapon:
            weapon_frame = ttk.Frame(weapon_list_frame_inner)
            weapon_frame.pack(fill="x", padx=10, pady=5)

            weapon_label = tk.Label(weapon_frame, text=f"{weapon_name} (Quantity: {quantity})", anchor="w")
            weapon_label.pack(side="left", fill="x", padx=5)

    else:
        messagebox.showinfo("Info", "No rings found.")
##ARMOR ilst

def find_armor_items(file_path, pattern_offset_start, pattern_offset_end):
    global found_armor
    found_armor = []

    # Adjust offsets
    pattern_offset_start += 30
    pattern_offset_end -= 100

    # Validate read range
    if pattern_offset_end <= pattern_offset_start:
        print(f"Invalid read range: start={pattern_offset_start}, end={pattern_offset_end}")
        return []

    with open(file_path, 'rb') as file:
        file.seek(pattern_offset_start)
        section_data = file.read(pattern_offset_end - pattern_offset_start)

        for ring_name, ring_hex in armor_item_patterns.items():
            ring_bytes = bytes.fromhex(ring_hex)
            idx = section_data.find(ring_bytes)
            if idx != -1:
                quantity_offset = pattern_offset_start + idx + len(ring_bytes)
                quantity = find_value_at_offset(file_path, quantity_offset, byte_size=1)
                found_armor.append((ring_name, quantity))

    return found_armor

def refresh_armor_list(file_path):
    global loaded_file_data
    # Find rings in the save file
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
    

    name_offset = fixed_pattern_offset + possible_name_distances_for_name_tap[0]
    updated_armor = find_armor_items(file_path,section_info['start'] + 10, section_info['start'] + name_offset)
    
    # Clear the previous list and display the updated rings
    for widget in armor_list_frame.winfo_children():
        widget.destroy()

    if updated_armor:
        # Create a canvas and scrollbar to contain the rings
        armor_list_canvas = tk.Canvas(armor_list_frame)
        armor_list_scrollbar = Scrollbar(armor_list_frame, orient="vertical", command=armor_list_canvas.yview)
        armor_list_frame_inner = ttk.Frame(armor_list_canvas)

        armor_list_frame_inner.bind(
            "<Configure>",
            lambda e: armor_list_canvas.configure(
                scrollregion=armor_list_canvas.bbox("all")
            )
        )

        armor_list_canvas.create_window((0, 0), window=armor_list_frame_inner, anchor="nw")
        armor_list_canvas.configure(yscrollcommand=armor_list_scrollbar.set)

        armor_list_canvas.pack(side="left", fill="both", expand=True)
        armor_list_scrollbar.pack(side="right", fill="y")

        # Add rings to the inner frame
        for armor_name, quantity in updated_armor:
            armor_frame = ttk.Frame(armor_list_frame_inner)
            armor_frame.pack(fill="x", padx=10, pady=5)

            armor_label = tk.Label(armor_frame, text=f"{armor_name} (Quantity: {quantity})", anchor="w")
            armor_label.pack(side="left", fill="x", padx=5)

    else:
        messagebox.showinfo("Info", "No rings found.")

##AOW
def find_aow_items(file_path, pattern_offset_start, pattern_offset_end):
    global found_aow
    found_aow = []

    # Adjust offsets
    pattern_offset_start += 30
    pattern_offset_end -= 100

    # Validate read range
    if pattern_offset_end <= pattern_offset_start:
        print(f"Invalid read range: start={pattern_offset_start}, end={pattern_offset_end}")
        return []

    with open(file_path, 'rb') as file:
        file.seek(pattern_offset_start)
        section_data = file.read(pattern_offset_end - pattern_offset_start)

        for ring_name, ring_hex in aow_item_patterns.items():
            ring_bytes = bytes.fromhex(ring_hex)
            idx = section_data.find(ring_bytes)
            if idx != -1:
                quantity_offset = pattern_offset_start + idx + len(ring_bytes)
                quantity = find_value_at_offset(file_path, quantity_offset, byte_size=1)
                found_aow.append((ring_name, quantity))

    return found_aow

def refresh_aow_list(file_path):
    global loaded_file_data
    # Find rings in the save file
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
    

    name_offset = fixed_pattern_offset + possible_name_distances_for_name_tap[0]
    updated_aow = find_aow_items(file_path,section_info['start'] + 10, section_info['start'] + name_offset)
    
    # Clear the previous list and display the updated rings
    for widget in aow_list_frame.winfo_children():
        widget.destroy()

    if updated_aow:
        # Create a canvas and scrollbar to contain the rings
        aow_list_canvas = tk.Canvas(aow_list_frame)
        aow_list_scrollbar = Scrollbar(aow_list_frame, orient="vertical", command=aow_list_canvas.yview)
        aow_list_frame_inner = ttk.Frame(aow_list_canvas)

        aow_list_frame_inner.bind(
            "<Configure>",
            lambda e: aow_list_canvas.configure(
                scrollregion=aow_list_canvas.bbox("all")
            )
        )

        aow_list_canvas.create_window((0, 0), window=aow_list_frame_inner, anchor="nw")
        aow_list_canvas.configure(yscrollcommand=aow_list_scrollbar.set)

        aow_list_canvas.pack(side="left", fill="both", expand=True)
        aow_list_scrollbar.pack(side="right", fill="y")

        # Add rings to the inner frame
        for aow_name, quantity in updated_aow:
            aow_frame = ttk.Frame(aow_list_frame_inner)
            aow_frame.pack(fill="x", padx=10, pady=5)

            aow_label = tk.Label(aow_frame, text=f"{aow_name} (Quantity: {quantity})", anchor="w")
            aow_label.pack(side="left", fill="x", padx=5)

    else:
        messagebox.showinfo("Info", "No rings found.")
# in the inventory       
def empty_slot_finder(default_pattern, file_path, pattern_offset_start, pattern_offset_end, quantity):
    with open(file_path, 'r+b') as file:
        slot_size = 12
        item_count = quantity
        valid_b4_values = {0x80, 0x90, 0xC0}
        pattern_offset_start = pattern_offset_start + 520
        pattern_offset_end = pattern_offset_end - 100

        # Load section
        file.seek(pattern_offset_start)
        section_data = file.read(pattern_offset_end - pattern_offset_start)
        print(f"[DEBUG] Loaded section of {len(section_data)} bytes.")

        def is_valid(slot):
            if len(slot) != slot_size:
                return False
            b3, b4 = slot[2], slot[3]
            return b4 == 0xB0 or (b3 == 0x80 and b4 in valid_b4_values) or b4 == 0xA0 #talisman

        # STEP 1: Find alignment point by scanning for one valid slot (simplified)
        start_offset = None
        for i in range(0, len(section_data) - slot_size):
            # Try alignment at current position
            slot1 = section_data[i:i + slot_size]

            if is_valid(slot1):
                start_offset = i
                print(f"[DEBUG] Found alignment at offset {i}")
                break
            
            # Also try alignment offset by 4 bytes (in case there's a 4-byte counter before slots)
            if i + 4 < len(section_data) - slot_size:
                slot1_alt = section_data[i + 4:i + 4 + slot_size]
                
                if is_valid(slot1_alt):
                    start_offset = i + 4
                    print(f"[DEBUG] Found alignment at offset {i + 4} (adjusted for 4-byte counter)")
                    break

        if start_offset is None:
            print("[ERROR] No valid slot alignment found.")
            return

        # STEP 2: Process all slots from alignment with realignment on invalid slots
        valid_slot_count = 0
        empty_slot_count = 0
        invalid_slot_count = 0
        highest_counter = b'\x00\x00\x00\x00'

        def find_next_alignment(data, start_pos):
            """Find the next alignment point starting from start_pos - only needs 1 valid slot"""
            for i in range(start_pos, len(data) - slot_size):
                slot = data[i:i + slot_size]
                
                if is_valid(slot):
                    print(f"[DEBUG] Found new alignment at offset {i}")
                    return i
            return None

        current_offset = start_offset
        
        while current_offset < len(section_data):
            slot = section_data[current_offset:current_offset + slot_size]
            if len(slot) < slot_size:
                print(f"[DEBUG] Reached end of section at offset {current_offset}")
                break

            b3, b4 = slot[2], slot[3]
            
            # Check if this is an empty slot (first 8 bytes are zero, indicating no item data)
            if slot[:8] == b'\x00' * 8:
                # Empty slot
                empty_slot_count += 1
                print(f"[DEBUG] Empty slot at offset {current_offset}")
                current_offset += slot_size
            elif b4 == 0xB0 or (b3 == 0x80 and b4 in valid_b4_values) or b4 == 0xA0: #talisman
                # Valid slot
                valid_slot_count += 1
                counter = slot[8:12]
                
                # Fixed comparison: proper bytes comparison
                if int.from_bytes(counter, byteorder='little') > int.from_bytes(highest_counter, byteorder='little'):
                    highest_counter = counter
                    print(f"[DEBUG] New highest counter found: {highest_counter.hex()}")
                current_offset += slot_size
            else:
                # Invalid slot - find new alignment point
                invalid_slot_count += 1
                print(f"[DEBUG] Invalid slot at offset {current_offset} - searching for new alignment")
                
                # Search for next alignment starting from current position + 1
                new_alignment = find_next_alignment(section_data, current_offset + 1)
                
                if new_alignment is not None:
                    current_offset = new_alignment
                    print(f"[DEBUG] Continuing from new alignment at offset {current_offset}")
                else:
                    print(f"[DEBUG] No more valid alignment found, ending search")
                    break

        updated_section = bytearray(section_data)

        # STEP 4: Write new entry in the first empty slot found after alignment
        new_counter = increment_counterss(highest_counter)
        print(f"[DEBUG] Highest counter: {highest_counter.hex()}, New counter: {new_counter.hex()}")
        
        new_entry = default_pattern + item_count.to_bytes(4, 'little') + new_counter

        for i in range(start_offset, len(updated_section), slot_size):
            if updated_section[i:i + slot_size] == b'\x00' * slot_size:
                absolute_position = pattern_offset_start + i
                file.seek(absolute_position)
                file.write(new_entry)
                print(f"[INFO] Wrote new entry at offset {hex(absolute_position)}")
                break

        print(f"[SUMMARY] Valid slots found: {valid_slot_count}, Empty slots found: {empty_slot_count}, Invalid slots found: {invalid_slot_count}")
        print(f"[SUMMARY] Highest counter: {highest_counter.hex()}, New counter used: {new_counter.hex()}")
        return new_entry, absolute_position




## ADD items
def find_and_replace_pattern_with_item_and_update_counters(item_name, quantity):
    global loaded_file_data, cached_counter_results_in  # Add this to ensure we can modify the global variable
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
        
        fixed_pattern_offset_start= fixed_pattern_offset
        search_start_position = fixed_pattern_offset_start + len(hex_pattern1_Fixed) + 1000
        fixed_pattern_offset_end = find_hex_offset(section_data[search_start_position:], hex_pattern_end)
        if fixed_pattern_offset_end is not None:
            fixed_pattern_offset_end += search_start_position
        else:
            # Handle case where end pattern isn't found
            print("End pattern not found")
            return
        if search_start_position >= len(section_data):
            print("Search start position beyond section data.")
            return
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

            ## NEW FUNCTION
            default_pattern = bytearray.fromhex("A4 06 00 B0")
            default_pattern[:len(item_id_bytes[:4])] = item_id_bytes[:4]  # Safely copy bytes
            empty_slot_finder(default_pattern, file_path, section_info['start'] + fixed_pattern_offset_start, section_info['start'] + fixed_pattern_offset_start + 37310, quantity)


            # Increment counters because a new item was added
            increment_counters(file, section_info['start'] + fixed_pattern_offset)

            messagebox.showinfo("Success", 
                f"Added '{item_name}' with quantity {quantity} to section {section_number}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to add or update item: {e}")

##STACK items
def find_and_replace_pattern_with_item_and_update_counters_stack(item_name, quantity):
    global loaded_file_data, cached_counter_results_in  # Add this to ensure we can modify the global variable
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

        max_quantity = 16777215
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
        # Locate Fixed Pattern 1
        fixed_pattern_offset = find_hex_offset(section_data, hex_pattern1_Fixed)
        
        fixed_pattern_offset_start= fixed_pattern_offset
        search_start_position = fixed_pattern_offset_start + len(hex_pattern1_Fixed) + 1000
        fixed_pattern_offset_end = find_hex_offset(section_data[search_start_position:], hex_pattern_end)
        if fixed_pattern_offset_end is not None:
            fixed_pattern_offset_end += search_start_position
        else:
            # Handle case where end pattern isn't found
            print("End pattern not found")
            return
        if search_start_position >= len(section_data):
            print("Search start position beyond section data.")
            return
        if fixed_pattern_offset is None:
            messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
            return

        with open(file_path, 'r+b') as file:
            loaded_file_data = bytearray(file.read())
            default_pattern = bytearray.fromhex("A4 06 00 B0")
            default_pattern[:len(item_id_bytes[:4])] = item_id_bytes[:4]  # Safely copy bytes
            empty_slot_finder(default_pattern, file_path, section_info['start'] + fixed_pattern_offset_start, section_info['start'] + fixed_pattern_offset_start+ 37310, quantity)

            # Increment counters because a new item was added
            increment_counters(file, section_info['start'] + fixed_pattern_offset)

            messagebox.showinfo("Success", 
                f"Added '{item_name}' with quantity {quantity} to section {section_number}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to add or update item: {e}")


##Talisman
def find_and_replace_pattern_with_talisman_and_update_counters(item_name):
    global loaded_file_data, cached_counter_results_in  # Add this to ensure we can modify the global variable
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
        with open(file_path, 'rb') as file:
            loaded_file_data = bytearray(file.read())
        
        # Convert loaded_file_data to bytearray if it's not already
        if isinstance(loaded_file_data, bytes):
            loaded_file_data = bytearray(loaded_file_data)
        
        # Get current section data from loaded_file_data
        section_data = loaded_file_data[section_info['start']:section_info['end']+1]

        fixed_pattern_offset = find_hex_offset(section_data, hex_pattern1_Fixed)
        
        fixed_pattern_offset_start= fixed_pattern_offset
        search_start_position = fixed_pattern_offset_start + len(hex_pattern1_Fixed) + 1000
        fixed_pattern_offset_end = find_hex_offset(section_data[search_start_position:], hex_pattern_end)
        if fixed_pattern_offset_end is not None:
            fixed_pattern_offset_end += search_start_position
        else:
            # Handle case where end pattern isn't found
            print("End pattern not found")
            return
        if search_start_position >= len(section_data):
            print("Search start position beyond section data.")
            return
        if fixed_pattern_offset is None:
            messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
            return

        with open(file_path, 'r+b') as file:
            loaded_file_data = bytearray(file.read())
            # Create the default pattern
            default_pattern = bytearray.fromhex("B2 1B 00 A0")
            default_pattern[:2] = item_id_bytes[:2]  # First 2 bytes from the item ID
            empty_slot_finder(default_pattern, file_path, section_info['start'] + fixed_pattern_offset_start, section_info['start'] + fixed_pattern_offset_start+ 37310, 1)
            # Increment counters because a new item was added
            increment_counters(file, section_info['start'] + fixed_pattern_offset)

        with open(file_path, 'rb') as file:
            loaded_file_data = bytearray(file.read())
        return True

    except Exception as e:
        messagebox.showerror("Error", f"Failed to add or update item: {e}")


def empty_slot_finder_aow(default_pattern, file_path, pattern_offset_start, pattern_offset_end):
    def get_slot_size(b4):
        if b4 == 0xC0:
            return 8
        elif b4 == 0x90:
            return 16
        elif b4 == 0x80:
            return 21
        else:
            return None
    with open(file_path, 'r+b') as file:
        valid_b4_values = {0x80, 0x90, 0xC0}

        # Load section
        file.seek(pattern_offset_start)
        section_data = file.read(pattern_offset_end - pattern_offset_start)
        print(f"[DEBUG] Loaded section of {len(section_data)} bytes.")

        # STEP 1: Find alignment point by scanning for valid slots
        # We need a more flexible approach since slots can have different sizes
        def is_valid_slot_start(pos):
            """Check if position could be the start of a valid slot"""
            if pos + 4 > len(section_data):  # Need at least 4 bytes
                return False, None
            
            b3, b4 = section_data[pos+2], section_data[pos+3]
            if b3 == 0x80 and b4 in valid_b4_values:
                slot_size = get_slot_size(b4)
                if slot_size and pos + slot_size <= len(section_data):
                    return True, slot_size
            return False, None
        
        # Find the first valid slot
        start_offset = None
        for i in range(0, len(section_data) - 8):  # At least 8 bytes for empty slot check
            valid, first_slot_size = is_valid_slot_start(i)
            if valid:
                # Check if the next position after this slot also starts a valid slot
                next_pos = i + first_slot_size
                valid_next, _ = is_valid_slot_start(next_pos)
                
                # Or check if it's an empty slot (which is also valid)
                is_empty_next = (next_pos + 8 <= len(section_data) and 
                                 section_data[next_pos:next_pos+8] == b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF')
                
                if valid_next or is_empty_next:
                    start_offset = i
                    print(f"[DEBUG] Found valid slot alignment at offset {i}")
                    break
        
        if start_offset is None:
            print("[ERROR] No valid slot alignment found.")
            return

        # STEP 2: Process all slots from alignment with variable slot sizes
        valid_slot_count = 0
        empty_slot_count = 0
        highest_counter = b'\x00\x00'
        
        # Process slots with variable sizes
        i = start_offset
        while i < len(section_data):
            # First check if this is an empty slot (8 bytes pattern)
            if i + 8 <= len(section_data) and section_data[i:i+8] == b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF':
                empty_slot_count += 1
                # Empty slots are always considered to be 8 bytes
                i += 8
                continue
            
            # Check if this is a valid slot
            if i + 4 <= len(section_data):
                b3, b4 = section_data[i+2], section_data[i+3]
                
                if b3 == 0x80 and b4 in valid_b4_values:
                    slot_size = get_slot_size(b4)
                    
                    if slot_size and i + slot_size <= len(section_data):
                        valid_slot_count += 1
                        counter = section_data[i:i+2]  # First 2 bytes are the counter
                        
                        # Compare counters as integers
                        if int.from_bytes(counter, byteorder='little') > int.from_bytes(highest_counter, byteorder='little'):
                            highest_counter = counter
                            print(f"[DEBUG] New highest counter found: {highest_counter.hex()}")
                        
                        i += slot_size  # Move to next slot
                        continue
            
            # If we reach here, this position doesn't match any known pattern
            # Try the next byte position
            i += 1

        # STEP 3: Write new entry in the first empty slot found after alignment
        new_counter = increment_countersss(highest_counter)
        print(f"[DEBUG] Highest counter: {highest_counter.hex()}, New counter: {new_counter.hex()}")
        
        print(f"[DEBUG] Default pattern: {default_pattern.hex()}")
        print(f"[DEBUG] New counter: {new_counter.hex()}")

        # Modify entry creation to be more explicit
        if len(default_pattern) >= 2:
            # Create new entry by explicitly slicing and combining
            new_entry = new_counter + default_pattern[2:]
            print(f"[DEBUG] New entry: {new_entry.hex()}")
        else:
            print("[ERROR] Default pattern is too short.")
            return

        # Extract b4 value from default pattern to determine its size
        if len(default_pattern) >= 4:
            new_entry_b4 = default_pattern[3]
            new_entry_size = get_slot_size(new_entry_b4)
            if not new_entry_size:
                print(f"[ERROR] Invalid b4 value in default pattern: {hex(new_entry_b4)}")
                return
            
            if len(new_entry) < new_entry_size:
                print(f"[ERROR] Default pattern is too short ({len(new_entry)} bytes) for slot size {new_entry_size}")
                return
        else:
            print("[ERROR] Default pattern too short to determine slot type.")
            return
            
        print(f"[DEBUG] New entry has b4={hex(new_entry_b4)}, requiring {new_entry_size} bytes slot")

        # Find the first empty slot and insert the new entry
        file.seek(pattern_offset_start)
        mod_section_data = file.read((pattern_offset_end-40163) - pattern_offset_start)
        found_empty = False
        empty_slot_position = None
        i = start_offset
        while i < len(mod_section_data):
            # Check for empty slot pattern
            if i + 8 <= len(mod_section_data) and mod_section_data[i:i+8] == b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF':
                empty_slot_position = i
                print(f"[DEBUG] Found empty slot at relative offset {i}")
                found_empty = True
                break
            
            # Move to next slot by determining its size
            if i + 4 <= len(mod_section_data):
                b3, b4 = mod_section_data[i+2], mod_section_data[i+3]
                if b3 == 0x80 and b4 in valid_b4_values:
                    slot_size = get_slot_size(b4)
                    if slot_size:
                        i += slot_size
                        continue
            
            # Move one byte at a time if not at a valid slot
            i += 1
                
        if not found_empty:
            print("[ERROR] No empty slots found to write new entry.")
            return
            

        
        # Step 1: Insert the new entry
        insertion_position =  empty_slot_position+ pattern_offset_start
        
        file.seek(insertion_position)
        file.write(new_entry)
        return new_counter
## AOW add
def find_and_replace_pattern_with_aow_and_update_counters(item_name):
    global loaded_file_data, cached_counter_results_in# Add this to ensure we can modify the global variable
    try:
        # Validate item name and fetch its ID
        item_id = inventory_aow_hex_patterns.get(item_name)
        if not item_id:
            messagebox.showerror("Error", f"Item '{item_name}' not found in aow.json.")
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
        
        fixed_pattern_offset_start= fixed_pattern_offset
        search_start_position = fixed_pattern_offset_start + len(hex_pattern1_Fixed) + 1000
        fixed_pattern_offset_end = find_hex_offset(section_data[search_start_position:], hex_pattern_end)
        if fixed_pattern_offset_end is not None:
            fixed_pattern_offset_end += search_start_position
        else:
            # Handle case where end pattern isn't found
            print("End pattern not found")
            return
        if search_start_position >= len(section_data):
            print("Search start position beyond section data.")
            return
        if fixed_pattern_offset is None:
            messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
            return

        with open(file_path, 'r+b') as file:
            loaded_file_data = bytearray(file.read())
            

            # Create the default pattern
            default_pattern = bytearray.fromhex("D0 04 80 C0 30 75 00 80")
            default_pattern[4:8] = item_id_bytes  # Replace all 4 bytes of the item ID
            

            file.seek(0)  
            entire_file = bytearray(file.read())  # Get updated file content
            section_data = entire_file[section_info['start']:section_info['end'] + 1]
            fixed_pattern_offset_top = find_hex_offset(section_data, hex_pattern1_Fixed)
            new_counter = empty_slot_finder_aow(default_pattern, file_path, section_info['start'] + 32, section_info['start'] + fixed_pattern_offset_top - 431)
            

            #in the inevmentory######################

            # Create the default pattern
            default_pattern_inven = bytearray.fromhex("D0 12 80 C0")
            default_pattern_inven = new_counter + default_pattern_inven[2:]
            empty_slot_finder(default_pattern_inven, file_path, section_info['start'] + fixed_pattern_offset_start, section_info['start'] + fixed_pattern_offset_start+ 37310, 1)

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
        "Base Game": list(inventory_talisman_hex_patterns.items())[:114],
        "DLC": list(inventory_talisman_hex_patterns.items())[114:155],
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



##AOW
def show_aow_list_bulk():
    aow_window = tk.Toplevel(window)
    aow_window.title("Add or Update Items by Category")
    aow_window.geometry("600x600")
    aow_window.attributes("-topmost", True)
    aow_window.focus_force()

    # Define categories
    categories = {
        "Base Game": list(inventory_aow_hex_patterns.items())[:115],
        "DLC": list(inventory_aow_hex_patterns.items())[115:155],
    }

    # Store the selected categories
    selected_categories = {category: tk.BooleanVar() for category in categories}

    # Create category selection section
    category_frame = ttk.Frame(aow_window)
    category_frame.pack(fill="x", padx=10, pady=10)
    tk.Label(category_frame, text="Select Categories to Add:").pack(anchor="w")
    for category, var in selected_categories.items():
        ttk.Checkbutton(
            category_frame,
            text=category,
            variable=var
        ).pack(anchor="w")

    # Action frame
    action_frame = ttk.Frame(aow_window)
    action_frame.pack(fill="x", padx=10, pady=10)

    def add_selected_items():
        success_items = []
        error_items = []

        # Loop through selected categories and process items
        for category, items in categories.items():
            if selected_categories[category].get():  # Check if category is selected
                for item_name, item_id in items:
                    try:
                        find_and_replace_pattern_with_aow_and_update_counters(item_name)
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
        command=aow_window.destroy
    ).pack(fill="x", padx=5, pady=5)

def add_item_from_aow(item_name, item_id, parent_window):
    
    find_and_replace_pattern_with_aow_and_update_counters(item_name)

def show_aow_list():
    
    aow_window = tk.Toplevel(window)
    aow_window.title("Add Items")
    aow_window.geometry("600x400")
    aow_window.attributes("-topmost", True)  # Keeps the window on top
    aow_window.focus_force()  # Brings the window into focus

    # Search bar for filtering items
    search_frame = ttk.Frame(aow_window)
    search_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Create a scrollable frame for the item list
    canvas = tk.Canvas(aow_window)
    scrollbar = ttk.Scrollbar(aow_window, orient="vertical", command=canvas.yview)
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
        filtered_items = {k: v for k, v in inventory_aow_hex_patterns.items() if search_term in k.lower()}

        for item_name, item_id in filtered_items.items():
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill="x", padx=5, pady=2)

            # Display item name
            tk.Label(item_frame, text=item_name, anchor="w").pack(side="left", fill="x", expand=True)

            # "Add/Update" button for each item
            add_button = ttk.Button(
                item_frame,
                text="Add",
                command=lambda name=item_name, hex_id=item_id: add_item_from_aow(name, hex_id, aow_window)
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
        "Base Game/ DLC": list(inventory_goods_magic_hex_patterns.items())[:227],
        
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


def add_item_from_goods_magic_stack(item_name, item_id, parent_window):
    
    # Use the parent window to keep the input dialog on top
    quantity = simpledialog.askinteger(
        "Input Quantity",
        f"Enter the quantity for {item_name} (1-16777215):",
        minvalue=1,
        maxvalue=16777215,
        parent=parent_window  # Attach the dialog to the "Add Items" list window
    )

    # Proceed to add the item if quantity is specified
    if quantity is not None:
        find_and_replace_pattern_with_item_and_update_counters_stack(item_name, quantity)

ITEMS_PER_BATCH = 50

def show_goods_magic_list():
    goods_magic_window = tk.Toplevel()
    goods_magic_window.title("Add or Update Items")
    goods_magic_window.geometry("600x400")
    goods_magic_window.attributes("-topmost", True)
    goods_magic_window.focus_force()

    # Search bar for filtering items
    search_frame = ttk.Frame(goods_magic_window)
    search_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Scrollable frame for item list
    canvas = tk.Canvas(goods_magic_window)
    scrollbar = ttk.Scrollbar(goods_magic_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    loaded_items = []
    all_items = list(inventory_goods_magic_hex_patterns.items())  # Convert dict to list
    start_index = 0

    def load_more_items():
        """Loads the next batch of items into the list."""
        nonlocal start_index
        end_index = start_index + ITEMS_PER_BATCH
        for item_name, item_id in all_items[start_index:end_index]:
            if item_name not in loaded_items:  # Prevent duplicate loading
                item_frame = ttk.Frame(scrollable_frame)
                item_frame.pack(fill="x", padx=5, pady=2)

                tk.Label(item_frame, text=item_name, anchor="w").pack(side="left", fill="x", expand=True)

                add_button = ttk.Button(
                    item_frame,
                    text="Add/Update",
                    command=lambda name=item_name, hex_id=item_id: add_item_from_goods_magic(name, hex_id, goods_magic_window)
                )
                add_button.pack(side="right", padx=5)
                loaded_items.append(item_name)

        start_index = end_index  # Update index for next batch

    def on_scroll(event):
        """Detects when user scrolls near the bottom and loads more items."""
        if canvas.yview()[1] >= 0.9:  # If near the bottom, load more
            load_more_items()

    def filter_items():
        """Filters items based on the search term."""
        nonlocal all_items, start_index, loaded_items
        search_term = search_var.get().lower()

        # Reset loaded items
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        if search_term:
            all_items = [(k, v) for k, v in inventory_goods_magic_hex_patterns.items() if search_term in k.lower()]
        else:
            all_items = list(inventory_goods_magic_hex_patterns.items())

        start_index = 0
        loaded_items.clear()
        load_more_items()

    # Bind search input to filtering function
    search_entry.bind("<KeyRelease>", lambda event: filter_items())

    # Bind scrolling to load more items
    canvas.bind("<Configure>", lambda e: load_more_items())  # Load initial batch
    canvas.bind_all("<MouseWheel>", lambda event: on_scroll(event))

    load_more_items()  # Load first batch


##stack
ITEMS_PER_BATCH = 50

def show_goods_magic_list_stack():
    goods_magic_window = tk.Toplevel()
    goods_magic_window.title("Add or Update Items")
    goods_magic_window.geometry("600x400")
    goods_magic_window.attributes("-topmost", True)
    goods_magic_window.focus_force()

    # Search bar for filtering items
    search_frame = ttk.Frame(goods_magic_window)
    search_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Scrollable frame for item list
    canvas = tk.Canvas(goods_magic_window)
    scrollbar = ttk.Scrollbar(goods_magic_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    loaded_items = []
    all_items = list(inventory_goods_magic_hex_patterns.items())  # Convert dict to list
    start_index = 0

    def load_more_items():
        """Loads the next batch of items into the list."""
        nonlocal start_index
        end_index = start_index + ITEMS_PER_BATCH
        for item_name, item_id in all_items[start_index:end_index]:
            if item_name not in loaded_items:  # Prevent duplicate loading
                item_frame = ttk.Frame(scrollable_frame)
                item_frame.pack(fill="x", padx=5, pady=2)

                tk.Label(item_frame, text=item_name, anchor="w").pack(side="left", fill="x", expand=True)

                add_button = ttk.Button(
                    item_frame,
                    text="Add/Update",
                    command=lambda name=item_name, hex_id=item_id: add_item_from_goods_magic_stack(name, hex_id, goods_magic_window)
                )
                add_button.pack(side="right", padx=5)
                loaded_items.append(item_name)

        start_index = end_index  # Update index for next batch

    def on_scroll(event):
        """Detects when user scrolls near the bottom and loads more items."""
        if canvas.yview()[1] >= 0.9:  # If near the bottom, load more
            load_more_items()

    def filter_items():
        """Filters items based on the search term."""
        nonlocal all_items, start_index, loaded_items
        search_term = search_var.get().lower()

        # Reset loaded items
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        if search_term:
            all_items = [(k, v) for k, v in inventory_goods_magic_hex_patterns.items() if search_term in k.lower()]
        else:
            all_items = list(inventory_goods_magic_hex_patterns.items())

        start_index = 0
        loaded_items.clear()
        load_more_items()

    # Bind search input to filtering function
    search_entry.bind("<KeyRelease>", lambda event: filter_items())

    # Bind scrolling to load more items
    canvas.bind("<Configure>", lambda e: load_more_items())  # Load initial batch
    canvas.bind_all("<MouseWheel>", lambda event: on_scroll(event))

    load_more_items()  # Load first batch


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
#######testing

def get_slot_size(b4):
    """Determine slot size based on b4 value"""
    if b4 == 0xC0:
        return 12
    elif b4 == 0x90:
        return 16
    elif b4 == 0x80:
        return 21
    else:
        return None

def empty_slot_finder_weapons(default_pattern, file_path, pattern_offset_start, pattern_offset_end):
    """Find an empty weapon slot and write the new entry with an incremented counter."""
    with open(file_path, 'r+b') as file:
        valid_b4_values = {0x80, 0x90, 0xC0}

        # Load section
        file.seek(pattern_offset_start)
        section_data = file.read(pattern_offset_end - pattern_offset_start)
        print(f"[DEBUG] Loaded section of {len(section_data)} bytes.")

        # STEP 1: Find alignment point by scanning for valid slots
        # We need a more flexible approach since slots can have different sizes
        def is_valid_slot_start(pos):
            """Check if position could be the start of a valid slot"""
            if pos + 4 > len(section_data):  # Need at least 4 bytes
                return False, None
            
            b3, b4 = section_data[pos+2], section_data[pos+3]
            if b3 == 0x80 and b4 in valid_b4_values:
                slot_size = get_slot_size(b4)
                if slot_size and pos + slot_size <= len(section_data):
                    return True, slot_size
            return False, None
        
        # Find the first valid slot
        start_offset = None
        for i in range(0, len(section_data) - 8):  # At least 8 bytes for empty slot check
            valid, first_slot_size = is_valid_slot_start(i)
            if valid:
                # Check if the next position after this slot also starts a valid slot
                next_pos = i + first_slot_size
                valid_next, _ = is_valid_slot_start(next_pos)
                
                # Or check if it's an empty slot (which is also valid)
                is_empty_next = (next_pos + 8 <= len(section_data) and 
                                 section_data[next_pos:next_pos+8] == b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF')
                
                if valid_next or is_empty_next:
                    start_offset = i
                    print(f"[DEBUG] Found valid slot alignment at offset {i}")
                    break
        
        if start_offset is None:
            print("[ERROR] No valid slot alignment found.")
            return

        # STEP 2: Process all slots from alignment with variable slot sizes
        valid_slot_count = 0
        empty_slot_count = 0
        highest_counter = b'\x00\x00'
        
        # Process slots with variable sizes
        i = start_offset
        while i < len(section_data):
            # First check if this is an empty slot (8 bytes pattern)
            if i + 8 <= len(section_data) and section_data[i:i+8] == b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF':
                empty_slot_count += 1
                # Empty slots are always considered to be 8 bytes
                i += 8
                continue
            
            # Check if this is a valid slot
            if i + 4 <= len(section_data):
                b3, b4 = section_data[i+2], section_data[i+3]
                
                if b3 == 0x80 and b4 in valid_b4_values:
                    slot_size = get_slot_size(b4)
                    
                    if slot_size and i + slot_size <= len(section_data):
                        valid_slot_count += 1
                        counter = section_data[i:i+2]  # First 2 bytes are the counter
                        
                        # Compare counters as integers
                        if int.from_bytes(counter, byteorder='little') > int.from_bytes(highest_counter, byteorder='little'):
                            highest_counter = counter
                            print(f"[DEBUG] New highest counter found: {highest_counter.hex()}")
                        
                        i += slot_size  # Move to next slot
                        continue
            
            # If we reach here, this position doesn't match any known pattern
            # Try the next byte position
            i += 1

        # STEP 3: Write new entry in the first empty slot found after alignment
        new_counter = increment_countersss(highest_counter)
        print(f"[DEBUG] Highest counter: {highest_counter.hex()}, New counter: {new_counter.hex()}")
        
        print(f"[DEBUG] Default pattern: {default_pattern.hex()}")
        print(f"[DEBUG] New counter: {new_counter.hex()}")

        # Modify entry creation to be more explicit
        if len(default_pattern) >= 2:
            # Create new entry by explicitly slicing and combining
            new_entry = new_counter + default_pattern[2:]
            print(f"[DEBUG] New entry: {new_entry.hex()}")
        else:
            print("[ERROR] Default pattern is too short.")
            return

        # Extract b4 value from default pattern to determine its size
        if len(default_pattern) >= 4:
            new_entry_b4 = default_pattern[3]
            new_entry_size = get_slot_size(new_entry_b4)
            if not new_entry_size:
                print(f"[ERROR] Invalid b4 value in default pattern: {hex(new_entry_b4)}")
                return
            
            if len(new_entry) < new_entry_size:
                print(f"[ERROR] Default pattern is too short ({len(new_entry)} bytes) for slot size {new_entry_size}")
                return
        else:
            print("[ERROR] Default pattern too short to determine slot type.")
            return
            
        print(f"[DEBUG] New entry has b4={hex(new_entry_b4)}, requiring {new_entry_size} bytes slot")

        # Find the first empty slot and insert the new entry
        file.seek(pattern_offset_start)
        mod_section_data = file.read(pattern_offset_end - (pattern_offset_start+1599))
        found_empty = False
        empty_slot_position = None
        i = start_offset
        while i < len(mod_section_data):
            # Check for empty slot pattern
            if i + 8 <= len(mod_section_data) and mod_section_data[i:i+8] == b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF':
                empty_slot_position = i
                print(f"[DEBUG] Found empty slot at relative offset {i}")
                found_empty = True
                break
            
            # Move to next slot by determining its size
            if i + 4 <= len(mod_section_data):
                b3, b4 = mod_section_data[i+2], mod_section_data[i+3]
                if b3 == 0x80 and b4 in valid_b4_values:
                    slot_size = get_slot_size(b4)
                    if slot_size:
                        i += slot_size
                        continue
            
            # Move one byte at a time if not at a valid slot
            i += 1
                
        if not found_empty:
            print("[ERROR] No empty slots found to write new entry.")
            return
            
        # Calculate how many bytes to remove to maintain file size
        # First, we're adding the new entry (new_entry_size)
        # Then removing an empty slot (8 bytes)
        # Then we need to remove additional bytes from end based on b4 value
        additional_bytes_to_remove = 0
        if new_entry_b4 == 0x80:  # 21 bytes total
            additional_bytes_to_remove = 21 - 8  # 13 bytes
        elif new_entry_b4 == 0x90:  # 16 bytes total
            additional_bytes_to_remove = 16 - 8  # 8 bytes
        elif new_entry_b4 == 0xC0:  # 12 bytes total
            additional_bytes_to_remove = 12 - 8  # 4 bytes
            
        print(f"[DEBUG] Need to remove {additional_bytes_to_remove} additional bytes to maintain file size")
        
        # Step 1: Insert the new entry
        insertion_position =  empty_slot_position+ pattern_offset_start
        
        # Get the file size
        file.seek(0, 2)  # Seek to end of file
        file_size = file.tell()
        
        # Read all data after the insertion point
        file.seek(insertion_position)
        remainder_data = file.read(file_size - insertion_position)
        
        # Go back to insertion point and write new entry
        file.seek(insertion_position) 
        file.write(new_entry)
        
        # Write the remainder of the file
        file.write(remainder_data)
        
        print(f"[INFO] Inserted new entry at offset {hex(insertion_position)}")
        
        # Step 2: Remove the empty slot (8 bytes)
        # Find another empty slot to remove
        def is_empty_slot(slot_bytes):
            empty_patterns = [
                b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF',
            ]
            return slot_bytes in empty_patterns
        # Step 2: Remove the empty slot (8 bytes)
        # Find another empty slot to remove
        all_empty_slots = []
        i = start_offset
        while i < len(section_data):
            # Check for empty slot pattern
            if i + 8 <= len(section_data) and is_empty_slot(section_data[i:i+8]):
                all_empty_slots.append(i)
            
            # Move to next slot by determining its size
            if i + 4 <= len(section_data):
                b3, b4 = section_data[i+2], section_data[i+3]
                if b3 == 0x80 and b4 in valid_b4_values:
                    slot_size = get_slot_size(b4)
                    if slot_size:
                        i += slot_size
                        continue
            
            # Move one byte at a time if not at a valid slot
            i += 1
        
        if not all_empty_slots:
            print("[WARNING] Could not find any empty slots.")
            return
        last_empty_slot_position = all_empty_slots[-1]    
        # Remove this second empty slot (8 bytes)
        removal_position = pattern_offset_start + last_empty_slot_position
            
        
        # Get updated file size
        file.seek(0, 2)
        updated_file_size = file.tell()
        
        # Read all data after the removal point
        file.seek(removal_position + 8)  # +8 to skip the empty slot
        remainder_data = file.read(updated_file_size - (removal_position + 8))
        
        # Go back to removal point and write remainder (skipping the empty slot)
        file.seek(removal_position)
        file.write(remainder_data)
        
        # Truncate the file to remove the trailing 8 bytes
        file.truncate(updated_file_size - 8)
        
        print(f"[INFO] Removed empty slot at offset {hex(removal_position)}")
        
        # Step 3: Remove additional bytes from the end of the section if needed
        if additional_bytes_to_remove > 0:
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
            deletion_start = section_end - 100
            if deletion_start < section_start:
                messagebox.showerror(
                    "Error",
                    "Distance from the end exceeds the section boundary. Cannot delete bytes."
                )
                return

            # Ensure we do not delete beyond the section start
            deletion_start = max(deletion_start, section_start)
            deletion_end = deletion_start + additional_bytes_to_remove

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
                f"Item Added to slot {section_number}."
            )
            
        print(f"[SUMMARY] Inserted new entry with b4={hex(new_entry_b4)} ({new_entry_size} bytes), "
              f"removed empty slot (8 bytes) and {additional_bytes_to_remove} additional bytes to maintain file size")
        
        print(f"[SUMMARY] Valid slots found: {valid_slot_count}, Empty slots found: {empty_slot_count}")
        print(f"[SUMMARY] Highest counter: {highest_counter.hex()}, New counter used: {new_counter.hex()}")
        return new_counter
##########







def get_slot_size(b4):
    """Determine slot size based on b4 value"""
    if b4 == 0xC0:
        return 12
    elif b4 == 0x90:
        return 16
    elif b4 == 0x80:
        return 21
    else:
        return None

def empty_slot_finder_weapon_test(default_pattern, file_path, pattern_offset_start, pattern_offset_end):
    """Find an empty weapon slot and write the new entry with an incremented counter."""
    with open(file_path, 'r+b') as file:
        valid_b4_values = {0x80, 0x90, 0xC0}
        pattern_offset_start = pattern_offset_start + 520
        pattern_offset_end = pattern_offset_end - 100

        # Load section
        file.seek(pattern_offset_start)
        section_data = file.read(pattern_offset_end - pattern_offset_start)
        print(f"[DEBUG] Loaded section of {len(section_data)} bytes.")

        # STEP 1: Find alignment point by scanning for valid slots
        # We need a more flexible approach since slots can have different sizes
        def is_valid_slot_start(pos):
            """Check if position could be the start of a valid slot"""
            if pos + 4 > len(section_data):  # Need at least 4 bytes
                return False, None
            
            b3, b4 = section_data[pos+2], section_data[pos+3]
            if b3 == 0x80 and b4 in valid_b4_values:
                slot_size = get_slot_size(b4)
                if slot_size and pos + slot_size <= len(section_data):
                    return True, slot_size
            return False, None
        
        # Find the first valid slot
        start_offset = None
        for i in range(0, len(section_data) - 8):  # At least 8 bytes for empty slot check
            valid, first_slot_size = is_valid_slot_start(i)
            if valid:
                # Check if the next position after this slot also starts a valid slot
                next_pos = i + first_slot_size
                valid_next, _ = is_valid_slot_start(next_pos)
                
                # Or check if it's an empty slot (which is also valid)
                is_empty_next = (next_pos + 8 <= len(section_data) and 
                                 section_data[next_pos:next_pos+8] == b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF')
                
                if valid_next or is_empty_next:
                    start_offset = i
                    print(f"[DEBUG] Found valid slot alignment at offset {i}")
                    break
        
        if start_offset is None:
            print("[ERROR] No valid slot alignment found.")
            return

        # STEP 2: Process all slots from alignment with variable slot sizes
        valid_slot_count = 0
        empty_slot_count = 0
        highest_counter = b'\x00\x00'
        
        # Process slots with variable sizes
        i = start_offset
        while i < len(section_data):
            # First check if this is an empty slot (8 bytes pattern)
            if i + 8 <= len(section_data) and section_data[i:i+8] == b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF':
                empty_slot_count += 1
                # Empty slots are always considered to be 8 bytes
                i += 8
                continue
            
            # Check if this is a valid slot
            if i + 4 <= len(section_data):
                b3, b4 = section_data[i+2], section_data[i+3]
                
                if b3 == 0x80 and b4 in valid_b4_values:
                    slot_size = get_slot_size(b4)
                    
                    if slot_size and i + slot_size <= len(section_data):
                        valid_slot_count += 1
                        counter = section_data[i:i+2]  # First 2 bytes are the counter
                        
                        # Compare counters as integers
                        if int.from_bytes(counter, byteorder='little') > int.from_bytes(highest_counter, byteorder='little'):
                            highest_counter = counter
                            print(f"[DEBUG] New highest counter found: {highest_counter.hex()}")
                        
                        i += slot_size  # Move to next slot
                        continue
            
            # If we reach here, this position doesn't match any known pattern
            # Try the next byte position
            i += 1

        # STEP 3: Write new entry in the first empty slot found after alignment
        new_counter = increment_countersss(highest_counter)
        print(f"[DEBUG] Highest counter: {highest_counter.hex()}, New counter: {new_counter.hex()}")
        
        # Use the provided default pattern, just replace the counter at the beginning
        if len(default_pattern) >= 2:
            new_entry = new_counter + default_pattern[2:]
        else:
            print("[ERROR] Default pattern is too short.")
            return

        # Extract b4 value from default pattern to determine its size
        if len(default_pattern) >= 4:
            new_entry_b4 = default_pattern[3]
            new_entry_size = get_slot_size(new_entry_b4)
            if not new_entry_size:
                print(f"[ERROR] Invalid b4 value in default pattern: {hex(new_entry_b4)}")
                return
            
            if len(new_entry) < new_entry_size:
                print(f"[ERROR] Default pattern is too short ({len(new_entry)} bytes) for slot size {new_entry_size}")
                return
        else:
            print("[ERROR] Default pattern too short to determine slot type.")
            return
            
        print(f"[DEBUG] New entry has b4={hex(new_entry_b4)}, requiring {new_entry_size} bytes slot")

        # Find the first empty slot and insert the new entry
        found_empty = False
        empty_slot_position = None
        i = start_offset
        while i < len(section_data):
            # Check for empty slot pattern
            if i + 8 <= len(section_data) and section_data[i:i+8] == b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF':
                empty_slot_position = i
                print(f"[DEBUG] Found empty slot at relative offset {i}")
                found_empty = True
                break
            
            # Move to next slot by determining its size
            if i + 4 <= len(section_data):
                b3, b4 = section_data[i+2], section_data[i+3]
                if b3 == 0x80 and b4 in valid_b4_values:
                    slot_size = get_slot_size(b4)
                    if slot_size:
                        i += slot_size
                        continue
            
            # Move one byte at a time if not at a valid slot
            i += 1
                
        if not found_empty:
            print("[ERROR] No empty slots found to write new entry.")
            return
            
        # Calculate how many bytes to remove to maintain file size
        # First, we're adding the new entry (new_entry_size)
        # Then removing an empty slot (8 bytes)
        # Then we need to remove additional bytes from end based on b4 value
        additional_bytes_to_remove = 0
        if new_entry_b4 == 0x80:  # 21 bytes total
            additional_bytes_to_remove = 21 - 8  # 13 bytes
        elif new_entry_b4 == 0x90:  # 16 bytes total
            additional_bytes_to_remove = 16 - 8  # 8 bytes

            
        print(f"[DEBUG] Need to remove {additional_bytes_to_remove} additional bytes to maintain file size")
        
        # Step 1: Insert the new entry
        insertion_position = pattern_offset_start + empty_slot_position
        
        # Get the file size
        file.seek(0, 2)  # Seek to end of file
        file_size = file.tell()
        
        # Read all data after the insertion point
        file.seek(insertion_position)
        remainder_data = file.read(file_size - insertion_position)
        
        # Go back to insertion point and write new entry
        file.seek(insertion_position)
        file.write(new_entry)
        
        # Write the remainder of the file
        file.write(remainder_data)
        
        print(f"[INFO] Inserted new entry at offset {hex(insertion_position)}")
        def is_empty_slot(slot_bytes):
            empty_patterns = [
                b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF',
            ]
            return slot_bytes in empty_patterns
        # Step 2: Remove the empty slot (8 bytes)
        # Find another empty slot to remove
        all_empty_slots = []
        i = start_offset
        while i < len(section_data):
            # Check for empty slot pattern
            if i + 8 <= len(section_data) and is_empty_slot(section_data[i:i+8]):
                all_empty_slots.append(i)
            
            # Move to next slot by determining its size
            if i + 4 <= len(section_data):
                b3, b4 = section_data[i+2], section_data[i+3]
                if b3 == 0x80 and b4 in valid_b4_values:
                    slot_size = get_slot_size(b4)
                    if slot_size:
                        i += slot_size
                        continue
            
            # Move one byte at a time if not at a valid slot
            i += 1
        
        if not all_empty_slots:
            print("[WARNING] Could not find any empty slots.")
            return
        last_empty_slot_position = all_empty_slots[-1]    
        # Remove this second empty slot (8 bytes)
        removal_position = pattern_offset_start + last_empty_slot_position
        
        # Get updated file size
        file.seek(0, 2)
        updated_file_size = file.tell()
        
        # Read all data after the removal point
        file.seek(removal_position + 8)  # +8 to skip the empty slot
        remainder_data = file.read(updated_file_size - (removal_position + 8))
        
        # Go back to removal point and write remainder (skipping the empty slot)
        file.seek(removal_position)
        file.write(remainder_data)
        
        # Truncate the file to remove the trailing 8 bytes
        file.truncate(updated_file_size - 8)
        
        print(f"[INFO] Removed empty slot at offset {hex(removal_position)}")
        
        # Step 3: Remove additional bytes from the end of the section if needed
        if additional_bytes_to_remove > 0:
            # Get updated file size again
            file.seek(0, 2)
            updated_file_size = file.tell()
            
            # Truncate the file to remove the additional bytes from the end
            file.truncate(updated_file_size - additional_bytes_to_remove)
            
            print(f"[INFO] Removed {additional_bytes_to_remove} additional bytes from end of file")
            
        print(f"[SUMMARY] Inserted new entry with b4={hex(new_entry_b4)} ({new_entry_size} bytes), "
              f"removed empty slot (8 bytes) and {additional_bytes_to_remove} additional bytes to maintain file size")
        
        print(f"[SUMMARY] Valid slots found: {valid_slot_count}, Empty slots found: {empty_slot_count}")
        print(f"[SUMMARY] Highest counter: {highest_counter.hex()}, New counter used: {new_counter.hex()}")


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


def search_fixed_pattern(file_path, pattern_hex, start_offset, end_offset=None):
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

            # Search upwards or downwards based on fixed_pattern_3_offset > end_offset
            while current_offset >= 0:
                # Stop if current_offset is less than end_offset when searching backward
                if end_offset is not None and current_offset < end_offset:
                    return None  # Stop if we've reached the end offset

                if data[current_offset:current_offset + pattern_length] == pattern:
                    return current_offset

                current_offset -= 1  # Move backward

            return None

        # If file_path is an actual file path
        with open(file_path, 'rb') as file:
            current_offset = start_offset

            # Search upwards or downwards based on fixed_pattern_3_offset > end_offset
            while current_offset >= 0:
                # Stop if current_offset is less than end_offset when searching backward
                if end_offset is not None and current_offset < end_offset:
                    return None  # Stop if we've reached the end offset

                file.seek(current_offset)
                chunk = file.read(pattern_length)

                if chunk == pattern:
                    return current_offset

                current_offset -= 1  # Move backward

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
            

            
            default_pattern_1= bytearray.fromhex("0B 11 80 80 F0 3B 2E 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
        
            weapon_id_offset = 4
            

            # Update default pattern with weapon ID and counter values
            default_pattern_1[weapon_id_offset:weapon_id_offset + 4] = weapon_id_bytes

            file.seek(0)  
            entire_file = bytearray(file.read())  # Get updated file content
            section_data = entire_file[section_info['start']:section_info['end'] + 1]
            fixed_pattern_offset_top = find_hex_offset(section_data, hex_pattern1_Fixed)
            new_counter = empty_slot_finder_weapons(default_pattern_1, file_path, section_info['start'] + 32, section_info['start'] + fixed_pattern_offset_top - 431)

            
            

            

            fixed_pattern_offset = find_hex_offset(section_data, hex_pattern1_Fixed)
            
            fixed_pattern_offset_start= fixed_pattern_offset
            search_start_position = fixed_pattern_offset_start + len(hex_pattern1_Fixed) + 1000
            fixed_pattern_offset_end = find_hex_offset(section_data[search_start_position:], hex_pattern_end)
            if fixed_pattern_offset_end is not None:
                fixed_pattern_offset_end += search_start_position
            else:
                # Handle case where end pattern isn't found
                print("End pattern not found")
                return
            if search_start_position >= len(section_data):
                print("Search start position beyond section data.")
                return
            if fixed_pattern_offset is None:
                messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
                return

            # Create and update default pattern 2
            default_pattern_2 = bytearray.fromhex("35 02 80 80")
            default_pattern_2 = new_counter + default_pattern_2[2:]
            
            empty_slot_finder(default_pattern_2, file_path, section_info['start'] + fixed_pattern_offset_start, section_info['start'] + fixed_pattern_offset_start + 37310, 1)
            
            file.seek(0)  
            entire_file = bytearray(file.read())  # Get updated file content
            section_data = entire_file[section_info['start']:section_info['end'] + 1]
    


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
            
            default_pattern_1= bytearray.fromhex("CD 12 80 90 3C 28 00 10 00 00 00 00 00 00 00 00")
        
            weapon_id_offset = 4
            

            # Update default pattern with weapon ID and counter values
            default_pattern_1[weapon_id_offset:weapon_id_offset + 4] = armor_id_bytes

            file.seek(0)  
            entire_file = bytearray(file.read())  # Get updated file content
            section_data = entire_file[section_info['start']:section_info['end'] + 1]
            fixed_pattern_offset_top = find_hex_offset(section_data, hex_pattern1_Fixed)
            new_counter = empty_slot_finder_weapons(default_pattern_1, file_path, section_info['start'] + 32, section_info['start'] + fixed_pattern_offset_top - 431)

            
            

            

            fixed_pattern_offset = find_hex_offset(section_data, hex_pattern1_Fixed)
            
            fixed_pattern_offset_start= fixed_pattern_offset
            search_start_position = fixed_pattern_offset_start + len(hex_pattern1_Fixed) + 1000
            fixed_pattern_offset_end = find_hex_offset(section_data[search_start_position:], hex_pattern_end)
            if fixed_pattern_offset_end is not None:
                fixed_pattern_offset_end += search_start_position
            else:
                # Handle case where end pattern isn't found
                print("End pattern not found")
                return
            if search_start_position >= len(section_data):
                print("Search start position beyond section data.")
                return
            if fixed_pattern_offset is None:
                messagebox.showerror("Error", "Fixed Pattern 1 not found in the selected section.")
                return

            # Create and update default pattern 2
            default_pattern_2 = bytearray.fromhex("35 02 80 90")
            default_pattern_2 = new_counter + default_pattern_2[2:]
            
            empty_slot_finder(default_pattern_2, file_path, section_info['start'] + fixed_pattern_offset_start, section_info['start'] + fixed_pattern_offset_start + 37310, 1)
            
            file.seek(0)  
            entire_file = bytearray(file.read())  # Get updated file content
            section_data = entire_file[section_info['start']:section_info['end'] + 1]
    


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
    upgrade_level= 0
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
import_btn = tk.Button(window, text="Import Save(PC/PS4)", command=import_done)
import_btn.pack(pady=5)
activate_button = tk.Button(window, text="Activate PC SAVE (AFTER EDITING)", command=activate_checksum)
activate_button.pack(pady=20)
frame_save = tk.Frame(window)
frame_save.pack(pady=10)



# Section Selection Frame
section_frame = tk.Frame(window)
section_frame.pack(fill="x", padx=10, pady=5)
section_buttons = []


#ahmeddd


for i in range(1, 11):
    btn = tk.Button(section_frame, text=f"Slot {i}", command=lambda x=i: load_section(x), state=tk.DISABLED)
    btn.pack(side="left", padx=5)
    section_buttons.append(btn)

notebook = ttk.Notebook(window)


# Character Tab
name_tab = ttk.Frame(notebook)
ttk.Label(name_tab, text="Current Character Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
ttk.Label(name_tab, textvariable=current_name_var).grid(row=0, column=1, padx=10, pady=10)
ttk.Label(name_tab, text="New Character Name:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
ttk.Entry(name_tab, textvariable=new_name_var, width=20).grid(row=1, column=1, padx=10, pady=10)
ttk.Button(name_tab, text="Update Name", command=update_character_name).grid(row=2, column=0, columnspan=2, pady=20)

#ng tap
ttk.Label(name_tab, text="Current NG+:").grid(row=5, column=5, padx=10, pady=10, sticky="e")
ttk.Label(name_tab, textvariable=current_ng_var).grid(row=5, column=4, padx=10, pady=10)
ttk.Label(name_tab, text="New NG+:").grid(row=7, column=5, padx=10, pady=10, sticky="e")
ttk.Entry(name_tab, textvariable=new_ng_var, width=20).grid(row=7, column=4, padx=10, pady=10)
ttk.Button(name_tab, text="Update NG+", command=update_ng_value).grid(row=8, column=5, columnspan=2, pady=20)

# Souls Tab
souls_tab = ttk.Frame(notebook)
ttk.Label(souls_tab, text="Current Souls:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
ttk.Label(souls_tab, textvariable=current_souls_var).grid(row=0, column=1, padx=10, pady=10)
ttk.Label(souls_tab, text="New Souls Value (MAX 999999999):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
ttk.Entry(souls_tab, textvariable=new_souls_var, width=20).grid(row=1, column=1, padx=10, pady=10)
ttk.Button(souls_tab, text="Update Souls", command=update_souls_value).grid(row=2, column=0, columnspan=2, pady=20)

inventory_tab = ttk.Frame(notebook)


# Sub-notebook inside inventory
sub_notebook = ttk.Notebook(inventory_tab)
sub_notebook.pack(expand=True, fill="both")

# 1. Rings tab
rings_tab = ttk.Frame(sub_notebook)
sub_notebook.add(rings_tab, text="Items")

ring_list_frame = ttk.Frame(rings_tab)
ring_list_frame.pack(fill="x", padx=10, pady=5)

refresh_ring_button = ttk.Button(
    rings_tab,
    text="Scan for items",
    command=lambda: refresh_ring_list(file_path_var.get())
)
refresh_ring_button.pack(pady=10)

# 2. Weapons tab
weapons_tab = ttk.Frame(sub_notebook)
sub_notebook.add(weapons_tab, text="Weapons")

weapons_list_frame = ttk.Frame(weapons_tab)
weapons_list_frame.pack(fill="x", padx=10, pady=5)

refresh_weapon_button = ttk.Button(
    weapons_tab,
    text="Scan for Weapons",
    command=lambda: refresh_weapon_list(file_path_var.get())
)
refresh_weapon_button.pack(pady=10)

#armor inven

armor_tab = ttk.Frame(sub_notebook)
sub_notebook.add(armor_tab, text="Armors")

armor_list_frame = ttk.Frame(armor_tab)
armor_list_frame.pack(fill="x", padx=10, pady=5)

refresh_armor_button = ttk.Button(
    armor_tab,
    text="Scan for Armors",
    command=lambda: refresh_armor_list(file_path_var.get())
)
refresh_armor_button.pack(pady=10)

#AAOW
aow_tab = ttk.Frame(sub_notebook)
sub_notebook.add(aow_tab, text="AOW")

aow_list_frame = ttk.Frame(aow_tab)
aow_list_frame.pack(fill="x", padx=10, pady=5)

refresh_aow_button = ttk.Button(
    aow_tab,
    text="Scan for AOW",
    command=lambda: refresh_aow_list(file_path_var.get())
)
refresh_aow_button.pack(pady=10)
# Talisman Tab
Talisman_tab = ttk.Frame(sub_notebook)
sub_notebook.add(Talisman_tab, text="Talisman")

talisman_list_frame = ttk.Frame(Talisman_tab)
talisman_list_frame.pack(fill="x", padx=10, pady=5)

refresh_Talisman_button = ttk.Button(
    Talisman_tab,
    text="Scan for Talisman",
    command=lambda: refresh_talisman_list(file_path_var.get())
)
refresh_Talisman_button.pack(pady=10)


# Stats Tab
stats_tab = ttk.Frame(notebook)
for idx, (stat, stat_offset) in enumerate(stats_offsets_for_stats_tap.items()):
    ttk.Label(stats_tab, text=f"Current {stat}:").grid(row=idx, column=0, padx=10, pady=5, sticky="e")
    ttk.Label(stats_tab, textvariable=current_stats_vars[stat]).grid(row=idx, column=1, padx=10, pady=5)
    
    # Use different widgets based on the stat type
    if stat == "Gender":
        # Combobox for Gender
        gender_combo = ttk.Combobox(stats_tab, textvariable=new_stats_vars[stat], 
                                    values=list(GENDER_MAP.values()), 
                                    state="readonly", width=10)
        gender_combo.grid(row=idx, column=2, padx=10, pady=5)
    elif stat == "Class":
        # Combobox for Class
        class_combo = ttk.Combobox(stats_tab, textvariable=new_stats_vars[stat], 
                                  values=list(CLASS_MAP.values()), 
                                  state="readonly", width=10)
        class_combo.grid(row=idx, column=2, padx=10, pady=5)
    else:
        # Regular Entry for numeric stats
        ttk.Entry(stats_tab, textvariable=new_stats_vars[stat], width=10).grid(row=idx, column=2, padx=10, pady=5)
    
    ttk.Button(stats_tab, text=f"Update {stat}", command=lambda s=stat: update_stat(s)).grid(row=idx, column=3, padx=10, pady=5)


# Main Tab Container
# Main Tab Container
add_tab = ttk.Frame(notebook)

notebook.add(name_tab, text="Character (OFFLINE ONLY)")
notebook.add(inventory_tab, text="Inventory/Remove")
notebook.add(add_tab, text="ADD Items")
notebook.add(stats_tab, text="Player Attributes")
notebook.add(souls_tab, text="Souls")

notebook.pack(expand=1, fill="both")
# Sub-Notebook inside "ADD" tab
add_sub_notebook = ttk.Notebook(add_tab)
add_sub_notebook.pack(expand=1, fill="both")


# Add instruction for "Add Weapons" tab
add_item_instructions = """
MAKE SURE WHEN DELETING AN ITEM THAT IT WAS NOT EQUIPED.
"""
ttk.Label(
    rings_tab,
    text=add_item_instructions,
    wraplength=500,
    justify="left",
    anchor="nw"
).pack(padx=10, pady=10, fill="x")
# Adding "Add Weapons" tab
add_weapons_tab = ttk.Frame(add_sub_notebook)
add_sub_notebook.add(add_weapons_tab, text="Add Weapons")

ttk.Button(
    add_weapons_tab,
    text="Add Weapons",
    command=show_weapons_list  # Opens the weapon list window
).pack(pady=20, padx=20)


# Add instruction for "Add Weapons" tab
add_weapons_instructions = """
MAKE SURE WHEN CHOOSING THE UPGRADE LEVEL THAT THE WEAPON COULD BE UPGRADED TO THAT OR YOU WILL GET BANNED.
"""
ttk.Label(
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

add_items_tab_stack = ttk.Frame(add_sub_notebook)
add_sub_notebook.add(add_items_tab_stack, text="Stack Items")

ttk.Button(
    add_items_tab_stack,
    text="Stack items Items ",
    command=show_goods_magic_list_stack  # Opens the item list window
).pack(pady=20, padx=20)

# Add instruction for "Add Items" tab
add_items_instructions = """
This includes items like runes, consumables, magic, bells, cook books, summmons, and more.
"""
ttk.Label(
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


add_talisman_tab = ttk.Frame(add_sub_notebook)
add_sub_notebook.add(add_talisman_tab, text="Add Talisman")

ttk.Button(
    add_talisman_tab,
    text="Add",
    command=show_talisman_list  # Opens the item list window
).pack(pady=20, padx=20)


##AOW
add_aow_tab = ttk.Frame(add_sub_notebook)
add_sub_notebook.add(add_aow_tab, text="Add AOW")

ttk.Button(
    add_aow_tab,
    text="Add",
    command=show_aow_list  # Opens the item list window
).pack(pady=20, padx=20)
# Add instruction for "Add Items" tab
add_sms_instructions = """
The slots for AOW are limited to about 50 item for each save load. If you want to add more, reload the game and then edit the save again.
"""
tk.Label(
    add_aow_tab,
    text=add_sms_instructions,
    wraplength=500,
    justify="left",
    anchor="nw"
).pack(padx=10, pady=10, fill="x")


my_label = tk.Label(window, text="Made by Alfazari911 --   Thanks to Nox and BawsDeep for help", anchor="e", padx=10)
my_label.pack(side="top", anchor="ne", padx=10, pady=5)

we_label = tk.Label(window, text="USE AT YOUR OWN RISK. EDITING STATS AND HP COULD GET YOU BANNED", anchor="w", padx=10)
we_label.pack(side="bottom", anchor="nw", padx=10, pady=5)
messagebox.showinfo("Info", "The editor is writing directly to file, no need to save.")
# Run 
window.mainloop()
