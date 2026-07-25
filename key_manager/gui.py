import os
import uuid
import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timezone
from typing import List, Optional

# Εισαγωγή των απαραίτητων στοιχείων από το project
from main import AsyncSessionLocal, OSINTApiKey, engine, Base
from key_vault import KeyVault
from osint_providers import list_supported_providers

# Ορισμός της κύριας κλάσης της εφαρμογής GUI
class OSINTKeyManagerGUI:
    """
    Διεπαφή χρήστη (GUI) με Tkinter για τη διαχείριση των OSINT API Keys.
    Συνδέεται απευθείας με τη βάση δεδομένων και χρησιμοποιεί το KeyVault.
    """

    def __init__(self, root_window: tk.Tk) -> None:
        """
        Αρχικοποίηση του παραθύρου και των στοιχείων της διεπαφής.
        """
        self.root = root_window
        self.root.title("Osinit - OSINT Key Manager")
        self.root.geometry("1100x650")
        
        # Αρχικοποίηση του KeyVault για κρυπτογράφηση/αποκρυπτογράφηση
        self.vault = KeyVault()
        
        # Ορισμός χρωματικής παλέτας (Slate & Sky Blue από τις οδηγίες branding)
        self.bg_color = "#020617"       # bg-slate-950
        self.frame_color = "#0f172a"    # bg-slate-900
        self.border_color = "#1e293b"   # border-slate-800
        self.text_color = "#f1f5f9"     # text-slate-100
        self.muted_text = "#94a3b8"     # text-slate-400
        self.accent_color = "#38bdf8"   # text-sky-400
        self.button_color = "#0c4a6e"   # bg-sky-900
        self.alert_color = "#f87171"    # text-red-400
        
        # Ρύθμιση φόντου του κύριου παραθύρου
        self.root.configure(bg=self.bg_color)
        
        # Αρχικοποίηση των πινάκων στη βάση δεδομένων
        self.initialize_database()
        
        # Δημιουργία των στοιχείων του UI
        self.create_widgets()
        
        # Φόρτωση των αποθηκευμένων κλειδιών
        self.refresh_keys_table()

    def initialize_database(self) -> None:
        """
        Δημιουργεί τους απαραίτητους πίνακες στη βάση δεδομένων αν δεν υπάρχουν.
        """
        async def create_tables() -> None:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
                
        try:
            asyncio.run(create_tables())
        except Exception as database_error:
            messagebox.showerror(
                "Σφάλμα Βάσης Δεδομένων", 
                f"Αποτυχία σύνδεσης στη βάση δεδομένων:\n{database_error}"
            )

    def create_widgets(self) -> None:
        """
        Δημιουργεί και τοποθετεί τα widgets στο παράθυρο.
        """
        # ----------------------------------------------------
        # 1. Header (Τίτλος και Υπότιτλος)
        # ----------------------------------------------------
        self.header_frame = tk.Frame(self.root, bg=self.bg_color, py=10)
        self.header_frame.pack(fill="x", padx=20)
        
        self.title_label = tk.Label(
            self.header_frame, 
            text="OSINT KEY MANAGER", 
            font=("Inter", 18, "bold"), 
            fg=self.text_color, 
            bg=self.bg_color
        )
        self.title_label.pack(side="left")
        
        self.subtitle_label = tk.Label(
            self.header_frame, 
            text="Local Secure Vault for OSINT API Credentials", 
            font=("Inter", 10), 
            fg=self.muted_text, 
            bg=self.bg_color
        )
        self.subtitle_label.pack(side="left", padx=15, pady=5)

        # ----------------------------------------------------
        # 2. Main Container (Χωρισμός σε Input και Table)
        # ----------------------------------------------------
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left Panel (Φόρμα Εισαγωγής)
        self.left_panel = tk.LabelFrame(
            self.main_container, 
            text=" Add API Key ", 
            font=("Inter", 10, "bold"), 
            fg=self.accent_color, 
            bg=self.frame_color, 
            bd=1, 
            relief="solid"
        )
        self.left_panel.pack(side="left", fill="both", expand=False, width=320, padx=(0, 10))
        self.left_panel.pack_propagate(False)
        
        # Right Panel (Πίνακας Προβολής)
        self.right_panel = tk.LabelFrame(
            self.main_container, 
            text=" Registered API Keys ", 
            font=("Inter", 10, "bold"), 
            fg=self.accent_color, 
            bg=self.frame_color, 
            bd=1, 
            relief="solid"
        )
        self.right_panel.pack(side="right", fill="both", expand=True)

        # ----------------------------------------------------
        # 3. Left Panel Widgets (Φόρμα Εισαγωγής)
        # ----------------------------------------------------
        # Επιλογή Provider
        self.provider_label = tk.Label(
            self.left_panel, 
            text="OSINT Provider:", 
            fg=self.text_color, 
            bg=self.frame_color, 
            font=("Inter", 9)
        )
        self.provider_label.pack(anchor="w", padx=15, pady=(15, 2))
        
        self.provider_var = tk.StringVar()
        self.provider_combo = ttk.Combobox(
            self.left_panel, 
            textvariable=self.provider_var, 
            values=list_supported_providers(), 
            state="readonly",
            font=("Inter", 9)
        )
        self.provider_combo.pack(fill="x", padx=15, pady=2)
        self.provider_combo.set("shodan")
        
        # Όνομα Κλειδιού
        self.key_name_label = tk.Label(
            self.left_panel, 
            text="Key Description/Name:", 
            fg=self.text_color, 
            bg=self.frame_color, 
            font=("Inter", 9)
        )
        self.key_name_label.pack(anchor="w", padx=15, pady=(10, 2))
        
        self.key_name_entry = tk.Entry(
            self.left_panel, 
            fg=self.text_color, 
            bg=self.bg_color, 
            insertbackground=self.text_color, 
            relief="solid", 
            bd=1, 
            font=("Inter", 9)
        )
        self.key_name_entry.pack(fill="x", padx=15, pady=2)
        self.key_name_entry.insert(0, "Production Key")
        
        # Τιμή API Key
        self.key_value_label = tk.Label(
            self.left_panel, 
            text="API Key Value:", 
            fg=self.text_color, 
            bg=self.frame_color, 
            font=("Inter", 9)
        )
        self.key_value_label.pack(anchor="w", padx=15, pady=(10, 2))
        
        self.key_value_entry = tk.Entry(
            self.left_panel, 
            show="*", 
            fg=self.text_color, 
            bg=self.bg_color, 
            insertbackground=self.text_color, 
            relief="solid", 
            bd=1, 
            font=("Inter", 9)
        )
        self.key_value_entry.pack(fill="x", padx=15, pady=2)
        
        # Checkbox για εμφάνιση/απόκρυψη κλειδιού κατά την πληκτρολόγηση
        self.show_key_var = tk.BooleanVar(value=False)
        self.show_key_check = tk.Checkbutton(
            self.left_panel, 
            text="Show characters", 
            variable=self.show_key_var, 
            command=self.toggle_key_visibility, 
            fg=self.muted_text, 
            bg=self.frame_color, 
            activeforeground=self.text_color, 
            activebackground=self.frame_color, 
            selectcolor=self.bg_color,
            font=("Inter", 8)
        )
        self.show_key_check.pack(anchor="w", padx=15, pady=2)

        # Κουμπιά Ενεργειών
        self.add_button = tk.Button(
            self.left_panel, 
            text="Encrypt & Save Key", 
            command=self.handle_add_key, 
            bg=self.button_color, 
            fg=self.text_color, 
            activebackground=self.accent_color, 
            activeforeground=self.bg_color, 
            relief="flat", 
            font=("Inter", 10, "bold")
        )
        self.add_button.pack(fill="x", padx=15, pady=(25, 10))
        
        self.generate_button = tk.Button(
            self.left_panel, 
            text="Generate System Key", 
            command=self.handle_generate_internal_key, 
            bg=self.frame_color, 
            fg=self.accent_color, 
            activebackground=self.accent_color, 
            activeforeground=self.bg_color, 
            relief="solid", 
            bd=1, 
            font=("Inter", 9, "bold")
        )
        self.generate_button.pack(fill="x", padx=15, pady=5)

        # ----------------------------------------------------
        # 4. Right Panel Widgets (Πίνακας & Actions)
        # ----------------------------------------------------
        # Διαμόρφωση στυλ για το Treeview (Πίνακας)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Treeview", 
            background=self.frame_color, 
            foreground=self.text_color, 
            fieldbackground=self.frame_color, 
            bordercolor=self.border_color, 
            rowheight=25, 
            font=("Inter", 9)
        )
        self.style.map(
            "Treeview", 
            background=[("selected", self.button_color)], 
            foreground=[("selected", self.text_color)]
        )
        self.style.configure(
            "Treeview.Heading", 
            background=self.border_color, 
            foreground=self.text_color, 
            relief="flat", 
            font=("Inter", 9, "bold")
        )
        
        # Ορισμός στηλών του πίνακα
        self.keys_tree = ttk.Treeview(
            self.right_panel, 
            columns=("id", "provider", "name", "masked", "created"), 
            show="headings"
        )
        
        self.keys_tree.heading("id", text="UUID")
        self.keys_tree.heading("provider", text="Provider")
        self.keys_tree.heading("name", text="Description")
        self.keys_tree.heading("masked", text="Masked API Key")
        self.keys_tree.heading("created", text="Created At (UTC)")
        
        self.keys_tree.column("id", width=220, anchor="center")
        self.keys_tree.column("provider", width=120, anchor="w")
        self.keys_tree.column("name", width=150, anchor="w")
        self.keys_tree.column("masked", width=120, anchor="center")
        self.keys_tree.column("created", width=160, anchor="center")
        
        # Scrollbar για τον πίνακα
        self.scrollbar = ttk.Scrollbar(
            self.right_panel, 
            orient="vertical", 
            command=self.keys_tree.yview
        )
        self.keys_tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.keys_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        self.scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # ----------------------------------------------------
        # 5. Bottom Actions (Κάτω από τον πίνακα)
        # ----------------------------------------------------
        self.bottom_frame = tk.Frame(self.root, bg=self.bg_color)
        self.bottom_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        self.decrypt_button = tk.Button(
            self.bottom_frame, 
            text="Decrypt & Show API Key", 
            command=self.handle_decrypt_key, 
            bg=self.button_color, 
            fg=self.text_color, 
            activebackground=self.accent_color, 
            activeforeground=self.bg_color, 
            relief="flat", 
            font=("Inter", 9, "bold")
        )
        self.decrypt_button.pack(side="left", padx=(0, 10))
        
        self.delete_button = tk.Button(
            self.bottom_frame, 
            text="Delete Selected Key", 
            command=self.handle_delete_key, 
            bg="#3b0712",  # dark red background
            fg=self.alert_color, 
            activebackground=self.alert_color, 
            activeforeground=self.bg_color, 
            relief="solid", 
            bd=1, 
            font=("Inter", 9, "bold")
        )
        self.delete_button.pack(side="left", padx=10)
        
        self.refresh_button = tk.Button(
            self.bottom_frame, 
            text="Refresh List", 
            command=self.refresh_keys_table, 
            bg=self.frame_color, 
            fg=self.muted_text, 
            activebackground=self.border_color, 
            activeforeground=self.text_color, 
            relief="solid", 
            bd=1, 
            font=("Inter", 9)
        )
        self.refresh_button.pack(side="right")

    def toggle_key_visibility(self) -> None:
        """
        Εναλλάσσει την ορατότητα των χαρακτήρων στο πεδίο API Key.
        """
        if self.show_key_var.get():
            self.key_value_entry.configure(show="")
        else:
            self.key_value_entry.configure(show="*")

    def refresh_keys_table(self) -> None:
        """
        Ανακτά τα κλειδιά από τη βάση δεδομένων και ενημερώνει τον πίνακα.
        """
        # Καθαρισμός υπαρχόντων στοιχείων στον πίνακα
        for item in self.keys_tree.get_children():
            self.keys_tree.delete(item)
            
        async def load_keys() -> List[OSINTApiKey]:
            async with AsyncSessionLocal() as session:
                query = select(OSINTApiKey).order_by(OSINTApiKey.created_at.desc())
                query_result = await session.execute(query)
                return list(query_result.scalars().all())
                
        try:
            keys_list = asyncio.run(load_keys())
            for key_record in keys_list:
                created_str = key_record.created_at.strftime("%Y-%m-%d %H:%M UTC")
                self.keys_tree.insert(
                    "", 
                    "end", 
                    values=(
                        str(key_record.id),
                        key_record.provider_name,
                        key_record.key_name,
                        key_record.masked_value,
                        created_str
                    )
                )
        except Exception as load_error:
            messagebox.showerror(
                "Σφάλμα Φόρτωσης", 
                f"Αποτυχία φόρτωσης κλειδιών από τη βάση δεδομένων:\n{load_error}"
            )

    def handle_add_key(self) -> None:
        """
        Διαβάζει τα δεδομένα από τη φόρμα, κρυπτογραφεί το API key και το αποθηκεύει.
        """
        provider = self.provider_var.get().strip().lower()
        key_name = self.key_name_entry.get().strip()
        key_value = self.key_value_entry.get().strip()
        
        if not key_name or not key_value:
            messagebox.showwarning(
                "Ελλιπή Στοιχεία", 
                "Παρακαλώ συμπληρώστε την περιγραφή και την τιμή του API Key."
            )
            return
            
        # Κρυπτογράφηση και προετοιμασία συγκαλυμμένης τιμής
        encrypted_val = self.vault.encrypt_key(key_value)
        masked_val = self.vault.mask_api_key(key_value)
        
        async def save_key() -> None:
            async with AsyncSessionLocal() as session:
                new_key = OSINTApiKey(
                    id=uuid.uuid4(),
                    provider_name=provider,
                    key_name=key_name,
                    encrypted_value=encrypted_val,
                    masked_value=masked_val,
                    is_active=True
                )
                session.add(new_key)
                await session.commit()
                
        try:
            asyncio.run(save_key())
            # Καθαρισμός του πεδίου κλειδιού μετά την αποθήκευση
            self.key_value_entry.delete(0, "end")
            self.refresh_keys_table()
            messagebox.showinfo("Επιτυχία", f"Το API Key για την υπηρεσία '{provider}' αποθηκεύτηκε με ασφάλεια.")
        except Exception as save_error:
            messagebox.showerror("Σφάλμα Αποθήκευσης", f"Αποτυχία αποθήκευσης στη βάση δεδομένων:\n{save_error}")

    def handle_generate_internal_key(self) -> None:
        """
        Δημιουργεί αυτόματα ένα τυχαίο API Key για εσωτερική χρήση.
        """
        key_name = self.key_name_entry.get().strip()
        if not key_name:
            key_name = "Generated Internal Key"
            
        # Παραγωγή τυχαίου κλειδιού
        raw_key = self.vault.generate_random_api_key(prefix="osinit_key")
        encrypted_val = self.vault.encrypt_key(raw_key)
        masked_val = self.vault.mask_api_key(raw_key)
        
        async def save_internal_key() -> None:
            async with AsyncSessionLocal() as session:
                new_key = OSINTApiKey(
                    id=uuid.uuid4(),
                    provider_name="internal",
                    key_name=key_name,
                    encrypted_value=encrypted_val,
                    masked_value=masked_val,
                    is_active=True
                )
                session.add(new_key)
                await session.commit()
                
        try:
            asyncio.run(save_internal_key())
            self.refresh_keys_table()
            # Προβολή του παραγόμενου κλειδιού στον χρήστη επειδή δεν θα το ξαναδεί
            messagebox.showinfo(
                "Παραγωγή Κλειδιού", 
                f"Παρήχθη το εσωτερικό κλειδί:\n\n{raw_key}\n\nΑποθηκεύτηκε με ασφάλεια στη βάση δεδομένων."
            )
        except Exception as generate_error:
            messagebox.showerror("Σφάλμα Παραγωγής", f"Αποτυχία αποθήκευσης στη βάση δεδομένων:\n{generate_error}")

    def handle_decrypt_key(self) -> None:
        """
        Ανακτά το επιλεγμένο κλειδί, το αποκρυπτογραφεί και το εμφανίζει με ασφάλεια.
        """
        selected_item = self.keys_tree.selection()
        if not selected_item:
            messagebox.showwarning("Επιλογή Κλειδιού", "Παρακαλώ επιλέξτε ένα κλειδί από τον πίνακα.")
            return
            
        item_values = self.keys_tree.item(selected_item[0], "values")
        key_id_str = item_values[0]
        key_id = uuid.UUID(key_id_str)
        
        async def get_encrypted_value() -> Optional[str]:
            async with AsyncSessionLocal() as session:
                query = select(OSINTApiKey).where(OSINTApiKey.id == key_id)
                query_result = await session.execute(query)
                key_record = query_result.scalars().first()
                if key_record:
                    return key_record.encrypted_value
                return None
                
        try:
            encrypted_val = asyncio.run(get_encrypted_value())
            if encrypted_val:
                decrypted_val = self.vault.decrypt_key(encrypted_val)
                
                # Δημιουργία προσαρμοσμένου διαλόγου για την προβολή του κλειδιού με δυνατότητα αντιγραφής
                self.show_decrypted_dialog(item_values[1], item_values[2], decrypted_val)
            else:
                messagebox.showerror("Σφάλμα", "Το κλειδί δεν βρέθηκε στη βάση δεδομένων.")
        except Exception as decrypt_error:
            messagebox.showerror("Σφάλμα Αποκρυπτογράφησης", f"Αποτυχία αποκρυπτογράφησης:\n{decrypt_error}")

    def show_decrypted_dialog(self, provider: str, name: str, value: str) -> None:
        """
        Εμφανίζει ένα προσαρμοσμένο παράθυρο με την αποκρυπτογραφημένη τιμή του API key.
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Decrypted API Key")
        dialog.geometry("500x200")
        dialog.configure(bg=self.frame_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Κεντράρισμα του διαλόγου πάνω από το κύριο παράθυρο
        dialog.geometry(f"+{self.root.winfo_x() + 300}+{self.root.winfo_y() + 200}")
        
        label_info = tk.Label(
            dialog, 
            text=f"Decrypted Key for {provider} ({name}):", 
            fg=self.accent_color, 
            bg=self.frame_color, 
            font=("Inter", 10, "bold")
        )
        label_info.pack(pady=(20, 5))
        
        # Monospace Text Box για εύκολη αντιγραφή
        text_box = tk.Entry(
            dialog, 
            fg=self.text_color, 
            bg=self.bg_color, 
            insertbackground=self.text_color, 
            relief="solid", 
            bd=1, 
            font=("Geist Mono", 10), 
            justify="center",
            width=50
        )
        text_box.pack(pady=10)
        text_box.insert(0, value)
        text_box.configure(state="readonly")
        text_box.focus_set()
        
        def copy_to_clipboard() -> None:
            self.root.clipboard_clear()
            self.root.clipboard_append(value)
            messagebox.showinfo("Clipboard", "Το API Key αντιγράφηκε στο clipboard.", parent=dialog)
            
        copy_button = tk.Button(
            dialog, 
            text="Copy Key", 
            command=copy_to_clipboard, 
            bg=self.button_color, 
            fg=self.text_color, 
            relief="flat", 
            font=("Inter", 9, "bold")
        )
        copy_button.pack(side="left", padx=(130, 10), pady=10)
        
        close_button = tk.Button(
            dialog, 
            text="Close", 
            command=dialog.destroy, 
            bg=self.border_color, 
            fg=self.text_color, 
            relief="flat", 
            font=("Inter", 9)
        )
        close_button.pack(side="left", padx=10, pady=10)

    def handle_delete_key(self) -> None:
        """
        Διαγράφει το επιλεγμένο κλειδί από τη βάση δεδομένων.
        """
        selected_item = self.keys_tree.selection()
        if not selected_item:
            messagebox.showwarning("Επιλογή Κλειδιού", "Παρακαλώ επιλέξτε ένα κλειδί από τον πίνακα.")
            return
            
        item_values = self.keys_tree.item(selected_item[0], "values")
        key_id_str = item_values[0]
        key_id = uuid.UUID(key_id_str)
        provider = item_values[1]
        name = item_values[2]
        
        confirm = messagebox.askyesno(
            "Διαγραφή Κλειδιού", 
            f"Είστε σίγουροι ότι θέλετε να διαγράψετε το κλειδί:\n'{name}' για την υπηρεσία '{provider}';"
        )
        
        if not confirm:
            return
            
        async def delete_key_record() -> None:
            async with AsyncSessionLocal() as session:
                query = select(OSINTApiKey).where(OSINTApiKey.id == key_id)
                query_result = await session.execute(query)
                key_record = query_result.scalars().first()
                if key_record:
                    await session.delete(key_record)
                    await session.commit()
                    
        try:
            asyncio.run(delete_key_record())
            self.refresh_keys_table()
            messagebox.showinfo("Επιτυχία", "Το API Key διαγράφηκε με ασφάλεια.")
        except Exception as delete_error:
            messagebox.showerror("Σφάλμα Διαγραφής", f"Αποτυχία διαγραφής από τη βάση δεδομένων:\n{delete_error}")


# Εκκίνηση της εφαρμογής
if __name__ == "__main__":
    # Έλεγχος αν υπάρχει ορισμένη μεταβλητή περιβάλλοντος για τη βάση δεδομένων.
    # Αν όχι, χρησιμοποιούμε τη διεύθυνση localhost καθώς τρέχουμε εκτός Docker.
    if "DATABASE_URL" not in os.environ:
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://osint_user:osint_password@localhost:5432/osint_db"
        
    # Δημιουργία του κύριου παραθύρου Tkinter
    main_window = tk.Tk()
    app_instance = OSINTKeyManagerGUI(main_window)
    
    # Εκκίνηση του main loop της εφαρμογής
    main_window.mainloop()
