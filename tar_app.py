import logging
import os
import sys
import tarfile
from pathlib import Path
import dearpygui.dearpygui as dpg

exe_dir = os.path.dirname(sys.executable)
log_file_path = os.path.join(exe_dir, "folderTarGUI.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    filename=log_file_path,
    filemode='a'
)

logger = logging.getLogger('folderTarGUI')
logger.info('Start folderTarGUI')
logger.info(f'log_file_path: {log_file_path}')

selected_folders = []


def select_folders_callback(sender, app_data):
    global selected_folders
    selections = app_data.get('selections', {})
    selected_folders = list(selections.values())
    
    if selected_folders:
        logger.info(f'Folders Selected: {selected_folders}')
        
        # Update the display
        folder_text = '\n'.join(selected_folders)
        dpg.set_value("folder_display", folder_text)
        dpg.configure_item("tar_button", enabled=True)


def open_folder_dialog():
    dpg.show_item("folder_dialog")


def compress_folders():
    dpg.configure_item("tar_button", enabled=False)
    dpg.configure_item("select_button", enabled=False)
    
    for raw_folder in selected_folders:
        logger.info(f'Creating tar file for {raw_folder}')
        dpg.set_value("status_text", f"Creating tar file for {Path(raw_folder).name}...")
        
        # Create tar file in the same parent directory as the folder
        folder_path = Path(raw_folder)
        tar_name = folder_path.name.replace(" ", "_") + '.tar'
        tar_path = folder_path.parent / tar_name
        
        with tarfile.open(str(tar_path), "w") as tar:
            for root, _, files in os.walk(raw_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    tar.add(file_path, arcname=os.path.relpath(file_path, folder_path.parent))
        
        logger.info(f'Path to tar file: {tar_path}')
    
    dpg.set_value("status_text", "Finished creating tar files!")
    dpg.configure_item("tar_button", enabled=True)
    dpg.configure_item("select_button", enabled=True)


def resize_callback():
    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()
    dpg.set_item_width("Primary Window", viewport_width)
    dpg.set_item_height("Primary Window", viewport_height)


dpg.create_context()

# Set up theme for better appearance
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 15, 15, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 10, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 6, category=dpg.mvThemeCat_Core)
        
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (41, 74, 122), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (66, 150, 250), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (15, 86, 135), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)

# File dialog - as a standalone modal window (not constrained by main window)
with dpg.file_dialog(directory_selector=True, show=False, callback=select_folders_callback, 
                     id="folder_dialog", width=800, height=500, modal=True):
    dpg.add_file_extension(".*")

# Main window
with dpg.window(label="Folder Tar Tool", tag="Primary Window", no_title_bar=True, 
                no_move=True, no_resize=True, no_collapse=True):
    
    with dpg.group(horizontal=False):
        # Title
        dpg.add_text("Folder Tar Tool", color=(100, 200, 255))
        with dpg.theme() as title_theme:
            with dpg.theme_component(dpg.mvText):
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 15, category=dpg.mvThemeCat_Core)
        dpg.bind_item_theme(dpg.last_item(), title_theme)
        
        dpg.add_separator()
        dpg.add_spacer(height=5)
        
        # Select button
        dpg.add_button(label="Select Folders", callback=open_folder_dialog, 
                       tag="select_button", height=50)
        
        dpg.add_spacer(height=15)
        
        # Selected folders section
        with dpg.group():
            dpg.add_text("Selected Folders:", color=(180, 180, 180))
            dpg.add_spacer(height=5)
            with dpg.child_window(height=250, border=True, tag="folder_window"):
                dpg.add_input_text(multiline=True, readonly=True, tag="folder_display", 
                                   default_value="No folders selected", width=-1, height=-1,
                                   no_spaces=False)
        
        dpg.add_spacer(height=15)
        
        # Tar button
        dpg.add_button(label="Create Tar Files", callback=compress_folders, 
                       tag="tar_button", height=50, enabled=False)
        
        dpg.add_spacer(height=10)
        
        # Status
        with dpg.group(horizontal=True):
            dpg.add_text("Status: ", color=(150, 150, 150))
            dpg.add_text("Ready", tag="status_text", color=(100, 255, 100))

dpg.create_viewport(title="Folder Tar Tool", width=900, height=650, resizable=True, min_width=900, min_height=650)
dpg.set_viewport_resize_callback(resize_callback)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()