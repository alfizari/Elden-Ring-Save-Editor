
# Dark Souls 3 Save Editor for PS4/PS5

![Logo](https://github.com/user-attachments/assets/492ede59-3360-47d5-b006-7a307797785c)

**USE AT YOUR OWN RISK**

A comprehensive save editor for Dark Souls 3 on PS4/PS5. Enables editing save files to modify characters, items, and game states. Requires a decrypted save file.

---

## Table of Contents
1. [Features](#features)
2. [Screenshots](#screenshots)
3. [Getting Started](#getting-started)
   - [Option 1: Download Compiled Binary](#option-1-download-compiled-binary)
   - [Option 2: Run from Source](#option-2-build-from-source)
4. [Usage](#usage)
5. [Contributing](#contributing)
6. [License](#license)
7. [Acknowledgments](#acknowledgments)

---

## Features

- See all characters in the save file.
- Replace weapons, rings, goods, magic, and armor.
- Modify character attributes (name, HP, stats, estus numbers, etc.).
- Edit souls and storage box item quantities.
- Unlock all bonfires and gestures.
- Kill or revive bosses and unlock the endgame.

---

## Screenshots

Below are screenshots showcasing the features of the Dark Souls 3 Save Editor. Click any image to view it in full size.

<div align="center">

### View All Characters in Save
<a href="https://github.com/user-attachments/assets/26ef2100-fe74-4efc-befb-bd698f051566" target="_blank">
<img src="https://github.com/user-attachments/assets/26ef2100-fe74-4efc-befb-bd698f051566" alt="View All Characters" style="border: 1px solid black; width: 200px;">
</a>

### Replace Weapons
<a href="https://github.com/user-attachments/assets/db5096c5-3e4e-4761-bd9f-8fe3f2312fba" target="_blank">
<img src="https://github.com/user-attachments/assets/db5096c5-3e4e-4761-bd9f-8fe3f2312fba" alt="Replace Weapons" style="border: 1px solid black; width: 200px;">
</a>

### Replace Rings
<a href="https://github.com/user-attachments/assets/1ac3a745-f6e7-49b2-a761-61fab72633b0" target="_blank">
<img src="https://github.com/user-attachments/assets/1ac3a745-f6e7-49b2-a761-61fab72633b0" alt="Replace Rings" style="border: 1px solid black; width: 200px;">
</a>

### Replace Goods and Magic
<a href="https://github.com/user-attachments/assets/25e7c71b-490f-4b13-b1c2-85acb430e258" target="_blank">
<img src="https://github.com/user-attachments/assets/25e7c71b-490f-4b13-b1c2-85acb430e258" alt="Replace Goods and Magic" style="border: 1px solid black; width: 200px;">
</a>

### Replace Armor
<a href="https://github.com/user-attachments/assets/cf61b444-e5bd-4fd7-9459-20565557fede" target="_blank">
<img src="https://github.com/user-attachments/assets/cf61b444-e5bd-4fd7-9459-20565557fede" alt="Replace Armor" style="border: 1px solid black; width: 200px;">
</a>

### Edit Character Name and HP
<a href="https://github.com/user-attachments/assets/b9d32b07-0a05-4c46-b169-545d9ff392a1" target="_blank">
<img src="https://github.com/user-attachments/assets/b9d32b07-0a05-4c46-b169-545d9ff392a1" alt="Edit Name and HP" style="border: 1px solid black; width: 200px;">
</a>

### Edit Souls
<a href="https://github.com/user-attachments/assets/b03a3b80-3d32-47b3-a18d-526205712d90" target="_blank">
<img src="https://github.com/user-attachments/assets/b03a3b80-3d32-47b3-a18d-526205712d90" alt="Edit Souls" style="border: 1px solid black; width: 200px;">
</a>

### Edit Stats and Estus Numbers
<a href="https://github.com/user-attachments/assets/179e28e7-6f7a-4f4e-bfc8-d20623ad72e3" target="_blank">
<img src="https://github.com/user-attachments/assets/179e28e7-6f7a-4f4e-bfc8-d20623ad72e3" alt="Edit Stats and Estus" style="border: 1px solid black; width: 200px;">
</a>

</div>

---

## Getting Started

You have two options to get started with the Dark Souls 3 Save Editor:

### Option 1: Download Compiled Binary available for Windows Mac and Linux (32 and 64bit)
The easiest way is to download the pre-compiled binary:
<<<<<<< HEAD
- Visit the [Releases Page](https://github.com/alfizari/ds3-save-editor/releases/latest) for the latest stable release.
- Or grab the [Latest Artifact](https://github.com/alfizari/ds3-save-editor/actions/) from the latest GitHub Actions build.
=======
- Visit the [Releases Page](https://github.com/alfizari/Dark-souls-3-editor-PS4/releases/latest) for the latest stable release.
- Or grab the [Latest Artifact](https://github.com/alfizari/Dark-souls-3-editor-PS4/actions/) from the latest GitHub Actions build.
>>>>>>> ce9619cfef9b35e936d4558a59c21e76253995ba

Simply download the appropriate binary for your operating system, then run the executable.

### Option 2: Run from Source

#### Prerequisites
- A decrypted save file.
- Python 3.x installed on your system.

#### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/alfizari/Dark-souls-3-editor-PS4
   ```
---

## Usage

1. Launch the application:
   ```bash
   python Final.py
   ```
2. Load your decrypted save file or Folder.
3. Modify desired settings.

---

## Contributing

We welcome contributions! Follow these steps to contribute:

1. Fork the repository.
2. Create your feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add some feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **[bawsdeep](https://github.com/bawsdeep):** UI/Code optimization github Workflow to compile binaries for Linux Windows and Mac.
- **[Nox](https://github.com/Noxde/Bloodborne-save-editor):** Insights on offsets and save editing. Check out his amaizing Bloodborne Save Editor.

