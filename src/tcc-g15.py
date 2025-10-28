import sys
import maliang
import maliang.theme
from PIL import Image
from Backend import AWCCThermal, AWCCWmiWrapper, DetectHardware
import threading
import tempfile
import os
from pystray import Icon, MenuItem, Menu

def create_lock():
    basename = (
        os.path.splitext(os.path.abspath(sys.argv[0]))[0]
            .replace("/", "-").replace(":", "").replace("\\", "-")
            + ".lock"
    )
    lockfile = os.path.normpath(tempfile.gettempdir() + "/" + basename)
    if os.path.exists(lockfile):
        os.unlink(lockfile)
    os.open(lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        
def main(minimize: bool = False):
    size = 900, 270

    root = maliang.Tk(size=size, position=(-1000, -1000))
    root.title('Lumine')
    root.icon(maliang.PhotoImage(Image.open('icons/icon.png').resize((64, 64))))
    root.maxsize(*size)
    root.minsize(*size)
    root.center()

    update_duration = 1000

    color_tempbar = '#98C379'
    color_fanbar = '#61AFEF'
    color_barbg = '#202020'
    color_barol = '#282C34'

    ui_family = 'Segoe UI'

    failsafe = False
    failsafe_cpu = 95
    failsafe_gpu = 85
    failsafe_activated = False

    current_mode = 0

    maliang.configs.Env.system = 'Windows10'
    # maliang.theme.apply_theme(root, theme='acrylic')
    maliang.theme.customize_window(root, disable_maximize_button=True)

    def update_info():
        nonlocal failsafe_activated
        gpu_fan_id = awccthermal._fanIdsAndRelatedSensorsIds[hardware.GPUFanIdx][0]
        cpu_fan_id = awccthermal._fanIdsAndRelatedSensorsIds[hardware.CPUFanIdx][0]

        ui_gpu_temp.set(awccthermal.getFanRelatedTemp(hardware.GPUFanIdx) / 95)
        ui_gpu_temp_text.set(f'{awccthermal.getFanRelatedTemp(hardware.GPUFanIdx)} °C')
        ui_gpu_fan.set(awccthermal._awcc.GetFanRPM(gpu_fan_id) / 5500)
        ui_gpu_fan_text.set(f'{awccthermal._awcc.GetFanRPM(gpu_fan_id)} RPM')

        ui_cpu_temp.set(awccthermal.getFanRelatedTemp(hardware.CPUFanIdx) / 110)
        ui_cpu_temp_text.set(f'{awccthermal.getFanRelatedTemp(hardware.CPUFanIdx)} °C')
        ui_cpu_fan.set(awccthermal._awcc.GetFanRPM(cpu_fan_id) / 5500)
        ui_cpu_fan_text.set(f'{awccthermal._awcc.GetFanRPM(cpu_fan_id)} RPM')

        ui_gpu_temp.style.set(
            bg_bar  = (color_tempbar, color_tempbar), 
            ol_bar  = (color_tempbar, color_tempbar), 
            bg_slot = (color_barbg, color_barbg), 
            ol_slot = (color_barol, color_barol),
        )

        ui_cpu_temp.style.set(
            bg_bar  = (color_tempbar, color_tempbar), 
            ol_bar  = (color_tempbar, color_tempbar), 
            bg_slot = (color_barbg, color_barbg), 
            ol_slot = (color_barol, color_barbg),
        )

        ui_gpu_fan.style.set(
            bg_bar  = (color_fanbar, color_fanbar), 
            ol_bar  = (color_fanbar, color_fanbar), 
            bg_slot = (color_barbg, color_barbg), 
            ol_slot = (color_barol, color_barol),
        )
        
        ui_cpu_fan.style.set(
            bg_bar  = (color_fanbar, color_fanbar), 
            ol_bar  = (color_fanbar, color_fanbar), 
            bg_slot = (color_barbg, color_barbg), 
            ol_slot = (color_barol, color_barol),
        )

        if failsafe:
            if awccthermal.getFanRelatedTemp(hardware.GPUFanIdx) > failsafe_gpu or awccthermal.getFanRelatedTemp(hardware.CPUFanIdx) > failsafe_cpu:
                if failsafe_activated:
                    ui_failsafe_status.style.set(bg=('#E06C75', '#E06C75'))
                    awccthermal.setMode(awccthermal.Mode.G_Mode)
                    ui_modeset.set(1)
                else:
                    ui_failsafe_status.style.set(bg=('#E5C07B', '#E5C07B'))
                    failsafe_activated = True
            else:
                ui_failsafe_status.style.set(bg=('#98C379', '#98C379'))    
                failsafe_activated = False
        else:
            ui_failsafe_status.style.set(bg=('#2B2B2B', '#2B2B2B'))

        root.after(update_duration, update_info)

    def set_fan(type, _):
        if type == 'normal':
            awccthermal.setMode(awccthermal.Mode.Custom)

            cpu_speed = int(ui_cpu_fan_slider.get() * 127)
            gpu_speed = int(ui_gpu_fan_slider.get() * 127)

            awccthermal.setFanSpeed(hardware.CPUFanIdx, cpu_speed)
            awccthermal.setFanSpeed(hardware.GPUFanIdx, gpu_speed)

    def set_mode(value):
        nonlocal current_mode

        current_mode = value

        ui_gpu_fan_slider.disable(True)
        ui_cpu_fan_slider.disable(True)

        match value:
            case 0:
                awccthermal.setMode(awccthermal.Mode.Balanced)
            case 1:
                awccthermal.setMode(awccthermal.Mode.G_Mode)
            case 2:
                ui_gpu_fan_slider.disable(False)
                ui_cpu_fan_slider.disable(False)
                awccthermal.setMode(awccthermal.Mode.Custom)

    def toggle_failsafe(value):
        nonlocal failsafe

        failsafe = value

    cv = maliang.Canvas(root)
    cv.place(x=0, y=0, width=size[0], height=size[1])

    awccthermal = AWCCThermal.AWCCThermal()
    awccwrapper = awccthermal._awcc
    hardware = DetectHardware.DetectHardware()

    gpu_name = hardware.getHardwareName(hardware.GPUFanIdx)
    ui_gpu_name = maliang.Text(cv, position=(25, 15), text=gpu_name, fontsize=18, family=ui_family)    
    ui_gpu_temp = maliang.ProgressBar(cv, position=(25, 45), size=(310, 40))
    ui_gpu_temp_text = maliang.Text(cv, position=(350, 55), fontsize=18, family=ui_family)
    ui_gpu_fan = maliang.ProgressBar(cv, position=(25, 95), size=(310, 40))
    ui_gpu_fan_text = maliang.Text(cv, position=(350, 105), fontsize=18, family=ui_family)

    ui_cpu_prefix = size[0] // 2 - 20

    cpu_name = hardware.getHardwareName(hardware.CPUFanIdx)
    ui_cpu_name = maliang.Text(cv, position=(ui_cpu_prefix + 25, 15), text=cpu_name, fontsize=18, family=ui_family)    
    ui_cpu_temp = maliang.ProgressBar(cv, position=(ui_cpu_prefix + 25, 45), size=(310, 40))
    ui_cpu_temp_text = maliang.Text(cv, position=(ui_cpu_prefix + 350, 55), fontsize=18, family=ui_family)
    ui_cpu_fan = maliang.ProgressBar(cv, position=(ui_cpu_prefix + 25, 95), size=(310, 40))
    ui_cpu_fan_text = maliang.Text(cv, position=(ui_cpu_prefix + 350, 105), fontsize=18, family=ui_family)

    maliang.configs.Env.system = 'Windows11'
    ui_gpu_fan_slider = maliang.Slider(cv, position=(25, 150), size=(310, 40), default=0.5)
    ui_gpu_fan_slider.bind_on_update(set_fan)
    ui_gpu_fan_slitext = maliang.Text(cv, position=(349, 155), text='Fan Speed', fontsize=18, family=ui_family)

    ui_cpu_fan_slider = maliang.Slider(cv, position=(ui_cpu_prefix + 25, 150), size=(310, 40), default=0.5)
    ui_cpu_fan_slider.bind_on_update(set_fan)
    ui_cpu_fan_slitext = maliang.Text(cv, position=(ui_cpu_prefix + 349, 155), text='Fan Speed', fontsize=18, family=ui_family)

    ui_modeset = maliang.SegmentedButton(cv, position=(25, 205), text=("Balanced", "Turbo", "Custom"), fontsize=18, family=ui_family, command=set_mode, default=0)
    set_mode(0)

    for i in ui_modeset.children:
        i.style.set(bg=('#2B2B2B', '#3C3C3C', '#323232', '#3C3C3C', '#3C3C3C', '#323232'), ol=('', '', '', '', '', ''))

    ui_failsafe = maliang.ToggleButton(cv, position=(size[0] - 195, 205), size=(100, ui_modeset.size[1]), text=("Fail-Safe"), fontsize=18, family=ui_family, command=toggle_failsafe)

    ui_failsafe_status = maliang.Label(cv, position=(size[0] - 85, 205), size=(50, ui_modeset.size[1]))

    root.after(update_duration, update_info)
    root.protocol("WM_DELETE_WINDOW", root.withdraw)

    def run_tray():
        icon = Icon("TkTray", icon=Image.open('icons/app.png').resize((64, 64)), menu=Menu(
            MenuItem(text='Lumine v1.0', action=lambda: ...),
            Menu.SEPARATOR,
            MenuItem('Show Window', root.deiconify, default=True),
            MenuItem('Exit', root.destroy)
        ))
        icon.run()

    threading.Thread(target=run_tray, daemon=True).start()

    root.mainloop()

    return 0

def wrapper():
    try:
        create_lock()
    except:
        raise PermissionError("Another instance of this app is already running")

    return main("--minimized" in sys.argv)

if __name__ == "__main__":
    sys.exit(wrapper())
