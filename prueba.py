
# Imports
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError, validate
from datetime import datetime
from flask_cors import CORS

# Initialize extensions without connecting them to the app yet
db = SQLAlchemy()
ma = Marshmallow()


# Flask application initialization
app = Flask(__name__)
CORS(app)


# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Ojalasalga200.@localhost:3306/METEOROLOGICAL_DB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions with the application

db.init_app(app)
ma.init_app(app)

# Database Models
# Model for storing wind data including speed, direction, and the associated date.

class Wind(db.Model):
    __tablename__ = 'wind'
    Wind_ID = db.Column(db.Integer, primary_key=True)
    Wind_Speed = db.Column(db.Float)
    Wind_Direction = db.Column(db.Float)
    Date = db.Column(db.Date, nullable=False)

# Model for storing wind data including speed, direction, and the associated date.

class Precipitation(db.Model):
    __tablename__ = 'precipitation'
    Precipitation_ID = db.Column(db.Integer, primary_key=True)
    Precipitation_Type = db.Column(db.String(100))
    Precipitation_Amount = db.Column(db.Float)
    Date = db.Column(db.Date, nullable=False)

# Model for storing atmospheric pressure data and the associated date.

class Pressure(db.Model):
    __tablename__ = 'pressure'
    Pressure_ID = db.Column(db.Integer, primary_key=True)
    PressureValue = db.Column(db.Float)
    Date = db.Column(db.Date, nullable=False)

# Model for storing humidity-related data such as soil wetness at different levels and the associated date.

class Humidity(db.Model):
    __tablename__ = 'humidity'
    Humidity_ID = db.Column(db.Integer, primary_key=True)
    SurfaceSoilWetness = db.Column(db.Float)
    RootZoneSoilWetness = db.Column(db.Float)
    ProfileSoilMoisture = db.Column(db.Float)
    Date = db.Column(db.Date, nullable=False)

# Model for geographic zones, storing location-specific information such as name, latitude, longitude, and altitude.

class GeographicZone(db.Model):
    __tablename__ = 'geographic_zone'
    GeographicZone_ID = db.Column(db.Integer, primary_key=True)
    Zone_Name = db.Column(db.String(100))
    Longitude = db.Column(db.Float)
    Altitude = db.Column(db.Float)
    Latitude = db.Column(db.Float)

# Model for storing weather measurements, linking data from other models and adding temperature, cloud amount, and date.

class WeatherMeasurement(db.Model):
    __tablename__ = 'weather_measurement'
    ClimateMeasurement_ID = db.Column(db.Integer, primary_key=True)
    Wind_ID = db.Column(db.Integer, db.ForeignKey('wind.Wind_ID'), nullable=False)
    Pressure_ID = db.Column(db.Integer, db.ForeignKey('pressure.Pressure_ID'), nullable=False)
    GeographicZone_ID = db.Column(db.Integer, db.ForeignKey('geographic_zone.GeographicZone_ID'), nullable=False)
    Precipitation_ID = db.Column(db.Integer, db.ForeignKey('precipitation.Precipitation_ID'), nullable=False)
    Humidity_ID = db.Column(db.Integer, db.ForeignKey('humidity.Humidity_ID'), nullable=False)
    Date = db.Column(db.Date, nullable=False)
    Max_Temperature_2m = db.Column(db.Float)
    Cloud_Amount = db.Column(db.Float)
    Min_Temperature_2m = db.Column(db.Float)


# Model for vegetation, linking weather and geographic data with vegetation type.

class Vegetation(db.Model):
    __tablename__ = 'vegetation'
    Vegetation_ID = db.Column(db.Integer, primary_key=True)
    ClimateMeasurement_ID = db.Column(db.Integer, db.ForeignKey('weather_measurement.ClimateMeasurement_ID'), nullable=False)
    Wind_ID = db.Column(db.Integer, db.ForeignKey('wind.Wind_ID'), nullable=False)
    Pressure_ID = db.Column(db.Integer, db.ForeignKey('pressure.Pressure_ID'), nullable=False)
    GeographicZone_ID = db.Column(db.Integer, db.ForeignKey('geographic_zone.GeographicZone_ID'), nullable=False)
    Vegetation_Type = db.Column(db.String(100))

# Schemas for Serialization and Validation

# Schema for wind data serialization and validation.
class WindSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Wind
        load_instance = True

# Schema for precipitation data serialization and validation.
class PrecipitationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Precipitation
        load_instance = True

# Schema for pressure data serialization and validation.
class PressureSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Pressure
        load_instance = True

# Schema for humidity data serialization and validation.
class HumiditySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Humidity
        load_instance = True

# Schema for geographic zone data serialization and validation.
class GeographicZoneSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GeographicZone
        load_instance = True

# Schema for weather measurements serialization and validation.
class WeatherMeasurementSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WeatherMeasurement
        load_instance = True

# Schema for vegetation data serialization and validation.
class VegetationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vegetation
        load_instance = True

# Create the database
with app.app_context():
    db.create_all()

# Schemas for serialization
# These schemas are used to convert model instances into JSON and validate input data for each entity.
wind_schema = WindSchema() # Single wind schema for single object serialization/deserialization
winds_schema = WindSchema(many=True) # Schema for handling lists of wind objects
precipitation_schema = PrecipitationSchema() #Single precipitation schema
precipitations_schema = PrecipitationSchema(many=True)# Schema for lists of precipitation objects
pressure_schema = PressureSchema() # Single pressure schema
pressures_schema = PressureSchema(many=True) # Schema for lists of pressure objects.....
humidity_schema = HumiditySchema()
humidities_schema = HumiditySchema(many=True)
geographic_zone_schema = GeographicZoneSchema()
geographic_zones_schema = GeographicZoneSchema(many=True)
weather_measurement_schema = WeatherMeasurementSchema()
weather_measurements_schema = WeatherMeasurementSchema(many=True)
vegetation_schema = VegetationSchema()
vegetations_schema = VegetationSchema(many=True)
#_________________________________________________________________
#___________________________________________________________________
# ----------------------- CRUD Endpoints -----------------------
# Pattern for all tables: POST, GET, PUT, DELETE.

# CRUD para Wind
@app.route('/wind', methods=['POST'])
def add_wind():
    data = request.get_json()

   # Validation for required fields
    if not  data.get('Date'):
        return jsonify({'error': 'Date) is required'}), 400

    new_wind = Wind(
        Wind_Speed=data.get('Wind_Speed'),
        Wind_Direction=data.get('Wind_Direction'),
        Date=data['Date']
    )
    db.session.add(new_wind) # Add the new wind object to the session
    db.session.commit() # Save changes to the database
    return wind_schema.jsonify(new_wind), 201 # Return the created object with status 201

#Endpoint to get all
@app.route('/wind', methods=['GET'])
def get_winds():
    all_winds = Wind.query.all()# Fetch all wind records
    return winds_schema.jsonify(all_winds) # Return serialized list of wind objects
#Endpoint to get by ID
@app.route('/wind/<int:wind_id>', methods=['GET'])
def get_wind(wind_id):
    wind = Wind.query.get_or_404(wind_id) # Fetch a specific wind object or return 404 if not found
    return wind_schema.jsonify(wind)
#Endpoint to update
@app.route('/wind/<int:wind_id>', methods=['PUT'])
def update_wind(wind_id):
    wind = Wind.query.get_or_404(wind_id)
    data = request.get_json()

    # Update only fields present in the JSON payload
    wind.Wind_Speed = data.get('Wind_Speed', wind.Wind_Speed)
    wind.Wind_Direction = data.get('Wind_Direction', wind.Wind_Direction)
    wind.Date = data.get('Date', wind.Date)

    db.session.commit() # Save updates to the database
    return wind_schema.jsonify(wind)
#Endpoint to delate
@app.route('/wind/<int:wind_id>', methods=['DELETE'])
def delete_wind(wind_id):
    wind = Wind.query.get_or_404(wind_id)
    db.session.delete(wind) # Mark the object for deletion
    db.session.commit()# Save changes to the database
    return jsonify({'message': 'Wind deleted successfully'}), 204

# CRUD for Precipitation
@app.route('/precipitation', methods=['POST'])
def add_precipitation():
    data = request.get_json()

    # Validation for required fields
    if not data.get('Date'):
        return jsonify({'error': 'Date) is required'}), 400

    new_precipitation = Precipitation(
        Precipitation_Type=data.get('Precipitation_Type'),
        Precipitation_Amount=data.get('Precipitation_Amount'),
        Date=data['Date']
    )
    db.session.add(new_precipitation)
    db.session.commit()
    return precipitation_schema.jsonify(new_precipitation), 201  # Return the created object with status 201

#Endpoint to GET all
@app.route('/precipitation', methods=['GET'])
def get_precipitations():
    all_precipitations = Precipitation.query.all()
    return precipitations_schema.jsonify(all_precipitations)
#Endpoint to get by ID
@app.route('/precipitation/<int:precipitation_id>', methods=['GET'])
def get_precipitation(precipitation_id):
    precipitation = Precipitation.query.get_or_404(precipitation_id)
    return precipitation_schema.jsonify(precipitation)
#Endpoint to update
@app.route('/precipitation/<int:precipitation_id>', methods=['PUT'])
def update_precipitation(precipitation_id):
    precipitation = Precipitation.query.get_or_404(precipitation_id)
    data = request.get_json()
    precipitation.Precipitation_Type = data.get('Precipitation_Type', precipitation.Precipitation_Type)
    precipitation.Precipitation_Amount = data.get('Precipitation_Amount', precipitation.Precipitation_Amount)
    precipitation.Date= data.get('Date',precipitation.Date)
    db.session.commit()
    return precipitation_schema.jsonify(precipitation)
#Endpoint to delate
@app.route('/precipitation/<int:precipitation_id>', methods=['DELETE'])
def delete_precipitation(precipitation_id):
    precipitation = Precipitation.query.get_or_404(precipitation_id)
    db.session.delete(precipitation) # Mark the object for deletion
    db.session.commit()# Save changes to the database
    return jsonify({'message': 'Precipitation deleted successfully'}), 204


# CRUD para Pressure
@app.route('/pressure', methods=['POST'])
def add_pressure():
    data = request.get_json()

    # Validación de campo requerido
    if not data.get('Date'):
        return jsonify({'error': 'Date'}), 400

    new_pressure = Pressure(
        PressureValue=data.get('PressureValue'),
        Date=data['Date']
    )
    db.session.add(new_pressure)
    db.session.commit()
    return pressure_schema.jsonify(new_pressure), 201 # Return the created object with status 201

# Endpoint to all
@app.route('/pressure', methods=['GET'])
def get_pressures():
    all_pressures = Pressure.query.all()
    return pressures_schema.jsonify(all_pressures)
# Endpoint to get by ID
@app.route('/pressure/<int:pressure_id>', methods=['GET'])
def get_pressure(pressure_id):
    pressure = Pressure.query.get_or_404(pressure_id)
    return pressure_schema.jsonify(pressure)
# Endpoint to update
@app.route('/pressure/<int:pressure_id>', methods=['PUT'])
def update_pressure(pressure_id):
    pressure = Pressure.query.get_or_404(pressure_id)
    data = request.get_json()
    pressure.PressureValue = data.get('PressureValue', pressure.PressureValue)
    pressure.Date=data.get('Date', pressure.Date)
    db.session.commit()
    return pressure_schema.jsonify(pressure)
# Endpoint to delate 
@app.route('/pressure/<int:pressure_id>', methods=['DELETE'])
def delete_pressure(pressure_id):
    pressure = Pressure.query.get_or_404(pressure_id)
    db.session.delete(pressure)# Mark the object for deletion
    db.session.commit()# Save changes to the database
    return jsonify({'message': 'Pressure deleted successfully'}), 204


# CRUD para Humidity
@app.route('/humidity', methods=['POST'])
def add_humidity():
    data = request.get_json()

    # Validation for required fields
    if not  data.get('Date'):
        return jsonify({'error': 'The field "Date" is required'}), 400

    new_humidity = Humidity (
        SurfaceSoilWetness=data.get('SurfaceSoilWetness', None),
        RootZoneSoilWetness=data.get('RootZoneSoilWetness', None),
        ProfileSoilMoisture=data.get('ProfileSoilMoisture', None),
        Date=data['Date']
    )
    db.session.add(new_humidity)
    db.session.commit()
    return humidity_schema.jsonify(new_humidity), 201 # Return the created object with status 201

# Endpoint to GET all 
@app.route('/humidity', methods=['GET'])
def get_humidities():
    all_humidities = Humidity.query.all()
    return humidities_schema.jsonify(all_humidities)
# Endpoint to get by ID
@app.route('/humidity/<int:humidity_id>', methods=['GET'])
def get_humidity(humidity_id):
    humidity = Humidity.query.get_or_404(humidity_id)
    return humidity_schema.jsonify(humidity)

@app.route('/humidity/<int:humidity_id>', methods=['PUT'])
def update_humidity(humidity_id):
    humidity = Humidity.query.get_or_404(humidity_id)
    data = request.get_json()
    humidity.SurfaceSoilWetness = data.get('SurfaceSoilWetness', humidity.SurfaceSoilWetness)
    humidity.RootZoneSoilWetness = data.get('RootZoneSoilWetness', humidity.RootZoneSoilWetness)
    humidity.ProfileSoilMoisture = data.get('ProfileSoilMoisture', humidity.ProfileSoilMoisture)
    humidity.Date=data.get('Date', humidity.Date)
    db.session.commit()
    return humidity_schema.jsonify(humidity)

@app.route('/humidity/<int:humidity_id>', methods=['DELETE'])
def delete_humidity(humidity_id):
    humidity = Humidity.query.get_or_404(humidity_id)
    db.session.delete(humidity)# Mark the object for deletion
    db.session.commit()# Save changes to the database
    return jsonify({'message': 'Humidity deleted successfully'}), 204


# CRUD para GeographicZone
@app.route('/geographiczone', methods=['POST'])
def add_geographic_zone():
    data = request.get_json()

    # Validation for required fields
    if not data.get('Zone_Name'):
        return jsonify({'error': 'Zone_Name is required'}), 400

    new_zone = GeographicZone(
        Zone_Name=data['Zone_Name'],
        Longitude=data.get('Longitude'),
        Altitude=data.get('Altitude'),
        Latitude=data.get('Latitude')
    )
    db.session.add(new_zone)
    db.session.commit()
    return geographic_zone_schema.jsonify(new_zone), 201 # Return the created object with status 201

# Endpoint to get all 
@app.route('/geographiczone', methods=['GET'])
def get_geographic_zones():
    all_zones = GeographicZone.query.all()
    return geographic_zones_schema.jsonify(all_zones)
# Endpoint to Get by ID
@app.route('/geographiczone/<int:zone_id>', methods=['GET'])
def get_geographic_zone(zone_id):
    zone = GeographicZone.query.get_or_404(zone_id)
    return geographic_zone_schema.jsonify(zone)
# Endpoint to put
@app.route('/geographiczone/<int:zone_id>', methods=['PUT'])
def update_geographic_zone(zone_id):
    zone = GeographicZone.query.get_or_404(zone_id)
    data = request.get_json()
    zone.Zone_Name = data.get('Zone_Name', zone.Zone_Name)
    zone.Longitude = data.get('Longitude', zone.Longitude)
    zone.Altitude = data.get('Altitude', zone.Altitude)
    zone.Latitude = data.get('Latitude', zone.Latitude)
    db.session.commit()
    return geographic_zone_schema.jsonify(zone)
# Endpoint to DELATE
@app.route('/geographiczone/<int:zone_id>', methods=['DELETE'])
def delete_geographic_zone(zone_id):
    zone = GeographicZone.query.get_or_404(zone_id)
    db.session.delete(zone)# Mark the object for deletion
    db.session.commit()# Save changes to the database
    return jsonify({'message': 'GeographicZone deleted successfully'}), 204
# Endpoint to GET all
@app.route('/weathermeasurement', methods=['GET'])
def get_weather_measurements():
    all_measurements = WeatherMeasurement.query.all()
    return weather_measurements_schema.jsonify(all_measurements)
# Endpoint to GET by ID
@app.route('/weathermeasurement/<string:measurement_id>', methods=['GET'])
def get_weather_measurement(measurement_id):
    measurement = WeatherMeasurement.query.get_or_404(measurement_id)
    return weather_measurement_schema.jsonify(measurement)

# Endpoint to DELATE 
@app.route('/weathermeasurement/<string:measurement_id>', methods=['DELETE'])
def delete_weather_measurement(measurement_id):
    measurement = WeatherMeasurement.query.get_or_404(measurement_id)
    db.session.delete(measurement)# Mark the object for deletion
    db.session.commit()# Save changes to the database
    return jsonify({'message': 'WeatherMeasurement deleted successfully'}), 204

@app.route('/weathermeasurement', methods=['POST'])
def add_weathermeasurement():
    data = request.get_json()

    # Extract the date from the request body
    date_str = data.get('Date')
    if not date_str:
        return jsonify({"error": "Date is required"}), 400

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Search for related records by date
    wind = Wind.query.filter_by(Date=date).first()
    pressure = Pressure.query.filter_by(Date=date).first()
    humidity = Humidity.query.filter_by(Date=date).first()
    precipitation = Precipitation.query.filter_by(Date=date).first()

    if not (wind and pressure and humidity and precipitation):
        return jsonify({"error": "Not all required data is available for the given date"}), 400

    # Create a new climate measurement
    new_measurement = WeatherMeasurement(
        Wind_ID=wind.Wind_ID,
        Pressure_ID=pressure.Pressure_ID,
        Humidity_ID=humidity.Humidity_ID,
        Precipitation_ID=precipitation.Precipitation_ID,
        GeographicZone_ID=data.get('GeographicZone_ID'),  # Proveer en el JSON
        Date=date,
        Max_Temperature_2m=data.get('Max_Temperature_2m'),
        Min_Temperature_2m=data.get('Min_Temperature_2m'),
        Cloud_Amount=data.get('Cloud_Amount')
    )

    # Save to database
    db.session.add(new_measurement)
    db.session.commit()

    return jsonify({"message": "Weather measurement added successfully", "id": new_measurement.ClimateMeasurement_ID}), 201 # Return the created object with status 201


@app.route('/update_weathermeasurement/<int:measurement_id>', methods=['PUT'])
def update_weathermeasurement(measurement_id):
    data = request.get_json()

    # Search WeatherMeasurement record by ID
    measurement = WeatherMeasurement.query.get(measurement_id)
    if not measurement:
        return jsonify({"error": "Weather measurement not found"}), 404

    # Update related fields
    if "Date" in data:
        try:
            date = datetime.strptime(data["Date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        # Find related records by the new date
        wind = Wind.query.filter_by(Date=date).first()
        pressure = Pressure.query.filter_by(Date=date).first()
        humidity = Humidity.query.filter_by(Date=date).first()
        precipitation = Precipitation.query.filter_by(Date=date).first()

        if not (wind and pressure and humidity and precipitation):
            return jsonify({"error": "Not all required data is available for the new date"}), 400

        # Update references
        measurement.Wind_ID = wind.Wind_ID
        measurement.Pressure_ID = pressure.Pressure_ID
        measurement.Humidity_ID = humidity.Humidity_ID
        measurement.Precipitation_ID = precipitation.Precipitation_ID
        measurement.Date = date

   # Update other fields
    if "GeographicZone_ID" in data:
        measurement.GeographicZone_ID = data["GeographicZone_ID"]

    if "Max_Temperature_2m" in data:
        measurement.Max_Temperature_2m = data["Max_Temperature_2m"]

    if "Min_Temperature_2m" in data:
        measurement.Min_Temperature_2m = data["Min_Temperature_2m"]

    if "Cloud_Amount" in data:
        measurement.Cloud_Amount = data["Cloud_Amount"]

    # Save changes to the database
    db.session.commit()

    return jsonify({"message": "Weather measurement updated successfully"}), 200

#CRUD for Vegetation
@app.route('/vegetation', methods=['POST'])
def add_vegetation():
    data = request.get_json()

    # Validation of required fields
    required_fields = ['Vegetation_ID', 'ClimateMeasurement_ID', 'Wind_ID', 'Pressure_ID', 'GeographicZone_ID']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    new_vegetation = Vegetation(
        Vegetation_ID=data['Vegetation_ID'],
        ClimateMeasurement_ID=data['ClimateMeasurement_ID'],
        Wind_ID=data['Wind_ID'],
        Pressure_ID=data['Pressure_ID'],
        GeographicZone_ID=data['GeographicZone_ID'],
        Vegetation_Type=data.get('Vegetation_Type')
    )
    db.session.add(new_vegetation)
    db.session.commit()
    return vegetation_schema.jsonify(new_vegetation), 201 # Return the created object with status 201

# Endpoint to retrieve all vegetation records
@app.route('/vegetation', methods=['GET'])
def get_vegetations():
        # Query all vegetation records from the database

    all_vegetations = Vegetation.query.all()
    return vegetations_schema.jsonify(all_vegetations)

# Endpoint to retrieve a specific vegetation record by ID

@app.route('/vegetation/<string:vegetation_id>', methods=['GET'])
def get_vegetation(vegetation_id):
    vegetation = Vegetation.query.get_or_404(vegetation_id)
    return vegetation_schema.jsonify(vegetation)

# Endpoint to update a specific vegetation record by ID

@app.route('/vegetation/<string:vegetation_id>', methods=['PUT'])
def update_vegetation(vegetation_id):
    vegetation = Vegetation.query.get_or_404(vegetation_id)
    data = request.get_json()
    vegetation.ClimateMeasurement_ID = data.get('ClimateMeasurement_ID', vegetation.ClimateMeasurement_ID)
    vegetation.Wind_ID = data.get('Wind_ID', vegetation.Wind_ID)
    vegetation.Pressure_ID = data.get('Pressure_ID', vegetation.Pressure_ID)
    vegetation.GeographicZone_ID = data.get('GeographicZone_ID', vegetation.GeographicZone_ID)
    vegetation.Vegetation_Type = data.get('Vegetation_Type', vegetation.Vegetation_Type)
    db.session.commit()
    return vegetation_schema.jsonify(vegetation)

# Endpoint to DELATE
@app.route('/vegetation/<string:vegetation_id>', methods=['DELETE'])
def delete_vegetation(vegetation_id):
    vegetation = Vegetation.query.get_or_404(vegetation_id)
    db.session.delete(vegetation)# Mark the object for deletion
    db.session.commit()# Save changes to the database
    return jsonify({'message': 'Vegetation deleted successfully'}), 204

#MAIN CODE
if __name__ == "__main__":
    app.run(debug=True)
