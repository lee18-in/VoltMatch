<!-- AI AGENTS: Read ./AGENTS.md first, then ./LLM_MEMORY.md.
     Do NOT write planning content into this file. -->
# ⚡ VoltMatch

**A Professional Voltage Divider Optimizer for Hardware Engineers**

## 📖 About VoltMatch

VoltMatch is a graphical voltage divider optimization tool designed for hardware engineers and electronics enthusiasts.

Unlike conventional calculators that only provide a "single best solution," VoltMatch's core design philosophy is to **exhaustively calculate all possible resistor combinations within an allowable tolerance range**. This approach gives engineers maximum flexibility to choose the most suitable standard components based on actual inventory, cost constraints, and specific application requirements.

## ✨ Core Features

- 🔍 **Exhaustive Search Algorithm**: Calculates and lists all feasible solutions. Features an Auto-Relaxing Tolerance mechanism to guarantee results even under strict constraints.
- 📊 **Standard Resistor Libraries**: Built-in E24 (5%) and E96 (1%) series support, with independent options to restrict High/Low sides to E24 only.
- ⚡ **Dual-Resistor Architecture**: Supports both Single (R1) and Dual (R1 + R2) modes for the High Side resistor to handle edge-case ratios.
- 🔄 **Quick Solver**: A compact reverse calculator to instantly derive any unknown parameter by locking the other three variables.
- 📈 **Advanced Data Grid**: Excel-like table capabilities powered by `tksheet` featuring multi-column sorting, right-click filtering, and color-coded error gradients.
- 🚀 **Asynchronous Multi-threading**: High-performance vectorized operations utilizing NumPy, running in background threads to keep the UI completely responsive.
- 🎨 **Dynamic Schematics & Notes**: Real-time ANSI Zigzag style circuit rendering alongside a built-in notepad for quick documentation.

## 🚀 Installation & Setup

VoltMatch requires **Python 3.x**.

### Linux Deployment (e.g., Ubuntu / Zorin OS)

1. Install Tkinter system package:

```bash
sudo apt update
sudo apt install python3-tk
```

1. Install Chinese fonts (Optional but recommended for UI rendering):

```bash
sudo apt install fonts-wqy-microhei fonts-noto-cjk
```

1. Setup Virtual Environment & Install Dependencies (PEP 668 compliance):

```bash
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install numpy tksheet
```

### Windows Deployment

1. Ensure Python 3.x is installed from python.org.

1. Open Command Prompt or PowerShell and install dependencies (`tkinter` is usually built-in on Windows):

```bash
pip install numpy tksheet
```

## 💡 Usage Guide

1. **Target Voltage:** Enter your desired `V_Out` and set the maximum allowable error tolerance using the slider or input box.
2. **High Side Resistor:** Choose between Single or Dual resistor mode, and optionally toggle the E24 restriction.
3. **Reference Voltage:** Enter the system's feedback reference voltage `V_Ref` (e.g., 3.3V, 1.25V).
4. **Low Side Resistor:** Choose to let the program automatically `Sweep` (search) or lock it to a `Fixed Value`.
5. **Calculate:** Click `5. Calculate` to initiate the background search. Once finished, right-click the grid headers or cells to filter and sort the results.
6. **Export:** Click `Export CSV` to export the filtered result list for BOM generation or engineering reports.

## 📦 Packaging Notes

If you intend to bundle this application into a standalone executable using tools like **PyInstaller** or **Nuitka**, please ensure that the `CREDITS.txt` file is placed in the same directory as the executable (or properly bundled into the resource path). Otherwise, the "About" window may fail to display the correct developer and open-source acknowledgments.

## � Download GitHub Actions Artifacts

When the GitHub Actions workflow runs, the generated packages are attached as workflow artifacts:

- `voltmatch-windows-exe` → contains `dist/VoltMatch.exe`
- `voltmatch-linux-appimage` → contains `VoltMatch-x86_64.AppImage`

To download them:

1. Open the GitHub repository page.
2. Go to the latest workflow run under **Actions**.
3. Select the completed workflow run.
4. Click **Artifacts** and download the package you need.

## �📜 License & Credits

- **Author:** Andy Lee (lee18.in)
- **License:** MIT License

This project utilizes several awesome open-source libraries. For detailed acknowledgments and third-party licenses, please refer to the `CREDITS.txt` file included in this repository.
