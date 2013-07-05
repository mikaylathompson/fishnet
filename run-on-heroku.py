#!flask/bin/python
import os
from flask import Flask
from app import app
if __name__ == "__main__":
	app.run(debug = False)
