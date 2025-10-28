import sys
import maliang
import maliang.theme
from PIL import Image
from Backend import AWCCThermal, AWCCWmiWrapper, DetectHardware
import threading
import tempfile
import os

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
    size = 900, 250

    root = maliang.Tk(size=size, position=(-1000, -1000))
    root.title('Lumine')
    root.icon(maliang.PhotoImage(Image.open('icons/icon.png').resize((64, 64))))
    root.maxsize(*size)
    root.minsize(*size)
    root.center()

    update_duration = 1000

    maliang.configs.Env.system = 'Windows10'
    # maliang.theme.apply_theme(root, theme='acrylic')
    maliang.theme.customize_window(root, disable_maximize_button=True)

    def update_info():
        fan_ids = [id for id, _ in awccthermal._fanIdsAndRelatedSensorsIds]
        cpu_fan_id = fan_ids[0]
        gpu_fan_id = fan_ids[1]

        ui_gpu_temp.set(awccthermal.getFanRelatedTemp(hardware.GPUFanIdx) / 95)
        ui_gpu_temp_text.set(f'{awccthermal.getFanRelatedTemp(hardware.GPUFanIdx)} ℃')
        ui_gpu_fan.set(awccthermal._awcc.GetFanRPM(gpu_fan_id) / 5500)
        ui_gpu_fan_text.set(f'{awccthermal._awcc.GetFanRPM(gpu_fan_id)} RPM')

        ui_cpu_temp.set(awccthermal.getFanRelatedTemp(hardware.CPUFanIdx) / 110)
        ui_cpu_temp_text.set(f'{awccthermal.getFanRelatedTemp(hardware.CPUFanIdx)} ℃')
        ui_cpu_fan.set(awccthermal._awcc.GetFanRPM(cpu_fan_id) / 5500)
        ui_cpu_fan_text.set(f'{awccthermal._awcc.GetFanRPM(cpu_fan_id)} RPM')

        ui_gpu_temp.style.set(
            bg_bar  = ('#34A853', '#34A853'), 
            ol_bar  = ('#34A853', '#34A853'), 
            bg_slot = ('#505050', '#505050'), 
            ol_slot = ('#808080', '#808080'),
        )

        ui_cpu_temp.style.set(
            bg_bar  = ('#34A853', '#34A853'), 
            ol_bar  = ('#34A853', '#34A853'), 
            bg_slot = ('#505050', '#505050'), 
            ol_slot = ('#808080', '#808080'),
        )

        ui_gpu_fan.style.set(
            bg_bar  = ('#1A6497', '#1A6497'), 
            ol_bar  = ('#1A6497', '#1A6497'), 
            bg_slot = ('#505050', '#505050'), 
            ol_slot = ('#808080', '#808080'),
        )
        
        ui_cpu_fan.style.set(
            bg_bar  = ('#1A6497', '#1A6497'), 
            ol_bar  = ('#1A6497', '#1A6497'), 
            bg_slot = ('#505050', '#505050'), 
            ol_slot = ('#808080', '#808080'),
        )

        root.after(update_duration, update_info)

    cv = maliang.Canvas(root)
    cv.place(x=0, y=0, width=size[0], height=size[1])

    awccthermal = AWCCThermal.AWCCThermal()
    awccwrapper = awccthermal._awcc
    hardware = DetectHardware.DetectHardware()

    gpu_name = hardware.getHardwareName(hardware.GPUFanIdx)
    ui_gpu_name = maliang.Text(cv, position=(25, 15), text=gpu_name, fontsize=17, family='Microsoft YaHei UI')    
    ui_gpu_temp = maliang.ProgressBar(cv, position=(25, 45), size=(310, 40))
    ui_gpu_temp_text = maliang.Text(cv, position=(350, 55), fontsize=17, family='Microsoft YaHei UI')
    ui_gpu_fan = maliang.ProgressBar(cv, position=(25, 95), size=(310, 40))
    ui_gpu_fan_text = maliang.Text(cv, position=(350, 105), fontsize=17, family='Microsoft YaHei UI')
    ui_gpu_fan_slider = maliang.Slider(cv, position=())

    ui_cpu_prefix = size[0] // 2 - 15

    cpu_name = hardware.getHardwareName(hardware.CPUFanIdx)
    ui_cpu_name = maliang.Text(cv, position=(ui_cpu_prefix + 25, 15), text=cpu_name, fontsize=17, family='Microsoft YaHei UI')    
    ui_cpu_temp = maliang.ProgressBar(cv, position=(ui_cpu_prefix + 25, 45), size=(310, 40))
    ui_cpu_temp_text = maliang.Text(cv, position=(ui_cpu_prefix + 350, 55), fontsize=17, family='Microsoft YaHei UI')
    ui_cpu_fan = maliang.ProgressBar(cv, position=(ui_cpu_prefix + 25, 95), size=(310, 40))
    ui_cpu_fan_text = maliang.Text(cv, position=(ui_cpu_prefix + 350, 105), fontsize=17, family='Microsoft YaHei UI')

    root.after(update_duration, update_info)

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
