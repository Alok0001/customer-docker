from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
api = Api(app)

# MongoDB setup
client = MongoClient('mongodb://db:27017')  # 'mongo' is the hostname of the MongoDB container in Docker
db = client['customer_db']
customers_collection = db['customers']

parser = reqparse.RequestParser()
parser.add_argument('customerName', type=str, required=True, help="Customer name cannot be blank!")
parser.add_argument('customerMobile', type=str, required=True, help="Mobile number must be provided!")
parser.add_argument('customerAddress', type=str, required=True, help="Address must be provided!")

class Customer:
    def __init__(self, customerId, customerName, customerMobile, customerAddress):
        self.customerId = customerId
        self.customerName = customerName
        self.customerMobile = customerMobile
        self.customerAddress = customerAddress

class CustomerServiceImpl:
    @staticmethod
    def add_customer(customer_data):
        result = customers_collection.insert_one(customer_data)
        customer_id = result.inserted_id
        customer_mongo = customers_collection.find_one({'_id': customer_id})
        customer_mongo['_id'] = str(customer_mongo['_id'])
        return customer_mongo

    @staticmethod
    def get_all_customers():
        customers_mongo = list(customers_collection.find())
        for customer in customers_mongo:
            customer['_id'] = str(customer['_id'])
        return customers_mongo

class CustomerController(Resource):
    def post(self):
        args = parser.parse_args()
        customer_data = {
            "customerName": args['customerName'],
            "customerMobile": args['customerMobile'],
            "customerAddress": args['customerAddress']
        }
        customer_data = CustomerServiceImpl.add_customer(customer_data)
        return {
            "customer_in_mongo": customer_data
        }, 201

    def get(self):
        all_customers = CustomerServiceImpl.get_all_customers()
        return all_customers, 200

api.add_resource(CustomerController, '/customer/customers')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
