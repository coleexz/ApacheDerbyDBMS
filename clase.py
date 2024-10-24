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

        titulos = ["Tablas", "Indices", "Procedimientos Almacenados", "Funciones Almacenadas","Triggers", "Vistas", "Checks", "Esquemas", "Query"]
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

    def crear_tab(self, titulo):
        tab = ttk.Frame(self.notebook, style="TNotebook.Tab")
        self.notebook.add(tab, text=titulo)

        sub_notebook = ttk.Notebook(tab)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        if titulo == "Query":
            operations = ["Console"]
        else:
            operations = ["Listar", "Crear", "Modificar", "Borrar"]

        for operation in operations:
            sub_tab = ttk.Frame(sub_notebook)
            sub_notebook.add(sub_tab, text=operation)

            if operation == "Listar":
                btn_listar = tk.Button(sub_tab, text="Ejecutar", bg="#3e3e3e", fg="black", command=lambda t=titulo: self.list_items(t))
                btn_listar.pack(pady=5)
            elif titulo == "Tablas":
                if operation == "Crear":
                    self.create_table_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_table_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_table_form(sub_tab)
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
                    self.show_modify_stored_function_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_stored_function_form(sub_tab)
            elif titulo == "Triggers":
                if operation == "Crear":
                    self.create_trigger_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_trigger_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_trigger_form(sub_tab)
            elif titulo == "Vistas":
                if operation == "Crear":
                    self.create_view_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_view_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_view_form(sub_tab)
            elif titulo == "Checks":
                if operation == "Crear":
                    self.create_check_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_check_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_check_form(sub_tab)
            elif titulo == "Esquemas":
                if operation == "Crear":
                    self.create_schema_form(sub_tab)
                elif operation == "Modificar":
                    self.modify_schema_form(sub_tab)
                elif operation == "Borrar":
                    self.delete_schema_form(sub_tab)
            elif titulo == "Query":
                self.create_query_form(sub_tab)

#=======================================================================================================================
#CREATE FORMS

    def create_query_form(self, parent):
        tk.Label(parent, text="Escribe tu Query:", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        query_input = tk.Text(parent, height=5, bg="#2e2e2e", fg="white", insertbackground="white")
        query_input.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="we")

        def execute_query():
            print("Ejecutando query...")
            query = query_input.get("1.0", tk.END).strip()
            if not query:
                messagebox.showerror("Error", "Debe ingresar una consulta.")
                return

            try:
                if not self.conn:
                    messagebox.showerror("Error", "Debe seleccionar una conexión para ejecutar el query.")
                    return

                cursor = self.conn.cursor()

                cursor.execute(query)

                if query.lower().startswith("select"):
                    results = cursor.fetchall()
                    result_text = ""

                    for row in results:
                        result_text += f"{row}\n"

                    self.resultado_text.delete(1.0, tk.END)
                    self.resultado_text.insert(tk.END, result_text or "Consulta ejecutada con éxito.")
                else:
                    self.conn.commit()
                    self.resultado_text.delete(1.0, tk.END)
                    self.resultado_text.insert(tk.END, "Consulta ejecutada con éxito.")

                cursor.close()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al ejecutar el query: {str(e)}")

        tk.Button(parent, text="Ejecutar", command=execute_query, bg="#3e3e3e", fg="black").grid(row=2, column=0, padx=5, pady=10, sticky="e")


    def create_table_form(self, parent):
        tk.Label(parent, text="Nombre de la Tabla:", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        table_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=table_name_var, bg="#2e2e2e", fg="white").grid(row=0, column=1, padx=5, pady=5, sticky="w")

        column_frame = tk.Frame(parent, bg="#2e2e2e")
        column_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        columns_tree = ttk.Treeview(column_frame, columns=("name", "data_type", "size", "not_null"), show="headings", height=6)
        columns_tree.grid(row=1, column=0, columnspan=5, pady=5)
        columns_tree.heading("name", text="Nombre")
        columns_tree.heading("data_type", text="Tipo de Dato")
        columns_tree.heading("size", text="Tamaño")
        columns_tree.heading("not_null", text="Not Null")

        def add_column():
            if not name_var.get() or not data_type_var.get() or not size_var.get():
                messagebox.showerror("Error", "Debe ingresar el nombre, tipo de dato y tamaño de la columna.")
                return
            columns_tree.insert("", "end", values=(name_var.get(), data_type_var.get(), size_var.get(), "NOT NULL" if not_null_var.get() else ""))

        def delete_column():
            selected_item = columns_tree.selection()
            if selected_item:
                columns_tree.delete(selected_item)

        name_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=name_var, width=15, bg="white", fg="black").grid(row=2, column=0, padx=5, pady=5)

        data_type_var = tk.StringVar()
        data_type_combobox = ttk.Combobox(column_frame, textvariable=data_type_var, values=["VARCHAR", "INT", "FLOAT"], state="readonly")
        data_type_combobox.grid(row=2, column=1, padx=5, pady=5)

        size_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=size_var, width=5, bg="white", fg="black").grid(row=2, column=2, padx=5, pady=5)

        not_null_var = tk.BooleanVar()
        tk.Checkbutton(column_frame, text="Not Null", variable=not_null_var, bg="#2e2e2e", fg="white").grid(row=2, column=3, padx=5, pady=5)

        tk.Button(column_frame, text="Agregar Columna", command=add_column, bg="#3e3e3e", fg="black").grid(row=2, column=4, padx=5, pady=5)
        tk.Button(column_frame, text="Eliminar Columna", command=delete_column, bg="#3e3e3e", fg="black").grid(row=3, column=4, padx=5, pady=5)

        def create_table():
            if not self.conn:
                messagebox.showerror("Error", "Debe seleccionar una conexión para ejecutar el DDL.")
                return

            cursor = self.conn.cursor()

            try:
                table_name = table_name_var.get()
                columns = [columns_tree.item(item, "values") for item in columns_tree.get_children()]

                ddl = f"CREATE TABLE {table_name} (\n"
                column_definitions = []
                for col in columns:
                    if col[1] == "INT" or col[1] == "FLOAT":
                        column_def = f"  {col[0]} {col[1]}"
                    else:
                        column_def = f"  {col[0]} {col[1]}({col[2]})"
                    if col[3]:
                        column_def += " NOT NULL"
                    column_definitions.append(column_def)
                ddl += ",\n".join(column_definitions) + "\n)"

                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, ddl)

                cursor.execute(ddl)
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Tabla '{table_name}' creada exitosamente.")

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al crear la tabla: {str(e)}")

            finally:
                cursor.close()


        tk.Button(parent, text="OK", command=create_table, bg="#3e3e3e", fg="black").grid(row=4, column=0, padx=5, pady=10, sticky="e")
        tk.Button(parent, text="Cancelar", command=parent.quit, bg="#3e3e3e", fg="black").grid(row=4, column=1, padx=5, pady=10, sticky="w")


    def create_trigger_form(self, parent):
        tk.Label(parent, text="Crear Trigger", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

    def create_check_form(self, parent):
        tk.Label(parent, text="Crear Check", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

    def create_view_form(self, parent):
        tk.Label(parent, text="Crear Vista", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

    def create_schema_form(self, parent):
        tk.Label(parent, text="Crear Esquema", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

#=======================================================================================================================
#MODIFY-FORMS
    def modify_table_form(self, parent):

        tk.Label(parent, text="Seleccione la Tabla:", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        table_name_var = tk.StringVar()
        table_name_combobox = ttk.Combobox(parent, textvariable=table_name_var, state="readonly")
        table_name_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Button(parent, text="Cargar Tablas", command=lambda: self.load_tables(table_name_combobox), bg="#3e3e3e", fg="black").grid(row=0, column=2, padx=5, pady=5)

        ddl_frame = tk.Frame(parent, bg="#2e2e2e")
        ddl_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        ddl_text = tk.Text(ddl_frame, height=10, bg="#1e1e1e", fg="white", insertbackground="white")
        ddl_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        def load_table_ddl():
            table_name = table_name_var.get()
            if not table_name:
                messagebox.showerror("Error", "Debe seleccionar una tabla para obtener su DDL.")
                return

            try:
                cursor = self.conn.cursor()

                cursor.execute(f"SELECT * FROM SYS.SYSCOLUMNS WHERE REFERENCEID IN (SELECT TABLEID FROM SYS.SYSTABLES WHERE TABLENAME = '{table_name}')")
                columns = cursor.fetchall()

                ddl = f"CREATE TABLE {table_name} (\n"
                column_definitions = []
                for col in columns:
                    column_def = f"  {col[0]} {col[1]}"
                    if col[2] == "NO":
                        column_def += " NOT NULL"
                    column_definitions.append(column_def)
                ddl += ",\n".join(column_definitions) + "\n);"

                ddl_text.delete(1.0, tk.END)
                ddl_text.insert(tk.END, ddl)

                cursor.close()

            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error al obtener el DDL de la tabla: {str(e)}")

        tk.Button(parent, text="Cargar DDL", command=load_table_ddl, bg="#3e3e3e", fg="black").grid(row=2, column=2, padx=5, pady=5)

        def execute_ddl():
            try:
                cursor = self.conn.cursor()

                ddl = ddl_text.get(1.0, tk.END).strip()

                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, ddl)

                cursor.execute(ddl)
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, "DDL ejecutado exitosamente.")

                cursor.close()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al ejecutar el DDL: {str(e)}")

        tk.Button(parent, text="Ejecutar DDL", command=execute_ddl, bg="#3e3e3e", fg="black").grid(row=4, column=0, padx=5, pady=10, sticky="e")
        tk.Button(parent, text="Cancelar", command=parent.quit, bg="#3e3e3e", fg="black").grid(row=4, column=1, padx=5, pady=10, sticky="w")

    def load_tables(self, table_combobox):
        """Carga las tablas disponibles en la base de datos en el combobox."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT TABLENAME FROM SYS.SYSTABLES WHERE TABLETYPE='T'")
            tables = cursor.fetchall()

            table_combobox['values'] = [table[0] for table in tables]
            if tables:
                table_combobox.current(0)

            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar las tablas: {str(e)}")


    def modify_trigger_form(self, parent):
        tk.Label(parent, text="Modificar Trigger", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

    def modify_check_form(self, parent):
        tk.Label(parent, text="Modificar Check", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

    def modify_view_form(self, parent):
        tk.Label(parent, text="Modificar Vista", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

    def modify_schema_form(self, parent):
        tk.Label(parent, text="Modificar Esquema", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

#=======================================================================================================================
#DELETE-FORMS
    def delete_table_form(self, parent):
        tk.Label(parent, text="Eliminar Tabla", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        table_frame = tk.Frame(parent, bg="#2e2e2e")
        table_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        tk.Label(parent, text="Seleccione una tabla:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)

        selected_table_var = tk.StringVar()
        self.table_combobox = ttk.Combobox(parent, textvariable=selected_table_var, state="readonly")
        self.table_combobox.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Cargar Tablas", command=lambda: self.load_tables(self.table_combobox), bg="#3e3e3e", fg="black").grid(row=2, column=1, padx=5, pady=5)

        def delete_table():
            table_name = selected_table_var.get()

            if not table_name:
                messagebox.showerror("Error", "Debe seleccionar una tabla para eliminar.")
                return

            try:
                cursor = self.conn.cursor()
                ddl = f"DROP TABLE {table_name}"
                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, ddl)
                cursor.execute(ddl)
                self.conn.commit()

                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Tabla '{table_name}' eliminada exitosamente.")

                cursor.close()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al eliminar la tabla: {str(e)}")

        tk.Button(parent, text="Eliminar", command=delete_table, bg="#3e3e3e", fg="black").grid(row=3, column=0, padx=5, pady=10, sticky="e")
        tk.Button(parent, text="Cancelar", command=parent.quit, bg="#3e3e3e", fg="black").grid(row=3, column=1, padx=5, pady=10, sticky="w")


    def load_tables(self, table_combobox):
        """Carga las tablas disponibles en la base de datos en el combobox."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT tablename FROM sys.systables WHERE tabletype='T'")
            tables = cursor.fetchall()

            table_combobox['values'] = [table[0] for table in tables]
            if tables:
                table_combobox.current(0)

            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar las tablas: {str(e)}")


    def delete_trigger_form(self, parent):
        tk.Label(parent, text="Borrar Trigger", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

    def delete_check_form(self, parent):
        tk.Label(parent, text="Borrar Check", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

    def delete_view_form(self, parent):
        tk.Label(parent, text="Borrar Vista", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

    def delete_schema_form(self, parent):
        tk.Label(parent, text="Borrar Esquema", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

#=======================================================================================================================
#DATABASE-OPERATIONS
    def get_schemas(self, connection_info):
        try:
            jdbc_driver = '/Users/coleexz/Documents/GitHub/ApacheDerbyDBMS/db-derby-10.17.1.0-bin/lib/derbyclient.jar'
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{connection_info["hostname"]}:{connection_info["port"]}/{connection_info["sid"]};create=true;currentSchema={connection_info.get("schema")}'
            conn = jaydebeapi.connect(driver_class, db_url, [connection_info["schema"], connection_info["password"]], jdbc_driver)
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
            db_url = f'jdbc:derby://{connection_info["hostname"]}:{connection_info["port"]}/{connection_info["sid"]};create=true;currentSchema={connection_info.get("schema")}'
            conn = jaydebeapi.connect(driver_class, db_url, [connection_info["schema"], connection_info["password"]], jdbc_driver)
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
            db_url = f'jdbc:derby://{connection_info["hostname"]}:{connection_info["port"]}/{connection_info["sid"]};create=true;currentSchema={connection_info.get("schema")}'
            conn = jaydebeapi.connect(driver_class, db_url, [connection_info["schema"], connection_info["password"]], jdbc_driver)
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

    def connect_to_selected_connection(self):
        if self.selected_connection:
            connection_info = self.connections.get(self.selected_connection, {})
            self.connect_to_database(connection_info)

    def connect_to_database(self, connection_info):
        try:
            jdbc_driver = '/Users/coleexz/Documents/GitHub/ApacheDerbyDBMS/db-derby-10.17.1.0-bin/lib/derbyclient.jar'
            driver_class = 'org.apache.derby.client.ClientAutoloadedDriver'
            db_url = f'jdbc:derby://{connection_info.get("hostname")}:{connection_info.get("port")}/{connection_info.get("sid")};create=true'
            self.conn = jaydebeapi.connect(driver_class, db_url, [connection_info.get("schema"), connection_info.get("password")], jdbc_driver)
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

#=======================================================================================================================




#=======================================================================================================================
    def create_stored_procedure_form(self, parent):
        tk.Label(parent, text="Crear Procedimiento Almacenado", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Procedimiento", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        self.procedure_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=self.procedure_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        column_frame = tk.Frame(parent, bg="#2e2e2e")
        column_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.columns_tree = ttk.Treeview(column_frame, columns=("name", "mode", "data_type"), show="headings", height=6)
        self.columns_tree.grid(row=1, column=0, columnspan=3, pady=5)
        self.columns_tree.heading("name", text="Nombre")
        self.columns_tree.heading("mode", text="Modo")
        self.columns_tree.heading("data_type", text="Tipo de Dato")

        name_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=name_var, width=15, bg="white", fg="black").grid(row=2, column=0, padx=5, pady=5)

        mode_var = tk.StringVar()
        mode_combobox = ttk.Combobox(column_frame, textvariable=mode_var, values=["IN", "OUT", "INOUT"], state="readonly")
        mode_combobox.grid(row=2, column=1, padx=5, pady=5)

        data_type_var = tk.StringVar()
        data_type_combobox = ttk.Combobox(column_frame, textvariable=data_type_var, values=["VARCHAR", "INT", "FLOAT"], state="readonly")
        data_type_combobox.grid(row=2, column=2, padx=5, pady=5)

        def add_column():
            if not name_var.get() or not mode_var.get() or not data_type_var.get():
                messagebox.showerror("Error", "Debe ingresar todos los valores del atributo.")
                return
            self.columns_tree.insert("", "end", values=(name_var.get(), mode_var.get(), data_type_var.get()))

        def delete_column():
            selected_item = self.columns_tree.selection()
            if selected_item:
                self.columns_tree.delete(selected_item)

        button_frame = tk.Frame(column_frame, bg="#2e2e2e")
        button_frame.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")

        tk.Button(button_frame, text="Agregar Atributo", command=add_column, bg="#3e3e3e", fg="black").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Eliminar Atributo", command=delete_column, bg="#3e3e3e", fg="black").pack(side=tk.LEFT, padx=5)

        tk.Button(parent, text="Crear Procedimiento", command=self.create_stored_procedure, bg="#3e3e3e", fg="black").grid(row=3, column=0, padx=5, pady=10)

    def create_stored_procedure(self):
        procedure_name = self.procedure_name_var.get()
        if not procedure_name:
            messagebox.showerror("Error", "Debe ingresar el nombre del procedimiento.")
            return

        parameters = [self.columns_tree.item(item, "values") for item in self.columns_tree.get_children()]
        param_definitions = []

        for param in parameters:
            param_mode = param[1]
            param_name = param[0]
            param_type = param[2]

            param_def = f"{param_mode} {param_name} {param_type}"
            param_definitions.append(param_def)

        ddl = f"""
        CREATE PROCEDURE {procedure_name} (
            {', '.join(param_definitions)}
        )
        PARAMETER STYLE JAVA
        LANGUAGE JAVA
        EXTERNAL NAME 'my.package.MyClass.myMethod'
        """

        self.query_text.delete(1.0, tk.END)
        self.query_text.insert(tk.END, ddl)

        try:
            cursor = self.conn.cursor()
            cursor.execute(ddl)
            self.conn.commit()
            cursor.close()

            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Procedimiento '{procedure_name}' creado exitosamente.")

        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al crear el procedimiento: {str(e)}")

    def delete_stored_procedure_form(self, parent):
        tk.Label(parent, text="Borrar Procedimiento Almacenado", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Procedimiento", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        procedure_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=procedure_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Borrar Procedimiento", bg="#3e3e3e", fg="black", command=lambda: self.delete_stored_procedure(procedure_name_var.get())).grid(row=2, column=0, columnspan=2, pady=10)

    def create_stored_function_form(self, parent):
        tk.Label(parent, text="Crear Función", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=3, pady=3, sticky="w")

        tk.Label(parent, text="Nombre de la Función", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=3, pady=3, sticky="w")
        function_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=function_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=3, pady=3, sticky="w")

        tk.Label(parent, text="Tipo de Retorno", bg="#2e2e2e", fg="white").grid(row=2, column=0, padx=3, pady=3, sticky="w")
        return_type_var = tk.StringVar()
        tk.Entry(parent, textvariable=return_type_var, bg="#2e2e2e", fg="white").grid(row=2, column=1, padx=3, pady=3, sticky="w")

        column_frame = tk.Frame(parent, bg="#2e2e2e")
        column_frame.grid(row=3, column=0, columnspan=2, padx=3, pady=3, sticky="w")

        columns_tree = ttk.Treeview(column_frame, columns=("name", "mode", "data_type", "default_value"), show="headings", height=6)
        columns_tree.grid(row=1, column=0, columnspan=5, pady=3)
        columns_tree.heading("name", text="Nombre")
        columns_tree.heading("mode", text="Modo")
        columns_tree.heading("data_type", text="Tipo de Dato")
        columns_tree.heading("default_value", text="Valor por Defecto")


        def add_parameter():
            if not param_name_var.get() or not param_mode_var.get() or not param_data_type_var.get():
                messagebox.showerror("Error", "Debe ingresar todos los campos del parámetro.")
                return
            columns_tree.insert("", "end", values=(param_name_var.get(), param_mode_var.get(), param_data_type_var.get(), param_default_var.get()))

        def delete_parameter():
            selected_item = columns_tree.selection()
            if selected_item:
                columns_tree.delete(selected_item)

        param_name_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=param_name_var, width=15, bg="white", fg="black").grid(row=2, column=0, padx=3, pady=3)

        param_mode_var = tk.StringVar()
        mode_combobox = ttk.Combobox(column_frame, textvariable=param_mode_var, values=["IN", "OUT", "INOUT"], state="readonly")
        mode_combobox.grid(row=2, column=1, padx=3, pady=3)

        param_data_type_var = tk.StringVar()
        data_type_combobox = ttk.Combobox(column_frame, textvariable=param_data_type_var, values=["VARCHAR", "INT", "FLOAT"], state="readonly")
        data_type_combobox.grid(row=2, column=2, padx=3, pady=3)

        param_default_var = tk.StringVar()
        tk.Entry(column_frame, textvariable=param_default_var, width=10, bg="white", fg="black").grid(row=2, column=3, padx=3, pady=3)

        tk.Button(column_frame, text="Agregar Parámetro", command=add_parameter, bg="#3e3e3e", fg="black").grid(row=3, column=4, padx=3, pady=3)
        tk.Button(column_frame, text="Eliminar Parámetro", command=delete_parameter, bg="#3e3e3e", fg="black").grid(row=4, column=4, padx=3, pady=3)

        def create_function():
            if not self.conn:
                messagebox.showerror("Error", "Debe seleccionar una conexión.")
                return

            try:
                cursor = self.conn.cursor()
                function_name = function_name_var.get()
                return_type = return_type_var.get()
                parameters = [columns_tree.item(item, "values") for item in columns_tree.get_children()]

                ddl = f"CREATE FUNCTION {function_name} ("
                param_definitions = []
                for param in parameters:
                    param_definitions.append(f"{param[0]} {param[2]}")
                ddl += ", ".join(param_definitions)
                ddl += f") RETURNS {return_type} LANGUAGE JAVA PARAMETER STYLE JAVA NO SQL EXTERNAL NAME 'your.java.classpath'"

                self.query_text.delete(1.0, tk.END)
                self.query_text.insert(tk.END, ddl)

                cursor.execute(ddl)
                self.conn.commit()
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Función {function_name} creada exitosamente.")
                cursor.close()

            except Exception as e:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"Error al crear la función: {str(e)}")


        tk.Button(parent, text="Crear Función", command=create_function, bg="#3e3e3e", fg="black").grid(row=5, column=0, padx=3, pady=3, sticky="e")
        tk.Button(parent, text="Cancelar", command=parent.quit, bg="#3e3e3e", fg="black").grid(row=5, column=1, padx=3, pady=3, sticky="w")

    def show_modify_stored_function_form(self, parent):
        tk.Label(parent, text="Seleccione la Función:", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        function_name_var = tk.StringVar()
        function_combobox = ttk.Combobox(parent, textvariable=function_name_var, state="readonly")
        function_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Button(parent, text="Cargar Funciones", command=lambda: self.load_functions(function_combobox), bg="#3e3e3e", fg="black").grid(row=0, column=2, padx=5, pady=5)

        tk.Label(parent, text="DDL de la Función:", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ddl_textbox = tk.Text(parent, height=10, bg="#2e2e2e", fg="white", insertbackground="white")
        ddl_textbox.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="we")

        def generate_ddl():
            function_name = function_name_var.get()
            if not function_name:
                messagebox.showerror("Error", "Debe seleccionar una función para generar el DDL.")
                return

            try:
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT FUNCTION_DEFINITION FROM SYS.SYSFUNCS WHERE ALIAS = '{function_name}'")
                ddl = cursor.fetchone()[0]

                ddl_textbox.delete(1.0, tk.END)
                ddl_textbox.insert(tk.END, ddl)

                cursor.close()

            except Exception as e:
                ddl_textbox.delete(1.0, tk.END)
                ddl_textbox.insert(tk.END, f"Error al obtener el DDL de la función: {str(e)}")

        tk.Button(parent, text="Generar DDL", command=generate_ddl, bg="#3e3e3e", fg="black").grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky="e")

        def execute_ddl():
            new_ddl = ddl_textbox.get("1.0", tk.END).strip()
            if not new_ddl:
                messagebox.showerror("Error", "Debe generar o modificar el DDL antes de ejecutarlo.")
                return

            self.modify_stored_function(function_name_var.get(), new_ddl)

        tk.Button(parent, text="Ejecutar DDL", command=execute_ddl, bg="#3e3e3e", fg="black").grid(row=4, column=0, columnspan=3, padx=5, pady=10, sticky="e")


    def delete_stored_function_form(self, parent):
        tk.Label(parent, text="Borrar Función", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre de la Función", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)
        function_name_var = tk.StringVar()
        tk.Entry(parent, textvariable=function_name_var, bg="#2e2e2e", fg="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Borrar", bg="#3e3e3e", fg="black", command=lambda: self.delete_function(function_name_var.get())).grid(row=2, column=0, columnspan=2, pady=10)


    def modify_stored_procedure_form(self, parent):
        tk.Label(parent, text="Modificar Procedimiento Almacenado", bg="#2e2e2e", fg="white").grid(row=0, column=0, padx=5, pady=5)

        tk.Label(parent, text="Nombre del Procedimiento", bg="#2e2e2e", fg="white").grid(row=1, column=0, padx=5, pady=5)

        procedure_name_var = tk.StringVar()
        procedure_combobox = ttk.Combobox(parent, textvariable=procedure_name_var, state="readonly")
        procedure_combobox.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(parent, text="Cargar Procedimientos", command=lambda: self.load_procedures(procedure_combobox), bg="#3e3e3e", fg="black").grid(row=1, column=2, padx=5, pady=5)

        tk.Button(parent, text="Cargar DDL", command=lambda: self.get_procedure_ddl(procedure_name_var.get()), bg="#3e3e3e", fg="black").grid(row=2, column=0, columnspan=2, pady=10)

        procedure_code_text = tk.Text(parent, height=10, bg="#2e2e2e", fg="white")
        procedure_code_text.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        tk.Button(parent, text="Modificar Procedimiento", bg="#3e3e3e", fg="black", command=lambda: self.modify_stored_procedure(procedure_name_var.get(), procedure_code_text.get("1.0", tk.END))).grid(row=4, column=0, columnspan=2, pady=10)


    def load_procedures(self, combobox):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT ALIAS FROM SYS.SYSALIASES WHERE ALIASTYPE = 'P'")
            procedures = cursor.fetchall()
            procedure_names = [proc[0] for proc in procedures]
            combobox['values'] = procedure_names
            cursor.close()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar los procedimientos: {str(e)}")


    def get_procedure_ddl(self, procedure_name):
        if not procedure_name:
            messagebox.showerror("Error", "Debe seleccionar un procedimiento.")
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT ALIASINFO FROM SYS.SYSALIASES WHERE ALIAS = '{procedure_name}'")
            ddl = cursor.fetchone()
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, ddl[0] if ddl else "No se encontró el DDL.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al obtener el DDL: {str(e)}")


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

    def get_function_ddl(self, function_name):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return
        try:
            cursor = self.conn.cursor()
            query = f"SELECT FUNCTIONTEXT FROM SYS.SYSALIASES WHERE ALIAS = '{function_name}'"
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)
            cursor.execute(query)
            ddl = cursor.fetchone()
            if ddl:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, ddl[0])
            else:
                self.resultado_text.delete(1.0, tk.END)
                self.resultado_text.insert(tk.END, f"No se encontró la función {function_name}.")
            cursor.close()
        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al obtener DDL de la función: {str(e)}")

    def create_stored_function(self, name, return_type, parameters):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return
        try:
            cursor = self.conn.cursor()

            query = f"CREATE FUNCTION {name}({parameters}) RETURNS {return_type} LANGUAGE JAVA PARAMETER STYLE JAVA NO SQL EXTERNAL NAME 'Class.method';"

            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query)

            cursor.execute(query)
            self.conn.commit()

            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Función {name} creada exitosamente.")
            cursor.close()

        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al crear la función: {str(e)}")


    def load_functions(self, combobox):
        try:
            if not self.conn:
                messagebox.showerror("Error", "No hay ninguna conexión establecida.")
                return

            cursor = self.conn.cursor()
            cursor.execute("SELECT ALIAS FROM SYS.SYSALIASES WHERE ALIASTYPE = 'F'")
            functions = cursor.fetchall()

            combobox['values'] = [func[0] for func in functions]
            if functions:
                combobox.current(0)

            cursor.close()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar las funciones: {str(e)}")


    def modify_stored_function(self, name, new_code):
        if not self.conn:
            messagebox.showerror("Error", "No hay ninguna conexión establecida.")
            return

        try:
            cursor = self.conn.cursor()

            drop_query = f"DROP FUNCTION {name}"
            create_query = new_code

            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, f"{drop_query};\n{create_query}")
            cursor.execute(drop_query)
            cursor.execute(create_query)
            self.conn.commit()

            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Función {name} modificada exitosamente.")
            cursor.close()

        except Exception as e:
            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Error al modificar la función: {str(e)}")

    def delete_function(self, name):
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
                   SELECT CONGLOMERATENAME
                    FROM SYS.SYSCONGLOMERATES
                    WHERE ISINDEX = true
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
            print(e)

root = tk.Tk()
app = SQLDeveloperEmulator(root)
root.mainloop()
