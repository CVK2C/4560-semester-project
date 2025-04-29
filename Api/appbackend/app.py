from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
app = Flask(__name__)
CORS(app)  # create bridge to react native 

# LOGIN page
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    print("Received data from React Native:", data)  

    email = data.get("username")  # Username 
    password = data.get("password")  # Pword 


    try:
        # Connect to MySQL database
        db = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="1234",  # your MySQL password 
            database="app4050"
        )
        cursor = db.cursor(dictionary=True)

        # Query USERINFO table to find the user based on Username and Pword
        query = "SELECT * FROM USERINFO WHERE Username = %s AND Pword = %s"
        cursor.execute(query, (email, password))

        # Fetch the first user record that matches the query
        user = cursor.fetchone()

        # Log the data fetched from MySQL
        if user:
            print("Data fetched from MySQL:", user)  # Log what was fetched from the MySQL database
        else:
            print("No user found with these credentials.")  # No data found

        # Check if the user exists and return response accordingly
        if user:
            return jsonify({"message": "Login successful", "user": user}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except mysql.connector.Error as err:
        print("Database error:", err)
        return jsonify({"error": "Database connection failed"}), 500

@app.route("/create-account", methods=["POST"])
def create_account():
    data=request.get_json()
    print("Received signup data",data)
    #extract field

    fname=data.get("fname")
    lname=data.get("lname")
    username=data.get("username")
    password=data.get("password")
    admsts=data.get("admsts","user")

    if not all([fname,lname,username,password]):
        return jsonify({"error": "All fields are required."}),400
    try:
        # Connect to MySQL database
        db = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="1234",  #my MySQL password??
            database="app4050"
        )
        cursor= db.cursor()
        count_query="SELECT COUNT(*) AS user_count FROM USERINFO"
        cursor.execute(count_query)
        result=cursor.fetchone()
        user_count=result[0]+1

        insert_query="""
            INSERT INTO USERINFO (User_id,Fname, Lname, Username, Pword, Admsts)
            VALUES (%s,%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (user_count,fname, lname, username, password, admsts))
        db.commit()
        print("User inserted successfully.")
        return jsonify({"message": "Account created successfully."}),201
    except mysql.connector.IntegrityError as e:
        print("Integrity error:", e)
        return jsonify({"Message": "Account created successfully. "}),201
    except mysql.connector.Error as err:
       print("Database error:", err)
       return jsonify({"error": "Database error."}), 500
    finally: 
        cursor.close()
        db.close()

@app.route("/dropdown-options", methods=["GET"])
def get_dropdown_options():

    try:
        db = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="1234",
            database="PROJECT_4560"
        )
        cursor = db.cursor(dictionary=True)

        # tables
        query = " SHOW TABLES"
        cursor.execute(query)
        results = cursor.fetchall()

    
        
        print("past the options")
        return jsonify(results), 200

    except mysql.connector.Error as err:
        print("Database error:", err)
        return jsonify({"error": "Failed to fetch dropdown options"}), 500
    finally:
        cursor.close()
        db.close()

@app.route("/HomeScreen", methods=["POST"])
def displayHomeScreen():
    data = request.get_json()
    selected_table = data.get("selectedTable")
    limit = data.get("limit", 20)  # default to 20 rows
    offset = data.get("offset", 0)

    if not selected_table:
        return jsonify({"error": "No table name provided"}), 400

    print(f"Selected Table: {selected_table}, Limit: {limit}, Offset: {offset}")  # Debug log

    try:
        db = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="1234",
            database="PROJECT_4560"
        )
        cursor = db.cursor(dictionary=True)

        # Use LIMIT and OFFSET
        query = f"SELECT trade_id, open, high, low, close, volume, start_time FROM `{selected_table}` LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))

        rows = cursor.fetchall()

        print("data past")

        if rows:
            return jsonify({"data": rows}), 200
        else:
            return jsonify({"error": "No data found"}), 404

    except mysql.connector.Error as err:
        print("Database error:", err)
        return jsonify({"error": "Database connection failed"}), 500


    
    
# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
