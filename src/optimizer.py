"""
optimizer.py

Solves for the cheapest flight(s) based on filtered data and constraints.
Uses Linear Programming via PuLP.
"""

import pandas as pd
from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpBinary, PULP_CBC_CMD

def find_cheapest_itinerary(df):
    """
    Solves an LP model to find the cheapest flight(s) based on input data.

    Parameters:
    - df (DataFrame): Filtered DataFrame containing flight options.

    Returns:
    - DataFrame: Selected flight(s) from the input, marked as optimal.
    - float: Total price of the optimal itinerary.
    """

    # Create the LP problem
    prob = LpProblem("FlightFareMinimization", LpMinimize)

    # Create binary decision variables for each flight
    flight_vars = {
        i: LpVariable(f"flight_{i}", cat=LpBinary)
        for i in df.index
    }

    # Objective: Minimize total price
    prob += lpSum(flight_vars[i] * df.loc[i, "price"] for i in df.index)

    # Constraint: Select exactly one flight for now (simple version)
    prob += lpSum(flight_vars[i] for i in df.index) == 1, "SelectOneFlight"

    # Solve
    prob.solve(PULP_CBC_CMD(msg=False))

    # Extract selected flight(s)
    selected_indices = [i for i in df.index if flight_vars[i].value() == 1.0]
    selected_flights = df.loc[selected_indices].copy()
    total_price = selected_flights["price"].sum()

    return selected_flights.reset_index(drop=True), total_price