#!/usr/bin/env python3
"""
Windows system control tool using PowerShell.
"""

import json
import subprocess
import sys


def run_ps(command: str) -> tuple:
    try:
        result = subprocess.run(
            ['powershell', '-Command', command],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def open_app(app_name: str) -> str:
    apps = {
        "code": "code",
        "vscode": "code",
        "chrome": "chrome",
        "firefox": "firefox",
        "spotify": "spotify",
        "discord": "discord",
        "slack": "slack",
        "notepad": "notepad",
        "calculator": "calc",
        "terminal": "wt",
        "cmd": "cmd",
        "explorer": "explorer",
        "settings": "ms-settings:",
        "control": "control",
        "taskmanager": "taskmgr",
    }
    
    cmd = apps.get(app_name.lower())
    if not cmd:
        return f"Unknown app: {app_name}. Available: {', '.join(apps.keys())}"
    
    run_ps(f"Start-Process {cmd}")
    return f"Opened {app_name}"


def set_volume(level: int) -> str:
    if level < 0 or level > 100:
        return "Volume must be between 0 and 100"
    try:
        from pycaw.pycaw import AudioUtilities

        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Failed to set volume: {e}"


def get_volume() -> int:
    try:
        from pycaw.pycaw import AudioUtilities

        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        return int(volume.GetMasterVolumeLevelScalar() * 100)
    except Exception:
        return None


def mute_volume(mute: bool) -> str:
    try:
        from pycaw.pycaw import AudioUtilities

        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        volume.SetMute(mute, None)
        return f"Volume {'muted' if mute else 'unmuted'}"
    except Exception as e:
        return f"Failed: {e}"


def set_brightness(level: int) -> str:
    if level < 0 or level > 100:
        return "Brightness must be between 0 and 100"
    run_ps(f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})")
    return f"Brightness set to {level}%"


def toggle_wifi(enable: bool) -> str:
    state = "enable" if enable else "disable"
    run_ps(f'Get-NetAdapter -Name "Wi-Fi" | {"Enable-NetAdapter" if enable else "Disable-NetAdapter"} -Confirm:$false')
    return f"Wi-Fi {state}d"


def toggle_bluetooth(enable: bool) -> str:
    state = "enable" if enable else "disable"
    run_ps(f'Get-NetAdapter -Name "Bluetooth" | {"Enable-NetAdapter" if enable else "Disable-NetAdapter"} -Confirm:$false')
    return f"Bluetooth {state}d"


def toggle_dark_mode(enable: bool) -> str:
    path = "HKCU:/SOFTWARE/Microsoft/Windows/CurrentVersion/Themes/Personalize"
    val = 1 if enable else 0
    run_ps(f'Set-ItemProperty -Path "{path}" -Name AppsUseLightTheme -Value {val}')
    return f"Dark mode {'enabled' if enable else 'disabled'}"


def take_screenshot(filename: str = "") -> str:
    if not filename:
        import datetime
        filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = f"$env:USERPROFILE/Desktop/{filename}"
    run_ps(f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen.Bounds | ForEach-Object {{ [System.Drawing.Bitmap]::new($_.Width, $_.Height) | ForEach-Object {{ $_.Graphics.CopyFromScreen($_.Location, [System.Drawing.Point]::Empty, $_.Size) | Out-Null; $_.Save('{path}') }}}}")
    return f"Screenshot saved to Desktop/{filename}"


def get_system_info() -> dict:
    success, cpu, _ = run_ps("(Get-CimInstance Win32_Processor).Name")
    success, mem, _ = run_ps("(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB")
    success, disk, _ = run_ps("(Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='C:'\").FreeSpace / 1GB")
    
    return {
        "cpu": cpu if success else "Unknown",
        "memory_gb": f"{float(mem):.1f}" if mem else "Unknown",
        "disk_free_gb": f"{float(disk):.1f}" if disk else "Unknown"
    }


def lock_screen() -> str:
    run_ps("rundll32.exe user32.dll,LockWorkStation")
    return "Screen locked"


def set_power_mode(mode: str) -> str:
    modes = {
        "saver": "a1841308-3541-4fab-bc81-f71556f20b4a",
        "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
        "performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
    }
    
    if mode.lower() not in modes:
        return f"Unknown mode: {mode}. Available: saver, balanced, performance"
    
    guid = modes[mode.lower()]
    run_ps(f"powercfg /setactive {guid}")
    return f"Power mode set to {mode}"


def sleep_pc() -> str:
    run_ps("Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)")
    return "PC going to sleep"


def shutdown_pc() -> str:
    run_ps("Stop-Computer -Force")
    return "PC shutting down"


def restart_pc() -> str:
    run_ps("Restart-Computer -Force")
    return "PC restarting"


def toggle_night_light(enable: bool) -> str:
    path = "HKCU:/Software/Microsoft/Windows/CurrentVersion/CloudStore/Store/Cache/DefaultAccount/$$windows.data.bluelightreduction.bluelightreductionstate/ windows.data.bluelightreduction.bluelightreductionstate"
    val = 1 if enable else 0
    run_ps(f'Set-ItemProperty -Path "{path}" -Name Data -Value ([byte[]]({val},0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))')
    return f"Night light {'enabled' if enable else 'disabled'}"


def toggle_airplane_mode(enable: bool) -> str:
    run_ps(f'Set-NetAdapter -Name "Wi-Fi" -Disabled:{"$false" if enable else "$true"}')
    return f"Airplane mode {'on' if enable else 'off'}"


def clipboard_copy(text: str) -> str:
    run_ps(f'Set-Clipboard -Value "{text}"')
    return "Text copied to clipboard"


def clipboard_paste() -> str:
    success, output, _ = run_ps("Get-Clipboard")
    if success:
        return output
    return "Failed to get clipboard content"


def toggle_touchpad(enable: bool) -> str:
    run_ps(f'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PrecisionTouchPad" -Name Enabled -Value {1 if enable else 0}')
    return f"Touchpad {'enabled' if enable else 'disabled'}"


def toggle_microphone(enable: bool) -> str:
    run_ps(f'Set-AudioDevice -RecordingMute {not enable}')
    return f"Microphone {'unmuted' if enable else 'muted'}"


def toggle_focus_assist(enable: bool) -> str:
    path = "HKCU:/Software/Microsoft/Windows/CurrentVersion/CloudStore/Store/DefaultAccount/Current/default$windows.data.shell.focusassist/FocusAssist"
    val = 2 if enable else 0
    run_ps(f'Set-ItemProperty -Path "{path}" -Name Data -Value ([byte[]]({val},0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))')
    return f"Focus assist {'enabled' if enable else 'disabled'}"


def kill_process(name: str) -> str:
    success, _, _ = run_ps(f'Stop-Process -Name "{name}" -Force -ErrorAction SilentlyContinue')
    if success:
        return f"Killed process: {name}"
    return f"Process not found or failed: {name}"


def list_processes(limit: int = 10) -> list:
    success, output, _ = run_ps(f'Get-Process | Sort-Object CPU -Descending | Select-Object -First {limit} Name, CPU, WorkingSet | ConvertTo-Json')
    if success:
        import json
        try:
            return json.loads(output)
        except:
            return [{"Name": "Error parsing", "CPU": "0", "WorkingSet": "0"}]
    return []


def get_network_info() -> dict:
    success, ip, _ = run_ps("(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -eq 'Wi-Fi' -or $_.InterfaceAlias -eq 'Ethernet'} | Select-Object -First 1).IPAddress")
    success, wifi, _ = run_ps('Get-NetAdapter | Where-Object {$_.Status -eq "Up" -and $_.Name -match "Wi-Fi"} | Select-Object -First 1 -ExpandProperty Name')
    success, connected, _ = run_ps('(Get-NetAdapter | Where-Object {$_.Name -match "Wi-Fi" -and $_.Status -eq "Up"}).Status')
    return {
        "ip_address": ip if ip else "Not connected",
        "wifi_adapter": wifi if wifi else "None",
        "connected": connected == "Up" if connected else False
    }


def get_battery_status() -> dict:
    success, output, _ = run_ps('Get-CimInstance Win32_Battery | Select-Object EstimatedChargeRemaining, BatteryStatus, EstimatedRunTime | ConvertTo-Json')
    if success and output:
        import json
        try:
            return json.loads(output)
        except:
            pass
    return {"status": "No battery or error"}


def get_disk_usage() -> list:
    success, output, _ = run_ps('Get-CimInstance Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} | Select-Object DeviceID, @{N="FreeGB";E={[math]::Round($_.FreeSpace/1GB,2)}}, @{N="TotalGB";E={[math]::Round($_.Size/1GB,2)}}, @{N="UsedGB";E={[math]::Round(($_.Size-$_.FreeSpace)/1GB,2)}} | ConvertTo-Json')
    if success and output:
        import json
        try:
            return json.loads(output)
        except:
            pass
    return []


def minimize_all() -> str:
    run_ps('Add-Type -TypeDefinition @"using System; using System.Runtime.InteropServices; public class Win32 {[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);}"@; [Win32]::keybd_byte(0x5B,0,0,[UIntPtr]::Zero); Start-Sleep -Milliseconds 10; [Win32]::keybd_byte(0x4D,0,0,[UIntPtr]::Zero); Start-Sleep -Milliseconds 10; [Win32]::keybd_byte(0x4D,0x2,[UIntPtr]::Zero)')
    return "Minimized all windows"


def open_folder(path: str) -> str:
    run_ps(f'Start-Process explorer.exe "{path}"')
    return f"Opened folder: {path}"


def open_settings(page: str) -> str:
    pages = {
        "wifi": "ms-settings:network-wifi",
        "bluetooth": "ms-settings:bluetooth",
        "display": "ms-settings:display",
        "sound": "ms-settings:sound",
        "notifications": "ms-settings:notifications",
        "power": "ms-settings:powersleep",
        "privacy": "ms-settings:privacy",
        "update": "ms-settings:windowsupdate",
        "apps": "ms-settings:appsfeatures",
        "storage": "ms-settings:storagesense",
    }
    if page.lower() not in pages:
        return f"Unknown settings page. Available: {', '.join(pages.keys())}"
    run_ps(f'Start-Process {pages[page.lower()]}')
    return f"Opened settings: {page}"


def get_wifi_networks() -> list:
    success, output, _ = run_ps('netsh wlan show networks mode=bssid | Select-String -Pattern "SSID|BSSID|Signal|Authentication" | ForEach-Object {$_.Line.Trim()}')
    if success:
        return output.split('\n') if output else []
    return []


def main() -> int:
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            print(json.dumps({"success": False, "message": "No input provided."}))
            return 1

        data = json.loads(input_data)
        action = data.get("action", "").strip()

        if action == "open":
            app = data.get("app", "").strip()
            if not app:
                print(json.dumps({"success": False, "message": "No app name provided."}))
                return 1
            result = open_app(app)

        elif action == "volume":
            level = data.get("level")
            if level is not None:
                result = set_volume(int(level))
            elif data.get("mute") is not None:
                result = mute_volume(data.get("mute"))
            else:
                vol = get_volume()
                result = f"Current volume: {vol}%" if vol else "Failed to get volume"

        elif action == "brightness":
            level = data.get("level")
            if level is None:
                print(json.dumps({"success": False, "message": "No brightness level provided."}))
                return 1
            result = set_brightness(int(level))

        elif action == "wifi":
            enable = data.get("enable")
            if enable is None:
                print(json.dumps({"success": False, "message": "No enable value provided."}))
                return 1
            result = toggle_wifi(enable)

        elif action == "bluetooth":
            enable = data.get("enable")
            if enable is None:
                print(json.dumps({"success": False, "message": "No enable value provided."}))
                return 1
            result = toggle_bluetooth(enable)

        elif action == "darkmode":
            enable = data.get("enable")
            if enable is None:
                print(json.dumps({"success": False, "message": "No enable value provided."}))
                return 1
            result = toggle_dark_mode(enable)

        elif action == "screenshot":
            filename = data.get("filename", "")
            result = take_screenshot(filename)

        elif action == "sysinfo":
            info = get_system_info()
            print(json.dumps({"success": True, "info": info}))
            return 0

        elif action == "lock":
            result = lock_screen()

        elif action == "power":
            mode = data.get("mode", "").strip()
            if not mode:
                print(json.dumps({"success": False, "message": "No power mode provided (saver, balanced, performance)"}))
                return 1
            result = set_power_mode(mode)

        elif action == "sleep":
            result = sleep_pc()

        elif action == "shutdown":
            result = shutdown_pc()

        elif action == "restart":
            result = restart_pc()

        elif action == "nightlight":
            enable = data.get("enable")
            if enable is None:
                print(json.dumps({"success": False, "message": "No enable value provided."}))
                return 1
            result = toggle_night_light(enable)

        elif action == "airplane":
            enable = data.get("enable")
            if enable is None:
                print(json.dumps({"success": False, "message": "No enable value provided."}))
                return 1
            result = toggle_airplane_mode(enable)

        elif action == "clipboard":
            if data.get("text"):
                result = clipboard_copy(data.get("text"))
            else:
                result = clipboard_paste()

        elif action == "touchpad":
            enable = data.get("enable")
            if enable is None:
                print(json.dumps({"success": False, "message": "No enable value provided."}))
                return 1
            result = toggle_touchpad(enable)

        elif action == "microphone":
            enable = data.get("enable")
            if enable is None:
                print(json.dumps({"success": False, "message": "No enable value provided."}))
                return 1
            result = toggle_microphone(enable)

        elif action == "focus":
            enable = data.get("enable")
            if enable is None:
                print(json.dumps({"success": False, "message": "No enable value provided."}))
                return 1
            result = toggle_focus_assist(enable)

        elif action == "kill":
            name = data.get("name", "").strip()
            if not name:
                print(json.dumps({"success": False, "message": "No process name provided."}))
                return 1
            result = kill_process(name)

        elif action == "processes":
            limit = data.get("limit", 10)
            procs = list_processes(limit)
            print(json.dumps({"success": True, "processes": procs}))
            return 0

        elif action == "network":
            info = get_network_info()
            print(json.dumps({"success": True, "network": info}))
            return 0

        elif action == "battery":
            info = get_battery_status()
            print(json.dumps({"success": True, "battery": info}))
            return 0

        elif action == "disks":
            info = get_disk_usage()
            print(json.dumps({"success": True, "disks": info}))
            return 0

        elif action == "minimize":
            result = minimize_all()

        elif action == "folder":
            path = data.get("path", "").strip()
            if not path:
                print(json.dumps({"success": False, "message": "No folder path provided."}))
                return 1
            result = open_folder(path)

        elif action == "settings":
            page = data.get("page", "").strip()
            if not page:
                print(json.dumps({"success": False, "message": "No settings page provided."}))
                return 1
            result = open_settings(page)

        elif action == "wifi-networks":
            nets = get_wifi_networks()
            print(json.dumps({"success": True, "networks": nets}))
            return 0

        else:
            print(json.dumps({"success": False, "message": f"Unknown action: {action}"}))
            return 1

        print(json.dumps({"success": True, "message": result}))
        return 0

    except Exception as e:
        print(json.dumps({"success": False, "message": f"Error: {str(e)}"}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
