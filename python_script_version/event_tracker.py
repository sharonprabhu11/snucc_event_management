import csv
import os
import uuid
import qrcode
import json
import datetime
from tabulate import tabulate
from typing import Dict, List, Tuple


class Attendee:
    
    def __init__(self, name: str, email: str, phone: str = "", role: str = "Attendee", unique_id: str = None):
        self.name = name
        self.email = email
        self.phone = phone
        self.role = role
        self.unique_id = unique_id or str(uuid.uuid4())
        self.check_in_status = False
        self.lunch_collected = set() 
        self.kit_collected = False
        self.registration_time = None
    
    def check_in(self) -> bool:
        if self.check_in_status:
            return False 
        self.check_in_status = True
        self.registration_time = datetime.datetime.now()
        return True
    
    def collect_lunch(self, date: str = None) -> bool:
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if date in self.lunch_collected:
            return False  
        self.lunch_collected.add(date)
        return True
    
    def collect_kit(self) -> bool:
        if self.kit_collected:
            return False 
        self.kit_collected = True
        return True
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "unique_id": self.unique_id,
            "check_in_status": self.check_in_status,
            "lunch_collected": list(self.lunch_collected),
            "kit_collected": self.kit_collected,
            "registration_time": str(self.registration_time) if self.registration_time else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Attendee':
        attendee = cls(
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            role=data.get("role", "Attendee"),
            unique_id=data["unique_id"]
        )
        attendee.check_in_status = data["check_in_status"]
        attendee.lunch_collected = set(data["lunch_collected"])
        attendee.kit_collected = data["kit_collected"]
        attendee.registration_time = data["registration_time"]
        return attendee



class UUIDGenerator:
    def generate_id(self) -> str:
        return str(uuid.uuid4())
    
    def save_id(self, attendee: Attendee, output_dir: str) -> str:
        file_path = os.path.join(output_dir, f"{attendee.email}.txt")
        with open(file_path, "w") as f:
            f.write(f"Name: {attendee.name}\n")
            f.write(f"Email: {attendee.email}\n")
            f.write(f"Phone: {attendee.phone}\n")
            f.write(f"Role: {attendee.role}\n")
            f.write(f"Unique ID: {attendee.unique_id}\n")
        return file_path


class QRCodeGenerator:
    #creates the QR, but open cv does not work on WSL2, so i'm not implementing the scanning of the QR, just showing that it can be done
    def generate_id(self) -> str:
        return str(uuid.uuid4())
    
    def save_id(self, attendee: Attendee, output_dir: str) -> str:
        file_path = os.path.join(output_dir, f"{attendee.email}.png")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(attendee.unique_id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)
        return file_path


class DataStore:
    
    def __init__(self, storage_path: str = "event_data"):
        self.storage_path = storage_path
        self.attendees_file = os.path.join(storage_path, "attendees.json")
        self.ensure_storage_exists()
    
    def ensure_storage_exists(self):
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def save_attendees(self, attendees: Dict[str, Attendee]):
        data = {uid: attendee.to_dict() for uid, attendee in attendees.items()}
        with open(self.attendees_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_attendees(self) -> Dict[str, Attendee]:
        if not os.path.exists(self.attendees_file):
            return {}
        
        with open(self.attendees_file, "r") as f:
            data = json.load(f)
        
        return {uid: Attendee.from_dict(attendee_data) for uid, attendee_data in data.items()}
    
    def create_backup(self, manual=False) -> str:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "manual_backup" if manual else "backup"
        backup_file = os.path.join(self.storage_path, f"{prefix}_{timestamp}.json")
        
        if os.path.exists(self.attendees_file):
            with open(self.attendees_file, "r") as src:
                with open(backup_file, "w") as dst:
                    dst.write(src.read())
        
        return backup_file


class EventManager:
    def __init__(self, id_generator=None):
        self.id_generator = id_generator if id_generator else UUIDGenerator()
        self.data_store = DataStore()
        self.attendees = self.data_store.load_attendees()
        self.id_output_dir = os.path.join(self.data_store.storage_path, "ids")
        
        if not os.path.exists(self.id_output_dir):
            os.makedirs(self.id_output_dir)
    
    def import_attendees_from_csv(self, csv_file: str) -> Tuple[int, List[str]]:
        imported_count = 0
        id_files = []
        
        try:
            with open(csv_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if any(attendee.email == row["Email"] for attendee in self.attendees.values()):
                        continue
                    
                    unique_id = self.id_generator.generate_id(None)
                    attendee = Attendee(
                        name=row["Name"],
                        email=row["Email"],
                        phone=row.get("Phone", ""),
                        role=row.get("Role", "Attendee"),
                        unique_id=unique_id
                    )
                    
                   
                    self.attendees[unique_id] = attendee
                    imported_count += 1
                    
                    #
                    id_file = self.id_generator.save_id(attendee, self.id_output_dir)
                    id_files.append(id_file)
            
       
            self.data_store.save_attendees(self.attendees)
            
           
            self.data_store.create_backup()
            
            return imported_count, id_files
            
        except Exception:
            print(f"Error importing attendees: {Exception}")
            return 0, []
    
    def check_in_attendee(self, unique_id: str) -> Tuple[bool, str]:
    
        if unique_id not in self.attendees:
            return False, "Attendee not found"
        
        attendee = self.attendees[unique_id]
        if attendee.check_in_status:
            return False, f"Attendee {attendee.name} already checked in"
        
        success = attendee.check_in()
        if success:
            self.data_store.save_attendees(self.attendees)
            return True, f"Successfully checked in {attendee.name}"
        else:
            return False, "Check-in failed"
    
    def collect_lunch(self, unique_id: str, date: str = None) -> Tuple[bool, str]:
        if unique_id not in self.attendees:
            return False, "Attendee not found"
        
        attendee = self.attendees[unique_id]
        if not attendee.check_in_status:
            return False, f"Attendee {attendee.name} has not checked in yet"
        
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if date in attendee.lunch_collected:
            return False, f"Attendee {attendee.name} already collected lunch for {date}"
        
        success = attendee.collect_lunch(date)
        if success:
            self.data_store.save_attendees(self.attendees)
            return True, f"Successfully marked lunch collected for {attendee.name}"
        else:
            return False, "Lunch collection marking failed"
    
    def collect_kit(self, unique_id: str) -> Tuple[bool, str]:
        if unique_id not in self.attendees:
            return False, "Attendee not found"
        
        attendee = self.attendees[unique_id]
        if not attendee.check_in_status:
            return False, f"Attendee {attendee.name} has not checked in yet"
        
        if attendee.kit_collected:
            return False, f"Attendee {attendee.name} already collected their kit"
        
        success = attendee.collect_kit()
        if success:
            self.data_store.save_attendees(self.attendees)
            return True, f"Successfully marked kit collected for {attendee.name}"
        else:
            return False, "Kit collection marking failed"
    
    def get_stats(self) -> dict:
        total_attendees = len(self.attendees)
        checked_in = sum(1 for attendee in self.attendees.values() if attendee.check_in_status)
        
        role_counts = {}
        checked_in_by_role = {}
        for attendee in self.attendees.values():
            role = attendee.role
            role_counts[role] = role_counts.get(role, 0) + 1
            if attendee.check_in_status:
                checked_in_by_role[role] = checked_in_by_role.get(role, 0) + 1
      
        lunch_by_date = {}
        for attendee in self.attendees.values():
            for date in attendee.lunch_collected:
                lunch_by_date[date] = lunch_by_date.get(date, 0) + 1
        
        kits_distributed = sum(1 for attendee in self.attendees.values() if attendee.kit_collected)
        
        return {
            "total_attendees": total_attendees,
            "checked_in": checked_in,
            "role_counts": role_counts,
            "checked_in_by_role": checked_in_by_role,
            "lunch_by_date": lunch_by_date,
            "kits_distributed": kits_distributed,
            "check_in_percentage": (checked_in / total_attendees * 100) if total_attendees > 0 else 0,
            "kit_distribution_percentage": (kits_distributed / total_attendees * 100) if total_attendees > 0 else 0
        }
    
    def search_attendees(self, query: str) -> List[Attendee]:
        results = []
        query = query.lower()
        
        for attendee in self.attendees.values():
            if (query in attendee.name.lower() or 
                query in attendee.email.lower() or 
                query in attendee.phone.lower() or
                query in attendee.role.lower() or
                query in attendee.unique_id.lower()):
                results.append(attendee)
        
        return results
    
    def export_report(self, filename: str = None) -> str:
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"event_report_{timestamp}.csv"
        
        file_path = os.path.join(self.data_store.storage_path, filename)
        
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Name", "Email", "Phone", "Role", "Unique ID", "Checked In", 
                "Registration Time", "Lunch Dates", "Kit Collected"
            ])
            
            for attendee in self.attendees.values():
                writer.writerow([
                    attendee.name,
                    attendee.email,
                    attendee.phone,
                    attendee.role,
                    attendee.unique_id,
                    "Yes" if attendee.check_in_status else "No",
                    attendee.registration_time or "",
                    ", ".join(sorted(attendee.lunch_collected)),
                    "Yes" if attendee.kit_collected else "No"
                ])
        
        return file_path
    
    def create_manual_backup(self) -> str:
        backup_file = self.data_store.create_backup(manual=True)
        return backup_file


class EventManagementPlatformCLI:
    def __init__(self):
        print("\n===== SNUCC Event Management Platform =====\n")
        self.event_manager = EventManager(id_generator=QRCodeGenerator())
        self.menu_options = {
            "1": self.import_attendees,
            "2": self.check_in_attendee,
            "3": self.mark_lunch_collected,
            "4": self.mark_kit_collected,
            "5": self.view_stats,
            "6": self.search_attendee,
            "7": self.export_event_report,
            "8": self.create_backup, 
            "9": self.exit_program 
        }
    
    def display_menu(self):
        print("\n===== SNUCC Event Tracker Menu =====")
        print("1. Import Attendees from CSV")
        print("2. Check In Attendee")
        print("3. Mark Lunch Collected")
        print("4. Mark Kit Collected")
        print("5. View Event Statistics")
        print("6. Search Attendee")
        print("7. Export Event Report")
        print("8. Create Data Backup") 
        print("9. Exit")    
        return input("\nSelect an option (1-8): ")
    
    def import_attendees(self):
        csv_file = input("Enter path to CSV file: ")
        if not os.path.exists(csv_file):
            print(f"File {csv_file} not found.")
            return
        
        count, files = self.event_manager.import_attendees_from_csv(csv_file)
        print(f"Successfully imported {count} attendees.")
        print(f"ID files generated in {self.event_manager.id_output_dir}")
    
    def check_in_attendee(self):
        unique_id = input("Enter attendee unique ID: ")
        success, message = self.event_manager.check_in_attendee(unique_id)
        print(message)
    
    def mark_lunch_collected(self):
        unique_id = input("Enter attendee unique ID: ")
        date = input("Enter date (YYYY-MM-DD) or leave blank for today: ")
        date = date if date else None
        success, message = self.event_manager.collect_lunch(unique_id, date)
        print(message)
    
    def mark_kit_collected(self):
        unique_id = input("Enter attendee unique ID: ")
        success, message = self.event_manager.collect_kit(unique_id)
        print(message)
    
    def view_stats(self):
        stats = self.event_manager.get_stats()
        print("\n===== Event Statistics =====")
        print(f"Total Attendees: {stats['total_attendees']}")
        print(f"Checked In: {stats['checked_in']} ({stats['check_in_percentage']:.1f}%)")
        print(f"Kits Distributed: {stats['kits_distributed']} ({stats['kit_distribution_percentage']:.1f}%)")
        
        print("\nAttendees by Role:")
        for role, count in stats['role_counts'].items():
            checked_in = stats['checked_in_by_role'].get(role, 0)
            percentage = (checked_in / count * 100) if count > 0 else 0
            print(f"  {role}: {count} total, {checked_in} checked in ({percentage:.1f}%)")
        
        print("\nLunch Distribution by Date:")
        for date, count in stats['lunch_by_date'].items():
            print(f"  {date}: {count} attendees")
    
    def search_attendee(self):
        query = input("Enter search term (name, email, phone, role): ")
        results = self.event_manager.search_attendees(query)
        
        if not results:
            print("No attendees found matching your search.")
            return
        
        print(f"\nFound {len(results)} attendees:")
        table_data = []
        for attendee in results:
            table_data.append([
                attendee.name,
                attendee.email,
                attendee.role,
                "Yes" if attendee.check_in_status else "No",
                ", ".join(sorted(attendee.lunch_collected)) if attendee.lunch_collected else "None",
                "Yes" if attendee.kit_collected else "No"
            ])
        
        headers = ["Name", "Email", "Role", "Checked In", "Lunch Dates", "Kit Collected"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def export_event_report(self):
        filename = input("Enter filename for report (or leave blank for auto-generated): ")
        filename = filename if filename else None
        file_path = self.event_manager.export_report(filename)
        print(f"Report exported to {file_path}")
    
    def create_backup(self):
        backup_file = self.event_manager.create_manual_backup()
        print(f"Manual backup created successfully: {backup_file}")
    
    
    def exit_program(self):
        print("Thank you for using SNUCC Event Management Platform!")
        exit(0)
    
    def run(self):
        while True:
            option = self.display_menu()
            if option in self.menu_options:
                self.menu_options[option]()
            else:
                print("Invalid option. Please try again.")


def main():
    try:
        cli = EventManagementPlatformCLI()
        cli.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        with open("error_log.txt", "a") as f:
            f.write(f"{datetime.datetime.now()}: {str(e)}\n")

if __name__ == "__main__":
    main()