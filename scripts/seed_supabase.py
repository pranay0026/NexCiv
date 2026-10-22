import sys
from pathlib import Path
import json

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import settings
from database import get_supabase

def seed_supabase():
    sb = get_supabase()
    if sb is None:
        print("[!] Supabase client could not be initialized. Check SUPABASE_URL and SUPABASE_KEY in backend/.env")
        return

    print(f"[*] Connecting to Supabase at: {settings.SUPABASE_URL}")

    # 1. Check & Seed Employees
    employees_file = backend_dir / "data" / "local_employees.json"
    if employees_file.exists():
        with open(employees_file, "r", encoding="utf-8") as f:
            employees = json.load(f)
        print(f"[*] Found {len(employees)} local employee records.")

        try:
            # Check if employees table exists
            res = sb.table("employees").select("employee_code").limit(5).execute()
            existing_codes = set()
            try:
                full_res = sb.table("employees").select("employee_code").execute()
                if full_res.data:
                    existing_codes = {r["employee_code"] for r in full_res.data}
            except Exception:
                pass

            to_insert = [e for e in employees if e["employee_code"] not in existing_codes]
            if to_insert:
                print(f"[*] Seeding {len(to_insert)} new employees into Supabase cloud table...")
                # Insert in batches of 10
                for i in range(0, len(to_insert), 10):
                    batch = to_insert[i:i+10]
                    sb.table("employees").insert(batch).execute()
                print(f"[+] Successfully seeded employees into Supabase!")
            else:
                print(f"[+] All {len(employees)} employees already present in Supabase.")
        except Exception as e:
            if "PGRST205" in str(e) or "Could not find the table" in str(e):
                print("\n[!] The 'employees' table does not exist in Supabase yet.")
                print("    Please run 'supabase_setup.sql' in your Supabase Dashboard -> SQL Editor.\n")
            elif "42501" in str(e):
                print("\n[!] Supabase Row-Level Security (RLS) blocked the employee insert.")
                print("    Please run in Supabase SQL Editor: ALTER TABLE employees DISABLE ROW LEVEL SECURITY;\n")
            else:
                print(f"[!] Employee seed note: {e}")

    # 2. Check & Seed Complaints
    complaints_file = backend_dir / "data" / "local_complaints.json"
    if complaints_file.exists():
        with open(complaints_file, "r", encoding="utf-8") as f:
            complaints = json.load(f)
        print(f"[*] Found {len(complaints)} local complaint records.")

        try:
            res = sb.table("complaints").select("id").limit(1).execute()
            if not res.data or len(res.data) == 0:
                print("[*] Complaints table is currently empty in Supabase. Attempting to seed sample complaints...")
                for c in complaints[:5]:
                    try:
                        clean_c = {k: v for k, v in c.items() if v is not None}
                        sb.table("complaints").insert(clean_c).execute()
                    except Exception as err:
                        print(f"Complaint insert note: {err}")
                print("[+] Complaints seeding attempt completed.")
            else:
                print(f"[+] Supabase complaints table has {len(res.data)} existing records.")
        except Exception as e:
            if "42501" in str(e):
                print("\n[!] Supabase Row-Level Security (RLS) blocked the complaints insert.")
                print("    Please run in Supabase SQL Editor: ALTER TABLE complaints DISABLE ROW LEVEL SECURITY;\n")
            else:
                print(f"[!] Complaints check note: {e}")

if __name__ == "__main__":
    seed_supabase()
