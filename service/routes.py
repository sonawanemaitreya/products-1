import os
from flask import Flask, render_template, url_for, make_response
from werkzeug.exceptions import BadRequest
from werkzeug.utils import redirect
from flask.globals import request
from service.error_handler import  bad_request, request_validation_error, not_found
from service.products import ProductService
from service import app
from service import status
from flask import Flask, jsonify, request, url_for, make_response, abort, request
import json
import logging

#root Home page
@app.route("/",  methods=['GET'])
def index():
    return make_response(jsonify(name='Products REST API Service', version='1.0', 
                            url = url_for('list_all_products', _external=True)), status.HTTP_200_OK)

#get all products
@app.route("/products", methods=["GET"])
def list_all_products(): 
    app.logger.info("Request to list all products") 
    products = ProductService.get_all_products()
    return make_response(
        jsonify(products), status.HTTP_200_OK
    )

#get a specific product
@app.route("/products/<int:id>", methods=["GET"])
def list_product(id):  
    id = int(id)
    app.logger.info("Request to list a product with a given id") 
    product= ProductService.find_product_by_id(id)
    if product is None:
        return not_found("Product Id not found from database")
    return make_response(
        product, status.HTTP_200_OK
    )

@app.route("/products", methods=["POST"])
def create():
    app.logger.info("Request to Create product...")
    check_content_type("application/json")
    record = json.loads(request.data)
    product_name = record['name']
    product_price = record['price']
    description = record['description']

    if product_name =="":
        return request_validation_error("Product name is required.")
    if len(product_name)>100:
        return request_validation_error("Product name max limit 100 characters")

    if description =="":
        return request_validation_error("Product description is required.")
    if len(description)>250:
        return request_validation_error("Product description max limit 250 characters")

    try:
        price_value = float(product_price)
    except:
        return request_validation_error("Product price is required and needs to be a numeric") 
    if float(product_price)<0:
        return request_validation_error("Product price cannot be less than zero.")

    output = ProductService.create_product(product_name, product_price, description)
    location_url = url_for("list_all_products", id=output['id'], _external=True)
    return make_response(
        jsonify(output), status.HTTP_201_CREATED, {'Location': location_url}
    )

@app.route('/products/<int:id>',  methods=["PUT"])
def update(id):
    app.logger.info("Request to Update product...")
    check_content_type("application/json")
    product = ProductService.find_product_by_id(id)
    if product :
        record = json.loads(request.data)
        name = record['name']
        price = record['price']
        description = record['description']

        if len(name)>100:
            return request_validation_error("Product name max limit 100 characters")

        if len(description)>250:
            return request_validation_error("Product description max limit 250 characters")

        if price!="":
            try:
                price_value = float(price)
            except:
                return request_validation_error("Product price needs to be a numeric") 

        if price!="" and float(price)<0:
            return request_validation_error("Product price cannot be less than zero.")
        output = ProductService.update_product(id,name, price, description)
    
        response_code = status.HTTP_200_OK
        return make_response(jsonify(output), response_code)    
    else:
        return not_found("Product Id not found from database which needs to update")
    
@app.route('/products/<int:id>', methods=['DELETE'])
def delete(id):
    app.logger.info("Request to delete product...")
    output = ProductService.delete_product(id)
    response_code = status.HTTP_204_NO_CONTENT
    return make_response('', response_code) 

def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )

