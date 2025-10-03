import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import struct
import hashlib
import binascii


#Distanced and patterns
souls_distance = -331
ng_distance=-280
souls_distance = -331
from_aob_steam= 44 
magic_pattern='00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 00 00 00 FF FF FF FF'
hex_pattern_ng= 'FF FF FF FF 00 00 00 00 00 00 00 00 00 01'
AOB_search='00 00 00 00 ?? 00 !! 00 ?? ?? 00 00 00 00 00 00 ??'
AOB_maybe_worldflag= '00 00 00 00 FF FF FF FF 00 00 00 00 00 00 00 00 00 01 00 00 FF FF FF FF 00 00 00 00 00 00 00 00'



#Stats
stats_offsets_for_stats_tap = {
    "Level": -335,
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
    "Scadutree Blessing": -187,
    "Shadow Realm Blessing":-186,

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


# Main window
window = tk.Tk()
window.title("Elden Ring Save Editor")

#Inventory list
weapons = []
aow = []
armors = []
goods = []
rings = []
empty=[]
inventory_items=[]

#torage box
storage_inventory_items=[]
storage_weapons = []
storage_aow = []
storage_armors = []
storage_goods = []
storage_rings = []
storage_empty=[]


#GA ITEM HANDLE
ga_weapons=[]
ga_armors=[]
ga_aow=[]
ga_empty=[]
ga_items=[]

#list
char_name=tk.StringVar()
current_name=tk.StringVar()
current_name_var=tk.StringVar(value="N/A")
new_name_var=tk.StringVar()
current_runes_var=tk.StringVar(value="N/A")
new_runes_var=tk.StringVar()
inventory_type_var = tk.StringVar(value="Ash of War")
storage_type_var = tk.StringVar(value="Talismans")
current_stats_vars = {}
new_stats_vars = {}
imported_name=[]
# Initialize variables for each stat
for stat in stats_offsets_for_stats_tap:
    current_stats_vars[stat] = tk.StringVar()
    new_stats_vars[stat] = tk.StringVar()  # Use StringVar for all stats
current_ng_var = tk.StringVar(value="N/A")
new_ng_var = tk.StringVar()
current_stemaid_var=tk.StringVar()


#path
userdata_path=None
import_path=None

#bytes
data=None
imported_data=None


# Set the working directory
working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)


#Jsons
def load_and_copy_json(file_name):
    file_path = os.path.join(working_directory, "Resources/Json", file_name)
    with open(file_path, "r") as file:
        return json.load(file).copy()
    
goods_and_magic_json= load_and_copy_json("goods.json")
weapons_json = load_and_copy_json("weapons.json")
armor_json= load_and_copy_json("armor.json")
talisman_json= load_and_copy_json("talisman.json")
aow_json= load_and_copy_json("aow.json")
graces_json= load_and_copy_json("graces.json")
weapons_sorted_json = load_and_copy_json("weapons_sorted.json")
goods_and_magic_sorted_json= load_and_copy_json("goods_sorted.json")
#Helpers
def find_hex_offset(section_data, hex_pattern):
    try:
        pattern_bytes = bytes.fromhex(hex_pattern)
        if pattern_bytes in section_data:
            return section_data.index(pattern_bytes)
        return None
    except ValueError as e:
        messagebox.showerror("Error", f"Failed to find hex pattern: {str(e)}")
        return None
    
def find_value_at_offset(section_data, offset, byte_size=4):
    try:
        value_bytes = section_data[offset:offset+byte_size]
        if len(value_bytes) == byte_size:
            return int.from_bytes(value_bytes, 'little')
    except IndexError:
        pass
    return None

def write_value_at_offset(data, offset, value, byte_size=4):
    value_bytes = value.to_bytes(byte_size, 'little')
    # Replace the bytes at the given offset with the new value
    return data[:offset] + value_bytes + data[offset+byte_size:]

def calculate_offset2(offset1, distance):
    return offset1 + distance


#AOB
def aob_to_pattern(aob: str):
    parts = aob.split()
    pattern = bytearray()
    mask = bytearray()

    for p in parts:
        if p == "??":  
            # wildcard but must not be 0x00
            pattern.append(0x00)
            mask.append(2)   # custom code: 2 = wildcard no-zero
        elif p == "!!":  
            # wildcard can be 0x00
            pattern.append(0x00)
            mask.append(0)   # 0 = wildcard any byte
        else:
            pattern.append(int(p, 16))
            mask.append(1)   # 1 = exact match

    return bytes(pattern), bytes(mask)


def aob_search(data: bytes, aob: str):
    pattern, mask = aob_to_pattern(aob)
    L = len(pattern)
    mv = memoryview(data)

    for i in range(len(data) - L + 1):
        # skip offsets below 0x1FFD20
        if i < 0x1FFD20:
            continue

        ok = True
        for j in range(L):
            if mask[j] == 1:  # exact
                if mv[i + j] != pattern[j]:
                    ok = False
                    break
            elif mask[j] == 2:  # wildcard but not zero
                if mv[i + j] == 0x00:
                    ok = False
                    break
            # mask[j] == 0 means wildcard (any byte, including 0x00)

        if ok:
            print([i])  # debug print
            return [i]

    print([])  # no matches
    return None

# load and copy JSON data from files in the working directory
def load_and_copy_json(file_name):
    file_path = os.path.join(working_directory, "Resources/Json", file_name)
    with open(file_path, "r") as file:
        return json.load(file).copy()
    
def split_files(file_path, folder_name):
    file_name = os.path.basename(file_path)

    # Case 1: If file name is memory.dat
    if file_name.lower() == 'memory.dat':
        split_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder_name)
        os.makedirs(split_dir, exist_ok=True)

        with open(file_path, "rb") as f:
            # 1. Header (0x70 bytes)
            header = f.read(0x70)
            with open(os.path.join(split_dir, "header"), "wb") as out:
                out.write(header)

            # 2. userdata0 - userdata9 (each 0x27FFFF bytes)
            chunk_size = 0x280000
            for i in range(10):
                data = f.read(chunk_size)
                if not data:  # stop if file ends early
                    break
                with open(os.path.join(split_dir, f"userdata{i}"), "wb") as out:
                    out.write(data)

            # 3. Regulation (remaining bytes)
            regulation = f.read()
            if regulation:
                with open(os.path.join(split_dir, "regulation"), "wb") as out:
                    out.write(regulation)


    if file_name== 'ER0000.sl2': ##FIX
        split_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder_name)
        os.makedirs(split_dir, exist_ok=True)

        with open(file_path, "rb") as f:
            # 1. Header (0x70 bytes)
            header = f.read(0x300)
            with open(os.path.join(split_dir, "header"), "wb") as out:
                out.write(header)

            # 2. userdata0 - userdata9 (each 0x28 000F bytes)
            chunk_size = 0x280010
            for i in range(10):
                data = f.read(chunk_size)
                if not data:  # stop if file ends early
                    break
                with open(os.path.join(split_dir, f"userdata{i}"), "wb") as out:
                    out.write(data)
            

            # 3. Regulation (remaining bytes)
            regulation = f.read()
            if regulation:
                with open(os.path.join(split_dir, "regulation"), "wb") as out:
                    out.write(regulation)
        for i in range(10):
            file_path = os.path.join(split_dir, f"userdata{i}")
            if not os.path.exists(file_path):
                continue
            with open(file_path, "rb") as f:
                data = f.read()
            data = data[16:]
            with open(file_path, "wb") as f:
                f.write(data)

MODE=None

def save_file():
    global userdata_path, data

    if userdata_path is None or data is None:
        messagebox.showerror("Error", "No userdata loaded to save.")
        return

    # Write the modified data back to the userdata file
    with open(userdata_path, 'wb') as f:
        f.write(data)

def merge_files(folder_name, output_file=None):
    save_file()

    split_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder_name)
    if not os.path.exists(split_dir):
        print(f"Directory {split_dir} does not exist.")
        return
    
    # Create new file with appropriate name based on MODE
    if output_file is None:
        if MODE == 'ps4':
            output_file = 'memory.dat'
        elif MODE == 'PC':
            output_file = 'ER0000.sl2'
    else:
        # If output_file is provided, ensure correct extension
        if MODE == 'ps4':
            if not output_file.lower().endswith('.dat'):
                output_file += '.dat'
        elif MODE == 'PC':
            if not output_file.lower().endswith('.sl2'):
                output_file += '.sl2'
    
    with open(output_file, "wb") as out:
        # 1. Header
        header_path = os.path.join(split_dir, "header")
        if os.path.exists(header_path):
            with open(header_path, "rb") as f:
                out.write(f.read())
        else:
            print(f"Header file not found in {split_dir}.")
            return

        # 2. userdata0 - userdata9
        if MODE == 'ps4':
            for i in range(10):
                userdata_path = os.path.join(split_dir, f"userdata{i}")
                if os.path.exists(userdata_path):
                    with open(userdata_path, "rb") as f:
                        out.write(f.read())
                else:
                    print(f"{userdata_path} not found, stopping merge.")
                    break
        elif MODE == 'PC':
            # For each userdata file add 16 bytes of 0x00 at the start
            for i in range(10):
                userdata_path = os.path.join(split_dir, f"userdata{i}")
                if os.path.exists(userdata_path):
                    with open(userdata_path, "rb") as f:
                        out.write(b'\x00' * 16)  # add 16 bytes of 0x00
                        out.write(f.read())
                else:
                    print(f"{userdata_path} not found, stopping merge.")
                    break

        # 3. Regulation
        regulation_path = os.path.join(split_dir, "regulation")
        if os.path.exists(regulation_path):
            with open(regulation_path, "rb") as f:
                out.write(f.read())
        if MODE=='PC':
            recalc_checksum(output_file)

    messagebox.showinfo("Success", f"Files merged into {output_file}")

def save_as():
    global MODE
    if MODE is None:
        messagebox.showerror("Error", "No mode set. Please open a valid userdata file first.")
        return

    output_file = filedialog.asksaveasfilename(
        initialfile="memory.dat" if MODE == 'ps4' else "ER0000.sl2",
        filetypes=[("All files", "*.*")],
        title="Save merged file as"
    )

    if output_file:
        merge_files("split", output_file)
    else:
        print("Save operation cancelled.")

#Calculate checksum for pc
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

def open_file():

    global MODE

    MODE=None

    file_path = filedialog.askopenfilename(title="Select memory.dat or ER0000.sl2 file", filetypes=[("All files", "*.*"), ("DAT files", "*.dat"), ("SL2 files", "*.sl2") ])
    if not file_path:
        return
    file_name = os.path.basename(file_path)

    if file_name=='memory.dat':
        MODE= "ps4"
    elif file_name=='ER0000.sl2':
        MODE= "PC" 
    else:
        messagebox.showerror("Error", "Please select a valid memory.dat or ER0000.sl2 file.")
        return

    split_files(file_path, "split")
    display_char_name("split")
    return MODE

def find_char_name(data):
    magic_bytes=bytes.fromhex(magic_pattern)
    magic_offset=data.find(magic_bytes)
    if magic_offset == -1:
        return None
    
    name_offset=magic_offset-0x11b


    max_chars = 16
    raw_name = data[name_offset:name_offset + max_chars * 2]
    char_name = raw_name.decode("utf-16-le", errors="ignore").rstrip("\x00")

    return char_name
def select_userdata(path, folder_name):
    global userdata_path, import_path, data, imported_data

    if folder_name == "split":
        if userdata_path is not None and data is not None:
            save_file()

        userdata_path = path
        load_data()
        gaprint(data)
        inventoryprint()
        sort_list()
        storage_par()
        init_graces_tab()
        display_inventory("Ash of War")
        display_storage("Talismans")


    elif folder_name == "imported":
        import_path = path
        with open(import_path, 'rb') as f:
            imported_data = f.read()

        # Replace Steam ID in imported data with my save’s Steam ID
        my_steam_id, _ = find_steam_id(data, data)
        _, steam_offset = find_steam_id(imported_data, imported_data, is_import=True)
        my_steam_id = bytes.fromhex(my_steam_id)
        steam_offset=steam_offset

        new_data = imported_data[:steam_offset] + my_steam_id + imported_data[steam_offset+8:]
        data = new_data
        save_file()

        userdata_path = path
        load_data()
        gaprint(data)
        inventoryprint()
        sort_list()
        init_graces_tab()
        display_inventory("Ash of War")
        display_storage("Talismans")
        messagebox.showinfo("Import Successful", f"Imported character from {import_path} and replaced Steam ID.")



def char_name_to_userdata(folder_name):
    global char_name, imported_name
    char_name = []
    imported_name=[]


    split_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder_name)
    for i in range(10):

        file_path = os.path.join(split_dir, f"userdata{i}")
        with open(file_path, "rb") as f:
            data = f.read()
            name=find_char_name(data)
            if name is None:
                return
            if folder_name == 'split':
                char_name.append((name, file_path))
            elif folder_name == 'imported':
                imported_name.append((name, file_path))


def display_char_name(folder_name):
    char_name_to_userdata(folder_name)

    if folder_name == 'split':
        name_list = char_name
    elif folder_name == 'imported':
        name_list = imported_name
    else:
        return

    if folder_name == 'split':
        # Clear and redraw in the left panel
        for widget in file_open_frame.winfo_children():
            widget.destroy()

        selected_var = tk.StringVar()

        for n, path in name_list:
            rb = tk.Radiobutton(
                file_open_frame,
                text=n,
                variable=selected_var,
                value=path,
                indicatoron=False,
                width=20,
                command=lambda p=path, f=folder_name: select_userdata(p, f)
            )
            rb.pack(pady=2, fill="x")

        # --- Recreate the file buttons ---
        ttk.Button(file_open_frame, text="Open Save File", command=open_file).pack(pady=5, anchor="w")
        ttk.Button(file_open_frame, text="Save Modified File", command=save_as).pack(pady=5, anchor="w")
        ttk.Button(file_open_frame, text="Import Save File", command=import_save).pack(pady=5, anchor="w")

    elif folder_name == 'imported':
        # Open a separate window for imported saves
        import_window = tk.Toplevel()
        import_window.title("Select Imported Character")
        import_window.geometry("300x400")
        import_window.attributes("-topmost", True)

        selected_var = tk.StringVar()

        for n, path in name_list:
            rb = tk.Radiobutton(
                import_window,
                text=n,
                variable=selected_var,
                value=path,
                indicatoron=False,
                width=20,
                command=lambda p=path, f=folder_name, w=import_window: (
                    select_userdata(p, f),
                    w.destroy()  # close after selection
                )
            )
            rb.pack(pady=5, fill="x")





def find_steam_id(section_data, save_data, is_import=False):
    gaprint(save_data)
    inventoryprint()
    sort_list()


    _,_, offsets, _=save_struct(save_data)
    offset = offsets


    steam_id = section_data[offset:offset+8]
    if is_import==False:
        if MODE=='ps4':
            if steam_id != b'\x00' * 8:  # 8 bytes of zero
                print('Issue with steam id not being zero for PS4')
                return
            
        elif MODE == 'PC':
            if steam_id == b'\x00' * 8:
                print('Issue with steam id being zero for PC')
                return


    hex_str = steam_id.hex().upper()  


    #current_stemaid_var.set(hex_str)
    return hex_str, offset

def load_data():
    global userdata_path, current_name, data, magic_offset

    current_name = None
    data = None

    if userdata_path is None:
        return

    with open(userdata_path, 'rb') as f:
        data = f.read()
    
    # Name
    name = find_char_name(data)
    if name is not None:
        current_name = name
        current_name_var.set(current_name)   # <-- update the label
    else: 
        print('Name not found')
        current_name_var.set("Unknown")

    # NG+
    ng_pattern_offset = data.find(bytes.fromhex(hex_pattern_ng))
    if ng_pattern_offset == -1:  # use -1 check, not None
        return
    ng_offset = ng_pattern_offset + ng_distance
    current_ng = find_value_at_offset(data, ng_offset, byte_size=1)

    current_ng_var.set(current_ng)

    # Stats
    magic_offset = data.find(bytes.fromhex(magic_pattern))
    for stats, distance in stats_offsets_for_stats_tap.items():
        stats_offset = magic_offset + distance
        byte_size = 2 if stats == "Level" else 1
        current_stat_value = find_value_at_offset(data, stats_offset, byte_size)

        if current_stat_value is None:
            current_stats_vars[stats].set("N/A")
            new_stats_vars[stats].set("")
        elif stats == "Gender":
            display_value = GENDER_MAP.get(current_stat_value, f"Unknown ({current_stat_value})")
            current_stats_vars[stats].set(display_value)
            new_stats_vars[stats].set(display_value)
        elif stats == "Class":
            display_value = CLASS_MAP.get(current_stat_value, f"Unknown ({current_stat_value})")
            current_stats_vars[stats].set(display_value)
            new_stats_vars[stats].set(display_value)
        else:
            display_value = str(current_stat_value)
            current_stats_vars[stats].set(display_value)
            new_stats_vars[stats].set(display_value)

    # Runes
    runes_offset = magic_offset + souls_distance
    current_runes_value = find_value_at_offset(data, runes_offset, byte_size=4)
    current_runes_var.set(current_runes_value)


    #steam id
    find_steam_id(data, data)

        
    
## Updating value

#Char name
def update_name(new_name):
    global data

    magic_offset = data.find(bytes.fromhex(magic_pattern))
    offset = magic_offset - 0x11B

    # Encode to UTF-16 LE
    new_name_utf16 = new_name.encode("utf-16-le")
    # Pad or trim to 32 bytes (16 characters)
    new_name_utf16 = new_name_utf16[:32].ljust(32, b"\x00")

    # Write the new name into the save data
    data = data[:offset] + new_name_utf16 + data[offset+32:]

    # Update the Tkinter variable → this refreshes the label
    current_name_var.set(new_name)

    return data


def update_runes(new_runes):
    global data

    # Convert safely
    new_runes = int(new_runes)  # convert from string to int
    if new_runes > 4294967295:
        messagebox.showerror("Error", "Runes value must be between 0 and 4,294,967,295.")
        return

    decimal_runes = new_runes
    new_runes_bytes = new_runes.to_bytes(length=4, byteorder="little")

    # Find offset
    magic_offset = data.find(bytes.fromhex(magic_pattern))
    offset = magic_offset + souls_distance

    # Overwrite 4 bytes
    data = data[:offset] + new_runes_bytes + data[offset+4:]

    current_runes_var.set(str(decimal_runes))


    return data


def update_ng(new_ng):
    global data

    # Convert safely
    new_ng = int(new_ng)  # convert from string to int
    if new_ng < 0 or new_ng > 255:
        messagebox.showerror("Error", "NG+ value must be between 0 and 255.")
        return

    decimal_ng = new_ng
    new_ng_bytes = new_ng.to_bytes(length=1, byteorder="little")

    # Find offset
    magic_offset = data.find(bytes.fromhex(hex_pattern_ng))
    offset = magic_offset + ng_distance  # fix

    # Overwrite 1 byte
    data = data[:offset] + new_ng_bytes + data[offset+1:]

    current_ng_var.set(str(decimal_ng))


    return data



#Stats
def update_stat(stat):
    global data
    
    try:
        if stat == "Gender":
            selected = new_stats_vars[stat].get()

            if selected == "":  # Check if the user left the field empty
                raise ValueError("Please select a gender")
            new_stat_value = REVERSE_GENDER_MAP[selected]
        elif stat == "Class":
            selected = new_stats_vars[stat].get()

            if selected == "":  # Check if the user left the field empty
                raise ValueError("Please select a class")
            new_stat_value = REVERSE_CLASS_MAP[selected]
        else:
            # Get the value from the StringVar
            user_input = new_stats_vars[stat].get().strip()

            if user_input == "":
                raise ValueError(f"Please enter a valid value for {stat}.")
            new_stat_value = int(user_input)

    except (ValueError, KeyError) as e:
        messagebox.showerror("Invalid Input", str(e))
        return
    
    
    offset1 = find_hex_offset(data, magic_pattern)
    if offset1 is not None:

        relative_offset = calculate_offset2(offset1, stats_offsets_for_stats_tap[stat])
        absolute_offset = relative_offset
        
        
        # For Level stat, use 2 bytes
        byte_size = 2 if stat == "Level" else 1
        data=write_value_at_offset(data, absolute_offset, new_stat_value, byte_size=byte_size)
        
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




#Inventory stuff parsing system



ITEM_TYPE_EMPTY = 0x00000000
ITEM_TYPE_WEAPON = 0x80000000
ITEM_TYPE_ARMOR  = 0x90000000
ITEM_TYPE_AOW  = 0xC0000000    

class Item:

    BASE_SIZE= 8

    def __init__(self, gaitem_handle, item_id, offset , extra=None, size=BASE_SIZE):

        self.gaitem_handle= gaitem_handle
        self.item_id= item_id
        self.extra= extra or {}
        self.size= size
        self.offset= offset

    @classmethod
    def from_bytes(cls, data_type, offset= 0 ):

        gaitem_handle, item_id= struct.unpack_from("<II", data_type, offset)
        type_bits= gaitem_handle & 0xF0000000
        extra = {}
        cursor = offset + cls.BASE_SIZE
        size = cls.BASE_SIZE

        if gaitem_handle != 0:
            if type_bits == ITEM_TYPE_WEAPON:
                extra_4_1 , extra_4_2 , AOW_handle = struct.unpack_from("<II I", data_type, cursor)
                cursor += 12
                extra_1_1 = struct.unpack_from("<B", data_type, cursor)[0]
                cursor += 1
                size = cursor - offset
                
                extra = {
                    "extra_4_1": extra_4_1,
                    "extra_4_2": extra_4_2,
                    "AOW_handle": AOW_handle,
                    "extra_1_1": extra_1_1,
                }
            elif type_bits == ITEM_TYPE_ARMOR:
                extra_4_1 , extra_4_2= struct.unpack_from("<II", data_type, cursor)
                cursor += 8
                size= cursor-offset
                extra= {
                    "extra_4_1": extra_4_1,
                    "extra_4_2": extra_4_2,

                }


        return cls(gaitem_handle, item_id, offset, extra, size)
    


def parse_items(data_type, start_offset, end_offset):
    items = []
    offset = start_offset

    while offset < end_offset:
        item = Item.from_bytes(data_type, offset)
        items.append(item)
        offset += item.size  

    return items

def gaprint(data_type):
    global ga_weapons, ga_armors, ga_aow, ga_empty, ga_items

    save_data=data_type
    ga_items=[]
    ga_weapons=[]
    ga_armors=[]
    ga_aow=[]
    ga_empty=[]

    start_offset = 0x20

    magic_offset=save_data.find(bytes.fromhex(magic_pattern))

    end_offset = magic_offset- 432

    items = parse_items(save_data, start_offset, end_offset)

    for item in items:
        type_bits = item.gaitem_handle & 0xF0000000
        ga_items.append((item.gaitem_handle, item.item_id, item.offset))
        if type_bits == ITEM_TYPE_WEAPON:
            ga_weapons.append((item.gaitem_handle, item.item_id, item.offset))
        elif type_bits == ITEM_TYPE_ARMOR:
            ga_armors.append((item.gaitem_handle, item.item_id, item.offset))
        elif type_bits == ITEM_TYPE_AOW:
            ga_aow.append((item.gaitem_handle, item.item_id, item.offset))
        elif type_bits == ITEM_TYPE_EMPTY:
            ga_empty.append((item.gaitem_handle, item.item_id, item.offset))

# iNVENTORY section

ITEM_TYPE_EMPTY = 0x00000000
ITEM_TYPE_WEAPON = 0x80000000
ITEM_TYPE_ARMOR  = 0x90000000
ITEM_TYPE_AOW  = 0xC0000000   
ITEM_TYPE_GOOD = 0XB0000000
ITEM_TYPE_RINGS= 0XA0000000 

class INVENTORY:
    BASE_SIZE = 12

    def __init__(self, gaitem_handle, quantity, index, offset):
        self.gaitem_handle = gaitem_handle 
        self.quantity = quantity
        self.index = index
        self.offset = offset
        self.size = self.BASE_SIZE

    @classmethod
    def from_bytes(cls, data, offset=0):
        gaitem_handle, quantity, index = struct.unpack_from("<III", data, offset)
        return cls(gaitem_handle, quantity, index, offset)




def parse_inventory(data, start_offset, end_offset):
    inventory_item = []
    offset = start_offset

    while offset < end_offset:
        item = INVENTORY.from_bytes(data, offset)
        inventory_item.append(item)
        offset += item.size  

    return inventory_item

def inventoryprint():
    global data
    global weapons, aow, armors, goods, rings, empty, inventory_items
    
    inventory_items=[]
    weapons = []
    aow = []
    armors = []
    goods = []
    rings = []
    empty=[]

    start_offset = find_hex_offset(data, magic_pattern) + 505

    end_offset = find_hex_offset(data, magic_pattern)+37365


    items = parse_inventory(data, start_offset, end_offset)

    for item in items:
        type_bits = item.gaitem_handle & 0xF0000000
        inventory_items.append((item.gaitem_handle, item.quantity, item.index, item.offset))

        if type_bits == ITEM_TYPE_WEAPON:
            weapons.append((item.gaitem_handle, item.quantity, item.index, item.offset))
        elif type_bits == ITEM_TYPE_ARMOR:
            armors.append((item.gaitem_handle, item.quantity, item.index, item.offset))
        elif type_bits == ITEM_TYPE_AOW:
            aow.append((item.gaitem_handle, item.quantity, item.index, item.offset))
        elif type_bits == ITEM_TYPE_GOOD:
            goods.append((item.gaitem_handle, item.quantity, item.index, item.offset))
        elif type_bits == ITEM_TYPE_RINGS:
            rings.append((item.gaitem_handle, item.quantity, item.index, item.offset))
        elif type_bits == ITEM_TYPE_EMPTY:
            empty.append((item.gaitem_handle, item.quantity, item.index, item.offset))


####
#Item spawn (none on ga handle)

import struct

def inventory_counters(data):
    magic_offset = data.find(bytes.fromhex(magic_pattern))

    first_counter_offset = magic_offset + 501
    second_counter_offset = magic_offset + 37373
    third_counter_offset = magic_offset + 37377

    first_val = struct.unpack_from("<H", data, first_counter_offset)[0]
    second_val = struct.unpack_from("<H", data, second_counter_offset)[0]
    third_val = struct.unpack_from("<H", data, third_counter_offset)[0]

    first_val += 1
    second_val += 1
    third_val += 1


    data = data[:first_counter_offset] + struct.pack("<H", first_val) + data[first_counter_offset+2:]
    data = data[:second_counter_offset] + struct.pack("<H", second_val) + data[second_counter_offset+2:]
    data = data[:third_counter_offset] + struct.pack("<H", third_val) + data[third_counter_offset+2:]

    return data


def sort_list():
    global inventory_items, ga_items

    # First sort by index (3rd element)
    inventory_items.sort(key=lambda x: x[2])

    # Then sort by gaitem_handle (1st element)
    ga_items.sort(key=lambda x: x[0])


def spawn_goods(item_name, item_quantity, item_type, Stack=False):
    global data
    global inventory_items, goods



    #incrementing inventory counters

    if item_type == 'goods':
        item_id = goods_and_magic_json.get(item_name)
        if not item_id:
            print('no id found')
            return
        
    elif item_type == 'talisman':
        item_id = talisman_json.get(item_name)
        item_quantity= 1
        if not item_id:
            print('no id found')
            return

    item_id_bytes = bytes.fromhex(item_id)
    if len(item_id_bytes) != 4:
        print('length error')
        return
    
    item_id_int= int.from_bytes(item_id_bytes, 'little')

    #check if the item alr exisits or no
    if Stack == False:
        if item_type == 'goods':
            for i, (gaitem_handle, quantity, index, offset) in enumerate(inventory_items):
                if item_id_int == gaitem_handle:

                    quantity_offset = offset + 4
                    new_quantity = item_quantity  
                    data = (
                        data[:quantity_offset] 
                        + new_quantity.to_bytes(4, 'little') 
                        + data[quantity_offset+4:]
                    )

                    # update inventory_items to reflect the new quantity
                    inventory_items[i] = (gaitem_handle, new_quantity, index, offset)


                    return
         

        
    # If item not found, we will add it
    last_offset = empty[0][3]

    highest_index= inventory_items[-2][2]  

    highest_index +=2


    goods_slot = (
        item_id_int.to_bytes(4, 'little') +
        item_quantity.to_bytes(4, 'little') +
        highest_index.to_bytes(4, 'little')
    )


    data = data[:last_offset] + goods_slot + data[last_offset+12:]

    data=inventory_counters(data)

    slot_bytes = data[last_offset:last_offset+12]
    aob_str = " ".join(f"{b:02X}" for b in slot_bytes)




    gaprint(data)
    inventoryprint()
    sort_list()

#weapons spawn

def spawn_weapons(item_name, item_type):
    global data
    global inventory_items, ga_items, ga_weapons, ga_empty

    if item_type == 'weapons':
        item_id = weapons_sorted_json.get(item_name)
        if not item_id:
            print('no id found')
            return
        
    elif item_type == 'armors':
        item_id = armor_json.get(item_name)
        if not item_id:
            print('no id found')
            return
        
    elif item_type == 'aow':
        item_id = aow_json.get(item_name)
        if not item_id:
            print('no id found')
            return
        

    item_id_bytes = bytes.fromhex(item_id)
    if len(item_id_bytes) != 4:
        print('length error')
        return
    

    #weapons slot
    # ga item handle
    # item id


    # GA handle first


    First_weapon_offset=ga_weapons[0][2]
    first_spawn_offset = None

    if item_type == 'weapons' or item_type == 'armors':

        for _, _, offset in ga_empty:
            if offset > First_weapon_offset:
                first_spawn_offset = offset
                break
    elif item_type== 'aow':
        for _, _, offset in ga_empty:
            if offset < First_weapon_offset:
                first_spawn_offset = offset
                break


    if first_spawn_offset is not None:

    
    
        highest_GA=0
        
        for gaitem_handle, _, _ in ga_items:

            type_bits = gaitem_handle & 0x0000FFFF
            if type_bits > highest_GA:
                highest_GA= type_bits

        highest_GA +=1

        if item_type=='weapons':
            item_handle=highest_GA.to_bytes(2, "little") + (0x8080).to_bytes(2, "little")
            extra=bytes(13)
        
        if item_type=='armors':
            item_handle=highest_GA.to_bytes(2, "little") + (0x9080).to_bytes(2, "little")
            extra=bytes(8)

        if item_type== 'aow':
            item_handle=highest_GA.to_bytes(2, "little") + (0xC080).to_bytes(2, "little")
            extra=bytes(0)


        weapons_slot = (
            item_handle +
            item_id_bytes +                      # 4 bytes
            extra                            # 13 zero bytes
        )



    # in inventory
    


    last_offset = empty[0][3]

    highest_index= inventory_items[-2][2]  

    highest_index +=2


    item_quantity=1

    goods_slot = (
        item_handle+
        item_quantity.to_bytes(4, 'little') +
        highest_index.to_bytes(4, 'little')
    )


    data = data[:last_offset] + goods_slot + data[last_offset+12:]
    data = inventory_counters(data)



    slot_bytes = data[last_offset:last_offset+12]
    aob_str = " ".join(f"{b:02X}" for b in slot_bytes)





    # 21 total new bytes. delete 8 from GA handle
    # delete 13 from end of file
    if item_type == 'weapons' or item_type == 'armors':

        last_ga_empty= 0
        for _,_, offset_empty in ga_empty:
            if last_ga_empty < offset_empty:
                last_ga_empty=offset_empty

        empty_value_at_offset= b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF'
        if empty_value_at_offset == data[last_ga_empty:last_ga_empty+8]:
            lenght=len(data)
            _,critical,wwws,_=save_struct(data)
            if critical>lenght:
                messagebox.showinfo("Error", "No more data can be deleted without corrupting the save.")
                return

            data = data[:first_spawn_offset] + weapons_slot + data[first_spawn_offset:]
            data = data[:last_ga_empty] + data[last_ga_empty+8:]


            if item_type=='weapons':

                lenght=len(data)
                _,critical,wwws,_=save_struct(data)
                if critical>lenght:
                    messagebox.showinfo("Error", "No more data can be deleted without corrupting the save.")
                    return
                data = data[:-13]
                
            if item_type=='armors':
                lenght=len(data)
                _,critical,_,_=save_struct(data)
                
                if critical>lenght:
                    messagebox.showinfo("Error", "No more data can be deleted without corrupting the save.")
                    return
                data= data[:-8]
    
    if item_type== 'aow': # no deletion is needed

        data= data[:first_spawn_offset] + weapons_slot + data[first_spawn_offset+8:]

    
    gaprint(data)
    inventoryprint()
    sort_list()
    return item_handle

###IMPORTING SAVES

def import_save():
    global imported_data, import_path

    imported_data = None
    import_path = None

    file_path = filedialog.askopenfilename(
        title="Select imported save", 
        filetypes=[("All Files", "*.*")]
    )
    if not file_path:
        return
    
    # Split into imported folder
    split_files(file_path, "imported")

    # Show character selection window
    display_char_name("imported")  






def delete_goods(item_name_delete):
    global data, goods

    item_id= goods_and_magic_json.get(item_name_delete)

    item_id_bytes = bytes.fromhex(item_id)
    if len(item_id_bytes) != 4:
        print('length error')
        return
    
    item_id_int= int.from_bytes(item_id_bytes, 'little')

    found = False

    for item_ids, _, _, offset in goods:
        if item_ids == item_id_int:

            data = data[:offset] + b'\x00' * 12 + data[offset+12:]

            found = True
            break 

    if not found:
        print('no item name exists')

def delete_goods_storage(item_name_delete):
    global data, storage_goods

    item_id= goods_and_magic_json.get(item_name_delete)

    item_id_bytes = bytes.fromhex(item_id)
    if len(item_id_bytes) != 4:
        print('length error')
        return
    
    item_id_int= int.from_bytes(item_id_bytes, 'little')

    found = False

    for item_ids, _, _, offset in storage_goods:
        if item_ids == item_id_int:

            data = data[:offset] + b'\x00' * 12 + data[offset+12:]

            found = True
            break 

    if not found:
        print('no item name exists')

def toggle_grace(name):
    """Toggle grace unlocked state in save data."""
    global data
    data = bytearray(data)
    event_flag_start_offset = save_struct(data)

    for grace in graces_json:
        if grace["grace_name"] != name:
            continue

        offset = int(grace["offset"], 16) + event_flag_start_offset[0]
        index = grace["index"]

        current_value = data[offset]
        if grace_vars[name].get():  # checked → unlock
            new_value = current_value | (1 << index)
        else:  # unchecked → lock
            new_value = current_value & ~(1 << index)

        struct.pack_into('B', data, offset, new_value)


    data = bytes(data)

def storage_par():
    global data
    global storage_weapons, storage_aow, storage_armors, storage_goods, storage_rings, storage_empty, storage_inventory_items
    
    storage_inventory_items=[]
    storage_weapons = []
    storage_aow = []
    storage_armors = []
    storage_goods = []
    storage_rings = []
    storage_empty=[]

    _,_,_,start_offset = save_struct(data)
    start_offset=start_offset+4
    end_offset = start_offset+ 0x6006


    items = parse_inventory(data, start_offset, end_offset)

    for item in items:
        type_bits = item.gaitem_handle & 0xF0000000
        storage_inventory_items.append((item.gaitem_handle, item.quantity, item.index, item.offset))

        if type_bits == ITEM_TYPE_WEAPON:
            storage_weapons.append((item.gaitem_handle, item.quantity, item.index, item.offset))
        elif type_bits == ITEM_TYPE_ARMOR:
            storage_armors.append((item.gaitem_handle, item.quantity, item.index, item.offset))
        elif type_bits == ITEM_TYPE_AOW:
            storage_aow.append((item.gaitem_handle, item.quantity, item.index, item.offset))
        elif type_bits == ITEM_TYPE_GOOD:
            storage_goods.append((item.gaitem_handle, item.quantity, item.index, item.offset))
        elif type_bits == ITEM_TYPE_RINGS:
            storage_rings.append((item.gaitem_handle, item.quantity, item.index, item.offset))
        elif type_bits == ITEM_TYPE_EMPTY:
            storage_empty.append((item.gaitem_handle, item.quantity, item.index, item.offset))



    



def save_struct(save_data):
    """
    The defined variable is the end of that struct
    """
    gaprint(save_data)
    inventoryprint()
    sort_list()
    ga_item_sorted = sorted(ga_items, key=lambda x: x[2])
    GA_item_handle_size= ga_item_sorted [-1][2] + 8
    Player_data=GA_item_handle_size+ 0x1B0
    SP_effect= Player_data + 0xD0
    equiped_item_index= SP_effect+0x58
    active_equiped_items= equiped_item_index + 0x1c
    equiped_items_id=active_equiped_items+0x58
    active_equiped_items_ga=equiped_items_id+0x58
    iventory_held=active_equiped_items_ga+0x9010
    equiped_spells=iventory_held+0x74
    equiped_items=equiped_spells+ 0x8c
    equiped_gestures= equiped_items+ 0x18
    equiped_projc_size = struct.unpack_from("<I", save_data, equiped_gestures)[0]

    equiped_projctile= equiped_gestures + (equiped_projc_size*8 + 4)
    equiped_arraments= equiped_projctile+ 0x9C
    equipe_physics=equiped_arraments+ 0xC
    face_data=equipe_physics+ 0x12f
    inevntory_storage_box= face_data+ 0x6010
    gestures= inevntory_storage_box+ 0x100

    unlocked_region_size = struct.unpack_from("<I", save_data, gestures)[0]
    unlocked_region= gestures+ (unlocked_region_size*4 + 4)
    extra_1= 0x1
    horse= unlocked_region+ 0x28+ extra_1
    extra_2= 0x8
    blood_stain=horse+ 0x44 +extra_2
    extra_3= 0x34
    menu_profile= blood_stain+ 0x1008 + extra_3
    ga_items_data_other= menu_profile+ 0x1b588 # need to confirm
    extra_4=0x3
    toturial_data= ga_items_data_other+ 0x408 + extra_4
    total_death=toturial_data+ 0x4
    char_type= total_death+ 0x4
    in_online= char_type+ 0x1
    online_char_type= in_online+0x4
    last_rested_grace=online_char_type+ 0x4
    not_alone_flag= last_rested_grace+ 0x1
    extra_5= 0x4
    ingame_timer= not_alone_flag+ 0x4+ extra_5
    extra_6= 0x1
    event_flag= ingame_timer+ 0x1bf99f + extra_6
    
    filedarea_size=struct.unpack_from("<I", save_data, event_flag)[0]
    FieldArea= event_flag  + (filedarea_size + 4)

    worldarea_size=struct.unpack_from("<I", save_data, FieldArea)[0]
    WorldArea= FieldArea+ (worldarea_size+4)

    Worldgeom_size=struct.unpack_from("<I", save_data, WorldArea)[0]
    WorldGeom= WorldArea+ (Worldgeom_size + 4)


    Worldgeom2_size=struct.unpack_from("<I", save_data, WorldGeom)[0]
    WorldGeom2= WorldGeom+ (Worldgeom2_size + 4)

    rendman_size=struct.unpack_from("<I", save_data, WorldGeom2)[0]
    rendman= WorldGeom2+ (rendman_size+4)

    extra_7=0x2
    player_coord= rendman + 0x3d + extra_7
    extra_8=0x4
    SpawnPointEntityId=player_coord+ 0x4 + extra_8
    extra_9=0x1
    TempSpawnPointEntityId=SpawnPointEntityId +0x4 + extra_9

    NetMan=TempSpawnPointEntityId+0x20004
    WorldAreaWeather=NetMan+0xC
    WorldAreaTime= WorldAreaWeather+0xC
    BaseCharacterVersion=WorldAreaTime+0x10
    steam_id=BaseCharacterVersion+0x8
    PS5Activity=steam_id+0x20
    DLC_data=PS5Activity+0x32
    PlayerGameDataHash=DLC_data+ 0x80 # could be used as the end offset for item deletion
    
    return ingame_timer, PlayerGameDataHash, BaseCharacterVersion, face_data

    

        
file_open_frame = tk.Frame(window)
file_open_frame.pack(side="left", fill="y", padx=10, pady=5)

ttk.Button(file_open_frame, text="Open Save File", command=open_file).pack(pady=5, anchor="w")
file_name_label = tk.Label(file_open_frame, text="No file selected", anchor="w")
file_name_label.pack(pady=5, anchor="w")




#Char tab
notebook = ttk.Notebook(window)


# Character Tab
name_tab = ttk.Frame(notebook)

# === Character Name Section ===
ttk.Label(name_tab, text="Current Character Name:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
ttk.Label(name_tab, textvariable=current_name_var).grid(row=0, column=1, padx=10, pady=10)

ttk.Label(name_tab, text="New Character Name:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
ttk.Entry(name_tab, textvariable=new_name_var, width=20).grid(row=1, column=1, padx=10, pady=10)

ttk.Button(
    name_tab,
    text="Update Name",
    command=lambda: update_name(new_name_var.get())
).grid(row=2, column=0, columnspan=2, pady=10)


# === NG+ Section ===
ttk.Label(name_tab, text="Current NG+:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
ttk.Label(name_tab, textvariable=current_ng_var).grid(row=3, column=1, padx=10, pady=10)

ttk.Label(name_tab, text="New NG+:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
ttk.Entry(name_tab, textvariable=new_ng_var, width=20).grid(row=4, column=1, padx=10, pady=10)

ttk.Button(
    name_tab,
    text="Update NG+",
    command=lambda: update_ng(new_ng_var.get())
).grid(row=5, column=0, columnspan=2, pady=10)


# === Runes Section ===
ttk.Label(name_tab, text="Current Runes:").grid(row=6, column=0, padx=10, pady=10, sticky="e")
ttk.Label(name_tab, textvariable=current_runes_var).grid(row=6, column=1, padx=10, pady=10)

ttk.Label(name_tab, text="New Runes Value (MAX 999999999):").grid(row=7, column=0, padx=10, pady=10, sticky="e")
ttk.Entry(name_tab, textvariable=new_runes_var, width=20).grid(row=7, column=1, padx=10, pady=10)

ttk.Button(
    name_tab,
    text="Update Runes",
    command=lambda: update_runes(new_runes_var.get())
).grid(row=8, column=0, columnspan=2, pady=10)



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


# --- Player Inventory Tab ---
inventory_tab = ttk.Frame(notebook)

# --- Type filter ---
filter_frame = tk.Frame(inventory_tab)
filter_frame.pack(side="top", fill="x", padx=10, pady=5)

tk.Label(filter_frame, text="Filter by Type:").pack(side="left", padx=5)
inventory_type_var = tk.StringVar(value="Ash of War")  # default to Goods
type_options = ["Ash of War", "Weapons", "Armors", "Goods", "Talismans"]
type_menu = ttk.OptionMenu(filter_frame, inventory_type_var, type_options[0], *type_options)
type_menu.pack(side="left", padx=5)

# --- Treeview setup ---
columns = ("Type", "Name", "Quantity", "Level", "Ash of War")
inventory_tree = ttk.Treeview(inventory_tab, columns=columns, show="headings", height=20)
for col in columns:
    inventory_tree.heading(col, text=col)
    inventory_tree.column(col, width=150, anchor="center")

scrollbar = ttk.Scrollbar(inventory_tab, orient="vertical", command=inventory_tree.yview)
inventory_tree.configure(yscrollcommand=scrollbar.set)

inventory_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
scrollbar.pack(side="right", fill="y")

##Storage box
# --- Player Inventory Tab ---
storage_tab = ttk.Frame(notebook)

# --- Type filter ---
filter_storage_frame = tk.Frame(storage_tab)
filter_storage_frame.pack(side="top", fill="x", padx=10, pady=5)

tk.Label(filter_storage_frame, text="Filter by Type:").pack(side="left", padx=5)
storage_type_var = tk.StringVar(value="Talismans")  # default to Goods
type_optionss = ["Talismans","Goods" ]
type_menus = ttk.OptionMenu(filter_storage_frame, storage_type_var, type_optionss[0], *type_optionss)
type_menus.pack(side="left", padx=5)

# --- Treeview setup ---
columnss = ("Type", "Name", "Quantity")
storage_tree = ttk.Treeview(storage_tab, columns=columnss, show="headings", height=20)
for col in columnss:
    storage_tree.heading(col, text=col)
    storage_tree.column(col, width=150, anchor="center")

scrollbar = ttk.Scrollbar(storage_tab, orient="vertical", command=storage_tree.yview)
storage_tree.configure(yscrollcommand=scrollbar.set)

storage_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
scrollbar.pack(side="right", fill="y")
####
def display_storage(item_type=None):
    global data
    if item_type is None:
        item_type = storage_type_var.get()

    # Clear previous rows
    storage_tree.delete(*storage_tree.get_children())

    if item_type == "Goods":
        source_json = goods_and_magic_json
        source_items = storage_inventory_items
        for name, id_hex in source_json.items():
            id_int = int.from_bytes(bytes.fromhex(id_hex), "little")
            for item_id, quantity, _, _ in source_items:
                if id_int == item_id:
                    storage_tree.insert("", "end", values=(item_type, name, quantity))

    elif item_type == "Talismans":
        source_json = talisman_json
        source_items = storage_inventory_items
        for name, id_hex in source_json.items():
            id_int = int.from_bytes(bytes.fromhex(id_hex), "little")
            for item_id, quantity, _, _ in source_items:
                if id_int == item_id:
                    storage_tree.insert("", "end", values=(item_type, name, 1))

    return data


###

# --- Display inventory with weapon Level & AOW ---
def display_inventory(item_type=None):
    global data
    if item_type is None:
        item_type = inventory_type_var.get()
    inventory_tree.delete(*inventory_tree.get_children())

    if item_type == "Goods":
        source_json = goods_and_magic_json
        source_items = inventory_items
        for name, id_hex in source_json.items():
            id_int = int.from_bytes(bytes.fromhex(id_hex), "little")
            for item_id, quantity, _, _ in source_items:
                if id_int == item_id:
                    inventory_tree.insert("", "end", values=(item_type, name, quantity, "-", "-"))

    elif item_type == "Weapons":
        source_json = weapons_json
        source_items = ga_items
        for name, id_hex in source_json.items():
            base_id = int.from_bytes(bytes.fromhex(id_hex), "little")

            for gaitem_handle, item_id, offset in source_items:
                if (item_id & 0xFFFFFF00) == (base_id & 0xFFFFFF00):
                    if name == "Unarmed":
                        continue
                    level = item_id - base_id
                    aow_id = int.from_bytes(data[offset+16:offset+20], "little")
                    aow_name = next((n for n, h in aow_json.items() if int.from_bytes(bytes.fromhex(h), "little") == aow_id), "None")

                    # Insert row with offset and current item_id as tags
                    inventory_tree.insert(
                        "", "end",
                        values=(item_type, name, 1, level, aow_name),
                        tags=(str(offset), str(item_id))
                    )

    elif item_type == "Armors":
        source_json = armor_json
        source_items = ga_items
        for name, id_hex in source_json.items():
            id_int = int.from_bytes(bytes.fromhex(id_hex), "little")
            for gaitem_handle, item_id, offset in source_items:
                if id_int == item_id:
                    inventory_tree.insert("", "end", values=(item_type, name, 1, "-", "-"))

    elif item_type == "Ash of War":
        source_json = aow_json
        source_items = ga_items
        for name, id_hex in source_json.items():
            id_int = int.from_bytes(bytes.fromhex(id_hex), "little")
            for gaitem_handle, item_id, offset in source_items:
                if id_int == item_id:
                    inventory_tree.insert("", "end", values=(item_type, name, 1, "-", "-"))

    elif item_type == "Talismans":
        source_json = talisman_json
        source_items = inventory_items
        for name, id_hex in source_json.items():
            id_int = int.from_bytes(bytes.fromhex(id_hex), "little")
            for item_id, quantity, _, _ in source_items:
                if id_int == item_id:
                    inventory_tree.insert("", "end", values=(item_type, name, 1, "-", "-"))
    return data



def update_weapon():
    selected = inventory_tree.selection()
    if not selected:
        print("No weapon selected")
        return

    item = inventory_tree.item(selected[0])
    item_type, name, _, _, _ = item["values"]
    if item_type != "Weapons":
        print("Selected item is not a weapon")
        return

    # Get offset from tag
    offset = int(item["tags"][0])

    global data

    # --- Update level ---
    try:
        new_level = int(weapon_level_entry.get())
        if new_level > 25:
            messagebox.showerror("Error", "Level cannot exceed 25")
            return
    except ValueError:
        new_level = None

    # --- Update AOW ---
    new_aow_name = aow_var.get()
    if new_aow_name == "None":
        new_aow_id = 0
    else:
        # spawn handle safely
        aow_handle = spawn_weapons(new_aow_name, "aow")
        new_aow_id = int.from_bytes(aow_handle, "little")

    # --- Apply updates ---
    base_id = int.from_bytes(bytes.fromhex(weapons_json[name]), "little")

    if new_level is not None:
        new_item_id = base_id + new_level
        data = data[:offset+4] + new_item_id.to_bytes(4, "little") + data[offset+8:]

    if new_aow_id:
        aow_offset = offset + 16
        data = data[:aow_offset] + new_aow_id.to_bytes(4, "little") + data[aow_offset+4:]
    elif new_aow_name == "None":
        # clear AOW slot
        aow_offset = offset + 16
        data = data[:aow_offset] + (0).to_bytes(4, "little") + data[aow_offset+4:]



    gaprint(data)         
    inventoryprint()   
    sort_list()        

    # Update Treeview row directly
    inventory_tree.item(
        selected[0],
        values=(item_type, name, 1, new_level if new_level is not None else "-", new_aow_name)
    )








# --- Initial load ---
display_inventory("Ash of War")
#storage
display_storage("Talismans")
# --- Functions ---
def update_selected_quantity():
    global data
    selected = inventory_tree.selection()
    if not selected:
        print("No item selected")
        return
    item = inventory_tree.item(selected[0])
    item_type, item_name, quantity = item["values"][:3]
    
    if item_type != "Goods":
        print("Quantity can only be updated for Goods")
        return

    try:
        new_quantity = int(quantity_entry.get())
    except ValueError:
        print("Invalid quantity")
        return

    for gaitem_handle, quantity_val, index, offset in inventory_items:
        item_id = goods_and_magic_json[item_name]
        item_id_bytes = bytes.fromhex(item_id)
        item_id_int = int.from_bytes(item_id_bytes, "little")
        if gaitem_handle == item_id_int:
            quantity_offset = offset + 4
            
            data = data[:quantity_offset] + new_quantity.to_bytes(4, "little") + data[quantity_offset+4:]
            inventoryprint()
            display_inventory()
            return data

def delete_selected_item():
    selected = inventory_tree.selection()
    if not selected:
        print("No item selected")
        return
    item = inventory_tree.item(selected[0])
    # Only unpack the first three columns
    item_type, item_name, quantity = item["values"][:3]
    
    if item_type != "Goods":
        messagebox.showinfo("Info", "Only Goods can be deleted")
        return
    
    delete_goods(item_name)
    inventoryprint()
    display_inventory()

##
def update_selected_quantity_storage():
    global data
    selected = storage_tree.selection()
    if not selected:
        print("No item selected")
        return
    item = storage_tree.item(selected[0])
    item_type, item_name, quantity = item["values"][:3]
    
    if item_type != "Goods":
        messagebox.showinfo("Info", "Quantity can only be updated for Goods")
        return

    try:
        new_quantity = int(storage_quantity_entry.get())  
    except ValueError:
        messagebox.showerror("Error", "Invalid quantity")
        return

    for gaitem_handle, quantity_val, index, offset in storage_inventory_items:
        item_id = goods_and_magic_json[item_name]
        item_id_bytes = bytes.fromhex(item_id)
        item_id_int = int.from_bytes(item_id_bytes, "little")
        if gaitem_handle == item_id_int:
            quantity_offset = offset + 4
            
            data = data[:quantity_offset] + new_quantity.to_bytes(4, "little") + data[quantity_offset+4:]
            storage_par()
            display_storage(storage_type_var.get())  
            return data

def delete_selected_item_storage():
    selected = storage_tree.selection()
    if not selected:
        print("No item selected")
        return
    item = storage_tree.item(selected[0])
    # Only unpack the first three columns
    item_type, item_name, quantity = item["values"][:3]
    
    if item_type != "Goods":
        messagebox.showinfo("Info", "Only Goods can be deleted")
        return
    
    delete_goods_storage(item_name)
    storage_par()
    display_storage(storage_type_var.get())
    
    
    

## --- Control frames ---
goods_frame = tk.Frame(inventory_tab)
tk.Label(goods_frame, text="New Quantity:").pack(side="left", padx=5)
quantity_entry = tk.Entry(goods_frame, width=10)
quantity_entry.pack(side="left", padx=5)
ttk.Button(goods_frame, text="Update Quantity", command=update_selected_quantity).pack(side="left", padx=5)
ttk.Button(goods_frame, text="Delete Item", command=delete_selected_item).pack(side="left", padx=5)

#storage
storage_frame = tk.Frame(storage_tab)
tk.Label(storage_frame, text="New Quantity:").pack(side="left", padx=5)
storage_quantity_entry = tk.Entry(storage_frame, width=10)  # ✅ Different name!
storage_quantity_entry.pack(side="left", padx=5)
ttk.Button(storage_frame, text="Update Quantity", command=update_selected_quantity_storage).pack(side="left", padx=5)
ttk.Button(storage_frame, text="Delete Item", command=delete_selected_item_storage).pack(side="left", padx=5)
#
weapon_frame = tk.Frame(inventory_tab)
tk.Label(weapon_frame, text="Weapon Level:").pack(side="left", padx=5)
weapon_level_var = tk.IntVar()
weapon_level_entry = tk.Entry(weapon_frame, textvariable=weapon_level_var, width=5)
weapon_level_entry.pack(side="left", padx=5)

tk.Label(weapon_frame, text="Ash of War:").pack(side="left", padx=5)
aow_options = ["None"] + list(aow_json.keys())
aow_var = tk.StringVar(value="None")
aow_menu = ttk.OptionMenu(weapon_frame, aow_var, *aow_options)
aow_menu.pack(side="left", padx=5)
tk.Button(weapon_frame, text="Update Weapon", command=update_weapon).pack(side="left", padx=5)

# --- Function to show correct controls ---
def update_control_frames(item_type):
    goods_frame.pack_forget()
    weapon_frame.pack_forget()

    if item_type == "Goods":
        goods_frame.pack(side="bottom", fill="x", padx=10, pady=5)
    elif item_type == "Weapons":
        weapon_frame.pack(side="bottom", fill="x", padx=10, pady=5)

# Call this on type change
def on_type_change(*args):
    item_type = inventory_type_var.get()
    display_inventory(item_type)
    update_control_frames(item_type)

inventory_type_var.trace_add("write", on_type_change)

#storage
# --- Function to show correct controls ---
def update_control_frames_storage(item_type):
    storage_frame.pack()

    if item_type == "Goods":
        goods_frame.pack(side="bottom", fill="x", padx=10, pady=5)

# Call this on type change
def on_type_change_storage(*args):
    item_type = storage_type_var.get()
    display_storage(item_type)
    update_control_frames_storage(item_type)

storage_type_var.trace_add("write", on_type_change_storage)

#Tabs
notebook.add(name_tab, text="Character")
notebook.add(stats_tab, text="Stats")
notebook.add(inventory_tab, text="Player Inventory")
notebook.add(storage_tab, text="Storage Box")
# --- Pack notebook into main window ---
notebook.pack(expand=True, fill="both", padx=10, pady=10)
#World flags
# --- World Flags Tab ---
world_flags_tab = ttk.Frame(notebook)
notebook.add(world_flags_tab, text="World Flags")

# --- Main Container with Better Padding ---
main_container = ttk.Frame(world_flags_tab)
main_container.pack(fill="both", expand=True, padx=15, pady=15)

# --- Controls Frame (Top Section) ---
controls_frame = ttk.LabelFrame(main_container, text="Quick Actions", padding=10)
controls_frame.pack(fill="x", pady=(0, 10))

# Unlock All checkboxes in a grid layout
unlock_base_var = tk.IntVar()
unlock_dlc_var = tk.IntVar()

ttk.Checkbutton(
    controls_frame, 
    text="🌍 Unlock All Base Game Graces", 
    variable=unlock_base_var,
    command=lambda: toggle_all_graces("Base Game", unlock_base_var.get())
).grid(row=0, column=0, sticky="w", padx=10, pady=5)

ttk.Checkbutton(
    controls_frame, 
    text="⭐ Unlock All DLC Graces", 
    variable=unlock_dlc_var,
    command=lambda: toggle_all_graces("DLC", unlock_dlc_var.get())
).grid(row=0, column=1, sticky="w", padx=10, pady=5)

# --- Graces List Frame ---
graces_frame = ttk.LabelFrame(main_container, text="Grace Sites", padding=5)
graces_frame.pack(fill="both", expand=True)

# --- Canvas with Scrollbar ---
canvas = tk.Canvas(graces_frame, highlightthickness=0, bg='white')
scrollbar = ttk.Scrollbar(graces_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg='white')

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Enable mousewheel scrolling
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


# --- Populate checkboxes ---
def init_graces_tab():
    global grace_vars, unlock_base_var, unlock_dlc_var

    # Clear previous checkboxes (if any)
    for child in scrollable_frame.winfo_children():
        child.destroy()

    grace_vars = {}

    event_offset = save_struct(data)[0]

    # Recreate frames fresh
    base_game_frame = ttk.LabelFrame(scrollable_frame, text="Base Game Graces", padding=10)
    base_game_frame.pack(fill="x", padx=10, pady=5)
    
    dlc_frame = ttk.LabelFrame(scrollable_frame, text="DLC Graces", padding=10)
    dlc_frame.pack(fill="x", padx=10, pady=5)

    # Populate with updated save data
    for i, grace in enumerate(graces_json):
        name = grace["grace_name"]
        offset = int(grace["offset"], 16) + event_offset
        index = grace["index"]

        unlocked = (data[offset] & (1 << index)) != 0
        var = tk.IntVar(value=1 if unlocked else 0)
        grace_vars[name] = var

        parent_frame = base_game_frame if i < 314 else dlc_frame

        cb = tk.Checkbutton(
            parent_frame,
            text=name,
            variable=var,
            onvalue=1,
            offvalue=0,
            command=lambda n=name: toggle_grace(n)
        )
        cb.pack(anchor="w", padx=10, pady=3)


def toggle_all_graces(category, value):
    global data
    data = bytearray(data)  # make it mutable
    event_offset = save_struct(data)[0]  # safe, data loaded
    
    for i, grace in enumerate(graces_json):
        if (category == "Base Game" and i >= 314) or (category == "DLC" and i < 314):
            continue
        name = grace["grace_name"]
        offset = int(grace["offset"], 16) + event_offset
        index = grace["index"]

        # update checkbox variable
        grace_vars[name].set(value)

        # update data
        current_value = data[offset]
        if value:  # unlock
            new_value = current_value | (1 << index)
        else:      # lock
            new_value = current_value & ~(1 << index)
        struct.pack_into("B", data, offset, new_value)


    # convert back to immutable bytes
    data = bytes(data)

#Item spawn
# --- Spawn Items Tab ---
spawn_items_tab = ttk.Frame(notebook)
notebook.add(spawn_items_tab, text="Spawn Items")

# --- Internal notebook for Goods, Talismans, Weapons, Armors, AoW ---
items_notebook = ttk.Notebook(spawn_items_tab)
items_notebook.pack(fill="both", expand=True)

# --- Goods Tab ---
goods_tab = ttk.Frame(items_notebook)
items_notebook.add(goods_tab, text="Goods and Magic")

# --- Talismans Tab ---
talisman_tab = ttk.Frame(items_notebook)
items_notebook.add(talisman_tab, text="Talismans")

# --- Weapons Tab ---
weapons_tab = ttk.Frame(items_notebook)
items_notebook.add(weapons_tab, text="Weapons")

# --- Armors Tab ---
armors_tab = ttk.Frame(items_notebook)
items_notebook.add(armors_tab, text="Armors")

# --- Ashes of War Tab ---
aow_tab = ttk.Frame(items_notebook)
items_notebook.add(aow_tab, text="Ashes of War")

# --- Goods Search Bar (at top) ---
select_all_var = tk.IntVar(value=0)
goods_category_ranges = {
    "Consumables": (0, 24),
    "Meats": (24, 39),
    "Throwables": (39, 56),
    "Grease": (56, 75),
    "Crafting: Animal": (75, 106),
    "Crafting: Plant": (106, 136),
    "Crafting: Inorganic": (136, 142),
    "Smithing Stones": (142, 151),
    "Somber Smithing Stones": (151, 161),
    "Grave Glovewort": (161, 171),
    "Ghost Glovewort": (171, 181),
    "Perfumes": (181, 184),
    "Pots": (184, 216),
    "Crystal Tears": (216, 245),
    "Prattling Pates": (245, 253),
    "Bell Bearings": (253, 305),
    "Spirit Ashes": (305, 369),
    "Sorceries": (369, 440),
    "Incantations": (440, 540)
}
goods_names = list(goods_and_magic_sorted_json.keys())

goods_categories = {
    cat: goods_names[start:end]
    for cat, (start, end) in goods_category_ranges.items()
}

tk.Label(goods_tab, text="Search Goods:").pack(anchor="w", padx=5, pady=2)
goods_search_var = tk.StringVar()
goods_search_entry = tk.Entry(goods_tab, textvariable=goods_search_var)
goods_search_entry.pack(fill="x", anchor="w", padx=5, pady=2)

# --- Goods Treeview with category dropdown ---
goods_tree_frame = tk.Frame(goods_tab)
goods_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

# Dropdown for category filter
goods_category_var = tk.StringVar()
goods_category_dropdown = ttk.Combobox(
    goods_tree_frame,
    textvariable=goods_category_var,
    values=list(goods_categories.keys()),
    state="readonly"
)
goods_category_dropdown.pack(fill="x", padx=5, pady=5)

# Treeview
goods_tree = ttk.Treeview(goods_tree_frame, show="tree", height=20)  # FIX: only show tree
goods_tree.heading("#0", text="Items")
goods_tree.pack(fill="both", expand=True, side="left")

scrollbar = ttk.Scrollbar(goods_tree_frame, orient="vertical", command=goods_tree.yview)
goods_tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Cache item IDs and vars
item_vars = {}
item_ids = {}

def load_goods_category(category):
    """Clear and load selected category items into the tree."""
    goods_tree.delete(*goods_tree.get_children())
    item_vars.clear()
    item_ids.clear()

    items = goods_categories.get(category, [])
    for item in items:
        var = tk.IntVar(value=0)
        item_id = goods_tree.insert("", "end", text=item, tags=("item",))
        item_vars[item] = var
        item_ids[item] = item_id

    # Reset select-all when category changes
    select_all_var.set(0)

# Dropdown event
def on_category_change(event=None):
    selected_cat = goods_category_var.get()
    if selected_cat:
        load_goods_category(selected_cat)

goods_category_dropdown.bind("<<ComboboxSelected>>", on_category_change)

# Default: load first category
if goods_categories:
    first_cat = list(goods_categories.keys())[0]
    goods_category_var.set(first_cat)
    load_goods_category(first_cat)

# Click toggling
def on_tree_click(event):
    item = goods_tree.identify('item', event.x, event.y)
    if item:
        item_text = goods_tree.item(item, "text")
        if item_text in item_vars:
            current = item_vars[item_text].get()
            item_vars[item_text].set(1 if current == 0 else 0)
            # Update visual feedback
            if item_vars[item_text].get():
                goods_tree.item(item, tags=("item", "checked"))
            else:
                goods_tree.item(item, tags=("item",))

goods_tree.bind("<Button-1>", on_tree_click)
goods_tree.tag_configure("checked", background="lightblue")

# --- Category-level "Select All" for current category ---


def toggle_current_category():
    current_state = select_all_var.get()
    current_cat = goods_category_var.get()
    if not current_cat:
        return
    
    for item in goods_categories.get(current_cat, []):
        item_vars[item].set(current_state)
        if current_state:
            goods_tree.item(item_ids[item], tags=("item", "checked"))
        else:
            goods_tree.item(item_ids[item], tags=("item",))

select_all_checkbox = tk.Checkbutton(
    goods_tab,
    text="Select All in Current Category",
    variable=select_all_var,
    command=toggle_current_category
)
select_all_checkbox.pack(anchor="w", padx=5, pady=5)

# --- Search filter ---
search_after_id = None

def filter_goods():
    term = goods_search_var.get().lower()
    current_cat = goods_category_var.get()
    if not current_cat:
        return

    goods_tree.delete(*goods_tree.get_children())
    item_vars.clear()
    item_ids.clear()

    for item in goods_categories.get(current_cat, []):
        if term in item.lower():
            var = tk.IntVar(value=0)
            item_id = goods_tree.insert("", "end", text=item, tags=("item",))
            item_vars[item] = var
            item_ids[item] = item_id

def debounced_filter(*args):
    global search_after_id
    if search_after_id:
        goods_tab.after_cancel(search_after_id)
    search_after_id = goods_tab.after(200, filter_goods)

goods_search_var.trace_add("write", debounced_filter)

# --- Add selected goods button ---
tk.Label(goods_tab, text="Quantity:").pack(anchor="w", padx=5, pady=2)
goods_quantity_entry = tk.Entry(goods_tab, width=10)
goods_quantity_entry.insert(0, "1")
goods_quantity_entry.pack(anchor="w", padx=5, pady=2)

def add_selected_goods():
    quantity = int(goods_quantity_entry.get())
    for item_name, var in item_vars.items():
        if var.get():
            spawn_goods(item_name, quantity, "goods")
    messagebox.showinfo("Info", "Selected Goods added to inventory.")

tk.Button(goods_tab, text="Add Selected Goods", command=add_selected_goods).pack(padx=5, pady=2)

def add_selected_goods_stack():
    quantity = int(goods_quantity_entry.get())
    for item_name, var in item_vars.items():
        if var.get():
            spawn_goods(item_name, quantity, "goods", Stack=True)
    messagebox.showinfo("Info", "Selected Goods added to inventory.")

tk.Button(goods_tab, text="Stack Selected Goods", command=add_selected_goods_stack).pack(padx=6, pady=3)

# --- Talismans with optimized search ---
tk.Label(talisman_tab, text="Search Talismans:").pack(anchor="w", padx=5, pady=2)
talisman_search_var = tk.StringVar()
talisman_search_entry = tk.Entry(talisman_tab, textvariable=talisman_search_var)
talisman_search_entry.pack(anchor="w", padx=5, pady=2)

# NEW: Cache talisman names as list
talisman_names = list(talisman_json.keys())

talisman_frame = tk.Frame(talisman_tab)
talisman_frame.pack(fill="both", expand=True, padx=5, pady=5)

talisman_listbox = tk.Listbox(talisman_frame, selectmode="extended")
talisman_listbox.pack(fill="both", expand=True, side="left")

talisman_scrollbar = ttk.Scrollbar(talisman_frame, orient="vertical", command=talisman_listbox.yview)
talisman_listbox.configure(yscrollcommand=talisman_scrollbar.set)
talisman_scrollbar.pack(side="right", fill="y")

for name in talisman_names:
    talisman_listbox.insert("end", name)

# NEW: Debounce talisman search
talisman_search_after_id = None

def filter_talismans():
    search_term = talisman_search_var.get().lower()
    
    if not search_term:
        # Restore all items
        talisman_listbox.delete(0, "end")
        for name in talisman_names:
            talisman_listbox.insert("end", name)
        return
    
    # Filter list
    talisman_listbox.delete(0, "end")
    for name in talisman_names:
        if search_term in name.lower():
            talisman_listbox.insert("end", name)

def debounced_talisman_filter(*args):
    global talisman_search_after_id
    if talisman_search_after_id:
        talisman_tab.after_cancel(talisman_search_after_id)
    talisman_search_after_id = talisman_tab.after(200, filter_talismans)

talisman_search_var.trace_add("write", debounced_talisman_filter)

# --- Add Selected Talismans ---
def add_selected_talismans():
    for i in talisman_listbox.curselection():
        name = talisman_listbox.get(i)
        spawn_goods(name, 1, "talisman")
    messagebox.showinfo("Info", "Selected Talismans added to inventory.")
tk.Button(talisman_tab, text="Add Selected Talismans", command=add_selected_talismans).pack(padx=5, pady=2)

# --- Add All Talismans ---
def add_all_talismans():
    for name in talisman_names:  # Use cached list
        spawn_goods(name, 1, "talisman")
    messagebox.showinfo("Info", "All Talismans added to inventory.")
tk.Button(talisman_tab, text="Add All Talismans", command=add_all_talismans).pack(padx=5, pady=2)

# --- Weapons Tab with optimized search ---
weapon_categories = {
    "Daggers": (0, 16),
    "Straight Swords": (16, 37),
    "Greatswords": (37, 57),
    "Colossal Swords": (57, 68),
    "Thrusting Swords": (68, 75),
    "Heavy Thrusting Swords": (75, 79),
    "Curved Swords": (79, 93),
    "Curved Greatswords": (93, 102),
    "Katanas": (102, 110),
    "Twinblades": (110, 116),
    "Hammers": (116, 131),
    "Great Hammers": (131, 137),
    "Warhammers": (137, 145),
    "Flails": (145, 150),
    "Axes": (150, 162),
    "Greataxes": (162, 174),
    "Spears": (174, 190),
    "Great Spears": (190, 196),
    "Halberds": (196, 212),
    "Reapers": (212, 216),
    "Whips": (216, 222),
    "Fists": (222, 231),
    "Claws": (231, 235),
    "Colossal Weapons": (235, 250),
    "Torches": (250, 256),
    "Shields": (256, 300),
    "Great Shields": (300, 325),
    "Staves": (325, 343),
    "Seals": (343, 352),
    "Light Bows": (352, 357),
    "Bows": (357, 364),
    "Greatbows": (364, 368),
    "Crossbows": (368, 375),
    "Ballistae": (375, 377),
    "Arrows": (377, 409),
    "Greatarrows": (409, 416),
    "Bolts": (416, 436),
    "Greatbolts": (436, 440)
}

tk.Label(weapons_tab, text="Search Weapons:").pack(anchor="w", padx=5, pady=2)
weapons_search_var = tk.StringVar()
weapons_search_entry = tk.Entry(weapons_tab, textvariable=weapons_search_var)
weapons_search_entry.pack(anchor="w", padx=5, pady=2)

# Cache weapon names as list
weapons_names = list(weapons_sorted_json.keys())

weapons_frame = tk.Frame(weapons_tab)
weapons_frame.pack(fill="both", expand=True, padx=5, pady=5)

weapons_listbox = tk.Listbox(weapons_frame, selectmode="extended")
weapons_listbox.pack(fill="both", expand=True, side="left")

weapons_scrollbar = ttk.Scrollbar(weapons_frame, orient="vertical", command=weapons_listbox.yview)
weapons_listbox.configure(yscrollcommand=weapons_scrollbar.set)
weapons_scrollbar.pack(side="right", fill="y")

for name in weapons_names:
    weapons_listbox.insert("end", name)

# Debounce weapon search
weapons_search_after_id = None

def filter_weapons():
    search_term = weapons_search_var.get().lower()
    
    if not search_term:
        weapons_listbox.delete(0, "end")
        for name in weapons_names:
            weapons_listbox.insert("end", name)
        return
    
    weapons_listbox.delete(0, "end")
    for name in weapons_names:
        if search_term in name.lower():
            weapons_listbox.insert("end", name)

def debounced_weapons_filter(*args):
    global weapons_search_after_id
    if weapons_search_after_id:
        weapons_tab.after_cancel(weapons_search_after_id)
    weapons_search_after_id = weapons_tab.after(200, filter_weapons)

weapons_search_var.trace_add("write", debounced_weapons_filter)
selected_category = tk.StringVar(value="All")

category_dropdown = ttk.Combobox(
    weapons_tab, 
    textvariable=selected_category,
    values=["All"] + list(weapon_categories.keys()),
    state="readonly"
)
category_dropdown.pack(anchor="w", padx=5, pady=2)

def update_weapon_list(*args):
    weapons_listbox.delete(0, "end")
    if selected_category.get() == "All":
        for name in weapons_names:
            weapons_listbox.insert("end", name)
    else:
        start, end = weapon_categories[selected_category.get()]
        for name in weapons_names[start:end]:
            weapons_listbox.insert("end", name)

category_dropdown.bind("<<ComboboxSelected>>", update_weapon_list)
def add_selected_weapons():
    for i in weapons_listbox.curselection():
        name = weapons_listbox.get(i)
        spawn_weapons(name, "weapons")
    messagebox.showinfo("Info", "Selected Weapons added to inventory.")
tk.Button(weapons_tab, text="Add Selected Weapons", command=add_selected_weapons).pack(padx=5, pady=2)

def add_all_weapons():
    if selected_category.get() == "All":
        names_to_add = weapons_names
    else:
        start, end = weapon_categories[selected_category.get()]
        names_to_add = weapons_names[start:end]

    for name in names_to_add:
        spawn_weapons(name, "weapons")
    messagebox.showinfo("Info", f"All {selected_category.get()} Weapons added to inventory.")
tk.Button(weapons_tab, text="Add All Weapons in selected category", command=add_all_weapons).pack(padx=5, pady=2)

# --- Armors Tab with optimized search ---
tk.Label(armors_tab, text="Search Armors:").pack(anchor="w", padx=5, pady=2)
armors_search_var = tk.StringVar()
armors_search_entry = tk.Entry(armors_tab, textvariable=armors_search_var)
armors_search_entry.pack(anchor="w", padx=5, pady=2)

# Cache armor names as list
armors_names = list(armor_json.keys())

armors_frame = tk.Frame(armors_tab)
armors_frame.pack(fill="both", expand=True, padx=5, pady=5)

armors_listbox = tk.Listbox(armors_frame, selectmode="extended")
armors_listbox.pack(fill="both", expand=True, side="left")

armors_scrollbar = ttk.Scrollbar(armors_frame, orient="vertical", command=armors_listbox.yview)
armors_listbox.configure(yscrollcommand=armors_scrollbar.set)
armors_scrollbar.pack(side="right", fill="y")

for name in armors_names:
    armors_listbox.insert("end", name)

# Debounce armor search
armors_search_after_id = None

def filter_armors():
    search_term = armors_search_var.get().lower()
    
    if not search_term:
        armors_listbox.delete(0, "end")
        for name in armors_names:
            armors_listbox.insert("end", name)
        return
    
    armors_listbox.delete(0, "end")
    for name in armors_names:
        if search_term in name.lower():
            armors_listbox.insert("end", name)

def debounced_armors_filter(*args):
    global armors_search_after_id
    if armors_search_after_id:
        armors_tab.after_cancel(armors_search_after_id)
    armors_search_after_id = armors_tab.after(200, filter_armors)

armors_search_var.trace_add("write", debounced_armors_filter)

def add_selected_armors():
    for i in armors_listbox.curselection():
        name = armors_listbox.get(i)
        spawn_weapons(name, "armors")
    messagebox.showinfo("Info", "Selected Armors added to inventory.")
tk.Button(armors_tab, text="Add Selected Armors", command=add_selected_armors).pack(padx=5, pady=2)

def add_all_armors():
    for name in armors_names:
        spawn_weapons(name, "armors")
    messagebox.showinfo("Info", "All Armors added to inventory.")
tk.Button(armors_tab, text="Add All Armors", command=add_all_armors).pack(padx=5, pady=2)

# --- Ashes of War Tab with optimized search ---
tk.Label(aow_tab, text="Search Ashes of War:").pack(anchor="w", padx=5, pady=2)
aow_search_var = tk.StringVar()
aow_search_entry = tk.Entry(aow_tab, textvariable=aow_search_var)
aow_search_entry.pack(anchor="w", padx=5, pady=2)

# Cache AoW names as list
aow_names = list(aow_json.keys())

aow_frame = tk.Frame(aow_tab)
aow_frame.pack(fill="both", expand=True, padx=5, pady=5)

aow_listbox = tk.Listbox(aow_frame, selectmode="extended")
aow_listbox.pack(fill="both", expand=True, side="left")

aow_scrollbar = ttk.Scrollbar(aow_frame, orient="vertical", command=aow_listbox.yview)
aow_listbox.configure(yscrollcommand=aow_scrollbar.set)
aow_scrollbar.pack(side="right", fill="y")

for name in aow_names:
    aow_listbox.insert("end", name)

# Debounce AoW search
aow_search_after_id = None

def filter_aow():
    search_term = aow_search_var.get().lower()
    
    if not search_term:
        aow_listbox.delete(0, "end")
        for name in aow_names:
            aow_listbox.insert("end", name)
        return
    
    aow_listbox.delete(0, "end")
    for name in aow_names:
        if search_term in name.lower():
            aow_listbox.insert("end", name)

def debounced_aow_filter(*args):
    global aow_search_after_id
    if aow_search_after_id:
        aow_tab.after_cancel(aow_search_after_id)
    aow_search_after_id = aow_tab.after(200, filter_aow)

aow_search_var.trace_add("write", debounced_aow_filter)

def add_selected_aow():
    for i in aow_listbox.curselection():
        name = aow_listbox.get(i)
        spawn_weapons(name, "aow")
    messagebox.showinfo("Info", "Selected Ashes of War added to inventory.")
tk.Button(aow_tab, text="Add Selected Ashes of War", command=add_selected_aow).pack(padx=5, pady=2)

def add_all_aow():
    for name in aow_names:
        spawn_weapons(name, "aow")
    messagebox.showinfo("Info", "All Ashes of War added to inventory.")

tk.Button(aow_tab, text="Add All Ashes of War", command=add_all_aow).pack(padx=5, pady=2)
###

window.mainloop()
