import os
import subprocess
import time

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr
    except Exception as e:
        return None, str(e)

def check_interface_status(interface):
    # Check if the interface is up
    stdout, stderr = run_command(f"ifconfig {interface}")
    if "UP" in stdout:
        print(f"{interface} is up.")
    else:
        print(f"{interface} is down. Attempting to bring it up...")
        run_command(f"sudo ifconfig {interface} up")
        time.sleep(2)
        stdout, stderr = run_command(f"ifconfig {interface}")
        if "UP" in stdout:
            print(f"{interface} is now up.")
        else:
            print(f"Failed to bring {interface} up. Error: {stderr}")
    
def set_monitor_mode(interface):
    # Set the interface to monitor mode
    print(f"Setting {interface} to monitor mode...")
    run_command(f"sudo airmon-ng start {interface}")
    time.sleep(2)
    stdout, _ = run_command("iwconfig")
    if f"{interface}mon" in stdout:
        print(f"{interface} is now in monitor mode.")
    else:
        print(f"Failed to set {interface} to monitor mode.")

def kill_conflicting_processes():
    # Kill processes that could interfere
    print("Killing interfering processes...")
    stdout, stderr = run_command("sudo airmon-ng check kill")
    if stdout:
        print(stdout)
    if stderr:
        print(f"Error killing processes: {stderr}")
    
def check_and_install_drivers():
    # Check and install firmware drivers
    print("Checking for missing firmware...")
    stdout, stderr = run_command("sudo dmesg | grep -i firmware")
    if "missing" in stdout:
        print("Missing firmware detected. Installing drivers...")
        run_command("sudo apt install firmware-realtek")
    else:
        print("No missing firmware detected.")
        
def scan_for_networks(interface):
    # Use nmcli or airodump-ng to scan for networks
    print(f"Scanning for networks with {interface}...")
    stdout, stderr = run_command(f"sudo nmcli device wifi list ifname {interface}")
    if stdout:
        print("Networks detected using nmcli:")
        print(stdout)
    else:
        print(f"nmcli failed. Error: {stderr}")
    
    # Scan with airodump-ng as a backup method
    print(f"Attempting scan with airodump-ng on {interface}mon...")
    run_command(f"sudo airodump-ng {interface}mon")

def disable_power_management(interface):
    # Disable power management for the Wi-Fi interface
    print(f"Disabling power management on {interface}...")
    run_command(f"sudo iwconfig {interface} power off")
    print(f"Power management disabled on {interface}.")

def main():
    interface = input("Enter your TP-Link interface name (e.g., wlan0): ")
    
    # Step 1: Check if the interface is up
    check_interface_status(interface)
    
    # Step 2: Set monitor mode
    set_monitor_mode(interface)
    
    # Step 3: Kill interfering processes
    kill_conflicting_processes()
    
    # Step 4: Check for missing drivers
    check_and_install_drivers()
    
    # Step 5: Disable power management
    disable_power_management(interface)
    
    # Step 6: Scan for networks
    scan_for_networks(interface)

if __name__ == "__main__":
    main()
