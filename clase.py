import tkinter as tk
from tkinter import messagebox, ttk
import jaydebeapi

class SQLDeveloperEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("DBMS")
        self.root.geometry("800x800")
        self.root.resizable(False, False)
        self.root.eval('tk::PlaceWindow . center')

        self.conn = None  #
        self.connections = {}

        topFrame = tk.Frame(root)
        topFrame.config(width=800, height=200, bg="red")
        topFrame.pack(side="top", fill="both")

        self.combo = ttk.Combobox(topFrame, values=["Vista", "Índice", "Procedimientos", "Funciones", "Triggers", "Checks", "Tablas", "Esquemas"], state="disabled")
        self.combo.set("Seleccione una opción")
        self.combo.pack(pady=10)



        leftContainerFrame = tk.Frame(root)
        leftContainerFrame.config(width=200, height=400, bg="white")
        leftContainerFrame.pack(side="left", fill="both")

        self.leftUpperFrame = tk.Frame(leftContainerFrame)
        self.leftUpperFrame.config(bg="blue")
        self.leftUpperFrame.pack(side="top", fill="both", expand=True)
        self.leftUpperFrame.config(width=200, height=360)

        leftLowerFrame = tk.Frame(leftContainerFrame)
        leftLowerFrame.config(bg="yellow")
        leftLowerFrame.pack(side="top", fill="both", expand=True)
        leftLowerFrame.config(width=200, height=30)
        self.agregarConexionBtn = tk.Button(leftLowerFrame, text="Agregar conexión", command=lambda: self.show_new_connection_form(middleFrame))
        self.agregarConexionBtn.pack(pady=10)
        self.eliminarConexionBtn = tk.Button(leftLowerFrame, text="Eliminar conexión", command=lambda: self.delete_connection)
        self.eliminarConexionBtn.pack(pady=10)
        self.modificarConexionBtn = tk.Button(leftLowerFrame, text="Modificar conexión", command=lambda: self.show_modify_connection_form(middleFrame))
        self.modificarConexionBtn.pack(pady=10)

        middleFrame = tk.Frame(root)
        middleFrame.config(width=500, height=400, bg="green")
        middleFrame.pack(side="right", fill="both", expand=True)

    def show_new_connection_form(self, middleFrame):
        for widget in middleFrame.winfo_children():
            widget.destroy()

        self.name_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.hostname_var = tk.StringVar()
        self.port_var = tk.StringVar(value="1527")
        self.sid_var = tk.StringVar(value="myNewDB")

        # Widgets para replicar la interfaz de agregar conexión
        tk.Label(middleFrame, text="Name").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(middleFrame, text="Username").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.username_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(middleFrame, text="Password").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.password_var, show="*").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(middleFrame, text="Hostname").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.hostname_var).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(middleFrame, text="Port").grid(row=4, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.port_var).grid(row=4, column=1, padx=5, pady=5)

        tk.Label(middleFrame, text="SID").grid(row=5, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.sid_var).grid(row=5, column=1, padx=5, pady=5)

        tk.Button(middleFrame, text="Test", command=self.test_connection).grid(row=6, column=0, padx=5, pady=5)
        tk.Button(middleFrame, text="Connect", command=self.connect_to_database).grid(row=6, column=1, padx=5, pady=5)

    def test_connection(self):
        try:
            jdbc_driver = '/Users/coleexz/Documents/GitHub/PruebaPython/db-derby-10.17.1.0-bin/lib/derbyclient.jar'
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{self.hostname_var.get()}:{self.port_var.get()}/{self.sid_var.get()};create=true'
            conn = jaydebeapi.connect(driver_class, db_url, [self.username_var.get(), self.password_var.get()], jdbc_driver)
            conn.close()
            messagebox.showinfo("Test de Conexión", "Prueba de conexión realizada exitosamente")
        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))

    def connect_to_database(self):
        try:
            jdbc_driver = '/Users/coleexz/Documents/GitHub/PruebaPython/db-derby-10.17.1.0-bin/lib/derbyclient.jar'
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{self.hostname_var.get()}:{self.port_var.get()}/{self.sid_var.get()};create=true'
            self.conn = jaydebeapi.connect(driver_class, db_url, [self.username_var.get(), self.password_var.get()], jdbc_driver)
            messagebox.showinfo("Conexión exitosa", f"Conexión a {self.sid_var.get()} realizada correctamente")

            connection_info = {
                "name": self.name_var.get(),
                "username": self.username_var.get(),
                "password": self.password_var.get(),
                "hostname": self.hostname_var.get(),
                "port": self.port_var.get(),
                "sid": self.sid_var.get()
            }
            self.connections[self.name_var.get()] = connection_info

            self.combo.config(state="readonly")

            self.add_connection_button(self.name_var.get())

        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))

    def add_connection_button(self, connection_name):
        connection_button = tk.Button(self.leftUpperFrame, text=connection_name, command=lambda: self.select_connection(connection_name))
        connection_button.pack(pady=5, padx=5)

    def select_connection(self, connection_name):
        self.selected_connection = connection_name
        messagebox.showinfo("Conexión seleccionada", f"Conexión {connection_name} seleccionada.")

    def show_modify_connection_form(self, middleFrame):
        if not hasattr(self, 'selected_connection'):
            messagebox.showwarning("Advertencia", "No hay ninguna conexión seleccionada.")
            return

        connection_info = self.connections[self.selected_connection]

        for widget in middleFrame.winfo_children():
            widget.destroy()

        # Llenar el formulario con los datos de la conexión seleccionada
        self.name_var.set(connection_info["name"])
        self.username_var.set(connection_info["username"])
        self.password_var.set(connection_info["password"])
        self.hostname_var.set(connection_info["hostname"])
        self.port_var.set(connection_info["port"])
        self.sid_var.set(connection_info["sid"])

        # Reutilizamos el formulario para modificar la conexión
        tk.Label(middleFrame, text="Name").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(middleFrame, text="Username").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.username_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(middleFrame, text="Password").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.password_var, show="*").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(middleFrame, text="Hostname").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.hostname_var).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(middleFrame, text="Port").grid(row=4, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.port_var).grid(row=4, column=1, padx=5, pady=5)

        tk.Label(middleFrame, text="SID").grid(row=5, column=0, padx=5, pady=5)
        tk.Entry(middleFrame, textvariable=self.sid_var).grid(row=5, column=1, padx=5, pady=5)

        tk.Button(middleFrame, text="Guardar Cambios", command=lambda: self.save_modified_connection(connection_info["name"])).grid(row=6, column=1, padx=5, pady=5)

    def save_modified_connection(self, original_name):
        connection_info = {
            "name": self.name_var.get(),
            "username": self.username_var.get(),
            "password": self.password_var.get(),
            "hostname": self.hostname_var.get(),
            "port": self.port_var.get(),
            "sid": self.sid_var.get()
        }

        del self.connections[original_name]
        self.connections[connection_info["name"]] = connection_info
        messagebox.showinfo("Conexión modificada", f"Conexión {original_name} ha sido modificada.")

    def delete_connection(self):
        if not hasattr(self, 'selected_connection'):
            messagebox.showwarning("Advertencia", "No hay ninguna conexión seleccionada.")
            return

        del self.connections[self.selected_connection]
        messagebox.showinfo("Conexión eliminada", f"Conexión {self.selected_connection} ha sido eliminada.")

    def close_connection(self):
        if self.conn:
            self.conn.close()
            messagebox.showinfo("Conexión cerrada", "Conexión a la base de datos cerrada correctamente.")

root = tk.Tk()
app = SQLDeveloperEmulator(root)
root.protocol("WM_DELETE_WINDOW", lambda: (app.close_connection(), root.destroy()))
root.mainloop()
