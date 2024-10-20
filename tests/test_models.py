# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        # logging.info(f'product: {product}')
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        # checking the properties
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should update a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        # logging.info(f'product: {product}')
        self.assertIsNotNone(product.id)
        # update description
        product.description = 'modified'
        org_id = product.id
        product.update()
        self.assertEqual(product.id, org_id)
        self.assertEqual(product.description, "modified")
        # fetching all products
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, org_id)
        self.assertEqual(products[0].description, "modified")

    def test_update_on_invalid_id(self):
        """It should return Data validation error """
        product = ProductFactory()
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should delete a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # delete the product
        product.delete()
        products = Product.all()
        self.assertEqual(len(products), 0)

    def test_list_all_products(self):
        """It should list atll the products"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        # add 5 products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # check len of products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """It should find a product by its name"""
        # create 5 products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # check len of products
        products = Product.all()
        self.assertEqual(len(products), 5)
        first_product_name = products[0].name
        product_freq = len([i for i in products if i.name == first_product_name])
        product_list = Product.find_by_name(first_product_name)
        self.assertEqual(product_list.count(), product_freq)
        for prod in product_list:
            self.assertEqual(prod.name, first_product_name)

    def test_find_product_by_availability(self):
        """It should find a product by its availability"""
        # create 10 products
        for _ in range(10):
            product = ProductFactory()
            product.create()
        # check len of products
        products = Product.all()
        self.assertEqual(len(products), 10)
        first_product_availability = products[0].available
        product_freq = len([i for i in products if i.available == first_product_availability])
        product_list = Product.find_by_availability(first_product_availability)
        self.assertEqual(product_list.count(), product_freq)
        for prod in product_list:
            self.assertEqual(prod.available, first_product_availability)

    def test_find_product_by_category(self):
        """It should find a product by its category"""
        # create 10 products
        for _ in range(10):
            product = ProductFactory()
            product.create()
        # check len of products
        products = Product.all()
        self.assertEqual(len(products), 10)
        first_product_category = products[0].category
        product_freq = len([i for i in products if i.category == first_product_category])
        product_list = Product.find_by_category(first_product_category)
        self.assertEqual(product_list.count(), product_freq)
        for prod in product_list:
            self.assertEqual(prod.category, first_product_category)

    def test_find_product_by_price(self):
        """It should find a product by its price"""
        # create 10 products
        for _ in range(10):
            product = ProductFactory()
            product.create()
        # check len of products
        products = Product.all()
        self.assertEqual(len(products), 10)
        first_product_price = products[0].price
        product_freq = len([i for i in products if i.price == first_product_price])
        product_list = Product.find_by_price(first_product_price)
        self.assertEqual(product_list.count(), product_freq)
        for prod in product_list:
            self.assertEqual(prod.price, first_product_price)

        # test sad path with price as a string
        product = ProductFactory()
        product.create()
        product.price = 29
        product.update()
        self.assertEqual(product.price, 29)
        found_product = Product.find_by_price('29')
        for i in found_product:
            self.assertEqual(i.price, 29)
