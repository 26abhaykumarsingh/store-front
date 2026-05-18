from locust import HttpUser, between, task
from random import randint

class WebsiteUser(HttpUser):
  wait_time = between(1, 5)

  @task(2) # the number in parantheses set the priority of this task, task with 4 is twice important as one having 2
  def view_products(self):
    collection_id = randint(2, 6)
    self.client.get(
      f'/store/products/?collection_id={collection_id}', name='/store/products')

  @task(4)
  def view_product(self):
    product_id = randint(1, 1000)
    self.client.get(
      f'/store/products/{product_id}', name='/store/products/:id')

  @task(1)
  def add_to_cart(self):
    product_id = randint(1, 10)
    self.client.post(
      f'/store/carts/{self.cart_id}/items/',
      name='/store/carts/items', # name is for grouping all the urls in the report
      json={'product_id': product_id, 'quantity': 1}
    )

  @task
  def say_hello(self):
    self.client.get('/playground/hello/')

  def on_start(self): # this is not a task but a lifecycle hook, it gets called everytime a new user starts browsing our website
    response = self.client.post('/store/carts/')
    result = response.json()
    self.cart_id = result['id']

