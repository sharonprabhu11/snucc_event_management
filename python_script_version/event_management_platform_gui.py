import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import datetime
import csv
from tabulate import tabulate
import sys
from typing import Dict, List, Optional
from event_tracker import EventManager, QRCodeGenerator, Attendee

class EventManagementGUI:
    
    def __init__(self, root):
        self.root = root
        self.root.title("SNUCC Event Management Platform")
        self.root.geometry("900x600")
        self.root.minsize(900, 600)
        
        
        self.event_manager = EventManager(id_generator=QRCodeGenerator())
        
        self.setup_ui()
        
        self.update_stats()
        
        self.populate_attendee_list()
    
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
       
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.attendees_tab = ttk.Frame(self.notebook)
        self.import_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.attendees_tab, text="Attendees")
        self.notebook.add(self.import_tab, text="Import")
        self.notebook.add(self.reports_tab, text="Reports")
        
      
        self.setup_dashboard_tab()
        self.setup_attendees_tab()
        self.setup_import_tab()
        self.setup_reports_tab()

    def setup_dashboard_tab(self):
    
        stats_frame = ttk.LabelFrame(self.dashboard_tab, text="Event Statistics")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
     
        self.stats_text = tk.Text(stats_frame, height=20, width=80, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.stats_text.config(state=tk.DISABLED)
        
        buttons_frame = ttk.Frame(self.dashboard_tab)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="Check In Attendee", command=self.check_in_attendee).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Mark Lunch Collected", command=self.mark_lunch_collected).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Mark Kit Collected", command=self.mark_kit_collected).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Refresh Stats", command=self.update_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Create Backup", command=self.create_backup).pack(side=tk.LEFT, padx=5)

    def setup_attendees_tab(self):
       
        search_frame = ttk.Frame(self.attendees_tab)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_attendees).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        list_frame = ttk.Frame(self.attendees_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Name", "Email", "Role", "Checked In", "Lunch", "Kit")
        self.attendee_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        

        for col in columns:
            self.attendee_tree.heading(col, text=col)
            if col == "Email":
                self.attendee_tree.column(col, width=200)
            else:
                self.attendee_tree.column(col, width=100)
        

        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.attendee_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.attendee_tree.xview)
        self.attendee_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
       
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.attendee_tree.pack(fill=tk.BOTH, expand=True)
        
        self.create_context_menu()

    def setup_import_tab(self):
      
        import_frame = ttk.LabelFrame(self.import_tab, text="Import Attendees from CSV")
        import_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
      
        ttk.Label(import_frame, text="Select a CSV file to import attendees. The CSV file should have the following columns:").pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(import_frame, text="- Name (required)").pack(anchor=tk.W, padx=20, pady=2)
        ttk.Label(import_frame, text="- Email (required)").pack(anchor=tk.W, padx=20, pady=2)
        ttk.Label(import_frame, text="- Phone (optional)").pack(anchor=tk.W, padx=20, pady=2)
        ttk.Label(import_frame, text="- Role (optional, defaults to 'Attendee')").pack(anchor=tk.W, padx=20, pady=2)
        
        file_frame = ttk.Frame(import_frame)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(import_frame, text="Import Attendees", command=self.import_attendees).pack(pady=10)
        
     
        self.import_status_var = tk.StringVar()
        ttk.Label(import_frame, textvariable=self.import_status_var).pack(pady=5)

    def setup_reports_tab(self):
        reports_frame = ttk.LabelFrame(self.reports_tab, text="Generate Reports")
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(reports_frame, text="Export Full Attendee Report", 
                  command=lambda: self.export_report()).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Button(reports_frame, text="Export Check-In Summary", 
                  command=lambda: self.export_check_in_summary()).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Button(reports_frame, text="Export Lunch Distribution Summary", 
                  command=lambda: self.export_lunch_summary()).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Button(reports_frame, text="Export Kit Distribution Summary", 
                  command=lambda: self.export_kit_summary()).pack(anchor=tk.W, padx=10, pady=5)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Check In", command=self.context_check_in)
        self.context_menu.add_command(label="Mark Lunch Collected", command=self.context_lunch_collected)
        self.context_menu.add_command(label="Mark Kit Collected", command=self.context_kit_collected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Details", command=self.view_attendee_details)
  
        self.attendee_tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        item = self.attendee_tree.identify_row(event.y)
        if item:
            self.attendee_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def context_check_in(self):
        selected_item = self.attendee_tree.selection()
        if selected_item:
            attendee_id = self.get_attendee_id_from_selection(selected_item[0])
            if attendee_id:
                success, message = self.event_manager.check_in_attendee(attendee_id)
                messagebox.showinfo("Check In", message)
                self.update_attendee_display(selected_item[0], attendee_id)
                self.update_stats()
    
    def context_lunch_collected(self):
        selected_item = self.attendee_tree.selection()
        if selected_item:
            attendee_id = self.get_attendee_id_from_selection(selected_item[0])
            if attendee_id:
                date = simpledialog.askstring("Lunch Collection", 
                                             "Enter date (YYYY-MM-DD) or leave blank for today:",
                                             parent=self.root)
                date = date if date else None
                success, message = self.event_manager.collect_lunch(attendee_id, date)
                messagebox.showinfo("Lunch Collection", message)
                self.update_attendee_display(selected_item[0], attendee_id)
                self.update_stats()
    
    def context_kit_collected(self):
        selected_item = self.attendee_tree.selection()
        if selected_item:
            attendee_id = self.get_attendee_id_from_selection(selected_item[0])
            if attendee_id:
                success, message = self.event_manager.collect_kit(attendee_id)
                messagebox.showinfo("Kit Collection", message)
                self.update_attendee_display(selected_item[0], attendee_id)
                self.update_stats()
    
    def update_attendee_display(self, tree_item, attendee_id):
        attendee = self.event_manager.attendees.get(attendee_id)
        if attendee:
            self.attendee_tree.item(tree_item, values=(
                attendee.name,
                attendee.email,
                attendee.role,
                "Yes" if attendee.check_in_status else "No",
                len(attendee.lunch_collected),
                "Yes" if attendee.kit_collected else "No"
            ))
    
    def view_attendee_details(self):
        selected_item = self.attendee_tree.selection()
        if selected_item:
            attendee_id = self.get_attendee_id_from_selection(selected_item[0])
            if attendee_id:
                attendee = self.event_manager.attendees.get(attendee_id)
                if attendee:
                    details = f"Name: {attendee.name}\n"
                    details += f"Email: {attendee.email}\n"
                    details += f"Phone: {attendee.phone}\n"
                    details += f"Role: {attendee.role}\n"
                    details += f"Unique ID: {attendee.unique_id}\n"
                    details += f"Checked In: {attendee.check_in_status}\n"
                    details += f"Registration Time: {attendee.registration_time}\n"
                    details += f"Lunch Collected: {', '.join(sorted(attendee.lunch_collected)) if attendee.lunch_collected else 'None'}\n"
                    details += f"Kit Collected: {attendee.kit_collected}"
                    
                    details_window = tk.Toplevel(self.root)
                    details_window.title(f"Attendee Details: {attendee.name}")
                    details_window.geometry("500x300")
                    
                    text_widget = tk.Text(details_window, wrap=tk.WORD)
                    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    text_widget.insert(tk.END, details)
                    text_widget.config(state=tk.DISABLED)
                    
                    scrollbar = ttk.Scrollbar(text_widget, command=text_widget.yview)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    text_widget.config(yscrollcommand=scrollbar.set)
                    
    
                    details_window.transient(self.root)
                    details_window.grab_set()
                    self.root.wait_window(details_window)
    
    def get_attendee_id_from_selection(self, tree_item):
        item_values = self.attendee_tree.item(tree_item, "values")
        email = item_values[1]  
        
        for attendee_id, attendee in self.event_manager.attendees.items():
            if attendee.email == email:
                return attendee_id
        
        return None
    
    def update_stats(self):
        stats = self.event_manager.get_stats()
        
        stats_text = f"Total Attendees: {stats['total_attendees']}\n"
        stats_text += f"Checked In: {stats['checked_in']} ({stats['check_in_percentage']:.1f}%)\n"
        stats_text += f"Kits Distributed: {stats['kits_distributed']} ({stats['kit_distribution_percentage']:.1f}%)\n\n"
        
        stats_text += "Attendees by Role:\n"
        for role, count in stats['role_counts'].items():
            checked_in = stats['checked_in_by_role'].get(role, 0)
            percentage = (checked_in / count * 100) if count > 0 else 0
            stats_text += f"  {role}: {count} total, {checked_in} checked in ({percentage:.1f}%)\n"
        
        stats_text += "\nLunch Distribution by Date:\n"
        for date, count in stats['lunch_by_date'].items():
            stats_text += f"  {date}: {count} attendees\n"
        
        # Update the text widget
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
        self.stats_text.config(state=tk.DISABLED)
    
    def populate_attendee_list(self, filtered=None):
        self.attendee_tree.delete(*self.attendee_tree.get_children())
       
        attendees = filtered if filtered else self.event_manager.attendees.values()
        
        for attendee in attendees:
            self.attendee_tree.insert("", tk.END, values=(
                attendee.name,
                attendee.email,
                attendee.role,
                "Yes" if attendee.check_in_status else "No",
                len(attendee.lunch_collected),
                "Yes" if attendee.kit_collected else "No"
            ))
    
    def check_in_attendee(self):
        unique_id = simpledialog.askstring("Check In", "Enter attendee unique ID:", parent=self.root)
        if unique_id:
            success, message = self.event_manager.check_in_attendee(unique_id)
            messagebox.showinfo("Check In", message)
            self.populate_attendee_list()
            self.update_stats()
    
    def mark_lunch_collected(self):
        unique_id = simpledialog.askstring("Lunch Collection", "Enter attendee unique ID:", parent=self.root)
        if unique_id:
            date = simpledialog.askstring("Lunch Collection", 
                                         "Enter date (YYYY-MM-DD) or leave blank for today:",
                                         parent=self.root)
            date = date if date else None
            success, message = self.event_manager.collect_lunch(unique_id, date)
            messagebox.showinfo("Lunch Collection", message)
            self.populate_attendee_list()
            self.update_stats()
    
    def mark_kit_collected(self):
        unique_id = simpledialog.askstring("Kit Collection", "Enter attendee unique ID:", parent=self.root)
        if unique_id:
            success, message = self.event_manager.collect_kit(unique_id)
            messagebox.showinfo("Kit Collection", message)
            self.populate_attendee_list()
            self.update_stats()
    
    def create_backup(self):
        backup_file = self.event_manager.create_manual_backup()
        messagebox.showinfo("Backup", f"Manual backup created successfully: {backup_file}")
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filename:
            self.file_path_var.set(filename)
    
    def import_attendees(self):
        csv_file = self.file_path_var.get()
        if not csv_file:
            messagebox.showerror("Error", "Please select a CSV file")
            return
        
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", f"File {csv_file} not found")
            return
        
        count, files = self.event_manager.import_attendees_from_csv(csv_file)
        
        if count > 0:
            messagebox.showinfo("Import Successful", 
                               f"Successfully imported {count} attendees.\nID files generated in {self.event_manager.id_output_dir}")
            self.import_status_var.set(f"Last import: {count} attendees on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
    
            self.populate_attendee_list()
            self.update_stats()
        else:
            messagebox.showwarning("Import Result", "No new attendees were imported.")
    
    def search_attendees(self):
        query = self.search_var.get()
        if query:
            results = self.event_manager.search_attendees(query)
            self.populate_attendee_list(results)
        else:
            self.populate_attendee_list()
    
    def clear_search(self):
        self.search_var.set("")
        self.populate_attendee_list()
    
    def export_report(self, report_type: str = "full"):
        filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
        default_name = f"{report_type}_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=filetypes,
            initialfile=default_name,
            title="Save Report As"
        )
        
        if not filename:
            return 
        
        if report_type == "full":
            file_path = self.event_manager.export_report(os.path.basename(filename))
            messagebox.showinfo("Export Complete", f"Report exported to {file_path}")
        else:
            self.export_custom_report(filename, report_type)
    
    def export_check_in_summary(self):
        self.export_report("check_in")
    
    def export_lunch_summary(self):
        self.export_report("lunch")
    
    def export_kit_summary(self):
        self.export_report("kit")
    
    def export_custom_report(self, filename: str, report_type: str):
        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                
                if report_type == "check_in":
                    writer.writerow(["Name", "Email", "Role", "Checked In", "Registration Time"])
                    for attendee in self.event_manager.attendees.values():
                        writer.writerow([
                            attendee.name,
                            attendee.email,
                            attendee.role,
                            "Yes" if attendee.check_in_status else "No",
                            attendee.registration_time or ""
                        ])
                
                elif report_type == "lunch":
                    writer.writerow(["Date", "Count", "Attendees"])
                    lunch_by_date = {}
                  
                    for attendee in self.event_manager.attendees.values():
                        for date in attendee.lunch_collected:
                            if date not in lunch_by_date:
                                lunch_by_date[date] = []
                            lunch_by_date[date].append(attendee.name)
                    
                
                    for date, attendees in sorted(lunch_by_date.items()):
                        writer.writerow([date, len(attendees), ", ".join(attendees)])
                
                elif report_type == "kit":
                    writer.writerow(["Name", "Email", "Role", "Kit Collected"])
                    for attendee in self.event_manager.attendees.values():
                        writer.writerow([
                            attendee.name,
                            attendee.email,
                            attendee.role,
                            "Yes" if attendee.kit_collected else "No"
                        ])
            
            messagebox.showinfo("Export Complete", f"Report exported to {filename}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred during export: {str(e)}")


def main():
    root = tk.Tk()
    root.title("SNUCC Event Management Platform")
    app = EventManagementGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()