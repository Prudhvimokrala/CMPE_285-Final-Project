from flask import Flask, request, jsonify
from flask_cors import CORS
from ml_model import predict_disease
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}},
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"])
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:gautam@localhost/doctor'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"User: {self.fullname}"

    def __init__(self, fullname, password, email):
        self.fullname = fullname
        self.password = password
        self.email = email

def format_user(user):
    return {
        "id": user.id,
        "fullname": user.fullname,
        "email": user.email,
        "password":user.password,
        "created_at": user.created_at.isoformat()
    }


@app.route('/')
def home():
    return "Hello 295"





# API endpoint for user signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    fullname = data.get('fullname')
    email = data.get('email')
    password = data.get('password')

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    # Create a new user instance
    new_user = User(fullname=fullname, email=email, password=password)

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User signed up successfully"}), 201




# API endpoint for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Find the user by email
    user = User.query.filter_by(email=email).first()

    # Check if the user exists and the password is correct
    if user and user.password == password:
        return jsonify({"message": "User logged in successfully"}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
    



# API endpoint to create a new user
@app.route('/users', methods=['POST'])
def create_user():
    fullname = request.json.get('fullname')
    email = request.json.get('email')
    password = request.json.get('password')
    new_user = User(fullname, password, email)
    db.session.add(new_user)
    db.session.commit()
    return format_user(new_user)

@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        # Query all users from the database
        users = User.query.all()

        # Convert users to a list of dictionaries
        users_data = [format_user(user) for user in users]

        # Return JSON response with users data
        return jsonify(users_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500





# API endpoint to retrieve a specific user by email
@app.route('/users/<email>', methods=['GET'])
def get_user(email):
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(format_user(user)), 200

# API endpoint to update a user's information
@app.route('/users/<email>', methods=['PUT'])
def update_user(email):
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    data = request.json
    user.fullname = data.get('fullname', user.fullname)
    user.password = data.get('password', user.password)
    db.session.commit()
    return jsonify(format_user(user)), 200




# API endpoint to delete a user
@app.route('/users/<email>', methods=['DELETE'])
def delete_user(email):
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        symptoms = data.get('symptoms', [])  # Ensure symptoms is a list

        # Convert symptoms to integers if necessary
        symptoms = [int(symptom) for symptom in symptoms]

        # Call predict_disease function from ml_model module
        prediction, confidence = predict_disease(symptoms)

        return jsonify({
            'prediction': prediction,
            'confidence': confidence
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

    


if __name__ == "__main__":
    app.run(debug=True)
