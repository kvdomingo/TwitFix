#!/bin/bash

pytest --cov-config=.coveragerc --cov=. --cov-report html
