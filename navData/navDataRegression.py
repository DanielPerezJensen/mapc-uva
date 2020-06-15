import csv
import numpy as np


from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures

import matplotlib.pyplot as plt


nav_durations = []
goals = []

# open data
with open('navData_clearEventChance_0.txt', 'r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        nav_durations.append(int(row[0]))
        temp_str = ",".join(row[1:3])
        goals.append(eval(temp_str[1:]))

# create train/test data
x = np.array(goals)
y = np.array(nav_durations)

poly = PolynomialFeatures(degree=3)
poly_variables = poly.fit_transform(x)

poly_var_train, poly_var_test, res_train, res_test = train_test_split(poly_variables, y, test_size = 0.3, random_state = 4)

# fit the regression
regression = LinearRegression()

model = regression.fit(poly_var_train, res_train)
# test model on test data set
score = model.score(poly_var_test, res_test)

# plot model
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(x[:,0], x[:,1], y, marker='o')

x_grid, y_grid = np.meshgrid(np.linspace(-30, 30, 100), np.linspace(-30, 30, 100))

coord_grid = np.array([x_grid.flatten(), y_grid.flatten()])

coord_variables = poly.fit_transform(coord_grid.swapaxes(1,0))

# prediction
# Gebruik regression.predict met een x en y coordinaat om te predicten hoelang de naviation kost
prediction = regression.predict(coord_variables).reshape(len(x_grid),len(x_grid))

ax.plot_surface(x_grid, y_grid, prediction)

plt.show()
