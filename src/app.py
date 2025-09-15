import customtkinter as ctk
import psutil
import subprocess
from fpdf import FPDF
from datetime import datetime

# Create the main application class
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.title("Battery Health Report Generator")

        # Set the window size
        self.geometry("300x300")

        # Center the window on the screen
        self.center_window()

        # Create a Tabview for two tabs (Main Logic and Developer Info)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        # Add tabs
        self.tabview.add("Battery Health Report")
        self.tabview.add("Developer Info")

        # Create Main Logic Tab (Battery Health Report)
        self.main_tab = self.tabview.tab("Battery Health Report")
        self.create_main_tab_content()

        # Create Developer Info Tab
        self.dev_info_tab = self.tabview.tab("Developer Info")
        self.create_dev_info_tab_content()

    def create_main_tab_content(self):
        # Create a frame to hold the label and button for the Main Logic tab
        self.frame = ctk.CTkFrame(self.main_tab)
        self.frame.pack(expand=True, padx=10, pady=10)  # Expand the frame to fill the tab

        # Create a label for main logic tab
        self.label = ctk.CTkLabel(self.frame, text="Battery Health Report Generator")
        self.label.pack(pady=20)

        # Create a button to generate the battery health report
        self.report_button = ctk.CTkButton(self.frame, text="Generate Battery Health Report", command=self.generate_report)
        self.report_button.pack(pady=15)

        # Create a button to close the application
        self.close_button = ctk.CTkButton(self.frame, text="Close", command=self.close_app)
        self.close_button.pack(pady=10)

    def create_dev_info_tab_content(self):
        # Create a frame to hold the developer info
        dev_info_frame = ctk.CTkFrame(self.dev_info_tab)
        dev_info_frame.pack(expand=True, padx=10, pady=10)

        # Developer information text
        dev_info_text = """
        Developer Name: Mohammad Mahfuz Rahman
        Email: mahfuzrahman0712@gmail.com
        GitHub: https://github.com/mahfuz0712
        """

        # Create a label for developer information
        label = ctk.CTkLabel(dev_info_frame, text=dev_info_text, padx=20, pady=20)
        label.pack()

        # Close button for dev info tab
        close_button = ctk.CTkButton(dev_info_frame, text="Close", command=self.close_app)
        close_button.pack(pady=10)

    def center_window(self):
        # Get the dimensions of the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Get the dimensions of the window
        window_width = 360
        window_height = 300

        # Calculate x and y coordinates to center the window
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Set the position of the window
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def close_app(self):
        self.destroy()  # Close the application

    def generate_report(self):
        battery_info = self.get_battery_info()

        if isinstance(battery_info, str):
            # No battery found, change button color to red and text
            self.report_button.configure(text="No Battery Found", fg_color="red")
        else:
            # Battery found, generate the PDF and change button color to green and text
            self.generate_pdf(battery_info)
            self.report_button.configure(text="Report Generated", fg_color="green")

    def get_battery_info(self):
        # Get basic battery information
        battery = psutil.sensors_battery()
        if battery is None:
            return "No battery found."

        # Get battery health and other details (using WMIC on Windows)
        if psutil.WINDOWS:
            battery_info = self.get_battery_info_windows()
        else:
            battery_info = self.get_battery_info_linux()

        # Basic battery details
        info = {
            "Battery Percentage": f"{battery.percent}%",
            "Power Plugged": "Yes" if battery.power_plugged else "No",
            "Time Left": f"{battery.secsleft // 3600}h {(battery.secsleft % 3600) // 60}m" if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Unlimited",
            "Battery Health": battery_info.get("health", "Not Available"),
            "Design Capacity": battery_info.get("design_capacity", "Not Available"),
            "Full Charge Capacity": battery_info.get("full_charge_capacity", "Not Available"),
            "Charge Cycle": battery_info.get("charge_cycle", "Not Available"),
            "Battery Age": battery_info.get("battery_age", "Not Available")
        }
        return info

    def get_battery_info_windows(self):
        # Using PowerShell to get more battery details on Windows
        battery_info = {}

        try:
            result = subprocess.run(
                ['powershell', 'Get-WmiObject', 'Win32_Battery'],
                capture_output=True, text=True, check=True
            )
            output = result.stdout.strip()
            if output:
                # Parse PowerShell output to extract cycle count
                for line in output.splitlines():
                    if "CycleCount" in line:
                        battery_info["charge_cycle"] = line.split(":")[1].strip()
                        battery_info["health"] = "Not available"
                        battery_info["design_capacity"] = "Not available"
                        battery_info["full_charge_capacity"] = "Not available"
                        battery_info["battery_age"] = "Not available"
        except subprocess.CalledProcessError:
            battery_info = {
                "health": "Unable to fetch",
                "design_capacity": "Unable to fetch",
                "full_charge_capacity": "Unable to fetch",
                "charge_cycle": "Unable to fetch",
                "battery_age": "Unable to fetch"
            }

        return battery_info

    def get_battery_info_linux(self):
        # For Linux systems, we can use upower for additional details
        battery_info = {}

        try:
            result = subprocess.run(
                ['upower', '-i', '/org/freedesktop/UPower/devices/battery_BAT0'],
                capture_output=True, text=True, check=True
            )
            output = result.stdout.strip().split('\n')
            for line in output:
                if "energy-full-design" in line:
                    battery_info["design_capacity"] = line.split(":")[1].strip()
                elif "energy-full" in line:
                    battery_info["full_charge_capacity"] = line.split(":")[1].strip()
                elif "cycle-count" in line:
                    battery_info["charge_cycle"] = line.split(":")[1].strip()
                elif "battery-age" in line:
                    battery_info["battery_age"] = line.split(":")[1].strip()
                elif "state" in line:
                    battery_info["health"] = line.split(":")[1].strip()
        except subprocess.CalledProcessError:
            battery_info = {
                "health": "Unable to fetch",
                "design_capacity": "Unable to fetch",
                "full_charge_capacity": "Unable to fetch",
                "charge_cycle": "Unable to fetch",
                "battery_age": "Unable to fetch"
            }

        return battery_info

    def generate_pdf(self, battery_info):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)

        pdf.cell(0, 10, "Laptop Battery Health Report", ln=True, align="C")
        pdf.ln(10)

        # Adding the battery information to the PDF
        for key, value in battery_info.items():
            pdf.cell(200, 10, f"{key}: {value}", ln=True)

        # Save the generated PDF with a timestamp
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        pdf_output_path = f"battery_health_report_{now}.pdf"
        pdf.output(pdf_output_path)





if __name__ == "__main__":
    app = App()
    app.mainloop()
