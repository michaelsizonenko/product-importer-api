from app.db import conn


class Product(conn.Model):
    __tablename__ = "product"
    id = conn.Column(conn.Integer, primary_key=True, autoincrement=True)
    name = conn.Column(conn.String())
    sku = conn.Column(conn.String())
    description = conn.Column(conn.String())
