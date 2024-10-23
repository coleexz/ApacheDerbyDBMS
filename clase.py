import tkinter as tk
from tkinter import messagebox, ttk
import jaydebeapi
import pickle
import atexit

class SQLDeveloperEmulator:
    def __init__(self, root):
        self.root = root
        self.root.title("デー タベース管理シ")
        self.root.geometry("1024x600")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#2e2e2e", foreground="white", borderwidth=0)
        style.configure("TNotebook.Tab", background="#3e3e3e", foreground="white")
        style.map("TNotebook.Tab", background=[("selected", "#1c1c1c")])

        self.conn = None
        self.connections = {}
        self.selected_connection = None
        self.selected_schema = None

        frame_izquierdo = tk.Frame(root, width=150, bg="#2e2e2e", bd=2, relief=tk.SUNKEN)
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(frame_izquierdo, text="Conexiones", bg="#2e2e2e", fg="white").pack(pady=5)

        self.connection_listbox = tk.Listbox(frame_izquierdo, bg="#1e1e1e", fg="white", selectbackground="#3e3e3e")
        self.connection_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.connection_listbox.bind('<<ListboxSelect>>', self.select_connection)

        self.agregarConexionBtn = tk.Button(frame_izquierdo, text="Crear", bg="#3e3e3e", fg="black", command=self.show_new_connection_form)
        self.agregarConexionBtn.pack(pady=2)

        self.modificarConexionBtn = tk.Button(frame_izquierdo, text="Modificar", bg="#3e3e3e", fg="black", command=self.show_modify_connection_form, state="disabled")
        self.modificarConexionBtn.pack(pady=2)

        self.eliminarConexionBtn = tk.Button(frame_izquierdo, text="Eliminar", bg="#3e3e3e", fg="black", command=self.delete_connection, state="disabled")
        self.eliminarConexionBtn.pack(pady=2)

        self.conectarBtn = tk.Button(frame_izquierdo, text="Conectar", bg="#3e3e3e", fg="black", command=self.connect_to_selected_connection, state="disabled")
        self.conectarBtn.pack(pady=2)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Crear las tabs
        titulos = ["Tablas", "Indices", "Procedimientos Almacenados", "Funciones Almacenadas","Triggers", "Vistas", "Checks", "Esquemas"]
        for titulo in titulos:
            self.crear_tab(titulo)

        tk.Label(root, text="QUERY", bg="#1e1e1e", fg="white").pack(anchor=tk.W, padx=5)
        self.query_text = tk.Text(root, height=2, bg="#2e2e2e", fg="white", insertbackground="white")
        self.query_text.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(root, text="RESULTADO", bg="#1e1e1e", fg="white").pack(anchor=tk.W, padx=5)
        self.resultado_text = tk.Text(root, height=8, bg="#1e1e1e", fg="white", insertbackground="white")
        self.resultado_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)
        atexit.register(self.insert_connections_to_file)
        self.load_connections_from_file()


    def get_schemas(self, connection_info):
        try:
            jdbc_driver = '/Users/coleexz/Documents/GitHub/ApacheDerbyDBMS/db-derby-10.17.1.0-bin/lib/derbyclient.jar'
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{connection_info["hostname"]}:{connection_info["port"]}/{connection_info["sid"]};create=true'
            conn = jaydebeapi.connect(driver_class, db_url, [connection_info["username"], connection_info["password"]], jdbc_driver)
            cursor = conn.cursor()
            cursor.execute("SELECT SCHEMANAME FROM SYS.SYSSCHEMAS")
            schemas = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return schemas
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener los esquemas: {str(e)}")
            return []

    def select_connection(self, event):
        try:
            widget = event.widget
            selection = widget.curselection()
            if selection:
                self.selected_connection = widget.get(selection[0])
                connection_info = self.connections.get(self.selected_connection, {})
                schemas = self.get_schemas(connection_info)
                if hasattr(self, 'schema_combobox'):
                    self.schema_combobox['values'] = schemas
                    if schemas:
                        self.schema_combobox.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

    def populate_schemas(self):
        if not self.selected_connection:
            return
        connection_info = self.connections[self.selected_connection]
        try:
            jdbc_driver = '/Users/coleexz/Documents/GitHub/ApacheDerbyDBMS/db-derby-10.17.1.0-bin/lib/derbyclient.jar'
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{connection_info["hostname"]}:{connection_info["port"]}/{connection_info["sid"]};create=true'
            conn = jaydebeapi.connect(driver_class, db_url, [connection_info["username"], connection_info["password"]], jdbc_driver)
            cursor = conn.cursor()
            cursor.execute("SELECT SCHEMANAME FROM SYS.SYSSCHEMAS")
            schemas = [row[0] for row in cursor.fetchall()]
            self.schema_combobox['values'] = schemas
            if connection_info.get('schema') in schemas:
                self.schema_combobox.set(connection_info.get('schema'))
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener esquemas: {str(e)}")

    def populate_schemas_combobox(self, combobox):
        if not self.selected_connection:
            return
        connection_info = self.connections[self.selected_connection]
        try:
            jdbc_driver = '/Users/coleexz/Documents/GitHub/ApacheDerbyDBMS/db-derby-10.17.1.0-bin/lib/derbyclient.jar'
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{connection_info["hostname"]}:{connection_info["port"]}/{connection_info["sid"]};create=true'
            conn = jaydebeapi.connect(driver_class, db_url, [connection_info["username"], connection_info["password"]], jdbc_driver)
            cursor = conn.cursor()
            cursor.execute("SELECT SCHEMANAME FROM SYS.SYSSCHEMAS")
            schemas = [row[0] for row in cursor.fetchall()]
            combobox['values'] = schemas
            if connection_info.get('schema') in schemas:
                combobox.set(connection_info.get('schema'))
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener esquemas: {str(e)}")

    def crear_tab(self, titulo):
        tab = ttk.Frame(self.notebook, style="TNotebook.Tab")
        self.notebook.add(tab, text=titulo)

        sub_notebook = ttk.Notebook(tab)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        operations = ["Listar", "Crear", "Modificar", "Borrar"]
        for operation in operations:
            sub_tab = ttk.Frame(sub_notebook)
            sub_notebook.add(sub_tab, text=operation)

            if operation == "Listar":
                btn_listar = tk.Button(sub_tab, text="Ejecutar", bg="#3e3e3e", fg="black", command=lambda t=titulo: self.list_items(t))
                btn_listar.pack(pady=5)
            elif titulo == "Indices":
                if operation == "Crear":
                    self.create_index_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_index_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_index_form(sub_tab)
            elif titulo == "Procedimientos Almacenados":
                if operation == "Crear":
                    self.create_stored_procedure_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_stored_procedure_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_stored_procedure_form(sub_tab)
            elif titulo == "Funciones Almacenadas":
                if operation == "Crear":
                    self.create_stored_function_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_stored_function_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_stored_function_form(sub_tab)
            elif titulo == "Triggers":
                if operation == "Crear":
                    pass
                elif operation == "Modificar":
                    pass
                elif operation == "Borrar":
                    pass
            elif titulo == "Vistas":
                if operation == "Crear":
                    pass
                elif operation == "Modificar":
                    pass
                elif operation == "Borrar":
                    pass
            elif titulo == "Checks":
                if operation == "Crear":
                    pass
                elif operation == "Modificar":
                    pass
                elif operation == "Borrar":
                    pass
            elif titulo == "Esquemas":
                if operation == "Crear":
                    pass
                elif operation == "Modificar":
                    pass
                elif operation == "Borrar":
                    pass

    def create_stored_procedure_form(self, parent):
        tk.Label(parent, text="Crear Procedimiento Almacenado", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Procedimiento", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        procedure_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=procedure_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Código del Procedimiento", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        procedure_code_text = tk.Text(parent, height=10, bg="#2e2e2e", fg="white")
        procedure_code_text.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(parent, text="Crear Procedimiento", bg="#3e3e3e", fg="black", command=lambda: self.create_stored_procedure(procedure_name_var.get(), procedure_code_text.get("1.0", tk.END))).grid(row=3, column=0, columnspan=2, pady=10)

    def modify_stored_procedure_form(self, parent):
        tk.Label(parent, text="Modificar Procedimiento Almacenado", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Procedimiento", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        procedure_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=procedure_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Nuevo Código del Procedimiento", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        procedure_code_text = tk.Text(parent, height=10, bg="#2e2e2e", fg="white")
        procedure_code_text.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(parent, text="Modificar Procedimiento", bg="#3e3e3e", fg="black", command=lambda: self.modify_stored_procedure(procedure_name_var.get(), procedure_code_text.get("1.0", tk.END))).grid(row=3, column=0, columnspan=2, pady=10)

    def delete_stored_procedure_form(self, parent):
        tk.Label(parent, text="Borrar Procedimiento Almacenado", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Procedimiento", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        procedure_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=procedure_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Borrar Procedimiento", bg="#3e3e3e", fg="black", command=lambda: self.delete_stored_procedure(procedure_name_var.get())).grid(row=2, column=0, columnspan=2, pady=10)

    def create_stored_function_form(self, parent):
        tk.Label(parent, text="Crear Función Almacenada", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre de la Función", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        function_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=function_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Código de la Función", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        function_code_text = tk.Text(parent, height=10, bg="#2e2e2e", fg="white")
        function_code_text.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(parent, text="Crear Función", bg="#3e3e3e", fg="black", command=lambda: self.create_stored_function(function_name_var.get(), function_code_text.get("1.0", tk.END))).grid(row=3, column=0, columnspan=2, pady=10)

    def modify_stored_function_form(self, parent):
        tk.Label(parent, text="Modificar Función Almacenada", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre de la Función", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        function_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=function_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Nuevo Código de la Función", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        function_code_text = tk.Text(parent, height=10, bg="#2e2e2e", fg="white")
        function_code_text.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(parent, text="Modificar Función", bg="#3e3e3e", fg="black", command=lambda: self.modify_stored_function(function_name_var.get(), function_code_text.get("1.0", tk.END))).grid(row=3, column=0, columnspan=2, pady=10)

    def delete_stored_function_form(self, parent):
        tk.Label(parent, text="Borrar Función Almacenada", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre de la Función", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        function_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=function_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Borrar Función", bg="#3e3e3e", fg="black", command=lambda: self.delete_stored_function(function_name_var.get())).grid(row=2, column=0, columnspan=2, pady=10)

    def create_stored_procedure(self, name, code):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            query = f"CREATE PROCEDURE {name} AS {code}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Procedimiento {name} creado exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al crear el procedimiento: {str(e)}")

    def modify_stored_procedure(self, name, new_code):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            drop_query = f"DROP PROCEDURE {name}"
            create_query = f"CREATE PROCEDURE {name} AS {new_code}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, f"{drop_query};\n{create_query}")
            cursor.execute(drop_query)
            cursor.execute(create_query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Procedimiento {name} modificado exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al modificar el procedimiento: {str(e)}")

    def delete_stored_procedure(self, name):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            query = f"DROP PROCEDURE {name}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Procedimiento {name} borrado exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al borrar el procedimiento: {str(e)}")

    def create_stored_function(self, name, code):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            query = f"CREATE FUNCTION {name} RETURNS INTEGER AS {code}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Función {name} creada exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al crear la función: {str(e)}")

    def modify_stored_function(self, name, new_code):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            drop_query = f"DROP FUNCTION {name}"
            create_query = f"CREATE FUNCTION {name} RETURNS INTEGER AS {new_code}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, f"{drop_query};\n{create_query}")
            cursor.execute(drop_query)
            cursor.execute(create_query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Función {name} modificada exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al modificar la función: {str(e)}")

    def delete_stored_function(self, name):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            query = f"DROP FUNCTION {name}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Función {name} borrada exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al borrar la función: {str(e)}")

    def list_items(self, option):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        self.query_text.delete(1.0, tk.END)
        textbox = self.resultado_text
        textbox.delete(1.0, tk.END)

        try:
            cursor = self.conn.cursor()
            query = ""

            if option.lower() == "tablas":
                query = "SELECT TABLENAME FROM SYS.SYSTABLES WHERE TABLETYPE='T'"
            elif option.lower() == "vistas":
                query = "SELECT TABLENAME FROM SYS.SYSTABLES WHERE TABLETYPE='V'"
            elif option.lower() == "indices":
                query = """
                    SELECT S.SCHEMANAME, T.TABLENAME, C.CONSTRAINTNAME, C.TYPE
                    FROM SYS.SYSCONSTRAINTS C
                    JOIN SYS.SYSTABLES T ON C.TABLEID = T.TABLEID
                    JOIN SYS.SYSSCHEMAS S ON T.SCHEMAID = S.SCHEMAID
                    WHERE C.TYPE IN ('P', 'F')
                """
            elif option.lower() == "procedimientos almacenados":
                query = "SELECT ALIAS FROM SYS.SYSALIASES WHERE ALIASTYPE='P'"
            elif option.lower() == "funciones almacenadas":
                query = "SELECT ALIAS, ALIASTYPE FROM SYS.SYSALIASES WHERE ALIASTYPE ='F'"
            elif option.lower() == "triggers":
                query = """
                    SELECT TRIGGERNAME, EVENT, TABLENAME
                    FROM SYS.SYSTRIGGERS
                    JOIN SYS.SYSTABLES ON SYS.SYSTRIGGERS.TABLEID = SYS.SYSTABLES.TABLEID
                """
            elif option.lower() == "checks":
                query = """
                    SELECT C.CONSTRAINTNAME, T.TABLENAME
                    FROM SYS.SYSCONSTRAINTS C
                    JOIN SYS.SYSTABLES T ON C.TABLEID = T.TABLEID
                    WHERE C.TYPE = 'C'
                """
            elif option.lower() == "esquemas":
                query = "SELECT SCHEMANAME FROM SYS.SYSSCHEMAS"

            if query:
                self.query_text.insert(tk.END, query)
                cursor.execute(query)
                items = cursor.fetchall()
                if items:
                    for item in items:
                        textbox.insert(tk.END, f"{item[0]}\n")
                else:
                    textbox.insert(tk.END, f"No se encontraron {option.lower()}.")

            cursor.close()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al listar los {option.lower()}s: {str(e)}")

    def insert_connections_to_file(self):
        try:
            with open('connections.pkl', 'wb') as file:
                pickle.dump(self.connections, file)
            messagebox.showinfo("Guardar Conexiones", "Conexiones guardadas correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al guardar las conexiones: {str(e)}")

    def load_connections_from_file(self):
        try:
            with open('connections.pkl', 'rb') as file:
                self.connections = pickle.load(file)
            self.update_connections()
            messagebox.showinfo("Cargar Conexiones", "Conexiones cargadas correctamente.")
        except FileNotFoundError:
            messagebox.showwarning("Advertencia", "No se encontró el archivo de conexiones.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar las conexiones: {str(e)}")

    def show_new_connection_form(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Nueva Conexión")
        new_window.geometry("400x350")
        new_window.configure(bg="#1e1e1e")

        name_var = tk.StringVar()
        username_var = tk.StringVar()
        password_var = tk.StringVar()
        hostname_var = tk.StringVar()
        port_var = tk.StringVar(value="1527")
        sid_var = tk.StringVar(value="myNewDB")
        schema_var = tk.StringVar()

        tk.Label(new_window, text="Nombre", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=name_var, bg="#2e2e2e", fg="white").grid(row=0, column=1, padx=5, pady=5)

        tk.Label(new_window, text="Usuario", bg="#1e1e1e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=username_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(new_window, text="Contraseña", bg="#1e1e1e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=password_var, show="*", bg="#2e2e2e", fg="white").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(new_window, text="Hostname", bg="#1e1e1e", fg="white").grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=hostname_var, bg="#2e2e2e", fg="white").grid(row=3, column=1, padx=5, pady=5)

        tk.Label(new_window, text="Puerto", bg="#1e1e1e", fg="white").grid(row=4, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=port_var, bg="#2e2e2e", fg="white").grid(row=4, column=1, padx=5, pady=5)

        tk.Label(new_window, text="SID", bg="#1e1e1e", fg="white").grid(row=5, column=0, padx=5, pady=5)
        tk.Entry(new_window, textvariable=sid_var, bg="#2e2e2e", fg="white").grid(row=5, column=1, padx=5, pady=5)

        tk.Label(new_window, text="Schema", bg="#1e1e1e", fg="white").grid(row=6, column=0, padx=5, pady=5)
        schema_combobox = ttk.Combobox(new_window, textvariable=schema_var, state="readonly")
        schema_combobox.grid(row=6, column=1, padx=5, pady=5)
        self.populate_schemas_combobox(schema_combobox)

        def save_connection():
            connection_info = {
                "name": name_var.get(),
                "username": username_var.get(),
                "password": password_var.get(),
                "hostname": hostname_var.get(),
                "port": port_var.get(),
                "sid": sid_var.get(),
                "schema": schema_var.get()
            }
            self.connections[name_var.get()] = connection_info
            self.update_connections()
            new_window.destroy()

        tk.Button(new_window, text="Guardar Conexión", bg="#3e3e3e", fg="black", command=save_connection).grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(new_window, text="Cancelar", bg="#3e3e3e", fg="black", command=new_window.destroy).grid(row=8, column=0, columnspan=2, pady=5)

    def test_connection(self, hostname, port, sid, username, password):
        try:
            jdbc_driver = '/Users/coleexz/Documents/GitHub/ApacheDerbyDBMS/db-derby-10.17.1.0-bin/lib/derbyclient.jar'
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{hostname}:{port}/{sid};create=true'
            conn = jaydebeapi.connect(driver_class, db_url, [username, password], jdbc_driver)
            conn.close()
            messagebox.showinfo("Test de Conexión", "Prueba de conexión realizada exitosamente")
        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))

    def save_connection(self, name, hostname, port, sid, username, password, schema):
        connection_info = {
            "name": name,
            "username": username,
            "password": password,
            "hostname": hostname,
            "port": port,
            "sid": sid,
            "schema": schema
        }
        self.connections[name] = connection_info
        self.update_connections()
        messagebox.showinfo("Conexión guardada", f"Conexión {name} guardada correctamente.")

    def update_connections(self):
        self.connection_listbox.delete(0, tk.END)
        for connection_name in self.connections:
            self.connection_listbox.insert(tk.END, connection_name)
        if self.connections:
            self.modificarConexionBtn.config(state="normal")
            self.eliminarConexionBtn.config(state="normal")
            self.conectarBtn.config(state="normal")
        else:
            self.modificarConexionBtn.config(state="disabled")
            self.eliminarConexionBtn.config(state="disabled")
            self.conectarBtn.config(state="disabled")

    def delete_connection(self):
        if not self.selected_connection:
            messagebox.showwarning("Advertencia", "No hay ninguna conexión seleccionada.")
            return
        del self.connections[self.selected_connection]
        self.update_connections()
        messagebox.showinfo("Conexión eliminada", f"Conexión {self.selected_connection} ha sido eliminada.")
        self.selected_connection = None

    def connect_to_selected_connection(self):
        if self.selected_connection:
            connection_info = self.connections.get(self.selected_connection, {})
            self.connect_to_database(connection_info)

    def connect_to_database(self, connection_info):
        try:
            jdbc_driver = '/Users/coleexz/Documents/GitHub/ApacheDerbyDBMS/db-derby-10.17.1.0-bin/lib/derbyclient.jar'
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{connection_info.get("hostname")}:{connection_info.get("port")}/{connection_info.get("sid")};create=true'
            self.conn = jaydebeapi.connect(driver_class, db_url, [connection_info.get("username"), connection_info.get("password")], jdbc_driver)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Conexión con {self.selected_connection} realizada exitosamente.")
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al conectar con {self.selected_connection}: {str(e)}")

    def show_modify_connection_form(self):
        if not self.selected_connection:
            messagebox.showwarning("Advertencia", "No hay ninguna conexión seleccionada.")
            return

        connection_info = self.connections[self.selected_connection]

        modify_window = tk.Toplevel(self.root)
        modify_window.title("Modificar Conexión")
        modify_window.geometry("400x350")
        modify_window.configure(bg="#2e2e2e")

        tk.Label(modify_window, text="Nombre", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)
        name_var = tk.StringVar(value=self.selected_connection)
        tk.Entry(modify_window, textvariable=name_var, bg="#1e1e1e", fg="white").grid(row=0, column=1, padx=5, pady=5)

        tk.Label(modify_window, text="Hostname", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        hostname_var = tk.StringVar(value=connection_info['hostname'])
        tk.Entry(modify_window, textvariable=hostname_var, bg="#1e1e1e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(modify_window, text="Port", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        port_var = tk.StringVar(value=connection_info['port'])
        tk.Entry(modify_window, textvariable=port_var, bg="#1e1e1e", fg="white").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(modify_window, text="SID", bg="#2e2e2e", fg="white").grid(row=3, column=0, padx=5, pady=5)
        sid_var = tk.StringVar(value=connection_info['sid'])
        tk.Entry(modify_window, textvariable=sid_var, bg="#1e1e1e", fg="white").grid(row=3, column=1, padx=5, pady=5)

        tk.Label(modify_window, text="Username", bg="#2e2e2e", fg="white").grid(row=4, column=0, padx=5, pady=5)
        username_var = tk.StringVar(value=connection_info['username'])
        tk.Entry(modify_window, textvariable=username_var, bg="#1e1e1e", fg="white").grid(row=4, column=1, padx=5, pady=5)

        tk.Label(modify_window, text="Password", bg="#2e2e2e", fg="white").grid(row=5, column=0, padx=5, pady=5)
        password_var = tk.StringVar(value=connection_info['password'])
        tk.Entry(modify_window, textvariable=password_var, show="*", bg="#1e1e1e", fg="white").grid(row=5, column=1, padx=5, pady=5)

        tk.Label(modify_window, text="Schema", bg="#2e2e2e", fg="white").grid(row=6, column=0, padx=5, pady=5)
        schema_var = tk.StringVar(value=connection_info.get('schema', ''))
        schema_combobox = ttk.Combobox(modify_window, textvariable=schema_var, state="readonly")
        schema_combobox.grid(row=6, column=1, padx=5, pady=5)
        self.populate_schemas_combobox(schema_combobox)

        def save_changes():
            new_name = name_var.get()
            self.connections.pop(self.selected_connection)
            self.connections[new_name] = {
                'hostname': hostname_var.get(),
                'port': port_var.get(),
                'sid': sid_var.get(),
                'username': username_var.get(),
                'password': password_var.get(),
                'schema': schema_var.get()
            }
            self.update_connections()
            modify_window.destroy()

        tk.Button(modify_window, text="Guardar", bg="#3e3e3e", fg="black", command=save_changes).grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(modify_window, text="Cancelar", bg="#3e3e3e", fg="black", command=modify_window.destroy).grid(row=8, column=0, columnspan=2, pady=5)

    def delete_connection(self):
        if not self.selected_connection:
            messagebox.showwarning("Advertencia", "No hay ninguna conexión seleccionada.")
            return
        del self.connections[self.selected_connection]
        self.update_connections()
        messagebox.showinfo("Conexión eliminada", f"Conexión {self.selected_connection} ha sido eliminada.")
        self.selected_connection = None

    def create_index_form(self, parent):
        tk.Label(parent, text="Crear Índice", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Índice", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        index_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=index_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Tabla", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        table_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=table_name_var, bg="#2e2e2e", fg="white").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(parent, text="Columnas (separadas por comas)", bg="#2e2e2e", fg="white").grid(row=3, column=0, padx=5, pady=5)
        columns_var = tk.StringVar()
        tk.Entry(parent, textvariable=columns_var, bg="#2e2e2e", fg="white").grid(row=3, column=1, padx=5, pady=5)

        tk.Label(parent, text="Tipo de Índice", bg="#2e2e2e", fg="white").grid(row=4, column=0, padx=5, pady=5)
        index_type_var = tk.StringVar(value="No único")
        ttk.Combobox(parent, textvariable=index_type_var, values=["No único", "Único"], state="readonly").grid(row=4, column=1, padx=5, pady=5)

        tk.Button(parent, text="Crear Índice", bg="#3e3e3e", fg="black", command=lambda: self.create_index(index_name_var.get(), table_name_var.get(), columns_var.get(), index_type_var.get())).grid(row=5, column=0, columnspan=2, pady=10)

    def modify_index_form(self, parent):
        tk.Label(parent, text="Modificar Índice", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Índice", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        index_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=index_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(parent, text="Nueva Tabla", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=5, pady=5)
        new_table_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=new_table_name_var, bg="#2e2e2e", fg="white").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(parent, text="Nuevas Columnas (separadas por comas)", bg="#2e2e2e", fg="white").grid(row=3, column=0, padx=5, pady=5)
        new_columns_var = tk.StringVar()
        tk.Entry(parent, textvariable=new_columns_var, bg="#2e2e2e", fg="white").grid(row=3, column=1, padx=5, pady=5)

        tk.Button(parent, text="Modificar Índice", bg="#3e3e3e", fg="black", command=lambda: self.modify_index(index_name_var.get(), new_table_name_var.get(), new_columns_var.get())).grid(row=4, column=0, columnspan=2, pady=10)

    def delete_index_form(self, parent):
        tk.Label(parent, text="Borrar Índice", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Índice", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        index_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=index_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Borrar Índice", bg="#3e3e3e", fg="black", command=lambda: self.delete_index(index_name_var.get())).grid(row=2, column=0, columnspan=2, pady=10)

    def create_index(self, index_name, table_name, columns, index_type):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            unique = "UNIQUE" if index_type == "Único" else ""
            query = f"CREATE {unique} INDEX {index_name} ON {table_name} ({columns})"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Índice {index_name} creado exitosamente en la tabla {table_name}.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al crear el índice: {str(e)}")

    def modify_index(self, index_name, new_table_name, new_columns):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            # No existe un comando directo para modificar un índice en Derby, se debe eliminar y crear uno nuevo
            drop_query = f"DROP INDEX {index_name}"
            create_query = f"CREATE INDEX {index_name} ON {new_table_name} ({new_columns})"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, f"{drop_query};\n{create_query}")
            cursor.execute(drop_query)
            cursor.execute(create_query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Índice {index_name} modificado exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al modificar el índice: {str(e)}")

    def delete_index(self, index_name):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()
            query = f"DROP INDEX {index_name}"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Índice {index_name} borrado exitosamente.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al borrar el índice: {str(e)}")


root = tk.Tk()
app = SQLDeveloperEmulator(root)
root.mainloop()
